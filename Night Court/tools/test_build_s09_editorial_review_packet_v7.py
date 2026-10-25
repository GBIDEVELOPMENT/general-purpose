#!/usr/bin/env python3
import hashlib
import unittest
from build_s09_editorial_review_packet_v7 import build
from render_in_scene_stage_directions_v6 import render as prior

class OriginalSourceEditorPacketTests(unittest.TestCase):
    def test_untimed_original_script_exact_prefix_and_honest_review_guide(self):
        original,old_manifest,_=prior("S09E19")
        text,proof=build()
        self.assertTrue(text.startswith(original.rstrip()))
        self.assertIn("15 suggested paragraph positions",text)
        self.assertIn("three picture events intentionally",text)
        self.assertIn("ABSTAIN",text)
        self.assertIn("UNVERIFIED",text)
        self.assertIn("C347.1",text)
        self.assertEqual(proof["original_source_untimed_paragraphs_preserved"],347)
        self.assertEqual(proof["source_v6_screenplay_sha256"],hashlib.sha256(original.encode()).hexdigest())
        self.assertEqual(proof["source_picture_review_suggestions"],15)
        self.assertEqual(proof["source_picture_review_abstentions"],3)
        self.assertFalse(proof["source_paragraph_original_times_invented"])
        self.assertFalse(proof["editor_ready"])
        self.assertFalse(proof["independently_av_certified"])
        self.assertEqual((text,proof),build())
if __name__=="__main__":unittest.main()
