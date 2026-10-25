#!/usr/bin/env python3
"""Synthetic controls for two-tier direct/interpretive Night Court fan search."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from search_fan_corpus import combined_search, load_cards
from build_pilot_fan_beat_cards import CARD_SCHEMA
from search_fan_retrieval_chunks import SCHEMA as SOURCE_SCHEMA


def examples():
    direct = [
        {"schema": SOURCE_SCHEMA, "episode_id": "S01E01", "episode_title": "All You Need Is Love",
         "record_id": "S01E01:retrieval:0001", "section_label": "court",
         "retrieval_text": "Harry produces a mysterious coin at the bench.",
         "script_sha256": "a" * 64, "caption_source_sha256": "b" * 64,
         "evidence_tier": "provisional_filmed_staging_working_script",
         "speaker_names_verified": False, "whole_episode_av_certified": False},
        {"schema": SOURCE_SCHEMA, "episode_id": "S09E19", "episode_title": "P.S. Do I Know You?",
         "record_id": "S09E19:retrieval:0001", "section_label": "correspondence",
         "retrieval_text": "Roz exchanges letters with Alex.",
         "script_sha256": "c" * 64, "caption_source_sha256": "d" * 64,
         "evidence_tier": "provisional_filmed_staging_working_script",
         "speaker_names_verified": False, "whole_episode_av_certified": False}
    ]
    card = {
        "schema": CARD_SCHEMA, "id": "S01E01:beat:coin",
        "episode_id": "S01E01", "episode_title": "All You Need Is Love",
        "source_witness_sha256": "b" * 64,
        "title": "Rigged coin trick", "semantic_text": "coin heads both sides rigged justice",
        "source_anchor_evidence": [
            {"caption_cue": 1, "caption_source_sha256": "b" * 64}
        ],
        "original_audio_speaker_identities_verified": False,
        "vocal_delivery_verified": False, "film_staging_verified": False,
        "editorial_interpretation_not_original_script_fact": True
    }
    return direct, [card]


class CombinedSearchTests(unittest.TestCase):
    def test_provenance_and_retrieval_are_separate(self):
        direct, cards = examples()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "beats.jsonl"
            path.write_text(json.dumps(cards[0]) + "\n", "utf-8")
            imported = load_cards(path, direct)
            result = combined_search(direct, imported, "coin heads rigged justice", episode="S01E01")
            self.assertEqual(len(result["editorial_fan_beat_candidates"]), 1)
            self.assertEqual(result["editorial_fan_beat_candidates"][0]["id"], cards[0]["id"])
            self.assertTrue(result["script_witness_hits"])
            self.assertFalse(result["editorial_fan_beat_candidates"][0]["film_staging_verified"])
            self.assertNotIn("editorial_fan_beat_candidates", result["script_witness_hits"][0])

    def test_reject_wrong_source_or_false_claim(self):
        direct, cards = examples()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "beats.jsonl"
            for field, value in (
                ("source_witness_sha256", "f" * 64),
                ("film_staging_verified", True),
                ("vocal_delivery_verified", True),
                ("original_audio_speaker_identities_verified", True),
                ("editorial_interpretation_not_original_script_fact", False),
            ):
                broken = copy.deepcopy(cards[0])
                broken[field] = value
                path.write_text(json.dumps(broken) + "\n", "utf-8")
                with self.assertRaises(ValueError):
                    load_cards(path, direct)

    def test_cross_episode_filter_and_unmatched_terms(self):
        direct, cards = examples()
        result = combined_search(direct, cards, "coin heads", episode="S09E19")
        self.assertFalse(result["editorial_fan_beat_candidates"])
        result = combined_search(direct, cards, "quantum submarine dolphins")
        self.assertEqual(result["editorial_fan_beat_candidates"], [])
        self.assertEqual(result["script_witness_hits"], [])

    def test_duplicate_card_ids_refused(self):
        direct, cards = examples()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cards.jsonl"
            path.write_text(json.dumps(cards[0]) + "\n" + json.dumps(cards[0]) + "\n", "utf-8")
            with self.assertRaises(ValueError):
                load_cards(path, direct)


if __name__ == "__main__":
    unittest.main()
