#!/usr/bin/env python3
"""No TV media. Test real signal features on a generated synthetic tone."""
import math, unittest
import numpy as np
from s01e01_utterance_prosody import features, load_source

class Features(unittest.TestCase):
    def test_original_ASR_source_provenance(self):
        obj,mapping=load_source()
        self.assertEqual(len(obj["asr_segments"]),10)
        self.assertEqual(len(mapping),10)
        self.assertEqual(mapping[4],22)
    def test_synthetic_pitch(self):
        sr=16000
        t=np.arange(sr*2,dtype=np.float64)/sr
        signal=(0.08*np.sin(2*np.pi*190*t)).astype(np.float32)
        f=features(signal,sr)
        self.assertTrue(165<f["mix_pitch_median_hz"]<215,f)
        self.assertGreater(f["mix_pitch_frames_passing_energy_gate"],30)
        self.assertIsNotNone(f["mix_pitch_first_to_last_change_semitones"])
        self.assertTrue(-30<f["rms_dbfs"]<-15)
        self.assertIn("unreviewed",f["pitch_reliability"])
    def test_short_segment_abstains_from_stable_delivery(self):
        sr=16000
        t=np.arange(8000)/sr
        f=features((.08*np.sin(2*np.pi*160*t)).astype(np.float32),sr)
        self.assertIn("too_short",f["pitch_reliability"])
    def test_bad_durations(self):
        with self.assertRaises(ValueError):features(np.zeros(800,dtype=np.float32),16000)
        with self.assertRaises(ValueError):features(np.zeros(16000*6,dtype=np.float32),16000)

if __name__=="__main__":unittest.main()
