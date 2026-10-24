#!/usr/bin/env python3
"""Offline regression for safe paragraph matching. No audio/model downloads."""
import unittest
from match_s09e19_untimed_paragraphs import assess,candidates,score_windows,tokens,similarity
from s09e19_untimed_video_anchor_pilot import exact_candidate,sources,WINDOWS,TXT_SHA

class SourceMatchTests(unittest.TestCase):
    def test_s09e19_source_and_video_selection(self):
        p=sources()
        self.assertEqual(len(p),347)
        self.assertEqual(p[0]["cue"],1)
        self.assertTrue(all(x["start_ms"] is None and x["end_ms"] is None for x in p))
        c=exact_candidate()
        self.assertEqual(c["size_bytes"],183377920)
        self.assertEqual(c["episode_id_from_filename"],"S09E19")
        self.assertEqual(len(WINDOWS),5)
        self.assertTrue(all(b-a==25 for a,b in WINDOWS))
    def fixture(self):
        return [{"cue":i+1,
                 "text":f"Default hypothetical testing paragraph number {i} with generic content",
                 "start_ms":None,"end_ms":None} for i in range(347)]
    def test_unique_sentence_high_match_only_candidate(self):
        paragraphs=self.fixture()
        phrase="Amber orbits chromium while velvet moons descend tonight"
        paragraphs[42]["text"]=phrase
        bank=candidates(paragraphs)
        result=assess({"index":0,"text":phrase},bank)
        self.assertEqual(result["source_paragraph_candidate"],{"first":43,"last":43})
        self.assertEqual(result["decision"],"distinct_high_lexical_match_UNVERIFIED")
        self.assertFalse(result["source_timecode_invented"])
    def test_repeated_phrase_is_ambiguous(self):
        paragraphs=self.fixture()
        phrase="Amber orbits chromium while velvet moons descend tonight"
        paragraphs[10]["text"]=paragraphs[240]["text"]=phrase
        result=assess({"index":0,"text":phrase},candidates(paragraphs))
        self.assertIsNone(result["source_paragraph_candidate"])
        self.assertEqual(result["decision"],"abstain_low_or_ambiguous_lexical_evidence")
    def test_short_generic_asr_abstains(self):
        x=assess({"index":0,"text":"Yes indeed."},candidates(self.fixture()))
        self.assertEqual(x["decision"],"abstain_short_asr_phrase")
    def test_boundary_clipped_audio_never_promotes_match(self):
        phrase="Amber orbits chromium while velvet moons descend tonight"
        paragraphs=self.fixture()
        paragraphs[75]["text"]=phrase
        item={"index":0,"start_ms":180000,"end_ms":183000,
              "segment_boundary_clipped":True,"text":phrase}
        window={"source_window_ms":[180000,205000],"source_audio_sha256":"f"*64,
                "asr_segments":[item]}
        matched=score_windows([window],paragraphs)[0]
        self.assertIsNone(matched["text_alignment_candidates"][0]["source_paragraph_candidate"])
        self.assertFalse(matched["source_paragraphs_timed_or_verified"])
    def test_low_information_noise_does_not_fake_score(self):
        self.assertEqual(similarity("No.", "No problem at all."),0)
        self.assertEqual(tokens("What’s that?"),["what's","that"])

if __name__=="__main__":unittest.main()
