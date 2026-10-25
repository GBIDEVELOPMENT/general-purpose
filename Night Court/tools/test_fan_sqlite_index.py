#!/usr/bin/env python3
"""Synthetic FTS5 controls: source provenance, evidence separation, no overwrite."""
import json
import tempfile
import unittest
from pathlib import Path

from fan_sqlite_index import SCHEMA, build_database, query, validate_evidence
from build_pilot_character_evidence import SCHEMA as ROLE_SCHEMA
from build_pilot_fan_beat_cards import CARD_SCHEMA
from search_fan_retrieval_chunks import SCHEMA as SCRIPT_SCHEMA


def fixtures():
    episode = "S01E01"
    witness = "b" * 64
    source = [{
        "schema": SCRIPT_SCHEMA, "episode_id": episode,
        "record_id": episode + ":retrieval:0001",
        "episode_title": "All You Need Is Love",
        "section_label": "court", "retrieval_text": "Harry examines a double-headed coin.",
        "script_sha256": "a" * 64, "caption_source_sha256": witness,
        "evidence_tier": "provisional_filmed_staging_working_script",
        "speaker_names_verified": False, "whole_episode_av_certified": False
    }]
    cards = [{
        "schema": CARD_SCHEMA, "id": episode + ":beat:coin",
        "episode_id": episode, "episode_title": "All You Need Is Love",
        "title": "The double-headed coin",
        "setup": "The judge proposes a coin flip.",
        "payoff": "The trick is explained by the heads on both sides.",
        "interpretation": "A comically rigged judicial procedure.",
        "mechanisms": ["prop_gag", "callback"],
        "semantic_text": "Coin of justice and a trick with two heads.",
        "source_witness_sha256": witness,
        "source_anchor_evidence": [{"caption_cue": 1, "caption_source_sha256": witness}],
        "candidate_characters": ["Harry Stone"],
        "original_audio_speaker_identities_verified": False,
        "vocal_delivery_verified": False,
        "film_staging_verified": False,
        "editorial_interpretation_not_original_script_fact": True
    }]
    roles = [{
        "schema": ROLE_SCHEMA, "episode_id": episode,
        "reading_block_id": episode + ":speaker-evidence:0001",
        "source_reading_ref": "C001.1",
        "original_source_part_refs": ["C001.1"],
        "original_source_sha256": witness,
        "speaker_turn_boundary_verified": False,
        "actor_face_or_voice_independently_verified": False,
        "candidate_role": "HARRY STONE",
        "role_attribution_status": "provisional_not_original_audio_verified",
        "caption_text": "Harry has the coin."
    }]
    return source, cards, roles


class SqliteFanCorpusTests(unittest.TestCase):
    def test_full_private_build_and_three_kinds(self):
        src, cards, roles = fixtures()
        with tempfile.TemporaryDirectory() as temp:
            paths = [Path(temp) / x for x in ("source.jsonl", "cards.jsonl", "roles.jsonl")]
            for rows, path in zip((src, cards, roles), paths):
                path.write_text("".join(json.dumps(item) + "\n" for item in rows), "utf-8")
            db = Path(temp) / "search.sqlite"
            summary = build_database(db, *paths, require_full=False)
            self.assertEqual(summary["source_episodes"], 1)
            self.assertEqual(summary["indexed_documents"], 3)
            results = query(db, "Harry coin")
            self.assertEqual(results["schema"], SCHEMA)
            self.assertEqual([len(results["results_by_evidence_kind"][k]) for k in (
                "script_witness", "provisional_character_dialogue", "editorial_comedy_and_story"
            )], [1, 1, 1])
            results = query(db, "Harry coin", episode="S01E01", role="WRONG")
            self.assertFalse(results["results_by_evidence_kind"]["provisional_character_dialogue"])
            self.assertTrue(results["results_by_evidence_kind"]["script_witness"])
            with self.assertRaises(FileExistsError):
                build_database(db, *paths, require_full=False)

    def test_no_false_verified_role_or_mixed_episode(self):
        src, cards, roles = fixtures()
        roles[0]["actor_face_or_voice_independently_verified"] = True
        with self.assertRaises(ValueError):
            validate_evidence(src, cards, roles, require_full=False)
        roles[0]["actor_face_or_voice_independently_verified"] = False
        roles[0]["original_source_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            validate_evidence(src, cards, roles, require_full=False)

    def test_untrusted_episode_and_empty_query(self):
        with tempfile.TemporaryDirectory() as temp:
            src, cards, roles = fixtures()
            paths = [Path(temp) / x for x in ("source.jsonl", "cards.jsonl", "roles.jsonl")]
            for rows, path in zip((src, cards, roles), paths):
                path.write_text("".join(json.dumps(item) + "\n" for item in rows), "utf-8")
            db = Path(temp) / "search.sqlite"
            build_database(db, *paths, require_full=False)
            with self.assertRaises(ValueError):
                query(db, "the episode night court")
            with self.assertRaises(ValueError):
                query(db, "Harry", episode="DROP TABLE episodes")


if __name__ == "__main__":
    unittest.main()
