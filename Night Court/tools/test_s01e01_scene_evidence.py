#!/usr/bin/env python3
"""Fast offline tests: source cue selection and no fabricated observations."""
import json, unittest
from pathlib import Path
from build_s01e01_scene_evidence import CAPTION_DIR,SRT_SHA,digest,select_cues,FRAMES

class Tests(unittest.TestCase):
    def test_witness_integrity(self):
        self.assertEqual(digest(CAPTION_DIR/"original.srt"),SRT_SHA)
    def test_30_second_source_window(self):
        rows=[json.loads(x) for x in (CAPTION_DIR/"segments.jsonl").read_text().splitlines() if x.strip()]
        out=select_cues(rows)
        self.assertGreaterEqual(len(out),5)
        self.assertTrue(all(c["offset_status"]=="not_audio_verified" for c in out))
        self.assertTrue(all(c["start_ms"]<90000 and c["end_ms"]>60000 for c in out))
    def test_boundaries(self):
        self.assertEqual(len(FRAMES),10)
        self.assertTrue(all(60<=t<90 for t in FRAMES))
    def test_no_missing_source_cues(self):
        rows=[json.loads(x) for x in (CAPTION_DIR/"segments.jsonl").read_text().splitlines() if x.strip()]
        expected={x["cue"] for x in rows if x["end_ms"]>60000 and x["start_ms"]<90000}
        self.assertEqual(expected,{x["cue"] for x in select_cues(rows)})

if __name__=="__main__":unittest.main()
