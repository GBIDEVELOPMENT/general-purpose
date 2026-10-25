#!/usr/bin/env python3
"""Source-first physical action review. Never infer action truth from VLM JSON.

Create a private source-bound all-pending reviewer form, or validate a later
human-completed form. Emit repository-safe numeric provenance ONLY.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

from run_headless_video_description import SCHEMA as MODEL_SCHEMA
from review_video_stage_directions import valid_window

SCHEMA = "night-court-original-action-ledger-review/1"
SAFE_SCHEMA = "night-court-original-action-ledger-summary/1"
STATES = ("pending", "observed", "corrected", "absent", "uncertain")
FIELDS = ("initiator", "action_verb", "recipient_or_object", "visible_evidence",
          "timing_or_cut_note", "source_sound_note")
SHA = re.compile(r"[0-9a-f]{64}\Z")
REVIEWER = re.compile(r"[a-zA-Z0-9_.-]{1,80}\Z")
MAX_BYTES = 150000
LIMIT_ACTIONS = 24


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def verified_model(report):
    if not isinstance(report, dict) or report.get("schema") != MODEL_SCHEMA:
        raise ValueError("Not an original video model report")
    if report.get("script_or_claim_independently_accepted") is not False:
        raise ValueError("Input model cannot claim stage acceptance")
    source = report.get("source_video_sha256")
    if not isinstance(source,str) or not SHA.fullmatch(source) or report.get("verified_source_sha256") != source:
        raise ValueError("Original source movie hash verification missing")
    episodes = report.get("episode_id")
    if not isinstance(episodes,str) or not re.fullmatch(r"S0[1-9]E\d{2}",episodes):
        raise ValueError("Original-series episode identity missing")
    windows = report.get("windows")
    if not isinstance(windows,list) or len(windows) != 1:
        raise ValueError("One bounded source movie clip per action review")
    w = windows[0]
    valid_window(report,w)
    if w.get("shot_partition_verified") is not False:
        raise ValueError("Original shot partition cannot be assumed verified")
    return w


def template(report, model_sha):
    w = verified_model(report)
    if not SHA.fullmatch(model_sha):
        raise ValueError("Exact model report SHA invalid")
    return {
        "schema":SCHEMA,
        "episode_id":report["episode_id"],
        "source_video_sha256":report["source_video_sha256"],
        "source_window_ms":[w["start_ms"],w["end_ms"]],
        "source_model_report_sha256":model_sha,
        "reviewer_id":"editor-unassigned",
        "original_continuous_video_viewed":False,
        "original_synchronized_sound_reviewed":False,
        "source_native_frame_pts_verified":False,
        "source_action_review_complete":False,
        "actions":[{
            "action_id":"A01",
            "status":"pending",
            "initiator":None,
            "action_verb":None,
            "recipient_or_object":None,
            "visible_evidence":None,
            "timing_or_cut_note":None,
            "source_sound_note":None,
            "reviewer_confidence":"unassessed"
        }],
        "_instructions":"View the exact source film continuously, with synchronized soundtrack. Identify anonymous initiator and recipient only when actually visible. Add one entry per action, including misses; use status absent or uncertain if justified. Never paste VLM prose into evidence. A completed ledger is a reviewer attestation, not independently certified episode truth.",
    }


def summarize(report, model_sha, review, review_sha):
    w = verified_model(report)
    if not isinstance(review,dict) or review.get("schema") != SCHEMA:
        raise ValueError("Wrong source action review form")
    if (review.get("episode_id") != report["episode_id"] or
        review.get("source_video_sha256") != report["source_video_sha256"] or
        review.get("source_window_ms") != [w["start_ms"],w["end_ms"]] or
        review.get("source_model_report_sha256") != model_sha):
        raise ValueError("Model-source-window form mismatch")
    if not isinstance(review_sha,str) or not SHA.fullmatch(review_sha):
        raise ValueError("Exact private reviewer SHA invalid")
    reviewer=review.get("reviewer_id")
    if not isinstance(reviewer,str) or not REVIEWER.fullmatch(reviewer):
        raise ValueError("Bad reviewer identifier")
    video=review.get("original_continuous_video_viewed")
    sound=review.get("original_synchronized_sound_reviewed")
    pts=review.get("source_native_frame_pts_verified")
    complete=review.get("source_action_review_complete")
    if any(type(x) is not bool for x in (video,sound,pts,complete)):
        raise ValueError("Explicit source-review flags required")
    if complete and not (video and sound):
        raise ValueError("Cannot complete action record without source moving video and synchronized audio")
    if pts and not video:
        raise ValueError("Cannot verify native source PTS without video review")
    rows=review.get("actions")
    if not isinstance(rows,list) or len(rows) > LIMIT_ACTIONS:
        raise ValueError("Invalid number of action records")
    if len(rows) == 0 and not complete:
        raise ValueError("Empty action list requires source-review completion")
    ids=set()
    counts={status:0 for status in STATES}
    for entry in rows:
        if not isinstance(entry,dict) or set(entry) != {"action_id","status",*FIELDS,"reviewer_confidence"}:
            raise ValueError("Action fields must be complete, no extras")
        aid=entry["action_id"]
        if not isinstance(aid,str) or not REVIEWER.fullmatch(aid) or aid in ids:
            raise ValueError("Invalid/duplicate source action ID")
        ids.add(aid)
        state=entry["status"]
        if state not in STATES:
            raise ValueError("Unknown action verification status")
        counts[state]+=1
        if not video and state != "pending":
            raise ValueError("Unviewed original film cannot create a reviewed action")
        conf=entry["reviewer_confidence"]
        if conf not in ("unassessed","low","medium","high"):
            raise ValueError("Invalid reviewer confidence")
        if state == "pending":
            if conf != "unassessed" or any(entry[k] is not None for k in FIELDS):
                raise ValueError("Pending action must remain fully unknown")
        else:
            if conf == "unassessed":
                raise ValueError("Reviewed action must have a confidence")
            if state in ("observed","corrected"):
                for field in ("initiator","action_verb","recipient_or_object","visible_evidence"):
                    text=entry[field]
                    if not isinstance(text,str) or not 1 <= len(text.strip()) <= 400:
                        raise ValueError("Observed action must identify source-attested actor/verb/recipient/evidence")
            if state in ("absent","uncertain"):
                if any(entry[k] is not None for k in ("initiator","action_verb","recipient_or_object")):
                    raise ValueError("Unseen/uncertain action cannot assert a directional fact")
                if not isinstance(entry["visible_evidence"],str) or not entry["visible_evidence"].strip():
                    raise ValueError("Uncertain or absent requires reviewer source explanation")
            for field in FIELDS:
                value=entry[field]
                if value is not None and (not isinstance(value,str) or not 1<=len(value.strip())<=400):
                    raise ValueError("Oversized/invalid reviewer evidence")
    if complete and counts["pending"]:
        raise ValueError("Completed action ledger still contains pending entries")
    if not complete and counts["observed"]+counts["corrected"]+counts["absent"]+counts["uncertain"]:
        # A partial reviewed ledger is allowed, but is NOT source-complete.
        pass
    return {
        "schema":SAFE_SCHEMA,"episode_id":report["episode_id"],
        "source_video_sha256":report["source_video_sha256"],
        "source_window_ms":[w["start_ms"],w["end_ms"]],
        "source_model_report_sha256":model_sha,
        "private_reviewer_document_sha256":review_sha,
        "reviewer_id":reviewer,"original_continuous_video_viewed":video,
        "original_synchronized_sound_reviewed":sound,
        "source_native_frame_pts_verified":pts,
        "source_action_review_complete":complete,
        "action_status_counts":counts,
        "directed_actions_reviewed":counts["observed"]+counts["corrected"],
        "stage_directions_automatically_accepted":0,
        "complete_original_episode_certified":False,
        "model_prose_or_original_dialogue_exported":False,
    }


def load(path):
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_BYTES:
        raise ValueError("Missing or oversized private report")
    raw=path.read_bytes()
    return json.loads(raw), digest(raw)


def write_new(path, contents, sources):
    if path.exists() or path.resolve() in {p.resolve() for p in sources}:
        raise ValueError("Refusing to overwrite source or existing review")
    encoded=(json.dumps(contents,indent=2,ensure_ascii=False)+"\n").encode()
    if len(encoded)>MAX_BYTES:
        raise ValueError("Action report exceeds size budget")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(encoded)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-report",required=True,type=Path)
    p.add_argument("--new-private-form",type=Path)
    p.add_argument("--private-review",type=Path)
    p.add_argument("--safe-summary",type=Path)
    a=p.parse_args()
    if bool(a.new_private_form)==bool(a.private_review) or (a.private_review and not a.safe_summary):
        p.error("Choose either new private form or existing private review plus safe summary")
    report,report_sha=load(a.model_report)
    if a.new_private_form:
        write_new(a.new_private_form,template(report,report_sha),[a.model_report])
        print("Source-bound action review prepared, zero stage approvals")
    else:
        review,review_sha=load(a.private_review)
        summary=summarize(report,report_sha,review,review_sha)
        write_new(a.safe_summary,summary,[a.model_report,a.private_review])
        print("Source-safe action counts written, stage direction approvals: zero")


if __name__=="__main__":
    main()
