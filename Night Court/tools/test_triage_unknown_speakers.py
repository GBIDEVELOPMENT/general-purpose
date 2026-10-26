#!/usr/bin/env python3
"""Offline unknown-speaker queue prioritization and no false attribution tests."""
import unittest
from triage_unknown_speakers import rank_unknowns, SCHEMA


def sample(i, ep, role, text, ref=None, span=None):
    return {
        "episode_id": ep, "candidate_role": role,
        "caption_text": text,
        "source_reading_ref": ref or f"C{i:03d}.1",
        "original_source_part_refs": [ref or f"C{i:03d}.1"],
        "reading_block_id": f"{ep}:source:{i:03d}",
        "original_source_sha256": "a"*64,
        "role_attribution_status": "unidentified" if role is None else "provisional_not_original_audio_verified",
        "source_original_times_ms": span,
        "original_source_untimed": span is None,
    }


class SpeakerTriageTests(unittest.TestCase):
    def test_short_continuation_unknown_comes_before_long_speech(self):
        rows=[
            sample(1,"S01E01","HARRY STONE","I was talking to",span=[{"start_ms":0,"end_ms":200}]),
            sample(2,"S01E01",None,"...you.",span=[{"start_ms":200,"end_ms":350}]),
            sample(3,"S01E01","DAN FIELDING","Oh.",span=[{"start_ms":400,"end_ms":500}]),
            sample(4,"S01E01",None,"A longer statement should remain an unidentified original speaker even if it is next to a named one in a working draft.",span=[{"start_ms":750,"end_ms":1400}]),
        ]
        queue,summary=rank_unknowns(rows,[],require_full=False)
        self.assertEqual(summary["source_units_unidentified"],2)
        self.assertEqual(summary["automatically_accepted_new_names"],0)
        self.assertEqual(queue[0]["source_ref"],"C002.1")
        self.assertIsNone(queue[0]["proposed_character"])
        self.assertIsNotNone(queue[0]["review_srt_window"])
        self.assertEqual(queue[0]["review_srt_window"]["srt_approx_start_ms"],0)
        self.assertFalse(queue[0]["review_srt_window"]["is_verified_audio_alignment"])
        self.assertIn("syntactic_continuation_possible",queue[0]["triage_triggers"])

    def test_untimed_s09_never_invents_time_or_character(self):
        a=sample(10,"S09E19",None,"What now?")
        q,summary=rank_unknowns([a],[],require_full=False)
        self.assertIsNone(q[0]["review_srt_window"])
        self.assertTrue(q[0]["original_untimed"])
        self.assertIsNone(q[0]["proposed_character"])

    def test_false_provisional_label_flag_is_separate_from_unknown_count(self):
        known=sample(28,"S01E01","BULL SHANNON","Bye, Bull.")
        flagged=[{"episode_id":"S01E01","source_ref":"C028.1",
                  "current_provisional_role":"BULL SHANNON",
                  "reason":"Possibly addresses someone else"}]
        q,m=rank_unknowns([known],flagged,require_full=False)
        self.assertEqual(m["source_units_unidentified"],0)
        self.assertEqual(m["suspected_existing_wrong_labels"],1)
        self.assertEqual(q[0]["priority_score"],40)
        self.assertEqual(q[0]["editorial_acceptance"],"P1_POTENTIAL_FALSE_POSITIVE_REVIEW_REQUIRED")
        self.assertIsNone(q[0]["proposed_character"])


if __name__=="__main__":
    unittest.main()
