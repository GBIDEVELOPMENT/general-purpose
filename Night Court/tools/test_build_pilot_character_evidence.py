#!/usr/bin/env python3
"""Offline tests of reversible speaker evidence indexing and attribution caveats."""
from __future__ import annotations
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import build_pilot_character_evidence as module


class PilotCharacterTests(unittest.TestCase):
    def test_source_ranges_preserve_cue_membership(self):
        self.assertEqual(module.source_refs("C003.2"), ["C003.2"])
        self.assertEqual(module.source_refs("C007.1–C009.1"),
                         ["C007.1", "C008.1", "C009.1"])
        for value in ("C009.1–C007.1", "C001.2–C002.1", "C001.1–C002.2", "not-a-cue"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.source_refs(value)

    def test_exact_source_block_hash_and_provisional_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "source-index.json"
            source = {
                "episode_id": "S09E19", "source_original_caption_sha256": "b" * 64,
                "source_reading_index": [
                    {"source_ref": "C001.1–C002.1",
                     "speaker": "ROZ RUSSELL · PROVISIONAL TEXT-CONTEXT ASSIGNMENT",
                     "source_text_sha256": hashlib.sha256(
                         "I wrote the first letter. Then a reply arrived.".encode()
                     ).hexdigest()},
                    {"source_ref": "C003.1", "speaker": "UNIDENTIFIED SPEAKER · unresolved",
                     "source_text_sha256": hashlib.sha256("Who replied?".encode()).hexdigest()},
                ],
            }
            target.write_text(json.dumps(source), "utf-8")
            cues = [
                {"cue":1, "text":"I wrote the first letter.", "start_ms":None, "end_ms":None},
                {"cue":2, "text":"Then a reply arrived.", "start_ms":None, "end_ms":None},
                {"cue":3, "text":"Who replied?", "start_ms":None, "end_ms":None},
            ]
            meta={"episode_id":"S09E19","source_version_id":"x",
                  "version_id":"x","sha256":"b"*64,"timecoded":False}
            fake = {"S09E19": ("source-index.json", "source_reading_index", 3, 2, 1)}
            with patch.object(module, "INDEXES", fake), patch.object(
                module, "load_witness", return_value=(meta, cues)
            ):
                rows = module.records_for_episode(root, "S09E19")
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0]["original_source_part_refs"], ["C001.1", "C002.1"])
                self.assertEqual(rows[0]["candidate_role"], "ROZ RUSSELL")
                self.assertIsNone(rows[1]["candidate_role"])
                self.assertIsNone(rows[0]["source_original_times_ms"])
                self.assertFalse(rows[0]["speaker_turn_boundary_verified"])
                source["source_reading_index"][0]["source_text_sha256"] = "a" * 64
                target.write_text(json.dumps(source), "utf-8")
                with self.assertRaisesRegex(ValueError, "first-line evidence mismatch"):
                    module.records_for_episode(root, "S09E19")

    def test_no_incorrect_named_voice_from_ambiguous_source(self):
        with self.assertRaises(ValueError):
            module.source_refs("C001.1,C002.1")


if __name__ == "__main__":
    unittest.main()
