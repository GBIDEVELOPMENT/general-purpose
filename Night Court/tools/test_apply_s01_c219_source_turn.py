#!/usr/bin/env python3
"""No invented source-actor identity, timestamp or dialogue in S01 C219 P0."""
import copy
import hashlib
import unittest

from apply_s01_c219_source_turn import (
    SOURCE_SHA,SOURCE_REF,EXPECTED_START,EXPECTED_END,split
)

ORIGINAL="...must have been a living hell, huh?\n- Yeah."

def fixture():
    return [
      {"episode_id":"S01E01","source_reading_ref":"C218.1",
       "original_source_part_refs":["C218.1"],"original_source_sha256":SOURCE_SHA,
       "caption_text":"- Yes, sir.\n- Twenty-seven years. Jeez...",
       "candidate_role":"HARRY STONE","role_attribution_status":"provisional",
       "actor_face_or_voice_independently_verified":False,
       "speaker_turn_boundary_verified":False},
      {"episode_id":"S01E01","source_reading_ref":SOURCE_REF,
       "original_source_part_refs":[SOURCE_REF],"original_source_sha256":SOURCE_SHA,
       "caption_text":ORIGINAL,"candidate_role":None,"role_attribution_status":"unidentified",
       "actor_face_or_voice_independently_verified":False,
       "speaker_turn_boundary_verified":False,
       "source_original_times_ms":{"start_ms":EXPECTED_START,"end_ms":EXPECTED_END}},
      {"episode_id":"S01E01","source_reading_ref":"C220.1",
       "original_source_part_refs":["C220.1"],"original_source_sha256":SOURCE_SHA,
       "caption_text":"Well, there were some okay times.","candidate_role":"UNIDENTIFIED",
       "role_attribution_status":"provisional",
       "actor_face_or_voice_independently_verified":False,
       "speaker_turn_boundary_verified":False}
    ]

class OriginalS01C219Tests(unittest.TestCase):
    def test_dashed_reply_is_a_reversible_proposed_turn_not_an_actor_id(self):
        old=fixture()
        result,report=split(old,ORIGINAL,strict=False)
        self.assertEqual(len(result),4)
        self.assertEqual(report["original_caption_source_units"],3)
        self.assertEqual(report["current_provisional_speaking_blocks"],4)
        self.assertEqual(report["original_source_cue_start_ms"],879532)
        self.assertEqual(report["original_source_cue_end_ms"],882330)
        self.assertEqual(report["new_original_actor_identities_certified"],0)
        self.assertTrue(report["source_cue_timing_is_not_performer_turn_timing"])
        self.assertEqual(result[0],old[0])
        self.assertEqual(result[-1],old[-1])
        a,b=result[1:3]
        self.assertIsNone(a["candidate_role"])
        self.assertIsNone(b["candidate_role"])
        self.assertFalse(a["speaker_turn_boundary_verified"])
        self.assertFalse(b["actor_face_or_voice_independently_verified"])
        self.assertEqual(a["original_source_part_refs"],[SOURCE_REF])
        self.assertEqual(b["original_source_part_refs"],[SOURCE_REF])
        self.assertEqual(a["source_original_times_ms"],old[1]["source_original_times_ms"])
        self.assertEqual(b["source_original_times_ms"],old[1]["source_original_times_ms"])
        self.assertEqual(a["caption_text"]+b["caption_text"],ORIGINAL)
        for part in (a,b):
            x=part["source_exact_character_span"]
            self.assertEqual(hashlib.sha256(ORIGINAL[x["start_char"]:x["end_char"]].encode()).hexdigest(),
                             x["exact_text_sha256"])
        self.assertIsNone(old[1]["candidate_role"])

    def test_false_speaker_existing_name_or_srt_changes_fail_closed(self):
        old=fixture()
        changed=copy.deepcopy(old)
        changed[1]["candidate_role"]="HARRY STONE"
        with self.assertRaisesRegex(ValueError,"prior speaker identity"):
            split(changed,ORIGINAL,strict=False)
        changed=copy.deepcopy(old)
        changed[1]["caption_text"]="A different line entirely."
        with self.assertRaisesRegex(ValueError,"prior speaker identity"):
            split(changed,ORIGINAL,strict=False)
        changed=copy.deepcopy(old)
        changed[1]["actor_face_or_voice_independently_verified"]=True
        with self.assertRaisesRegex(ValueError,"prior speaker identity"):
            split(changed,ORIGINAL,strict=False)
        with self.assertRaisesRegex(ValueError,"prior speaker identity"):
            split(old,ORIGINAL.replace("- Yeah.","- Maybe."),strict=False)

if __name__=="__main__":
    unittest.main()
