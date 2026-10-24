#!/usr/bin/env python3
"""Conservative untimed-original-source paragraph matcher for S09E19.

Matches ASR snippets against all original untimed source paragraphs. A proposed
alignment is NEVER a source subtitle timestamp or proof of completeness.
No external dependencies; synthetic offline regression before any FTP use.
"""
from __future__ import annotations
from difflib import SequenceMatcher
import re

WORDS=re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")

def tokens(text):
    return WORDS.findall(text.lower().replace("\u2019","'"))

def similarity(left,right):
    a,b=tokens(left),tokens(right)
    if len(a)<5 or len(b)<4:return 0.0
    # Balanced lexical similarity is more robust than a misleading substring
    # match for short repeated catchphrases or an unspoken source paragraph.
    count_a={}
    count_b={}
    for w in a:count_a[w]=count_a.get(w,0)+1
    for w in b:count_b[w]=count_b.get(w,0)+1
    shared=sum(min(n,count_b.get(w,0)) for w,n in count_a.items())
    if shared<3:return 0.0
    f1=2*shared/(len(a)+len(b))
    order=SequenceMatcher(None,a,b,autojunk=False).ratio()
    return round(.6*f1+.4*order,4)

def candidates(paragraphs):
    if len(paragraphs)!=347 or any(x["cue"]!=i+1 for i,x in enumerate(paragraphs)):
        raise ValueError("Exact 347 original untimed paragraphs required")
    rows=[]
    for start in range(len(paragraphs)):
        for length in (1,2,3):
            end=start+length
            if end>len(paragraphs):continue
            text=" ".join(x["text"] for x in paragraphs[start:end])
            if len(tokens(text))<4:continue
            rows.append({"source_first_paragraph":start+1,"source_last_paragraph":end,
                         "source_text":text})
    return rows

def assess(asr,candidate_rows):
    utterance=asr["text"]
    if len(tokens(utterance))<5:
        return {"asr_segment_index":asr["index"],"source_paragraph_candidate":None,
                "decision":"abstain_short_asr_phrase","source_timecode_invented":False,
                "top_matches":[]}
    ranking=sorted(({
        "source_first_paragraph":row["source_first_paragraph"],
        "source_last_paragraph":row["source_last_paragraph"],
        "similarity":similarity(utterance,row["source_text"])} for row in candidate_rows),
        key=lambda x:(-x["similarity"],x["source_first_paragraph"],
                      x["source_last_paragraph"]))
    # Treat overlapping candidates referring to the *same source passage* as
    # variants, not independent second-best evidence of unambiguity.
    distinct=[]
    for match in ranking:
        if not distinct or all(
            match["source_last_paragraph"]<v["source_first_paragraph"] or
            match["source_first_paragraph"]>v["source_last_paragraph"]
            for v in distinct):
            distinct.append(match)
        if len(distinct)>=4:break
    best=distinct[0]
    next_score=distinct[1]["similarity"] if len(distinct)>1 else 0
    unique=(best["similarity"]>=.75 and
            best["similarity"]-next_score>=.08 and
            best["similarity"]>=next_score*1.12)
    return {
        "asr_segment_index":asr["index"],
        "source_paragraph_candidate":{
            "first":best["source_first_paragraph"],"last":best["source_last_paragraph"]}
             if unique else None,
        "best_lexical_similarity":best["similarity"],
        "runner_up_similarity_nonoverlapping":next_score,
        "decision":"distinct_high_lexical_match_UNVERIFIED" if unique
                   else "abstain_low_or_ambiguous_lexical_evidence",
        "source_timecode_invented":False,
        "top_matches":distinct[:3]
    }

def score_windows(windows,paragraphs):
    bank=candidates(paragraphs)
    results=[]
    for window in windows:
        considered=[]
        for seg in window["asr_segments"]:
            match=assess(seg,bank)
            match["source_audio_interval_ms"]=[seg["start_ms"],seg["end_ms"]]
            match["asr_model_text"]=seg["text"]
            match["source_audio_segment_boundary_clipped"]=seg["segment_boundary_clipped"]
            if seg["segment_boundary_clipped"]:
                match["source_paragraph_candidate"]=None
                match["decision"]="abstain_audio_excerpt_boundary"
            considered.append(match)
        confident=[c for c in considered if c["source_paragraph_candidate"] is not None]
        candidate_numbers=[c["source_paragraph_candidate"]["first"] for c in confident]
        monotonically_increasing=all(x<y for x,y in zip(candidate_numbers,candidate_numbers[1:]))
        # Chronological/source order can support review priority, never certify
        # that any source subtitle paragraph was actually spoken at this time.
        results.append({
           "source_window_ms":window["source_window_ms"],
           "source_audio_sha256":window["source_audio_sha256"],
           "asr_segments":window["asr_segments"],
           "text_alignment_candidates":considered,
           "distinct_high_lexical_match_candidates":len(confident),
           "candidate_paragraph_order_monotonic":monotonically_increasing,
           "source_paragraphs_timed_or_verified":False
        })
    return results
