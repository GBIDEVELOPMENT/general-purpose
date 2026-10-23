#!/usr/bin/env python3
"""Offline synthetic tests only. No real dialogue or external downloads."""
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
spec=spec_from_file_location("nightcourt_import_dialogue",HERE/"import_dialogue.py")
D=module_from_spec(spec)
spec.loader.exec_module(D)

class ImportTest(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.old=D.ROOT
        self.addCleanup(setattr,D,"ROOT",self.old)
        D.ROOT=Path(self.tmp.name)/"Night Court"
        p=D.ROOT/"seasons"/"S01"/"S01E01"/"episode.json"
        p.parent.mkdir(parents=True,exist_ok=True)
        self.ep=p
        p.write_text(json.dumps({"id":"S01E01","season":1,"episode":1,
          "holdings":{"full_transcripts":[],"caption_files":[],
                      "recaps":[],"reviews":[],"wiki_exports":[],"other":[]}}),
          encoding="utf-8")
        self.opts={"episode":"S01E01","edition":"test-synthetic-dvd",
                   "rights_basis":"user_provided","confirmed":True,
                   "language":"en","complete":True,
                   "source_name":"synthetic test captions"}
    def create(self,name,content):
        p=Path(self.tmp.name)/name
        p.write_bytes(content)
        return p
    def test_srt_and_idempotency(self):
        sample=(b"1\n00:00:00,500 --> 00:00:01,200\n"
                b"Hello, hypothetical court.\n\n"
                b"2\n00:00:01,200 --> 00:00:03,000\n"
                b"[FAKE APPLAUSE]\nThank you.\n")
        p=self.create("fiction.S01E01.srt",sample)
        D.import_one(p,self.opts)
        D.import_one(p,self.opts)
        rows=D.rebuild_index()
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["cue_count"],2)
        obj=json.loads(self.ep.read_text("utf-8"))
        self.assertEqual(len(obj["holdings"]["caption_files"]),1)
        manifest=json.loads((self.ep.parent/rows[0]["manifest"].split("S01E01/",1)[-1]).read_text("utf-8"))
        self.assertEqual(manifest["sha256"],hashlib.sha256(sample).hexdigest())
        self.assertTrue(manifest["declared_complete"])
        self.assertEqual(manifest["completeness_status"],"submitter_declared_complete_unverified")
    def test_variants_coexist(self):
        a=self.create("S01E01.first.txt",b"Case called.\n\nMotion noted.")
        b=self.create("S01E01.second.txt",b"Case called.\n\nSecond variation.")
        D.import_one(a,self.opts)
        D.import_one(b,{**self.opts,"edition":"test-synthetic-typed-transcript"})
        entries=D.rebuild_index()
        self.assertEqual(len(entries),2)
        obj=json.loads(self.ep.read_text("utf-8"))
        self.assertEqual(len(obj["holdings"]["full_transcripts"]),2)
    def test_inbox_requires_sidecar_and_rights(self):
        folder=D.ROOT/"incoming"
        folder.mkdir(parents=True)
        sample=folder/"S01E01.any.vtt"
        sample.write_text("WEBVTT\n\n00:01.000 --> 00:02.300\nSynthetic caption.\n","utf-8")
        D.inbox(folder)
        self.assertEqual(len(D.rebuild_index()),0)
        sidecar=Path(str(sample)+".meta.json")
        sidecar.write_text(json.dumps({"edition":"vtt-test",
             "rights_basis":"user_provided","confirmed":True,
             "complete":True,"episode":"S01E01"}),encoding="utf-8")
        D.inbox(folder)
        self.assertEqual(len(D.rebuild_index()),1)
    def test_denies_unknown_episode_and_unconfirmed_rights(self):
        p=self.create("S01E01.subs.srt",b"1\n00:00:01,000 --> 00:00:02,000\nSynthetic.\n")
        with self.assertRaises(ValueError):D.import_one(p,{**self.opts,"confirmed":False})
        with self.assertRaises(ValueError):D.import_one(p,{**self.opts,"episode":"S10E01"})
    def test_bad_timestamps_rejected(self):
        p=self.create("S01E01.bad.srt",b"1\n00:00:09,100 --> 00:00:01,200\nImpossible.\n")
        with self.assertRaises(ValueError):D.import_one(p,self.opts)
    def test_vtt_punctuation_and_text(self):
        p=self.create("S01E01.vtt",b"WEBVTT\n\nNOTE test note\n\n"
           b"00:00:01.111 --> 00:00:02.222 align:start\n"
           b"<v Speaker>Test cue!</v>\n")
        D.import_one(p,self.opts)
        rows=D.rebuild_index()
        self.assertEqual(rows[0]["cue_count"],1)
        mfiles=list((self.ep.parent/"dialogue"/"versions").glob("*/manifest.json"))
        metadata=json.loads(mfiles[0].read_text("utf-8"))
        self.assertEqual(metadata["first_start_ms"],1111)
        self.assertEqual(metadata["last_end_ms"],2222)

if __name__=="__main__":
    unittest.main()
