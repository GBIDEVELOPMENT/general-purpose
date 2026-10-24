import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plexmatch_upload import validate,contents
def item():
    return {"directory":"/downloads/Example.Show.S01","show":"Example Show",
    "year":2006,"season":1,"episodes":[{"number":1,"filename":"ex-s01e01.avi","size":365000,"modify":"20261001000000"}]}
class PlexmatchTests(unittest.TestCase):
    def test_hint_format(self):
        e=item();validate({"batch_id":"studio_pilot","entries":[e]})
        self.assertIn(b"ep: S01E01: ex-s01e01.avi",contents(e))
    def test_duplicate_episode_rejected(self):
        e=item();e["episodes"].append(dict(e["episodes"][0]))
        with self.assertRaises(ValueError):validate({"batch_id":"studio_pilot","entries":[e]})
    def test_remote_path_escape_rejected(self):
        e=item();e["directory"]="/downloads/../outside"
        with self.assertRaises(ValueError):validate({"batch_id":"studio_pilot","entries":[e]})
    def test_script_name_rejected(self):
        e=item();e["episodes"][0]["filename"]="bad; rm -rf /"
        with self.assertRaises(ValueError):validate({"batch_id":"studio_pilot","entries":[e]})
if __name__=="__main__":unittest.main()
