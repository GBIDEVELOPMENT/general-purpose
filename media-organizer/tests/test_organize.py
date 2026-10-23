import unittest, importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("organize",Path(__file__).resolve().parents[1]/"organize.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def inventory(*names):
    return {"files":[{"path":name,"size":15} for name in names],"failures":[],"truncated":[]}
class OrganizerTests(unittest.TestCase):
    def test_path_guard(self):
        for p in ("/etc/passwd","/downloads/../other","/downloads/a\\b","/downloads/file\x00.mkv"):
            with self.assertRaises(ValueError):m.safe(p)
    def test_episode_candidate(self):
        result=m.propose(inventory("/downloads/Comedy.Show.S1E2.720p.mkv"))
        self.assertEqual(result["moves"][0]["to"],"/downloads/Comedy Show - S01E02.mkv")
    def test_parent_title_inference(self):
        result=m.propose(inventory("/downloads/Night Court/Season 1/S01E01.mkv"))
        self.assertEqual(result["moves"][0]["to"],"/downloads/Night Court/Season 1/Night Court - S01E01.mkv")
    def test_sidecar_language_not_episode_title(self):
        result=m.propose(inventory("/downloads/Comedy.Show.S1E2.en.forced.srt"))
        self.assertEqual(result["moves"][0]["to"],"/downloads/Comedy Show - S01E02.en.forced.srt")
    def test_no_ambiguous_movie_rename(self):
        self.assertEqual(m.propose(inventory("/downloads/Some.Movie.1999.mkv"))["moves"],[])
    def test_multi_episode_quarantined(self):
        result=m.propose(inventory("/downloads/Comedy.Show.S01E01E02.mkv"))
        self.assertEqual(result["moves"],[])
        self.assertEqual(result["review"][0]["reason"],"Multi-episode file requires review")
    def test_collision_quarantined(self):
        result=m.propose(inventory("/downloads/Comedy.Show.S1E2.mkv","/downloads/Comedy Show - S01E02.mkv"))
        self.assertEqual(result["moves"],[])
        self.assertEqual(result["review"][0]["reason"],"Destination collision")
    def test_depth_limit_is_reported(self):
        class FakeFTP:
            def cwd(self,p):self.path=p
            def mlsd(self):return iter([("nested",{"type":"dir"})]) if self.path=="/downloads" else iter([])
        result=m.scan(FakeFTP(),max_depth=0)
        self.assertEqual(result["truncated"],["/downloads/nested"])
if __name__=="__main__":unittest.main()
