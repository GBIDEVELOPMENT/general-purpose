"""Offline, media-free safety and source-conservation tests for Qwen review import."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from owner_qwen_original_video_pilot import MODEL_ID, MODEL_SHA, SOURCES
from preserve_original_qwen_model_reports import (
    preserve, sha, validate_bundle, review_original_qwen_report,
)
from run_headless_video_description import FIELDS


def fixture(ep):
    pin = SOURCES[ep]["sha256"]
    start = SOURCES[ep]["candidate_starts_ms"][0]
    window_id = ep + "-REAL-PICTURE-CANDIDATE-01"
    report = {
        "schema": "night-court-headless-video-description/1",
        "owner_source_pilot_schema": "night-court-original-qwen-picture-pilot/1",
        "episode_id": ep, "source_video_sha256": pin,
        "verified_source_sha256": pin, "original_avi_sha256_verified": pin,
        "backend": "qwen3vl", "model_id": MODEL_ID, "model_revision": MODEL_SHA,
        "original_avi_download_count": 1, "source_original_media_is_ephemeral": True,
        "no_source_clip_or_still_uploaded": True, "original_srt_or_dialogue_modified": False,
        "original_soundtrack_listened_to_or_uploaded": False,
        "actor_identity_or_voice_verified": False,
        "original_series_production_screenplay_accepted": False,
        "script_or_claim_independently_accepted": False,
        "whole_episode_visual_coverage_accepted": False,
        "windows": [{
            "id": window_id, "start_ms": start, "end_ms": start + 2000,
            "candidate_cut_crossing": False, "shot_partition_verified": False,
            "source_AV_human_review_done": False, "independently_accepted": False,
            "status": "machine_proposed",
            "model_hypothesis": {field: "" for field in FIELDS},
        }],
    }
    original = json.dumps(report, ensure_ascii=False, sort_keys=True).encode()
    pending = {
        "schema": "night-court-visual-review-decisions/1",
        "episode_id": ep, "source_video_sha256": pin,
        "model_report_sha256": sha(original), "reviewer_id": "original-film-pending",
        "decisions": [{
            "window_id": window_id, "field": field,
            "verdict": "deferred", "direct_original_video_review_attested": False,
            "reviewer_text": None,
        } for field in FIELDS],
    }
    metrics = {
        "schema": "night-court-original-qwen-source-safe-metrics/1",
        "machine_video_semantics_independently_accepted": False,
        "production_screenplay_complete": False,
        "original_source_media_or_audio_retained": False,
        "episodes": [{
            "episode_id": ep, "source_video_sha256": pin,
            "exact_private_owner_model_report_sha256": sha(original),
            "original_source_human_stage_reviewed": False,
        }],
    }
    return report, pending, metrics


def write_bundle(folder, ep, values):
    folder.mkdir(parents=True, exist_ok=True)
    report, pending, metrics = values
    for stem, value in (
        ("original", report), ("pending", pending), ("safe-metrics", metrics)
    ):
        (folder / f"nc-qwen-{stem}-{ep}.json").write_text(
            json.dumps(value, ensure_ascii=False, sort_keys=True), encoding="utf-8")


class SourceVisualEvidenceSafety(unittest.TestCase):
    def test_both_original_sources_preserved_once_idempotently_and_without_movie(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for ep in SOURCES:
                write_bundle(root / ep, ep, fixture(ep))
            first = preserve(root, root / "saved")
            self.assertEqual(first["episodes"], ["S01E01", "S09E19"])
            self.assertEqual(first["files_changed"], 6)
            self.assertEqual(first["independent_stage_actions_accepted"], 0)
            self.assertFalse(first["source_media_written"])
            self.assertEqual(preserve(root, root / "saved")["files_changed"], 0)
            self.assertEqual(len(list((root / "saved").glob("*"))), 6)
            self.assertFalse(any(p.suffix in (".avi", ".mp4", ".jpg")
                                 for p in (root / "saved").iterdir()))

    def test_fails_closed_on_forged_source_review_model_and_unbounded_hypotheses(self):
        ep = "S01E01"
        for patch in (
            {"source_video_sha256": "0" * 64},
            {"model_revision": "0" * 40},
            {"original_soundtrack_listened_to_or_uploaded": True},
            {"actor_identity_or_voice_verified": True},
            {"whole_episode_visual_coverage_accepted": True},
            {"windows": []},
        ):
            report, _, _ = fixture(ep)
            report.update(patch)
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError):
                    review_original_qwen_report(ep, report)
        report, _, _ = fixture(ep)
        report["windows"][0]["model_hypothesis"]["props"] = "X" * 600
        with self.assertRaises(ValueError):
            review_original_qwen_report(ep, report)

    def test_no_partial_write_if_second_episode_reviews_are_forged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for ep in SOURCES:
                write_bundle(root / ep, ep, fixture(ep))
            p = root / "S09E19" / "nc-qwen-pending-S09E19.json"
            data = json.loads(p.read_text())
            data["decisions"][0]["verdict"] = "accepted"
            p.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "acceptance"):
                preserve(root, root / "saved")
            self.assertFalse((root / "saved").exists())

    def test_model_and_pending_report_must_share_exact_byte_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ep = "S01E01"
            write_bundle(root / ep, ep, fixture(ep))
            original = root / ep / f"nc-qwen-original-{ep}.json"
            original.write_bytes(original.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "not linked"):
                validate_bundle(ep, root / ep)


if __name__ == "__main__":
    unittest.main()
