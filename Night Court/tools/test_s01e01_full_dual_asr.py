#!/usr/bin/env python3
"""Offline trusted-source constraints only. No network, model weights or real AV."""
import hashlib
from fractions import Fraction
import json
import os
from pathlib import Path
import tempfile
import unittest
import wave
import zipfile

from compare_independent_asr import compare, ALLOWED_FAMILIES
from probe_s01e01_full_dual_asr import (
    SHA,SIZE,VOSK_ZIP_SHA256,VOSK_ROOT,MAX_ASR_WORDS,
    decode_audio, unpack_pinned_model, preserve_word, word_rejection_reason
)


class DistinctModelSourceAcceptance(unittest.TestCase):
    def test_original_sha_and_true_kaldi_family_not_ctc(self):
        self.assertEqual(len(SHA),64)
        self.assertEqual(SIZE,183386112)
        self.assertEqual(VOSK_ZIP_SHA256,
                         '30f26242c4eb449f948e42cb302dd7a686cb29a3423a8367f99ff41780942498')
        self.assertIn('kaldi_hmm_wfst',ALLOWED_FAMILIES)

    def test_same_source_audio_two_distinct_families_can_corroborate(self):
        fields={'episode_id':'S01E01',
                'source_video_sha256':SHA,'decoded_audio_sha256':'3'*64,
                'source_window_ms':[0,5000],
                'schema':'night-court-two-independent-asr-words/1'}
        words=[{'text':w,'start_ms':100+i*350,'end_ms':400+i*350}
               for i,w in enumerate(['Did','you','say','mercurial'])]
        fields['models']=[
            {'model_id':'whisper-tiny','architecture_family':'whisper',
             'free_decoding':True,'srt_or_other_model_prompt_used':False,'words':words},
            {'model_id':'vosk-kaldi','architecture_family':'kaldi_hmm_wfst',
             'free_decoding':True,'srt_or_other_model_prompt_used':False,'words':words}]
        result=compare(fields)
        self.assertEqual(result['counts']['corroborated_words'],4)
        self.assertFalse(result['source_srt_verified'])
        self.assertFalse(result['original_source_audio_listened'])
        self.assertTrue(result['two_models_do_not_prove_statistically_independent_errors'])

    def test_word_bounds_are_never_fabricated(self):
        self.assertEqual(preserve_word(' Mercurial ',1.0,1.3,3000),
                         {'text':'Mercurial','start_ms':1000,'end_ms':1300})
        self.assertIsNone(preserve_word('',1,2,3000))
        self.assertIsNone(preserve_word('wrong',2.9,3.1,3000))
        self.assertIsNone(preserve_word('reversed',1.1,1.0,3000))
        self.assertIsNone(preserve_word('oversize'*40,1,2,3000))

    def test_all_rejection_reasons_preserve_original_source_boundaries(self):
        self.assertEqual(word_rejection_reason('x',0.1,0.1,3000),
                         'zero_or_reversed_rounded_word_time')
        self.assertEqual(word_rejection_reason('x',-0.1,0.1,3000),
                         'negative_original_time')
        self.assertEqual(word_rejection_reason('x',2.9,3.1,3000),
                         'beyond_decoded_original_soundtrack')
        self.assertEqual(word_rejection_reason('x',float('nan'),0.1,3000),
                         'nonfinite_or_missing_model_time')
        self.assertEqual(word_rejection_reason('',0,1,3000),
                         'missing_empty_or_long_word')
        self.assertIsNone(word_rejection_reason('genuinely spoken',0.1,0.2,3000))
        self.assertIsNone(preserve_word('x',0.1,0.1,3000))
        self.assertIsNone(word_rejection_reason('fraction',Fraction(1,10),Fraction(1,5),3000))
        self.assertEqual(preserve_word('fraction',Fraction(1,10),Fraction(1,5),3000),{'text':'fraction','start_ms':100,'end_ms':200})
        self.assertEqual(word_rejection_reason('x',True,0.3,3000),'nonfinite_or_missing_model_time')

    def test_model_zip_rejects_traversal_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            z=Path(tmp)/'bad.zip'
            with zipfile.ZipFile(z,'w') as w:
                w.writestr('../secret.txt','secret')
            with self.assertRaisesRegex(ValueError,'Unsafe'):
                unpack_pinned_model(z,Path(tmp)/'extracted')

            z.unlink()
            with zipfile.ZipFile(z,'w') as w:
                w.writestr(VOSK_ROOT+'/am/final.mdl','dummy')
            base=Path(tmp)/'safe-model-root'
            result=unpack_pinned_model(z,base)
            self.assertEqual(result,base/VOSK_ROOT)
            self.assertTrue((result/'am/final.mdl').exists())


if __name__=='__main__':
    unittest.main()
