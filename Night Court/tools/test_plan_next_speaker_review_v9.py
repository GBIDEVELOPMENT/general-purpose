#!/usr/bin/env python3
"""Synthetic security/integrity checks for source-led original speaker review."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from plan_next_speaker_review_v9 import make_queue,load_s09_locator,S09_LOCATOR_SHA,SCHEMA


def row(ep,ref,role,text,time=None):
    return {
        "episode_id":ep,"source_reading_ref":ref,
        "original_source_part_refs":[ref],
        "original_source_sha256":"a"*64 if ep=="S01E01" else "b"*64,
        "caption_text":text,"candidate_role":role,
        "source_original_times_ms":time,
        "original_source_untimed":ep=="S09E19",
    }

class RemainingSpeakerReviewTests(unittest.TestCase):
    def test_source_unit_unknowns_rank_audio_leads_and_multivoice_p0(self):
        rows=[
            row("S01E01","C001.1","HARRY STONE","First lawyer line",[
                {"start_ms":1000,"end_ms":2100}
            ]),
            row("S01E01","C002.1",None,"Yeah.",[
                {"start_ms":2200,"end_ms":2800}
            ]),
            row("S09E19","C101.1","CHRISTINE SULLIVAN","Our lives have changed."),
            row("S09E19","C102.1",None,"Did you already know? No, not at all."),
            row("S09E19","C103.1",None,"Well..."),
        ]
        positions={102:{
            "candidate_original_audio_window_ms":[12000,17000],
            "original_paragraph_timecode_ms":None,
        }}
        seeds={"cues":[{"episode_id":"S09E19","original_cue":102}]}
        tasks,report=make_queue(rows,positions,seeds,strict=False)
        self.assertEqual(report["original_source_units_still_unknown"],3)
        self.assertEqual(report["original_units_provisionally_named"],2)
        self.assertEqual(report["s09_actual_audio_window_leads"],1)
        self.assertEqual(report["suspected_internal_switch_review_records"],1)
        self.assertEqual(tasks[0]["source_reading_ref"],"C102.1")
        self.assertEqual(tasks[0]["actual_original_sound_candidate_window_ms"],[12000,17000])
        self.assertTrue(tasks[0]["all_original_S09_caption_times_remain_null"])
        self.assertTrue(all(t["model_proposed_character"] is None for t in tasks))
        self.assertEqual(tasks[1]["source_reading_ref"],"C002.1")
        self.assertEqual(tasks[1]["actual_original_sound_candidate_window_ms"],[1000,4000])
        self.assertEqual(tasks[2]["source_reading_ref"],"C103.1")
        self.assertFalse(tasks[0]["actual_original_voice_actor_name_verified"])

    def test_no_guess_or_untimed_in_original_s09_source(self):
        rows=[row("S09E19","C099.1",None,"Hey there.")]
        rows[0]["source_original_times_ms"]=[{"start_ms":1,"end_ms":50}]
        with self.assertRaisesRegex(ValueError,"must remain untimed"):
            make_queue(rows,{},{"cues":[]},strict=False)

    def test_source_sentence_continuation_is_prioritized_without_guessing_speaker(self):
        rows=[
            row("S09E19","C266.1",None,
                "You ever make a huge mistake you knew you were going to end up regretting"),
            row("S09E19","C267.1","ROZ RUSSELL",
                "every minute for the rest of your life?"),
        ]
        tasks,report=make_queue(rows,{},{"cues":[]},strict=False)
        self.assertEqual(report["original_source_units_still_unknown"],1)
        self.assertEqual(report["possible_unknown_to_named_same_sentence_continuation_reviews"],1)
        self.assertIn("possible_same_voice_sentence_continuation_to_next_named_cue_P0",
                      tasks[0]["reasons"])
        candidate=tasks[0]["adjacent_source_sentence_continuation_candidate_not_auto_attributed"]
        self.assertEqual(candidate["next_provisional_role_not_verified"],"ROZ RUSSELL")
        self.assertIsNone(tasks[0]["model_proposed_character"])
        self.assertFalse(candidate["actual_original_audio_review_done"])
        self.assertTrue(tasks[0]["all_original_S09_caption_times_remain_null"])

    def test_new_v9_privacy_sha_required(self):
        from plan_next_speaker_review_v9 import load_private_v9
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"pilot-current-source-first-s09-audio-v9.jsonl").write_text("{}\\n","utf-8")
            (root/"pilot-current-speaker-s09-audio-v9-manifest.json").write_text("{}","utf-8")
            with self.assertRaisesRegex(ValueError,"v9 source-role ledger"):
                load_private_v9(root)

    def test_latest_v10_160_unknowns_and_original_two_source_cue_identity(self):
        from plan_next_speaker_review_v9 import load_private_v10
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"pilot-current-source-turns-v10.jsonl").write_text("{}\\n","utf-8")
            (root/"pilot-current-source-turns-v10-manifest.json").write_text("{}","utf-8")
            with self.assertRaisesRegex(ValueError,"Source-v10 original"):
                load_private_v10(root)
        rows=[
            row("S09E19","C265.1",None,"As usual."),
            row("S09E19","C266.1–C267.1","ROZ RUSSELL",
                "You ever make a huge mistake you knew you were going to end up regretting every minute for the rest of your life?"),
            row("S09E19","C268.1",None,"Yeah. I bought stock in Earthshoes."),
        ]
        rows[1]["original_source_part_refs"]=["C266.1","C267.1"]
        result,summary=make_queue(rows,{},{"cues":[]},strict=False)
        self.assertEqual(summary["original_source_units"],4)
        self.assertEqual(summary["original_units_provisionally_named"],2)
        self.assertEqual(summary["original_source_units_still_unknown"],2)
        self.assertTrue(all("C266.1" not in r["unidentified_original_unit_refs"] for r in result))

    def test_v11_original_mixed_speaker_roles_and_156_unknown_manifest_cannot_be_forged(self):
        from plan_next_speaker_review_v9 import load_private_v11
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp)
            (base/"pilot-current-multi-voice-turns-v11.jsonl").write_text("{}\\n","utf-8")
            (base/"pilot-current-multi-voice-turns-v11-manifest.json").write_text("{}","utf-8")
            with self.assertRaisesRegex(ValueError,"Source-v11 original-role"):
                load_private_v11(base)
        rows=[
            row("S09E19","C188.1:v11a","ROZ RUSSELL","short original voice"),
            row("S09E19","C188.1:v11b","CHRISTINE SULLIVAN","responding original voice"),
            row("S09E19","C189.1",None,"Still unidentified."),
        ]
        rows[0]["original_source_part_refs"]=["C188.1"]
        rows[1]["original_source_part_refs"]=["C188.1"]
        queue,summary=make_queue(rows,{},{"cues":[{"episode_id":"S09E19","original_cue":188}]},
                                 strict=False)
        self.assertEqual(summary["original_source_units"],2)
        self.assertEqual(summary["original_units_provisionally_named"],1)
        self.assertEqual(summary["original_source_units_still_unknown"],1)
        self.assertEqual(queue[0]["source_reading_ref"],"C189.1")

    def test_live_v13_handoff_source_queue_cannot_falsely_certify_actor(self):
        from plan_next_speaker_review_v9 import load_private_v13
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"pilot-source-dialogue-turns-v13.jsonl").write_text("{}\\n","utf-8")
            (root/"pilot-source-dialogue-turns-v13-manifest.json").write_text("{}","utf-8")
            with self.assertRaisesRegex(ValueError,"source-v13 private"):
                load_private_v13(root)
        rows=[
            row("S09E19","S09-C146.1-TURN-1","DAN FIELDING","Come along Harry"),
            row("S09E19","S09-C146.1-TURN-2","HARRY STONE","Yeah thanks Dan"),
            row("S09E19","C147.1",None,"A missing voice nearby"),
        ]
        rows[0]["original_source_part_refs"]=["C146.1"]
        rows[1]["original_source_part_refs"]=["C146.1"]
        q,m=make_queue(rows,{},{"cues":[{"episode_id":"S09E19","original_cue":146}]},strict=False)
        self.assertEqual(m["original_source_units"],2)
        self.assertEqual(m["original_units_provisionally_named"],1)
        self.assertEqual(m["original_source_units_still_unknown"],1)
        self.assertEqual(q[0]["source_reading_ref"],"C147.1")
        self.assertIsNone(q[0]["model_proposed_character"])

    def test_source_role_patch_review_requires_all_current_guest_paul_clues(self):
        from plan_next_speaker_review_v9 import load_private_source_patches
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            (p/"pilot-source-role-amendments.jsonl").write_text("{}\\n","utf-8")
            (p/"pilot-source-role-amendments-manifest.json").write_text("{}","utf-8")
            with self.assertRaisesRegex(ValueError,"132-UNKNOWN source patch"):
                load_private_source_patches(p)
        rows=[
            row("S09E19","C112.1","PAUL","You found the old safe"),
            row("S09E19","C113.1",None,"You knew about that book?"),
        ]
        q,summary=make_queue(rows,{},{"cues":[]},strict=False)
        self.assertEqual(summary["original_source_units"],2)
        self.assertEqual(summary["original_units_provisionally_named"],1)
        self.assertEqual(summary["original_source_units_still_unknown"],1)
        self.assertEqual(q[0]["source_reading_ref"],"C113.1")
        self.assertIsNone(q[0]["model_proposed_character"])

    def test_latest_source_turn_patch_queue_uses_only_fully_unidentified_original_cues(self):
        from plan_next_speaker_review_v9 import load_private_source_turn_patches
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"pilot-source-turn-amendments.jsonl").write_text("{}\\n","utf-8")
            (root/"pilot-source-turn-amendments-manifest.json").write_text("{}","utf-8")
            with self.assertRaisesRegex(ValueError,"130-UNKNOWN source turn"):
                load_private_source_turn_patches(root)
        rows=[
            row("S09E19","S09-DAN-102-T01","DAN FIELDING","Did you know the safe?"),
            row("S09E19","S09-HARRY-102-103","HARRY STONE","No I did not."),
            row("S09E19","S09-DAN-103-T03","DAN FIELDING","Wow."),
            row("S09E19","C104.1",None,"That is old."),
        ]
        rows[0]["original_source_part_refs"]=["C102.1"]
        rows[1]["original_source_part_refs"]=["C102.1","C103.1"]
        rows[2]["original_source_part_refs"]=["C103.1"]
        queue,m=make_queue(rows,{},{"cues":[]},strict=False)
        self.assertEqual(m["original_source_units"],3)
        self.assertEqual(m["original_units_provisionally_named"],2)
        self.assertEqual(m["original_source_units_still_unknown"],1)
        self.assertEqual(queue[0]["source_reading_ref"],"C104.1")

    def test_private_original_audio_numeric_sha_required(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"real-source.json"
            p.write_text("{}","utf-8")
            with self.assertRaisesRegex(ValueError,"Wrong S09 original-source"):
                load_s09_locator(p)

    def test_duplicate_parts_do_not_disappear_as_unknown(self):
        rows=[row("S01E01","C001.1",None,"Hello.",[{"start_ms":20,"end_ms":50}])]
        result,summary=make_queue(rows,{},{"cues":[]},strict=False)
        self.assertEqual(len(result),1)
        self.assertEqual(summary["new_speaker_names_automatically_assigned"],0)


if __name__=="__main__":
    unittest.main()
