#!/usr/bin/env python3
"""Cross-method candidate comparison invariants on immutable S01E01 evidence."""
import unittest
from compare_s01e01_word_models import evaluate

class CompareModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.doc=evaluate()
    def test_complete_source_tokens_are_counted_once(self):
        d=self.doc
        self.assertGreater(d["source_words"],50)
        self.assertEqual(d["source_words"],len(d["per_source_word_review"]))
        self.assertEqual(d["shared_words_with_both_time_candidates"],39)
        self.assertEqual(d["within_300ms_start_proposals"],37)
        self.assertEqual(d["over_300ms_start_disagreements"],2)
        self.assertEqual(sum(d["counts"].values()),d["source_words"])
    def test_not_independent_or_verified(self):
        d=self.doc
        self.assertFalse(d["audiovisual_word_timing_verified"])
        self.assertFalse(d["character_voices_verified"])
        self.assertIn("tiny.en",d["shared_window_dependence"])
        for x in d["per_source_word_review"]:
            self.assertFalse(x["manual_audio_confirmation"])
            self.assertFalse(x["speaker_verified"])
            self.assertFalse(x["original_caption_text_modified"])
    def test_genuinely_different_cases_survive(self):
        d=self.doc
        unresolved=[x for x in d["per_source_word_review"]
                    if x["source_review_priority"]!="two_model_start_proximity_300ms_or_less"]
        self.assertTrue(any(x["original_normalized_word"]=="MINIMIFIDIAN" for x in unresolved))
        self.assertTrue(any(x["original_normalized_word"]=="MERCURIAL" for x in unresolved))
        self.assertTrue(any(x["source_cue"]==27 for x in unresolved))
    def test_clock_offsets_explicit(self):
        d=self.doc
        both=[x for x in d["per_source_word_review"] if x["start_delta_ctc_minus_tiny_ms"] is not None]
        self.assertTrue(all(
            x["start_delta_ctc_minus_tiny_ms"]==
            x["ctc_start_end_ms"][0]-x["tiny_en_start_end_ms"][0] for x in both))

if __name__=="__main__":unittest.main()
