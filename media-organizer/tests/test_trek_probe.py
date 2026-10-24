import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from trek_probe import validate
def item(path="/downloads/Star Trek/Star Trek Strange New Worlds S03E03 HDR 2160p.mkv"):
    return {"from":path,"size":1000000,"modify":"20261023093000"}
def plan(entries):
    return {"root":"/downloads","description":"Read-only HDR and DV metadata probe on exact vetted private media","targets":entries}
class ProbeTests(unittest.TestCase):
    def test_valid(self):self.assertEqual(len(validate(plan([item()]))),1)
    def test_escape(self):
        with self.assertRaises(ValueError):validate(plan([item("/downloads/../secret/file.mkv")]))
    def test_no_non_trek(self):
        with self.assertRaises(ValueError):validate(plan([item("/downloads/Other Show S01E01.mkv")]))
    def test_duplicate(self):
        with self.assertRaises(ValueError):validate(plan([item(),item()]))
    def test_requires_timestamp(self):
        x=item();x["modify"]=None
        with self.assertRaises(ValueError):validate(plan([x]))
if __name__=="__main__":unittest.main()
