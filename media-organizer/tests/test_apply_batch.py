import sys, unittest, tempfile, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from apply_batch import plan_validate, execute, parse_episode_identity
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
    def test_multi_episode_retained(self):
        x=op(src="/downloads/S.S01E01E02.mkv",dst="/downloads/S/Season 01/S - S01E01-E02.mkv")
        self.assertEqual(len(plan_validate(plan([x]))),1)
    def test_multi_episode_drop_refused(self):
        x=op(src="/downloads/S.S01E01E02.mkv",dst="/downloads/S/Season 01/S - S01E01.mkv")
        with self.assertRaisesRegex(ValueError,"episode identity"):plan_validate(plan([x]))
    def test_cross_season_source_refused(self):
        x=op(src="/downloads/Show.S03E26S04E01.mkv",dst="/downloads/Show/Season 03/Show - S03E26.mkv")
        with self.assertRaisesRegex(ValueError,"Cross-season"):plan_validate(plan([x]))
    def test_wrong_episode_refused(self):
        with self.assertRaisesRegex(ValueError,"episode identity"):
            plan_validate(plan([op(dst="/downloads/S/Season 01/S - S01E02.mkv")]))
    def test_parser_various_sequences(self):
        self.assertEqual(parse_episode_identity("A.S01E01E02.mkv"),{(1,1),(1,2)})
        self.assertEqual(parse_episode_identity("A.S07E25-E26.mkv"),{(7,25),(7,26)})
        self.assertEqual(parse_episode_identity("A.S03E26S04E01.mkv"),{(3,26),(4,1)})
    def test_no_duplicate_destinations(self):
        with self.assertRaises(ValueError):plan_validate(plan([op(),op(src="/downloads/S.S01E02.mkv")]))
    def test_no_move_chains(self):
        with self.assertRaises(ValueError):plan_validate(plan([op(),op(src="/downloads/S/Season 01/S - S01E01.mkv",dst="/downloads/Else/Other - S01E01.mkv")]))
    def test_no_unapproved_metadata(self):
        x=op();x["ignore"]=True
        with self.assertRaises(ValueError):plan_validate(plan([x]))

class FakeFTP:
    def __init__(self):
        self.dirs={"/downloads"}
        self.files={"/downloads/S.S01E01.mkv":{"type":"file","size":"100","modify":"20261023000000"}}
        self.current="/downloads"
    def cwd(self,p):
        if p not in self.dirs:raise ValueError("No such remote directory")
        self.current=p
    def mlsd(self):
        for p in sorted(self.dirs):
            if p!="/downloads" and str(Path(p).parent)==self.current:
                yield (Path(p).name,{"type":"dir"})
        for p,facts in sorted(self.files.items()):
            if str(Path(p).parent)==self.current:yield (Path(p).name,facts)
    def mkd(self,p):
        if str(Path(p).parent) not in self.dirs:raise ValueError("Parent missing")
        self.dirs.add(p)
    def rename(self,a,b):
        if b in self.files:raise AssertionError("overwrite attempted")
        self.files[b]=self.files.pop(a)

class FTPExecutionTests(unittest.TestCase):
    def test_move_creates_only_needed_folders_and_journals(self):
        ftp=FakeFTP()
        with tempfile.TemporaryDirectory() as d:
            journal=Path(d)/"completed.json"
            execute(ftp,plan([op()]),journal)
            self.assertIn("/downloads/S/Season 01/S - S01E01.mkv",ftp.files)
            self.assertNotIn("/downloads/S.S01E01.mkv",ftp.files)
            evidence=json.loads(journal.read_text())
            self.assertEqual(evidence["status"],"complete")
            self.assertEqual(len(evidence["completed"]),1)
            self.assertTrue(evidence["completed"][0]["destination_verified"])
    def test_broken_postrename_result_retains_uncertain_operation(self):
        class DropOnRename(FakeFTP):
            def rename(self,a,b):
                self.files.pop(a)
        ftp=DropOnRename()
        with tempfile.TemporaryDirectory() as d:
            journal=Path(d)/"completed.json"
            with self.assertRaisesRegex(RuntimeError,"Post-rename"):
                execute(ftp,plan([op()]),journal)
            evidence=json.loads(journal.read_text())
            self.assertEqual(evidence["status"],"partial_or_failed")
            self.assertEqual(len(evidence["completed"]),1)
            self.assertFalse(evidence["completed"][0]["destination_verified"])
    def test_occupied_destination_is_never_overwritten(self):
        ftp=FakeFTP()
        ftp.dirs.update({"/downloads/S","/downloads/S/Season 01"})
        ftp.files["/downloads/S/Season 01/S - S01E01.mkv"]={"type":"file","size":"50"}
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):execute(ftp,plan([op()]),Path(d)/"journal.json")
            self.assertIn("/downloads/S.S01E01.mkv",ftp.files)

if __name__=="__main__":unittest.main()
