#!/usr/bin/env python3
"""No-source-media QA for exact original-action video prompt A/B provenance."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from compare_original_qwen_prompt_ab import compare,SCHEMA
from test_summarize_original_qwen_pilot_metrics import synthetic


def trial_pair():
    baseline=synthetic("S01E01",focus="physical_comedy",prompt_profile="standard")
    treatment=synthetic("S01E01",focus="physical_comedy",prompt_profile="action_compact")
    for record in (baseline,treatment):
        record["video_sampling_fps"]=1
        record["video_width_pixels"]=256
        record["max_generated_tokens"]=256
        record["windows"][0]["model_output_error"]=None
        record["windows"][0]["clip_sha256_ephemeral"]="f"*64
    treatment["windows"][0]["inference_seconds"]=119.5
    treatment["wall_seconds"]=145.2
    return baseline,treatment


def digest(record):
    return hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest()


class OriginalMatchedPromptTests(unittest.TestCase):
    def test_valid_paired_source_single_changed_input_and_no_model_prose(self):
        a,b=trial_pair()
        out=compare(a,digest(a),b,digest(b))
        self.assertEqual(out["schema"],SCHEMA)
        self.assertTrue(out["same_original_episode_video_and_window_verified"])
        self.assertTrue(out["fixed_dimensions_other_than_prompt_identical"])
        self.assertTrue(out["identical_ephemeral_encoded_clip_sha256"])
        self.assertEqual(out["difference_treatment_minus_control_model_inference_seconds"],-9.9)
        self.assertEqual([r["prompt_profile"] for r in out["runs"]],["standard","action_compact"])
        self.assertEqual([r["strict_ten_field_json_valid"] for r in out["runs"]],[True,True])
        self.assertFalse(out["model_factual_action_quality_comparison_established"])
        self.assertEqual(out["stage_direction_approval_count"],0)
        self.assertNotIn("PRIVATE UNTRUSTED",json.dumps(out))

    def test_episode_source_clip_and_sample_dimensions_can_not_drift(self):
        for field,new in (("episode_id","S09E19"),("source_video_sha256","c"*64),
                          ("video_sampling_fps",3),("max_generated_tokens",512),
                          ("video_width_pixels",448),("model_revision","e"*40)):
            with self.subTest(field=field):
                a,b=trial_pair()
                b[field]=new
                with self.assertRaises(ValueError):
                    compare(a,digest(a),b,digest(b))
        a,b=trial_pair()
        b["windows"][0]["end_ms"]+=200
        with self.assertRaises(ValueError):
            compare(a,digest(a),b,digest(b))

    def test_same_prompt_or_forged_prompt_hash_fails(self):
        a,b=trial_pair()
        b["prompt_profile"]="standard"
        with self.assertRaisesRegex(ValueError,"prompt"):
            compare(a,digest(a),b,digest(b))
        a,b=trial_pair()
        b["prompt_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"prompt hash"):
            compare(a,digest(a),b,digest(b))

    def test_explicit_parser_failure_counts_but_stage_acceptance_stays_zero(self):
        a,b=trial_pair()
        b["windows"][0]["status"]="requires_review"
        b["windows"][0]["model_output_error"]="non_json_model_output"
        r=compare(a,digest(a),b,digest(b))
        self.assertFalse(r["runs"][1]["strict_ten_field_json_valid"])
        self.assertEqual(r["runs"][1]["model_output_error"],"non_json_model_output")
        self.assertFalse(r["direct_original_moving_video_review_complete"])

    def test_forged_original_movie_acceptance_refused(self):
        a,b=trial_pair()
        b["script_or_claim_independently_accepted"]=True
        with self.assertRaises(ValueError):
            compare(a,digest(a),b,digest(b))
        a,b=trial_pair()
        b["original_series_production_screenplay_accepted"]=True
        with self.assertRaises(ValueError):
            compare(a,digest(a),b,digest(b))

    def test_real_cli_keeps_private_inputs_and_refuses_overwrite(self):
        a,b=trial_pair()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            pa=root/"standard.json"
            pb=root/"compact.json"
            pa.write_text(json.dumps(a,sort_keys=True))
            pb.write_text(json.dumps(b,sort_keys=True))
            out=root/"safe.json"
            cmd=[sys.executable,str(Path(__file__).with_name("compare_original_qwen_prompt_ab.py")),
                "--standard",str(pa),"--action-compact",str(pb),"--output",str(out)]
            subprocess.run(cmd,check=True,capture_output=True,text=True)
            score=json.loads(out.read_text())
            self.assertEqual(score["episode_id"],"S01E01")
            self.assertNotIn("PRIVATE UNTRUSTED",out.read_text())
            again=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(again.returncode,0)
            self.assertIn("overwrite",again.stderr)


if __name__=="__main__":
    unittest.main()
