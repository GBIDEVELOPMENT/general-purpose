#!/usr/bin/env python3
"""Offline safety tests for the owner-dispatched exact S01E01 FTP worker."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from pilot_ftp_video_acoustics import candidate, retrieve

class FakeFTP:
    def __init__(self,data):
        self.data=data
        self.calls=[]
    def retrbinary(self,command,callback,blocksize):
        self.calls.append(command)
        callback(self.data)

class Tests(unittest.TestCase):
    def test_exact_inventory(self):
        x=candidate()
        self.assertEqual(x["episode_id_from_filename"],"S01E01")
        self.assertEqual(x["size_bytes"],183386112)
        self.assertEqual(x["basename"],"Night Court - 1x01 - All You Need Is Love.avi")
    def test_wrong_byte_count_rejected(self):
        with TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                retrieve(FakeFTP(b"synthetic media"),candidate(),Path(temp)/"test.avi")
    def test_never_reads_directory_or_other_episode(self):
        with TemporaryDirectory() as temp:
            ftp=FakeFTP(b"synthetic media")
            with self.assertRaises(ValueError):
                retrieve(ftp,candidate(),Path(temp)/"test.avi")
            self.assertEqual(ftp.calls,["RETR "+candidate()["remote_path"]])
    def test_over_size_rejected_before_retrieval(self):
        with TemporaryDirectory() as temp:
            item={**candidate(),"size_bytes":300_000_000}
            ftp=FakeFTP(b"a")
            with self.assertRaises(ValueError):
                retrieve(ftp,item,Path(temp)/"test.avi")
            self.assertEqual(ftp.calls,[])
if __name__=="__main__":unittest.main()
