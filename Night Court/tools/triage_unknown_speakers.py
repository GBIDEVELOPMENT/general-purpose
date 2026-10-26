#!/usr/bin/env python3
"""Rank unresolved Night Court voices for targeted source-audio review, P0/P1 FIRST.

This emits a *private review queue* with source text and nearby provisional
labels, not automatic new names. S01 time windows are SRT-based approximate
review pointers; S09 held paragraphs remain untimed.
"""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from pathlib import Path

from build_pilot_character_evidence import ROOT, records_for_episode
from fan_sqlite_index import apply_speaker_improvements

SCHEMA = "night-court-private-speaker-identity-first-review/1"


def rank_unknowns(rows: list[dict], review_flags: list[dict],
                  require_full: bool = True) -> tuple[list[dict], dict]:
    grouped = {}
    for ep in ("S01E01", "S09E19"):
        grouped[ep] = [r for r in rows if r["episode_id"] == ep]
    output = []
    for ep, entries in grouped.items():
        for pos, record in enumerate(entries):
            if record["candidate_role"] is not None:
                continue
            neighbors = entries[max(0,pos-2):pos] + entries[pos+1:pos+3]
            immediate_before = entries[pos-1] if pos else None
            immediate_after = entries[pos+1] if pos+1 < len(entries) else None
            ref = record["source_reading_ref"]
            cueparts = record["original_source_part_refs"]
            words = re.findall(r"\b[\w']+\b", record["caption_text"])
            both_known = (immediate_before is not None and immediate_after is not None
                          and immediate_before["candidate_role"] is not None
                          and immediate_after["candidate_role"] is not None)
            adjacency_names = []
            for other in (immediate_before, immediate_after):
                if other is not None and other["candidate_role"] is not None:
                    if other["candidate_role"] not in adjacency_names:
                        adjacency_names.append(other["candidate_role"])
            multi_part = any(not ref.endswith(".1") for ref in cueparts)
            continuation = bool(re.match(r"^(?:\.\.\.|[a-z])", record["caption_text"].lstrip()))
            score = 10
            triggers = ["unidentified_original_source_voice"]
            if len(words) <= 4:
                score += 6
                triggers.append("short_reply_identity_ambiguous")
            if multi_part:
                score += 8
                triggers.append("within_cue_speaker_split_needs_validation")
            if len(cueparts) > 1:
                score += 4
                triggers.append("reader_joins_multiple_original_paragraphs")
            if both_known:
                score += 5
                triggers.append("sandwiched_between_named_editorial_roles")
            if continuation:
                score += 6
                triggers.append("syntactic_continuation_possible")
            if immediate_before is not None and immediate_before["candidate_role"] is None:
                score += 2
                triggers.append("neighboring_unidentified_speech_cluster")
            if immediate_after is not None and immediate_after["candidate_role"] is None:
                score += 2
                if "neighboring_unidentified_speech_cluster" not in triggers:
                    triggers.append("neighboring_unidentified_speech_cluster")
            timings = record["source_original_times_ms"]
            if timings is None:
                window = None
            else:
                start = min(x["start_ms"] for x in timings)
                end = max(x["end_ms"] for x in timings)
                window = {"srt_approx_start_ms": max(0, start-1500),
                          "srt_approx_end_ms": end+1500,
                          "is_verified_audio_alignment": False}
            output.append({
                "schema": SCHEMA,
                "episode_id": ep,
                "source_ref": ref,
                "reading_block_id": record["reading_block_id"],
                "source_sha256": record["original_source_sha256"],
                "original_source_units_unresolved": len(cueparts),
                "priority_score": score,
                "triage_triggers": triggers,
                "source_text": record["caption_text"],
                "adjacent_provisionally_named_characters_for_review_not_attribution":
                    adjacency_names,
                "neighboring_source_context": [{
                    "source_ref": n["source_reading_ref"],
                    "role_status": n["role_attribution_status"],
                    "provisional_role": n["candidate_role"],
                    "dialogue": n["caption_text"],
                } for n in neighbors],
                "review_srt_window": window,
                "original_untimed": record["original_source_untimed"],
                "proposed_character": None,
                "original_soundtrack_reviewed": False,
                "original_video_lips_confirmed": False,
                "editorial_acceptance": "P0_P1_REVIEW_REQUIRED",
            })
    for flag in review_flags:
        ep,ref=flag["episode_id"],flag["source_ref"]
        candidates=[r for r in grouped.get(ep,[]) if r["source_reading_ref"]==ref]
        if len(candidates)!=1:
            raise ValueError("Review flag does not refer to one original source block")
        row=candidates[0]
        output.append({
            "schema": SCHEMA,
            "episode_id": ep,
            "source_ref": ref,
            "reading_block_id": row["reading_block_id"],
            "source_sha256": row["original_source_sha256"],
            "priority_score": 40,
            "triage_triggers": ["potentially_false_existing_speaker_attribution"],
            "source_text": row["caption_text"],
            "existing_provisional_role_to_review": flag["current_provisional_role"],
            "reason_for_independent_audio_review": flag["reason"],
            "proposed_character": None,
            "original_soundtrack_reviewed": False,
            "original_video_lips_confirmed": False,
            "editorial_acceptance": "P1_POTENTIAL_FALSE_POSITIVE_REVIEW_REQUIRED",
        })
    output.sort(key=lambda x:(-x["priority_score"],x["episode_id"],x["source_ref"]))
    counts=Counter()
    for row in output:
        if row["editorial_acceptance"]=="P0_P1_REVIEW_REQUIRED":
            counts[row["episode_id"]]+=row["original_source_units_unresolved"]
    summary={
        "schema": SCHEMA,
        "source_units_unidentified_by_episode": dict(sorted(counts.items())),
        "source_units_unidentified": sum(counts.values()),
        "review_queue_items": len(output),
        "suspected_existing_wrong_labels": len(review_flags),
        "automatically_accepted_new_names": 0,
        "independently_audio_confirmed_by_triage": 0,
        "remaining_unverified_candidates": len(output),
    }
    if require_full and (counts["S01E01"], counts["S09E19"], sum(counts.values()))!=(97,164,261):
        raise ValueError("Unexpected speaker UNKNOWN unit ledger, recheck v6 overlays")
    return output,summary


