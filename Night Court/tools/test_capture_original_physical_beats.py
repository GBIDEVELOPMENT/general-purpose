#!/usr/bin/env python3
"""Source-free dense original frame window constraints."""
import unittest
from capture_original_physical_beats import windows,SOURCES,FPS,MAX_FRAMES_PER_WINDOW


class PhysicalReviewTargets(unittest.TestCase):
    def test_two_shorts_per_real_original_episode(self):
        for ep in ("S01E01","S09E19"):
            a=windows(ep)
            self.assertEqual(len(a),2)
            self.assertEqual(len({q[2] for q in a}),2)
            self.assertTrue(all(x[1]*FPS<=MAX_FRAMES_PER_WINDOW for x in a))
            self.assertEqual(len(SOURCES[ep][0]),64)
    def test_tamper_and_wrong_episode_rejected(self):
        with self.assertRaises(ValueError):windows("S09E22")
        a=SOURCES["S09E19"][1]
        try:
            a.append((1200,50,"unsafe"))
            with self.assertRaises(ValueError):windows("S09E19")
        finally:a.pop()


if __name__=="__main__":
    unittest.main()
