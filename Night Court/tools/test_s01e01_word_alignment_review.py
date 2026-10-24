#!/usr/bin/env python3
"""Provenance/epistemic regression on the real 30s ASR and caption witnesses."""
import unittest
from build_s01e01_word_alignment_review import build, tokens, turns, word_matches

class ReviewAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=build()
        cls.cues={x["cue"]:x for x in cls.doc["cue_turn_packets"]}
    def test_identity_and_coverage(self):
        x=self.doc
        self.assertEqual(x["source_caption_cues"],9)
        self.assertEqual(x["asr_segments"],10)
        self.assertEqual(set(self.cues),set(range(19,28)))
        self.assertFalse(x["verified_word_alignment"])
        self.assertFalse(x["verified_speaker_identity"])
        self.assertFalse(x["verified_source_video_speech_alignment"])
    def test_split_real_two_voice_source_typography(self):
        self.assertEqual(len(self.cues[19]["source_turns"]),2)
        self.assertEqual(len(self.cues[22]["source_turns"]),2)
        self.assertEqual(self.cues[19]["source_turns"][0]["asr_segment_index"],None)
    def test_word_anchors_are_only_exact_matched_model_tokens(self):
        matched=0
        for cue in self.cues.values():
            for turn in cue["source_turns"]:
                self.assertIsNone(turn["speaker_identity"])
                source_tokens=tokens(turn["text"])
                for w in turn["exact_word_time_candidates"]:
                    self.assertEqual(source_tokens[w["source_caption_word_index"]],w["source_word"])
                    self.assertTrue(60000<=w["proposed_audio_interval_ms"][0]<w["proposed_audio_interval_ms"][1]<=90000)
                    self.assertIn("not_forced_alignment",w["status"])
                    matched+=1
        self.assertGreater(matched,35)
    def test_protect_the_rare_words(self):
        self.assertEqual(self.cues[24]["source_cue_text"],"Does a bear extravasate in the forest?")
        self.assertEqual(self.cues[22]["source_turns"][1]["text"],"Minimifidian?")
        self.assertTrue(self.doc["review_notes"])
    def test_segment_comparison_is_not_global_time_sync(self):
        self.assertIn("NOT a global sync correction",self.doc["strong_segment_start_difference_ms"]["meaning"])
    def test_missing_asr_not_emotion_guess(self):
        self.assertEqual(turns("- Hello.\n- Goodbye.")[0]["speaker_identity"] if "speaker_identity" in turns("- Hello.\n- Goodbye.")[0] else None,None)
        self.assertEqual(tokens("Minimifidian?"),["minimifidian"])
        self.assertEqual(word_matches("Hello",{"word_candidates":[{"word":"Goodbye","start_ms":60000,"end_ms":60400,"model_probability":0.99}]})[0],[])

if __name__=="__main__":unittest.main()
