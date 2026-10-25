#!/usr/bin/env python3
"""Cheap original-AVI lexical-to-image review search with no fake paragraph timestamps."""
import unittest
from plan_s09e19_coarse_picture_dialogue_review import (
    read_original_anchors,propose,render,EXPECTED_DISTINCT_PROBES)

class CoarseReview(unittest.TestCase):
    def test_anchored_source_matches_and_real_original_image_counts(self):
        anchors,source_sha=read_original_anchors()
        self.assertEqual(len(anchors),EXPECTED_DISTINCT_PROBES)
        self.assertEqual(len(source_sha),64)
        report,markdown=render()
        self.assertEqual(report["source_original_untimed_paragraph_count"],347)
        self.assertFalse(report["source_paragraph_original_timestamps_created"])
        self.assertTrue(report["ASR_consensus_is_not_original_audio_listening_verification"])
        self.assertEqual(report["counts"]["original_reviewed_still_notes"],16)
        self.assertEqual(report["counts"]["original_reviewed_motion_sequences"],2)
        self.assertEqual(report["counts"]["total_picture_editorial_review_events"],18)
        self.assertEqual(report["counts"]["review_pointers_with_approximate_paragraph"]+
                         report["counts"]["source_picture_events_deferred_without_interpolation"],18)
        self.assertIn("ABSTAIN",markdown)
        self.assertIn("UNTIMED",markdown)
        self.assertEqual((report,markdown),render())

    def test_model_agreement_never_creates_original_source_times(self):
        report,_=render()
        for event in report["original_picture_search_proposals"]:
            proposal=event["paragraph_search"]
            self.assertIsNone(proposal["paragraph_original_timecode_ms"])
            if proposal["candidate_approx_source_paragraph"] is not None:
                self.assertFalse(proposal["original_audio_soundtrack_listened_to_validate"])
                self.assertFalse(proposal["speaker_and_scene_crossmodal_verified"])
                left,right=proposal["possible_paragraph_bracket"]
                self.assertLessEqual(left,proposal["candidate_approx_source_paragraph"])
                self.assertLessEqual(proposal["candidate_approx_source_paragraph"],right)
        anchors,_=read_original_anchors()
        self.assertIsNone(propose(9000,anchors)["candidate_approx_source_paragraph"])
        self.assertIsNone(propose(1300000,anchors)["candidate_approx_source_paragraph"])

    def test_refuse_unbounded_original_positions(self):
        anchors,_=read_original_anchors()
        with self.assertRaises(ValueError):propose(-1,anchors)
        with self.assertRaises(ValueError):propose(1600000,anchors)

if __name__=="__main__":
    unittest.main()
