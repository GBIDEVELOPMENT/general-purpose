#!/usr/bin/env python3
"""Synthetic tests for quote/variant source comparison, not real TV dialogue."""
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

HERE=Path(__file__).resolve().parent
def load(filename,name):
    spec=spec_from_file_location(name,HERE/filename)
    obj=module_from_spec(spec);spec.loader.exec_module(obj)
    return obj
D=load("import_dialogue.py","nc_ingestion_comparison_tests")
C=load("compare_dialogue_versions.py","nc_compare_tests")

class WitnessComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/"Night Court"
        self.old=(D.ROOT,C.ROOT)
        self.addCleanup(self.revert)
        D.ROOT=C.ROOT=self.root
        (self.root/"catalog").mkdir(parents=True)
        for ep in ("S01E01","S01E02"):
            path=self.root/"seasons"/"S01"/ep/"episode.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"id":ep,"holdings":{"caption_files":[],
                "full_transcripts":[],"other":[],"recaps":[],"reviews":[],"wiki_exports":[]}}),"utf-8")
    def revert(self):D.ROOT,C.ROOT=self.old
    def ingest(self,ep,edition,ext,content):
        f=Path(self.temp.name)/(edition.replace(" ","-")+"-"+ep+"."+ext)
        f.write_text(content,"utf-8")
        D.import_one(f,{"episode":ep,"edition":edition,"rights_basis":"user_provided",
                        "confirmed":True,"language":"en","complete":False})
    def test_same_words_different_caption_format(self):
        self.ingest("S01E01","dvd-srt","srt",
            "1\n00:00:01,000 --> 00:00:03,000\nHARRY: Synthetic judicial dialogue.\n")
        self.ingest("S01E01","written-txt","txt","Synthetic judicial dialogue.")
        D.rebuild_index();C.main()
        result=json.loads((self.root/"catalog"/"dialogue-variant-comparison.json").read_text("utf-8"))
        self.assertEqual(result["version_comparisons"],1)
        self.assertEqual(result["comparison_results"][0]["status"],"same_normalized_words")
        self.assertTrue(result["comparison_results"][0]["not_canonical"])
    def test_materially_different_and_repeatable(self):
        self.ingest("S01E01","version-a","txt","Hypothetical court meeting includes a bright surprise.")
        self.ingest("S01E01","version-b","txt","Another imaginary scene concerns a sports contest and parking.")
        D.rebuild_index();C.main()
        p=self.root/"catalog"/"dialogue-variant-comparison.json"
        data=json.loads(p.read_text("utf-8"))
        self.assertEqual(data["comparison_results"][0]["status"],"materially_different_source_witnesses")
        prior=p.read_bytes()
        C.main()
        self.assertEqual(prior,p.read_bytes())
    def test_cross_episode_collision_warning(self):
        payload=" ".join(["synthetic","words","repeated","for","testing"]*14)
        self.ingest("S01E01","a","txt",payload)
        self.ingest("S01E02","b","txt",payload)
        D.rebuild_index();C.main()
        report=json.loads((self.root/"catalog"/"dialogue-variant-comparison.json").read_text("utf-8"))
        self.assertEqual(report["version_comparisons"],0)
        self.assertEqual(len(report["cross_episode_identical_long_text_alerts"]),1)
    def test_empty_corpus_is_valid(self):
        D.rebuild_index();C.main()
        report=json.loads((self.root/"catalog"/"dialogue-variant-comparison.json").read_text("utf-8"))
        self.assertEqual(report["source_witnesses"],0)
        self.assertFalse(report["cross_episode_identical_long_text_alerts"])

if __name__=="__main__":
    unittest.main()
