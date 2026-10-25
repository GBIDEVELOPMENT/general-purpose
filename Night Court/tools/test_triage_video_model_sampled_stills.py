#!/usr/bin/env python3
"""Offline hash/source/field gate tests for nominal-frame-only VLM triage."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_headless_video_description import FIELDS
from triage_video_model_sampled_stills import review, OUT_SCHEMA, KINDS

SHA = "a" * 64
SOURCE = "b" * 64


def model():
    return {
        "schema": "night-court-headless-video-description/1",
        "episode_id": "S01E01",
        "source_video_sha256": SHA, "verified_source_sha256": SHA,
        "script_or_claim_independently_accepted": False,
        "duration_ms": 1448256,
        "windows": [{
            "id": "S01E01-REAL-PICTURE-CANDIDATE-01",
            "start_ms": 77000, "end_ms": 79000,
            "status": "machine_proposed",
            "candidate_cut_crossing": False,
            "shot_partition_verified": False,
            "independently_accepted": False,
            "model_hypothesis": {k: "model hypotheses, never facts" for k in FIELDS},
        }],
    }


def labels(model_digest):
    return {
        "schema": "night-court-sampled-frame-claim-review/1",
        "episode_id": "S01E01",
        "source_video_sha256": SHA,
        "exact_model_report_sha256": model_digest,
        "sampled_source_material_sha256": SOURCE,
        "window_id": "S01E01-REAL-PICTURE-CANDIDATE-01",
        "reviewer_id": "independent-sample-review",
        "sampled_stills_visually_inspected": True,
        "original_moving_video_reviewed": False,
        "original_soundtrack_reviewed": False,
        "native_frame_pts_independently_verified": False,
        "episode_independently_certified": False,
        "nominal_sampling_fps": 4,
        "nominal_sample_times_ms": [77000,77250,77500,77750,78000,78250,78500,78750],
        "field_reviews": [
            {"field": f, "status": "not_resolvable",
             "sampled_frame_observation": "The sampled images cannot establish the claim."}
            for f in FIELDS
        ],
    }


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


class SampledStillTriageTests(unittest.TestCase):
    def test_produces_numeric_only_noncertifying_ten_field_assessment(self):
        m = model()
        result = review(m, sha(m), labels(sha(m)), SOURCE)
        self.assertEqual(result["schema"], OUT_SCHEMA)
        self.assertEqual(result["field_counts"]["not_resolvable"], 10)
        self.assertEqual(result["nominal_frames_examined"], 8)
        self.assertFalse(result["reference_is_original_full_motion_video"])
        self.assertFalse(result["source_video_editorial_staging_approved"])
        self.assertFalse(result["quality_accuracy_or_model_recall_established"])
        self.assertNotIn("model hypotheses", json.dumps(result))
        self.assertNotIn("sampled images cannot", json.dumps(result))

    def test_positive_classifications_require_actual_proposed_field(self):
        m = model()
        m["windows"][0]["model_hypothesis"]["setting"] = ""
        r = labels(sha(m))
        with self.assertRaisesRegex(ValueError, "Empty model"):
            review(m, sha(m), r, SOURCE)
        r["field_reviews"][0]["status"] = "model_absent"
        result = review(m, sha(m), r, SOURCE)
        self.assertEqual(result["field_counts"]["model_absent"], 1)

    def test_source_movie_model_bytes_and_sampling_artifact_are_pinned(self):
        m = model()
        r = labels(sha(m))
        r["sampled_source_material_sha256"] = "f"*64
        with self.assertRaisesRegex(ValueError, "evidence bytes changed"):
            review(m, sha(m), r, SOURCE)
        r = labels(sha(m))
        r["exact_model_report_sha256"] = "f"*64
        with self.assertRaisesRegex(ValueError, "different model"):
            review(m, sha(m), r, SOURCE)
        r = labels(sha(m))
        m["verified_source_sha256"] = "f"*64
        with self.assertRaisesRegex(ValueError, "not source-SHA"):
            review(m, sha(m), r, SOURCE)

    def test_rejects_any_false_original_motion_video_or_pts_claim(self):
        m = model()
        for key in ("original_moving_video_reviewed", "original_soundtrack_reviewed",
                    "native_frame_pts_independently_verified",
                    "episode_independently_certified"):
            r = labels(sha(m))
            r[key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                review(m, sha(m), r, SOURCE)

    def test_duplicate_out_of_window_missing_fields_or_unreviewed_images_fail(self):
        m = model()
        r = labels(sha(m))
        r["field_reviews"].append(copy.deepcopy(r["field_reviews"][-1]))
        with self.assertRaisesRegex(ValueError, "ten model"):
            review(m, sha(m), r, SOURCE)
        r = labels(sha(m))
        r["field_reviews"][1]["field"] = "setting"
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            review(m, sha(m), r, SOURCE)
        r = labels(sha(m))
        r["nominal_sample_times_ms"][0] = 76000
        with self.assertRaisesRegex(ValueError, "outside model"):
            review(m, sha(m), r, SOURCE)
        r = labels(sha(m))
        r["sampled_stills_visually_inspected"] = False
        with self.assertRaisesRegex(ValueError, "must attest"):
            review(m, sha(m), r, SOURCE)

    def test_unsupported_stage_motive_cannot_gain_accuracy_or_certification(self):
        m = model()
        r = labels(sha(m))
        r["field_reviews"][-1]["status"] = "unsupported_interpretation"
        out = review(m, sha(m), r, SOURCE)
        self.assertEqual(out["field_counts"]["unsupported_interpretation"], 1)
        self.assertFalse(out["source_video_editorial_staging_approved"])
        self.assertFalse(out["quality_accuracy_or_model_recall_established"])

    def test_real_cli_verifies_artifact_sha_and_never_overwrites(self):
        m = model()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            mr = root / "original-model.json"
            raw = json.dumps(m,sort_keys=True).encode()
            mr.write_bytes(raw)
            material = root / "source-index.json"
            material.write_bytes(b"private synthetic still reference")
            d = labels(hashlib.sha256(raw).hexdigest())
            d["sampled_source_material_sha256"] = hashlib.sha256(material.read_bytes()).hexdigest()
            lab = root / "sampled-review.json"
            lab.write_text(json.dumps(d))
            out = root / "noncertified.json"
            script = Path(__file__).with_name("triage_video_model_sampled_stills.py")
            command = [sys.executable, str(script),
                "--model-report", str(mr), "--sampled-review", str(lab),
                "--sample-material", str(material), "--output", str(out)]
            subprocess.run(command, check=True, text=True, capture_output=True)
            result = json.loads(out.read_text())
            self.assertEqual(result["field_count"], len(FIELDS))
            self.assertNotIn("private synthetic", out.read_text())
            self.assertNotIn("model hypotheses", out.read_text())
            self.assertEqual(mr.read_bytes(),raw)
            again = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(again.returncode, 0)
            self.assertIn("overwrite",again.stderr)


if __name__ == "__main__":
    unittest.main()
