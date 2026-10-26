#!/usr/bin/env python3
"""Fail closed on inconsistent *private* pilot snapshots before persistence.

This is an integrity check, not independent performance or AV certification.
It deliberately derives current speaker coverage from source-part provenance:
editing an episode must not require changing hard-coded v16 named counts.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

SOURCE = {
    "S01E01": (404, "aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"),
    "S09E19": (347, "659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"),
}
PILOT_TIER = "provisional_source_first_chronological_screenplay_layout"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check(snapshot: Path) -> dict:
    snapshot = snapshot.resolve(strict=True)
    layout = load_json(snapshot / "working-screenplay-layout-manifest.json")
    assert layout["schema"] == "night-court-private-pilot-screenplay-layout/2"
    assert layout["provisional_contextual_roles_only"] is True
    assert layout["scene_review_complete"] is False
    assert layout["new_independently_verified_actor_voices"] == 0
    assert layout["new_independently_verified_performed_turns"] == 0
    # This existing schema cannot record independent AV reviewer evidence.
    # Certification must not be introduced by a generated status change.

    total_named = total_unknown = total_blocks = 0
    per_episode_unknown = {}
    for ep, (expected_source_units, source_sha) in SOURCE.items():
        manuscript = snapshot / f"{ep}-working-screenplay.md"
        provenance = snapshot / f"{ep}-working-screenplay-provenance.jsonl"
        assert manuscript.is_file() and provenance.is_file()
        text = manuscript.read_bytes()
        assert hashlib.sha256(text).hexdigest() == layout["manuscript_sha256"][ep]
        assert f"Original caption source SHA-256: {source_sha}".encode() in text
        rows = [json.loads(line) for line in provenance.read_text("utf-8").splitlines() if line]
        assert len(rows) == layout["episodes"][ep]["source_blocks"]
        assert layout["episodes"][ep]["source_units"] == expected_source_units
        assert layout["episodes"][ep]["full_original_audio_video_accepted"] is False
        assert layout["episodes"][ep]["original_caption_timed"] is (ep == "S01E01")
        ids = [row["display_group_id"] for row in rows]
        assert ids and ids == sorted(ids)
        assert set(ids) == set(range(1, layout["episodes"][ep]["display_groups"] + 1))
        roles = defaultdict(set)
        groups = defaultdict(set)
        for row in rows:
            assert row["source_sha256"] == source_sha
            assert row["actual_original_av_reviewer_accepted"] is False
            assert isinstance(row["display_group_id"], int)
            assert isinstance(row["original_source_part_refs"], list) and row["original_source_part_refs"]
            assert isinstance(row["exact_rendered_caption_sha256"], str) and len(row["exact_rendered_caption_sha256"]) == 64
            role = row["candidate_role"]
            assert role is None or (isinstance(role, str) and role.strip())
            groups[row["display_group_id"]].add(role)
            for ref in row["original_source_part_refs"]:
                assert isinstance(ref, str) and ref.startswith("C")
                roles[ref].add(role)
            clocks = row["source_cue_times_not_subturn_times_ms"]
            if ep == "S09E19":
                assert clocks is None, "S09 original witness is untimed"
            else:
                assert isinstance(clocks, list) and len(clocks) == 2 and clocks[0] <= clocks[1]
        assert all(len(v) == 1 for v in groups.values()), "Different speaker labels merged in display group"
        assert len(roles) == expected_source_units, "Lost or duplicated original speaking-unit refs"
        unnamed = sum(None in role_set for role_set in roles.values())
        per_episode_unknown[ep] = unnamed
        total_unknown += unnamed
        total_named += expected_source_units - unnamed
        total_blocks += len(rows)

    counts = layout["source_unit_counts"]
    assert counts == {
        "original_source_units": sum(pair[0] for pair in SOURCE.values()),
        "named_provisional": total_named,
        "unknown": total_unknown,
    }, "Manifest disagrees with per-source-part coverage"
    fan_root = snapshot / "private-fan-retrieval"
    fan = load_json(fan_root / "fan-retrieval-manifest.json")
    episodes = fan["episodes"]
    assert len(episodes) == fan["episode_count"] == 193
    assert len({e["episode_id"] for e in episodes}) == 193
    assert fan["all_speakers_and_staging_provisional"] is True
    assert fan["contains_original_source_dialogue"] is True
    by_ep = {e["episode_id"]: e for e in episodes}
    for ep, (_, source_sha) in SOURCE.items():
        assert by_ep[ep]["source_sha256"] == source_sha
        assert by_ep[ep]["evidence_tier"] == PILOT_TIER
        assert by_ep[ep]["script_sha256"] == layout["manuscript_sha256"][ep]
    assert sum(e["evidence_tier"] == "source_only_dialogue_scaffold" for e in episodes) == 191
    chunks = fan_root / "fan-retrieval-chunks.jsonl"
    assert chunks.is_file() and chunks.stat().st_size
    with chunks.open("r", encoding="utf-8") as handle:
        assert sum(bool(line.strip()) for line in handle) == fan["chunk_count"]

    review_summaries = sorted((snapshot / "private-review").glob("remaining-*-speaker-review-summary.json"))
    assert len(review_summaries) == 1, "Missing or ambiguous current remaining-review summary"
    review = load_json(review_summaries[0])
    assert review["original_source_units"] == counts["original_source_units"]
    assert review["original_source_units_still_unknown"] == total_unknown
    assert review["original_units_provisionally_named"] == total_named
    assert review["remaining_unknown_original_source_units_by_episode"] == per_episode_unknown
    assert review["new_voices_human_accepted"] == 0

    files = [p for p in snapshot.rglob("*") if p.is_file()]
    assert all(not p.is_symlink() and p.suffix in {".md", ".json", ".jsonl", ".txt"} for p in files)
    assert all(p.stat().st_size < 30_000_000 for p in files)
    assert sum(p.stat().st_size for p in files) < 85_000_000

    return {
        "original_source_units": counts["original_source_units"],
        "named_provisional": total_named,
        "remaining_unknown": total_unknown,
        "provisional_reader_blocks": total_blocks,
        "display_groups": {ep: layout["episodes"][ep]["display_groups"] for ep in SOURCE},
        "private_fan_episodes": fan["episode_count"],
        "original_av_certified_episodes": 0,
        "files": len(files),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.snapshot), sort_keys=True))


if __name__ == "__main__":
    main()
