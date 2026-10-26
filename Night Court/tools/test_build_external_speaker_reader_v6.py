#!/usr/bin/env python3
"""Offline regression for external original-episode quote attribution overlay."""
from __future__ import annotations
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_external_speaker_reader_v6 as mod


def fake(root: Path):
    texts = {
        "S01E01": {142: "Your Honor, this is highly irregular."},
        "S09E19": {27: "So, how'd you start writing?",
                   34: "me. Wow, what a great story."},
    }
    episodes = {
        "S01E01": {"source_sha256": "a"*64, "external_url": "https://example.test/01"},
        "S09E19": {"source_sha256": "b"*64, "external_url": "https://example.test/09"},
    }
    override = [
        {"episode_id": "S01E01", "source_ref": "C142.1",
         "original_cue_text": texts["S01E01"][142],
         "legacy_candidate": "UNIDENTIFIED SPEAKER",
         "proposed_spans": [{
             "start": 0, "end": len(texts["S01E01"][142]), "role": "DAN FIELDING",
             "reader_label": "DAN FIELDING · EXTERNALLY QUOTE-ATTRIBUTED; AUDIO UNVERIFIED",
             "basis": "episode_specific_external_exact_quote_attribution"
         }]},
        {"episode_id": "S09E19", "source_ref": "C027.1",
         "original_cue_text": texts["S09E19"][27], "legacy_candidate": "UNIDENTIFIED SPEAKER",
         "proposed_spans": [{
             "start": 0, "end": len(texts["S09E19"][27]), "role": "CHRISTINE SULLIVAN",
             "reader_label": "CHRISTINE SULLIVAN · EXTERNALLY CONTEXT-ATTRIBUTED; AUDIO UNVERIFIED",
             "basis": "episode_specific_external_paraphrased_question_in_same_conversation"
         }]},
        {"episode_id": "S09E19", "source_ref": "C034.1",
         "original_cue_text": texts["S09E19"][34], "legacy_candidate": "UNIDENTIFIED SPEAKER",
         "proposed_spans": [
             {"start": 0, "end": 3, "role": "ROZ RUSSELL",
              "reader_label": "ROZ RUSSELL · SOURCE-CONTINUATION PROPOSAL; AUDIO UNVERIFIED",
              "basis": "syntactic_continuation_from_provisionally_attributed_preceding_C033"},
             {"start": 4, "end": 28, "role": "CHRISTINE SULLIVAN",
              "reader_label": "CHRISTINE SULLIVAN · EXTERNALLY QUOTE-ATTRIBUTED; AUDIO UNVERIFIED",
              "basis": "episode_specific_external_quote_exact_attribution"}
         ]},
    ]
    ledger = {
        "schema": "night-court-episode-specific-external-quote-speaker-improvements/1",
        "original_captions_unchanged": True, "original_audio_reviewed": False,
        "episodes": episodes, "overrides": override
    }
    lookup = {}
    existing = {}
    for ep, pairs in texts.items():
        cues = [{"cue": i, "text": pairs.get(i, "Synthetic other source")}
                for i in range(1, max(pairs)+1)]
        meta = {"sha256": episodes[ep]["source_sha256"],
                "timecoded": ep == "S01E01"}
        lookup[ep] = (meta, cues)
        existing[ep] = [
            {"source_reading_ref": f"C{n:03d}.1", "candidate_role": None,
             "caption_text": value}
            for n, value in pairs.items()
        ]
        path = root / mod.V5[ep].relative_to(mod.ROOT)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# " + ep + " held source " + meta["sha256"] + "\n\n" +
            ("The original transcript is UNTIMED.\n\n" if ep == "S09E19" else "") +
            "".join("UNIDENTIFIED SPEAKER · UNRESOLVED SOURCE VOICE\n"
                    + text + "\n\n" for text in pairs.values()), "utf-8"
        )
    return ledger, lookup, existing


class SpeakerOverrideTests(unittest.TestCase):
    def test_validated_single_and_two_voice_source_spans(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ledger, lookup, old = fake(root)
            with patch.object(mod, "load_witness", side_effect=lambda root, ep: lookup[ep]):
                spans = mod.verify_overrides(root, ledger, old)
            self.assertEqual(len(spans), 4)
            self.assertEqual(
                [(x["candidate_role"], x["text"]) for x in spans if x["source_ref"] == "C034.1"],
                [("ROZ RUSSELL", "me."), ("CHRISTINE SULLIVAN", "Wow, what a great story.")]
            )
            self.assertTrue(all(not x["original_soundtrack_verified"] for x in spans))
            output = mod.improved_readers(root, ledger, spans)
            self.assertIn("ROZ RUSSELL · SOURCE-CONTINUATION", output["S09E19"])
            self.assertIn("\n\nCHRISTINE SULLIVAN · EXTERNALLY QUOTE-ATTRIBUTED", output["S09E19"])
            self.assertIn("Your Honor, this is highly irregular.", output["S01E01"])

    def test_missing_source_characters_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ledger, lookup, old = fake(root)
            bad = copy.deepcopy(ledger)
            bad["overrides"][2]["proposed_spans"][1]["start"] = 7
            with patch.object(mod, "load_witness", side_effect=lambda root, ep: lookup[ep]):
                with self.assertRaisesRegex(ValueError, "skipped non-whitespace"):
                    mod.verify_overrides(root, bad, old)

    def test_wrong_prior_role_and_source_drift_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ledger, lookup, old = fake(root)
            old["S01E01"][0]["candidate_role"] = "HARRY STONE"
            with patch.object(mod, "load_witness", side_effect=lambda root, ep: lookup[ep]):
                with self.assertRaisesRegex(ValueError, "Cannot overwrite an existing named role"):
                    mod.verify_overrides(root, ledger, old)
            old["S01E01"][0]["candidate_role"] = None
            wrong = copy.deepcopy(ledger)
            wrong["overrides"][0]["original_cue_text"] += " Invented."
            with patch.object(mod, "load_witness", side_effect=lambda root, ep: lookup[ep]):
                with self.assertRaisesRegex(ValueError, "Exact original source paragraph drift"):
                    mod.verify_overrides(root, wrong, old)

    def test_single_span_cannot_claim_verified_audio(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ledger, lookup, old = fake(root)
            broken = copy.deepcopy(ledger)
            broken["overrides"][0]["proposed_spans"][0]["reader_label"] = "DAN FIELDING · VERIFIED"
            with patch.object(mod, "load_witness", side_effect=lambda root, ep: lookup[ep]):
                with self.assertRaisesRegex(ValueError, "overconfident speaker"):
                    mod.verify_overrides(root, broken, old)


if __name__ == "__main__":
    unittest.main()
