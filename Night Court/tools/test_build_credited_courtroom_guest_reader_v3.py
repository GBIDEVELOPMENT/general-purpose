#!/usr/bin/env python3
"""Verify pilot case guest cast attribution changes only source-indexed headings."""
import unittest
from build_credited_courtroom_guest_reader_v3 import build,COUNT
from build_cast_context_reading_screenplays import render as previous

class CourtroomGuestSpeakerTest(unittest.TestCase):
    def test_source_complete_and_credibly_auditable(self):
        before,old=previous("S01E01")
        script,proof=build()
        self.assertEqual(proof["original_held_caption_cues"],336)
        self.assertEqual(proof["original_speaking_units"],404)
        self.assertEqual(proof["source_all_speaking_word_hashes"],
                         old["source_original_unit_text_hashes"])
        self.assertEqual(proof["additional_contextual_turns_proposed"],COUNT)
        self.assertEqual(proof["previously_unknown_source_blocks_assigned_provisionally"],COUNT)
        self.assertFalse(proof["source_words_or_original_times_modified"])
        self.assertFalse(proof["source_lip_or_audio_voice_identity_verified"])
        self.assertFalse(proof["full_original_video_action_coverage_complete"])
        self.assertFalse(proof["editor_ready"])
        self.assertFalse(proof["independently_av_certified"])
        self.assertTrue(proof["credited_cast_does_not_identify_people_in_photos"])
        self.assertEqual(len(before.splitlines()),len(script.splitlines()))
        self.assertIn("PHIL KERR · PROVISIONAL CREDITED-EPISODE",script)
        self.assertIn("LOUISE KERR · PROVISIONAL CREDITED-EPISODE",script)
        self.assertIn("CARLA BOUVIER · PROVISIONAL CREDITED-EPISODE",script)
        self.assertIn("HACKSAW HAMMOND · PROVISIONAL CREDITED-EPISODE",script)
        self.assertIn("SELMA HACKER · PROVISIONAL CREDITED-EPISODE",script)
        self.assertIn("SOURCE-PICTURE STAGE DIRECTION",script)
        self.assertEqual((script,proof),build())
    def test_previous_credited_episode_edits_remain(self):
        script,proof=build()
        self.assertIn("PAINTER · PROVISIONAL EPISODE-CAST AND DIALOGUE",script)
        self.assertIn("BULL SHANNON · PROVISIONAL EPISODE-CAST AND DIALOGUE",script)
        self.assertIn("SHEILA GARDINER · PROVISIONAL EPISODE-CAST AND DIALOGUE",script)
        self.assertEqual(len(proof["new_contextual_guest_role_proposals"]),106)

if __name__=="__main__":unittest.main()
