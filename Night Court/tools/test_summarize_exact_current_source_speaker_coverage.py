#!/usr/bin/env python3
"""Provisional original speaker counts must never use S09 joined reading blocks."""
import unittest
from summarize_exact_current_source_speaker_coverage import build,per_episode,expand

class SourceSpeakerCoverage(unittest.TestCase):
    def test_exact_original_units_and_all_unidentified_refs_accounted_for(self):
        report=build()
        self.assertEqual(report["source_speaking_units_total"],751)
        self.assertEqual(report["original_speaking_units_provisionally_attributed"],487)
        self.assertEqual(report["original_speaking_units_unidentified"],264)
        self.assertEqual(report["original_source_unit_attribution_percentage"],64.8)
        self.assertEqual(report["full_original_episode_editor_ready"],0)
        self.assertEqual(report["original_entire_av_episodes_certified"],0)
        self.assertFalse(report["all_original_audio_identifications_independently_verified"])
        self.assertEqual(report,build())
        self.assertTrue(all(not p["original_soundtrack_listened_to_resolve"]
           for ep in report["pilots"] for p in ep["unknown_original_speaking_unit_review_queue"]))
    def test_reading_blocks_are_not_original_source_timecoded_paragraphs(self):
        a=per_episode("S01E01")
        b=per_episode("S09E19")
        self.assertEqual((a["current_reading_blocks"],a["original_speaking_units"]), (404,404))
        self.assertEqual((a["original_speaking_units_provisionally_named"],a["original_speaking_units_unidentified"]),(306,98))
        self.assertTrue(a["original_subtitle_source_has_authentic_timecodes"])
        self.assertEqual((b["current_reading_blocks"],b["original_speaking_units"]),(311,347))
        self.assertEqual((b["current_reading_blocks_provisionally_named"],b["current_reading_blocks_unidentified"]),(152,159))
        self.assertEqual((b["original_speaking_units_provisionally_named"],b["original_speaking_units_unidentified"]),(181,166))
        self.assertFalse(b["original_subtitle_source_has_authentic_timecodes"])
        self.assertTrue(all(x["original_caption_start_ms"] is None and
                            x["original_caption_end_ms"] is None
                            for x in b["unknown_original_speaking_unit_review_queue"]))
        self.assertEqual(len(b["unknown_original_speaking_unit_review_queue"]),166)
    def test_exact_unrolled_original_caption_source_ranges(self):
        self.assertEqual(expand("C007.1"),[(7,1)])
        self.assertEqual(expand("C007.1–C009.1"),[(7,1),(8,1),(9,1)])
        self.assertEqual(expand("C002.2"),[(2,2)])
        with self.assertRaises(ValueError):expand("C003.2–C004.1")
        with self.assertRaises(ValueError):expand("C008.1–C007.1")
        with self.assertRaises(ValueError):expand("C008.1–C009.2")

if __name__=="__main__":unittest.main()
