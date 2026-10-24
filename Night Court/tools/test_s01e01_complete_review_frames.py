#!/usr/bin/env python3
"""Offline bounded-review source and synthetic frame packet regression."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from build_s01e01_complete_review_frames import capture, sample_plan, source_manifest, sha

class SourceReviewFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=source_manifest()

    def test_source_srt_avi_and_exact_review_window(self):
        m=self.m
        self.assertEqual(m["voice_tasks"],11)
        self.assertEqual(m["visual_tasks"],6)
        p=sample_plan(m)
        self.assertEqual(p["sample_count"],145)
        self.assertEqual(p["start_ms"],56912)
        self.assertEqual(p["end_required_ms"],93074)
        self.assertEqual(p["end_sampling_ms"],93162)

    def test_changed_window_and_overlarge_sample_schedule(self):
        m=copy.deepcopy(self.m)
        m["continuous_review_windows"][0]["end_ms"]=m["continuous_review_windows"][0]["start_ms"]+60000
        with self.assertRaisesRegex(ValueError,"sampling cap"):
            sample_plan(m)

    def test_synthetic_frames_are_hash_indexed_but_not_claimed_reviewed(self):
        import subprocess
        with tempfile.TemporaryDirectory(prefix="nc-review-regression-") as t:
            source=Path(t)/"synthetic.avi"
            # Exactly 95s of tiny synthetic video, entirely unrelated to the show.
            subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
                "-f","lavfi","-i","color=c=blue:s=160x90:r=4:d=95",
                "-an","-c:v","mpeg4","-q:v","12",str(source)],
                check=True,timeout=95,capture_output=True)
            fake=copy.deepcopy(self.m)
            fake["source_video_size_bytes_candidate"]=source.stat().st_size
            fake["source_video_sha256"]=sha(source)
            output=Path(t)/"derived-evidence"
            packet=capture(source,output,fake)
            self.assertEqual(len(packet["frames"]),145)
            self.assertEqual(len(packet["contact_sheets"]),4)
            self.assertFalse(packet["continuous_video_action_timing_verified"])
            self.assertFalse(packet["production_script_accepted"])
            self.assertTrue(all(not f["content_reviewed"] for f in packet["frames"]))
            self.assertEqual(packet["frames"][0]["nominal_video_time_ms"],56912)
            self.assertEqual(packet["frames"][-1]["nominal_video_time_ms"],92912)
            self.assertEqual(packet["frames"][0]["sha256"],sha(output/"frames/frame-001.jpg"))
            with self.assertRaisesRegex(ValueError,"existing output"):
                capture(source,output,fake)
            fake["source_video_sha256"]="0"*64
            with self.assertRaisesRegex(ValueError,"fingerprint mismatch"):
                capture(source,Path(t)/"corrupt-source",fake)

if __name__=="__main__":
    unittest.main()
