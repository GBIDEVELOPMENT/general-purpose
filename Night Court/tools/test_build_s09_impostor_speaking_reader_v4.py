#!/usr/bin/env python3
"""Narrative impostor identities have audit provenance; no original voice claims."""
import unittest
from build_s09_impostor_speaking_reader_v4 import render,COUNT
from build_s09_cast_continuity_reader_v3 import render as prior

class ImpostorEpisodeRoles(unittest.TestCase):
    def test_real_episode_credit_and_source_dialogue_consistency(self):
        old,base=prior()
        script,report=render()
        self.assertEqual(report["source_original_untimed_paragraphs"],347)
        self.assertEqual(report["source_original_spoken_units"],347)
        self.assertEqual(report["held_original_source_unit_word_hashes"],
                         base["source_unit_text_hashes_in_order"])
        self.assertEqual(report["new_provisional_speaker_role_blocks"],COUNT)
        self.assertEqual(report["previously_unidentified_dialogue_blocks_provisionally_labeled"],COUNT)
        self.assertEqual(len(old.splitlines()),len(script.splitlines()))
        self.assertFalse(report["original_source_words_or_paragraph_times_changed"])
        self.assertFalse(report["public_reference_images_used_to_identify_people"])
        self.assertFalse(report["lips_or_voice_verified_on_original_video"])
        self.assertFalse(report["whole_episode_script_editor_ready"])
        self.assertTrue(report["original_two_impostor_credit_distinction_preserved"])
        self.assertEqual((script,report),render())
    def test_creds_dual_identity_and_ambiguous_real_person_stays_unnamed(self):
        script,report=render()
        self.assertIn("LISETTE HOCHEISER (PLAYING ROZ) · PROVISIONAL",script)
        self.assertIn("THE GUY (PLAYING ALEX) · PROVISIONAL",script)
        self.assertIn("ROZ RUSSELL · PROVISIONAL",script)
        self.assertIn("ALEX PATTERSON · PROVISIONAL",script)
        self.assertEqual(script.count("LISETTE HOCHEISER (PLAYING ROZ) · PROVISIONAL"),11)
        self.assertEqual(script.count("THE GUY (PLAYING ALEX) · PROVISIONAL"),7)
        self.assertIn("UNTIMED",script)

if __name__=="__main__":unittest.main()
