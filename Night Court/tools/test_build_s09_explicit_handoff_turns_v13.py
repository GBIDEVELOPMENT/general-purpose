#!/usr/bin/env python3
"""Source-character conservation for three original S09 explicit actor handoffs."""
import copy
import json
import unittest
from collections import defaultdict
from build_s09_explicit_handoff_turns_v13 import (
    LEDGER,STATUS,SOURCE_SHA,check_ledger,transform
)

SAMPLES={
 "C126.1":"Christine Sullivan must be elected to Congress. Mac, your commercial inspired",
 "C127.1":"me. Well, thanks, Harriet. Hey, never underestimate the power of advertising.",
 "C146.1":"And I'm going to help him pull it. Come along, Harry. Yeah, thanks, Dan.",
 "C284.1":"And you are... Out of here.",
}

def fixture():
    old=[]
    for i,(ref,line) in enumerate(SAMPLES.items()):
        old.append({
            "episode_id":"S09E19","source_reading_ref":ref,
            "original_source_part_refs":[ref],"original_source_sha256":SOURCE_SHA,
            "reading_block_id":f"S09E19:old-v12:{i}",
            "caption_text":line,
            "candidate_role":"HARRIET" if ref=="C126.1" else None,
            "role_attribution_status":(
                "source_scene_character_dialogue_proposal_not_original_av_verified"
                if ref=="C126.1" else "unidentified"),
            "source_original_times_ms":None,"original_source_untimed":True,
            "speaker_turn_boundary_verified":False,
            "actor_face_or_voice_independently_verified":False,
        })
    old.append({
        "episode_id":"S01E01","source_reading_ref":"C020.1",
        "original_source_part_refs":["C020.1"],"original_source_sha256":"a"*64,
        "reading_block_id":"S01E01:unrelated", "caption_text":"Unrelated original cue.",
        "candidate_role":"HARRY STONE","role_attribution_status":"provisional",
        "source_original_times_ms":[{"start_ms":2345,"end_ms":5678}],
        "original_source_untimed":False,"speaker_turn_boundary_verified":False,
        "actor_face_or_voice_independently_verified":False,
    })
    return old,json.loads(LEDGER.read_text("utf-8"))


class SourceOriginalHandoffsTests(unittest.TestCase):
    def test_six_candidate_scene_voice_turns_preserve_all_four_source_cues(self):
        old,ledger=fixture()
        new,report=transform(old,ledger,strict=False)
        self.assertEqual(len(new),len(old)+2)
        self.assertEqual(report["original_held_caption_units"],5)
        self.assertEqual(report["provisionally_named_original_caption_units"],5)
        self.assertEqual(report["unidentified_original_caption_units"],0)
        self.assertEqual(report["new_provisional_speaking_turns"],7)
        self.assertEqual(report["source_audio_actor_identities_or_true_turns_independently_verified"],0)
        self.assertFalse(report["original_s09_untimed_source_changed"])
        scene=[r for r in new if r["episode_id"]=="S09E19"]
        self.assertEqual([r["candidate_role"] for r in scene],[
            "HARRIET","MAC ROBINSON","DAN FIELDING","HARRY STONE",
            "ALEX PATTERSON","ROZ RUSSELL"
        ])
        self.assertEqual(new[-1],old[-1])
        self.assertTrue(all(r["role_attribution_status"]==STATUS for r in scene))
        self.assertTrue(all(r["speaker_turn_boundary_verified"] is False
                            and r["actor_face_or_voice_independently_verified"] is False
                            and r["source_original_times_ms"] is None
                            and r["human_viewed_film_or_listened_to_actor"] is False
                            for r in scene))
        self.assertEqual(old[0]["candidate_role"],"HARRIET")
        self.assertIsNone(old[1]["candidate_role"])

    def test_every_original_unicode_character_is_recoverable_without_loss(self):
        old,ledger=fixture()
        new,_=transform(old,ledger,strict=False)
        spans=defaultdict(list)
        for row in new:
            for span in row.get("original_source_unicode_spans_v13",[]):
                spans[span["original_source_ref"]].append(span)
        self.assertEqual(set(spans),set(SAMPLES))
        for ref,parts in spans.items():
            ordered=sorted(parts,key=lambda p:p["start_char"])
            self.assertEqual(ordered[0]["start_char"],0)
            self.assertEqual(ordered[-1]["end_char"],len(SAMPLES[ref]))
            self.assertEqual("".join(SAMPLES[ref][p["start_char"]:p["end_char"]]
                                     for p in ordered),SAMPLES[ref])
            self.assertTrue(all(a["end_char"]==b["start_char"] for a,b in zip(ordered,ordered[1:])))

    def test_edited_original_cue_prior_character_and_fake_timing_rejected(self):
        old,ledger=fixture()
        bad=copy.deepcopy(old)
        bad[1]["caption_text"]="Something different."
        with self.assertRaisesRegex(ValueError,"unique claimed"):
            transform(bad,ledger,strict=False)
        bad=copy.deepcopy(old)
        bad[2]["candidate_role"]="ROZ RUSSELL"
        with self.assertRaisesRegex(ValueError,"Original source role"):
            transform(bad,ledger,strict=False)
        bad=copy.deepcopy(old)
        bad[3]["source_original_times_ms"]=[{"start_ms":123,"end_ms":456}]
        with self.assertRaisesRegex(ValueError,"Original source role"):
            transform(bad,ledger,strict=False)
        bad=copy.deepcopy(old)
        bad[0]["actor_face_or_voice_independently_verified"]=True
        with self.assertRaisesRegex(ValueError,"Original source role"):
            transform(bad,ledger,strict=False)

    def test_change_to_named_performers_source_ref_or_independent_av_assertion_abstains(self):
        old,ledger=fixture()
        bad=copy.deepcopy(ledger)
        bad["roles_original_actor_voice_verified"]=True
        with self.assertRaisesRegex(ValueError,"overstate original film"):
            check_ledger(bad)
        bad=copy.deepcopy(ledger)
        bad["proposals"][1]["split_role_groups"][1]["provisional_role"]="CHRISTINE SULLIVAN"
        with self.assertRaisesRegex(ValueError,"roles/split boundary"):
            check_ledger(bad)
        bad=copy.deepcopy(ledger)
        bad["proposals"][0]["split_role_groups"][0]["source_parts"]=[["C127.1",0]]
        with self.assertRaisesRegex(ValueError,"Unsupported source-character"):
            check_ledger(bad)

if __name__=="__main__":
    unittest.main()
