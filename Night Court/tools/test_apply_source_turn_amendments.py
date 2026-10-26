#!/usr/bin/env python3
"""Tests for source-exact original S09 C102/C103 3-party-turn proposal."""
import copy
import json
import unittest
from collections import defaultdict
from apply_source_turn_amendments import LEDGER,SOURCE_SHA,STATUS,apply,validate_ledger


def fixture():
    rows=[]
    for n,t in ((102,"Hold on a second. You mean you didn't know that was there? No, I've never seen"),
                (103,"it. Wow."),
                (209,"from. That's right, I mean, voters are very fickle."),
                (211,"I don't think so. Well, that outfit really showed off your figure."),
                (121,"letters. Yeah, probably."),
                (206,"Well... thing is very unsettling. No, this whole thing is really boring."),
                (271,"No. It's yours. You want it. No, really. You keep it."),
                (290,"He. Was she?")):
        rows.append({
            "episode_id":"S09E19","source_reading_ref":f"C{n:03d}.1",
            "original_source_part_refs":[f"C{n:03d}.1"],
            "original_source_sha256":SOURCE_SHA,
            "reading_block_id":f"S09E19:v13:{n}",
            "caption_text":t,"candidate_role":None,
            "role_attribution_status":"unidentified",
            "source_original_times_ms":None,"original_source_untimed":True,
            "actor_face_or_voice_independently_verified":False,
            "speaker_turn_boundary_verified":False
        })
    rows.append({
        "episode_id":"S01E01","source_reading_ref":"C100.1",
        "original_source_part_refs":["C100.1"],
        "reading_block_id":"S01E01:unrelated",
        "caption_text":"Unrelated held source sentence.",
        "candidate_role":"HARRY STONE",
        "role_attribution_status":"editorial",
        "original_source_sha256":"a"*64,
        "source_original_times_ms":[123,456],
        "original_source_untimed":False,
        "speaker_turn_boundary_verified":False,
        "actor_face_or_voice_independently_verified":False
    })
    return rows,json.loads(LEDGER.read_text("utf-8"))


