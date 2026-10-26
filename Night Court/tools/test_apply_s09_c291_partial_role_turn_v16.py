#!/usr/bin/env python3
"""S09 C291 partial-provisional Alex with original-source UNKNOWN interruption."""
import copy
import hashlib
import unittest
from apply_s09_c291_partial_role_turn_v16 import (
    SHA,SOURCE_REF,SOURCE_TEXT,ALEX,PRIOR_STATUS,PROPOSED_STATUS,transform
)

def fixture():
    return [
      {"episode_id":"S09E19","source_reading_ref":"C290.1",
       "original_source_part_refs":["C290.1"],"original_source_sha256":SHA,
       "caption_text":"He. Was she?","candidate_role":None,
       "role_attribution_status":"unidentified","original_source_untimed":True,
       "source_original_times_ms":None,
       "speaker_turn_boundary_verified":False,
       "actor_face_or_voice_independently_verified":False},
      {"episode_id":"S09E19","source_reading_ref":SOURCE_REF,
       "original_source_part_refs":[SOURCE_REF],"original_source_sha256":SHA,
       "caption_text":SOURCE_TEXT,"candidate_role":ALEX,
       "role_attribution_status":PRIOR_STATUS,"original_source_untimed":True,
       "source_original_times_ms":None,
       "speaker_turn_boundary_verified":False,
       "actor_face_or_voice_independently_verified":False},
      {"episode_id":"S09E19","source_reading_ref":"C292.1",
       "original_source_part_refs":["C292.1"],"original_source_sha256":SHA,
       "caption_text":"Was she you?","candidate_role":ALEX,
       "role_attribution_status":PRIOR_STATUS,"original_source_untimed":True,
       "source_original_times_ms":None,
       "speaker_turn_boundary_verified":False,
       "actor_face_or_voice_independently_verified":False},
    ]

class C291RoleAwareTurnTests(unittest.TestCase):
    def test_one_pronoun_cue_two_roles_but_no_false_fully_named_source_part(self):
        original=fixture()
        updated,m=transform(original,strict=False)
        self.assertEqual(len(updated),4)
        self.assertEqual(m["original_caption_source_units"],3)
        self.assertEqual(m["provisional_named_original_caption_units"],1)
        self.assertEqual(m["unknown_original_source_units"],2)
        self.assertEqual(m["new_original_AV_certified_voice_or_actor_turns"],0)
        self.assertEqual(updated[0],original[0])
        self.assertEqual(updated[-1],original[-1])
        first,second=updated[1:3]
        self.assertIsNone(first["candidate_role"])
        self.assertEqual(first["role_attribution_status"],"unidentified")
        self.assertEqual(second["candidate_role"],ALEX)
        self.assertEqual(second["role_attribution_status"],PROPOSED_STATUS)
        self.assertFalse(first["speaker_turn_boundary_verified"])
        self.assertFalse(second["actor_face_or_voice_independently_verified"])
        self.assertIsNone(first["source_original_times_ms"])
        self.assertIsNone(second["source_original_times_ms"])
        self.assertEqual(first["original_source_part_refs"],[SOURCE_REF])
        self.assertEqual(second["original_source_part_refs"],[SOURCE_REF])
        self.assertEqual(first["caption_text"]+second["caption_text"],SOURCE_TEXT)
        for part in (first,second):
            span=part["source_exact_character_span"]
            text=SOURCE_TEXT[span["start_char"]:span["end_char"]]
            self.assertEqual(hashlib.sha256(text.encode()).hexdigest(),
                             span["original_source_substring_sha256"])
        self.assertEqual(original[1]["candidate_role"],ALEX)

    def test_source_exact_context_or_performance_proof_drift_refuses_split(self):
        base=fixture()
        for idx,field,value in [
          (1,"candidate_role",None),
          (1,"role_attribution_status","original_audio_verified"),
          (1,"original_source_sha256","0"*64),
          (1,"caption_text","Edited pronunciation"),
          (1,"source_original_times_ms",[{"start_ms":1,"end_ms":4}]),
          (1,"actor_face_or_voice_independently_verified",True),
          (1,"speaker_turn_boundary_verified",True)
        ]:
            bad=copy.deepcopy(base)
            bad[idx][field]=value
            with self.assertRaisesRegex(ValueError,"cannot be safely partially inherited"):
                transform(bad,strict=False)

if __name__=="__main__":
    unittest.main()
