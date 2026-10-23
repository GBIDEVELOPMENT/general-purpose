#!/usr/bin/env python3
"""Synthetic speaker voting tests, no copyrighted dialogue or human labeling."""
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
import unittest

spec=spec_from_file_location("speaker_reconcile",Path(__file__).with_name("reconcile_speaker_votes.py"))
R=module_from_spec(spec);spec.loader.exec_module(R)
TURN={"turn_id":"S01E01:C00001:1",
      "structural_signals":{"explicit_speaker_label_candidates":[],
                            "vocative_addressee_candidates_not_speakers":[]}}
SHA="a"*64

def vote(agent,speaker,confidence=0.9):
    return R.checked_vote(
      {"turn_id":TURN["turn_id"],"speaker_id":speaker,
       "confidence":confidence,"source_sha256":SHA,
       "evidence_turn_ids":[TURN["turn_id"]]},
      agent,SHA,{TURN["turn_id"]},{"tvmaze:1","tvmaze:2"})

class VoteTests(unittest.TestCase):
    def test_agreement_is_provisional(self):
        v=[vote("context","tvmaze:1"),vote("skeptic","tvmaze:1",0.87)]
        o=R.reconcile(TURN,v)
        self.assertEqual(o["speaker_id"],"tvmaze:1")
        self.assertEqual(o["status"],"uncalibrated_agent_agreement")
        self.assertLess(o["confidence_rating_uncalibrated"],1)
    def test_conflict_abstains(self):
        v=[vote("context","tvmaze:1"),vote("skeptic","tvmaze:2")]
        self.assertEqual(R.reconcile(TURN,v)["speaker_id"],"UNKNOWN")
    def test_one_agent_abstains(self):
        self.assertEqual(R.reconcile(TURN,[vote("context","tvmaze:1")])["status"],"unresolved")
    def test_explicit_source_label_wins(self):
        original={**TURN,"structural_signals":{**TURN["structural_signals"],
                                "explicit_speaker_label_candidates":["tvmaze:2"]}}
        o=R.reconcile(original,[vote("context","tvmaze:1")])
        self.assertEqual(o["speaker_id"],"tvmaze:2")
        self.assertEqual(o["status"],"explicit_source_caption_label")
    def test_self_address_abstains(self):
        original={**TURN,"structural_signals":{**TURN["structural_signals"],
                    "vocative_addressee_candidates_not_speakers":["tvmaze:1"]}}
        v=[vote("context","tvmaze:1"),vote("skeptic","tvmaze:1")]
        self.assertEqual(R.reconcile(original,v)["speaker_id"],"UNKNOWN")
    def test_unknown_role_and_wrong_source_rejected(self):
        with self.assertRaises(ValueError):
            vote("context","tvmaze:999")
        with self.assertRaises(ValueError):
            R.checked_vote({"turn_id":TURN["turn_id"],"speaker_id":"tvmaze:1",
                            "confidence":0.95,"source_sha256":"other",
                            "evidence_turn_ids":[TURN["turn_id"]]},
                           "context",SHA,{TURN["turn_id"]},{"tvmaze:1"})
    def test_two_names_do_not_turn_into_independent_ground_truth(self):
        # Semantic independence remains a research question, not a test guarantee.
        self.assertEqual(R.reconcile(TURN,[])["status"],"unresolved")

if __name__=="__main__":unittest.main()
