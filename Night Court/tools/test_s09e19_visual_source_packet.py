#!/usr/bin/env python3
"""Synthetic visual source protocol: no original media or network."""
import hashlib,json,subprocess,tempfile,unittest
from pathlib import Path
import build_s09e19_visual_source_packet as V

class VisualProtocol(unittest.TestCase):
    def test_disallow_wrong_media(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad=Path(tmp)/"wrong.avi"
            bad.write_bytes(b"not the approved TV file")
            with self.assertRaises(ValueError):V.capture(bad,Path(tmp)/"bad")
    def test_100_frames_from_synthetic_25s(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/"synthetic.avi"
            subprocess.run(["ffmpeg","-hide_banner","-loglevel","error",
                "-f","lavfi","-i","testsrc2=s=160x90:r=4",
                "-t","26","-c:v","mpeg4","-q:v","15",
                "-y",str(src)],check=True,timeout=100)
            out=Path(tmp)/"out"
            V.capture(src,out,start=0,approved_sha=V.digest(src))
            j=json.loads((out/"frame-source-index.json").read_text("utf-8"))
            self.assertEqual(j["sample_count"],100)
            self.assertEqual(len(j["frames"]),100)
            self.assertEqual(j["source_window_ms"],[0,25000])
            self.assertFalse(j["scene_setting_reviewed"])
            self.assertFalse(j["physical_action_continuous_video_reviewed"])
            self.assertFalse(j["original_video_or_audio_in_artifact"])
            self.assertEqual(V.digest(out/"contact-sheet.jpg"),j["contact_sheet_sha256"])
            for row in j["frames"]:
                self.assertEqual(row["sha256"],V.digest(out/row["file"]))
                self.assertFalse(row["reviewed_for_scene_content"])
            with self.assertRaises(ValueError):V.capture(src,out,start=0,approved_sha=V.digest(src))

if __name__=="__main__":unittest.main()
