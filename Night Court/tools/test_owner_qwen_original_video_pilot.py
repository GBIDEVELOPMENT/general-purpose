#!/usr/bin/env python3
"""Unprivileged source-free QA for two fixed original-series pilot clip slots."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from owner_qwen_original_video_pilot import (
    SOURCES, MODEL_ID, MODEL_SHA, CLIP_MS,
    source_benchmark_manifest, select_bounded_candidate, candidate_cut_check,
    sample_source, trusted_owner_run,
)


class TrustedOriginalModelContracts(unittest.TestCase):
    def test_episode_and_source_shas_are_two_fixed_original_series_editions(self):
        self.assertEqual(set(SOURCES), {"S01E01", "S09E19"})
        self.assertEqual(MODEL_ID, "Qwen/Qwen3-VL-2B-Instruct")
        self.assertEqual(len(MODEL_SHA), 40)
        self.assertTrue(all(len(v["sha256"]) == 64 for v in SOURCES.values()))
        self.assertEqual(CLIP_MS, 2000)

    def test_source_inventory_exactly_matches_pinned_original_candidates(self):
        for episode in sorted(SOURCES):
            expected, source = sample_source(episode)
            self.assertEqual(expected["sha256"], SOURCES[episode]["sha256"])
            self.assertTrue(source["remote_path"].startswith("/downloads/Night Court TVRip S1-S9/"))
            self.assertGreater(source["size_bytes"], 100000)
        with self.assertRaises(ValueError):
            sample_source("S01E02")
        with self.assertRaises(ValueError):
            sample_source("2023-revival")

    def test_manifests_use_source_movie_sha_and_do_not_invent_subtitle_time(self):
        for episode, spec in SOURCES.items():
            manifest = source_benchmark_manifest(episode, spec["candidate_starts_ms"][0])
            self.assertEqual(manifest["source_video_sha256"], spec["sha256"])
            self.assertIsNone(manifest["caption_source_sha256"])
            self.assertEqual(len(manifest["windows"]), 1)
            self.assertEqual(manifest["windows"][0]["end_ms"] -
                             manifest["windows"][0]["start_ms"], CLIP_MS)
            self.assertFalse(manifest["windows"][0]["candidate_cut_crossing"])
            self.assertFalse(manifest["windows"][0]["shot_partition_verified"])
        with self.assertRaises(ValueError):
            source_benchmark_manifest("S01E01", 100000)

    def test_cut_scan_fallback_is_bounded_and_does_not_invent_verified_shots(self):
        with mock.patch("owner_qwen_original_video_pilot.candidate_cut_check",
                        side_effect=[2, 1, 0]) as scanner:
            offset, scans = select_bounded_candidate(Path("/synthetic-not-opened.avi"), "S01E01")
            self.assertEqual(offset, 77000)
            self.assertEqual([s["candidate_image_changes"] for s in scans], [2, 1, 0])
            self.assertEqual(scanner.call_count, 3)
            self.assertEqual(len(SOURCES["S01E01"]["candidate_starts_ms"]), 14)
            self.assertEqual(len(SOURCES["S09E19"]["candidate_starts_ms"]), 19)
        with mock.patch("owner_qwen_original_video_pilot.candidate_cut_check",
                        side_effect=[1] * len(SOURCES['S09E19']['candidate_starts_ms'])):
            with self.assertRaisesRegex(ValueError, "No proposed source-shot-safe"):
                select_bounded_candidate(Path("/synthetic.avi"), "S09E19")

    def test_privileged_source_path_requires_password_and_never_accepts_override(self):
        with mock.patch.dict(os.environ, {"FTP_PASSWORD": ""}):
            with self.assertRaisesRegex(ValueError, "Owner-secret source mode"):
                trusted_owner_run("S01E01", Path("/tmp/does-not-matter.json"))

    @unittest.skipUnless(subprocess.run(
        ["bash", "-lc", "command -v ffmpeg && command -v ffprobe"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0, "FFmpeg missing")
    def test_synthetic_no_cut_window_and_change_inside_vs_preroll(self):
        with tempfile.TemporaryDirectory() as root:
            clip = Path(root) / "steady.avi"
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-f", "lavfi", "-i", "color=c=blue:size=160x120:rate=30:duration=5",
                "-c:v", "mpeg4", "-q:v", "5", "-y", str(clip),
            ], capture_output=True, text=True, check=True, timeout=30)
            # The scan needs 1 second of previous decoded picture.
            self.assertEqual(candidate_cut_check(clip, 1000), 0)
            with self.assertRaises(ValueError):
                candidate_cut_check(clip, 0)
            with self.assertRaises(ValueError):
                candidate_cut_check(clip, -1)
            with self.assertRaises(ValueError):
                candidate_cut_check(clip, 1000, duration_ms=50000)

            # True hard cut from red to blue exactly two seconds into
            # the original, which lies inside the [1s,3s] scanned window.
            cut = Path(root) / "genuine-cut.avi"
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-f", "lavfi", "-i", "color=c=red:size=160x120:rate=30:duration=2",
                "-f", "lavfi", "-i", "color=c=blue:size=160x120:rate=30:duration=3",
                "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[clip]",
                "-map", "[clip]", "-c:v", "mpeg4", "-q:v", "5",
                "-y", str(cut),
            ], capture_output=True, text=True, check=True, timeout=30)
            self.assertGreaterEqual(candidate_cut_check(cut, 1000), 1)
            # Same actual movie, but its hard cut is entirely before
            # the selected [3s,5s] original-source interval.
            self.assertEqual(candidate_cut_check(cut, 3000), 0)


if __name__ == "__main__":
    unittest.main()
