#!/usr/bin/env python3
"""Offline synthetic movie-plan budget and cut-boundary regression tests."""
import copy
import unittest
from plan_fast_visual_pass import make_plan, frame_rate


def spec(fps="24", duration=1448256, window=None, cuts=None, events=None):
    return {
        "schema": "night-court-fast-visual-input/1", "episode_id": "S01E01",
        "source_video_sha256": "5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962",
        "duration_ms": duration, "avg_frame_rate": fps,
        "frame_rate_provenance": "synthetic_unverified_assumption",
        "window_ms": window or [0, duration],
        "cut_candidates": cuts or [], "activity_events": events or []
    }


class FastVisualPass(unittest.TestCase):
    def test_one_24minute_episode_is_bounded_without_full_frame_dump(self):
        s = spec()
        s["activity_events"] = [{"event_id": f"action-{i}", "time_ms": 3000 + i * 21000, "priority": 3}
                                for i in range(60)]
        s["cut_candidates"] = [{"time_ms": 8000 + i * 12000, "image_change_score": 0.5}
                                for i in range(110)]
        plan = make_plan(s)
        self.assertLessEqual(plan["counts"]["frames"], 240)
        self.assertLessEqual(plan["counts"]["bursts"], 32)
        self.assertLessEqual(plan["counts"]["transition_pairs"], 12)
        self.assertLessEqual(plan["counts"]["baseline"], 100)
        self.assertEqual(plan["source_video_sha256"], s["source_video_sha256"])
        self.assertFalse(plan["speaker_action_or_script_accepted"])
        self.assertEqual(len({f["nominal_frame_index"] for f in plan["frames"]}),
                         plan["counts"]["frames"])

    def test_cut_avoids_false_continuous_motion_and_makes_separate_pair(self):
        s = spec(duration=12000, window=[1000, 11000],
                 cuts=[{"time_ms": 5000, "image_change_score": .9}],
                 events=[{"event_id": "across", "time_ms": 5000, "priority": 5},
                         {"event_id": "safe", "time_ms": 8500, "priority": 4}])
        plan = make_plan(s)
        self.assertEqual([x["event_id"] for x in plan["motion_bursts"]], ["safe"])
        self.assertEqual(next(x["reason"] for x in plan["deferred_events"] if x["event_id"] == "across"),
                         "near_or_crosses_cut")
        pair = plan["transition_pairs"][0]
        self.assertLess(pair["frame_times_ms"][0], 5000)
        self.assertGreater(pair["frame_times_ms"][1], 5000)
        self.assertEqual(pair["relation"], "across_candidate_cut_not_continuous_motion")
        self.assertEqual(len({f["candidate_shot_partition"] for f in plan["frames"]
                              if f["evidence_event_id"] == "safe"}), 1)

    def test_adjoining_24fps_triads_retain_three_distinct_frames(self):
        s = spec(duration=3000, events=[{"event_id": "micro", "time_ms": 1500,
                                         "priority": 5, "mode": "adjacent"}])
        plan = make_plan(s)
        self.assertEqual(len(plan["motion_bursts"]), 1)
        triad = plan["motion_bursts"][0]["nominal_frame_times_ms"]
        self.assertEqual(triad, [1458, 1500, 1542])
        self.assertEqual(plan["motion_bursts"][0]["frame_count"], 3)

    def test_fractional_23976fps_no_fabricated_24fps(self):
        self.assertEqual(str(frame_rate("24000/1001")), "24000/1001")
        s = spec(fps="24000/1001", duration=6000,
                 events=[{"event_id": "gesture", "time_ms": 3000, "priority": 5}])
        plan = make_plan(s)
        self.assertEqual(plan["nominal_avg_frame_rate"], "24000/1001")
        self.assertEqual(len(plan["motion_bursts"]), 1)
        self.assertIn("not_verified", plan["frame_time_basis"])

    def test_invalid_sources_are_rejected(self):
        original = spec()
        mutations = [
            {"source_video_sha256": "f"*63},
            {"duration_ms": True},
            {"avg_frame_rate": "23.976"},
            {"avg_frame_rate": "0/0"},
            {"avg_frame_rate": "30000/1"},
            {"frame_rate_provenance": "confident_guess"},
            {"window_ms": [1000, 1000]},
            {"cut_candidates": [{"time_ms": 0, "image_change_score": 0.3}]},
            {"cut_candidates": [{"time_ms": 5000, "image_change_score": 0.3}]*2},
            {"cut_candidates": [{"time_ms": 5000, "image_change_score": float("nan")}]},
            {"activity_events": [{"event_id": "same", "time_ms": 1000, "priority": 5}]*2},
            {"activity_events": [{"event_id": "x", "time_ms": 1000, "priority": True}]}
        ]
        for patch in mutations:
            with self.subTest(patch=patch):
                mutated = copy.deepcopy(original)
                mutated.update(patch)
                with self.assertRaises((ValueError, ZeroDivisionError)):
                    make_plan(mutated)


if __name__ == "__main__":
    unittest.main()
