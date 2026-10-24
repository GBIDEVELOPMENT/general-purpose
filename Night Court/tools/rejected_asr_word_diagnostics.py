#!/usr/bin/env python3
"""Bounded, non-promoting diagnostic packets for rejected Whisper word times.

Preserves only original model hypotheses and nearby *independent model*
proposals so reviewers can target listening instead of whole-episode re-ASR.
"""
from __future__ import annotations
import math
from numbers import Real

MAX_REJECTED_ROWS=512
MAX_WORD_CHARS=80
MAX_CONTEXT_WORDS=4


def bounded_number(value):
    if isinstance(value,bool) or not isinstance(value,Real):
        return None
    number=float(value)
    return round(number,6) if math.isfinite(number) else None


def capture_rejection(sink, *, word, start, end, reason,
                      segment_start, segment_end, duration_ms):
    """Append bounded research-only detail, leave invalid model timings invalid."""
    if len(sink)>=MAX_REJECTED_ROWS:
        return False
    if type(duration_ms) is not int or not 1000<=duration_ms<=7200000:
        raise ValueError('Bad original audio source duration')
    if not isinstance(word,str) or len(word)>MAX_WORD_CHARS:
        text=None
    else:
        text=word
    if reason not in {
      'missing_empty_or_long_word','nonfinite_or_missing_model_time',
      'negative_original_time','zero_or_reversed_rounded_word_time',
      'beyond_decoded_original_soundtrack'
    }:
        raise ValueError('Unknown source-word timestamp rejection')
    start_number=bounded_number(start)
    end_number=bounded_number(end)
    segment_a=bounded_number(segment_start)
    segment_b=bounded_number(segment_end)
    proposed_segment=( [round(segment_a*1000),round(segment_b*1000)]
        if (segment_a is not None and segment_b is not None
            and 0<=segment_a<segment_b<=duration_ms/1000) else None )
    sink.append({
       'model_hypothesis_text':text,
       'rejection_reason':reason,
       'untrusted_raw_model_start_seconds':start_number,
       'untrusted_raw_model_end_seconds':end_number,
       'model_segment_interval_ms_proposal':proposed_segment,
       'model_proposed_original_source_word_interval_valid':False,
       'original_soundtrack_word_human_verified':False,
       'same_time_other_model_context_unverified':[]
    })
    return True


def add_independent_context(rows, other_model_words, duration_ms):
    """Point-only nearest proposals; never repair model time or infer speaker."""
    if len(rows)>MAX_REJECTED_ROWS or len(other_model_words)>15000:
        raise ValueError('Unbounded ASR diagnostics')
    prev=-1
    for w in other_model_words:
        a=w.get('start_ms')
        e=w.get('end_ms')
        if (type(a) is not int or type(e) is not int or
            not prev<=a<e<=duration_ms):
            raise ValueError('Unordered independent model word source hypotheses')
        prev=a
    for row in rows:
        a=row['untrusted_raw_model_start_seconds']
        e=row['untrusted_raw_model_end_seconds']
        if a is None or e is None or not 0<=a<=duration_ms/1000 or not 0<=e<=duration_ms/1000:
            continue
        # Invalid model duration (including a=b) remains invalid: this point
        # is an investigative cursor only, NOT a substitute word timestamp.
        point=round((a+e)*500)
        nearby=[]
        for w in other_model_words:
            if w['start_ms']-800<=point<=w['end_ms']+800:
                distance=min(abs(point-w['start_ms']),abs(point-w['end_ms']))
                nearby.append((distance,w['start_ms'],w))
        nearby.sort(key=lambda v:(v[0],v[1]))
        row['same_time_other_model_context_unverified']=[
            {'hypothesis_text':v[2]['text'][:MAX_WORD_CHARS],
             'model_proposed_time_ms':[v[2]['start_ms'],v[2]['end_ms']]}
            for v in nearby[:MAX_CONTEXT_WORDS]]
    return rows
