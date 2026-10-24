#!/usr/bin/env python3
"""Strict S09E19 original-untimed paragraph reviewer claim gate.

A valid decision is a SELF ATTESTATION. This validator has not listened to
the AVI, verified reviewer identity, viewed original continuous video or
established that the source text originally possessed timestamp metadata.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"seasons/S09/S09E19/derived/editorial-review-v1"
INPUT=BASE/"untimed-scene-review-queue.json"
TEMPLATE=BASE/"review-decisions-template.json"
STATES={"pending","accepted_by_reviewer","rejected_by_reviewer","needs_source_recheck"}
METHODS={
 "listened_original_audio", "compared_original_untimed_paragraph",
 "confirmed_exact_paragraph_occurrence", "watched_continuous_original_video",
 "compared_original_sampled_frames", "synchronized_mouth_voice_review",
 "reviewed_isolated_voice"
}
DECISION_KEYS={
 "task_id", "kind", "status", "reviewer_identifier", "reviewer_attested",
 "review_note", "evidence", "accepted_speaker_identity",
 "accepted_delivery_annotation", "accepted_stage_direction",
 "verified_source_video_interval_ms", "original_source_paragraph_timestamp_ms"
}
VIDEO_RUNTIME_MS=1320144
SHA_RE=re.compile(r"^[0-9a-f]{64}$")


def load():
    q=json.loads(INPUT.read_text("utf-8"))
    tasks=q.get("tasks",[])
    if (q.get("schema")!="night-court-s09e19-untimed-editorial-review-queue/1"
        or q.get("episode_id")!="S09E19"
        or q.get("original_paragraph_count")!=347
        or q.get("original_source_paragraphs_with_actual_timecodes")!=0
        or q.get("video_excerpt_ms")!=[900000,925000]
        or q.get("individual_review_tasks")!=11 or len(tasks)!=11
        or len({t["task_id"] for t in tasks})!=11
        or q.get("independently_accepted_dialogue_matches")!=0
        or q.get("independently_accepted_physical_actions")!=0
        or q.get("speaker_identity_verified") is not False):
        raise ValueError("S09E19 unaccepted original-source work queue changed")
    if not all(SHA_RE.fullmatch(q.get(key,"")) for key in
        ("original_video_sha256","original_untimed_source_sha256")):
        raise ValueError("Missing original episode source fingerprints")
    return q, {t["task_id"]:t for t in tasks}


def template(q,tasks):
    return {
      "schema":"night-court-s09e19-untimed-reviewer-decisions/1",
      "episode_id":q["episode_id"],
      "source_original_video_sha256":q["original_video_sha256"],
      "source_original_untimed_text_sha256":q["original_untimed_source_sha256"],
      "original_paragraphs_have_no_source_timecodes":True,
      "record_status":"all_pending_no_audiovisual_acceptance",
      "decisions":[{
        "task_id":task_id,
        "kind":t["kind"],
        "status":"pending",
        "reviewer_identifier":None,
        "reviewer_attested":False,
        "review_note":None,
        "evidence":[],
        "accepted_speaker_identity":None,
        "accepted_delivery_annotation":None,
        "accepted_stage_direction":None,
        "verified_source_video_interval_ms":None,
        "original_source_paragraph_timestamp_ms":None
      } for task_id,t in tasks.items()]
    }


def interval(value, label):
    if (not isinstance(value,list) or len(value)!=2 or
        type(value[0]) is not int or type(value[1]) is not int or
        not 0<=value[0]<value[1]<=VIDEO_RUNTIME_MS):
        raise ValueError(label+" interval is not a valid original AVI time")
    return value


def validate(q,tasks,proposed):
    if (not isinstance(proposed,dict) or
        proposed.get("schema")!="night-court-s09e19-untimed-reviewer-decisions/1"
        or proposed.get("episode_id")!=q["episode_id"]
        or proposed.get("source_original_video_sha256")!=q["original_video_sha256"]
        or proposed.get("source_original_untimed_text_sha256")!=q["original_untimed_source_sha256"]
        or proposed.get("original_paragraphs_have_no_source_timecodes") is not True):
        raise ValueError("Review proposed against another episode, caption source or time policy")
    entries=proposed.get("decisions")
    if not isinstance(entries,list) or len(entries)!=len(tasks):
        raise ValueError("Review must preserve all eleven original source worklist tasks")
    seen=set()
    totals=Counter()
    for d in entries:
        if not isinstance(d,dict) or set(d)!=DECISION_KEYS:
            raise ValueError("Unsupported decision field, including potential fake source timestamp")
        task_id=d["task_id"]
        if task_id not in tasks or task_id in seen:
            raise ValueError("Repeated, missing or unknown original evidence task")
        seen.add(task_id)
        src=tasks[task_id]
        if d["kind"]!=src["kind"] or d["status"] not in STATES:
            raise ValueError("Incorrect original AV task type or acceptance state")
        if d["original_source_paragraph_timestamp_ms"] is not None:
            raise ValueError("Original S09E19 untimed paragraph cannot gain an invented timecode")
        state=d["status"]
        accepted=state=="accepted_by_reviewer"
        if accepted and d["reviewer_attested"] is not True:
            raise ValueError("Acceptance must be explicitly reviewer-attested")
        if state!="pending":
            if (not isinstance(d["reviewer_identifier"],str)
                or len(d["reviewer_identifier"].strip())<3
                or not isinstance(d["review_note"],str) or not d["review_note"].strip()
                or d["reviewer_attested"] is not True):
                raise ValueError("Reviewed decisions require self-attested independent reviewer record")
        else:
            if (d["reviewer_identifier"] is not None or
                d["review_note"] is not None or
                d["reviewer_attested"] is not False or
                d["evidence"] or
                d["accepted_speaker_identity"] is not None or
                d["accepted_delivery_annotation"] is not None or
                d["accepted_stage_direction"] is not None or
                d["verified_source_video_interval_ms"] is not None):
                raise ValueError("Pending task contains misleading review or acceptance fields")
        evid=d["evidence"]
        if not isinstance(evid,list):
            raise ValueError("Reviewer source evidence must be a list")
        task_interval=(src["model_proposed_video_time_interval_ms"]
                       if src["kind"]=="proposed_dialogue_match"
                       else src["sampled_video_interval_ms"])
        interval(task_interval,"Original source task")
        methods=set()
        covers=[]
        for e in evid:
            if (not isinstance(e,dict) or set(e)!={"method","source_original_video_sha256","source_video_interval_ms"}
                or e["method"] not in METHODS
                or e["source_original_video_sha256"]!=q["original_video_sha256"]):
                raise ValueError("Original source reviewer evidence method or fingerprint is invalid")
            a,b=interval(e["source_video_interval_ms"],"Review evidence")
            if accepted and (a>task_interval[0] or b<task_interval[1]):
                raise ValueError("Accepted review evidence omits part of proposed source task window")
            methods.add(e["method"])
            covers.append([a,b])
        if accepted:
            if src["kind"]=="proposed_dialogue_match":
                mandatory={"listened_original_audio","compared_original_untimed_paragraph",
                           "confirmed_exact_paragraph_occurrence"}
                if not mandatory.issubset(methods):
                    raise ValueError("Untimed paragraph cannot be accepted from an ASR lexical match alone")
                if d["accepted_stage_direction"] is not None:
                    raise ValueError("A proposed spoken paragraph is not a physical stage direction")
                if d["accepted_speaker_identity"] is not None:
                    if not {"watched_continuous_original_video","synchronized_mouth_voice_review"}.issubset(methods):
                        raise ValueError("Speaker identity requires continuous mouth/voice source review")
                if d["accepted_delivery_annotation"] is not None:
                    if "reviewed_isolated_voice" not in methods:
                        raise ValueError("Vocal delivery requires original isolated voice review")
                claimed=d["verified_source_video_interval_ms"]
                if claimed is not None:
                    x,y=interval(claimed,"Human-confirmed derived video association")
                    if not any(a<=x<y<=b for a,b in covers):
                        raise ValueError("Confirmed derived AVI interval not covered by listened source")
            else:
                if not {"watched_continuous_original_video","compared_original_sampled_frames"}.issubset(methods):
                    raise ValueError("Sampled stills alone cannot certify a physical action")
                if not isinstance(d["accepted_stage_direction"],str) or not d["accepted_stage_direction"].strip():
                    raise ValueError("Accepted physical stage claim needs explicit reviewer wording")
                if (d["accepted_speaker_identity"] is not None or
                    d["accepted_delivery_annotation"] is not None or
                    d["verified_source_video_interval_ms"] is not None):
                    raise ValueError("Visual event cannot silently assign voices or derived utterance timings")
            totals[src["kind"]+"_self_attested_acceptances"]+=1
        elif any(d[key] is not None for key in (
             "accepted_speaker_identity","accepted_delivery_annotation",
             "accepted_stage_direction","verified_source_video_interval_ms")):
            raise ValueError("Nonaccepted original source task cannot publish positive claims")
        else:
            totals[src["kind"]+"_"+state]+=1
    if seen!=set(tasks):raise ValueError("Original source review worklist tasks were dropped")
    return {
        "schema":"night-court-s09e19-untimed-review-decision-validation/1",
        "episode_id":"S09E19",
        "review_task_records":len(seen),
        "self_attested_acceptance_count":sum(v for k,v in totals.items() if k.endswith("_self_attested_acceptances")),
        "status_counts":dict(sorted(totals.items())),
        "original_paragraph_timecodes_introduced":False,
        "reviewer_identity_independently_authenticated":False,
        "original_audio_or_continuous_video_actually_checked_by_this_validator":False,
        "full_episode_av_accepted":False,
        "note":"Schema and reviewer self-attestation check only; source truth remains a separate audiovisual/reviewer task."
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--write-template",action="store_true")
    ap.add_argument("--validate",type=Path)
    opts=ap.parse_args()
    q,tasks=load()
    if opts.write_template:
        TEMPLATE.write_text(json.dumps(template(q,tasks),indent=2,ensure_ascii=False)+"\n","utf-8")
    if opts.validate:
        d=json.loads(opts.validate.read_text("utf-8"))
        print(json.dumps(validate(q,tasks,d),indent=2))
    if not opts.write_template and not opts.validate:
        ap.error("Use --write-template or --validate PATH")


if __name__=="__main__":
    main()
