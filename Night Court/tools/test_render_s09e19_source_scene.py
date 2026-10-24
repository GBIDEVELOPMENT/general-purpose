#!/usr/bin/env python3
"""Full source/AV integrity of S09E19 first scene research script."""
import unittest
from render_s09e19_source_scene import build,TXT_SHA,AVI_SHA

class IntegratedSourceScene(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet,cls.md=build()
    def test_full_source_unchanged_and_partial_scene_only(self):
        p=self.packet
        self.assertEqual(p["source_original_untimed_text_sha256"],TXT_SHA)
        self.assertEqual(p["source_media_sha256"],AVI_SHA)
        self.assertEqual(p["source_paragraph_count"],347)
        self.assertEqual(p["source_paragraph_dialogue_candidates"],5)
        self.assertEqual(p["reviewed_sampled_video_observations"],6)
        self.assertEqual(p["observed_video_excerpt_ms"],[900000,925000])
        self.assertFalse(p["original_episode_audiovisual_complete"])
    def test_candidate_dialogue_never_becomes_verified_subtitle(self):
        p=self.packet
        self.assertTrue(p["original_source_paragraphs_still_untimed"])
        self.assertFalse(p["independent_audio_word_verification"])
        self.assertFalse(p["independent_speaker_character_attribution"])
        for e in p["events"]:
            if e["source_kind"]=="original_untimed_source_paragraph_candidate":
                self.assertIsNone(e["candidate_speaking_character"])
                self.assertFalse(e["human_audio_dialogue_verified"])
                self.assertTrue(e["original_source_paragraph_has_no_timecodes"])
                self.assertTrue(900000<=e["video_candidate_interval_ms"][0]<e["video_candidate_interval_ms"][1]<=925000)
    def test_first_script_has_genuine_visual_evidence(self):
        p=self.packet
        self.assertEqual(len(p["events"]),11)
        for e in p["events"]:
            if e["source_kind"]=="sampled_original_video_observation":
                self.assertTrue(all(len(x["sha256"])==64 for x in e["frame_evidence"]))
                self.assertIsNone(e["speaker_identity"])
                self.assertFalse(e["scene_action_continuous_video_verified"])
        self.assertIn("P240",self.md)
        self.assertIn("UNVERIFIED",self.md)
        self.assertIn("Frame evidence:",self.md)

if __name__=="__main__":unittest.main()
