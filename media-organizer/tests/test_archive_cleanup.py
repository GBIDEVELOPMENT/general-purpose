import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from archive_cleanup import check
def item(s,n):return {"path":f"/downloads/Show/a.{s}","size":n,"modify":"20261023000000"}
def plan():
    return {"root":"/downloads","batch_id":"archive_001","description":"Validated extracted episode with byte parity","video":{"path":"/downloads/Show/a.mkv","size":100000000,"modify":"20261023000000"},"volumes":[item("rar",50000100),item("r00",50000100)]}
class ArchiveChecks(unittest.TestCase):
    def test_parity(self):self.assertEqual(check(plan()),100000200)
    def test_no_video(self):
        x=plan();x["video"]["size"]=0
        with self.assertRaises(ValueError):check(x)
    def test_missing_part(self):
        x=plan();x["volumes"][1]["path"]="/downloads/Show/a.r02"
        with self.assertRaises(ValueError):check(x)
    def test_unmatched_content_size(self):
        x=plan();x["volumes"][0]["size"]=25000100
        with self.assertRaises(ValueError):check(x)
    def test_unrelated_stem(self):
        x=plan();x["volumes"][1]["path"]="/downloads/Show/b.r00"
        with self.assertRaises(ValueError):check(x)
if __name__=="__main__":unittest.main()
