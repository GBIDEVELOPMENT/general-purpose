#!/usr/bin/env python3
"""Adversarial original video visual observation metadata integrity tests."""
import copy
import json
import unittest
from validate_s01e01_expanded_frame_evidence import validate, PKT

class ExpandedS01SceneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=json.loads(PKT.read_text("utf-8"))

    def test_real_source_145_frame_observation_provenance(self):
        r=validate()
        self.assertEqual(r["source_frame_observations"],6)
        self.assertTrue(r["source_sha_consistent"])
        self.assertEqual(r["independent_continuous_av_acceptances"],0)
        self.assertFalse(r["source_video_audio_or_image_bytes_stored"])

    def test_wrong_original_video_fingerprint_rejected(self):
        d=copy.deepcopy(self.packet)
        d["source_original_video_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"source provenance mismatch"):
            validate(d)

    def test_fabricated_frame_hash_and_out_of_scope_time_rejected(self):
        d=copy.deepcopy(self.packet)
        d["observations"][0]["frame_evidence"][0]["sha256"]="not a real SHA"
        with self.assertRaisesRegex(ValueError,"frame index/hash/time"):
            validate(d)
        d=copy.deepcopy(self.packet)
        d["observations"][0]["frame_evidence"][0]["nominal_video_time_ms"]=900000
        with self.assertRaisesRegex(ValueError,"frame index/hash/time"):
            validate(d)

    def test_sampled_images_cannot_accept_speaker_or_continuous_action(self):
        for key in ("speaker_identity_verified","continuous_original_video_reviewed",
                    "exact_action_onset_verified","source_subtitle_synchronization_verified"):
            with self.subTest(key=key):
                d=copy.deepcopy(self.packet)
                d["observations"][0][key]=True
                with self.assertRaisesRegex(ValueError,"cannot certify"):
                    validate(d)

    def test_missing_visual_entry_or_contact_sheet_rejected(self):
        d=copy.deepcopy(self.packet)
        d["observations"].pop()
        with self.assertRaisesRegex(ValueError,"Expected six"):
            validate(d)
        d=copy.deepcopy(self.packet)
        d["contact_sheets"].pop()
        with self.assertRaisesRegex(ValueError,"contact sheet"):
            validate(d)

if __name__=="__main__":
    unittest.main()
