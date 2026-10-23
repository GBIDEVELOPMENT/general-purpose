#!/usr/bin/env python3
"""Synthetic tests of QA metrics and provenance-aware transcript retrieval."""
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent

def module(file,name):
    spec=spec_from_file_location(name,HERE/file)
    loaded=module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded

INGEST=module("import_dialogue.py","import_dialogue_qatests")
QC=module("audit_dialogue_quality.py","quality_tests")
SEARCH=module("search_dialogue.py","search_tests")

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/"Night Court"
        self.root.mkdir()
        self.ep=self.root/"seasons"/"S01"/"S01E01"
        self.ep.mkdir(parents=True)
        (self.root/"catalog").mkdir()
        (self.ep/"episode.json").write_text(json.dumps({
           "id":"S01E01","season":1,"episode":1,
           "holdings":{"full_transcripts":[],"caption_files":[],"recaps":[],
                       "reviews":[],"wiki_exports":[],"other":[]}}),"utf-8")
        self.roots=[(mod,mod.ROOT) for mod in (INGEST,QC,SEARCH)]
        self.addCleanup(self.restore)
        for mod,_ in self.roots:mod.ROOT=self.root
        self.opts={
            "episode":"S01E01","edition":"Synthetic DVD edition",
            "rights_basis":"user_provided","confirmed":True,
            "language":"en","complete":True
        }
    def restore(self):
        for m,r in self.roots:m.ROOT=r
    def input(self,name,contents):
        dest=Path(self.tmp.name)/name
        dest.write_text(contents,"utf-8")
        return dest
    def test_search_dialogue_links_cue_and_source(self):
        file=self.input("fiction.S01E01.srt",
            "1\n00:00:00,700 --> 00:00:02,000\nHARRY: Synthetic popcorn evidence.\n\n"
            "2\n00:00:02,200 --> 00:00:03,100\nBULL: Another example.\n")
        INGEST.import_one(file,self.opts)
        INGEST.rebuild_index()
        found=SEARCH.records("popcorn","dialogue")
        self.assertEqual(len(found),1)
        self.assertEqual(found[0]["episode_id"],"S01E01")
        self.assertEqual(found[0]["start_ms"],700)
        self.assertEqual(found[0]["speaker_explicit"]["label"],"HARRY")
        self.assertIn("sha256",found[0]["source_sha256"][:0]+"sha256") # source digest exists
        self.assertEqual(SEARCH.records("squash","dialogue"),[])
    def test_licensed_synopsis_separate(self):
        record={"id":"S01E01","season":1,"title":"All You Need Is Love",
            "plot_source_plaintext":"An imaginary judge finds the popcorn.",
            "source":{"permalink":"https://en.wikipedia.org/w/index.php?oldid=123",
                      "path":"licensed/s01","revision":123,"license":"CC BY-SA 4.0"}}
        (self.root/"catalog"/"episode-knowledge.jsonl").write_text(json.dumps(record)+"\n","utf-8")
        actual=SEARCH.records("popcorn","both")
        self.assertEqual(len(actual),1)
        self.assertEqual(actual[0]["kind"],"licensed_synopsis_not_dialogue")
        self.assertEqual(SEARCH.records("popcorn","dialogue"),[])
        self.assertEqual(SEARCH.records("popcorn","both",language="en"),[])
    def test_quality_flags_and_union_not_certification(self):
        file=self.input("S01E01.synthetic.srt",
            "1\n00:00:00,000 --> 00:00:01,000\nHARRY: Word one.\n\n"
            "2\n00:00:00,500 --> 00:00:01,500\nHARRY: Word one.\n\n"
            "3\n00:00:35,000 --> 00:00:35,900\nBULL: Say two.\n")
        INGEST.import_one(file,self.opts)
        INGEST.rebuild_index()
        QC.main()
        out=json.loads((self.root/"catalog"/"dialogue-quality.json").read_text("utf-8"))
        self.assertEqual(out["source_witnesses"],1)
        self.assertEqual(out["independently_verified_complete_episodes"],0)
        data=out["witness_quality"][0]
        self.assertIn("overlapping_source_cues_review",data["flags"])
        self.assertIn("suspiciously_short_caption_timeline",data["flags"])
        self.assertEqual(data["source_gaps_over_30_seconds"],1)
        self.assertEqual(data["source_cue_union_duration_ms"],2400)
        self.assertEqual(data["adjacent_exact_repetitions"],1)
        # Separate QA rerun is stable and doesn't rewrite source files.
        previous=(self.root/"catalog"/"dialogue-quality.json").read_bytes()
        QC.main()
        self.assertEqual(previous,(self.root/"catalog"/"dialogue-quality.json").read_bytes())
    def test_untimed_not_video_qualified(self):
        file=self.input("S01E01.text.txt","Imaginary text, no clock information.\n\nSecond paragraph.")
        INGEST.import_one(file,self.opts)
        INGEST.rebuild_index()
        QC.main()
        q=json.loads((self.root/"catalog"/"dialogue-quality.json").read_text("utf-8"))["witness_quality"][0]
        self.assertIsNone(q["latest_cue_end_ms"])
        self.assertIn("untimed_source_requires_separate_completeness_check",q["flags"])
    def test_live_empty_corpus(self):
        QC.main()
        self.assertEqual(SEARCH.records("anything","dialogue"),[])
        r=json.loads((self.root/"catalog"/"dialogue-quality.json").read_text("utf-8"))
        self.assertEqual(r["source_witnesses"],0)
        self.assertEqual(r["witnesses_with_flags"],0)

if __name__=="__main__":
    unittest.main()
