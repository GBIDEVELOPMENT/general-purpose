#!/usr/bin/env python3
"""One-pass, source-guarded AV editorial queue for canonical Night Court pilots.

Does not run a recognizer, watch film, certify actors or publish another script
revision. All original dialogue remains in saved-private/pilot-current. Run it
once after each *canonical* publication; amend a stable decision file, not v23.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

EPISODES = ("S01E01", "S09E19")
# Verified full original AVI SHA digests from episode source evidence, not SRT.
VIDEO_SHA = {
    "S01E01": "5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962",
    "S09E19": "51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649",
}
BATCH_BLOCKS = 12
SCHEMA = "night-court-single-pass-source-av-editorial/1"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def load_episode(snapshot: Path, episode: str):
    if episode not in EPISODES:
        raise ValueError("Unsupported pilot episode")
    manifest = json.loads((snapshot / "working-screenplay-layout-manifest.json").read_text("utf-8"))
    expected = manifest["episodes"][episode]
    source = snapshot / (episode + "-working-screenplay-provenance.jsonl")
    manuscript = snapshot / (episode + "-working-screenplay.md")
    script_sha = hashlib.sha256(manuscript.read_bytes()).hexdigest()
    if script_sha != manifest["manuscript_sha256"][episode]:
        raise ValueError("Canonical manuscript has drifted")
    rows = [json.loads(line) for line in source.read_text("utf-8").splitlines() if line.strip()]
    if len(rows) != expected["source_blocks"]:
        raise ValueError("Canonical provenance row count mismatch")
    source_refs, block_ids = set(), set()
    source_sha = None
    for r in rows:
        if r["reading_block_id"] in block_ids:
            raise ValueError("Duplicate source reading block ID")
        block_ids.add(r["reading_block_id"])
        refs = r.get("original_source_part_refs")
        if not isinstance(refs, list) or not refs:
            raise ValueError("Reading block lost original caption source")
        source_refs.update(refs)
        if source_sha is None:
            source_sha = r["source_sha256"]
        if source_sha != r["source_sha256"] or len(source_sha) != 64:
            raise ValueError("Inconsistent immutable source witness SHA")
        if r.get("actual_original_av_reviewer_accepted") is not False:
            raise ValueError("Unproven previous AV certification")
        if not isinstance(r.get("display_group_id"), int):
            raise ValueError("No stable displayed-turn proposal")
        if episode == "S09E19" and r["source_cue_times_not_subturn_times_ms"] is not None:
            raise ValueError("S09 source is untimed, cannot create fake offsets")
    if len(source_refs) != expected["source_units"]:
        raise ValueError("Source part union is not complete")
    if source_sha not in manuscript.read_text("utf-8"):
        raise ValueError("Manuscript lacks immutable original witness SHA")
    return manifest, rows, source_sha


def make_packet(snapshot: Path, episode: str):
    manifest, rows, source_sha = load_episode(snapshot, episode)
    groups, boundaries = [], []
    for i in range(1, len(rows)):
        old, new = rows[i - 1], rows[i]
        joined = old["display_group_id"] == new["display_group_id"]
        # This is a QUESTION, not an independently heard performed boundary.
        boundaries.append({
            "id": f"B{i:04d}",
            "left_reading_block_id": old["reading_block_id"],
            "right_reading_block_id": new["reading_block_id"],
            "provisional_same_turn": joined,
            "priority": "P0_UNVERIFIED_JOIN" if joined else "P0_UNVERIFIED_BREAK",
        })
    internal = {}
    for r in rows:
        for ref in r["original_source_part_refs"]:
            internal.setdefault(ref, []).append(r["reading_block_id"])
    internal = [{"source_part_ref": ref, "reading_block_ids": ids,
                 "priority": "P0_WITHIN_ORIGINAL_SOURCE_PART"}
                for ref, ids in internal.items() if len(ids) > 1]
    for start in range(0, len(rows), BATCH_BLOCKS):
        end = min(start + BATCH_BLOCKS, len(rows))
        subset = rows[start:end]
        clips = [r.get("source_cue_times_not_subturn_times_ms") for r in subset]
        source_window = ([max(0, min(v[0] for v in clips) - 1200),
                          max(v[1] for v in clips) + 1200]
                         if all(isinstance(v, list) and len(v) == 2
                                and all(type(t) is int for t in v) for v in clips)
                         else None)
        questions = boundaries[max(0, start - 1):end - 1]
        groups.append({
            "id": f"{episode}-AV-{len(groups) + 1:03d}",
            "block_index_first": start,
            "block_index_end_exclusive": end,
            "source_window_candidate_ms": source_window,
            "source_clock_verified": False,
            "reader_blocks": [{
                "id": r["reading_block_id"],
                "source_parts": r["original_source_part_refs"],
                "provisional_role": r["candidate_role"],
                "source_dialogue_sha256": r["exact_rendered_caption_sha256"],
                "provisional_display_group_id": r["display_group_id"]
            } for r in subset],
            "boundary_question_ids": [b["id"] for b in questions],
            "goals_same_source_playback": [
                "P0 listen for all actual speaker changes, joins, interruptions and overlap",
                "P1 identify each voice using heard and visible evidence or abstain",
                "P2 note performance delivery supported by original soundtrack",
                "P3 note narratively important visible props and clothing",
                "P4 observe actor-action-target, cuts and physical business"
            ],
            "whole_original_av_played_and_verified": False
        })
    result = {
        "schema": SCHEMA,
        "episode_id": episode,
        "source_original_dialogue_sha256": source_sha,
        "original_video_sha256_expected": VIDEO_SHA[episode],
        "canonical_manuscript_sha256": manifest["manuscript_sha256"][episode],
        "canonical_edition": manifest["episode_editorial_integrations"][episode],
        "original_source_speaking_part_refs": len(set(
            ref for r in rows for ref in r["original_source_part_refs"])),
        "source_reader_blocks": len(rows),
        "provisional_display_groups": manifest["episodes"][episode]["display_groups"],
        "source_timecodes_available": episode == "S01E01",
        "review_passes_required": len(groups),
        "all_adjacent_boundary_questions": boundaries,
        "within_source_part_handoffs_needing_review": internal,
        "sequential_one_pass_batches": groups,
        "no_fabricated_certifications": True,
        "original_audio_video_inspected_by_this_command": False,
        "script_final_or_full_episode_accepted": False,
        "workflow_instruction": "Review each sequential batch once on the SHA-pinned original film with synchronized sound; "
            "answer all P0 and P1 questions first, then record P2/P3/P4. "
            "Persist decisions in ONE stable episode ledger; regenerate ONE canonical screenplay. "
            "Machine-proposed names, source timestamps and display joins are not original-AV proof."
    }
    if len(boundaries) != len(rows) - 1:
        raise ValueError("Missing boundary")
    if sum(len(g["reader_blocks"]) for g in groups) != len(rows):
        raise ValueError("Review has incomplete reading-block coverage")
    if sum(b["provisional_same_turn"] for b in boundaries) != (
        len(rows) - manifest["episodes"][episode]["display_groups"]):
        raise ValueError("Unverified display joins mismatch")
    result["packet_sha256"] = digest(result)
    return result


def verify_decisions(packet: dict, decisions: dict):
    """Refuse script-complete claims without per-boundary, per-block original AV review.

    Checking a signed reviewer ledger is *not* itself proof of someone watching.
    Reviewer must have genuinely listened and watched the pinned original film.
    """
    if (decisions.get("packet_sha256") != packet.get("packet_sha256")
        or decisions.get("episode_id") != packet["episode_id"]
        or decisions.get("original_video_sha256") != packet["original_video_sha256_expected"]
        or decisions.get("review_method") != "continuous_original_synchronized_av"
        or not isinstance(decisions.get("reviewer"), str)
        or not decisions["reviewer"].strip()):
        raise ValueError("Missing reviewer, source media SHA or matching packet")
    decision_boundaries = decisions.get("boundaries", {})
    decision_roles = decisions.get("roles", {})
    decision_batches = decisions.get("batches", {})
    if not all(isinstance(x, dict) for x in (decision_boundaries, decision_roles, decision_batches)):
        raise ValueError("Malformed independent AV decisions")
    required_edges = {x["id"] for x in packet["all_adjacent_boundary_questions"]}
    required_blocks = {r["id"] for batch in packet["sequential_one_pass_batches"]
                       for r in batch["reader_blocks"]}
    required_batches = {b["id"] for b in packet["sequential_one_pass_batches"]}
    if (set(decision_boundaries) != required_edges
        or set(decision_roles) != required_blocks
        or set(decision_batches) != required_batches):
        raise ValueError("Episode not fully reviewed: missing P0 boundaries, P1 roles or viewing batches")
    for outcome in decision_boundaries.values():
        if not isinstance(outcome, dict) or outcome.get("result") not in (
                "same_speaker_continuation", "new_speaker", "overlapping_voices"):
            raise ValueError("A P0 boundary remains unreviewed")
        if outcome.get("heard_on_original_audio") is not True:
            raise ValueError("P0 decision requires original sound")
    for value in decision_roles.values():
        if (not isinstance(value, dict) or not isinstance(value.get("role"), str)
            or not value["role"].strip()
            or value.get("original_audio_voice_reviewed") is not True):
            raise ValueError("P1 role has no original-audio decision; UNIDENTIFIED VOICE is permitted")
    for value in decision_batches.values():
        if (not isinstance(value, dict)
            or value.get("synchronized_original_video_and_sound_reviewed") is not True
            or not isinstance(value.get("performance_notes"), list)
            or not isinstance(value.get("visible_props_and_wardrobe"), list)
            or not isinstance(value.get("observed_actor_action_target"), list)):
            raise ValueError("Original performance and picture coverage is incomplete")
    return {"episode_id": packet["episode_id"], "all_original_source_turn_boundaries_reviewed": True,
            "all_candidate_voices_source_listened": True, "all_sequential_av_batches_reviewed": True,
            "editorial_decisions_complete": True,
            "caveat": "Reviewer declarations, not automatic proof of audiovisual viewing."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--snapshot", type=Path, required=True)
    ap.add_argument("--episode", choices=(*EPISODES, "both"), required=True)
    ap.add_argument("--output", type=Path, required=True,
                    help="Stable destination directory; files overwritten in place, no vNN history")
    ap.add_argument("--verify-decisions", type=Path,
                    help="Explicit signed human original-AV ledger for one episode")
    args = ap.parse_args()
    if args.verify_decisions and args.episode == "both":
        ap.error("Verify a single episode at a time")
    args.output.mkdir(parents=True, exist_ok=True)
    for ep in (EPISODES if args.episode == "both" else (args.episode,)):
        packet = make_packet(args.snapshot, ep)
        target = args.output / f"{ep}-one-pass-av-review.json"
        target.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", "utf-8")
        print(ep, "blocks", packet["source_reader_blocks"], "batches",
              packet["review_passes_required"], "P0 boundaries",
              len(packet["all_adjacent_boundary_questions"]), "no AV certifications")
        if args.verify_decisions:
            decision = json.loads(args.verify_decisions.read_text("utf-8"))
            print(json.dumps(verify_decisions(packet, decision), sort_keys=True))


if __name__ == "__main__":
    main()
