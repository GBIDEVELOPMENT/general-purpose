#!/usr/bin/env python3
"""Synthetic, source-free comparative shot detector benchmark tests."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_shot_detectors import validate, compare, run, source_hash


def case(sha="a" * 64):
    return {
        "schema": "night-court-shot-benchmark-input/1",
        "episode_id": "S01E01", "source_video_sha256": sha,
        "duration_ms": 6000,
        "existing_ffmpeg_cuts_ms": [2010, 4010],
        "independently_reviewed_cuts_ms": [2000, 4000],
    }


class DetectionContracts(unittest.TestCase):
    def test_one_to_one_matching(self):
        report = compare([2010, 2050, 4000, 5800], [2000, 4000], tolerance_ms=100)
        self.assertEqual((report["matched"], report["false_positive_cuts"], report["missed_reference_cuts"]), (2, 2, 0))
        self.assertEqual(report["recall"], 1)
        self.assertEqual(report["precision"], 0.5)

    def test_readonly_existing_ffmpeg_candidates(self):
        result = run(validate(case()), "existing")
        self.assertEqual(result["accuracy"]["ffmpeg_existing"]["matched"], 2)
        self.assertFalse(result["production_script_accepted"])
        self.assertFalse(result["dramatic_scenes_identified"])
        self.assertFalse(result["shot_boundaries_are_source_pts_verified"])

    def test_no_human_labels_no_accuracy_claim(self):
        raw = case()
        raw["independently_reviewed_cuts_ms"] = None
        self.assertIsNone(run(validate(raw), "existing")["accuracy"])

    def test_reject_source_and_duplicate_cuts(self):
        raw = case()
        raw["source_video_sha256"] = "private AVI"
        with self.assertRaises(ValueError):
            validate(raw)
        raw = case()
        raw["existing_ffmpeg_cuts_ms"] = [2000, 2000]
        with self.assertRaises(ValueError):
            validate(raw)
        raw = case()
        raw["independently_reviewed_cuts_ms"] = [7000]
        with self.assertRaises(ValueError):
            validate(raw)

    def test_duplicate_prediction_does_not_double_count(self):
        self.assertEqual(compare([1000, 1010], [1000])["matched"], 1)


@unittest.skipUnless(subprocess.run(["bash", "-lc", "command -v ffmpeg && command -v ffprobe"],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0,
                     "FFmpeg unavailable")
class MediaContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="nc-shot-test-")
        cls.media = Path(cls.tmp.name) / "hard-cuts.mp4"
        inputs = []
        for color in ["red", "blue", "green"]:
            inputs.extend(["-f", "lavfi", "-i",
                           f"color=c={color}:s=160x120:r=12:d=2"])
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", *inputs,
            "-filter_complex", "[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]",
            "-map", "[v]", "-c:v", "mpeg4", "-q:v", "2", "-y",
            str(cls.media)], check=True, timeout=45)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_wrong_hash_denied(self):
        with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            run(validate(case()), "content", self.media)

    def test_dummy_detector_on_actual_sha_video(self):
        real = case(source_hash(self.media))
        called = []
        def fake_detector(media, backend):
            called.append((media, backend))
            return [2000, 4000]
        result = run(validate(real), "content", self.media, scene_detector=fake_detector)
        self.assertEqual(result["accuracy"]["pyscenedetect_content"]["matched"], 2)
        self.assertEqual(called, [(self.media, "content")])
        self.assertFalse(result["shot_boundaries_are_source_pts_verified"])

    @unittest.skipUnless(importlib.util.find_spec("scenedetect"), "PySceneDetect not installed")
    def test_real_pyscenedetect_on_synthetic_hard_cuts(self):
        result = run(validate(case(source_hash(self.media))), "content", self.media)
        self.assertEqual(result["accuracy"]["pyscenedetect_content"]["matched"], 2)


if __name__ == "__main__":
    unittest.main()
