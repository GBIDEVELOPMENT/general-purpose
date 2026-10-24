#!/usr/bin/env python3
"""Source-only unit tests for honest original-dialogue coverage denominator."""
import copy
import json
import unittest
from measure_s01e01_three_witness_srt_coverage import (
    calculate,DERIVED,SOURCE_SRT
)


class Coverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=DERIVED.read_bytes()
        cls.srt=SOURCE_SRT.read_bytes()

    def test_complete_original_cue_word_denominator_and_no_human_claim(self):
        x=calculate(self.raw,self.srt)
        self.assertEqual(x['independent_two_model_consensus_spans'],200)
        self.assertEqual(x['three_text_witness_correspondence_spans'],184)
        self.assertEqual(x['two_model_agreement_needing_original_audio_listening'],16)
        self.assertEqual(x['original_srt_cues_total'],336)
        self.assertGreater(x['original_srt_word_tokens_total'],1000)
        self.assertGreater(x['original_srt_unique_word_positions_with_independent_2asr_and_srt_correspondence_candidate'],0)
        self.assertLessEqual(x['original_srt_unique_word_positions_with_independent_2asr_and_srt_correspondence_candidate'],
                             x['original_srt_word_tokens_total'])
        self.assertFalse(x['independent_original_source_audio_human_verified'])
        self.assertFalse(x['complete_original_srt_dialogue_verified'])
        self.assertFalse(x['complete_episode_production_script_accepted'])

    def test_unchanged_original_srt_and_no_duplicate_dialogue_corroboration(self):
        a=calculate(self.raw,self.srt)
        d=json.loads(self.raw)
        d['review_spans'][1]['model_agreed_text_candidate']=d['review_spans'][0]['model_agreed_text_candidate']
        d['review_spans'][1]['source_caption_cue_ids']=d['review_spans'][0]['source_caption_cue_ids']
        d['review_spans'][1]['source_caption_verbatim']=d['review_spans'][0]['source_caption_verbatim']
        fake=json.dumps(d).encode()
        b=calculate(fake,self.srt,strict=False)
        self.assertLess(b['original_srt_unique_word_positions_with_independent_2asr_and_srt_correspondence_candidate'],
                        a['original_srt_unique_word_positions_with_independent_2asr_and_srt_correspondence_candidate'])
        with self.assertRaisesRegex(ValueError,'SRT source changed'):
            calculate(self.raw,self.srt+b'\n')

    def test_cannot_relabel_source_subtitle_mismatch_as_three_witness(self):
        d=json.loads(self.raw)
        conflict=next(x for x in d['review_spans'] if x['review_tier']=='two_model_agreement_caption_lexical_disagreement')
        conflict['review_tier']='three_text_witness_correspondence_candidate'
        with self.assertRaisesRegex(ValueError,'proportions'):
            calculate(json.dumps(d).encode(),self.srt,strict=False)


if __name__=='__main__':
    unittest.main()
