#!/usr/bin/env python3
"""Synthetic FTP filesystem tests, no network, credentials or actual TV media."""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import unittest

HERE=Path(__file__).resolve().parent
spec=spec_from_file_location("night_court_ftp_intake",HERE/"ftp_research_intake.py")
F=module_from_spec(spec)
spec.loader.exec_module(F)

class FakeFTP:
    def __init__(self):
        self.directory="/"
        self.contents={
            "/downloads":[("S60",{"type":"dir"}),("Night Court",{"type":"dir"}),("other",{"type":"dir"})],
            "/downloads/S60":[("DVD",{"type":"dir"})],
            "/downloads/S60/DVD":[],
            "/downloads/other":[("secret-archive.rar",{"type":"file","size":"2345"})],
            "/downloads/Night Court":[
                ("Season 3",{"type":"dir"}),
                ("Night.Court.S01E01.en.srt",{"type":"file","size":"35"}),
                ("another.txt",{"type":"file","size":"15"})],
            "/downloads/Night Court/Season 3":[
                ("Night.Court.S03E01.en.srt",{"type":"file","size":"45"}),
                ("Episode.S03E02.mkv",{"type":"file","size":"123456"})]}
        self.files={"/downloads/Night Court/Night.Court.S01E01.en.srt":
                     b"1\n00:00:01,000 --> 00:00:02,000\nSynthetic.\n"}
        self.transfers=[]
    def cwd(self,directory):
        if directory not in self.contents:raise F.ftplib.error_perm("550 nonexistent")
        self.directory=directory
    def mlsd(self):return self.contents[self.directory]
    def size(self,path):return len(self.files[path])
    def retrbinary(self,command,callback,blocksize=None):
        self.transfers.append(command)
        callback(self.files[command[5:]])
    def quit(self):pass

class TestSafety(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name)/"Night Court"
        root.mkdir()
        self.previous=(F.ROOT,F.STAGING,F.ARCHIVES,F.MANIFEST)
        F.ROOT=root
        F.STAGING=root/"incoming"
        F.ARCHIVES=root/"research"/"source-archives"
        F.MANIFEST=root/"research"/"ftp-staging-records.jsonl"
        self.addCleanup(self.reset)
        self.server=FakeFTP()
    def reset(self):
        F.ROOT,F.STAGING,F.ARCHIVES,F.MANIFEST=self.previous
    def test_path_constraints(self):
        good="/downloads/Night Court/Season 3/Night.Court.S03E01.rar"
        self.assertEqual(F.clean_path(good,file=True),good)
        for bad in [
            "downloads/Night Court/X.srt",
            "/downloads/Night Court/../other.txt",
            "/downloads/S60/Some.Other.Show.srt",
            "/downloads/Night Court/2023.S01E01.srt",
            "/downloads/Night Court/file.mp4",
            "/downloads/Night Court/.env",
            "/downloads/Night Court/secret\npath.rar",
            "/etc/passwd",
            "/downloads/Night Court/evil\\file.zip"
        ]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):F.clean_path(bad,file=True)
    def test_inventory_does_not_list_other_account_files(self):
        inventory=F.inventory(self.server)
        self.assertEqual(inventory["matching_source_files"],3)
        dump=json.dumps(inventory)
        self.assertNotIn("secret-archive",dump)
        self.assertNotIn("Episode.S03E02.mkv",dump)
        self.assertIn("/downloads/Night Court",dump)
        self.assertIn("/downloads/Night Court/Season 3",dump)
        self.assertFalse(self.server.transfers)
    def test_stage_exact_single_source_and_sha(self):
        result=F.stage(self.server,"/downloads/Night Court/Night.Court.S01E01.en.srt")
        self.assertEqual(result["size_bytes"],len(self.server.files[self.server.transfers[0][5:]]))
        self.assertEqual(len(self.server.transfers),1)
        self.assertEqual(F.MANIFEST.exists(),True)
        self.assertTrue((F.STAGING/"Night.Court.S01E01.en.srt").exists())
        again=F.stage(self.server,"/downloads/Night Court/Night.Court.S01E01.en.srt")
        self.assertEqual(again["action"],"already_staged")
        self.assertEqual(len(self.server.transfers),1)
        self.assertEqual(len(F.MANIFEST.read_text("utf-8").splitlines()),1)
        self.assertNotIn("FTP_PASSWORD",F.MANIFEST.read_text("utf-8").replace("GitHub Actions FTP_PASSWORD repository secret",""))
    def test_existing_source_is_not_duplicated(self):
        F.ARCHIVES.mkdir(parents=True)
        (F.ARCHIVES/"Night.Court.S01E01.en.srt").write_bytes(b"existing source")
        item=F.stage(self.server,"/downloads/Night Court/Night.Court.S01E01.en.srt")
        self.assertEqual(item["action"],"already_archived")
        self.assertEqual(self.server.transfers,[])
    def test_missing_secret_fails_before_connection(self):
        with self.assertRaisesRegex(ValueError,"FTP_PASSWORD"):
            F.connect("test.host","research","","ftp")

if __name__=="__main__":
    unittest.main()
