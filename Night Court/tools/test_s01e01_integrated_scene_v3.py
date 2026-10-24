#!/usr/bin/env python3
"""Defend the source/interpretation boundary of the 30s script renderer."""
import unittest
from render_s01e01_integrated_scene_v3 import build

class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc,cls.md=build()
    def test_complete_bounded_evidence(self):
        c=self.doc["counts_and_gates"]
        self.assertEqual(c["source_caption_cues"],9)
        self.assertEqual(c["explicit_subtitle_typographic_voice_turns"],11)
        self.assertEqual(c["reviewed_static_observations"],5)
        self.assertEqual(c["reviewed_dense_motion_observations"],6)
        self.assertEqual(c["exact_text_ASR_word_time_candidates"],45)
        self.assertFalse(c["scene_audiovisual_complete"])
    def test_no_confident_character_or_emotion_invented(self):
        for event in self.doc["events"]:
            self.assertIn(event["source_kind"],("caption_turn","reviewed_static_frame","reviewed_sampled_sequence"))
            if event["source_kind"]=="caption_turn":
                self.assertEqual(event["review_status"],"unattributed_source_dialogue_candidate_audio_timing")
        self.assertIn("UNIDENTIFIED VOICE",self.md)
        self.assertNotIn("**DAN**",self.md)
        self.assertNotIn("**BULL**",self.md)
    def test_hard_comic_words_preserved(self):
        self.assertIn("Minimifidian?",self.md)
        self.assertIn("extravasate",self.md)
    def test_every_visual_has_linked_frames(self):
        for event in self.doc["events"]:
            if event["source_kind"]!="caption_turn":
                self.assertTrue(event["evidence"])
                self.assertTrue(all("frames/" in x for x in event["evidence"]))
    def test_subtitle_boundaries_flagged(self):
        self.assertIn("starts outside sample",self.md)
        self.assertIn("continues beyond sample",self.md)

if __name__=="__main__":unittest.main()
