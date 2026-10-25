#!/usr/bin/env python3
"""Original-cue-preserving low-clutter reader manuscript regression."""
import unittest
from build_clean_reading_screenplay import build
from render_in_scene_stage_directions_v6 import render as source

class CleanScript(unittest.TestCase):
    def test_both_full_dialogue_manuscripts_have_reversible_provenance(self):
        for ep,cues,units in (("S01E01",336,404),("S09E19",347,347)):
            with self.subTest(ep=ep):
                text,proof=build(ep)
                orig,old,_=source(ep)
                self.assertEqual(proof["source_original_cues"],cues)
                self.assertEqual(proof["source_original_speaking_units"],units)
                self.assertEqual(proof["original_source_cue_unit_hashes_in_order"],
                                 old["v5_original_unit_text_sha256_in_order"])
                self.assertFalse(proof["full_episode_editor_ready"])
                self.assertFalse(proof["independent_av_certification"])
                self.assertFalse(proof["source_speakers_verified"])
                self.assertTrue(len(proof["dialogue_index"])>=units-40)
                self.assertIn("Working screenplay",text)
                self.assertIn("UNIDENTIFIED SPEAKER",text)
                self.assertNotIn("*Source: C",text)
                self.assertEqual((text,proof),build(ep))
    def test_s01_real_inline_action_s09_untimed(self):
        s,_=build("S01E01")
        self.assertIn("SOURCE-PICTURE STAGE DIRECTION",s)
        t,m=build("S09E19")
        self.assertIn("UNTIMED",t)
        self.assertIn("P.S. Do I Know You?",t)
        self.assertFalse(m["original_timing_generated_for_untimed_source"])
if __name__=="__main__":unittest.main()
