import unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from folder_plan import plan
def inv(*paths):
    return {"files":[{"path":p,"size":100} for p in paths],"failures":[],"truncated":[]}
class FolderPlanTests(unittest.TestCase):
    def test_keeps_movies_in_mixed_root(self):
        p=plan(inv("/downloads/A.Movie.1998.mkv"))
        self.assertEqual(p["suggested_folder_moves"],[])
        self.assertEqual(len(p["review"]),1)
    def test_suggests_tv_season_folder(self):
        p=plan(inv("/downloads/Show.Name.S01E01.mkv"))
        self.assertEqual(p["suggested_folder_moves"][0]["to"],"/downloads/Show Name/Season 01/Show Name - S01E01.mkv")
    def test_preserves_existing_series_home(self):
        p=plan(inv("/downloads/Comedy/Show Name/Show.Name.S01E01.mkv"))
        self.assertEqual(p["suggested_folder_moves"][0]["to"],"/downloads/Comedy/Show Name/Season 01/Show Name - S01E01.mkv")
    def test_attaches_language_sidecar(self):
        p=plan(inv("/downloads/Show.Name.S01E01.mkv","/downloads/Show.Name.S01E01.en.srt"))
        self.assertIn("/downloads/Show Name/Season 01/Show Name - S01E01.en.srt",[x["to"] for x in p["suggested_folder_moves"]])
    def test_unpaired_subtitle_is_held(self):
        p=plan(inv("/downloads/Show.Name.S01E01.en.srt"))
        self.assertEqual(p["suggested_folder_moves"],[])
        self.assertTrue(p["review"])
    def test_multi_episode_held(self):
        p=plan(inv("/downloads/Show.S01E01E02.mkv"))
        self.assertEqual(p["suggested_folder_moves"],[])
    def test_incomplete_scan_marked(self):
        a=inv("/downloads/Show.S01E01.mkv");a["truncated"]=["/downloads/Other"]
        self.assertTrue(plan(a)["incomplete_scan"])
if __name__=="__main__":unittest.main()
