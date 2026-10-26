#!/usr/bin/env python3
"""Offline no-media controls for source-preserving contextual speaker hypotheses."""
import copy
import unittest
from build_contextual_speaker_reader_v7 import (
    SCHEMA, RECORD_SCHEMA, apply_candidates,
)


def fixtures():
    shas = {"S01E01":"a"*64, "S09E19":"b"*64}
    cast = {"episodes":{
        "S01E01":{"people":[{"character":"HARRY STONE"},{"character":"LANA WAGNER"}]},
        "S09E19":{"people":[{"character":"ROZ RUSSELL"},{"character":"CHRISTINE SULLIVAN"}]}
    }}
    rows=[
        {"episode_id":"S01E01","source_reading_ref":"C002.1",
         "original_source_part_refs":["C002.1"],"reading_block_id":"s01:1",
         "candidate_role":None,"role_attribution_status":"unidentified",
         "caption_text":"No idea.","speaker_turn_boundary_verified":False},
        {"episode_id":"S09E19","source_reading_ref":"C070.1–C071.1",
         "original_source_part_refs":["C070.1","C071.1"],"reading_block_id":"s09:1",
         "candidate_role":None,"role_attribution_status":"unidentified",
         "caption_text":"Well, not that time.","speaker_turn_boundary_verified":False},
        {"episode_id":"S09E19","source_reading_ref":"C034.1",
         "original_source_part_refs":["C034.1"],"reading_block_id":"s09:2:p1",
         "candidate_role":"ROZ RUSSELL","role_attribution_status":"external_or_context_editorial_proposal",
         "caption_text":"me.","speaker_turn_boundary_verified":False},
        {"episode_id":"S09E19","source_reading_ref":"C034.1",
         "original_source_part_refs":["C034.1"],"reading_block_id":"s09:2:p2",
         "candidate_role":"CHRISTINE SULLIVAN","role_attribution_status":"external_or_context_editorial_proposal",
         "caption_text":"Wow.","speaker_turn_boundary_verified":False},
    ]
    seed = {"schema":SCHEMA,"source_witnesses":shas,"proposals":[
        {"episode_id":"S01E01","source_ref":"C002.1",
         "proposed_role":"HARRY STONE","evidence_tier":"narrative_context_proposal",
         "original_audio_reviewed":False,"character_verified":False},
        {"episode_id":"S09E19","source_ref":"C070.1–C071.1",
         "proposed_role":"CHRISTINE SULLIVAN","evidence_tier":"narrative_context_proposal",
         "original_audio_reviewed":False,"character_verified":False}
    ]}
    return shas,cast,rows,seed


class ContextualSpeakerProposalTests(unittest.TestCase):
    def test_context_names_only_previously_unknown_original_units(self):
        shas,cast,rows,seed=fixtures()
        updated,report=apply_candidates(rows,seed,cast,shas,strict=False)
        self.assertEqual(report["new_contextual_source_units_proposed"],3)
        self.assertEqual(report["source_units_total"],4)
        self.assertEqual(report["source_units_provisionally_named"],4)
        self.assertEqual(report["source_units_unknown"],0)
        self.assertEqual(report["audio_confirmed_by_this_pass"],0)
        self.assertEqual(updated[0]["candidate_role"],"HARRY STONE")
        self.assertEqual(updated[1]["candidate_role"],"CHRISTINE SULLIVAN")
        self.assertFalse(updated[1]["actor_face_or_voice_independently_verified"])
        self.assertIsNone(rows[0]["candidate_role"])

    def test_cannot_replace_named_role_or_split_cue(self):
        shas,cast,rows,seed=fixtures()
        broken=copy.deepcopy(seed)
        broken["proposals"][0]["source_ref"]="C034.1"
        broken["proposals"][0]["episode_id"]="S09E19"
        broken["proposals"][0]["proposed_role"]="ROZ RUSSELL"
        with self.assertRaisesRegex(ValueError,"Ambiguous original source block"):
            apply_candidates(rows,broken,cast,shas,strict=False)

    def test_no_false_audio_acceptance_or_invented_cast_member(self):
        shas,cast,rows,seed=fixtures()
        tampered=copy.deepcopy(seed)
        tampered["proposals"][0]["original_audio_reviewed"]=True
        with self.assertRaisesRegex(ValueError,"False AV certainty"):
            apply_candidates(rows,tampered,cast,shas,strict=False)
        tampered=copy.deepcopy(seed)
        tampered["proposals"][0]["proposed_role"]="FAKE ACTOR"
        with self.assertRaisesRegex(ValueError,"unlisted named character"):
            apply_candidates(rows,tampered,cast,shas,strict=False)

    def test_wrong_edition_or_duplicate_fails(self):
        shas,cast,rows,seed=fixtures()
        tampered=copy.deepcopy(seed)
        tampered["source_witnesses"]["S09E19"]="z"*64
        with self.assertRaisesRegex(ValueError,"different original source"):
            apply_candidates(rows,tampered,cast,shas,strict=False)
        tampered=copy.deepcopy(seed)
        tampered["proposals"].append(copy.deepcopy(tampered["proposals"][0]))
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            apply_candidates(rows,tampered,cast,shas,strict=False)


if __name__=="__main__":
    unittest.main()
