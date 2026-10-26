#!/usr/bin/env python3
"""Regression for original S09 acoustic proposals with disputed character abstention."""
import copy
import unittest
from build_s09_source_acoustic_speaker_reader_v9 import (
    LEDGER_SCHEMA,ORIGINAL_SHA,FILM_SHA,PCM_SHA,MODEL_NUMERIC_SHA,
    ALIGNMENT_SHA, NEW_STATUS,merge
)

NAMES={
  "C046.1":("CHRISTINE SULLIVAN","provisional_speaker_working_reader_only"),
  "C057.1":("CHRISTINE SULLIVAN","provisional_speaker_working_reader_only"),
  "C129.1":("CHRISTINE SULLIVAN","quarantine_plausible_out_of_bank_speaker"),
  "C267.1":("ROZ RUSSELL","provisional_speaker_working_reader_only")
}
def fixture():
    evidence={
      "schema":LEDGER_SCHEMA,"episode_id":"S09E19",
      "original_video_sha256":FILM_SHA,"original_caption_sha256":ORIGINAL_SHA,
      "original_pcm_sha256":PCM_SHA,"full_numeric_original_voice_report_sha256":MODEL_NUMERIC_SHA,
      "source_asr_paragraph_alignment_report_sha256":ALIGNMENT_SHA,
      "model":"resemblyzer-0.1.4",
      "role_holdout_correct":18,"role_holdout_total":26,
      "source_unknown_original_paragraphs_compared":28,
      "acoustic_similarity_threshold_proposals":4,
      "working_character_proposals_to_add":3,
      "quarantined_speaker_suspicions":1,
      "source_soundtrack_human_actor_voice_identifications_accepted":0,
      "original_untimed_cue_timestamps_introduced":0,
      "known_reference_roles_count":{
          "CHRISTINE SULLIVAN":10,"DAN FIELDING":5,
          "MAC ROBINSON":4,"ROZ RUSSELL":7
      },
      "candidates":[{
        "source_ref":ref,"proposed_role":role,"disposition":status,
        "similarity":.81,"margin":.14,
        "reason":"Acoustically plausible but original actor identification unreviewed, source context needs audit."
      } for ref,(role,status) in NAMES.items()]
    }
    rows=[{
        "episode_id":"S09E19","source_reading_ref":ref,
        "original_source_part_refs":[ref],
        "original_source_sha256":ORIGINAL_SHA,
        "original_source_untimed":True,
        "source_original_times_ms":None,
        "candidate_role":None,"role_attribution_status":"unidentified",
        "actor_face_or_voice_independently_verified":False,
        "speaker_turn_boundary_verified":False,
        "caption_text":"Source private dialogue stays in test fixture."
    } for ref in NAMES]
    return rows,evidence

class S09AcousticOverlayTests(unittest.TestCase):
    def test_three_proposed_names_one_disputed_continues_unknown(self):
        original,voice=fixture()
        final,report=merge(original,voice,strict=False)
        self.assertEqual(report["current_working_named_provisional_original_units"],3)
        self.assertEqual(report["unidentified_original_cue_units"],1)
        self.assertEqual(report["original_audio_human_identified_characters_added"],0)
        byref={x["source_reading_ref"]:x for x in final}
        self.assertEqual(byref["C057.1"]["candidate_role"],"CHRISTINE SULLIVAN")
        self.assertEqual(byref["C057.1"]["role_attribution_status"],NEW_STATUS)
        self.assertIsNone(byref["C129.1"]["candidate_role"])
        self.assertEqual(byref["C129.1"]["quarantined_acoustic_alternative_only"],"CHRISTINE SULLIVAN")
        self.assertTrue(all(x["original_soundtrack_human_role_reviewed"] is False for x in final))
        self.assertTrue(all(x["source_original_times_ms"] is None for x in final))
        self.assertTrue(all(r["candidate_role"] is None for r in original))

    def test_model_out_of_reference_set_cannot_be_promoted(self):
        original,voice=fixture()
        bad=copy.deepcopy(voice)
        bad["candidates"][2]["disposition"]="provisional_speaker_working_reader_only"
        with self.assertRaisesRegex(ValueError,"out-of-bank"):
            merge(original,bad,strict=False)

    def test_source_fingerprint_and_absent_character_proof_required(self):
        original,voice=fixture()
        bad=copy.deepcopy(voice)
        bad["role_holdout_correct"]=26
        with self.assertRaisesRegex(ValueError,"numeric actor-role"):
            merge(original,bad,strict=False)
        bad=copy.deepcopy(original)
        bad[0]["source_original_times_ms"]=[{"start_ms":0,"end_ms":1500}]
        with self.assertRaisesRegex(ValueError,"wrongly timed"):
            merge(bad,voice,strict=False)

    def test_no_existing_role_replaced_by_model_guess(self):
        original,voice=fixture()
        original[0]["candidate_role"]="DAN FIELDING"
        with self.assertRaisesRegex(ValueError,"no longer UNKNOWN"):
            merge(original,voice,strict=False)


if __name__=="__main__":
    unittest.main()
