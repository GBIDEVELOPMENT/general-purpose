#!/usr/bin/env python3
"""Secondary subtitle time candidates MUST match every held original paragraph.

Synthetic times are test data ONLY, never imported as original movie times.
No public network or video/ASR usage during this QA.
"""
import unittest
from build_caption_first_working_drafts import witness
from probe_original_s09_public_srt_timing import analyze,build,candidates_from_visible_text

class TimedSecondaryWitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,metadata,cls.cues,_,_=witness("S09E19")
        assert metadata["timecoded"] is False
    def synthetic_html(self,tamper=None,omit=None,reorder=None):
        rows=[]
        for c in self.cues:
            n=c["cue"]
            if n==omit:continue
            at=(n*3000 if n!=reorder else 0)
            def clock(t):
                return f"{t//3600000:02d}:{t//60000%60:02d}:{t//1000%60:02d},{t%1000:03d}"
            body=c["text"]
            if n==tamper:body+=" FICTITIOUS SPEECH"
            rows.append(f"{n} {clock(at)} --> {clock(at+2000)} {body}\n")
        return ("<html><body><div>"+"".join(rows)+"</div></body></html>").encode()
    def test_complete_exact_secondary_witness_with_synthetic_time_only(self):
        body=self.synthetic_html()
        rows,details=analyze(body,self.cues)
        self.assertEqual(len(rows),347)
        self.assertEqual(rows[0]["cue"],1)
        self.assertEqual(rows[-1]["cue"],347)
        self.assertEqual(rows[-1]["candidate_start_ms"],347*3000)
        self.assertIsNotNone(details["selected_extract_mode"])
        proof=build(public_body=body)
        self.assertEqual(proof["status"],"SECONDARY_CUE_TIMES_ALL_SOURCE_TEXT_EXACT")
        self.assertEqual(proof["verified_secondary_timed_cues"],347)
        self.assertFalse(proof["original_video_synchronization_verified"])
        self.assertFalse(proof["original_witness_timestamps_edited"])
    def test_abstain_text_mutation_even_when_cue_numbers_match(self):
        proof=build(public_body=self.synthetic_html(tamper=113))
        self.assertEqual(proof["status"],"ABSTAIN_UNVERIFIED_SECONDARY_TIMING")
        self.assertEqual(proof["verified_secondary_timed_cues"],0)
    def test_abstain_missing_source_caption(self):
        proof=build(public_body=self.synthetic_html(omit=170))
        self.assertEqual(proof["status"],"ABSTAIN_UNVERIFIED_SECONDARY_TIMING")
        self.assertEqual(proof["verified_secondary_timed_cues"],0)
    def test_abstain_out_of_order_time(self):
        proof=build(public_body=self.synthetic_html(reorder=200))
        self.assertEqual(proof["status"],"ABSTAIN_UNVERIFIED_SECONDARY_TIMING")
    def test_original_public_page_rendered_without_times_remains_unknown(self):
        source_text="<html><body><h3>Original subtitles</h3>"+(" ".join(x["text"] for x in self.cues))+"</body></html>"
        proof=build(public_body=source_text.encode())
        self.assertEqual(proof["status"],"ABSTAIN_UNVERIFIED_SECONDARY_TIMING")
        self.assertFalse(proof["original_video_synchronization_verified"])

if __name__=="__main__":unittest.main()
