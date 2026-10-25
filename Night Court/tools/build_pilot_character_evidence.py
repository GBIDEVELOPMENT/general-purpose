#!/usr/bin/env python3
"""Private, reversible character evidence index for both Night Court pilots.

All named attributions remain provisional. Reading blocks are not necessarily
genuine speaker turns. Covers merged UNTImED S09 continuation paragraphs without
inventing times, and produces same-speaker adjacency *review proposals* only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from build_caption_turns import parse_caption
from build_pilot_fan_beat_cards import ROOT, load_witness

SCHEMA = "night-court-private-character-dialogue-evidence/1"
INDEXES = {
    "S01E01": (
        "seasons/S01/S01E01/derived/pilot-quote-corrected-screenplay-v4/"
        "quote-correction-source-index.json",
        "reversible_dialogue_source_index",
        404, 306, 98,
    ),
    "S09E19": (
        "seasons/S09/S09E19/derived/impostor-scene-reading-screenplay-v4/"
        "impostor-role-source-index.json",
        "source_reading_index",
        347, 181, 166,
    ),
}
SPAN = re.compile(r"^C(\d{3})\.(\d+)(?:–C(\d{3})\.(\d+))?$")


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_refs(label: str) -> list[str]:
    m = SPAN.fullmatch(label)
    if not m:
        raise ValueError("Unrecognized original source cue-part range: " + label)
    a, part, b, ending = (int(v) if v else None for v in m.groups())
    if b is None:
        return [f"C{a:03d}.{part}"]
    if part != 1 or ending != 1 or b < a:
        raise ValueError("Unsupported cue-part range: " + label)
    return [f"C{cue:03d}.1" for cue in range(a, b + 1)]


def records_for_episode(root: Path, ep: str) -> list[dict]:
    if ep not in INDEXES:
        raise ValueError("Only original series pilots are provisionally speaker-labelled")
    rel, index_field, expected_units, expected_named, expected_unknown = INDEXES[ep]
    meta, cues = load_witness(root, ep)
    raw = (root / rel).read_bytes()
    speaker_index = json.loads(raw)
    if speaker_index["episode_id"] != ep or speaker_index["source_original_caption_sha256"] != meta["sha256"]:
        raise ValueError("Speaker reader from wrong original source")
    rows = speaker_index[index_field]
    original = [u for cue in cues for u in parse_caption(cue, meta)]
    cue_map = {f"C{u['cue']:03d}.{u['part']}": u for u in original}
    if len(original) != expected_units or len(cue_map) != len(original):
        raise ValueError("Original source speaking-unit coverage drift")
    evidence = []
    encountered = set()
    for i, line in enumerate(rows):
        refs = source_refs(line["source_ref"])
        if len(refs) != len(set(refs)) or any(ref not in cue_map or ref in encountered for ref in refs):
            raise ValueError("Overlapping, duplicated, or missing source cue-part evidence")
        encountered.update(refs)
        units = [cue_map[r] for r in refs]
        if not all(u["source_sha256"] == meta["sha256"] for u in units):
            raise ValueError("Source SHA mismatch for reading block")
        recovered = " ".join(u["source_text"].strip() for u in units)
        full_text_sha = checksum(recovered.encode("utf-8"))
        # The legacy reader index hashes ONLY its first *displayed line*
        # for a multiline SRT cue; a continuation-joined S09 paragraph may
        # instead consist of one rendered line. Always keep the full SHA
        # as a separate stronger source-text invariant in our own output.
        first_line_sha = checksum(recovered.splitlines()[0].encode("utf-8"))
        if line["source_text_sha256"] not in (full_text_sha, first_line_sha):
            raise ValueError(
                "Existing reader first-line evidence mismatch at "
                + ep + ":" + line["source_ref"]
            )
        speaker = line["speaker"].split(" · ", 1)[0].strip()
        unknown = speaker.startswith("UNIDENTIFIED")
        if not unknown and not speaker:
            raise ValueError("Empty named role")
        evidence.append({
            "schema": SCHEMA,
            "episode_id": ep,
            "reading_block_id": f"{ep}:speaker-evidence:{i+1:04d}",
            "source_reading_ref": line["source_ref"],
            "original_source_part_refs": refs,
            "original_source_sha256": meta["sha256"],
            "original_reading_block_sha256": full_text_sha,
            "legacy_reading_first_line_sha256": line["source_text_sha256"],
            "reading_index_sha256": checksum(raw),
            "caption_text": recovered,
            "candidate_role": None if unknown else speaker,
            "attribution_full_provisional_label": line["speaker"],
            "source_original_times_ms": (
                [{"start_ms": u["start_ms"], "end_ms": u["end_ms"]} for u in units]
                if meta["timecoded"] else None
            ),
            "original_source_untimed": not meta["timecoded"],
            "role_attribution_status": "unidentified" if unknown else "provisional_not_original_audio_verified",
            "speaker_turn_boundary_verified": False,
            "actor_face_or_voice_independently_verified": False,
        })
    if encountered != set(cue_map):
        raise ValueError("Some original speaking units were not assigned a reversible reading-block locator")
    named = sum(len(r["original_source_part_refs"]) for r in evidence if r["candidate_role"])
    unknown = sum(len(r["original_source_part_refs"]) for r in evidence if not r["candidate_role"])
    if (named, unknown) != (expected_named, expected_unknown):
        raise ValueError("Pilot provisional coverage differs from authoritative unit ledger")
    return evidence


def build(root: Path) -> tuple[list[dict], list[dict], dict]:
    blocks = []
    for ep in INDEXES:
        blocks.extend(records_for_episode(root, ep))
    characters = defaultdict(list)
    for block in blocks:
        if block["candidate_role"] is not None:
            characters[block["candidate_role"]].append(block)
    candidates = []
    episode_rows = defaultdict(list)
    for block in blocks:
        episode_rows[block["episode_id"]].append(block)
    for ep, group in episode_rows.items():
        for left, right in zip(group, group[1:]):
            if left["candidate_role"] is None or left["candidate_role"] != right["candidate_role"]:
                continue
            # Adjacent provisional same-named caption blocks might be a single
            # performance turn. Do NOT auto-merge, especially untimed S09.
            if left["source_original_times_ms"] is not None:
                end = left["source_original_times_ms"][-1]["end_ms"]
                start = right["source_original_times_ms"][0]["start_ms"]
                gap = start - end
                if gap > 2500:
                    continue
            else:
                gap = None
            candidates.append({
                "episode_id": ep,
                "candidate_role": left["candidate_role"],
                "preceding_block_id": left["reading_block_id"],
                "following_block_id": right["reading_block_id"],
                "original_source_gap_ms": gap,
                "proposal": "review_potential_same_speaker_continuation",
                "speaker_turn_boundary_verified": False,
            })
    dossier = []
    for name, items in sorted(characters.items()):
        dossier.append({
            "schema": SCHEMA,
            "candidate_role": name,
            "episode_ids": sorted({r["episode_id"] for r in items}),
            "reading_blocks": len(items),
            "original_speaking_units": sum(len(x["original_source_part_refs"]) for x in items),
            "representative_source_refs": [
                {"episode_id": x["episode_id"], "ref": x["source_reading_ref"],
                 "source_sha256": x["original_source_sha256"]}
                for x in items[:8]
            ],
            "role_is_provisional": True,
            "character_traits_or_character_arc_inferred": False,
            "not_evidence_of_cast_or_screen_appearance": True,
        })
    summary = {
        "schema": SCHEMA,
        "episodes": len(episode_rows),
        "original_speaking_units": sum(
            len(b["original_source_part_refs"]) for b in blocks),
        "provisionally_named_source_units": sum(
            len(b["original_source_part_refs"]) for b in blocks if b["candidate_role"]),
        "unidentified_source_units": sum(
            len(b["original_source_part_refs"]) for b in blocks if not b["candidate_role"]),
        "reading_blocks": len(blocks),
        "distinct_provisional_roles": len(dossier),
        "adjacent_same_role_review_proposals": len(candidates),
        "original_audio_voice_identifications_verified": 0,
        "performance_delivery_tags_verified": 0,
        "actual_scene_boundaries_verified": 0,
    }
    if (summary["original_speaking_units"],
        summary["provisionally_named_source_units"], summary["unidentified_source_units"]) != (751, 487, 264):
        raise ValueError("Canonical pilot source-unit ledger mismatch")
    return blocks, dossier, {"summary": summary, "boundary_review": candidates}


def export(root: Path, output: Path) -> dict:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Output containing private dialogue must be outside repository")
    blocks, profiles, report = build(root)
    output.mkdir(parents=True, exist_ok=True)
    for name, collection in (
        ("pilot-character-reading-blocks.jsonl", blocks),
        ("pilot-character-dossier-seeds.jsonl", profiles),
        ("pilot-character-adjacent-boundary-review.jsonl", report["boundary_review"]),
    ):
        (output / name).write_text(
            "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in collection),
            "utf-8",
        )
    (output / "pilot-character-evidence-manifest.json").write_text(
        json.dumps(report["summary"], sort_keys=True, indent=2) + "\n", "utf-8")
    return report["summary"]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = export(args.root, args.output)
    print(f"{result['provisionally_named_source_units']}/{result['original_speaking_units']} "
          f"provisional named source units across both pilots; character evidence held privately")


if __name__ == "__main__":
    main()
