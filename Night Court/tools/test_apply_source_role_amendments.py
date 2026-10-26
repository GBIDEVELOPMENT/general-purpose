#!/usr/bin/env python3
"""Generic original-subtitle SHA checked, source-context role amendment QA."""
import copy
import json
import unittest
from apply_source_role_amendments import LEDGER,SOURCES,STATUS,apply,validate_ledger


def fixture():
    ledger=json.loads(LEDGER.read_text("utf-8"))
    rows=[]
    for i,p in enumerate(ledger["amendments"]):
        rows.append({
            "episode_id":p["episode_id"],
            "source_reading_ref":p["source_reading_ref"],
            "original_source_part_refs":p["original_source_part_refs"],
            "original_source_sha256":p["original_source_witness_sha256"],
            "reading_block_id":f"S09E19:synthetic:{i}",
            "caption_text":"What the character actually said: "+p["source_text_must_contain"],
            "candidate_role":None,"role_attribution_status":"unidentified",
            "source_original_times_ms":None,"original_source_untimed":True,
            "speaker_turn_boundary_verified":False,
            "actor_face_or_voice_independently_verified":False
        })
    rows.append({
        "episode_id":"S01E01","source_reading_ref":"C010.1",
        "original_source_part_refs":["C010.1"],
        "original_source_sha256":SOURCES["S01E01"],
        "reading_block_id":"S01:unchanged",
        "caption_text":"Known role line elsewhere in original series",
        "candidate_role":"HARRY STONE","role_attribution_status":"provisional_original_source",
        "source_original_times_ms":[{"start_ms":1,"end_ms":1234}],
        "original_source_untimed":False,
        "speaker_turn_boundary_verified":False,
        "actor_face_or_voice_independently_verified":False
    })
    return rows,ledger


class SourceRoleAmendmentsTests(unittest.TestCase):
    def test_six_source_guest_pauls_and_unrelated_episodes_preserved_exactly(self):
        original,ledger=fixture()
        changed,summary=apply(original,ledger,strict=False)
        self.assertEqual(len(changed),len(original))
        self.assertEqual(summary["original_held_source_caption_units"],7)
        self.assertEqual(summary["provisionally_named_source_units"],7)
        self.assertEqual(summary["unknown_original_source_units"],0)
        self.assertEqual(summary["source_reading_blocks"],len(original))
        self.assertEqual(summary["reusable_ledger_amendment_count"],6)
        self.assertEqual(summary["previously_unidentified_original_source_parts_now_contextually_named"],6)
        self.assertEqual(summary["source_character_roles_independently_verified_via_AV"],0)
        self.assertEqual(changed[-1],original[-1])
        self.assertTrue(all(x["candidate_role"]=="PAUL" for x in changed[:-1]))
        self.assertTrue(all(x["role_attribution_status"]==STATUS for x in changed[:-1]))
        self.assertTrue(all(x["speaker_turn_boundary_verified"] is False and
                            x["actor_face_or_voice_independently_verified"] is False
                            for x in changed))
        self.assertTrue(all(x["candidate_role"] is None for x in original[:-1]))

    def test_refuse_to_overwrite_old_name_source_clock_or_text(self):
        old,ledger=fixture()
        changed=copy.deepcopy(old)
        changed[0]["candidate_role"]="CHRISTINE SULLIVAN"
        with self.assertRaisesRegex(ValueError,"would overwrite"):
            apply(changed,ledger,strict=False)
        changed=copy.deepcopy(old)
        changed[1]["source_original_times_ms"]=[{"start_ms":15,"end_ms":30}]
        with self.assertRaisesRegex(ValueError,"would overwrite"):
            apply(changed,ledger,strict=False)
        changed=copy.deepcopy(old)
        changed[2]["caption_text"]="Mismatched source"
        with self.assertRaisesRegex(ValueError,"would overwrite"):
            apply(changed,ledger,strict=False)
        changed=copy.deepcopy(old)
        changed[0]["actor_face_or_voice_independently_verified"]=True
        with self.assertRaisesRegex(ValueError,"would overwrite"):
            apply(changed,ledger,strict=False)

    def test_repeat_name_missing_reference_or_false_soundtrack_certification_abstains(self):
        old,ledger=fixture()
        bad=copy.deepcopy(ledger)
        bad["amendments"].append(copy.deepcopy(bad["amendments"][0]))
        with self.assertRaisesRegex(ValueError,"Duplicated"):
            validate_ledger(bad)
        bad=copy.deepcopy(ledger)
        bad["amendments"][0]["source_actor_or_performer_independently_audio_verified"]=True
        with self.assertRaisesRegex(ValueError,"lacks reliable"):
            validate_ledger(bad)
        bad=copy.deepcopy(ledger)
        bad["source_actor_identity_independently_verified"]=True
        with self.assertRaisesRegex(ValueError,"frozen baseline"):
            validate_ledger(bad)
        bad=copy.deepcopy(ledger)
        bad["amendments"][0]["source_reading_ref"]="C998.1"
        with self.assertRaisesRegex(ValueError,"missing/previously joined"):
            apply(old,bad,strict=False)

if __name__=="__main__":
    unittest.main()
