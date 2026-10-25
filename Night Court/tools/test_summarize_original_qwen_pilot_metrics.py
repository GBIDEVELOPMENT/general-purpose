#!/usr/bin/env python3
"""No-media tests for safe ingestion of expiring original Qwen model reports."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from owner_qwen_original_video_pilot import SOURCES, MODEL_ID, MODEL_SHA
from summarize_original_qwen_pilot_metrics import source_safe_record, aggregate, OUT_SCHEMA


def synthetic(episode="S01E01", valid=True):
    source = SOURCES[episode]
    start = source["candidate_starts_ms"][0]
    return {
        "schema": "night-court-headless-video-description/1",
        "owner_source_pilot_schema": "night-court-original-qwen-picture-pilot/1",
        "episode_id": episode, "source_video_sha256": source["sha256"],
        "verified_source_sha256": source["sha256"],
        "original_avi_sha256_verified": source["sha256"],
        "duration_ms": source["duration_ms"], "model_id": MODEL_ID,
        "model_revision": MODEL_SHA,
        "original_avi_download_count": 1, "no_source_clip_or_still_uploaded": True,
        "script_or_claim_independently_accepted": False,
        "cut_detection_is_editorial_proposal_only": True,
        "original_native_decoded_frame_pts_human_verified": False,
        "source_frame_pts_independently_verified": False,
        "original_srt_or_dialogue_modified": False,
        "original_soundtrack_listened_to_or_uploaded": False,
        "actor_identity_or_voice_verified": False,
        "whole_episode_visual_coverage_accepted": False,
        "original_series_production_screenplay_accepted": False,
        "original_source_retrieval_wall_seconds": 4.222,
        "pre_model_original_cut_candidate_checks": [{
            "start_ms": start, "candidate_image_changes": 0,
        }],
        "model_load_seconds": 23.5, "wall_seconds": 155.6,
        "windows": [{
            "id": f"{episode}-REAL-PICTURE-CANDIDATE-01",
            "start_ms": start, "end_ms": start+2000,
            "candidate_cut_crossing": False, "shot_partition_verified": False,
            "independently_accepted": False, "source_AV_human_review_done": False,
            "status": "machine_proposed" if valid else "requires_review",
            "model_hypothesis": {"setting": "PRIVATE UNTRUSTED GIBBERISH"},
            "model_response_excerpt": "PRIVATE UNTRUSTED COPYRIGHTED STAGE TEXT",
            "decode_seconds": 0.20, "inference_seconds": 129.4,
        }],
    }


class NumericEvidenceContracts(unittest.TestCase):
    def test_source_safe_metrics_without_visual_prose(self):
        x = synthetic()
        result = source_safe_record(x, "b"*64)
        self.assertTrue(result["inference_schema_valid"])
        self.assertFalse(result["independently_verified_shot_or_gag"])
        self.assertEqual(result["original_excerpt_end_ms"]-result["original_excerpt_start_ms"], 2000)
        output = aggregate([result])
        self.assertEqual(output["schema"], OUT_SCHEMA)
        raw = json.dumps(output)
        self.assertNotIn("PRIVATE UNTRUSTED", raw)
        self.assertNotIn("model_hypothesis", raw)
        self.assertNotIn("model_response_excerpt", raw)
        self.assertFalse(output["machine_video_semantics_independently_accepted"])

    def test_two_known_original_pilots_and_no_duplicates(self):
        a = source_safe_record(synthetic("S01E01"), "b"*64)
        b = source_safe_record(synthetic("S09E19",False), "c"*64)
        out = aggregate([b,a])
        self.assertEqual(len(out["episodes"]), 2)
        self.assertEqual(out["episodes"][0]["episode_id"], "S01E01")
        self.assertFalse(out["episodes"][1]["inference_schema_valid"])
        with self.assertRaisesRegex(ValueError, "Repeated"):
            aggregate([a,a])

    def test_rejects_source_substitution_and_model_revision_change(self):
        x = synthetic()
        x["source_video_sha256"]="c"*64
        with self.assertRaisesRegex(ValueError, "Source original video SHA"):
            source_safe_record(x,"b"*64)
        x = synthetic()
        x["model_revision"]="0"*40
        with self.assertRaisesRegex(ValueError, "identity/revision"):
            source_safe_record(x,"b"*64)

    def test_no_forged_source_review_or_export_gates(self):
        for field, bad in [
            ("script_or_claim_independently_accepted", True),
            ("original_srt_or_dialogue_modified", True),
            ("source_frame_pts_independently_verified", True),
            ("no_source_clip_or_still_uploaded", False),
            ("original_series_production_screenplay_accepted", True)
        ]:
            with self.subTest(field=field):
                x=synthetic()
                x[field]=bad
                with self.assertRaises(ValueError):
                    source_safe_record(x,"b"*64)

    def test_candidate_cut_review_must_reject_known_images_changes(self):
        x=synthetic()
        x["pre_model_original_cut_candidate_checks"][0]["candidate_image_changes"]=1
        with self.assertRaisesRegex(ValueError, "detected cut"):
            source_safe_record(x,"b"*64)
        x=synthetic()
        x["windows"][0]["start_ms"]=666000
        with self.assertRaises(ValueError):
            source_safe_record(x,"b"*64)

    def test_runner_timing_cannot_be_forged_or_nonsensical(self):
        x=synthetic()
        x["model_load_seconds"]=float("nan")
        with self.assertRaisesRegex(ValueError, "Bad measured"):
            source_safe_record(x,"b"*64)
        x=synthetic()
        x["wall_seconds"]=22
        with self.assertRaisesRegex(ValueError, "smaller than stages"):
            source_safe_record(x,"b"*64)

    def test_real_cli_roundtrip_without_media_or_prose(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            inputs=[]
            for ep in ("S01E01", "S09E19"):
                p=folder / (ep+".json")
                p.write_text(json.dumps(synthetic(ep),sort_keys=True))
                inputs.append(p)
            dest=folder / "numeric.json"
            command=[sys.executable,
                str(Path(__file__).with_name("summarize_original_qwen_pilot_metrics.py")),
                "--report",str(inputs[0]),"--report",str(inputs[1]),"--output",str(dest)]
            subprocess.run(command,check=True,text=True,capture_output=True)
            output=json.loads(dest.read_text())
            self.assertEqual(output["pilot_episodes_with_verified_source_and_model"],2)
            self.assertNotIn("PRIVATE UNTRUSTED",dest.read_text())
            repeat=subprocess.run(command,text=True,capture_output=True)
            self.assertNotEqual(repeat.returncode,0)
            self.assertIn("overwrite",repeat.stderr)


if __name__=="__main__":
    unittest.main()
