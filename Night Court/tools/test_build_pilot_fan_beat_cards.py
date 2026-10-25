#!/usr/bin/env python3
"""Offline tests for source-anchored Night Court fan beat interpretation."""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from build_pilot_fan_beat_cards import CARD_SCHEMA, SEED_SCHEMA, build_cards, export


def make_fixture(root: Path):
    episodes = {}
    items = []
    for ep, timed in (("S01E01", True), ("S09E19", False)):
        source = (ep + " held original witness\n").encode("utf-8")
        sha = hashlib.sha256(source).hexdigest()
        rel = f"seasons/{ep[:3]}/{ep}/dialogue/fake-manifest.json"
        manifest = {
            "episode_id": ep, "sha256": sha, "cue_count": 3,
            "timecoded": timed, "original_path": "dialogue/original.txt",
            "segments_path": "dialogue/segments.jsonl"
        }
        ep_dir = root / "seasons" / ep[:3] / ep
        (ep_dir / "dialogue").mkdir(parents=True)
        (ep_dir / "dialogue" / "fake-manifest.json").write_text(json.dumps(manifest), "utf-8")
        (ep_dir / "dialogue" / "original.txt").write_bytes(source)
        cues = [
            {"cue": 1, "text": "Hello, the court is ready.", "start_ms": 100 if timed else None},
            {"cue": 2, "text": "The stage is full of surprises.", "start_ms": 300 if timed else None},
            {"cue": 3, "text": "Goodbye, I suppose.", "start_ms": 500 if timed else None},
        ]
        (ep_dir / "dialogue" / "segments.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in cues), "utf-8")
        items.append({"episode_id": ep, "sha256": sha, "manifest": rel})
        episodes[ep] = {"source_sha256": sha, "source_cue_count": 3, "title": ep}
    (root / "catalog").mkdir(parents=True)
    (root / "catalog" / "dialogue-index.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in items), "utf-8")
    seeds = {
        "schema": SEED_SCHEMA, "episodes": episodes,
        "cards": [
            {
                "id": f"{ep}:beat:test", "episode_id": ep, "kind": "comedic_beat",
                "title": "A court surprise", "setup": "The court prepares.",
                "payoff": "Something unexpectedly happens.",
                "analysis": "An interpretive caption-only note.",
                "mechanisms": ["reversal"], "characters": ["Unknown"],
                "anchors": [
                    {"cue": 1, "contains": "court is ready"},
                    {"cue": 2, "contains": "full of surprises"}
                ]
            } for ep in episodes
        ]
    }
    return seeds


class FanBeatTests(unittest.TestCase):
    def test_source_anchored_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Night Court"
            seeds = make_fixture(root)
            cards = build_cards(root, seeds, "f" * 64)
            self.assertEqual(len(cards), 2)
            self.assertTrue(all(c["schema"] == CARD_SCHEMA for c in cards))
            self.assertTrue(all(not c["vocal_delivery_verified"] for c in cards))
            self.assertTrue(all(c["editorial_interpretation_not_original_script_fact"] for c in cards))
            self.assertIsNone(cards[1]["source_anchor_evidence"][0]["original_cue_time_ms"])
            self.assertEqual(cards[0]["source_anchor_evidence"][0]["original_cue_time_ms"], 100)
            seed_path = Path(temp) / "seeds.json"
            seed_path.write_text(json.dumps(seeds), "utf-8")
            summary = export(root, seed_path, Path(temp) / "private")
            self.assertEqual(summary["card_count"], 2)
            self.assertEqual(summary["episode_counts"], {"S01E01": 1, "S09E19": 1})

    def test_does_not_guess_missing_cue(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Night Court"
            seeds = make_fixture(root)
            bad = copy.deepcopy(seeds)
            bad["cards"][0]["anchors"][1]["contains"] = "a fabricated line"
            with self.assertRaisesRegex(ValueError, "Original cue phrase missing"):
                build_cards(root, bad, "f" * 64)

    def test_source_edit_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Night Court"
            seeds = make_fixture(root)
            file = root / "seasons/S01/S01E01/dialogue/original.txt"
            file.write_text("silently modified!", "utf-8")
            with self.assertRaisesRegex(ValueError, "Original held witness SHA drift"):
                build_cards(root, seeds, "f" * 64)

    def test_episode_and_card_conflict_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Night Court"
            seeds = make_fixture(root)
            bad = copy.deepcopy(seeds)
            bad["cards"][0]["id"] = "S09E19:beat:wrong"
            with self.assertRaises(ValueError):
                build_cards(root, bad, "f" * 64)
            bad = copy.deepcopy(seeds)
            bad["cards"].append(copy.deepcopy(bad["cards"][0]))
            with self.assertRaises(ValueError):
                build_cards(root, bad, "f" * 64)

    def test_output_under_source_root_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Night Court"
            seeds = make_fixture(root)
            seed_path = Path(temp) / "seeds.json"
            seed_path.write_text(json.dumps(seeds), "utf-8")
            with self.assertRaisesRegex(ValueError, "outside the source repository"):
                export(root, seed_path, root / "derived/fan-cards")


if __name__ == "__main__":
    unittest.main()
