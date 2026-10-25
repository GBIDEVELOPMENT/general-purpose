#!/usr/bin/env python3
"""Both true original-source picture reviews must be source-locked and honest."""
import unittest
from build_s01_quote_correction_v4 import render as s01
from build_s09_impostor_speaking_reader_v4 import render as s09
from render_extra_observed_original_stage_v5 import (
    render,observed,source_counts,EXPECTED)

class AdditionalFilmStageTest(unittest.TestCase):
    def test_original_video_observations_verified_without_speech_identity(self):
        for ep in EXPECTED:
            with self.subTest(ep=ep):
                observations,digest=observed(ep)
                self.assertEqual(len(observations),3)
                self.assertEqual(len(digest),64)
                self.assertEqual(sum(x["frame_count"] for x in observations),300)
                self.assertTrue(all(len(x["contact_sheet_sha"])==2 for x in observations))
                self.assertTrue(all("not_native_pts" in x["source_frame_time_kind"]
                                    for x in observations))
    def test_s01_actual_source_painter_and_coins_inline_in_original_caption_dialogue(self):
        before,index=s01()
        after,report=render("S01E01")
        self.assertEqual((report["source_original_cues"],report["source_original_speaking_units"]),(336,404))
        self.assertEqual(report["source_speaking_units_attributed_provisionally"],306)
        self.assertEqual(report["source_speaking_units_unidentified"],98)
        self.assertEqual(report["new_original_picture_stage_windows"],3)
        self.assertEqual(report["source_movie_frame_windows_proving_original_target"],3)
        self.assertEqual(report["source_movie_frame_windows_rejecting_review_target"],0)
        self.assertIn("A man in bright yellow sleeves",after)
        self.assertIn("small pale round object",after)
        self.assertIn("dark red cardigan",after)
        self.assertIn("SOURCE-PICTURE STAGE DIRECTION",after)
        self.assertTrue(after.count("Source-video observed stage business")>=3)
        self.assertTrue(all(x["original_source_srt_cue"]>0 for x in report["source_picture_insertions_or_chronology_entries"]))
        self.assertTrue(all(not x["spoken_source_alignment_verified"] for x in report["source_picture_insertions_or_chronology_entries"]))
        self.assertFalse(report["original_dialogue_words_edited"])
        self.assertEqual((after,report),render("S01E01"))
    def test_s09_separate_untimed_movie_not_pretend_safe_or_entry(self):
        original,index=s09()
        after,report=render("S09E19")
        self.assertTrue(after.startswith(original.rstrip()))
        self.assertEqual((report["source_original_cues"],report["source_original_speaking_units"]),(347,347))
        self.assertEqual(report["original_reading_blocks"],311)
        self.assertEqual(report["source_speaking_units_attributed_provisionally"],181)
        self.assertEqual(report["source_speaking_units_unidentified"],166)
        self.assertEqual(report["new_original_picture_stage_windows"],3)
        self.assertEqual(report["source_movie_frame_windows_proving_original_target"],0)
        self.assertEqual(report["source_movie_frame_windows_rejecting_review_target"],3)
        self.assertIn("No safe is visibly opened",after)
        self.assertIn("prominent yellow rolling production credits",after)
        self.assertIn("both together at the same small lamp-lit table",after)
        self.assertTrue(all(x["original_text_paragraph_time_ms"] is None
                            for x in report["source_picture_insertions_or_chronology_entries"]))
        self.assertFalse(report["source_untimed_captions_given_timecodes"])
        self.assertFalse(report["full_episode_editor_ready"])
        self.assertEqual((after,report),render("S09E19"))

if __name__=="__main__":
    unittest.main()
