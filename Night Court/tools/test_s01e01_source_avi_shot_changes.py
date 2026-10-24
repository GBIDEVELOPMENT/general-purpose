#!/usr/bin/env python3
"""FFmpeg synthetic hard-cut timing and conservative original scene-probe contract."""
import copy
import json
import subprocess
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from probe_s01e01_source_avi_shot_changes import (
    contract,parse_scores,ffmpeg_candidates,analyze,sha,THRESHOLD,WINDOW
)

class OriginalShotPTS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=contract()

    def test_source_avi_contract_and_historical_tasks(self):
        self.assertEqual(WINDOW,(56912,93074))
        self.assertEqual(THRESHOLD,Decimal("0.12"))
        self.assertEqual(len(self.manifest["tasks"]),17)

    def test_parse_strictly_monotonic_actual_video_pts(self):
        message="""[Parsed_metadata_1 @ 0x1] frame:0    pts:120     pts_time:5
[Parsed_metadata_1 @ 0x1] lavfi.scene_score=1.000000
[Parsed_metadata_1 @ 0x1] frame:1    pts:192     pts_time:8
[Parsed_metadata_1 @ 0x1] lavfi.scene_score=0.250000"""
        rows=parse_scores(message,start_ms=4000,end_ms=9000)
        self.assertEqual([x["original_stream_pts_candidate_ms"] for x in rows],[5000,8000])
        self.assertEqual(len(rows),2)
        with self.assertRaisesRegex(ValueError,"not increasing"):
            parse_scores(message+"""
[Parsed_metadata_1 @ 0x1] frame:2 pts:185 pts_time:7.708
[Parsed_metadata_1 @ 0x1] lavfi.scene_score=0.700000""",
                start_ms=4000,end_ms=9000)
        with self.assertRaisesRegex(ValueError,"Unpaired"):
            parse_scores("[Parsed_metadata_1 @ x] lavfi.scene_score=1.0",start_ms=4000,end_ms=9000)

    def test_synthetic_24fps_hard_cuts_present_source_pts(self):
        with tempfile.TemporaryDirectory(prefix="night-court-synthetic-shots-") as t:
            media=Path(t)/"synthetic.avi"
            subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
              "-f","lavfi","-i","color=c=black:s=160x90:r=24:d=5",
              "-f","lavfi","-i","color=c=white:s=160x90:r=24:d=3",
              "-f","lavfi","-i","color=c=blue:s=160x90:r=24:d=4",
              "-filter_complex","[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]",
              "-map","[v]","-c:v","mpeg4","-q:v","4",str(media)],
              check=True,capture_output=True,timeout=90)
            rows=ffmpeg_candidates(media,4000,9000,Decimal("0.12"))
            times=[r["original_stream_pts_candidate_ms"] for r in rows]
            self.assertIn(5000,times)
            self.assertIn(8000,times)
            self.assertEqual(len(times),2)
            impostor=copy.deepcopy(self.manifest)
            impostor["source_video_size_bytes_candidate"]=media.stat().st_size
            impostor["source_video_sha256"]=sha(media)
            # The exact published source window cannot be replaced by synthetic data;
            # this synthetic source would otherwise generate a valid *empty* candidate set.
            report=analyze(media,impostor)
            self.assertEqual(report["candidate_count"],0)
            self.assertFalse(report["production_script_accepted"])
            self.assertFalse(report["scene_boundaries_verified"])
            with self.assertRaisesRegex(ValueError,"SHA-256 mismatch"):
                impostor["source_video_sha256"]="0"*64
                analyze(media,impostor)

if __name__=="__main__":
    unittest.main()
