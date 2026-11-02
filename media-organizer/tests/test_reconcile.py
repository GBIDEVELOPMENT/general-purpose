import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reconcile import compare

def plan():
    return {"root":"/downloads","batch_id":"media_0001","moves":[{"from":"/downloads/Original/Show.S01E01.mkv","to":"/downloads/Show/Season 01/Show - S01E01.mkv","size":100}]}
def inv(*items):
    return {"root":"/downloads","files":[{"path":path,"size":size} for path,size in items],"failures":[],"truncated":[]}
class IndependentMoveReconciliationTests(unittest.TestCase):
    def status(self,inventory):return compare(inventory,plan())["records"][0]["status"]
    def test_confirmed_target(self):
        self.assertEqual(self.status(inv(("/downloads/Show/Season 01/Show - S01E01.mkv",100))),"moved")
    def test_source_still_present(self):
        self.assertEqual(self.status(inv(("/downloads/Original/Show.S01E01.mkv",100))),"not_moved")
    def test_both_paths_is_not_success(self):
        self.assertEqual(self.status(inv(("/downloads/Original/Show.S01E01.mkv",100),("/downloads/Show/Season 01/Show - S01E01.mkv",100))),"both_present")
    def test_mismatched_bytes(self):
        self.assertEqual(self.status(inv(("/downloads/Show/Season 01/Show - S01E01.mkv",99))),"destination_size_mismatch")
    def test_missing_paths(self):
        self.assertEqual(self.status(inv()),"neither_found")
    def test_truncated_scan_not_authoritative(self):
        d=inv();d["truncated"]=["/downloads/Original"]
        self.assertFalse(compare(d,plan())["authoritative"])
    def test_folder_move_expands_to_exact_child_paths(self):
        document={"root":"/downloads","batch_id":"trek_folders_test",
                  "trek_folder_moves":[{"from":"/downloads/Star Trek Test",
                                        "to":"/downloads/Star Trek/Star Trek Test",
                                        "files":[{"name":"S01E01.mkv","size":100},
                                                 {"name":"S01E02.mkv","size":200}]}]}
        catalog=inv(("/downloads/Star Trek/Star Trek Test/S01E01.mkv",100),
                    ("/downloads/Star Trek/Star Trek Test/S01E02.mkv",200))
        report=compare(catalog,document)
        self.assertEqual(report["counts"],{"moved":2})
        self.assertTrue(report["authoritative"])
        self.assertEqual(report["total_moves"],2)
if __name__=="__main__":unittest.main()
