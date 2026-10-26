"""Independent regression tests for current S09 v18 source-exact editorial integration."""
from __future__ import annotations

from copy import deepcopy
import unittest

from integrate_committed_editorial_pilots import (
    ROOT, S09_DIR, assert_original_dialogue, integrate_s09_v18,
    read_json, read_jsonl,
)


class S09V18IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.v17 = read_jsonl(S09_DIR/"S09E19-v17-source-first-reader.jsonl")
        cls.ledger = read_json(ROOT/"seasons/S09/S09E19/derived/editorial-v18/s09e19-editorial-v18-amendments.json")
        cls.expected_sha = cls.ledger["base_reader_sha256"]

    def test_direct_source_and_annotated_manuscript_acceptance_without_av_promotion(self) -> None:
        reader, sidecars, screenplay, info = integrate_s09_v18(self.v17, self.expected_sha)
        self.assertEqual(len(reader), 323)
        self.assertEqual(len(sidecars), 323)
        self.assertEqual(len({r["display_group_id"] for r in sidecars}), 239)
        self.assertEqual(info["named_role_edits_added_v18"], 2)
        self.assertEqual(info["anonymous_same_voice_join_hypotheses"], 3)
        self.assertEqual(info["independently_accepted_original_voice_or_turns"], 0)
        self.assertEqual(sum(r["actual_original_av_reviewer_accepted"] for r in sidecars), 0)
        self.assertEqual(sum(r["source_cue_times_not_subturn_times_ms"] is not None for r in sidecars), 0)
        self.assertEqual(screenplay.count("*Checked original-picture reference ("), 11)
        assert_original_dialogue("S09E19", reader, screenplay)

    def test_text_mutation_fails_closed(self) -> None:
        changed=deepcopy(self.v17)
        changed[0]["caption_text"] += " SCRIPT REGRESSION"
        with self.assertRaises(AssertionError):
            integrate_s09_v18(changed,self.expected_sha)

    def test_unapproved_role_change_fails_closed(self) -> None:
        changed=deepcopy(self.v17)
        changed[0]["candidate_role"] = "HARRY STONE"
        with self.assertRaises(AssertionError):
            integrate_s09_v18(changed,self.expected_sha)

    def test_prior_source_sha_drift_fails_closed(self) -> None:
        with self.assertRaises(AssertionError):
            integrate_s09_v18(self.v17,"0"*64)


if __name__=="__main__":
    unittest.main()
