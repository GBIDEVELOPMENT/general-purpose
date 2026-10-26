#!/usr/bin/env python3
"""Standalone synthetic tests for production-screenplay ↔ aired-caption proposals."""
import unittest
from align_private_production_script import (
    ALIASES, SCHEMA, align, norm, parse_private_plaintext, scored_windows
)


def unit(cue, text):
    return {"cue":cue,"part":1,"source_text":text}


class ScriptToCaptionTests(unittest.TestCase):
    def test_extract_character_headings_not_stage_directions(self):
        source="""INT. COURTROOM - NIGHT

HARRY
Are you going to tell us what happened tonight?

[Distant crowd laughs]

DAN
I should say so; the whole incident was entirely predictable.

CHRISTINE
I certainly don't believe you.
"""
        blocks=parse_private_plaintext(source,"S09E19")
        self.assertEqual([x["character"] for x in blocks],
            ["HARRY STONE","DAN FIELDING","CHRISTINE SULLIVAN"])
        self.assertTrue(all(x["script_start_line"]>0 for x in blocks))

    def test_revival_and_wrong_pilot_roles_do_not_get_silent_approval(self):
        script="""ABBY
I am a new judge in town, from the 2023 revival.

GURGS
I am the new court bailiff.
"""
        self.assertEqual(parse_private_plaintext(script,"S01E01"),[])
        self.assertEqual(parse_private_plaintext("HARRY\nA tiny joke.","S01E01"),[])

    def test_source_accurate_candidate_and_no_audio_acceptance(self):
        units=[
            unit(1,"The judge will be here any minute."),
            unit(2,"Are you finished painting?"),
            unit(3,"I have nothing to say to you today."),
            unit(4,"Fine, then we will say goodbye.")
        ]
        claims=[{"character":"LANA WAGNER",
                 "dialogue":"The judge will be here any minute.",
                 "script_start_line":12},
                {"character":"LANA WAGNER",
                 "dialogue":"I have nothing to say to you today.",
                 "script_start_line":20}]
        result=align(units,claims,"f"*64)
        self.assertEqual(result["schema"],SCHEMA)
        self.assertEqual([x["source_unit_ids"] for x in result["matched_claims"]],
                         [["C001.1"],["C003.1"]])
        self.assertFalse(result["source_audio_identity_verified"])
        self.assertTrue(all(not x["original_speech_identity_verified"]
                            for x in result["matched_claims"]))

    def test_multi_cue_same_speaker_and_spurious_role_abstention(self):
        units=[
            unit(1,"The complete original conversation"),
            unit(2,"will be continued on this next cue"),
            unit(3,"another person answers something else"),
        ]
        matches=scored_windows(units,"The complete original conversation will be continued on this next cue")
        self.assertTrue(matches)
        self.assertEqual(matches[0][1:],(0,1))
        result=align(units,[{"character":"HARRY STONE",
               "dialogue":"Completely different manuscript, not the broadcast.",
               "script_start_line":3}],"a"*64)
        self.assertEqual(result["matched_claims"],[])
        self.assertEqual(result["unmatched_script_blocks"],1)

    def test_duplicate_lines_remain_ambiguous(self):
        units=[
            unit(1,"Everything about this episode was a wonderful surprise."),
            unit(2,"Some other person says something different."),
            unit(3,"Everything about this episode was a wonderful surprise."),
        ]
        a=align(units,[{"character":"HARRY STONE",
           "dialogue":"Everything about this episode was a wonderful surprise.",
           "script_start_line":1}],"c"*64)
        self.assertFalse(a["matched_claims"])
        self.assertEqual(len(a["ambiguous_claims"]),1)


if __name__=="__main__":
    unittest.main()
