#!/usr/bin/env python3
"""A corrected character quote must not change any original source dialogue."""
import unittest
from build_s01_quote_correction_v4 import render,REF,CORRECTED
from build_credited_courtroom_guest_reader_v3 import build as source

class SourcePilotCorrection(unittest.TestCase):
    def test_two_credited_dialogue_sources_correct_only_one_earlier_mistake(self):
        old,old_index=source()
        text,proof=render()
        self.assertIn(CORRECTED,text)
        self.assertEqual(proof["original_held_source_cues"],336)
        self.assertEqual(proof["original_held_source_speaking_units"],404)
        self.assertEqual(proof["source_original_unit_word_hashes"],
                         old_index["source_all_speaking_word_hashes"])
        self.assertEqual(proof["corrected_prior_wrong_speaker_labels"],1)
        self.assertEqual(proof["new_provisional_characters_from_correction"],0)
        self.assertFalse(proof["source_dialogue_word_or_caption_time_modified"])
        self.assertFalse(proof["original_audio_speaker_match_verified"])
        self.assertFalse(proof["independently_full_original_AV_certified"])
        self.assertEqual(len(text.splitlines()),len(old.splitlines()))
        idx=[x for x in proof["reversible_dialogue_source_index"] if x["source_ref"]==REF]
        self.assertEqual(len(idx),1)
        self.assertEqual(idx[0]["speaker"],CORRECTED)
        self.assertTrue(idx[0]["previous_incorrect_provisional_label"].startswith("HARRY STONE"))
        self.assertEqual((text,proof),render())
    def test_preserve_unchanged_source_stage_business(self):
        old,_=source()
        new,_=render()
        self.assertEqual(old.count("SOURCE-PICTURE STAGE DIRECTION"),
                         new.count("SOURCE-PICTURE STAGE DIRECTION"))
        self.assertIn("SELMA HACKER · PROVISIONAL CREDITED-EPISODE DIALOGUE CONTEXT",new)

if __name__=="__main__":unittest.main()
