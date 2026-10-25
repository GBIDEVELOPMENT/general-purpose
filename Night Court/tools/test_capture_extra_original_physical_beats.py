#!/usr/bin/env python3
"""Additional original-Night-Court action sampling must remain fast and bounded."""
import unittest
import capture_original_physical_beats as original
from capture_extra_original_physical_beats import configure,PASSES,PREVIOUS

class OriginalExtraSceneSamples(unittest.TestCase):
    def test_source_sha_fps_budget_and_nonoverlap(self):
        verified={"S01E01":"5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962",
                  "S09E19":"51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649"}
        for ep in sorted(PASSES):
            with self.subTest(ep=ep):
                digest,windows=configure(ep)
                self.assertEqual(digest,verified[ep])
                self.assertEqual(len(windows),3)
                self.assertEqual(sum(n for start,n,label in windows),60)
                self.assertEqual(original.FPS,5)
                self.assertTrue(all(n*original.FPS<=original.MAX_FRAMES_PER_WINDOW for _,n,_ in windows))
                self.assertEqual(windows,original.windows(ep))
                self.assertEqual(configure(ep),(digest,windows))
                for start,n,label in windows:
                    self.assertGreaterEqual(start,0)
                    self.assertTrue(label)
                    self.assertTrue(all(start+n<=prev or start>=prev+length
                                        for prev,length,_ in PREVIOUS[ep]))
    def test_extra_windows_target_actual_caption_motion_situations(self):
        s={label for start,n,label in PASSES["S01E01"]}
        self.assertIn("judge-ear-coin-conjuring",s)
        self.assertIn("opening-painter-window-business",s)
        self.assertIn("double-headed-coin-kerr-reconciliation",s)
        t={label for start,n,label in PASSES["S09E19"]}
        self.assertIn("restaurant-two-impostors-entry",t)
        self.assertIn("hidden-safe-final-reveal",t)
        self.assertIn("hidden-safe-combination-and-warning",t)

if __name__=="__main__":unittest.main()
