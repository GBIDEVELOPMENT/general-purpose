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
    def test_reject_nonmatching_parity(self):
        x=plan();x["video"]["size"]=x["video"]["size"]+2000000
        with self.assertRaises(ValueError):check(x)
    def test_unrelated_stem(self):
        x=plan();x["volumes"][1]["path"]="/downloads/Show/b.r00"
        with self.assertRaises(ValueError):check(x)

    def test_exact_six_reviewed_extracted_tv_archive_sets(self):
        import json
        approved=json.loads(Path("media-organizer/approved-archive-delete.json").read_text())
        self.assertEqual(len(approved["groups"]),6)
        self.assertEqual(sum(len(g["volumes"]) for g in approved["groups"]),257)
        self.assertEqual(sum(check(g) for g in approved["groups"]),31363601389)
        self.assertEqual(sum(g["video"]["path"].endswith(".iso") for g in approved["groups"]),2)
        self.assertTrue(all("/Poker Face/" in g["video"]["path"] or "/The.Durrells." in g["video"]["path"] for g in approved["groups"]))
        self.assertTrue(all(g["video"]["path"] not in {f["path"] for f in g["volumes"]} for g in approved["groups"]))
    def test_dvd_disc_iso_accepted_only_with_tv_disc_identity(self):
        import json,copy
        approved=json.loads(Path("media-organizer/approved-archive-delete.json").read_text())
        disc=next(g for g in approved["groups"] if g["video"]["path"].endswith(".iso"))
        self.assertGreater(check(disc),0)
        wrong=copy.deepcopy(disc)
        wrong["video"]["path"]=wrong["video"]["path"].replace("s01d01","s01d02")
        with self.assertRaises(ValueError):check(wrong)
        wrong=copy.deepcopy(disc)
        wrong["video"]["path"]=wrong["video"]["path"].replace("The.Durrells.S01D01","Video.Game.Release")
        with self.assertRaises(ValueError):check(wrong)
    def test_reject_duplicated_volume_or_missing_timestamp(self):
        import json,copy
        group=json.loads(Path("media-organizer/approved-archive-delete.json").read_text())["groups"][0]
        bad=copy.deepcopy(group)
        bad["volumes"][1]["path"]=bad["volumes"][0]["path"]
        with self.assertRaises(ValueError):check(bad)
        bad=copy.deepcopy(group)
        bad["video"]["modify"]=None
        with self.assertRaises(ValueError):check(bad)

if __name__=="__main__":unittest.main()
