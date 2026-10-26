#!/usr/bin/env python3
"""Synthetic role, exact-text P0, abstention and S09 untimed regression for v16."""
from __future__ import annotations
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from apply_manual_context_pilot_review_v16 import (
    LEDGER,STATUS,apply,counts,validate_ledger,sha,
)

SNACK="And the snacks are free. Yeah, but they're not fresh."

def fixture():
    ledger=json.loads(LEDGER.read_text("utf-8"))
    rows=[]
    for idx,p in enumerate(ledger["role_amendments"]):
        ep=p["episode_id"]
        rows.append({
            "episode_id":ep,"source_reading_ref":p["source_reading_ref"],
            "reading_block_id":f"{ep}:test:{idx}",
            "original_source_part_refs":p["original_source_part_refs"],
            "original_source_sha256":p["source_witness_sha256"],
            "caption_text":"Synthetic context "+p["source_text_must_contain"],
            "candidate_role":p["prior_role"],
            "role_attribution_status":"unidentified" if p["prior_role"] is None else "provisional",
            "source_original_times_ms":None,"original_source_untimed":ep=="S09E19",
            "speaker_turn_boundary_verified":False,
            "actor_face_or_voice_independently_verified":False,
        })
    # Current split source cue C219 is one original unit with TWO voice parts,
    # as is already split original S09 C206. The newly named half alone must not
    # cause those whole original units to count as completely named.
    for ep,ref,reading in [
        ("S01E01","C219.1","S01E01-C219-SOURCE-TURN-2"),
        ("S09E19","C206.1","S09-S09E19-C206-UNVERIFIED-TWO-VOICE-BOUNDARY-T01"),
    ]:
        rows.append({
            "episode_id":ep,"source_reading_ref":reading,
            "reading_block_id":f"{ep}:test:other:{ref}",
            "original_source_part_refs":[ref],
            "original_source_sha256":ledger["original_source_shas"][ep],
            "caption_text":"Synthetic unassigned remaining voice",
            "candidate_role":None,"role_attribution_status":"unidentified",
            "source_original_times_ms":None,"original_source_untimed":ep=="S09E19",
            "speaker_turn_boundary_verified":False,
            "actor_face_or_voice_independently_verified":False,
        })
    rows.append({
        "episode_id":"S09E19","source_reading_ref":"C277.1",
        "reading_block_id":"S09E19:test:original277",
        "original_source_part_refs":["C277.1"],
        "original_source_sha256":ledger["original_source_shas"]["S09E19"],
        "caption_text":SNACK,"candidate_role":None,
        "role_attribution_status":"unidentified",
        "source_original_times_ms":None,"original_source_untimed":True,
        "speaker_turn_boundary_verified":False,
        "actor_face_or_voice_independently_verified":False,
    })
    return rows,ledger

class ManualContextPilotV16Tests(unittest.TestCase):
    def test_apply_all_manual_candidates_with_two_partial_unknown_source_units(self):
        rows,ledger=fixture()
        original=copy.deepcopy(rows)
        updated,report=apply(rows,ledger,strict=False)
        self.assertEqual(report["new_contextual_role_assignments_in_reader_blocks"],32)
        self.assertEqual(report["corrected_previously_named_reader_blocks"],2)
        self.assertEqual(report["new_contextually_named_complete_source_units"],30)
        self.assertEqual(report["role_changes_in_reading_blocks"],34)
        self.assertEqual(report["current_reader_blocks"],len(rows)+1)
        self.assertEqual(report["performed_turns_independently_AV_verified"],0)
        self.assertEqual(report["actor_role_identifications_independently_original_audio_verified"],0)
        self.assertEqual(report["source_coverage"]["fully_provisionally_named_source_units"],
                         report["previous_source_coverage"]["fully_provisionally_named_source_units"]+30)
        index={(r["episode_id"],r["source_reading_ref"]):r for r in updated}
        self.assertEqual(index["S09E19","C305.1"]["candidate_role"],"ROZ RUSSELL")
        self.assertEqual(index["S09E19","C306.1"]["candidate_role"],"ALEX PATTERSON")
        self.assertEqual(index["S01E01","S01E01-C219-SOURCE-TURN-1"]["candidate_role"],
                         "HARRY STONE")
        self.assertIsNone(index["S01E01","S01E01-C219-SOURCE-TURN-2"]["candidate_role"])
        self.assertIsNone(index["S09E19","S09-S09E19-C206-UNVERIFIED-TWO-VOICE-BOUNDARY-T01"]["candidate_role"])
        self.assertEqual(index["S09E19","S09-S09E19-C206-UNVERIFIED-TWO-VOICE-BOUNDARY-T02"]["candidate_role"],
                         "DAN FIELDING")
        self.assertTrue(all(r["actor_face_or_voice_independently_verified"] is False for r in updated))
        self.assertEqual(rows,original)
        parts=[r for r in updated if r["episode_id"]=="S09E19"
               and r["source_reading_ref"].startswith("S09E19-C277-MANUAL-SOURCE-TURN-")]
        self.assertEqual(len(parts),2)
        self.assertEqual("".join(r["caption_text"] for r in parts),SNACK)
        for part in parts:
            span=part["source_exact_character_span"]
            self.assertEqual(hashlib.sha256(SNACK[span["start_char"]:span["end_char"]].encode()).hexdigest(),
                             span["exact_text_sha256"])
            self.assertIsNone(part["candidate_role"])
            self.assertIsNone(part["source_original_times_ms"])

    def test_decline_fake_soundtrack_certification_mismatched_context_or_cue(self):
        rows,ledger=fixture()
        bad=copy.deepcopy(ledger)
        bad["role_amendments"][0]["original_audio_verified"]=True
        with self.assertRaisesRegex(ValueError,"Unanchored"):
            validate_ledger(bad)
        bad=copy.deepcopy(ledger)
        bad["role_amendments"][0]["new_provisional_role"]="WRONG"
        wrong=copy.deepcopy(rows)
        wrong[0]["candidate_role"]="OTHER"
        with self.assertRaisesRegex(ValueError,"conflicts"):
            apply(wrong,ledger,strict=False)
        wrong=copy.deepcopy(rows)
        wrong[1]["caption_text"]="Different subtitle"
        with self.assertRaisesRegex(ValueError,"conflicts"):
            apply(wrong,ledger,strict=False)
        wrong=copy.deepcopy(rows)
        wrong[-1]["caption_text"]=SNACK.replace("Yeah,","Maybe,")
        with self.assertRaisesRegex(ValueError,"snack cue"):
            apply(wrong,ledger,strict=False)
        wrong=copy.deepcopy(rows)
        wrong[-1]["source_original_times_ms"]=[{"start_ms":15,"end_ms":20}]
        with self.assertRaisesRegex(ValueError,"snack cue"):
            apply(wrong,ledger,strict=False)
        bad=copy.deepcopy(ledger)
        bad["role_amendments"].append(copy.deepcopy(bad["role_amendments"][0]))
        with self.assertRaisesRegex(ValueError,"checked count"):
            validate_ledger(bad)
        bad=copy.deepcopy(ledger)
        bad["original_source_shas"]["S09E19"]="wrong"
        with self.assertRaisesRegex(ValueError,"exact current v15"):
            validate_ledger(bad)

if __name__=="__main__":
    unittest.main()
