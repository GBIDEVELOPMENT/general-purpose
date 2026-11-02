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

    def test_animated_series_distinct_from_hbo_lanterns(self):
        from trek_dedupe import validate
        from pathlib import Path
        approved=json.loads(Path("media-organizer/approved-trek-dedupe.json").read_text(encoding="utf-8"))
        self.assertEqual(len(validate(approved)),1)
        self.assertEqual({g["show"] for g in approved["groups"]},{"green_lantern_animated"})
        self.assertTrue(all("Green Lantern The Animated Series" in f["from"] for g in approved["groups"] for f in [g["retain"],g["retain_second"]]+g["delete"]))
    def test_reject_hbo_lanterns_masquerading_as_animated(self):
        with self.assertRaises(ValueError):
            info("/downloads/Lanterns (2026)/Season 01/Lanterns - S01E03.mkv")
    def test_reject_general_green_lantern_live_action(self):
        with self.assertRaises(ValueError):
            info("/downloads/Green Lantern 2011/Green Lantern S01E03.mkv")
    def test_keeper_protected_in_two_probed_animated_groups(self):
        approved=json.loads(Path("media-organizer/approved-trek-dedupe.json").read_text(encoding="utf-8"))
        self.assertEqual(len(validate(approved)),1)
        import copy
        corrupt=copy.deepcopy(approved)
        corrupt["groups"][0]["delete"][0]["from"]=corrupt["groups"][0]["retain"]["from"]
        with self.assertRaises(ValueError):validate(corrupt)


    def test_animated_premiere_requires_both_hd_parts(self):
        approved=json.loads(Path("media-organizer/approved-trek-dedupe.json").read_text(encoding="utf-8"))
        self.assertEqual(len(validate(approved)),1)
        class MiniFTP(FakeFTP):
            def __init__(self):
                self.current=None;self.removed=[];self.files={}
                for obj in [approved["groups"][0]["retain"],approved["groups"][0]["retain_second"],approved["groups"][0]["delete"][0]]:
                    self.files[obj["from"]]={"type":"file","size":str(obj["size"]),"modify":obj["modify"]}
        for missing in ("retain","retain_second"):
            ftp=MiniFTP();ftp.files.pop(approved["groups"][0][missing]["from"])
            with tempfile.TemporaryDirectory() as d:
                with self.assertRaisesRegex(ValueError,"Missing"):
                    execute(ftp,approved,Path(d)/"journal.json")
            self.assertFalse(ftp.removed)
        ftp=MiniFTP()
        with tempfile.TemporaryDirectory() as d:
            journal=Path(d)/"journal.json"
            execute(ftp,approved,journal)
            self.assertEqual(json.loads(journal.read_text())["status"],"complete")
        self.assertEqual(ftp.removed,[approved["groups"][0]["delete"][0]["from"]])
        self.assertIn(approved["groups"][0]["retain"]["from"],ftp.files)
        self.assertIn(approved["groups"][0]["retain_second"]["from"],ftp.files)
    def test_animated_premiere_rejects_unapproved_episode_or_lanterns(self):
        import copy
        approved=json.loads(Path("media-organizer/approved-trek-dedupe.json").read_text(encoding="utf-8"))
        bad=copy.deepcopy(approved)
        bad["groups"][0]["delete"][0]["from"]="/downloads/Lanterns Season 01/Lanterns S01E01-E02.avi"
        with self.assertRaises(ValueError):validate(bad)
        bad=copy.deepcopy(approved);bad["groups"][0]["retain_second"]["size"]+=1
        with self.assertRaises(ValueError):validate(bad)

if __name__=="__main__":unittest.main()
