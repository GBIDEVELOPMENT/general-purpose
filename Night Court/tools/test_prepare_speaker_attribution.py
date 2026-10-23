#!/usr/bin/env python3
"""Synthetic tests only; no reproduced Night Court captions."""
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

HERE=Path(__file__).resolve().parent
spec=spec_from_file_location("speaker_packets",HERE/"prepare_speaker_attribution.py")
S=module_from_spec(spec);spec.loader.exec_module(S)

ROSTER=[
 {"character_id":"tvmaze:1","character_name":"Harold T. Stone","aliases":["Harry","Harry Stone","Judge Stone"]},
 {"character_id":"tvmaze:2","character_name":"Dan Fielding","aliases":["Dan","Dan Fielding"]},
 {"character_id":"tvmaze:3","character_name":"Bull Shannon","aliases":["Bull","Bull Shannon"]}
]

class TestAttributionPreparation(unittest.TestCase):
    def test_reliable_typographic_split(self):
        a=S.pieces("- Hello, imaginary judge.\n- Good morning, courtroom.")
        self.assertEqual(len(a),2)
        self.assertTrue(all(m=="explicit_caption_dash_segment" for _,m in a))
        b=S.pieces("A whole sentence\ncontinues here.")
        self.assertEqual(len(b),1)
        c=S.pieces("A first voice.\n- Different speaker.")
        self.assertEqual(len(c),2)
        d=S.pieces("- A hyphen starter.\ncontinuation is same cue.")
        self.assertEqual(len(d),1)
    def test_label_vs_addressee_not_confused(self):
        self.assertEqual(S.explicit_colon_speaker("HARRY: Imaginary docket.",ROSTER),["tvmaze:1"])
        self.assertEqual(S.explicit_colon_speaker("Harry, can you help?",ROSTER),[])
        self.assertIn("tvmaze:1",S.addressed_people("Hey Harry, can you help?",ROSTER))
        self.assertEqual(S.explicit_colon_speaker("Mr. Judge: Order!",ROSTER),[])
    def test_packet_source_identity_and_unknown_default(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"segments.jsonl"
            cues=[
             {"cue":1,"start_ms":0,"end_ms":1200,"text":"- Harry, have a look.\n- I see it."},
             {"cue":2,"start_ms":1250,"end_ms":2200,"text":"DAN: Mock testimony."},
             {"cue":3,"start_ms":38000,"end_ms":39700,"text":"Silence has ended."}
            ]
            path.write_text("\n".join(json.dumps(s) for s in cues)+"\n","utf-8")
            turns=S.make_turns({"id":"S01E01"},path,ROSTER)
            self.assertEqual(len(turns),4)
            self.assertEqual(turns[0]["source_cue"],1)
            self.assertEqual(turns[1]["source_cue"],1)
            self.assertEqual(turns[2]["speaker"],"UNKNOWN")
            self.assertEqual(turns[2]["structural_signals"]["explicit_speaker_label_candidates"],["tvmaze:2"])
            self.assertEqual(turns[-1]["provisional_scene_number"],2)
            meta={"episode_id":"S01E01","version_id":"synthetic","sha256":"abc"}
            packs=S.packages(turns,ROSTER,meta)
            self.assertEqual(len(packs),1)
            self.assertEqual(packs[0]["utterances"][2]["text"],"DAN: Mock testimony.")
            self.assertIn("UNKNOWN",packs[0]["speaker_options"])
    def test_overlap_window_never_drops_turns(self):
        turns=[{"turn_id":f"T{i:03d}"} for i in range(120)]
        packs=S.packages(turns,ROSTER,{"episode_id":"S01E01","version_id":"synthetic","sha256":"abc"})
        self.assertTrue(all(len(p["utterances"])<=S.PACKET_LIMIT for p in packs))
        self.assertEqual({x["turn_id"] for p in packs for x in p["utterances"]},
                         {x["turn_id"] for x in turns})
        self.assertEqual(len(packs),3)
        self.assertEqual(packs[0]["utterances"][-6:],[*packs[1]["utterances"][:6]])
    def test_roster_uses_credits_as_candidates_not_appearances(self):
        with TemporaryDirectory() as tmp:
            old=S.CAST
            self.addCleanup(setattr,S,"CAST",old)
            S.CAST=Path(tmp)/"cast.json"
            S.CAST.write_text(json.dumps({"credits":[{
                "person":{"name":"Actor One"},
                "character":{"name":"Harold T. Stone","tvmaze_id":1}
            }]}),"utf-8")
            roster=S.cast_roster({"credits":{"guest_cast":[{
                "person":{"name":"Guest Actor"},
                "character":{"name":"Mock Guest","tvmaze_id":99}}]}})
            self.assertEqual(len(roster),2)
            self.assertEqual(roster[0]["credit_scope"],"episode_specific_guest_credit")
            self.assertEqual(roster[-1]["credit_scope"],"series_wide_cast_only")

if __name__=="__main__":unittest.main()
