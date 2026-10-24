import json,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from trek_dedupe import validate,execute,info

A="/downloads/Star Trek/Star Trek Strange New Worlds S03E03 HDR 2160p/Star Trek Strange New Worlds S03E03 HDR 2160p.mkv"
B="/downloads/Star Trek/Star Trek Strange New Worlds S03E03 DV 2160p/Star Trek Strange New Worlds S03E03 DV 2160p.mkv"
def plan(retain=A,delete=B):
    item=lambda p:{"from":p,"size":200,"modify":"20261023020000"}
    return {"root":"/downloads","batch_id":"trek_review_001","description":"Keep compatible HDR and delete DV-only duplicate after exact FTP inspection",
            "groups":[{"show":"strange_new_worlds","season":"03","episode":"03","retain":item(retain),"delete":[item(delete)],"reason":"Retain HDR 2160p candidate instead of a DV-only 2160p video"}]}
class FakeFTP:
    def __init__(self):
        self.files={A:{"type":"file","size":"200","modify":"20261023020000"},B:{"type":"file","size":"200","modify":"20261023020000"}}
        self.current=None;self.removed=[]
    def cwd(self,path):self.current=path
    def mlsd(self):
        return ((Path(p).name,facts) for p,facts in self.files.items() if str(Path(p).parent)==self.current)
    def delete(self,path):
        self.removed.append(path);self.files.pop(path)
class Tests(unittest.TestCase):
    def test_valid_pair(self):self.assertEqual(len(validate(plan())),1)
    def test_reject_enterprise_title_false_match(self):
        path="/downloads/Star Trek Enterprise Season 1/Star Trek Enterprise S01E04 Strange New World.mkv"
        with self.assertRaisesRegex(ValueError,"Enterprise"):info(path)
    def test_reject_other_episode(self):
        with self.assertRaisesRegex(ValueError,"Cross-show or cross-episode"):
            validate(plan(delete=B.replace("S03E03","S03E04")))
    def test_reject_keeper_same_as_loser(self):
        with self.assertRaisesRegex(ValueError,"multiple roles"):validate(plan(delete=A))
    def test_complete_retain_verified(self):
        ftp=FakeFTP()
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"result.json"
            execute(ftp,plan(),out)
            self.assertEqual(json.loads(out.read_text())["status"],"complete")
            self.assertIn(A,ftp.files);self.assertNotIn(B,ftp.files)
    def test_absent_keeper_halts_before_delete(self):
        ftp=FakeFTP();ftp.files.pop(A)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,"Missing"):
                execute(ftp,plan(),Path(tmp)/"result.json")
        self.assertIn(B,ftp.files);self.assertFalse(ftp.removed)
    def test_changed_loser_halts_before_delete(self):
        ftp=FakeFTP();ftp.files[B]["size"]="201"
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,"changed"):
                execute(ftp,plan(),Path(tmp)/"result.json")
        self.assertIn(B,ftp.files);self.assertFalse(ftp.removed)
if __name__=="__main__":unittest.main()
