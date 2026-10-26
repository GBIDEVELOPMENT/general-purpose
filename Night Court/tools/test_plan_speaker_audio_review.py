#!/usr/bin/env python3
"""Synthetic checks for private source-speaker listening plan and secure extract."""
from __future__ import annotations
import copy
import tempfile
import unittest
from pathlib import Path

from plan_speaker_audio_review import (
    PLAN_SCHEMA, QUEUE_SCHEMA, build_plan, extract_private_audio,
    sha256_stream, validate_queue
)


def row(ep: str, ref: str, score: int, times: tuple[int,int] | None):
    return {
        "schema":QUEUE_SCHEMA, "episode_id":ep,
        "source_ref":ref,"priority_score":score,
        "editorial_acceptance":"P0_P1_REVIEW_REQUIRED",
        "review_srt_window": (
            {"srt_approx_start_ms":times[0],"srt_approx_end_ms":times[1],
             "is_verified_audio_alignment":False} if times else None),
        "original_soundtrack_reviewed":False,"proposed_character":None
    }


class SpeakerAudioBundleTests(unittest.TestCase):
    def test_prioritize_and_coalesce_into_short_windows(self):
        rows=[
            row("S01E01","C010.1",35,(1000,2000)),
            row("S01E01","C011.1",33,(2600,3200)),
            row("S01E01","C100.1",18,(90000,92500)),
            row("S09E19","C040.1",37,None)
        ]
        plan=build_plan(rows,max_clips=2,context_ms=1800)
        self.assertEqual(plan["schema"],PLAN_SCHEMA)
        self.assertEqual(plan["selected_clip_count"],2)
        self.assertEqual(plan["deferred_untimed_s09_items"],1)
        self.assertEqual(plan["source_review_items_selected"],3)
        self.assertTrue(any(c["source_refs"]==["C010.1","C011.1"] for c in plan["clip_list"]))
        self.assertTrue(all(c["duration_ms"]<=18000 for c in plan["clip_list"]))
        self.assertTrue(all(not c["speaker_identity_audio_verified"] for c in plan["clip_list"]))

    def test_s09_cannot_have_invented_source_time(self):
        rows=[row("S09E19","C001.1",30,(10000,12000))]
        with self.assertRaisesRegex(ValueError,"invented"):
            validate_queue(rows)

    def test_source_proposal_cannot_claim_verified_audio(self):
        rows=[row("S01E01","C010.1",30,(1000,2000))]
        rows[0]["original_soundtrack_reviewed"]=True
        with self.assertRaisesRegex(ValueError,"falsely certified"):
            validate_queue(rows)

    def test_bounded_clips_and_long_context_deferred(self):
        rows=[row("S01E01","C020.1",70,(1000,25000))]
        p=build_plan(rows,max_clips=1)
        self.assertFalse(p["clip_list"])
        self.assertEqual(p["deferred"][0]["reason"],"unabridged_source_context_exceeds_18_second_cap")
        with self.assertRaises(ValueError):
            build_plan(rows,max_clips=100)

    def test_wrong_source_sha_refuses_soundtrack_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            movie=root/"wrong.avi"
            movie.write_bytes(b"fictional media not the pilot film")
            plan=build_plan([row("S01E01","C010.1",30,(1000,2100))])
            self.assertEqual(sha256_stream(movie),__import__("hashlib").sha256(movie.read_bytes()).hexdigest())
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                extract_private_audio(plan,movie,root/"wav")

    def test_no_duplicate_review_targets(self):
        r=row("S01E01","C020.1",22,(4000,5000))
        with self.assertRaisesRegex(ValueError,"Repeated"):
            build_plan([r,copy.deepcopy(r)])


if __name__=="__main__":
    unittest.main()