def create(root: Path, v6_root: Path, output: Path) -> dict:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private spoken text review packets must not be written to repo")
    proof=json.loads((v6_root/"speaker-improvement-manifest.json").read_text("utf-8"))
    if (proof.get("remaining_unidentified_source_units")!=261
        or proof.get("new_provisional_named_source_units")!=490
        or proof.get("original_audio_speaker_identities_verified_by_this_change")!=0):
        raise ValueError("Invalid current external speaker overlay status")
    prior=[r for ep in ("S01E01","S09E19") for r in records_for_episode(root,ep)]
    scripts=[{
        "episode_id":ep,
        "retrieval_text":(v6_root/ep/"screenplay-external-speakers-v6.md").read_text("utf-8")
    } for ep in ("S01E01","S09E19")]
    entries=[
        json.loads(x) for x in
        (v6_root/"speaker-improvement-overrides.jsonl").read_text("utf-8").splitlines()
        if x.strip()
    ]
    adjusted=apply_speaker_improvements(scripts,prior,entries,require_full=True)
    import hashlib
    original_ledger=json.loads((root/"research/pilot-speaker-external-quote-improvements-v1.json").read_text("utf-8"))
    flags=original_ledger["additional_review_flags"]
    queue,summary=rank_unknowns(adjusted,flags,require_full=True)
    output.mkdir(parents=True,exist_ok=True)
    (output/"speaker-identity-first-review.jsonl").write_text(
        "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in queue),"utf-8"
    )
    (output/"speaker-identity-first-review-summary.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n","utf-8"
    )
    return summary


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--speaker-v6-root",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    m=create(args.root,args.speaker_v6_root,args.output)
    print(f"{m['source_units_unidentified']} original units remain UNKNOWN across "
          f"{m['review_queue_items']} ranked P0/P1 review items; no dialogue printed")


if __name__=="__main__":
    main()
