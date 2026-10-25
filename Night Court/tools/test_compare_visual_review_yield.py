#!/usr/bin/env python3
"""Machine-only QA for sourced model-review pair ranking. No original AV."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_visual_review_yield import validated_pair, summarize, OUT_SCHEMA

VIDEO = "a" * 64
FIELDS = ("setting", "camera", "people_and_positions", "actions", "props",
          "entrances_exits", "physical_comedy", "reactions", "uncertainty",
          "proposed_stage_direction")


def model_report(model_id, text):
    fields = {field: "" for field in FIELDS}
    fields["actions"] = text
    fields["proposed_stage_direction"] = text
    return {
        "schema": "night-court-headless-video-description/1",
        "episode_id": "S01E01", "source_video_sha256": VIDEO,
        "verified_source_sha256": VIDEO, "script_or_claim_independently_accepted": False,
        "model_id": model_id, "duration_ms": 1448256, "wall_seconds": 44.5,
        "windows": [{
            "id": "S01E01-AV-01", "start_ms": 1000, "end_ms": 2200,
            "candidate_cut_crossing": False,
            "status": "machine_proposed", "model_hypothesis": fields,
            "source_AV_human_review_done": False, "independently_accepted": False,
            "inference_seconds": 31.25, "decode_seconds": 0.15,
        }],
    }


def make_audit(model_sha, verdict="accepted", reviewer="editor-1"):
    row = {
        "window_id": "S01E01-AV-01", "field": "proposed_stage_direction",
        "verdict": verdict, "source_video_sha256": VIDEO,
        "source_window_ms": [1000, 2200],
        "direct_original_video_review_attested": True, "reviewer_id": reviewer,
        "reviewer_text": "A person raises a book." if verdict in ("accepted", "corrected") else None,
    }
    return {
        "schema": "night-court-reviewed-visual-staging/1",
        "episode_id": "S01E01", "source_video_sha256": VIDEO,
        "model_report_sha256": model_sha, "reviewer_id": reviewer,
        "model_outputs_were_not_automatically_accepted": True,
        "full_episode_av_certified": False, "field_decisions": [row],
        "editorial_stage_directions": ([{"window_id": "S01E01-AV-01"}]
                                       if verdict in ("accepted", "corrected") else []),
    }


def pair(label, text="A person raises a book.", verdict="accepted", reviewer="editor-1"):
    report = model_report(label, text)
    sha = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
    audit = make_audit(sha, verdict, reviewer)
    return validated_pair(label, report, sha, audit)


class ReviewYieldTests(unittest.TestCase):
    def test_equivalent_reviewed_fields_offer_paired_metrics(self):
        a = pair("small", verdict="rejected")
        b = pair("large", verdict="accepted")
        score = summarize([a, b])
        self.assertEqual(score["schema"], OUT_SCHEMA)
        self.assertTrue(score["fair_comparison_supported"])
        self.assertEqual(score["paired_identical_time_windows"], 1)
        self.assertEqual(score["paired_source_reviewed_field_count"], 1)
        self.assertEqual(score["models"][0]["paired_rejected"], 1)
        self.assertEqual(score["models"][1]["paired_accepted"], 1)
        self.assertIsNone(score["models"][0]["process_seconds_per_usable_stage_direction"])
        self.assertEqual(score["models"][1]["process_seconds_per_usable_stage_direction"], 44.5)
        self.assertFalse(score["episode_independently_av_certified"])

    def test_different_reviewers_require_reservations(self):
        score = summarize([pair("a"), pair("b", reviewer="editor-2")])
        self.assertFalse(score["fair_comparison_supported"])
        self.assertFalse(score["same_reviewer_id"])

    def test_no_reviewed_field_does_not_imply_accuracy(self):
        a = pair("a")
        b = pair("b")
        b["decisions"] = {("S01E01-AV-01", "actions"): "deferred"}
        score = summarize([a, b])
        self.assertFalse(score["fair_comparison_supported"])
        self.assertEqual(score["paired_source_reviewed_field_count"], 0)

    def test_cross_edition_comparison_rejected(self):
        a = pair("a")
        b = pair("b")
        b["source_video_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "exact same original"):
            summarize([a, b])

    def test_source_hash_and_provenance_forgery_rejected(self):
        report = model_report("a", "A person raises a book.")
        sha = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
        audit = make_audit(sha)
        audit["model_report_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "exact model report"):
            validated_pair("a", report, sha, audit)
        audit = make_audit(sha)
        report["verified_source_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "verified source"):
            validated_pair("a", report, sha, audit)

    def test_fake_model_claims_and_unreviewed_acceptance_rejected(self):
        report = model_report("a", "A person raises a book.")
        sha = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
        audit = make_audit(sha)
        audit["field_decisions"][0]["direct_original_video_review_attested"] = False
        with self.assertRaisesRegex(ValueError, "reviewer attestation"):
            validated_pair("a", report, sha, audit)
        audit = make_audit(sha)
        report["script_or_claim_independently_accepted"] = True
        with self.assertRaisesRegex(ValueError, "may not self-certify"):
            validated_pair("a", report, sha, audit)

    def test_missing_or_duplicated_stage_notes_rejected(self):
        report = model_report("a", "A person raises a book.")
        sha = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
        audit = make_audit(sha)
        audit["editorial_stage_directions"] = []
        with self.assertRaisesRegex(ValueError, "disagree"):
            validated_pair("a", report, sha, audit)
        audit = make_audit(sha)
        audit["field_decisions"].append(copy.deepcopy(audit["field_decisions"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validated_pair("a", report, sha, audit)

    def test_real_json_roundtrip_cli(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            specs = []
            for label, verdict in [("small", "rejected"), ("large", "corrected")]:
                model = model_report(label, "A person raises a book.")
                raw = json.dumps(model, sort_keys=True).encode()
                model_path = folder / (label + "-model.json")
                model_path.write_bytes(raw)
                audit = make_audit(hashlib.sha256(raw).hexdigest(), verdict)
                audit_path = folder / (label + "-audit.json")
                audit_path.write_text(json.dumps(audit))
                specs.append({"label": label, "model_report": model_path.name,
                              "review_audit": audit_path.name})
            manifest = folder / "manifest.json"
            manifest.write_text(json.dumps({"schema": "night-court-review-yield-comparison-input/1",
                                            "models": specs}))
            output = folder / "result.json"
            script = Path(__file__).with_name("compare_visual_review_yield.py")
            command = [sys.executable, str(script), "--comparison", str(manifest),
                       "--output", str(output)]
            subprocess.run(command, capture_output=True, check=True, text=True)
            report = json.loads(output.read_text())
            self.assertEqual(report["paired_source_reviewed_field_count"], 1)
            self.assertEqual(report["models"][1]["paired_corrected"], 1)
            self.assertNotIn("A person raises", output.read_text())
            repeated = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(repeated.returncode, 0)
            self.assertIn("overwrite", repeated.stderr)


if __name__ == "__main__":
    unittest.main()
