#!/usr/bin/env python3
"""Subtitle-only reading-script renderer regression, including untimed S09E19."""
import json
import unittest
from build_source_script_scaffolds import INDEX,render_source,jsonl

class AllEpisodeScriptScaffolds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=jsonl(INDEX)
    def test_one_witness_per_original_episode(self):
        self.assertEqual(len(self.sources),193)
        self.assertEqual(len({x["episode_id"] for x in self.sources}),193)
    def test_real_S01E01_complete_source_preserved(self):
        first=next(x for x in self.sources if x["episode_id"]=="S01E01")
        md,record=render_source(first)
        self.assertEqual(record["caption_cues"],336)
        self.assertGreater(record["unattributed_caption_units"],336)
        self.assertIn("All You Need Is Love",md)
        self.assertIn("C00019",md)
        self.assertIn("UNIDENTIFIED VOICE",md)
        self.assertIn("not observed",md)
        self.assertFalse(record["complete_script_verified"])
        self.assertFalse(record["source_audio_alignment_verified"])
    def test_untimed_episode_does_not_invent_timecodes(self):
        source=next(x for x in self.sources if x["episode_id"]=="S09E19")
        md,record=render_source(source)
        self.assertFalse(record["timed"])
        self.assertEqual(record["caption_cues"],347)
        self.assertIn("UNTIMED SOURCE PARAGRAPHS",md)
        self.assertIn("UNTIMED · C00001",md)
        self.assertFalse(record["stage_directions_video_verified"])
    def test_all_source_ids_render_without_omitting_cues(self):
        for src in self.sources:
            with self.subTest(src=src["episode_id"]):
                _,record=render_source(src)
                self.assertEqual(record["caption_cues"],src["cue_count"])
                self.assertGreaterEqual(record["unattributed_caption_units"],src["cue_count"])
                self.assertFalse(record["speaker_identity_verified"])
                self.assertFalse(record["complete_script_verified"])

if __name__=="__main__":unittest.main()
