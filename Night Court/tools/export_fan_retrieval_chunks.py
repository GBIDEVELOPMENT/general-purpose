#!/usr/bin/env python3
"""Export private, labeled Night Court script chunks for fan-oriented retrieval.

This exporter creates NO new audiovisual claims. It uses the source-only
scaffolds for the series and provisional v5 screenplay readers for two pilots.
It does not download media, call models, or alter canonical sources.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT_SCRIPTS = {
    "S01E01": "seasons/S01/S01E01/derived/additional-original-film-staged-reader-v5/screenplay-extra-observed-business.md",
    "S09E19": "seasons/S09/S09E19/derived/additional-original-film-staged-reader-v5/screenplay-extra-observed-business.md",
}
SCHEMA = "night-court-private-fan-retrieval-chunks/1"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_queue(root: Path) -> list[dict]:
    queue = json.loads((root / "catalog/av-script-reconstruction-queue.json").read_text("utf-8"))
    rows = queue["episodes"]
    if queue["original_episode_records"] != len(rows):
        raise ValueError("Episode queue count mismatch")
    if len({e["episode_id"] for e in rows}) != len(rows):
        raise ValueError("Duplicate episode in source queue")
    return sorted(rows, key=lambda e: e["episode_id"])


def select_script(root: Path, record: dict) -> tuple[Path, str]:
    episode = record["episode_id"]
    tier = "provisional_filmed_staging_working_script" if episode in PILOT_SCRIPTS else "source_only_dialogue_scaffold"
    rel = PILOT_SCRIPTS.get(episode) or record["source_metadata"]["source_only_script"]
    path = (root / rel).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Unsafe path outside Night Court root")
    if not path.is_file():
        raise FileNotFoundError(f"Required existing script not found: {rel}")
    return path, tier


def section_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("### "):
            return line[4:].strip()
    return "Unheaded source section"


def partition_sections(document: str) -> list[str]:
    """Keep every character, including preamble, in document order."""
    markers = [m.start() for m in re.finditer(r"(?m)^### ", document)]
    if not markers:
        return [document]
    cuts = [0] + markers + [len(document)]
    # When the first heading is at byte zero, avoid an empty section.
    return [document[a:b] for a, b in zip(cuts, cuts[1:]) if a != b]


def chunk_section(section: str, maximum: int) -> list[str]:
    """Prefer paragraph boundaries; long indivisible paragraphs can overflow."""
    if maximum < 200:
        raise ValueError("Chunk size must be >= 200 characters")
    pieces = []
    remaining = section
    while remaining:
        if len(remaining) <= maximum:
            pieces.append(remaining)
            break
        candidate = remaining.rfind("\n\n", int(maximum * .45), maximum)
        if candidate >= 0:
            boundary = candidate + 2
        else:
            # Do not split a speaker utterance or a short stage-direction
            # paragraph in half solely to hit a token/character quota.
            later = remaining.find("\n\n", maximum)
            boundary = later + 2 if later >= 0 else len(remaining)
        if boundary <= 0:
            raise ValueError("Chunker failed to advance")
        pieces.append(remaining[:boundary])
        remaining = remaining[boundary:]
    if "".join(pieces) != section:
        raise AssertionError("Source section was not preserved")
    return pieces


def export(root: Path, out_dir: Path, pilot_only: bool = False, max_chars: int = 3600) -> dict:
    if max_chars < 200:
        raise ValueError("Chunk size must be >= 200 characters")
    rows = read_queue(root)
    if pilot_only:
        rows = [e for e in rows if e["episode_id"] in PILOT_SCRIPTS]
        if len(rows) != len(PILOT_SCRIPTS):
            raise ValueError("Both pilot episodes must exist")
    if not rows:
        raise ValueError("Empty source episode queue")
    records = []
    manifest_episodes = []
    for entry in rows:
        episode = entry["episode_id"]
        source_sha = entry["source_metadata"]["source_sha256"]
        if not re.fullmatch(r"[0-9a-f]{64}", source_sha):
            raise ValueError(f"Invalid source SHA: {episode}")
        path, tier = select_script(root, entry)
        content = path.read_bytes()
        document = content.decode("utf-8")
        if source_sha not in document:
            raise ValueError(f"Script not linked to expected original caption SHA: {episode}")
        if not document.lstrip().startswith("# " + episode):
            raise ValueError(f"Wrong episode script: {episode}")
        if episode == "S09E19" and entry["source_metadata"]["timed"]:
            raise ValueError("Untimed S09 original witness erroneously marked timed")
        rel_path = path.relative_to(root.resolve()).as_posix()
        parts = []
        for sec_index, section in enumerate(partition_sections(document), 1):
            heading = section_heading(section)
            for sub_index, text in enumerate(chunk_section(section, max_chars), 1):
                parts.append({
                    "schema": SCHEMA,
                    "episode_id": episode,
                    "episode_title": entry["title"],
                    "record_id": f"{episode}:retrieval:{len(parts)+1:04d}",
                    "section_index": sec_index,
                    "section_part": sub_index,
                    "section_label": heading,
                    "script_path": rel_path,
                    "script_sha256": sha256(content),
                    "caption_source_sha256": source_sha,
                    "dialogue_timed_original": bool(entry["source_metadata"]["timed"]),
                    "evidence_tier": tier,
                    "speaker_names_verified": False,
                    "whole_episode_av_certified": False,
                    "section_is_verified_visual_scene": False,
                    "retrieval_text": text,
                })
        if "".join(p["retrieval_text"] for p in parts) != document:
            raise AssertionError(f"Lossy retrieval export for {episode}")
        records.extend(parts)
        manifest_episodes.append({
            "episode_id": episode,
            "title": entry["title"],
            "evidence_tier": tier,
            "source_sha256": source_sha,
            "script_sha256": sha256(content),
            "script_path": rel_path,
            "chunks": len(parts),
            "source_characters": len(document),
        })
    out_dir.mkdir(parents=True, exist_ok=True)
    # Keep original dialog in the owner's designated local/private destination;
    # DO NOT commit the generated bulk corpus or upload to public endpoints.
    chunk_file = out_dir / "fan-retrieval-chunks.jsonl"
    chunk_file.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records), "utf-8")
    manifest = {
        "schema": SCHEMA,
        "scope": "original-1984-1992-only",
        "purpose": "private retrieval seed, not verified production screenplay",
        "episode_count": len(manifest_episodes),
        "chunk_count": len(records),
        "all_speakers_and_staging_provisional": True,
        "contains_original_source_dialogue": True,
        "do_not_publicly_redistribute": True,
        "episodes": manifest_episodes,
    }
    (out_dir / "fan-retrieval-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", "utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pilot-only", action="store_true")
    parser.add_argument("--max-chars", type=int, default=3600)
    options = parser.parse_args()
    result = export(options.root, options.output, options.pilot_only, options.max_chars)
    print(f"Exported {result['chunk_count']} retrieval chunks from {result['episode_count']} episodes")


if __name__ == "__main__":
    main()
