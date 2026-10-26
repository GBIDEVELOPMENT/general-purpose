#!/usr/bin/env python3
"""Offline source-conservation and provisional P0 dialogue-continuation tests."""
import copy
import unittest
from build_s09_source_turns_v10 import (
    SHA,EXPECTED_FIRST,EXPECTED_SECOND,STATUS,merge_v9
)

def fixture():
    out=[]
    for i,(ref,role,text,status) in enumerate([
        ("C265.1",None,"As usual.","unidentified"),
        ("C266.1",None,EXPECTED_FIRST,"unidentified"),
        ("C267.1","ROZ RUSSELL",EXPECTED_SECOND,
         "original_soundtrack_acoustic_context_proposal_not_independent_avi_id"),
        ("C268.1",None,"Yeah. I bought stock in Earthshoes.","unidentified")
    ]):
        r={
          "schema":"night-court-private-character-dialogue-evidence/1",
          "episode_id":"S09E19","source_reading_ref":ref,
          "original_source_part_refs":[ref],
          "reading_block_id":f"S09E19:reading:{i:04d}",
          "original_source_sha256":SHA,
          "caption_text":text,"candidate_role":role,
          "role_attribution_status":status,
          "source_original_times_ms":None,
          "original_source_untimed":True,
          "speaker_turn_boundary_verified":False,
          "actor_face_or_voice_independently_verified":False
        }
        if ref=="C267.1":
            r["speaker_identity_provisional_from_model_and_context"]=True
            r["source_acoustic_numeric_report_sha256"]="x"*64
        out.append(r)
    return out

class ProvisionalTurnJoinTests(unittest.TestCase):
    def test_join_full_original_words_onto_one_speaker_without_certification(self):
        original=fixture()
        after,manifest=merge_v9(original,strict=False)
        self.assertEqual(len(original),4)
        self.assertEqual(len(after),3)
        self.assertEqual(manifest["original_caption_immutable_source_units"],4)
        self.assertEqual(manifest["current_provisional_character_named_original_units"],2)
        self.assertEqual(manifest["still_unknown_original_source_units"],2)
        self.assertEqual(manifest["source_audio_human_actor_identity_confirmations_added"],0)
        self.assertEqual(after[1]["source_reading_ref"],"C266.1–C267.1")
        self.assertEqual(after[1]["original_source_part_refs"],["C266.1","C267.1"])
        self.assertEqual(after[1]["caption_text"],EXPECTED_FIRST+" "+EXPECTED_SECOND)
        self.assertEqual(after[1]["candidate_role"],"ROZ RUSSELL")
        self.assertEqual(after[1]["role_attribution_status"],STATUS)
        self.assertFalse(after[1]["independent_filmed_performance_turn_proven"])
        self.assertFalse(after[1]["speaker_turn_boundary_verified"])
        self.assertIsNone(after[1]["source_original_times_ms"])
        self.assertEqual(after[0],original[0])
        self.assertEqual(after[-1],original[-1])
        self.assertIsNone(original[1]["candidate_role"])

    def test_split_episode_or_different_source_blocks_fail(self):
        old=fixture()
        old[2]["episode_id"]="S01E01"
        with self.assertRaisesRegex(ValueError,"not found"):
            merge_v9(old,strict=False)
        old=fixture()
        old[2]["original_source_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"no longer source-consistent"):
            merge_v9(old,strict=False)
        old=fixture()
        old[1]["source_original_times_ms"]=[{"start_ms":100,"end_ms":400}]
        with self.assertRaisesRegex(ValueError,"no longer source-consistent"):
            merge_v9(old,strict=False)

    def test_cannot_overwrite_already_named_actor_or_conflicting_model(self):
        old=fixture()
        old[1]["candidate_role"]="HARRY STONE"
        with self.assertRaisesRegex(ValueError,"no longer source-consistent"):
            merge_v9(old,strict=False)
        old=fixture()
        old[2]["candidate_role"]="DAN FIELDING"
        with self.assertRaisesRegex(ValueError,"no longer source-consistent"):
            merge_v9(old,strict=False)
        old=fixture()
        old[2]["actor_face_or_voice_independently_verified"]=True
        with self.assertRaisesRegex(ValueError,"no longer source-consistent"):
            merge_v9(old,strict=False)

if __name__=="__main__":
    unittest.main()
