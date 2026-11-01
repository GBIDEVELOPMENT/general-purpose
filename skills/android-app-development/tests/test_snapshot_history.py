"""Offline tests for the bounded GitHub history inventory."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("history", HERE / "scripts" / "snapshot_history.py")
history = importlib.util.module_from_spec(spec)
spec.loader.exec_module(history)


class SnapshotTests(unittest.TestCase):
    def test_link_next_only(self):
        self.assertEqual(
            "https://api.github.com/repos/acme/repo/pulls?page=2",
            history.next_url('<https://api.github.com/repos/acme/repo/pulls?page=1>; rel="prev", <https://api.github.com/repos/acme/repo/pulls?page=2>; rel="next"'))
        self.assertIsNone(history.next_url('<https://example.com>; rel="last"'))

    def test_pagination_duplicate_fails_closed(self):
        first = "https://api.github.com/repos/test/r/pulls?page=1"
        second = "https://api.github.com/repos/test/r/pulls?page=2"
        def getter(url):
            return ([{"number": 3}], second if url == first else None)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            history.collection(first, getter)

    def test_snapshot_excludes_prs_from_issues_and_no_body(self):
        calls = []
        def getter(url):
            calls.append(url)
            if "/branches/main" in url:
                return {"commit": {"sha": "stable"}}, None
            if "/pulls?" in url:
                return [{"number": 4, "title": "Safe copy", "body": "SENSITIVE",
                         "state": "closed", "head": {"sha": "h"},
                         "base": {"sha": "b"}}], None
            return [{"number": 4, "pull_request": {}, "body": "SENSITIVE"},
                    {"number": 2, "title": "Real issue", "body": "SENSITIVE"}], None
        result = history.snapshot(["gamesbyian/Chunks"], getter)
        repo = result["repositories"]["gamesbyian/Chunks"]
        self.assertEqual((1, 1), (repo["pr_count"], repo["issue_count"]))
        self.assertEqual(2, repo["issues"][0]["number"])
        self.assertNotIn("body", str(result))
        self.assertEqual(2, len([x for x in calls if "/branches/main" in x]))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snapshot.json"
            history.atomic_write(path, result)
            self.assertIn('"pr_count": 1', path.read_text(encoding="utf-8"))

    def test_guard_api_url(self):
        with self.assertRaises(ValueError):
            history.github_get("https://example.org/capture")


if __name__ == "__main__":
    unittest.main()
