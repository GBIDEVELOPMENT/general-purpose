#!/usr/bin/env python3
"""Unverified S09 episode-context identities do not mutate exact source."""
import copy
import json
import unittest
from pathlib import Path
from build_s09_high_context_speaker_reader_v12 import (
    LEDGER,STATUS,SOURCE_SHA,apply_context,verify_ledger
)

def fixture():
    evidence=json.loads(LEDGER.read_text("utf-8"))
    rows=[]
    for i,x in enumerate(evidence["candidates"]):
        rows.append({
            "episode_id":"S09E19",
            "source_reading_ref":x["source_reading_ref"],
            "original_source_part_refs":x["original_source_part_refs"],
            "original_source_sha256":SOURCE_SHA,
            "reading_block_id":f"source-v11:{i}",
            "caption_text":"source excerpt "+x["source_text_must_contain"]+" continuing",
            "candidate_role":None,"role_attribution_status":"unidentified",
            "source_original_times_ms":None,"original_source_untimed":True,
            "speaker_turn_boundary_verified":False,
            "actor_face_or_voice_independently_verified":False,
        })
    rows.append({
        "episode_id":"S01E01","source_reading_ref":"C001.1",
        "original_source_part_refs":["C001.1"],
        "original_source_sha256":"a"*64,"reading_block_id":"s01:1",
        "caption_text":"An unrelated known-role pilot cue.",
        "candidate_role":"HARRY STONE","role_attribution_status":"editorial",
        "source_original_times_ms":[{"start_ms":0,"end_ms":1000}],
        "original_source_untimed":False,
        "speaker_turn_boundary_verified":False,
        "actor_face_or_voice_independently_verified":False
    })
    return rows,evidence

class SourceS09ContextualNamesTests(unittest.TestCase):
    def test_twelve_source_reading_blocks_fifteen_original_part_roles(self):
        old,evidence=fixture()
        updated,report=apply_context(old,evidence,strict=False)
        self.assertEqual(len(updated),len(old))
        self.assertEqual(report["original_caption_source_units"],16)
        self.assertEqual(report["current_provisional_character_named_original_units"],16)
        self.assertEqual(report["still_unknown_original_source_units"],0)
        self.assertEqual(report["new_original_caption_parts_with_working_names"],15)
        self.assertEqual(report["previously_unidentified_reader_blocks_now_contextually_named"],12)
        self.assertEqual(report["original_soundtrack_actor_identities_independently_reviewed_and_accepted"],0)
        self.assertTrue(report["original_S09_source_still_untimed"])
        self.assertEqual(updated[-1],old[-1])
        self.assertEqual(old[0]["candidate_role"],None)
        self.assertTrue(all(r["role_attribution_status"]==STATUS for r in updated[:-1]))
        self.assertTrue(all(r["actor_face_or_voice_independently_verified"] is False
                            and r["speaker_turn_boundary_verified"] is False
                            and r["source_original_times_ms"] is None
                            for r in updated[:-1]))
        self.assertEqual(updated[5]["original_source_part_refs"],["C134.1","C135.1"])
        self.assertEqual(updated[5]["candidate_role"],"BULL SHANNON")

    def test_existing_names_and_original_s09_times_cannot_be_overwritten(self):
        rows,evidence=fixture()
        damaged=copy.deepcopy(rows)
        damaged[0]["candidate_role"]="HARRY STONE"
        with self.assertRaisesRegex(ValueError,"conflicts"):
            apply_context(damaged,evidence,strict=False)
        damaged=copy.deepcopy(rows)
        damaged[3]["source_original_times_ms"]=[{"start_ms":1,"end_ms":22}]
        with self.assertRaisesRegex(ValueError,"conflicts"):
            apply_context(damaged,evidence,strict=False)
        damaged=copy.deepcopy(rows)
        damaged[5]["original_source_part_refs"]=["C134.1"]
        with self.assertRaisesRegex(ValueError,"conflicts"):
            apply_context(damaged,evidence,strict=False)
        damaged=copy.deepcopy(rows)
        damaged[2]["actor_face_or_voice_independently_verified"]=True
        with self.assertRaisesRegex(ValueError,"conflicts"):
            apply_context(damaged,evidence,strict=False)

    def test_fake_audio_certification_duplicate_cue_or_changed_ledger_abstains(self):
        rows,evidence=fixture()
        bad=copy.deepcopy(evidence)
        bad["contextual_name_proposals_are_independently_original_audio_verified"]=True
        with self.assertRaisesRegex(ValueError,"not admissible"):
            verify_ledger(bad)
        bad=copy.deepcopy(evidence)
        bad["candidates"][1]["original_source_part_refs"]=["C091.1"]
        with self.assertRaisesRegex(ValueError,"Duplicate original caption"):
            verify_ledger(bad)
        bad=copy.deepcopy(evidence)
        bad["candidates"][0]["proposed_role"]=" "
        with self.assertRaisesRegex(ValueError,"lacks exact source"):
            verify_ledger(bad)
        bad=copy.deepcopy(evidence)
        bad["candidates"][4]["source_actor_or_performer_independently_audio_verified"]=True
        with self.assertRaisesRegex(ValueError,"lacks exact source"):
            verify_ledger(bad)

if __name__=="__main__":
    unittest.main()
