import unittest
import tempfile
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from empty_release_dirs import validate,execute

def plan(dirs):
    return {"root":"/downloads","batch_id":"empty_release_001","description":"Remove vacated release folders only","directories":dirs}
class FakeFTP:
    def __init__(self):
        self.dirs={"/downloads","/downloads/Empty.Release","/downloads/NonEmpty.Release"}
        self.files={"/downloads/NonEmpty.Release/still.mkv":100}
        self.current="/downloads"
    def cwd(self,p):
        if p not in self.dirs:raise FileNotFoundError(p)
        self.current=p
    def mlsd(self):
        for d in sorted(self.dirs):
            if d!="/downloads" and str(Path(d).parent)==self.current:
                yield (Path(d).name,{"type":"dir"})
        for p in self.files:
            if str(Path(p).parent)==self.current:
                yield (Path(p).name,{"type":"file"})
    def rmd(self,p):
        if self.current!="/downloads":raise RuntimeError("not reset to root")
        if p in self.files:raise RuntimeError("not empty")
        self.dirs.remove(p)
class FolderRemovalTests(unittest.TestCase):
    def test_root_refused(self):
        with self.assertRaises(ValueError):validate(plan(["/downloads"]))
    def test_escape_refused(self):
        with self.assertRaises(ValueError):validate(plan(["/downloads/../outside"]))
    def test_case_duplicate_refused(self):
        with self.assertRaises(ValueError):validate(plan(["/downloads/A","/downloads/a"]))
    def test_empty_removed_nonempty_preserved(self):
        ftp=FakeFTP()
        with tempfile.TemporaryDirectory() as temp:
            removed,skipped=execute(ftp,plan(["/downloads/Empty.Release","/downloads/NonEmpty.Release"]),Path(temp)/"audit.json")
            self.assertEqual(removed,["/downloads/Empty.Release"])
            self.assertEqual(len(skipped),1)
            self.assertIn("/downloads/NonEmpty.Release",ftp.dirs)
            journal=json.loads((Path(temp)/"audit.json").read_text())
            self.assertEqual(journal["status"],"complete_with_skips")
if __name__=="__main__":unittest.main()
