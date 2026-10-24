#!/usr/bin/env python3
"""No-credentials/no-media scheduler regression tests."""
import threading
import time
import unittest
from source_once_av_lanes import run_av_lanes


class SourceOnceLaneTests(unittest.TestCase):
    def test_serial_is_ordered_and_never_claims_review(self):
        order = []
        result = run_av_lanes(lambda: order.append("audio") or {"heard": False},
                              lambda: order.append("video") or {"watched": False})
        self.assertEqual(order, ["audio", "video"])
        self.assertEqual(result.audio, {"heard": False})
        self.assertEqual(result.visual, {"watched": False})
        self.assertEqual(result.mode, "serial")

    def test_parallel_really_starts_both_lanes(self):
        barrier = threading.Barrier(2, timeout=2)
        def work(name):
            barrier.wait()
            time.sleep(0.025)
            return {"lane": name}
        result = run_av_lanes(lambda: work("audio"), lambda: work("visual"),
                              mode="parallel")
        self.assertEqual(result.audio["lane"], "audio")
        self.assertEqual(result.visual["lane"], "visual")
        self.assertGreater(result.overlapped_seconds, 0)
        self.assertLess(result.elapsed_seconds, result.audio_lane_seconds +
                        result.visual_lane_seconds)

    def test_exceptions_propagate_no_fake_success(self):
        def fail():
            raise RuntimeError("bad original evidence")
        with self.assertRaisesRegex(RuntimeError, "bad original evidence"):
            run_av_lanes(fail, lambda: {}, mode="parallel")

    def test_no_accidental_unbounded_workers(self):
        with self.assertRaises(ValueError):
            run_av_lanes(lambda: {}, lambda: {}, mode="gpu-unbounded")
        with self.assertRaises(ValueError):
            run_av_lanes(None, lambda: {})


if __name__ == "__main__":
    unittest.main()
