#!/usr/bin/env python3
"""Synthetic original soundtrack numeric evidence validation and role overlay."""
import copy
import unittest
from build_original_audio_speaker_reader_v8 import (
    SCHEMA, INPUT_ROLE_SCHEMA, REPORT_SHA, apply, validated_source_ledger
)

SRC="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
ROLES={
    "C074.1":"DAN FIELDING","C095.1":"DAN FIELDING",
    "C097.1":"HARRY STONE","C161.1":"HARRY STONE",
    "C172.1":"HARRY STONE","C179.1":"LANA WAGNER"
}
PREVIOUS={"C097.1":"HARRY STONE","C172.1":"HARRY STONE"}


def fixture():
    ledger={
        "schema":"night-court-actual-s01-source-voice-embedding-proposals/1",
        "original_caption_sha256":SRC,
        "original_movie_sha256":"5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962",
        "full_original_numeric_report_sha256":REPORT_SHA,
        "source_original_unknown_audio_samples_compared":42,
        "voice_model_role_suggestions_that_passed_threshold":6,
        "voice_model_abstentions":36,
        "model":"resemblyzer-0.1.4",
        "cannot_automatically_confirm_actor_id":True,
        "crossvalidation":{
            "held_out_samples":75,
            "correct_predicted_provisional_roles":56,
            "independent_human_actor_identity_acceptances":0
        },
        "proposals":[{
            "source_ref":ref,"voice_model_proposed_role":role,
            "cosine_similarity":.8,"next_best_margin":.11,
            "original_soundtrack_was_processed":True,
            "actor_id_independently_verified":False
        } for ref,role in ROLES.items()]
    }
    rows=[{
        "schema":INPUT_ROLE_SCHEMA,"episode_id":"S01E01",
        "source_reading_ref":ref,"original_source_part_refs":[ref],
        "original_source_sha256":SRC,
        "role_attribution_status":(
            "narrative_context_candidate_not_voice_verified" if ref in PREVIOUS
            else "unidentified"
        ),
        "candidate_role":PREVIOUS.get(ref),
        "reading_block_id":"S01E01:"+ref,
        "speaker_turn_boundary_verified":False,
        "actor_face_or_voice_independently_verified":False
    } for ref in ROLES]
    return ledger,rows


class RealAudioProposalTests(unittest.TestCase):
    def test_four_new_proposals_two_corroborations_zero_certifications(self):
        ledger,rows=fixture()
        updated,summ=apply(rows,ledger,SRC,require_full=False)
        self.assertEqual(len(updated),6)
        self.assertEqual(summ["new_original_audio_model_supported_provisional_role_units"],4)
        self.assertEqual(summ["provisional_previous_speaker_roles_corrob_by_acoustics"],2)
        self.assertEqual(summ["source_speaker_identities_human_verified_by_pass"],0)
        self.assertEqual(summ["source_units_with_provisional_names"],6)
        self.assertTrue(all(x["candidate_role"] for x in updated))
        self.assertTrue(all(not x["original_soundtrack_human_speaker_identity_verified"] for x in updated))
        self.assertIsNone(rows[0]["candidate_role"])

    def test_source_avi_and_seed_count_claim_fail_closed(self):
        ledger,rows=fixture()
        wrong=copy.deepcopy(ledger)
        wrong["original_movie_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"original soundtrack provenance"):
            apply(rows,wrong,SRC,require_full=False)
        wrong=copy.deepcopy(ledger)
        wrong["crossvalidation"]["correct_predicted_provisional_roles"]=75
        with self.assertRaises(ValueError):
            apply(rows,wrong,SRC,require_full=False)

    def test_cannot_replace_previously_named_role_or_invent_audio_certainty(self):
        ledger,rows=fixture()
        rows[0]["candidate_role"]="LANA WAGNER"
        with self.assertRaisesRegex(ValueError,"unsupported role overwrite"):
            apply(rows,ledger,SRC,require_full=False)
        ledger,rows=fixture()
        ledger["proposals"][0]["actor_id_independently_verified"]=True
        with self.assertRaisesRegex(ValueError,"Unsafe unverified"):
            apply(rows,ledger,SRC,require_full=False)

    def test_original_cue_id_cannot_duplicate_or_reach_other_episode(self):
        ledger,rows=fixture()
        wrong=copy.deepcopy(ledger)
        wrong["proposals"][1]["source_ref"]=wrong["proposals"][0]["source_ref"]
        with self.assertRaisesRegex(ValueError,"Unsafe unverified"):
            validated_source_ledger(wrong,SRC)
        other=copy.deepcopy(rows)
        other[0]["episode_id"]="S09E19"
        with self.assertRaisesRegex(ValueError,"missing or ambiguous"):
            apply(other,ledger,SRC,require_full=False)


if __name__=="__main__":
    unittest.main()
