#!/usr/bin/env python3
"""Synthetic participation-evidence tests. Never import actual TV dialogue."""
from pathlib import Path
from tempfile import TemporaryDirectory
from importlib.util import spec_from_file_location,module_from_spec
import unittest
import json

HERE=Path(__file__).resolve().parent
spec=spec_from_file_location("nc_scene_participation",HERE/"build_scene_participation.py")
P=module_from_spec(spec)
spec.loader.exec_module(P)

def person(i,name,scope):
    return {"character_id":f"tvmaze:{i}","character_name":name,
            "actor_name":"Synthetic Actor "+str(i),"credit_scope":scope,
            "aliases":[name]}

def turn(n,speaker=None,address=None,scene=1):
    return {"turn_id":f"S01E01:C{n:05d}:1","source_cue":n,
            "start_ms":n*1500,"end_ms":n*1500+1200,
            "provisional_scene_number":scene,
            "structural_signals":{
                "explicit_speaker_label_candidates":[speaker] if speaker else [],
                "vocative_addressee_candidates_not_speakers":[address] if address else []},
            "speaker":"UNKNOWN"}

class SceneEvidenceTests(unittest.TestCase):
    def test_addressed_character_is_not_assigned_as_speaker(self):
        roster=[person(1,"Judge Test","series_wide_cast_only"),
                person(2,"Courier Test","episode_specific_guest_credit"),
                person(3,"Other Regular","series_wide_cast_only")]
        dialogue=[
          turn(1,address="tvmaze:1"),
          turn(2,speaker="tvmaze:2"),
          turn(3)]
        r=P.scene_summary(1,dialogue,roster)
        self.assertEqual(r["source_turn_count"],3)
        self.assertEqual(r["turns_with_no_unique_speaker_label"],2)
        evidence={x["character_id"]:x for x in r["textually_signaled_possible_participants"]}
        self.assertEqual(evidence["tvmaze:1"]["speaker_hypothesis_strength"],"addressee_only_not_a_speaker")
        self.assertEqual(evidence["tvmaze:1"]["addressed_by_name_turn_ids"],["S01E01:C00001:1"])
        self.assertEqual(evidence["tvmaze:1"]["explicit_source_speaker_label_turn_ids"],[])
        self.assertEqual(evidence["tvmaze:2"]["speaker_hypothesis_strength"],"strong_explicit_label")
        self.assertEqual(evidence["tvmaze:2"]["explicit_source_speaker_label_turn_ids"],["S01E01:C00002:1"])
        self.assertEqual([x["character_id"] for x in r["series_cast_without_textual_scene_signal"]],
                         ["tvmaze:3"])
        self.assertTrue(r["uncredited_participants_must_remain_possible"])
    def test_no_cast_member_speaks_solely_because_credited(self):
        roster=[person(5,"Credited Role","episode_specific_guest_credit")]
        r=P.scene_summary(1,[turn(1)],roster)
        self.assertEqual(r["textually_signaled_possible_participants"],[])
        self.assertEqual(r["credited_guest_roles_without_textual_scene_signal"][0]["character_id"],"tvmaze:5")
        self.assertEqual(r["credited_guest_roles_without_textual_scene_signal"][0]["scene_presence"],"unverified")
    def test_missing_speaker_packet_fails_closed(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            previous=P.ROOT
            P.ROOT=root
            try:
                base=root/"seasons"/"S01"/"S01E01"/"dialogue"/"versions"/"test-id"
                base.mkdir(parents=True)
                manifest=base/"manifest.json"
                manifest.write_text(json.dumps({"episode_id":"S01E01"}),"utf-8")
                with self.assertRaisesRegex(ValueError,"packet preparation required"):
                    P.summarize_version({"episode_id":"S01E01","version_id":"test-id",
                                         "sha256":"a"*64,"manifest":str(manifest.relative_to(root))})
            finally:
                P.ROOT=previous

if __name__=="__main__":
    unittest.main()
