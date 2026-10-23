#!/usr/bin/env python3
"""Offline synthetic whole-season bundle tests; no TV dialogue or video."""
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
import zipfile

HERE=Path(__file__).resolve().parent
spec=spec_from_file_location("night_court_bundle",HERE/"import_dialogue_bundle.py")
B=module_from_spec(spec);spec.loader.exec_module(B)

class BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/"Night Court"
        self.previous=B.D.ROOT
        self.addCleanup(setattr,B.D,"ROOT",self.previous)
        B.D.ROOT=self.root
        for i in (1,2):
            path=self.root/"seasons"/"S01"/f"S01E{i:02d}"/"episode.json"
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps({"id":f"S01E{i:02d}","season":1,"episode":i,
                "holdings":{"caption_files":[],"full_transcripts":[],"recaps":[],
                            "reviews":[],"wiki_exports":[],"other":[]}}),"utf-8")
        (self.root/"catalog").mkdir()
        self.metadata={"edition":"self_owned_dvd","language":"en",
                       "rights_basis":"user_provided","confirmed":True,
                       "complete":False,"source_name":"User supplied original series subtitles"}
    def make_zip(self,filenames):
        path=Path(self.tmp.name)/"owned-caption-samples.zip"
        with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
            for key,body in filenames.items():z.writestr(key,body)
        return path
    def test_bulk_import_is_idempotent_and_does_not_claim_completeness(self):
        one="1\n00:00:00,100 --> 00:00:02,000\nSynthetic episode one.\n"
        two="1\n00:00:01,100 --> 00:00:03,000\nSynthetic episode two.\n"
        archive=self.make_zip({"season1/S01E01.en.srt":one,"season1/S01E02.en.srt":two})
        B.import_bundle(archive,self.metadata)
        B.import_bundle(archive,self.metadata)
        index=B.D.rebuild_index()
        self.assertEqual(len(index),2)
        self.assertEqual({x["episode_id"] for x in index},{"S01E01","S01E02"})
        self.assertTrue(all(x["declared_complete"] is False for x in index))
        for rec in index:
            m=json.loads((self.root/rec["manifest"]).read_text("utf-8"))
            self.assertIn("ZIP SHA-256",m["source_notes"])
            self.assertIn("owned-caption-samples.zip::",m["source_name"])
        self.assertEqual(len(json.loads((self.root/"seasons/S01/S01E01/episode.json").read_text("utf-8"))["holdings"]["caption_files"]),1)
    def test_no_sidecar_rights_refuses(self):
        z=self.make_zip({"S01E01.txt":"Synthetic paragraph."})
        with self.assertRaises(ValueError):B.import_bundle(z,{"edition":"dvd","confirmed":False})
        self.assertEqual(list(self.root.rglob("dialogue/versions")),[])
    def test_rejects_traversal_and_bad_id(self):
        for filename in ("../S01E01.srt","other/S10E02.srt"):
            path=self.make_zip({filename:"1\n00:00:01,000 --> 00:00:02,000\nSample.\n"})
            with self.assertRaises(ValueError):B.import_bundle(path,self.metadata)
    def test_overrides_are_limited_and_versioned(self):
        z=self.make_zip({"S01E02.fr.txt":"Bonjour, texte synthétique."})
        metadata={**self.metadata,"overrides":{"S01E02.fr.txt":{"language":"fr","edition":"dvd-french"}}}
        B.import_bundle(z,metadata)
        entry=B.D.rebuild_index()[0]
        self.assertEqual(entry["language"],"fr")
        self.assertEqual(entry["edition"],"dvd-french")
        with self.assertRaises(ValueError):
            B.import_bundle(z,{**self.metadata,
              "overrides":{"S01E02.fr.txt":{"rights_basis":"public_domain"}}})

if __name__=="__main__":
    unittest.main()
