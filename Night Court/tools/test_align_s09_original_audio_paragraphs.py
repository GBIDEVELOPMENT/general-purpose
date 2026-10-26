#!/usr/bin/env python3
"""Offline tests for original S09 ASR→untimed paragraph time *proposals*."""
import unittest

from align_s09_original_audio_paragraphs import SCHEMA, align, tokens


def cue(n,t):
    return {"cue":n,"text":t,"start_ms":None,"end_ms":None}


def words(text,start=1000,step=180):
    import re
    return [{"text":t,"start_ms":start+i*step,"end_ms":start+(i+1)*step}
            for i,t in enumerate(text.split())]


class OriginalS09ParagraphAlignmentTests(unittest.TestCase):
    def test_source_paragraph_locator_does_not_promote_original_timecodes(self):
        para=[
            cue(1,"The first long distinct sentence describes a court scene."),
            cue(2,"Yes."),
            cue(3,"The second substantial dramatic passage clearly discusses the courtroom."),
        ]
        asr=words("the first long distinct sentence describes a court scene "
                  "some unrelated intermission words " 
                  "the second substantial dramatic passage clearly discusses the courtroom",10000)
        result=align(para,asr)
        self.assertEqual(result["schema"],SCHEMA)
        self.assertEqual(result["source_paragraphs"],3)
        self.assertEqual(result["candidate_source_paragraphs_given_audio_window"],2)
        self.assertEqual(result["unlocated_original_source_paragraphs"],1)
        self.assertEqual(result["exact_subtitle_timecode_recovered"],0)
        self.assertEqual(result["voice_names_independently_verified"],0)
        self.assertTrue(all(x["original_paragraph_timecode_ms"] is None for x in result["matches"]))
        self.assertTrue(all(x["original_film_audio_timing_independently_verified"] is False for x in result["matches"]))
        self.assertTrue(result["matches"][0]["candidate_original_audio_window_ms"][0]<
                        result["matches"][1]["candidate_original_audio_window_ms"][0])

    def test_absent_dialogue_abstains_no_fabricated_alignment(self):
        paragraphs=[cue(1,"This long exact phrase is not in the provided soundtrack.")]
        asr=words("Something completely different was heard during that particular scene now",8000)
        result=align(paragraphs,asr)
        self.assertEqual(result["candidate_source_paragraphs_given_audio_window"],0)
        self.assertEqual(result["unlocated_original_source_paragraphs"],1)

    def test_reordered_original_paragraphs_and_fictional_clocks_rejected(self):
        para=[cue(2,"A sensible sentence with enough exact lexical tokens")]
        with self.assertRaisesRegex(ValueError,"paragraph IDs not sequential"):
            align(para,words("a sensible sentence with enough exact lexical tokens"))
        para=[cue(1,"A sensible sentence with enough exact lexical tokens")]
        bad=[{"text":"A","start_ms":4000,"end_ms":3900}]
        with self.assertRaisesRegex(ValueError,"word timestamps"):
            align(para,bad)
        with self.assertRaises(ValueError):
            align(para,words("a sensible sentence with enough exact lexical tokens"),minimum_coverage=.1)

    def test_same_soundtrack_utterance_below_three_contiguous_words_abstains(self):
        para=[cue(1,"Wow."),cue(2,"Yeah."),cue(3,"Well.")]
        asr=words("Wow Yeah Well",3000)
        r=align(para,asr)
        self.assertEqual(r["candidate_source_paragraphs_given_audio_window"],0)
        self.assertEqual(r["unlocated_original_source_paragraphs"],3)


if __name__=="__main__":
    unittest.main()
