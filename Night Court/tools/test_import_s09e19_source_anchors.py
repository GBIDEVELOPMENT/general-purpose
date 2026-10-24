#!/usr/bin/env python3
"""No network. Adversarial acceptance validation of S09E19 zero-timecode review."""
import json,tempfile,unittest
from pathlib import Path
from import_s09e19_source_anchors import validate,TXT_SHA,EXPECTED_BYTES,SCHEMA
from s09e19_untimed_video_anchor_pilot import WINDOWS,sources
from match_s09e19_untimed_paragraphs import score_windows

def fixture():
    paragraphs=sources()
    raw=[]
    for a,b in WINDOWS:
        raw.append({"source_window_ms":[a*1000,b*1000],
             "source_audio_sha256":"a"*64,
             "asr_segments":[]})
    windows=score_windows(raw,paragraphs)
    return {
       "schema":SCHEMA,"episode_id":"S09E19",
       "source_video_size_bytes":EXPECTED_BYTES,
       "source_video_sha256":"b"*64,"source_duration_seconds":1450.0,
       "original_untimed_transcript_sha256":TXT_SHA,"original_paragraphs":347,
       "model":"faster-whisper tiny.en","windows":windows,
       "segments_reviewed":0,"distinct_high_lexical_match_candidates_total":0,
       "candidate_paragraphs_monotonic_across_windows":True,
       "original_source_cue_times_introduced":False,
       "original_transcript_modified":False,
       "all_347_paragraphs_time_aligned":False,
       "source_edition_audiovisually_verified":False,
       "words_speaker_and_emotion_verified":False,
       "all_audio_or_video_complete":False,
       "raw_source_media_wav_or_model_weights_retained_in_artifact":False
    }

class SourceAcceptance(unittest.TestCase):
    def validate_fixture(self,change=None):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"source.json"
            j=fixture()
            if change:change(j)
            path.write_text(json.dumps(j),"utf-8")
            return validate(path)
    def test_no_candidates_is_a_legitimate_negative_result(self):
        r=self.validate_fixture()
        self.assertEqual(r["original_paragraphs"],347)
        self.assertFalse(r["all_347_paragraphs_time_aligned"])
    def test_cannot_fake_subtitle_timestamps(self):
        def f(j):j["original_source_cue_times_introduced"]=True
        with self.assertRaises(ValueError):self.validate_fixture(f)
    def test_source_video_must_match_source_inventory_size(self):
        def f(j):j["source_video_size_bytes"]+=1
        with self.assertRaises(ValueError):self.validate_fixture(f)
    def test_cannot_rewrite_model_match_data(self):
        def f(j):
            j["windows"][0]["distinct_high_lexical_match_candidates"]=3
            j["distinct_high_lexical_match_candidates_total"]=3
        with self.assertRaises(ValueError):self.validate_fixture(f)
    def test_unbounded_window_or_segments_rejected(self):
        def f(j):j["windows"][2]["source_window_ms"]=[660000,700000]
        with self.assertRaises(ValueError):self.validate_fixture(f)
    def test_source_transcript_remains_untimed(self):
        p=sources()
        self.assertTrue(all(x["start_ms"] is None for x in p))
        self.assertTrue(all(x["end_ms"] is None for x in p))

if __name__=="__main__":unittest.main()
