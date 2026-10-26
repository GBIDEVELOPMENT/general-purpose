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
