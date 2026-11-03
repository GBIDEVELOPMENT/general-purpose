"""Sanitized tracker counters: no endpoint URL exposure."""
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from tracker_analysis import FIELDS, sanitize_tracker_rows

class TestTrackerAnalysis(unittest.TestCase):
    def test_sanitization_and_truncation(self):
        rows = [[1,0,287,1,0,1,0,1793745618,1],
                [1,0,0,0,0,0,0,0,1],
                [0,2,4,3,10,5,1700000000,1700001000,2]]
        r=sanitize_tracker_rows(rows, server="primary", infohash="A"*40,
                                name="Example",limit=2)
        self.assertEqual(r["tracker_count"],3)
        self.assertEqual(len(r["trackers"]),2)
        self.assertTrue(r["truncated"])
        self.assertEqual(r["trackers"][0]["successful_requests_recorded"],287)
        self.assertIsNone(r["trackers"][1]["scrape_seed_count"])
        self.assertTrue(all("url" not in key.lower() for entry in r["trackers"] for key in entry))
        self.assertEqual(len(FIELDS),9)

    def test_invalid_tracker_rows_refused(self):
        cases = [None,["bad"],[[1]*8],[[1,-1,0,0,0,0,0,0,1]],[[1,1,1,1,1,1,1,1,"NaN"]]]
        for case in cases:
            with self.subTest(case=case),self.assertRaises(ValueError):
                sanitize_tracker_rows(case,server="primary",infohash="A"*40,name="Example")
        with self.assertRaises(ValueError):
            sanitize_tracker_rows([],server="primary",infohash="A"*40,name="Example",limit=0)

    def test_empty_tracker_inventory(self):
        r=sanitize_tracker_rows([],server="primary",infohash="A"*40,name="Example")
        self.assertEqual(r["tracker_count"],0)
        self.assertEqual(r["trackers"],[])
if __name__=="__main__":
    unittest.main()
