#!/usr/bin/env python3
"""Source-evidence screenplay renderer acceptance on real reviewed scene."""
from copy import deepcopy
from pathlib import Path
import json,unittest
from render_evidence_linked_scene import render

BASE=Path(__file__).resolve().parents[1]/"seasons/S01/S01E01/derived/scene-review-v1"
class Tests(unittest.TestCase):
    def setUp(self):
        self.e=json.loads((BASE/"evidence.json").read_text())
        self.r=json.loads((BASE/"visual-observations.json").read_text())
    def test_real_scene_renders_without_guessing(self):
        s=render(self.e,self.r)
        assert "BOOK-LINED COURT OFFICE" in s
        assert "UNATTRIBUTED VOICE" in s
        assert "telephone receiver" in s
        assert "AV completeness certified:** No" in s
        assert s.count("| CAPTION C")==len(self.e["source_cues"])==9
        assert s.count("| VISUAL STILL")==len(self.r["time_bounded_observations"])==5
    def test_rejects_wrong_media(self):
        x=deepcopy(self.r);x["source_media_sha256"]="0"*64
        with self.assertRaises(ValueError):render(self.e,x)
    def test_rejects_unreviewed_frame_fabrication(self):
        x=deepcopy(self.r);x["time_bounded_observations"][0]["motion_inference"]=True
        with self.assertRaises(ValueError):render(self.e,x)
    def test_rejects_missing_still(self):
        x=deepcopy(self.r);x["time_bounded_observations"][0]["evidence"]=["frames/fake.jpg"]
        with self.assertRaises(ValueError):render(self.e,x)
if __name__=="__main__":unittest.main()