class SourceTurnPatchTests(unittest.TestCase):
    def test_original_two_cues_reconstruct_as_three_utterances_without_new_audio_evidence(self):
        rows,ledger=fixture()
        output,m=apply(rows,ledger,strict=False)
        self.assertEqual(len(output),16)
        self.assertEqual(m["original_caption_source_units"],9)
        self.assertEqual(m["named_original_source_units"],3)
        self.assertEqual(m["unknown_original_source_units"],6)
        self.assertEqual(m["newly_named_original_source_units"],2)
        self.assertEqual(m["source_p0_amendment_count"],7)
        self.assertEqual([r["candidate_role"] for r in output[3:7]],
            ["DAN FIELDING",None,"CHRISTINE SULLIVAN",None])
        self.assertEqual([r["role_attribution_status"] for r in output[3:7]],
            [STATUS,"unidentified",STATUS,"unidentified"])
        self.assertEqual(m["source_new_performer_identifications_AV_certified"],0)
        self.assertEqual(m["source_new_turn_boundaries_AV_verified"],0)
        self.assertEqual([r["candidate_role"] for r in output[:3]],[
            "DAN FIELDING","HARRY STONE","DAN FIELDING"
        ])
        self.assertEqual(output[-1],rows[-1])
        self.assertTrue(all(r["role_attribution_status"]==STATUS for r in output[:3]))
        self.assertTrue(all(r["speaker_turn_boundary_verified"] is False and
                            r["actor_face_or_voice_independently_verified"] is False and
                            r["source_original_times_ms"] is None for r in output[:3]))

    def test_every_unicode_source_character_restored_once(self):
        rows,ledger=fixture()
        output,_=apply(rows,ledger,strict=False)
        orig={x["source_reading_ref"]:x["caption_text"] for x in rows[:-1]}
        collected=defaultdict(list)
        for row in output:
            for p in row.get("source_exact_character_spans",[]):
                collected[p["original_source_ref"]].append((p["start_char"],p["end_char"]))
        self.assertEqual(set(collected),set(orig))
        for ref,parts in collected.items():
            spans=sorted(parts)
            self.assertEqual(spans[0][0],0)
            self.assertEqual(spans[-1][1],len(orig[ref]))
            self.assertTrue(all(a[1]==b[0] for a,b in zip(spans,spans[1:])))
            self.assertEqual("".join(orig[ref][a:b] for a,b in spans),orig[ref])

    def test_source_timing_and_preexisting_roles_cannot_be_changed_by_split(self):
        rows,ledger=fixture()
        bad=copy.deepcopy(rows)
        bad[0]["candidate_role"]="DAN FIELDING"
        with self.assertRaisesRegex(ValueError,"original unidentified"):
            apply(bad,ledger,strict=False)
        bad=copy.deepcopy(rows)
        bad[1]["source_original_times_ms"]=[100,200]
        with self.assertRaisesRegex(ValueError,"original unidentified"):
            apply(bad,ledger,strict=False)
        bad=copy.deepcopy(rows)
        bad[0]["caption_text"]="The original dialogue was modified"
        with self.assertRaisesRegex(ValueError,"lexical turn boundary"):
            apply(bad,ledger,strict=False)
        bad=copy.deepcopy(rows)
        bad[1]["actor_face_or_voice_independently_verified"]=True
        with self.assertRaisesRegex(ValueError,"original unidentified"):
            apply(bad,ledger,strict=False)

    def test_a_new_unconfirmed_unnamed_subturn_does_not_count_as_fully_named(self):
        rows,ledger=fixture()
        bad=copy.deepcopy(ledger)
        bad["p0_amendments"][0]["new_turns"][2]["role"]=None
        output,summary=apply(rows,bad,strict=False)
        self.assertEqual(summary["newly_named_original_source_units"],1)
        self.assertEqual(summary["unknown_original_source_units"],7)
        self.assertEqual(summary["named_original_source_units"],2)
        self.assertIsNone(output[2]["candidate_role"])

    def test_second_person_in_mixed_source_caption_must_remain_unidentified(self):
        rows,ledger=fixture()
        bad=copy.deepcopy(ledger)
        bad["p0_amendments"][1]["new_turns"][1]["role"]="DAN FIELDING"
        result,summary=apply(rows,bad,strict=False)
        # A model can propose the same character for both fragments, but the
        # source cue remains only editorially named; do not accept it as AV proof.
        self.assertEqual(summary["named_original_source_units"],4)
        self.assertFalse(result[4]["actor_face_or_voice_independently_verified"])
        self.assertFalse(result[4]["speaker_turn_boundary_verified"])
        bad=copy.deepcopy(ledger)
        bad["p0_amendments"][1]["split_before"]["C209.1"]=["Invented boundary"]
        with self.assertRaisesRegex(ValueError,"exact original lexical"):
            apply(rows,bad,strict=False)

    def test_repeated_span_wrong_sequence_and_false_actor_ids_refused(self):
        rows,ledger=fixture()
        bad=copy.deepcopy(ledger)
        bad["source_audio_actor_identifications_independently_accepted"]=1
        with self.assertRaisesRegex(ValueError,"live character/role evidence"):
            validate_ledger(bad)
        bad=copy.deepcopy(ledger)
        bad["p0_amendments"][0]["new_turns"][2]["source_fragments"]=[
            ["C102.1",0]]
        with self.assertRaisesRegex(ValueError,"zero times or twice"):
            validate_ledger(bad)
        bad=copy.deepcopy(ledger)
        bad["p0_amendments"][0]["new_turns"][2]["role"]="Dan fielding"
        with self.assertRaisesRegex(ValueError,"label malformed"):
            validate_ledger(bad)

if __name__=="__main__":
    unittest.main()
