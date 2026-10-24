#!/usr/bin/env python3
import unittest
from audit_production_script_publication import assess,REQUIRED

class PublicationGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=assess()
    def test_every_original_episode_has_an_explicit_gate(self):
        j=self.data
        self.assertEqual(len(j["episodes"]),193)
        self.assertEqual(j["blocked_full_episode_scripts"],193)
        self.assertEqual(j["verified_full_episode_scripts"],0)
        self.assertEqual(len({x["episode_id"] for x in j["episodes"]}),193)
        self.assertTrue(all(set(x["required_review_gates"])==set(REQUIRED) for x in j["episodes"]))
    def test_bounded_pilots_do_not_count_as_finished_scripts(self):
        byid={x["episode_id"]:x for x in self.data["episodes"]}
        for ep in ["S01E01","S09E19"]:
            self.assertFalse(byid[ep]["verified_production_script"])
            self.assertEqual(byid[ep]["release_status"],"BLOCKED_AWAITING_INDEPENDENT_AV_ACCEPTANCE")
            self.assertEqual(byid[ep]["required_review_gates"]["full_episode_independent_av_QA"],"not_verified")
        self.assertEqual(byid["S09E19"]["source_format"],"txt")
    def test_no_emotion_or_speaker_by_inference(self):
        self.assertTrue(all(x["signed_independent_review"] is None for x in self.data["episodes"]))
        self.assertTrue(all(not x["identity_or_emotion_inferred_from_model"] for x in self.data["episodes"]))

if __name__=="__main__":unittest.main()
