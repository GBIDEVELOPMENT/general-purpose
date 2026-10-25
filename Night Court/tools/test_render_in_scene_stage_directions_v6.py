#!/usr/bin/env python3
"""Original source AV picture stage insertions must never change cue dialogue."""
import unittest
from build_caption_first_working_drafts import witness
from render_in_scene_stage_directions_v6 import render
from render_readable_caption_screenplay_v5 import render as v5

class StageReadings(unittest.TestCase):
    def test_all_held_dialogue_and_source_sha_survive(self):
        for episode,cuecount,unitcount in (("S01E01",336,404),("S09E19",347,347)):
            with self.subTest(episode=episode):
                screenplay,proof,review=render(episode)
                old,oldproof,_=v5(episode)
                self.assertEqual(proof["source_original_cues"],cuecount)
                self.assertEqual(proof["source_original_speaking_units"],unitcount)
                self.assertTrue(proof["all_v5_original_cue_text_and_fingerprints_preserved"])
                self.assertEqual(proof["v5_original_unit_text_sha256_in_order"],
                                 oldproof["source_unit_text_sha256_in_order"])
                self.assertFalse(proof["original_audio_lip_voices_matched"])
                self.assertFalse(proof["screenplay_editor_ready"])
                self.assertFalse(proof["independently_whole_episode_av_certified"])
                self.assertIn(f"C{cuecount:03d}.1",screenplay)
                self.assertEqual((screenplay,proof,review),render(episode))

    def test_real_timed_s01_picture_act_is_inside_dialogue_not_just_appendix(self):
        script,proof,review=render("S01E01")
        self.assertEqual(proof["original_srt_nearby_in_scene_still_notes"],17)
        self.assertEqual(proof["original_srt_nearby_in_scene_motion_notes"],2)
        self.assertEqual(len(proof["source_timed_caption_evidence_insertions"]),19)
        self.assertIn("SOURCE-PICTURE STAGE DIRECTION",script)
        self.assertIn("A man in a grey shirt and blue trousers reclines",script)
        self.assertIn("reclines along the padded ledge",script)
        self.assertIn("nearby timing locator",script)
        self.assertLess(script.index("SOURCE-PICTURE STAGE DIRECTION"),
                        script.index("## Source-picture motion and setting evidence"))
        self.assertTrue(all(not x["speaker_or_original_audio_verified"]
                            and not x["native_frame_pts_accepted"]
                            for x in proof["source_timed_caption_evidence_insertions"]))

    def test_untimed_s09_source_movie_not_silently_aligned_to_paragraphs(self):
        script,proof,review=render("S09E19")
        self.assertEqual(proof["original_srt_nearby_in_scene_still_notes"],0)
        self.assertEqual(proof["original_srt_nearby_in_scene_motion_notes"],0)
        self.assertEqual(proof["source_timed_caption_evidence_insertions"],[])
        self.assertEqual(script.count("SOURCE-PICTURE STAGE DIRECTION"),0)
        self.assertIn("C347.1",script)
        self.assertIn("UNTIMED",script)

if __name__=="__main__":
    unittest.main()
