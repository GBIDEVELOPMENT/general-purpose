#!/usr/bin/env python3
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_compare_original_qwen_prompt_ab import trial_pair,digest
from compare_original_qwen_temporal_ab import compare,SCHEMA

class TemporalSourceMatching(unittest.TestCase):
    def pair(self):
        a,b=trial_pair()
        # Use unchanged compact prompt for both variants.
        a["prompt_profile"]=b["prompt_profile"]
        a["prompt_sha256"]=b["prompt_sha256"]
        b["video_sampling_fps"]=2
        b["windows"][0]["clip_sha256_ephemeral"]="e"*64
        return a,b

    def test_paired_original_movie_same_compact_prompt(self):
        a,b=self.pair()
        result=compare(a,digest(a),b,digest(b))
        self.assertEqual(result["schema"],SCHEMA)
        self.assertEqual([r["video_sampling_fps"] for r in result["runs"]],[1,2])
        self.assertTrue(result["fixed_dimensions_other_than_video_sampling_fps_identical"])
        self.assertFalse(result["direct_original_moving_video_review_complete"])
        self.assertFalse(result["model_factual_action_quality_comparison_established"])
        self.assertNotIn("PRIVATE UNTRUSTED",json.dumps(result))

    def test_confounds_rejected(self):
        for key,wrong in [("source_video_sha256","a"*64),("episode_id","S09E19"),
            ("video_width_pixels",320),("max_generated_tokens",512),
            ("model_revision","0"*40),("prompt_sha256","a"*64)]:
            with self.subTest(key=key):
                a,b=self.pair()
                b[key]=wrong
                with self.assertRaises(ValueError):
                    compare(a,digest(a),b,digest(b))
        a,b=self.pair()
        b["windows"][0]["start_ms"] += 200
        with self.assertRaises(ValueError):
            compare(a,digest(a),b,digest(b))

    def test_silent_changed_prompt_and_other_temporal_experiments_rejected(self):
        a,b=self.pair()
        b["video_sampling_fps"]=3
        with self.assertRaises(ValueError):
            compare(a,digest(a),b,digest(b))
        a,b=self.pair()
        a["prompt_profile"]="standard"
        with self.assertRaises(ValueError):
            compare(a,digest(a),b,digest(b))
        a,b=self.pair()
        b["script_or_claim_independently_accepted"]=True
        with self.assertRaises(ValueError):
            compare(a,digest(a),b,digest(b))

if __name__=="__main__":
    unittest.main()
