"""Deterministic, credential-free analysis regression tests."""
import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from inventory_analysis import analyze, compare

def record(h, size, *, complete=True, active=True, ratio=1.0, rate=0, started=1700000000):
    return {
        "hash": h * 40, "name": "record " + h, "size_bytes": size,
        "downloaded_bytes": size if complete else 0,
        "uploaded_bytes": int(size*ratio),
        "ratio": ratio, "active": active, "started": active,
        "complete": complete, "down_bytes_per_sec": rate,
        "up_bytes_per_sec": 0, "first_started_at": started,
        "finished_at": started if complete else None,
    }

class TestAnalysis(unittest.TestCase):
    def test_empty_inventory(self):
        result = analyze([], "primary", now=1800000000)
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["logical_size_bytes"], 0)
        self.assertEqual(result["retention_review"], [])

    def test_placeholder_and_incomplete_are_not_cleanup_candidates(self):
        rows = [record("a", 1, complete=False),
                record("b", 1000, complete=False),
                record("c", 2000, ratio=0.5),
                record("d", 3000, ratio=2.0)]
        result = analyze(rows, "primary", now=1800000000)
        self.assertEqual(result["metadata_placeholder_count"], 1)
        self.assertEqual(result["incomplete_zero_download_rate_count"], 2)
        self.assertEqual(result["complete_below_target_ratio_count"], 1)
        self.assertEqual([r["hash"] for r in result["retention_review"]], ["d"*40])

    def test_boundaries_and_truncation(self):
        with self.assertRaises(ValueError):
            analyze([], "primary", limit=0)
        with self.assertRaises(ValueError):
            analyze([], "primary", target_ratio=-1)
        rows = [record(str(i), i+10, ratio=3) for i in range(3)]
        result = analyze(rows, "primary", limit=1, now=1800000000)
        self.assertTrue(result["truncated"]["retention_review"])
        self.assertEqual(result["complete_meeting_target_ratio_count"], 3)
        self.assertEqual(result["retention_review"][0]["recorded_start_age_seconds"], 100000000)

    def test_compare_exact_hash_not_filename_and_partial_failures(self):
        a = record("a", 100)
        b = record("b", 1000)
        another = dict(a, name="a completely different label")
        result = compare({"primary":[a, b], "second":[another]}, {"third":"gateway unavailable"})
        self.assertEqual(result["duplicate_infohash_group_count"], 1)
        self.assertEqual(len(result["duplicate_infohash_groups"][0]), 2)
        self.assertIn("third", result["errors"])
        self.assertEqual(result["configured_or_checked_servers"], 3)

    def test_compare_same_server_does_not_create_cross_server_duplicate(self):
        a=record("a", 100)
        result=compare({"primary":[a,a]})
        self.assertEqual(result["duplicate_infohash_group_count"], 0)

if __name__ == "__main__":
    unittest.main()
