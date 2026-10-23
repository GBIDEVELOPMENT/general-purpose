#!/usr/bin/env python3
"""Synthetic subtitle/audio-source ingestion tests. No TV audio/video is included."""
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
import shutil
import subprocess
import unittest

HERE=Path(__file__).resolve().parent

def loader(filename,name):
    spec=spec_from_file_location(name,HERE/filename)
    m=module_from_spec(spec);spec.loader.exec_module(m)
    return m

E=loader("extract_local_media.py","extract_local_media_test")

class LocalMediaTests(unittest.TestCase):
    def test_stream_selection_distinguishes_original_language_and_codec(self):
        data={"streams":[
          {"index":1,"codec_type":"subtitle","codec_name":"hdmv_pgs_subtitle","tags":{"language":"eng"}},
          {"index":2,"codec_type":"subtitle","codec_name":"subrip","tags":{"language":"eng"},"disposition":{"default":0}},
          {"index":3,"codec_type":"subtitle","codec_name":"mov_text","tags":{"language":"fra"},"disposition":{"default":1}},
          {"index":4,"codec_type":"subtitle","codec_name":"webvtt","tags":{"language":"eng"},"disposition":{"default":1}},
          {"index":5,"codec_type":"video","codec_name":"h264"}
        ]}
        self.assertEqual([x["index"] for x in E.select_text_tracks(data,"en")],[4])
        self.assertEqual([x["index"] for x in E.select_text_tracks(data,"fr")],[3])
        self.assertEqual([x["index"] for x in E.select_text_tracks(data,"en",specific=2)],[2])
        self.assertEqual([x["index"] for x in E.select_text_tracks(data,"en",all_tracks=True)],[2,3,4])
        with self.assertRaises(ValueError):E.select_text_tracks(data,"en",specific=1)
    def test_asr_uses_stable_srt_timing_without_fictional_speakers(self):
        segments=[SimpleNamespace(start=1.234,end=2.345,text=" Hello, synthetic judge. "),
                  SimpleNamespace(start=2.4,end=3.001,text="This is a test.") ]
        srt=E.srt_from_asr(segments)
        self.assertIn("00:00:01,234 --> 00:00:02,345",srt)
        self.assertIn("00:00:02,400 --> 00:00:03,001",srt)
        self.assertNotIn("HARRY:",srt)
        with self.assertRaises(ValueError):
            E.srt_from_asr([SimpleNamespace(start=4,end=1,text="bad")])
    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),"requires installed local ffmpeg/ffprobe")
    def test_end_to_end_owned_synthetic_mkv_caption_track(self):
        with TemporaryDirectory() as td:
            temp=Path(td)
            media=temp/"Night.Court.S01E01.synthetic.mkv"
            captions=temp/"synthetic.srt"
            captions.write_text("1\n00:00:00,250 --> 00:00:01,500\nSynthetic judicial exchange.\n\n"
                                "2\n00:00:02,000 --> 00:00:03,750\nImaginary reply.\n","utf-8")
            subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
                            "-f","lavfi","-i","color=c=black:s=64x64:r=1:d=4",
                            "-i",str(captions),"-map","0:v:0","-map","1:s:0",
                            "-c:v","mpeg4","-c:s","srt",str(media)],check=True,timeout=40)
            import_path=E.D.ROOT
            self.addCleanup(setattr,E.D,"ROOT",import_path)
            E.D.ROOT=temp/"Night Court"
            ep=E.D.ROOT/"seasons"/"S01"/"S01E01"/"episode.json"
            ep.parent.mkdir(parents=True)
            ep.write_text(json.dumps({"id":"S01E01","season":1,"episode":1,
              "holdings":{"full_transcripts":[],"caption_files":[],"recaps":[],
                          "reviews":[],"wiki_exports":[],"other":[]}}),"utf-8")
            args=SimpleNamespace(
                episode="S01E01",edition="synthetic-owned-test",language="en",
                track_index=None,all_text_tracks=False,dry_run=False,
                mode="subtitles",model=None,allow_model_download=False,
                rights_basis="user_provided",confirm_rights=True,
                confirm_original_series=True,complete=False)
            source=E.probe(media)
            self.assertTrue(E.select_text_tracks(source,"en"))
            self.assertEqual(E.extract_one(media,args),1)
            self.assertEqual(E.extract_one(media,args),1) # stable immutable reimport
            index=(E.D.ROOT/"catalog"/"dialogue-index.jsonl").read_text("utf-8").splitlines()
            self.assertEqual(len(index),1)
            item=json.loads(index[0])
            self.assertEqual(item["episode_id"],"S01E01")
            self.assertEqual(item["cue_count"],2)
            self.assertEqual(item["declared_complete"],False)
            original=E.D.ROOT/item["manifest"]
            m=json.loads(original.read_text("utf-8"))
            self.assertEqual(m["source_name"],media.name)
            self.assertEqual(m["timecoded"],True)
            self.assertEqual(len(json.loads(ep.read_text("utf-8"))["holdings"]["caption_files"]),1)

if __name__=="__main__":
    unittest.main()
