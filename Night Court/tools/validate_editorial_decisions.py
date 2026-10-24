#!/usr/bin/env python3
"""Metadata validation for human-reviewed S01E01 script claims.

A schema-valid review is a *reviewer's attestation*, not automatic audio or
video verification. This module never grants truth based solely on LLM/ASR
confidence, image presence, or cast/wardrobe inference.
"""
from __future__ import annotations
import argparse,json,re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"seasons"/"S01"/"S01E01"/"derived"/"editorial-review-v1"
INPUT=DIR/"acceptance-worklist.json"
STATES={"pending","accepted_by_reviewer","rejected_by_reviewer","needs_source_recheck"}
MODES={"listened_original_audio","watched_continuous_original_video",
       "synchronized_mouth_voice_review","audited_source_caption",
       "reviewed_isolated_voice"}
SHA_RE=re.compile(r"^[0-9a-f]{64}$")

def load_packet():
    j=json.loads(INPUT.read_text("utf-8"))
    if j["schema"]!="night-court-s01e01-editorial-qa-packet/1":
        raise ValueError("Unexpected editorial packet")
    if not SHA_RE.fullmatch(j["source_video_sha256"]) or not SHA_RE.fullmatch(j["source_caption_sha256"]):
        raise ValueError("Unverifiable source fingerprints")
    tasks={x["task_id"]:("voice",x) for x in j["voice_review_tasks"]}
    tasks.update({x["task_id"]:("visual",x) for x in j["visual_review_tasks"]})
    if len(tasks)!=17 or j["counts"]["source_speaking_turns"]!=11 or j["counts"]["visual_motion_observations"]!=6:
        raise ValueError("Missing original source editorial tasks")
    return j,tasks

def template(packet,tasks):
    return {
      "schema":"night-court-reviewed-script-claims/1",
      "episode_id":packet["episode_id"],
      "source_video_sha256":packet["source_video_sha256"],
      "source_caption_sha256":packet["source_caption_sha256"],
      "record_status":"template_no_acceptances",
      "notes":"Reviewer claims are not cryptographically authenticated or automatically AV-verified.",
      "decisions":[{
         "task_id":key,
         "task_type":kind,
         "status":"pending",
         "reviewer_identifier":None,
         "review_note":None,
         "evidence":[ ],
         "accepted_speaker_identity":None,
         "accepted_vocal_delivery":None,
         "reviewer_attested":False
      } for key,(kind,_) in sorted(tasks.items())]
    }

