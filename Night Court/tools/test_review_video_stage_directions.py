#!/usr/bin/env python3
"""Original-video editorial decisions must not silently certify model guesses."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_headless_video_description import FIELDS, SCHEMA as MODEL_SCHEMA
from review_video_stage_directions import (
    adjudicate, render_editorial_appendix, file_sha, SCHEMA,
)

VIDEO = "a" * 64
WINDOW = [1000, 2500]


def model_report():
    proposals = {f: "" for f in FIELDS}
    proposals["proposed_stage_direction"] = "A person points toward a book."
    proposals["actions"] = "A person points toward a book."
    return {
        "schema": MODEL_SCHEMA, "episode_id": "S01E01",
        "source_video_sha256": VIDEO, "verified_source_sha256": VIDEO,
        "duration_ms": 1448256, "script_or_claim_independently_accepted": False,
        "windows": [{
            "id": "S01E01-AV-01", "start_ms": WINDOW[0], "end_ms": WINDOW[1],
            "candidate_cut_crossing": False, "shot_partition_verified": False,
            "independently_accepted": False,
            "source_AV_human_review_done": False,
            "status": "machine_proposed", "model_hypothesis": proposals,
        }],
    }


def decisions(model, verdict="corrected", review=True):
    return {
        "schema": "night-court-visual-review-decisions/1",
        "episode_id": "S01E01", "source_video_sha256": VIDEO,
        "model_report_sha256": hashlib.sha256(
            json.dumps(model, sort_keys=True).encode()).hexdigest(),
        "reviewer_id": "editor-trial-01",
        "decisions": [{
            "window_id": "S01E01-AV-01",
            "field": "proposed_stage_direction",
            "verdict": verdict, "source_window_ms": WINDOW,
            "direct_original_video_review_attested": review,
            "reviewer_text": "A person reaches toward the bookcase." if verdict in ("corrected", "accepted") else None,
            "reason": "Motion is too blurry to resolve." if verdict in ("rejected", "deferred") else None,
        }],
    }


def hash_for(model):
    return hashlib.sha256(json.dumps(model, sort_keys=True).encode()).hexdigest()


class ReviewGateTests(unittest.TestCase):
    def test_corrected_direction_from_explicit_original_video_review(self):
        model = model_report()
        review = decisions(model)
        result = adjudicate(model, review, hash_for(model))
        self.assertEqual(result["schema"], SCHEMA)
        self.assertEqual(result["decision_counts"]["corrected"], 1)
        self.assertEqual(result["unreviewed_field_count"], 9)
        self.assertEqual(len(result["editorial_stage_directions"]), 1)
        self.assertEqual(result["editorial_stage_directions"][0]["text"],
                         "A person reaches toward the bookcase.")
        self.assertFalse(result["full_episode_av_certified"])
        self.assertTrue(result["model_outputs_were_not_automatically_accepted"])
        appendix = render_editorial_appendix(result)
        self.assertIn("bookcase", appendix)
        self.assertIn("independently unverified", appendix)

    def test_deferred_never_generates_script(self):
        model = model_report()
        result = adjudicate(model, decisions(model, "deferred", False), hash_for(model))
        self.assertEqual(result["editorial_stage_directions"], [])
        self.assertIn("No accepted", render_editorial_appendix(result))

    def test_rejection_does_not_reuse_model_text(self):
        model = model_report()
        result = adjudicate(model, decisions(model, "rejected", True), hash_for(model))
        self.assertEqual(result["decision_counts"]["rejected"], 1)
        self.assertEqual(result["editorial_stage_directions"], [])

    def test_accepted_requires_original_video_review(self):
        model = model_report()
        d = decisions(model, "accepted", False)
        with self.assertRaisesRegex(ValueError, "Source review is required"):
            adjudicate(model, d, hash_for(model))

    def test_corrected_requires_reviewer_prose(self):
        model = model_report()
        d = decisions(model)
        d["decisions"][0]["reviewer_text"] = None
        with self.assertRaisesRegex(ValueError, "reviewer-authored"):
            adjudicate(model, d, hash_for(model))

    def test_cannot_accept_empty_model_field(self):
        model = model_report()
        d = decisions(model, "accepted")
        d["decisions"][0]["field"] = "camera"
        with self.assertRaisesRegex(ValueError, "absent model"):
            adjudicate(model, d, hash_for(model))

    def test_no_forged_source_video_or_review_hash(self):
        model = model_report()
        d = decisions(model)
        d["source_video_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "source mismatch"):
            adjudicate(model, d, hash_for(model))
        d = decisions(model)
        d["model_report_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "different model report"):
            adjudicate(model, d, hash_for(model))

    def test_rejects_any_input_certification_or_missing_real_source_verification(self):
        model = model_report()
        d = decisions(model)
        model["script_or_claim_independently_accepted"] = True
        with self.assertRaisesRegex(ValueError, "falsely asserts episode acceptance"):
            adjudicate(model, d, hash_for(model))
        model = model_report()
        d = decisions(model)
        model["verified_source_sha256"] = None
        with self.assertRaisesRegex(ValueError, "lacks independently checked source hash"):
            adjudicate(model, d, hash_for(model))

    def test_rejects_cross_cut_and_duplicate_reviews(self):
        model = model_report()
        d = decisions(model)
        model["windows"][0]["candidate_cut_crossing"] = True
        with self.assertRaisesRegex(ValueError, "Cross-cut"):
            adjudicate(model, d, hash_for(model))
        model = model_report()
        d = decisions(model)
        d["decisions"].append(copy.deepcopy(d["decisions"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            adjudicate(model, d, hash_for(model))

    def test_rejects_mismatched_source_time_window(self):
        model = model_report()
        d = decisions(model)
        d["decisions"][0]["source_window_ms"] = [1000, 3000]
        with self.assertRaisesRegex(ValueError, "time-window mismatch"):
            adjudicate(model, d, hash_for(model))

    def test_actual_cli_never_overwrites_source_files(self):
        model = model_report()
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            raw = (json.dumps(model, sort_keys=True) + "\n").encode()
            model_path = p / "model.json"
            model_path.write_bytes(raw)
            d = decisions(model)
            d["model_report_sha256"] = file_sha(raw)
            decision_path = p / "review.json"
            decision_path.write_text(json.dumps(d))
            out = p / "result.json"
            appendix = p / "stage.md"
            script = Path(__file__).with_name("review_video_stage_directions.py")
            command = [sys.executable, str(script), "--model-report", str(model_path),
                       "--decisions", str(decision_path), "--output", str(out),
                       "--appendix", str(appendix)]
            subprocess.run(command, check=True, capture_output=True, text=True)
            result = json.loads(out.read_text())
            self.assertEqual(result["review_decisions_sha256"], file_sha(decision_path.read_bytes()))
            self.assertIn("reaches toward the bookcase", appendix.read_text())
            self.assertEqual(model_path.read_bytes(), raw)
            rerun = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(rerun.returncode, 0)
            self.assertIn("overwrite", rerun.stderr)


if __name__ == "__main__":
    unittest.main()
