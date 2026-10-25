#!/usr/bin/env python3
"""Validate interpretive Night Court pilot comedy cards against held caption cues.

Editorial synopsis and comic interpretation are NOT authenticated film action
or speaker identity. The tool fails if any keyed lexical source anchor drifts.
Private outputs contain recap prose and copyrighted short source phrases.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEEDS = ROOT / "research" / "pilot-fan-beat-seeds-v1.json"
SEED_SCHEMA = "night-court-private-editorial-fan-beat-seeds/1"
CARD_SCHEMA = "night-court-private-fan-beat-cards/1"


def digest(binary: bytes) -> str:
    return hashlib.sha256(binary).hexdigest()


def canon(value: str) -> str:
    return " ".join(value.casefold().split())


def safe_file(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Untrusted source path outside Night Court tree")
    return path


def load_witness(root: Path, episode_id: str) -> tuple[dict, list[dict]]:
    lines = (root / "catalog" / "dialogue-index.jsonl").read_text("utf-8").splitlines()
    entries = [json.loads(line) for line in lines if line.strip()]
    matched = [item for item in entries if item.get("episode_id") == episode_id]
    if len(matched) != 1:
        raise ValueError("Expected one held source witness for " + episode_id)
    record = matched[0]
    meta = json.loads(safe_file(root, record["manifest"]).read_text("utf-8"))
    if meta["episode_id"] != episode_id or meta["sha256"] != record["sha256"]:
        raise ValueError("Episode/source witness identity mismatch")
    ep_dir = root / "seasons" / episode_id[:3] / episode_id
    original = safe_file(ep_dir, meta["original_path"]).read_bytes()
    if digest(original) != meta["sha256"]:
        raise ValueError("Original held witness SHA drift")
    cues = [json.loads(line) for line in
            safe_file(ep_dir, meta["segments_path"]).read_text("utf-8").splitlines()
            if line.strip()]
    if len(cues) != meta["cue_count"] or [x["cue"] for x in cues] != list(range(1, len(cues) + 1)):
        raise ValueError("Original source cue coverage mismatch")
    if any(not isinstance(x.get("text"), str) for x in cues):
        raise ValueError("Malformed caption text")
    return meta, cues


def build_cards(root: Path, seeds: dict, seed_sha: str) -> list[dict]:
    if seeds.get("schema") != SEED_SCHEMA or not isinstance(seeds.get("episodes"), dict):
        raise ValueError("Wrong beat seed schema")
    if not isinstance(seeds.get("cards"), list):
        raise ValueError("No beat seed card array")
    witness = {}
    for ep, detail in seeds["episodes"].items():
        if not re.fullmatch(r"S\d{2}E\d{2}", ep):
            raise ValueError("Invalid original-series episode identifier")
        meta, cues = load_witness(root, ep)
        if (meta["sha256"] != detail.get("source_sha256")
            or meta["cue_count"] != detail.get("source_cue_count")
            or meta["timecoded"] != (ep != "S09E19")):
            raise ValueError("Seed catalog does not match held episode source")
        witness[ep] = (meta, cues)
    cards = []
    seen = set()
    for card in seeds["cards"]:
        ep, cid = card.get("episode_id"), card.get("id")
        if ep not in witness or not isinstance(cid, str) or not cid.startswith(ep + ":beat:") or cid in seen:
            raise ValueError("Duplicate, misplaced, or malformed beat ID")
        seen.add(cid)
        if card.get("kind") not in {"comedic_beat", "character_beat", "plot_beat"}:
            raise ValueError("Unknown beat type")
        fields = ("title", "setup", "payoff", "analysis")
        if any(not isinstance(card.get(field), str) or not card[field].strip() for field in fields):
            raise ValueError("Incomplete interpretive beat")
        if not isinstance(card.get("mechanisms"), list) or not card["mechanisms"]:
            raise ValueError("Missing comic/narrative mechanisms")
        if not isinstance(card.get("characters"), list):
            raise ValueError("Character candidate list must exist")
        anchors = card.get("anchors")
        if not isinstance(anchors, list) or len(anchors) < 2:
            raise ValueError("At least two source anchors required per beat")
        meta, cues = witness[ep]
        matches = []
        encountered = set()
        for item in anchors:
            cue = item.get("cue")
            phrase = item.get("contains")
            if type(cue) is not int or not 1 <= cue <= len(cues):
                raise ValueError("Invalid real original cue number")
            if cue in encountered:
                raise ValueError("Ambiguous repeated original cue anchor")
            encountered.add(cue)
            if not isinstance(phrase, str) or not 3 <= len(phrase) <= 80:
                raise ValueError("Unbounded or empty lexical evidence phrase")
            if canon(phrase) not in canon(cues[cue - 1]["text"]):
                raise ValueError(f"Original cue phrase missing for {cid}, C{cue}")
            matches.append({
                "caption_cue": cue,
                "caption_source_sha256": meta["sha256"],
                "short_source_phrase": phrase,
                "original_caption_is_timed": meta["timecoded"],
                "original_cue_time_ms": cues[cue-1].get("start_ms") if meta["timecoded"] else None
            })
        if matches != sorted(matches, key=lambda x: x["caption_cue"]):
            raise ValueError("Story anchor order must follow original caption order")
        search_text = " ".join([
            ep, seeds["episodes"][ep]["title"],
            card["title"], card["setup"], card["payoff"],
            card["analysis"], " ".join(card["characters"]),
            " ".join(card["mechanisms"]), " ".join(x["short_source_phrase"] for x in matches),
        ])
        cards.append({
            "schema": CARD_SCHEMA,
            "id": cid,
            "episode_id": ep,
            "episode_title": seeds["episodes"][ep]["title"],
            "kind": card["kind"],
            "title": card["title"],
            "setup": card["setup"],
            "payoff": card["payoff"],
            "interpretation": card["analysis"],
            "candidate_characters": card["characters"],
            "mechanisms": card["mechanisms"],
            "source_anchor_evidence": matches,
            "semantic_text": search_text,
            "seed_sha256": seed_sha,
            "source_witness_sha256": meta["sha256"],
            "factual_grounding": "caption_phrase_anchors_only",
            "original_audio_speaker_identities_verified": False,
            "vocal_delivery_verified": False,
            "film_staging_verified": False,
            "editorial_interpretation_not_original_script_fact": True,
        })
    return cards


def export(root: Path, seed_path: Path, output: Path) -> dict:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private fan cards must be exported outside the source repository")
    binary = seed_path.read_bytes()
    seeds = json.loads(binary)
    cards = build_cards(root, seeds, digest(binary))
    output.mkdir(parents=True, exist_ok=True)
    (output / "pilot-fan-beat-cards.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in cards), "utf-8")
    summary = {
        "schema": CARD_SCHEMA,
        "card_count": len(cards),
        "episode_counts": {ep: sum(x["episode_id"] == ep for x in cards) for ep in sorted(seeds["episodes"])},
        "original_media_reviewed_by_this_export": False,
        "factual_grounding": "held_caption_fragments",
        "source_seed_sha256": digest(binary),
    }
    (output / "pilot-fan-beat-manifest.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", "utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--seeds", type=Path, default=DEFAULT_SEEDS)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = export(args.root, args.seeds, args.output)
    print(f"{result['card_count']} source-anchored editorial cards validated; "
          "private text not printed or uploaded")


if __name__ == "__main__":
    main()
