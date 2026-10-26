#!/usr/bin/env python3
"""Make the next 100-original-unit P0/P1 review queue from private editorial v16.

Preserves real S01 SRT cue windows and S09 provisional original-audio ASR
locators. Does not turn an untimed paragraph into an actual subtitle timecode
or change already accepted (provisional) character roles.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from build_pilot_fan_beat_cards import ROOT,load_witness
from render_current_pilot_screenplays import SOURCE,original_reading_order,sha
from plan_next_speaker_review_v9 import load_s09_locator,make_queue
from apply_manual_context_pilot_review_v16 import SCHEMA as EDITORIAL_SCHEMA,counts

def build(root:Path,v16:Path,locator:Path,output:Path)->dict:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private original dialogue review cannot be committed")
    raw=(v16/"pilot-manual-context-speaker-v16.jsonl").read_bytes()
    m=json.loads((v16/"pilot-manual-context-speaker-v16-manifest.json").read_text("utf-8"))
    if (m.get("schema")!=EDITORIAL_SCHEMA
        or m.get("current_v16_reader_sha256")!=sha(raw)
        or m.get("current_reader_blocks")!=727
        or m.get("source_coverage",{}).get("fully_provisionally_named_source_units")!=651
        or m.get("source_coverage",{}).get("source_units_with_any_unknown_voice")!=100
        or m.get("actor_role_identifications_independently_original_audio_verified")!=0):
        raise ValueError("Current unreviewed manual v16 reader SHA/count drift")
    rows=[json.loads(t) for t in raw.decode("utf-8").splitlines() if t.strip()]
    if len(rows)!=727 or counts(rows)!=m["source_coverage"]:
        raise ValueError("Manual current role provenance differs from source rows")
    for ep in SOURCE:
        meta,_=load_witness(root,ep)
        if meta["sha256"]!=SOURCE[ep][0] or any(
            x["original_source_sha256"]!=meta["sha256"] for x in rows if x["episode_id"]==ep
        ):
            raise ValueError("Held original pilot witness edition changed")
    internal=json.loads((root/"research/probable-internal-speaker-switches-v1.json").read_text("utf-8"))
    source_audio=load_s09_locator(locator)
    review,summary=make_queue(original_reading_order(rows),source_audio,internal,
                               expected_named=651,expected_unknown=100)
    if (summary["remaining_unknown_original_source_units_by_episode"]!={"S01E01":21,"S09E19":79}
        or summary["unknown_source_unit_review_records"]<100
        or summary["original_untimed_S09_captions_modified"] is not False
        or summary["new_voices_human_accepted"]!=0
        or not any(x["episode_id"]=="S09E19" and
                   "C277.1" in x["unidentified_original_unit_refs"] for x in review)
        or not any(x["episode_id"]=="S09E19" and
                   x["source_reading_ref"]=="C129.1" and
                   x["model_proposed_character"] is None for x in review)
        or not any(x["episode_id"]=="S01E01" and
                   "C219.1" in x["unidentified_original_unit_refs"] and
                   x["source_reading_ref"].endswith("SOURCE-TURN-2") for x in review)):
        raise ValueError("Unsafe or incomplete remaining 100 source unit review queue")
    summary["current_v16_source_sha256"]=sha(raw)
    summary["new_automatic_roles_proposed_from_editorial_review"]=0
    summary["prior_contextual_editorial_assignments_unverified"]=32
    summary["preexisting_named_role_corrections_unverified"]=2
    summary["current_original_cue_p0_unknown_handoff"]="S09E19:C277.1"
    output.mkdir(parents=True,exist_ok=True)
    (output/"remaining-100-speaker-review.jsonl").write_text(
        "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in review),"utf-8")
    (output/"remaining-100-speaker-review-summary.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)+"\n","utf-8")
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--v16-root",type=Path,required=True)
    p.add_argument("--s09-original-audio-locator",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    m=build(a.root,a.v16_root,a.s09_original_audio_locator,a.output)
    print("Manual-context P0/P1 review: 100 original source units with remaining UNKNOWN voices,",
          m["remaining_unknown_original_source_units_by_episode"],
          "audio candidate windows",m["s09_actual_audio_window_leads"],
          "zero independently certified original speakers")

if __name__=="__main__":
    main()
