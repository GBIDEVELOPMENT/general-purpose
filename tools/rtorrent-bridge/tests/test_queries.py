"""Offline regression tests for filtered queries and peer diagnostics."""
import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from torrent_queries import HEALTH_FIELDS, explain_health, select_page

def item(h, name, size, ratio, *, active=True, complete=True, started=None):
    return {
        "hash": h*40, "name": name, "size_bytes": size, "ratio": ratio,
        "uploaded_bytes": 0, "downloaded_bytes": 0,
        "down_bytes_per_sec": 0, "up_bytes_per_sec": 0,
        "active": active, "complete": complete, "first_started_at": started,
    }

class TestQueries(unittest.TestCase):
    def setUp(self):
        self.rows = [
            item("a","Alpha",100,0.1,started=200),
            item("b","alpha 2",100,2.0,started=None),
            item("c","Beta",300,2.5,active=False,complete=False,started=100)
        ]

    def test_page_stable_and_filters(self):
        a=select_page(self.rows, sort_by="size", descending=True, limit=1)
        self.assertEqual(a["torrents"][0]["hash"], "c"*40)
        self.assertEqual(a["next_offset"],1)
        b=select_page(list(reversed(self.rows)),sort_by="size",descending=True,offset=1,limit=2)
        self.assertEqual([r["hash"] for r in b["torrents"]], ["a"*40,"b"*40])
        c=select_page(self.rows, query="ALPHA",complete=True,min_ratio=1.0)
        self.assertEqual(c["matching"],1)
        self.assertEqual(c["torrents"][0]["hash"], "b"*40)
        self.assertEqual(select_page(self.rows, active=False)["matching"],1)

    def test_unknown_times_last_and_pagination_errors(self):
        a=select_page(self.rows,sort_by="first_started",descending=True)
        self.assertEqual([r["hash"] for r in a["torrents"]],["a"*40,"c"*40,"b"*40])
        for kw in ({"limit":0},{"offset":-1},{"sort_by":"doSomethingDangerous"},
                   {"min_ratio":-1},{"query":"x"*257}):
            with self.assertRaises(ValueError):
                select_page(self.rows,**kw)

    def test_health_keeps_diagnostics_limited_and_cautious(self):
        row=item("a","Alpha",1,0,complete=False)
        fields=["a"*40,0,0,1,3,0,1,"leech"]
        result=explain_health(row,fields)
        self.assertEqual(result["peers_connected"],0)
        self.assertEqual(result["tracker_entry_count"],3)
        self.assertTrue(any("placeholder" in s for s in result["observations"]))
        self.assertFalse("tracker_url" in result)
        self.assertEqual(len(fields),len(HEALTH_FIELDS))
        with self.assertRaises(ValueError):
            explain_health(row,["b"*40]+fields[1:])
        with self.assertRaises(ValueError):
            explain_health(row,fields[:2])

if __name__ == "__main__":
    unittest.main()
