#!/usr/bin/env python3
"""Readable pilot script quality checks with exact source cue/word lineage."""
import hashlib
import unittest
from build_caption_first_working_drafts import witness
from render_readable_caption_screenplay_v5 import render, EXPECTED_ADDITIONS, S09_CONTINUATION_GROUPS

class PilotReadable(unittest.TestCase):
    def test_complete_unmodified_original_words_and_roles(self):
        for episode,cues,units in (("S01E01",336,404),("S09E19",347,347)):
            with self.subTest(episode=episode):
                document,metadata,review=render(episode)
                _,_,originals,source_units,_=witness(episode)
                self.assertEqual(metadata["source_original_cues"],cues)
                self.assertEqual(metadata["source_original_units"],units)
                self.assertEqual(metadata["rendered_source_cue_ids_in_order"],list(range(1,cues+1)))
                self.assertEqual(metadata["rendered_source_cue_part_ids_in_order"],
                    [f"C{u['cue']:03d}.{u['part']}" for u in source_units])
                self.assertEqual(metadata["source_unit_text_sha256_in_order"],
                    [hashlib.sha256(u["source_text"].strip().encode()).hexdigest()
                     for u in source_units])
                self.assertEqual(metadata["new_provisional_context_label_count"],
                                 EXPECTED_ADDITIONS[episode])
                self.assertTrue(metadata["all_original_source_dialogue_units_preserved"])
                self.assertFalse(metadata["source_dialogue_words_rewritten"])
                self.assertFalse(metadata["speakers_original_audio_verified"])
                self.assertFalse(metadata["full_av_screenplay_accepted"])
                self.assertFalse(metadata["screenplay_editor_ready"])
                self.assertIn("Actual source-picture physical business",document)
                self.assertIn("Directly observed original-video scene",document)
                self.assertIn(f"C{cues:03d}.1",document)
                self.assertEqual((document,metadata,review),render(episode))

    def test_untimed_source_wraps_repaired_without_fake_source_times(self):
        text,metadata,review=render("S09E19")
        expected=sum(len(g)-1 for g in S09_CONTINUATION_GROUPS)
        self.assertEqual(metadata["paragraph_soft_wrapped_original_text_records_joined"],expected)
        self.assertGreater(expected,30)
        self.assertTrue(metadata["original_source_untimed_paragraphs_still_untimed"])
        self.assertEqual(metadata["new_provisional_context_label_count"],56)
        self.assertIn("C007.1–C008.1",text)
        self.assertIn("C175.1–C177.1",text)
        self.assertIn("source-caption",text.casefold())
        self.assertIn("UNTIMED original source",text)
        self.assertNotIn("AV certified",metadata["quality_state"])
        self.assertEqual(review["source_audio_listened_for_these_roles"],False)

    def test_s01_judicial_speaking_monologue_survives(self):
        text,metadata,_=render("S01E01")
        self.assertIn("HARRY STONE · PROVISIONAL TEXT-CONTEXT ASSIGNMENT",text)
        self.assertEqual(metadata["paragraph_soft_wrapped_original_text_records_joined"],0)
        self.assertFalse(metadata["original_source_untimed_paragraphs_still_untimed"])
        self.assertIn("courtroom",text.lower())

if __name__=="__main__":
    unittest.main()
