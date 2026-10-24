#!/usr/bin/env python3
"""Check S09E19 review attestations without inventing original paragraph timecodes.

The original S09E19 transcript has 347 UNTIMED paragraphs. The separate
original-video excerpt has five audio-match proposals and six sampled-image
states. This validator checks reported provenance and reviewer attestation,
not whether that reviewer truly watched or listened.
"""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"seasons/S09/S09E19/derived/editorial-review-v1"
WORKLIST=BASE/"untimed-scene-review-queue.json"
TEMPLATE=BASE/"review-decisions-template.json"
STATES={"pending","accepted_by_reviewer","rejected_by_reviewer","needs_source_recheck"}
METHODS={
 "listened_original_audio",
 "audited_original_untimed_paragraph",
 "watched_continuous_original_video",
 "synchronized_mouth_voice_review",
 "reviewed_isolated_original_voice",
}
VIDEOWINDOW=(900000,925000)
SOURCE_VIDEO_SHA="51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649"
SOURCE_TEXT_SHA="659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
SHA_RE=re.compile(r"^[0-9a-f]{64}$")

def load_worklist():
    p=json.loads(WORKLIST.read_text("utf-8"))
    tasks=p.get("tasks")
    if (p.get("schema")!="night-court-s09e19-untimed-editorial-review-queue/1"
        or p.get("episode_id")!="S09E19"
        or p.get("original_video_sha256")!=SOURCE_VIDEO_SHA
        or p.get("original_untimed_source_sha256")!=SOURCE_TEXT_SHA
        or p.get("original_paragraph_count")!=347
        or p.get("original_source_paragraphs_with_actual_timecodes")!=0
        or p.get("video_excerpt_ms")!=list(VIDEOWINDOW)
        or p.get("source_asr_candidate_count")!=5
        or p.get("sampled_video_event_count")!=6
        or p.get("individual_review_tasks")!=11
        or p.get("independently_accepted_dialogue_matches")!=0
        or p.get("independently_accepted_physical_actions")!=0
        or not isinstance(tasks,list) or len(tasks)!=11):
        raise ValueError("S09E19 original-untimed episode source contract changed")
    byid={t["task_id"]:t for t in tasks}
    if len(byid)!=11:
        raise ValueError("Duplicate original untimed review task ID")
    for t in tasks:
        if t["kind"]=="proposed_dialogue_match":
            if (t.get("source_paragraph_timestamp_ms") is not None
                or t.get("source_audio_segment_independently_verified") is not False
                or t.get("mouth_voice_synchronization_verified") is not False):
                raise ValueError("Source paragraph was timed or incorrectly audio-accepted")
        elif t["kind"]=="sampled_visual_stage_claim":
            if (t.get("continuous_video_action_verified") is not False
                or t.get("original_frame_presentation_times_verified") is not False):
                raise ValueError("Sampled source frames incorrectly AV-accepted")
        else:
            raise ValueError("Unknown original source review task")
    return p,byid

def template(p,byid):
    return {
       "schema":"night-court-s09e19-editorial-review-decisions/1",
       "episode_id":"S09E19",
       "source_video_sha256":p["original_video_sha256"],
       "source_original_untimed_text_sha256":p["original_untimed_source_sha256"],
       "original_source_paragraphs_remain_untimed":True,
       "record_status":"all_pending_no_accepted_original_AV_claims",
       "reviewer_identity_authenticated_by_validator":False,
       "decisions":[{
          "task_id":task_id,"kind":task["kind"],
          "status":"pending","reviewer_identifier":None,
          "review_note":None,"reviewer_attested":False,
          "evidence":[],
          "accepted_speaker_identity":None,
          "accepted_vocal_delivery":None
       } for task_id,task in sorted(byid.items())]
    }

