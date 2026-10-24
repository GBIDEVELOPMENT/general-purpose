#!/usr/bin/env python3
"""No-media batch grouping and forged-acceptance regression tests."""
import copy
import unittest
from plan_original_av_microbatches import batches

def sample():
    sha="a"*64
    rows=[]
    for i in range(12):
        rows.append({
          "id":f"S09E19-AV-{i+1:02d}",
          "original_video_sha256":sha,
          "source_window_ms":[i*5000+100,i*5000+3100],
          "goals":{"scene_location":"PENDING_ORIGINAL_AV_REVIEW",
                   "prop_business":"PENDING_ORIGINAL_AV_REVIEW"},
          "independently_accepted":False
        })
    return {"schema":"night-court-multigoal-original-AV-review/1",
            "episode_id":"S09E19","original_video_sha256":sha,
            "original_duration_ms":1320144,
            "script_or_claim_independently_accepted":False,
            "requests":rows}

class AVBatches(unittest.TestCase):
    def test_batch_limits_and_complete_assignment(self):
        source=sample()
        data=batches(source)
        self.assertEqual(len(data["batches"]),3)
        self.assertTrue(all(len(x["review_request_ids"])<=4 for x in data["batches"]))
        self.assertTrue(all(x["requested_window_ms"]<=12000 for x in data["batches"]))
        self.assertEqual(sum(len(x["review_request_ids"]) for x in data["batches"]),12)
        self.assertFalse(data["semantic_video_inference_executed"])
        self.assertFalse(data["original_episodes_or_scenes_accepted"])

    def test_failed_provenance_abstentions(self):
        for case in ("source","accepted","goal","duplicate","overlong","out_of_time"):
            data=sample()
            row=data["requests"][0]
            if case=="source":row["original_video_sha256"]="b"*64
            if case=="accepted":row["independently_accepted"]=True
            if case=="goal":row["goals"]["prop_business"]="ACCEPTED"
            if case=="duplicate":data["requests"][1]["id"]=row["id"]
            if case=="overlong":row["source_window_ms"]=[100,15000]
            if case=="out_of_time":row["source_window_ms"]=[0,1320200]
            with self.subTest(case=case),self.assertRaises(ValueError):
                batches(data)

if __name__=="__main__":
    unittest.main()
