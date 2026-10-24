#!/usr/bin/env python3
"""Synthetic vectors only: no original audio or model weights fetched."""
import unittest
import numpy as np
from s01e01_anonymous_voice_similarity import cosines,source_segments,MIN_LENGTH_MS

class VoiceSimilarityTests(unittest.TestCase):
    def test_bounded_original_source_segments(self):
        segments=source_segments()
        self.assertEqual(len(segments),10)
        self.assertEqual([x["index"] for x in segments],list(range(10)))
        self.assertGreater(MIN_LENGTH_MS,600)
        self.assertTrue(all(60000<=x["start_ms"]<x["end_ms"]<=90000 for x in segments))
    def test_anonymous_pairwise_no_identity_or_clusters(self):
        sims=cosines({0:[1,0,0],1:[.6,.8,0],2:[0,0,1]})
        self.assertEqual(len(sims),3)
        pair=next(x for x in sims if x["asr_segment_a"]==0 and x["asr_segment_b"]==1)
        self.assertAlmostEqual(pair["anonymous_cosine_similarity_unreviewed"],.6)
        self.assertIsNone(pair["same_speaker_conclusion"])
        self.assertFalse(pair["model_probability_calibrated"])
        self.assertEqual(cosines({0:[1,2,3]}),[])
    def test_bad_vectors_rejected(self):
        for x in [{0:[0,0,0]},{0:[float("nan"),1,0]},
                  {0:[1,0],1:[1,0,0]}, {-1:[1,2]}]:
            with self.subTest(x=x):
                with self.assertRaises(ValueError):cosines(x)

if __name__=="__main__":unittest.main()
