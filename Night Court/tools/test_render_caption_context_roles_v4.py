#!/usr/bin/env python3
"""Source-only editorial role confidence and complete-caption preservation QA."""
import unittest
from render_caption_context_roles_v4 import render,context_proposals,EXPECTED
from render_caption_first_motion_edit_v3 import render as prior


class OriginalCaptionContextRoleTests(unittest.TestCase):
    def test_two_original_dialogue_scripts_preserved(self):
        for episode,count,cues in (("S01E01",18,336),("S09E19",20,347)):
            with self.subTest(episode=episode):
                original,_=prior(episode)
                new,report=render(episode)
                self.assertEqual(report["contextual_role_proposals_applied"],count)
                self.assertEqual(report["source_original_cue_count"],cues)
                self.assertTrue(report["all_original_dialogue_preserved_from_v3"])
                self.assertFalse(report["original_audio_speaker_identity_verified"])
                self.assertFalse(report["visual_face_character_identity_asserted"])
                self.assertFalse(report["source_untimed_paragraph_timecodes_fabricated"])
                self.assertFalse(report["substantial_all_episode_speaker_attribution_complete"])
                self.assertFalse(report["editor_ready"])
                self.assertFalse(report["independently_av_certified"])
                self.assertIn(f"C{cues:03d}.1",new)
                self.assertIn("source-caption contextual",new.casefold())
                self.assertIn("PROVISIONAL TEXT-CONTEXT ASSIGNMENT",new)
                self.assertGreater(len(new),len(original))
                self.assertEqual((new,report),render(episode))
                self.assertEqual(new.count("PROVISIONAL TEXT-CONTEXT ASSIGNMENT"),count)

    def test_character_proposals_are_not_img_or_audio_acceptance(self):
        s,report=render("S01E01")
        self.assertIn("DAN FIELDING · PROVISIONAL",s)
        self.assertIn("SHEILA GARDINER · PROVISIONAL",s)
        self.assertIn("HARRY STONE · PROVISIONAL",s)
        self.assertIn("C336.1",s)
        t,other=render("S09E19")
        self.assertIn("ROZ RUSSELL · PROVISIONAL",t)
        self.assertIn("MAC ROBINSON · PROVISIONAL",t)
        self.assertIn("DAN FIELDING · PROVISIONAL",t)
        self.assertIn("C347.1 · UNTIMED",t)
        self.assertEqual(other["source_original_cue_count"],347)

    def test_source_context_sha_and_bounded_evidence(self):
        for ep in EXPECTED:
            proposals,sha=context_proposals(ep)
            self.assertEqual(len(proposals),EXPECTED[ep])
            self.assertEqual(len(sha),64)
            self.assertTrue(all(p["independently_verified"] is False for p in proposals))


if __name__=="__main__":
    unittest.main()
