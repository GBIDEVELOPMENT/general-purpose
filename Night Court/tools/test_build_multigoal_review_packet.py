#!/usr/bin/env python3
"""No-media source integrity, coverage and false-acceptance tests."""
import copy
import unittest
from build_multigoal_review_packet import build,unique_coverage,GOALS


def fixture(episode):
    nine = episode=="S09E19"
    clip = {"event_id":"V01","time_window_ms_candidate_only":[900,1800],
            "selection_reason":"editorial_original_source_task",
            "candidate_shot_partition_unverified":2,
            "original_shot_and_action_human_verified":False,
            "speaking_identity_or_prosody_verified":False,
            "draft_stage_direction_accepted":False}
    result={"episode_id":episode,"original_video_sha256":"a"*64,
            "model_families" if nine else "model_independent_families":
                ["whisper","kaldi_hmm_wfst"],
            "original_video_duration_ms" if nine else
                "source_audio_video_duration_ms":1320144,
            "episode_production_script_accepted" if nine else
                "complete_production_screenplay_accepted":False}
    plan={"source_video_sha256":"a"*64,
          "source_duration_ms":1320144,
          "human_continuous_video_review_done":False,
          "full_original_episode_screenplay_accepted":False,
          "excerpt_media_decoded_or_retained":False,
          "review_requests":[clip],
          "requested_video_excerpt_count":1,
          "requested_total_video_excerpt_ms":900}
    result["shot_bounded_selective_original_video_review" if nine else
           "shot_bounded_original_video_review"]=plan
    return result


class Reviews(unittest.TestCase):
    def test_both_pilots_stay_unaccepted(self):
        for episode in ("S01E01","S09E19"):
            with self.subTest(episode=episode):
                report=build(fixture(episode))
                self.assertEqual(report["selected_window_count"],1)
                self.assertEqual(report["original_runtime_unselected_ms"],1320144-900)
                self.assertFalse(report["script_or_claim_independently_accepted"])
                row=report["requests"][0]
                self.assertEqual(set(row["goals"]),set(GOALS))
                self.assertTrue(all(v=="PENDING_ORIGINAL_AV_REVIEW"
                                    for v in row["goals"].values()))

    def test_coverage_deduplicated(self):
        self.assertEqual(unique_coverage([(10,20),(15,25),(50,60)]),25)

    def test_bad_inputs_cannot_become_acceptance(self):
        for fault in ("wrong_sha","accepted","accepted_action","bad_time",
                      "too_long","wrong_model","duplicate"):
            src=fixture("S09E19")
            p=src["shot_bounded_selective_original_video_review"]
            r=p["review_requests"][0]
            if fault=="wrong_sha":p["source_video_sha256"]="b"*64
            if fault=="accepted":src["episode_production_script_accepted"]=True
            if fault=="accepted_action":r["draft_stage_direction_accepted"]=True
            if fault=="bad_time":r["time_window_ms_candidate_only"]=[900,900]
            if fault=="too_long":
                r["time_window_ms_candidate_only"]=[100,6100]
                p["requested_total_video_excerpt_ms"]=6000
            if fault=="wrong_model":src["model_families"]=["whisper","whisper"]
            if fault=="duplicate":
                p["review_requests"].append(copy.deepcopy(r))
                p["requested_video_excerpt_count"]=2
                p["requested_total_video_excerpt_ms"]=1800
            with self.subTest(fault=fault),self.assertRaises(ValueError):
                build(src)


if __name__=="__main__":
    unittest.main()
