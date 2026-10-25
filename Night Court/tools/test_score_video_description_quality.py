#!/usr/bin/env python3
"""Cross-check source-attested visual positives and synthetic negative controls."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score_video_description_quality import score, validate_pair, load_bounded, OUT_SCHEMA

SHA = "a" * 64


def model():
    return {
        "schema": "night-court-headless-video-description/1",
        "episode_id": "S01E01",
        "source_video_sha256": SHA,
        "verified_source_sha256": SHA,
        "duration_ms": 10000,
        "script_or_claim_independently_accepted": False,
        "model_id": "synthetic-test-model", "model_revision": "c" * 40,
        "model_load_seconds": 12.2, "wall_seconds": 22.0,
        "windows": [
            {"id": "A", "start_ms": 0, "end_ms": 2000,
             "candidate_cut_crossing": False, "independently_accepted": False,
             "status": "requires_review", "inference_seconds": 4.5},
            {"id": "B", "start_ms": 3000, "end_ms": 5000,
             "candidate_cut_crossing": False, "independently_accepted": False,
             "status": "machine_proposed", "inference_seconds": 5.1},
        ],
    }


def observations():
    return {
        "schema": "night-court-visual-quality-review-labels/1",
        "episode_id": "S01E01",
        "source_video_sha256": SHA,
        "reviewer_id": "reviewer-1",
        "full_original_video_coverage_verified": False,
        "observations": [
            {"window_id": "A", "source_window_ms": [0, 2000], "event_id": "A-person",
             "kind": "entrance_exit", "reference_truth": "absent",
             "model_claim": "present",
             "direct_original_visual_review_attested": True,
             "reference_note": "No person is present in the synthetic film."},
            {"window_id": "A", "source_window_ms": [0, 2000], "event_id": "A-window",
             "kind": "setting", "reference_truth": "absent",
             "model_claim": "present",
             "direct_original_visual_review_attested": True,
             "reference_note": "No physical room or window is present."},
            {"window_id": "B", "source_window_ms": [3000, 5000], "event_id": "B-action",
             "kind": "action", "reference_truth": "present",
             "model_claim": "absent",
             "direct_original_visual_review_attested": True,
             "reference_note": "The synthetic fixture's moving square crosses the frame."},
            {"window_id": "B", "source_window_ms": [3000, 5000], "event_id": "B-camera",
             "kind": "camera", "reference_truth": "absent",
             "model_claim": "absent",
             "direct_original_visual_review_attested": True,
             "reference_note": "Static generated camera throughout fixture."},
        ],
    }


class QualityMetricTests(unittest.TestCase):
    def test_hallucination_and_missed_motion_cannot_look_accurate(self):
        report = score(model(), observations())
        self.assertEqual(report["schema"], OUT_SCHEMA)
        self.assertEqual(report["sample_windows"], 2)
        self.assertEqual(report["negative_control_absences"], 3)
        self.assertEqual(report["expected_visible_events"], 1)
        self.assertEqual(report["confusion_counts"]["false_positive"], 2)
        self.assertEqual(report["confusion_counts"]["false_negative"], 1)
        self.assertEqual(report["confusion_counts"]["true_negative"], 1)
        self.assertEqual(report["metrics"]["false_positive_rate_negative_controls"], 0.666667)
        self.assertEqual(report["metrics"]["recall_explicit_claims"], 0.0)
        self.assertEqual(report["metrics"]["precision_explicit_claims"], 0.0)
        self.assertEqual(report["structured_json_success_fraction"], 0.5)
        self.assertEqual(report["total_inference_seconds"], 9.6)
        self.assertFalse(report["whole_episode_visual_coverage_certified"])

    def test_absent_ground_truth_yields_null_not_false_perfection(self):
        labels = observations()
        labels["observations"] = []
        report = score(model(), labels)
        self.assertIsNone(report["metrics"]["false_positive_rate_negative_controls"])
        self.assertIsNone(report["metrics"]["recall_explicit_claims"])
        self.assertEqual(report["sample_events_independently_labeled"], 0)

    def test_unknown_reference_is_rejected(self):
        labels = observations()
        labels["observations"][0]["reference_truth"] = "maybe"
        with self.assertRaisesRegex(ValueError, "Reference must"):
            score(model(), labels)

    def test_unreviewed_claims_cannot_be_reference(self):
        labels = observations()
        labels["observations"][0]["direct_original_visual_review_attested"] = False
        with self.assertRaisesRegex(ValueError, "unreviewed"):
            score(model(), labels)

    def test_reference_source_and_window_must_match(self):
        labels = observations()
        labels["source_video_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "does not match"):
            score(model(), labels)
        labels = observations()
        labels["observations"][0]["source_window_ms"] = [1000, 2000]
        with self.assertRaisesRegex(ValueError, "window mismatch"):
            score(model(), labels)

    def test_duplicate_events_or_nonexistent_window_rejected(self):
        labels = observations()
        labels["observations"].append(copy.deepcopy(labels["observations"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            score(model(), labels)
        labels = observations()
        labels["observations"][0]["window_id"] = "unknown"
        with self.assertRaisesRegex(ValueError, "Unmatched"):
            score(model(), labels)

    def test_model_cannot_promote_certification(self):
        m = model()
        m["script_or_claim_independently_accepted"] = True
        with self.assertRaisesRegex(ValueError, "cannot certify"):
            score(m, observations())
        m = model()
        m["verified_source_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "actual SHA"):
            score(m, observations())

    def test_no_full_episode_claim_from_bounded_labels(self):
        labels = observations()
        labels["full_original_video_coverage_verified"] = True
        with self.assertRaisesRegex(ValueError, "bounded sample"):
            score(model(), labels)

    def test_cli_retains_exact_source_hash_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            mp = folder / "model.json"
            lp = folder / "labels.json"
            op = folder / "quality.json"
            model_bytes = (json.dumps(model(), sort_keys=True) + "\n").encode()
            mp.write_bytes(model_bytes)
            label_obj = observations()
            label_obj["exact_model_report_sha256"] = hashlib.sha256(model_bytes).hexdigest()
            lp.write_text(json.dumps(label_obj, sort_keys=True))
            script = Path(__file__).with_name("score_video_description_quality.py")
            cmd = [sys.executable, str(script), "--model-report", str(mp),
                   "--reference-labels", str(lp), "--output", str(op)]
            subprocess.run(cmd, check=True, capture_output=True)
            report = json.loads(op.read_text())
            self.assertEqual(report["model_report_sha256"], hashlib.sha256(model_bytes).hexdigest())
            self.assertEqual(report["confusion_counts"]["false_positive"], 2)
            self.assertEqual(mp.read_bytes(), model_bytes)
            retry = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(retry.returncode, 0)
            self.assertIn("overwrite", retry.stderr)


if __name__ == "__main__":
    unittest.main()
