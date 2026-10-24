#!/usr/bin/env python3
"""No FTP/model: verify bounded S01E01 sampling and honest subtitle matches."""
import unittest
from s01e01_sparse_asr_drift_study import WINDOWS,caption_candidates,match,compare_windows,sources,ftp_connect_with_one_retry

class Windows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cues=sources()
    def test_schedule_from_first_quarter_through_final_minutes(self):
        self.assertEqual(WINDOWS,((300,330),(600,630),(900,930),(1200,1230),(1350,1380)))
        self.assertTrue(all(b-a==30 for a,b in WINDOWS))
        for (a,b),(c,d) in zip(WINDOWS,WINDOWS[1:]):
            self.assertLess(b,c)
        for start,end in WINDOWS:
            self.assertGreater(len(caption_candidates(self.cues,start,end)),0)
    def test_does_not_claim_exact_alignment_for_two_line_caption(self):
        cues=[{"cue":1,"start_ms":600000,"end_ms":602500,
                "text":"Hello. Good evening."}]
        m=match({"index":0,"text":"Hello, good evening.","start_ms":600260,
                 "end_ms":602050},cues,600,630)
        self.assertTrue(m["usable_for_global_drift_review"])
        self.assertEqual(m["candidate_start_offset_ms"],260)
        self.assertIn("not_verified",m["review_state"])
    def test_wrong_or_short_text_abstains(self):
        cues=[{"cue":1,"start_ms":600000,"end_ms":602500,"text":"Hello again"}]
        self.assertIsNone(match({"index":0,"text":"","start_ms":600020,"end_ms":600340},cues,600,630))
        x=match({"index":0,"text":"completely different words","start_ms":600020,"end_ms":601990},cues,600,630)
        self.assertFalse(x["usable_for_global_drift_review"])
    def test_clipped_asr_end_cannot_be_global_drift_anchor(self):
        cues=[{"cue":1,"start_ms":600000,"end_ms":602500,"text":"Hello, good evening."}]
        x=match({"index":0,"text":"Hello good evening","start_ms":600260,
                 "end_ms":602050,"segment_boundary_clipped":True},cues,600,630)
        self.assertFalse(x["usable_for_global_drift_review"])
        self.assertEqual(x["candidate_start_offset_ms"],260)
    def test_bounded_one_retry_only_on_connection_errors(self):
        attempts=[]
        def flaky(*args):
            attempts.append(args)
            if len(attempts)==1:raise TimeoutError("synthetic connect timeout")
            return "connected"
        sleeps=[]
        self.assertEqual(ftp_connect_with_one_retry(flaky,"test.host","user","dummy",
                         sleep=lambda s:sleeps.append(s)),"connected")
        self.assertEqual(len(attempts),2)
        self.assertEqual(sleeps,[4])
        def always_bad(*args):
            attempts.append(args)
            raise TimeoutError("connection unavailable")
        with self.assertRaises(TimeoutError):
            ftp_connect_with_one_retry(always_bad,"host","user","dummy",sleep=lambda _:None)
        self.assertEqual(len(attempts),4)
    def test_spread_metric_not_av_acceptance(self):
        example=[{"source_window_ms":[300000,330000],
                  "alignment_candidates":[{"usable_for_global_drift_review":True,"candidate_start_offset_ms":200}]*2},
                 {"source_window_ms":[1200000,1230000],
                  "alignment_candidates":[{"usable_for_global_drift_review":True,"candidate_start_offset_ms":500}]*2}]
        j=compare_windows(example)
        self.assertEqual(j["spread_between_window_median_start_differences_ms"],300)
        self.assertFalse(j["global_drift_verified"])
        self.assertFalse(j["global_video_to_subtitle_offset_verified"])

if __name__=="__main__":unittest.main()
