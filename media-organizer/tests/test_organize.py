import unittest, importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("organize",Path(__file__).resolve().parents[1]/"organize.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class OrganizerTests(unittest.TestCase):
    def test_path_guard(self):
        for p in ("/etc/passwd","/downloads/../other","/downloads/a\\b"):
            with self.assertRaises(ValueError):m.safe(p)
    def test_episode_candidate(self):
        inventory={"files":[{"path":"/downloads/Comedy.Show.S1E2.720p.mkv","size":15}],"failures":[]}
        result=m.propose(inventory)
        self.assertEqual(result["moves"][0]["to"],"/downloads/Comedy Show - S01E02.mkv")
    def test_no_ambiguous_movie_rename(self):
        inventory={"files":[{"path":"/downloads/Some.Movie.1999.mkv","size":1}],"failures":[]}
        self.assertEqual(m.propose(inventory)["moves"],[])
if __name__=="__main__":unittest.main()
