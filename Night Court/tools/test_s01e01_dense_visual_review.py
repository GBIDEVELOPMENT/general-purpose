#!/usr/bin/env python3
"""FFmpeg integration regression with synthetic episode-length stand-in only."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
import unittest
import build_s01e01_dense_visual_review as D

class DenseEvidenceTests(unittest.TestCase):
    def test_guarded_real_source_identity(self):
        with tempfile.TemporaryDirectory() as td:
            source=Path(td)/"not-video.avi";source.write_bytes(b"not a Night Court video")
            with self.assertRaises(ValueError):D.capture(source,Path(td)/"out")
    def test_end_to_end_only_synthetic_media(self):
        with tempfile.TemporaryDirectory() as td:
            src=Path(td)/"synthetic.avi"
            subprocess.run(["ffmpeg","-hide_banner","-loglevel","error",
                "-f","lavfi","-i","testsrc2=s=160x90:r=5",
                "-t","92","-c:v","mpeg4","-q:v","12",
                "-y",str(src)],check=True,timeout=80)
            real=D.SOURCE_SHA
            try:
                D.SOURCE_SHA=D.hashfile(src)
                out=Path(td)/"packet"
                D.capture(src,out)
                j=json.loads((out/"dense-frame-index.json").read_text())
                self.assertEqual(j["frames_actual"],60)
                self.assertEqual(j["source_time_window_ms"],[75000,90000])
                self.assertEqual(len(list((out/"sampled-frames").glob("*.jpg"))),60)
                self.assertFalse(j["character_speaker_identities_confirmed"])
                self.assertFalse(j["source_video_audio_bytes_in_artifact"])
                for item in j["frame_evidence"]:
                    self.assertFalse(item["continuous_motion_proven"])
                    self.assertEqual(item["sha256"],D.hashfile(out/item["file"]))
                with self.assertRaises(ValueError):D.capture(src,out)
            finally:
                D.SOURCE_SHA=real

if __name__=="__main__":unittest.main()
