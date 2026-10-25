#!/usr/bin/env python3
"""One local search across direct Night Court script evidence AND fan analyses.

Returns two distinct ranked groups so text-supported interpretations cannot
masquerade as independently verified film events. No external services.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

from search_fan_retrieval_chunks import (
    load_records, score_records, search as search_scripts
)
from build_pilot_fan_beat_cards import CARD_SCHEMA

SCHEMA = "night-court-private-fan-evidence-search/1"


def load_cards(path: Path, source_records: list[dict]) -> list[dict]:
    original_sha = {}
    for row in source_records:
        ep = row["episode_id"]
        original_sha.setdefault(ep, set()).add(row["caption_source_sha256"])
    cards = []
    ids = set()
    for i, line in enumerate(path.read_text("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        card = json.loads(line)
        ep = card.get("episode_id")
        cid = card.get("id")
        if (card.get("schema") != CARD_SCHEMA
            or not isinstance(ep, str) or not re.fullmatch(r"S\d{2}E\d{2}", ep)
            or not isinstance(cid, str) or not cid.startswith(ep + ":beat:")
            or cid in ids):
            raise ValueError(f"Invalid/duplicated fan beat card line {i}")
        ids.add(cid)
        if card.get("source_witness_sha256") not in original_sha.get(ep, set()):
            raise ValueError(f"Fan card has no matching held source edition: {cid}")
        if (card.get("original_audio_speaker_identities_verified") is not False
            or card.get("vocal_delivery_verified") is not False
            or card.get("film_staging_verified") is not False
            or card.get("editorial_interpretation_not_original_script_fact") is not True
            or not isinstance(card.get("semantic_text"), str)):
            raise ValueError("Fan card falsely promotes interpretation or source modality")
        for anchor in card.get("source_anchor_evidence", []):
            if (anchor.get("caption_source_sha256") != card["source_witness_sha256"]
                or type(anchor.get("caption_cue")) is not int):
                raise ValueError("Fan card source anchor mismatch")
        cards.append(card)
    if not cards:
        raise ValueError("No fan beat cards")
    return cards


def combined_search(source: list[dict], cards: list[dict], query: str,
                    episode: str | None = None, limit: int = 5) -> dict:
    direct = search_scripts(source, query=query, limit=limit, episode=episode, neighbors=1)
    mapped = [
        {"episode_id": c["episode_id"], "episode_title": c["episode_title"],
         "section_label": c["title"], "record_id": c["id"],
         "retrieval_text": c["semantic_text"]} for c in cards
    ]
    ranked = score_records(mapped, query, episode)[:limit]
    return {
        "schema": SCHEMA,
        "query": query,
        "episode_filter": episode,
        "script_witness_hits": direct["hits"],
        "editorial_fan_beat_candidates": [
            {**cards[i], "search_score": value} for value, i in ranked
        ],
        "critical_distinction": (
            "Script witness hits contain held source text; fan-beat candidates "
            "are independently unverified human editorial interpretations of "
            "short exact source-caption anchor phrases. Neither establishes "
            "actor identity, audible delivery, physical staging or a scene cut."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--cards", type=Path, required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--episode")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    opt = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if (opt.output.resolve().is_relative_to(root)
        or opt.output.resolve() == opt.corpus.resolve()
        or opt.output.resolve() == opt.cards.resolve()):
        raise ValueError("Do not overwrite corpus or publish private search output to repository")
    original = load_records(opt.corpus)
    cards = load_cards(opt.cards, original)
    results = combined_search(original, cards, opt.query, opt.episode, opt.limit)
    opt.output.parent.mkdir(parents=True, exist_ok=True)
    opt.output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(f"{len(results['script_witness_hits'])} direct hits; "
          f"{len(results['editorial_fan_beat_candidates'])} interpretive candidates; "
          "private dialogue not printed")


if __name__ == "__main__":
    main()
