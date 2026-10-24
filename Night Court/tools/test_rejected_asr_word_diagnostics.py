#!/usr/bin/env python3
"""Zero-source targeted rejected-word timestamp diagnostic tests."""
from __future__ import annotations
import math
import unittest
from rejected_asr_word_diagnostics import (
    capture_rejection,add_independent_context,MAX_REJECTED_ROWS
)

DURATION=1320144


def add(sink, start=10.0, end=10.0, reason='zero_or_reversed_rounded_word_time'):
    return capture_rejection(sink,word=' conjecture',start=start,end=end,
           reason=reason,segment_start=9.5,segment_end=12.0,duration_ms=DURATION)


class RejectDiagnostics(unittest.TestCase):
    def test_zero_duration_remains_invalid_with_independent_context(self):
        rows=[]
        self.assertTrue(add(rows))
        other=[
          {'text':'possibility','start_ms':9500,'end_ms':10200},
          {'text':'surely','start_ms':10200,'end_ms':10500},
          {'text':'later','start_ms':50000,'end_ms':52000}]
        add_independent_context(rows,other,DURATION)
        r=rows[0]
        self.assertEqual(r['untrusted_raw_model_start_seconds'],10.0)
        self.assertEqual(r['untrusted_raw_model_end_seconds'],10.0)
        self.assertFalse(r['model_proposed_original_source_word_interval_valid'])
        self.assertFalse(r['original_soundtrack_word_human_verified'])
        self.assertEqual(len(r['same_time_other_model_context_unverified']),2)
        self.assertEqual(r['model_segment_interval_ms_proposal'],[9500,12000])
        self.assertNotIn('source_original_paragraph_timestamp',r)

    def test_nan_and_negative_dont_become_timestamps(self):
        rows=[]
        add(rows,start=math.nan,end=10,reason='nonfinite_or_missing_model_time')
        self.assertIsNone(rows[0]['untrusted_raw_model_start_seconds'])
        add(rows,start=-1,end=1,reason='negative_original_time')
        add_independent_context(rows,[{'text':'x','start_ms':0,'end_ms':1000}],DURATION)
        self.assertEqual(rows[0]['same_time_other_model_context_unverified'],[])
        self.assertEqual(rows[1]['same_time_other_model_context_unverified'],[])

    def test_byte_cap_and_unsafe_word_rejection(self):
        rows=[]
        self.assertTrue(capture_rejection(rows,word='x'*100,start=2,end=2,
           reason='zero_or_reversed_rounded_word_time',
           segment_start=1,segment_end=3,duration_ms=DURATION))
        self.assertIsNone(rows[0]['model_hypothesis_text'])
        for _ in range(MAX_REJECTED_ROWS-1):add(rows)
        self.assertFalse(add(rows))
        self.assertEqual(len(rows),MAX_REJECTED_ROWS)

    def test_invalid_other_model_proposals_fail_closed(self):
        rows=[]
        add(rows)
        with self.assertRaisesRegex(ValueError,'Unordered'):
            add_independent_context(rows,[{'text':'x','start_ms':200,'end_ms':300},
             {'text':'y','start_ms':100,'end_ms':200}],DURATION)
        with self.assertRaisesRegex(ValueError,'Unbounded'):
            add_independent_context([{}]*(MAX_REJECTED_ROWS+1),[],DURATION)


if __name__=='__main__':
    unittest.main()
