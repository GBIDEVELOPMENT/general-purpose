#!/usr/bin/env python3
"""Source-free dense original frame window constraints."""
import unittest
from capture_original_physical_beats import windows,SOURCES,SECONDARY,FPS,MAX_FRAMES_PER_WINDOW


class PhysicalReviewTargets(unittest.TestCase):
    def test_two_shorts_per_real_original_episode(self):
        for ep in ("S01E01","S09E19"):
            a=windows(ep)
            self.assertEqual(len(a),2)
            self.assertEqual(len({q[2] for q in a}),2)
            self.assertTrue(all(x[1]*FPS<=MAX_FRAMES_PER_WINDOW for x in a))
            self.assertEqual(len(SOURCES[ep][0]),64)
    def test_secondary_three_short_unoverlapped_original_story_windows(self):
        for ep in ('S01E01','S09E19'):
            selected=windows(ep,'secondary')
            self.assertEqual(len(selected),3)
            self.assertEqual(selected,SECONDARY[ep])
            self.assertEqual(sum(duration for start,duration,label in selected),60)
            self.assertEqual(len({label for start,duration,label in selected}),3)
            self.assertTrue(all(duration*FPS<=MAX_FRAMES_PER_WINDOW for start,duration,label in selected))
            self.assertTrue(all(not (a<b+duration and b<a+d) for a,d,_ in selected for b,duration,_ in windows(ep)))
        with self.assertRaises(ValueError):windows('S01E01','unknown')

    def test_tamper_and_wrong_episode_rejected(self):
        with self.assertRaises(ValueError):windows("S09E22")
        a=SOURCES["S09E19"][1]
        try:
            a.append((1200,50,"unsafe"))
            with self.assertRaises(ValueError):windows("S09E19")
        finally:a.pop()


if __name__=="__main__":
    unittest.main()
