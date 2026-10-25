#!/usr/bin/env python3
"""Offline superfan prompt packet behavior on a synthetic private database."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path

from build_fan_answer_packet import build_packet, save_packet
from fan_sqlite_index import build_database
from test_fan_sqlite_index import fixtures


def seed(temp: Path) -> Path:
    src, cards, roles = fixtures()
    paths = [temp / n for n in ("source.jsonl", "cards.jsonl", "roles.jsonl")]
    for rows, path in zip((src, cards, roles), paths):
        path.write_text("".join(json.dumps(r) + "\n" for r in rows), "utf-8")
    db = temp / "fan.sqlite"
    build_database(db, *paths, require_full=False)
    return db


class PromptPacketTests(unittest.TestCase):
    def test_packet_gives_source_and_interpretation_separately(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            db = seed(path)
            packet = build_packet(db, "How does Harry use the double-headed coin?")
            self.assertIn("1984–1992", packet)
            self.assertIn("Original dialogue and working-script witness", packet)
            self.assertIn("Provisional role-specific source dialogue", packet)
            self.assertIn("Interpretation grounded to source cue anchors", packet)
            self.assertIn("Harry examines a double-headed coin", packet)
            self.assertIn("role: HARRY STONE", packet)
            self.assertIn("editorial interpretation", packet.casefold())
            self.assertIn("speaker names are not wholly validated", packet)
            self.assertLess(len(packet), 16000)

    def test_no_unsupported_query_does_not_hallucinate(self):
        with tempfile.TemporaryDirectory() as folder:
            db = seed(Path(folder))
            packet = build_packet(db, "quantum submarine dolphins")
            self.assertIn("No relevant source evidence was retrieved", packet)

    def test_packet_is_not_a_model_response_and_never_overwrites_database(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            db = seed(base)
            output = base / "private-prompt.md"
            result = save_packet(db, "What is Harry's coin trick?", output)
            self.assertTrue(output.is_file())
            self.assertFalse(result["generated_answer"])
            self.assertTrue(result["contains_private_source_dialogue"])
            with self.assertRaises(ValueError):
                save_packet(db, "question", db)
            with self.assertRaises(ValueError):
                build_packet(db, "coin", max_chars=1200)


if __name__ == "__main__":
    unittest.main()
