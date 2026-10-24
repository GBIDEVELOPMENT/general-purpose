#!/usr/bin/env python3
"""Offline CTC correctness: repeated letters, boundaries and abstention."""
import unittest
import numpy as np
from ctc_source_aligner import normalize_words,encode,viterbi,align_words

class ForcedAlignmentTests(unittest.TestCase):
    def setUp(self):
        self.vocab={"_":0,"A":1,"B":2,"|":3}
    def test_repeated_letters_need_intermediate_blank(self):
        words=["AA","B"]
        labels,mapping=encode(words,self.vocab)
        self.assertEqual(labels,[1,1,3,2])
        self.assertEqual(mapping,[0,0,None,1])
        # blank,A,blank,A,blank,|,blank,B,blank
        expected=[0,1,0,1,0,3,0,2,0]
        lp=np.log(np.full((len(expected),4),0.01))
        for t,c in enumerate(expected):lp[t,c]=np.log(.97)
        out=align_words(lp,"A'A B!",self.vocab,blank=0,
                        absolute_start_ms=60000,frame_step_ms=20)
        self.assertEqual([x["word"] for x in out["words"]],words)
        self.assertEqual(out["words"][0]["time_candidate_ms"],[60020,60080])
        self.assertEqual(out["words"][1]["time_candidate_ms"],[60140,60160])
        self.assertEqual(out["abstentions"],0)
        self.assertFalse(out["audio_word_timing_verified"])
    def test_impossible_repeated_tokens_fail(self):
        lp=np.log(np.full((2,4),.25))
        with self.assertRaises(ValueError):viterbi(lp,[1,1],0)
    def test_low_support_abstains_even_if_forced_path_exists(self):
        lp=np.log(np.full((8,4),.25))
        out=align_words(lp,"AB",self.vocab,blank=0,absolute_start_ms=0,
                        frame_step_ms=20,min_confidence=.7)
        self.assertEqual(out["abstentions"],1)
        self.assertEqual(out["words"][0]["status"],"abstain_low_acoustic_support")
    def test_bad_source_and_no_words(self):
        self.assertEqual(normalize_words("I'm... there!"),["IM","THERE"])
        with self.assertRaises(ValueError):encode([],self.vocab)
        with self.assertRaises(ValueError):viterbi(np.zeros((9,4)),[],0)
        with self.assertRaises(ValueError):viterbi(np.zeros((9,4)),[9],0)
        with self.assertRaises(ValueError):viterbi(np.full((9,4),np.nan),[1],0)

if __name__=="__main__":unittest.main()