def validate(p,byid,d):
    if (not isinstance(d,dict) or
        set(d)!=set(template(p,byid)) or
        d.get("schema")!="night-court-s09e19-editorial-review-decisions/1"
        or d.get("episode_id")!="S09E19"
        or d.get("source_video_sha256")!=SOURCE_VIDEO_SHA
        or d.get("source_original_untimed_text_sha256")!=SOURCE_TEXT_SHA
        or d.get("original_source_paragraphs_remain_untimed") is not True
        or d.get("reviewer_identity_authenticated_by_validator") is not False
        or d.get("record_status") not in {
           "all_pending_no_accepted_original_AV_claims","source_review_attestations_present"
        }):
        raise ValueError("Review result has changed immutable original source identity or claimed verification")
    records=d.get("decisions")
    if not isinstance(records,list) or len(records)!=len(byid):
        raise ValueError("Incomplete original source review decisions")
    seen=set(); counts=Counter()
    for result in records:
        if not isinstance(result,dict) or set(result)!=set(template(p,byid)["decisions"][0]):
            raise ValueError("Review record has unknown or missing claim fields")
        task_id=result.get("task_id")
        if task_id not in byid or task_id in seen:
            raise ValueError("Duplicate or unknown source paragraph/action task")
        seen.add(task_id)
        task=byid[task_id]
        kind=task["kind"]
        state=result.get("status")
        if result.get("kind")!=kind or state not in STATES:
            raise ValueError("Source review task kind or status changed")
        ident=result.get("reviewer_identifier")
        note=result.get("review_note")
        if state=="pending":
            if (ident is not None or note is not None or result.get("reviewer_attested") is not False
                or result.get("evidence")!=[]
                or result.get("accepted_speaker_identity") is not None
                or result.get("accepted_vocal_delivery") is not None):
                raise ValueError("Pending review must not carry evidence/acceptance claims")
        else:
            if (not isinstance(ident,str) or len(ident.strip())<3
                or not isinstance(note,str) or len(note.strip())<10
                or result.get("reviewer_attested") is not True):
                raise ValueError("Nonpending source decision requires identified reviewer attestation")
        reviewed=result.get("evidence")
        if not isinstance(reviewed,list):
            raise ValueError("Evidence must be structured original-source citations")
        expected=(task["model_proposed_video_time_interval_ms"]
                  if kind=="proposed_dialogue_match"
                  else task["sampled_video_interval_ms"])
        observed_methods=set()
        for ev in reviewed:
            if (not isinstance(ev,dict) or set(ev)!={
                "method","source_video_sha256","original_untimed_source_sha256","interval_ms"
            } or ev["method"] not in METHODS
                or ev["source_video_sha256"]!=SOURCE_VIDEO_SHA
                or ev["original_untimed_source_sha256"]!=SOURCE_TEXT_SHA):
                raise ValueError("Source evidence method, SHA or fields invalid")
            bounds=ev["interval_ms"]
            if (not isinstance(bounds,list) or len(bounds)!=2
                or any(type(x) is not int for x in bounds)
                or not 0<=bounds[0]<bounds[1]<=1320144):
                raise ValueError("Source review evidence interval invalid")
            if state=="accepted_by_reviewer" and (bounds[0]>expected[0] or bounds[1]<expected[1]):
                raise ValueError("Accepted review cited a partial or unrelated source-video moment")
            observed_methods.add(ev["method"])
        if state=="accepted_by_reviewer":
            if kind=="proposed_dialogue_match":
                if not {"listened_original_audio","audited_original_untimed_paragraph"}.issubset(observed_methods):
                    raise ValueError("Cannot accept original untimed paragraph match without listening and source paragraph audit")
                if result["accepted_speaker_identity"] is not None:
                    if not {"watched_continuous_original_video","synchronized_mouth_voice_review"}.issubset(observed_methods):
                        raise ValueError("No named speaker from costumes, lexical text or sampled image alone")
                if result["accepted_vocal_delivery"] is not None:
                    if "reviewed_isolated_original_voice" not in observed_methods:
                        raise ValueError("Mixed soundtrack model pitch does not prove emotional delivery")
            else:
                if "watched_continuous_original_video" not in observed_methods:
                    raise ValueError("Cannot certify physical action from sampled frames")
                if (result["accepted_speaker_identity"] is not None
                    or result["accepted_vocal_delivery"] is not None):
                    raise ValueError("A stage-action record cannot identify an audio speaker")
            counts[kind+"_attested_acceptance"]+=1
        else:
            if (result["accepted_speaker_identity"] is not None
                or result["accepted_vocal_delivery"] is not None):
                raise ValueError("Rejected, pending or recheck cannot assign character or delivery")
            counts[kind+"_"+state]+=1
    pending=all(rec["status"]=="pending" for rec in records)
    if d["record_status"]!=(
        "all_pending_no_accepted_original_AV_claims" if pending
        else "source_review_attestations_present"):
        raise ValueError("Top-level review decision state is inconsistent")
    return {
      "schema":"night-court-s09e19-review-evidence-validator-report/1",
      "episode_id":"S09E19",
      "source_original_paragraphs_still_untimed":True,
      "reviewed_claim_records":len(seen),
      "reviewer_attested_acceptances":sum(v for k,v in counts.items() if k.endswith("_attested_acceptance")),
      "source_review_status_counts":dict(sorted(counts.items())),
      "independent_original_AV_review_performed_by_validator":False,
      "reviewer_identity_independently_verified_by_validator":False,
      "production_script_certified":False
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--validate",type=Path)
    ap.add_argument("--write-template",action="store_true")
    a=ap.parse_args()
    p,tasks=load_worklist()
    if a.write_template:
        if TEMPLATE.exists():
            raise ValueError("Existing reviewer template must not be overwritten")
        TEMPLATE.write_text(json.dumps(template(p,tasks),indent=2)+"\n","utf-8")
    if a.validate:
        print(json.dumps(validate(p,tasks,json.loads(a.validate.read_text("utf-8"))),indent=2))
    if not a.write_template and a.validate is None:
        ap.error("Use --validate PATH or --write-template")

if __name__=="__main__":
    main()
