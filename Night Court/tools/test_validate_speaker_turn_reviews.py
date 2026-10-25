#!/usr/bin/env python3
"""Source-free P0 editorial contract checks."""
import copy
import unittest
from validate_speaker_turn_reviews import validate,review_template

S="a"*64
P={"schema":"night-court-p0-turn-boundaries/1","episode_id":"S01E01","source_sha256":S,
   "boundary_decisions":[{"left_unit_id":"a","right_unit_id":"b"}]}

class ReviewTests(unittest.TestCase):
    def test_template_stays_unresolved(self):
        r=review_template(P)
        self.assertEqual(validate(P,r)["unresolved"],1)
        self.assertFalse(validate(P,r)["independent_whole_episode_audiovisual_certification"])
    def test_supported_attested_resolution(self):
        r=review_template(P)
        r["decisions"][0].update(decision="same_speaker",evidence_kind="original_audio",
             evidence_location="original source private listening note 12",reviewed_source_sha256=S,
             reviewer_attested_original_source=True)
        self.assertTrue(validate(P,r)["all_boundaries_resolved"])
    def test_refuses_unattested_decision(self):
        r=review_template(P);r["decisions"][0]["decision"]="speaker_change"
        with self.assertRaises(ValueError):validate(P,r)
    def test_refuses_other_source_and_other_pair(self):
        r=review_template(P);r["source_sha256"]="b"*64
        with self.assertRaises(ValueError):validate(P,r)
        r=review_template(P);r["decisions"][0]["right_unit_id"]="other"
        with self.assertRaises(ValueError):validate(P,r)
    def test_refuses_missing_duplicate_and_unknown(self):
        r=review_template(P);r["decisions"]=[]
        with self.assertRaises(ValueError):validate(P,r)
        r=review_template(P);r["decisions"]*=2
        with self.assertRaises(ValueError):validate(P,r)
        r=review_template(P);r["decisions"][0]["decision"]="hallucinated"
        with self.assertRaises(ValueError):validate(P,r)

if __name__=="__main__":unittest.main()
