#!/usr/bin/env python3
"""Original S09 rapid exchange: lossless unpunctuated source turn tests."""
import copy
import unittest
from build_s09_mixed_voice_turns_v11 import (
    SOURCE_SHA,STATUS,DELIMITERS,TARGETS,GROUPS,transform,splits
)

TEXT={
    "C188.1":"meet i just got carried away oh roz there are worse things i",
    "C189.1":"can't think of any at the moment but there are i can't face him now i lied to",
    "C190.1":"him i think you're missing a really great opportunity roz yeah i",
    "C191.1":"really would like to get a look at him there's only one way to do that you",
    "C192.1":"gotta go",
}

def old():
    result=[]
    for i,ref in enumerate(TARGETS):
        result.append({
            "schema":"night-court-private-character-dialogue-evidence/1",
            "episode_id":"S09E19",
            "source_reading_ref":ref,
            "original_source_part_refs":[ref],
            "original_source_sha256":SOURCE_SHA,
            "reading_block_id":f"old-v10:{i+1}",
            "candidate_role":"CHRISTINE SULLIVAN" if ref=="C190.1" else None,
            "role_attribution_status":"unidentified" if ref!="C190.1" else "provisional_script_context",
            "caption_text":TEXT[ref],
            "original_source_untimed":True,
            "source_original_times_ms":None,
            "speaker_turn_boundary_verified":False,
            "actor_face_or_voice_independently_verified":False,
        })
    return result

class SourceMixedS09TurnTests(unittest.TestCase):
    def test_five_caption_units_six_proposed_role_turns_with_full_source_bytes(self):
        old_rows=old()
        output,summary=transform(old_rows,full=False)
        self.assertEqual(len(output),6)
        self.assertEqual(summary["original_caption_units"],5)
        self.assertEqual(summary["provisional_named_original_units"],5)
        self.assertEqual(summary["original_units_remaining_unknown"],0)
        self.assertFalse(summary["actual_audio_review_performed"])
        self.assertEqual(summary["potential_character_voice_and_turn_verifications_from_actual_original_av"],0)
        self.assertEqual([x["candidate_role"] for x in output],
            [name for name,_ in GROUPS])
        self.assertTrue(all(x["role_attribution_status"]==STATUS for x in output))
        self.assertTrue(all(x["speaker_turn_boundary_verified"] is False for x in output))
        self.assertTrue(all(x["actor_face_or_voice_independently_verified"] is False for x in output))
        self.assertTrue(all(x["source_original_times_ms"] is None for x in output))
        self.assertTrue(all(x["original_two_performer_scene_not_actually_verified"] is True for x in output))
        self.assertEqual(old_rows[2]["candidate_role"],"CHRISTINE SULLIVAN")
        self.assertEqual(old_rows[2]["caption_text"],TEXT["C190.1"])

    def test_each_unicode_character_from_source_is_used_exactly_once(self):
        result,_=transform(old(),full=False)
        byref={}
        for r in result:
            for s in r["source_original_unicode_spans"]:
                byref.setdefault(s["source_ref"],[]).append((s["start_char"],s["end_char"]))
        self.assertEqual(set(byref),set(TARGETS))
        for ref,spans in byref.items():
            endpoints=sorted(spans)
            self.assertEqual(endpoints[0][0],0)
            self.assertEqual(endpoints[-1][1],len(TEXT[ref]))
            self.assertTrue(all(a[1]==b[0] for a,b in zip(endpoints,endpoints[1:])))

    def test_wrong_prior_character_or_source_cue_cannot_promote_names(self):
        current=old()
        current[2]["candidate_role"]="ROZ RUSSELL"
        with self.assertRaisesRegex(ValueError,"drift"):
            transform(current,full=False)
        current=old()
        current[0]["caption_text"]=current[0]["caption_text"].replace("oh roz","a different phrase")
        with self.assertRaisesRegex(ValueError,"missing or duplicated"):
            transform(current,full=False)
        current=old()
        current[1]["actor_face_or_voice_independently_verified"]=True
        with self.assertRaisesRegex(ValueError,"drift"):
            transform(current,full=False)

    def test_nonmonotone_source_character_boundaries_abstain(self):
        with self.assertRaisesRegex(ValueError,"missing or duplicated"):
            splits("one two three",["different"])
        with self.assertRaisesRegex(ValueError,"nonmonotone"):
            splits("one two three",["three","two"])

if __name__=="__main__":
    unittest.main()
