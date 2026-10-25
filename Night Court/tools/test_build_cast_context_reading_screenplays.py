#!/usr/bin/env python3
"""External credited episode roles are editorial hypotheses, not identified faces."""
import unittest
from build_cast_context_reading_screenplays import render,inputs,EXPECTED
from build_clean_reading_screenplay import build as original


class CastRoles(unittest.TestCase):
    def test_both_complete_original_dialogue_sources_and_reversible_index(self):
        for ep,cues,units,extra,new in (
            ("S01E01",336,404,82,82),
            ("S09E19",347,347,18,17)):
            with self.subTest(episode=ep):
                src,index=original(ep)
                text,report=render(ep)
                self.assertEqual(report["source_original_cues"],cues)
                self.assertEqual(report["source_original_speaking_units"],units)
                self.assertEqual(report["source_original_unit_text_hashes"],
                                 index["original_source_cue_unit_hashes_in_order"])
                self.assertEqual(report["provisional_cast_attribution_edits"],extra)
                self.assertEqual(report["newly_named_previously_unknown_dialogue_blocks"],new)
                self.assertEqual(len(report["source_reading_index"]),
                                 index["indexed_reading_dialogue_blocks"])
                self.assertEqual(src.count("\n"),text.count("\n"))
                self.assertFalse(report["identities_identified_from_images"])
                self.assertFalse(report["original_audio_or_lips_verified"])
                self.assertFalse(report["whole_episode_editor_ready"])
                self.assertFalse(report["independently_av_certified"])
                self.assertFalse(report["original_source_words_changed"])
                self.assertEqual((text,report),render(ep))
                self.assertTrue(all(not row["independent_voice_or_face_identification"]
                    for row in report["additional_cast_dialogue_assessments"]))

    def test_pilot_actual_character_dialogue_from_original_credited_episode(self):
        text,data=render("S01E01")
        self.assertIn("LANA WAGNER · PROVISIONAL EPISODE-CAST AND DIALOGUE",text)
        self.assertIn("PAINTER · PROVISIONAL EPISODE-CAST AND DIALOGUE",text)
        self.assertIn("BULL SHANNON · PROVISIONAL EPISODE-CAST AND DIALOGUE",text)
        self.assertIn("SHEILA GARDINER · PROVISIONAL EPISODE-CAST AND DIALOGUE",text)
        self.assertIn("COURIER · PROVISIONAL EPISODE-CAST AND DIALOGUE",text)
        self.assertIn("That's depraved.",text)
        self.assertIn("My wife won't do that.",text)
        self.assertIn("SOURCE-PICTURE STAGE DIRECTION",text)

    def test_s09_real_alex_distinct_from_separately_credited_other_man(self):
        text,data=render("S09E19")
        self.assertTrue(data["known_distinct_guest_characters_alex_and_the_guy"])
        self.assertIn("ALEX · PROVISIONAL EPISODE-CAST AND DIALOGUE",text)
        self.assertIn("FINGERS KIRBY · PROVISIONAL EPISODE-CAST AND DIALOGUE",text)
        self.assertIn("BULL SHANNON · PROVISIONAL EPISODE-CAST AND DIALOGUE",text)
        self.assertIn("347",str(data["source_original_cues"]))
        self.assertNotIn("THE GUY · PROVISIONAL EPISODE-CAST AND DIALOGUE",text)
        self.assertFalse(data["original_audio_or_lips_verified"])
        self.assertFalse(data["identities_identified_from_images"])

    def test_credited_roster_has_provenance_and_no_photo_identity(self):
        for ep in EXPECTED:
            cast,proposals,digest=inputs(ep)
            self.assertEqual(len(proposals),EXPECTED[ep])
            self.assertEqual(len(digest),64)
            self.assertTrue(cast["primary_source_urls"])
            self.assertTrue(all(not x["image_identity_claimed"] for x in proposals))

if __name__=="__main__":
    unittest.main()
