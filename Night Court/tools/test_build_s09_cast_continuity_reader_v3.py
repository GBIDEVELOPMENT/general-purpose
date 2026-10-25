#!/usr/bin/env python3
"""Conservative credited late-season original-untimed guest dialogue QA."""
import unittest
from build_s09_cast_continuity_reader_v3 import render,EXPECTED
from build_cast_context_reading_screenplays import render as earlier

class CastContinuity(unittest.TestCase):
    def test_original_script_complete_and_genuinely_more_readable(self):
        old,base=earlier("S09E19")
        script,report=render()
        self.assertEqual(report["source_original_untimed_paragraphs"],347)
        self.assertEqual(report["source_original_speaking_units"],347)
        self.assertEqual(report["source_unit_text_hashes_in_order"],
                         base["source_original_unit_text_hashes"])
        self.assertEqual(report["additional_provisional_guest_and_regular_voice_roles"],EXPECTED)
        self.assertEqual(report["previously_unknown_speaking_blocks_provisionally_named"],EXPECTED)
        self.assertEqual(len(old.splitlines()),len(script.splitlines()))
        self.assertFalse(report["source_original_paragraph_timestamps_created"])
        self.assertFalse(report["dialogue_or_observed_stage_directions_modified"])
        self.assertFalse(report["actors_identified_by_faces_or_pictures"])
        self.assertFalse(report["whole_original_source_av_certified"])
        self.assertFalse(report["original_episode_scene_edit_ready"])
        self.assertEqual((script,report),render())

    def test_real_alex_separate_from_guys_and_bartender(self):
        script,report=render()
        self.assertTrue(report["distinct_alex_and_the_guy_credited_roles_preserved"])
        self.assertFalse(report["the_guy_actual_spoken_voice_verified"])
        self.assertIn("BARTENDER · PROVISIONAL EPISODE-CAST DIALOGUE",script)
        self.assertIn("MAC ROBINSON · PROVISIONAL EPISODE-CAST DIALOGUE",script)
        self.assertIn("ROZ RUSSELL · PROVISIONAL EPISODE-CAST DIALOGUE",script)
        self.assertIn("BULL SHANNON · PROVISIONAL EPISODE-CAST DIALOGUE",script)
        self.assertIn("ALEX · PROVISIONAL EPISODE-CAST DIALOGUE",script)
        self.assertNotIn("THE GUY · PROVISIONAL EPISODE-CAST DIALOGUE",script)
        self.assertIn("UNTIMED",script)
        self.assertIn("I lied.",script)

if __name__=="__main__":
    unittest.main()
