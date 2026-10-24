import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from apply_batch import plan_validate, execute
def plan(moves):
    return {"root":"/downloads","batch_id":"batch_0001",
      "description":"Plex naming only, no media content touched","moves":moves}
def op(src="/downloads/S.S01E01.mkv",dst="/downloads/S/Season 01/S - S01E01.mkv"):
    return {"from":src,"to":dst,"size":100,"modify":"20261023000000","reason":"Plex episode grouping"}
class BatchSafetyTests(unittest.TestCase):
    def test_valid(self):self.assertEqual(len(plan_validate(plan([op()]))),1)
    def test_path_escape(self):
        with self.assertRaises(ValueError):plan_validate(plan([op(dst="/downloads/../other/S - S01E01.mkv")]))
    def test_no_extension_change(self):
        with self.assertRaises(ValueError):plan_validate(plan([op(dst="/downloads/S/S - S01E01.avi")]))
    def test_no_episode_loss(self):
        with self.assertRaises(ValueError):plan_validate(plan([op(dst="/downloads/S/Filename.mkv")]))
    def test_no_duplicate_destinations(self):
        with self.assertRaises(ValueError):plan_validate(plan([op(),op(src="/downloads/S.S01E02.mkv")]))
    def test_no_move_chains(self):
        with self.assertRaises(ValueError):plan_validate(plan([op(),op(src="/downloads/S/Season 01/S - S01E01.mkv",dst="/downloads/Else/Other - S01E01.mkv")]))
    def test_no_unapproved_metadata(self):
        x=op();x["ignore"]=True
        with self.assertRaises(ValueError):plan_validate(plan([x]))
if __name__=="__main__":unittest.main()
