#!/usr/bin/env python3
"""Held-source, offline latest two-pilot integration regressions, no media replay."""
import copy
import json
import unittest

from integrate_committed_editorial_pilots import ROOT, read_jsonl, counts
from upgrade_latest_editorial_pilots import integrate_s01, integrate_s09, validate_stage_overlay


class LatestCommittedPilotsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows=read_jsonl(ROOT/"saved-private/pilot-current/pilot-current-editorial-reader.jsonl")
        cls.s01=[r for r in rows if r["episode_id"]=="S01E01"]
        cls.s09=[r for r in rows if r["episode_id"]=="S09E19"]

    def prior_s01(self):
        prior=copy.deepcopy(self.s01)
        reverted={"C010.1","C011.1","C084.1","C102.1","C103.1",
                  "S01E01-C219-SOURCE-TURN-2"}
        assert reverted <= {r["source_reading_ref"] for r in prior}
        for row in prior:
            if row["source_reading_ref"] in reverted:
                row["candidate_role"]=None
        return prior

    def prior_s09(self):
        prior=copy.deepcopy(self.s09)
        reverted={"C051.1","C229.1"}
        assert reverted <= {r["source_reading_ref"] for r in prior}
        for row in prior:
            if row["source_reading_ref"] in reverted:
                row["candidate_role"]=None
        return prior

    def test_complete_s01_v22_held_original_source(self):
        rows,proof,script,info=integrate_s01(self.prior_s01())
        self.assertEqual(len(rows),405)
        self.assertEqual(len(proof),405)
        self.assertEqual(counts(rows)["fully_provisionally_named_source_units"],390)
        self.assertEqual(len({p["display_group_id"] for p in proof}),275)
        self.assertEqual(script.count("[PIC-"),27)
        self.assertIn("PIC-03",script)
        self.assertEqual(info["editorial_version"],"Agent1-v22")
        self.assertTrue(all(not r["actor_face_or_voice_independently_verified"] for r in rows))

    def test_complete_s09_v19_held_original_source(self):
        rows,proof,script,info=integrate_s09(self.prior_s09())
        self.assertEqual(len(rows),323)
        self.assertEqual(len(proof),323)
        self.assertEqual(counts(rows)["fully_provisionally_named_source_units"],273)
        self.assertEqual(len({p["display_group_id"] for p in proof}),234)
        self.assertEqual(info["editorial_version"],"Agent2-v19")
        self.assertTrue(all(r["source_original_times_ms"] is None for r in rows))

    def test_source_mutation_rejected_before_publication(self):
        prior=self.prior_s01()
        prior[0]["caption_text"]="CORRUPTED ORIGINAL SOURCE TEXT"
        with self.assertRaises(AssertionError):
            integrate_s01(prior)

    def test_false_audio_certification_rejected(self):
        prior=self.prior_s09()
        prior[0]["actor_face_or_voice_independently_verified"]=True
        with self.assertRaises(AssertionError):
            integrate_s09(prior)

    def test_original_p0_c219_part_is_not_lost(self):
        _,proof,_,_=integrate_s01(self.prior_s01())
        parts=[p for p in proof if "C219.1" in p["original_source_part_refs"]]
        self.assertEqual(len(parts),2)
        self.assertEqual({p["candidate_role"] for p in parts},{"HARRY STONE","PHIL KERR"})
        self.assertEqual(parts[1]["source_exact_character_span"]["start_char"],38)
        self.assertEqual(parts[1]["source_exact_character_span"]["end_char"],45)


if __name__=="__main__":
    unittest.main()
