#!/usr/bin/env python3
"""Synthetic safety/quality gates for original-video voice matching."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from compare_original_speaker_embeddings import (
    SCHEMA, VIDEO_SHA, centroid, cosine, infer, holdout, source_plan
)


class SpeakerEmbeddingTests(unittest.TestCase):
    def test_duplicate_and_silence_voice_embeddings_are_not_accepted(self):
        self.assertAlmostEqual(cosine([1,0],[1,0]),1.)
        self.assertAlmostEqual(cosine([1,0],[0,1]),0.)
        with self.assertRaises(ValueError):
            centroid([[1,0],[0,0,0]])
        with self.assertRaises(ValueError):
            cosine([0,0],[0,0])

    def test_explicit_threshold_and_competitor_margin_abstention(self):
        refs={"HARRY STONE":[1.,0.,0.],
              "DAN FIELDING":[0.,1.,0.],
              "LANA WAGNER":[0.,0.,1.]}
        guess=infer([.95,.1,0],refs)
        self.assertEqual(guess["role"],"HARRY STONE")
        self.assertEqual(guess["status"],"candidate_passed_uncalibrated_threshold")
        self.assertTrue(guess["thresholds_not_calibrated_to_original_episode"])
        ambiguous=infer([.8,.8,.01],refs)
        self.assertIsNone(ambiguous["role"])
        self.assertEqual(ambiguous["status"],"ambiguous_or_low_similarity_abstain")
        unknown=infer([.4,.4,.4],refs,minimum=.9)
        self.assertIsNone(unknown["role"])
        with self.assertRaises(ValueError):
            infer([1.,0.,0.],refs,minimum=1.2)

    def test_evaluate_provisional_known_voices_before_any_unknowns(self):
        rows={
            "HARRY STONE":[("C001.1",[1.,.01]),("C002.1",[1.,.02]),
                           ("C003.1",[.99,.01]),("C004.1",[.98,.02])],
            "DAN FIELDING":[("C010.1",[.01,1.]),("C011.1",[.02,1.]),
                            ("C012.1",[.01,.99]),("C013.1",[.02,.98])]
        }
        report=holdout(rows)
        self.assertEqual(report["evaluated_provisional_known_voice_samples"],8)
        self.assertEqual(report["correctly_recovered_held_out_provisional_roles"],8)
        self.assertEqual(report["raw_leave_one_out_role_accuracy"],1.)
        self.assertFalse(report["source_av_voice_confirmation_completed"])

    def test_source_plan_skips_multivoice_captions_and_untimed(self):
        rows=[]
        cues=[]
        for i in range(1,35):
            role="HARRY STONE" if i<=12 else ("DAN FIELDING" if i<=24 else None)
            refs=[f"C{i:03d}.1"]
            rows.append({"episode_id":"S01E01","source_reading_ref":refs[0],
                "original_source_part_refs":refs,"candidate_role":role,
                "role_attribution_status":"unidentified" if role is None else
                    "provisional_not_original_audio_verified"})
            cues.append({"cue":i,"start_ms":i*4000,"end_ms":i*4000+2300})
        cue_parts=rows[24]["original_source_part_refs"]
        rows.append({"episode_id":"S01E01","source_reading_ref":"C025.2",
           "original_source_part_refs":["C025.2"],"candidate_role":None,
           "role_attribution_status":"unidentified"})
        with patch("compare_original_speaker_embeddings.load_witness",
                   return_value=({"sha256":"aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496",
                                  "timecoded":True},cues)),\
             patch("compare_original_speaker_embeddings.records_for_episode",
                   return_value=rows):
            plan=source_plan(Path(tempfile.gettempdir()))
        self.assertEqual(plan["schema"],SCHEMA)
        self.assertEqual(plan["original_movie_sha256_required"],VIDEO_SHA)
        self.assertEqual(len(plan["reference_cues"]),2)
        self.assertEqual(plan["source_unidentified_candidates_timeable"],9)
        self.assertGreater(plan["skipped_multi_speaker_or_untimed_source_blocks"],0)


if __name__=="__main__":
    unittest.main()