def validate(packet,tasks,decisions):
    if not isinstance(decisions,dict) or decisions.get("schema")!="night-court-reviewed-script-claims/1":
        raise ValueError("Invalid review decisions schema")
    if (decisions.get("episode_id")!=packet["episode_id"]
       or decisions.get("source_video_sha256")!=packet["source_video_sha256"]
       or decisions.get("source_caption_sha256")!=packet["source_caption_sha256"]):
        raise ValueError("Reviewer's proposed result does not match original audiovisual sources")
    data=decisions.get("decisions")
    if not isinstance(data,list) or len(data)!=len(tasks):
        raise ValueError("Review must preserve every existing voice and frame task")
    observed=set()
    tallies=Counter()
    for d in data:
        if not isinstance(d,dict) or d.get("task_id") not in tasks or d["task_id"] in observed:
            raise ValueError("Duplicate/unknown source claim")
        observed.add(d["task_id"])
        kind,task=tasks[d["task_id"]]
        if d.get("task_type")!=kind or d.get("status") not in STATES:
            raise ValueError("Review type/state mismatch")
        state=d["status"]
        evid=d.get("evidence")
        if not isinstance(evid,list):raise ValueError("Evidence must be a list")
        if state=="pending":
            if (d.get("reviewer_identifier") is not None or d.get("accepted_speaker_identity") is not None
                or d.get("accepted_vocal_delivery") is not None or evid or d.get("reviewer_attested") is not False):
                raise ValueError("Pending review includes unjustified accepted source assertions")
        else:
            if (not isinstance(d.get("reviewer_identifier"),str)
                or len(d["reviewer_identifier"].strip())<3 or
                not isinstance(d.get("review_note"),str) or not d["review_note"].strip()
                or d.get("reviewer_attested") is not True):
                raise ValueError("Nonpending claims require identified review and self-attestation")
        # Each accepted method must actually cover the task being certified.
        # A valid AVI checksum with a completely unrelated time window is not
        # evidence for the original subtitle turn or sampled visual action.
        source_span=(task["source_caption_interval_ms"] if kind=="voice"
                     else task["source_interval_ms"])
        if (not isinstance(source_span,list) or len(source_span)!=2 or
            any(type(x) is not int for x in source_span) or
            not 0<=source_span[0]<source_span[1]<=1448256):
            raise ValueError("Original editorial task interval is invalid")
        methods=set()
        for ev in evid:
            if not isinstance(ev,dict) or ev.get("method") not in MODES:
                raise ValueError("Unrecognized original-source evidence method")
            if ev.get("source_video_sha256")!=packet["source_video_sha256"]:
                raise ValueError("Evidence from wrong original episode AVI")
            if not isinstance(ev.get("interval_ms"),list) or len(ev["interval_ms"])!=2:
                raise ValueError("Evidence source time range missing")
            a,b=ev["interval_ms"]
            if (type(a) is not int or type(b) is not int
                or a<0 or b<=a or b>1448256):
                raise ValueError("Evidence range outside original episode duration")
            if state=="accepted_by_reviewer" and (a>source_span[0] or b<source_span[1]):
                raise ValueError("Accepted evidence interval does not cover its source task")
            methods.add(ev["method"])
        if state=="accepted_by_reviewer":
            if kind=="voice":
                if not {"listened_original_audio","audited_source_caption"}.issubset(methods):
                    raise ValueError("Voice text cannot be accepted without original listening and source reading")
                if d.get("accepted_speaker_identity") is not None:
                    if ("synchronized_mouth_voice_review" not in methods or
                        "watched_continuous_original_video" not in methods):
                        raise ValueError("A visible person or cast roster alone does not identify a spoken voice")
                if d.get("accepted_vocal_delivery") is not None:
                    if not {"reviewed_isolated_voice","listened_original_audio"}.issubset(methods):
                        raise ValueError("Mixed soundtrack pitch or textual tone is insufficient delivery evidence")
            else:
                if "watched_continuous_original_video" not in methods:
                    raise ValueError("Sampled frame stills cannot independently accept timed physical action")
                if d.get("accepted_speaker_identity") is not None or d.get("accepted_vocal_delivery") is not None:
                    raise ValueError("A visual stage action is not a speaker/emotion assignment")
            tallies[f"{kind}_attested_acceptances"]+=1
        else:
            if d.get("accepted_speaker_identity") is not None or d.get("accepted_vocal_delivery") is not None:
                raise ValueError("Unaccepted review must not assign named speaker or vocal delivery")
            tallies[f"{kind}_{state}"]+=1
    if set(tasks)!=observed:raise ValueError("Some caption or motion source tasks disappeared")
    return {
      "schema":"night-court-reviewed-claims-validation/1",
      "episode_id":packet["episode_id"],
      "validated_claim_records":len(observed),
      "reviewer_attested_claims":sum(v for k,v in tallies.items() if k.endswith("_attested_acceptances")),
      "result_counts":dict(sorted(tallies.items())),
      "independent_av_verification_conducted_by_this_validator":False,
      "reviewer_identity_independently_authenticated":False,
      "original_subtitles_modified":False,
      "note":"Validation checks provenance and self-attested review methods, not whether a human actually watched/listened."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--write-template",action="store_true")
    p.add_argument("--validate",type=Path)
    a=p.parse_args()
    packet,tasks=load_packet()
    if a.write_template:
        path=DIR/"review-decisions-template.json"
        if path.exists():raise ValueError("Review template already exists")
        path.write_text(json.dumps(template(packet,tasks),indent=2)+"\n","utf-8")
        print("Generated seventeen explicit PENDING review decisions")
    if a.validate:
        decisions=json.loads(a.validate.read_text("utf-8"))
        status=validate(packet,tasks,decisions)
        print(json.dumps(status,indent=2))
    if not a.write_template and not a.validate:p.error("Use --write-template or --validate PATH")

if __name__=="__main__":main()
