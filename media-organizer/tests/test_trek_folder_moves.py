"""Exact-snapshot Trek directory relocation safety and full offline FTP simulation."""
import copy
import ftplib
import json
import sys
import tempfile
import unittest
from pathlib import Path,PurePosixPath
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from trek_folder_moves import validate,execute

APPROVED=Path("media-organizer/approved-batch.json")

class FakeFTP:
    def __init__(self,doc):
        self.dirs={"/downloads","/downloads/Star Trek"}
        self.files={}
        for group in doc["trek_folder_moves"]:
            root=group["from"]
            self.dirs.add(root)
            for child in group["files"]:
                self.files[root+"/"+child["name"]]={"type":"file","size":str(child["size"]),"modify":child["modify"]}
        self.current="/downloads"
        self.renamed=[]
    def cwd(self,path):
        if path not in self.dirs:raise ftplib.error_perm("550 directory missing")
        self.current=path
    def mlsd(self):
        for path in sorted(self.dirs):
            if path!=self.current and str(PurePosixPath(path).parent)==self.current:
                yield PurePosixPath(path).name,{"type":"dir"}
        for path,info in sorted(self.files.items()):
            if str(PurePosixPath(path).parent)==self.current:
                yield PurePosixPath(path).name,info
    def mkd(self,path):
        if str(PurePosixPath(path).parent) not in self.dirs:raise ftplib.error_perm("550 no parent")
        self.dirs.add(path)
    def rename(self,src,dst):
        if src not in self.dirs or dst in self.dirs:raise AssertionError("Unsafe renaming attempt")
        self.dirs.remove(src);self.dirs.add(dst)
        for path in list(self.files):
            if path.startswith(src+"/"):
                self.files[dst+path[len(src):]]=self.files.pop(path)
        self.renamed.append((src,dst))

class TrekFolderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(APPROVED.read_text(encoding="utf-8"))
        assert cls.doc["batch_id"]=="trek_folders_12_20261102"
    def test_12_exact_folders_and_200_files(self):
        ops=validate(self.doc)
        self.assertEqual(len(ops),12)
        self.assertEqual(sum(len(x["files"]) for x in ops),200)
        self.assertEqual(sum(y["size"] for x in ops for y in x["files"]),158506008493)
    def test_no_unreviewed_lanterns_or_other_series(self):
        bad=copy.deepcopy(self.doc)
        bad["trek_folder_moves"][0]["from"]="/downloads/Lanterns Season 01"
        with self.assertRaises(ValueError):validate(bad)
    def test_no_hidden_extra_entries(self):
        ftp=FakeFTP(self.doc)
        root=self.doc["trek_folder_moves"][0]["from"]
        ftp.files[root+"/.hidden"]={"type":"file","size":"6","modify":"20260101000000"}
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError,"Unexpected"):
                execute(ftp,self.doc,Path(folder)/"journal.json")
        self.assertEqual(ftp.renamed,[])
    def test_wrong_child_byte_refused_before_any_move(self):
        ftp=FakeFTP(self.doc)
        root=self.doc["trek_folder_moves"][0]["from"]
        child=self.doc["trek_folder_moves"][0]["files"][0]["name"]
        ftp.files[root+"/"+child]["size"]="1"
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                execute(ftp,self.doc,Path(folder)/"journal.json")
        self.assertEqual(ftp.renamed,[])
    def test_full_relocation_preserves_all_200_files(self):
        ftp=FakeFTP(self.doc)
        with tempfile.TemporaryDirectory() as folder:
            audit=Path(folder)/"journal.json"
            results=execute(ftp,self.doc,audit)
            record=json.loads(audit.read_text())
        self.assertEqual(record["status"],"complete")
        self.assertEqual(len(results),12)
        self.assertEqual(len(ftp.renamed),12)
        self.assertEqual(len(ftp.files),200)
        self.assertTrue(all(item["destination_verified"] for item in record["completed"]))
        for group in self.doc["trek_folder_moves"]:
            self.assertNotIn(group["from"],ftp.dirs)
            self.assertIn(group["to"],ftp.dirs)
            for child in group["files"]:
                self.assertIn(group["to"]+"/"+child["name"],ftp.files)
    def test_wrong_destination_refused(self):
        bad=copy.deepcopy(self.doc)
        bad["trek_folder_moves"][0]["to"]="/downloads/Star Trek/Studio 60"
        with self.assertRaises(ValueError):validate(bad)

if __name__=="__main__":unittest.main()
