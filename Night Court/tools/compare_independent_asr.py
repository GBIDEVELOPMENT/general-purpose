#!/usr/bin/env python3
"""Fast two-decoder word/time corroboration, not a source-audio or identity review.

Requires genuinely different declared architecture families and no caption hints.
Recognizers may have correlated errors despite that separation. Outputs strongly
matched continuous *machine* spans and explicit unresolved word candidates.
"""
from __future__ import annotations
import argparse
from bisect import bisect_left
from collections import defaultdict
import json
import re
import unicodedata
from pathlib import Path

WINDOW_TOLERANCE_MS=600
MAX_WORDS=15000
MIN_SPAN_WORDS=3
ALLOWED_FAMILIES={'whisper','ctc','conformer_ctc','rnnt','seq2seq_other'}


def normalized(text):
    return re.sub(r'[^\w]+','',unicodedata.normalize('NFKC',text).casefold())


def positive_int(value, maximum):
    if type(value) is not int or not 0<=value<=maximum:
        raise ValueError('Invalid integer time/bound')
    return value


def get_words(model, start, end):
    if (model.get('architecture_family') not in ALLOWED_FAMILIES
        or not isinstance(model.get('model_id'),str) or not model['model_id'].strip()
        or model.get('free_decoding') is not True
        or model.get('srt_or_other_model_prompt_used') is not False):
        raise ValueError('Free decoding provenance and model architecture required')
    words=model.get('words')
    if not isinstance(words,list) or len(words)>MAX_WORDS:
        raise ValueError('Unbounded model transcript')
    result=[]
    previous=-1
    for idx,w in enumerate(words):
        if not isinstance(w,dict) or not isinstance(w.get('text'),str):
            raise ValueError('Invalid model word')
        a=positive_int(w.get('start_ms'),end)
        b=positive_int(w.get('end_ms'),end)
        if a<start or a>=b or a<previous or not normalized(w['text']):
            raise ValueError('Invalid, empty or unordered word timing')
        previous=a
        result.append({'index':idx,'start_ms':a,'end_ms':b,
                       'midpoint_ms':(a+b)//2,'token':normalized(w['text']),
                       'verbatim_text':w['text']})
    return result


def compare(spec):
    if spec.get('schema')!='night-court-two-independent-asr-words/1':
        raise ValueError('Unrecognized consensus input')
    if not re.fullmatch(r'S0[1-9]E\d{2}',str(spec.get('episode_id'))):
        raise ValueError('Invalid original-series episode ID')
    for key in ('source_video_sha256','decoded_audio_sha256'):
        if not re.fullmatch(r'[a-f0-9]{64}',str(spec.get(key))):
            raise ValueError('Missing source/audio SHA256')
    window=spec.get('source_window_ms')
    if (not isinstance(window,list) or len(window)!=2):
        raise ValueError('Expected one bounded source window')
    start=positive_int(window[0],7200000)
    end=positive_int(window[1],7200000)
    if end<=start:raise ValueError('Invalid source window')
    models=spec.get('models')
    if not isinstance(models,list) or len(models)!=2:
        raise ValueError('Exactly two independently decoded model witnesses required')
    if models[0].get('architecture_family')==models[1].get('architecture_family') or models[0].get('model_id')==models[1].get('model_id'):
        raise ValueError('Model pair has shared family or duplicate identity')
    a=get_words(models[0],start,end)
    b=get_words(models[1],start,end)
    # Index candidate words by normalized token and timestamp. O(N log M),
    # not quadratic all-against-all word alignment across 24 minutes.
    buckets=defaultdict(list)
    for w in b:buckets[w['token']].append((w['midpoint_ms'],w['index']))
    for rows in buckets.values():rows.sort()
    aligned=[]
    previous_b=-1
    for aw in a:
        options=buckets.get(aw['token'],[])
        needle=bisect_left(options,(aw['midpoint_ms'],-1))
        nearby=options[max(0,needle-4):needle+5]
        valid=[(abs(t-aw['midpoint_ms']),idx) for t,idx in nearby
               if idx>previous_b and abs(t-aw['midpoint_ms'])<=WINDOW_TOLERANCE_MS]
        if not valid:continue
        distance,j=min(valid)
        aligned.append((aw['index'],j,distance))
        previous_b=j
    # Keep only runs of >=3 aligned consecutive words. Single-word consensus
    # is evidence too, but insufficient to promote a whole utterance here.
    runs=[];current=[]
    for pair in aligned:
        if current and (pair[0]!=current[-1][0]+1 or pair[1]!=current[-1][1]+1
                        or a[pair[0]]['start_ms']-a[current[-1][0]]['end_ms']>1500
                        or b[pair[1]]['start_ms']-b[current[-1][1]]['end_ms']>1500):
            runs.append(current);current=[]
        current.append(pair)
    if current:runs.append(current)
    spans=[];accepted_a=set();accepted_b=set()
    for run in runs:
        if len(run)<MIN_SPAN_WORDS:continue
        for i,j,_ in run:accepted_a.add(i);accepted_b.add(j)
        spans.append({'model_a_word_range':[run[0][0],run[-1][0]],
                      'model_b_word_range':[run[0][1],run[-1][1]],
                      'time_interval_ms':[min(a[run[0][0]]['start_ms'],b[run[0][1]]['start_ms']),
                                          max(a[run[-1][0]]['end_ms'],b[run[-1][1]]['end_ms'])],
                      'model_a_verbatim_candidate':' '.join(a[i]['verbatim_text'] for i,_,_ in run),
                      'word_count':len(run),
                      'largest_model_time_disagreement_ms':max(k for _,_,k in run),
                      'classification':'independently_machine_corroborated_dialogue_candidate',
                      'original_audio_human_reviewed':False,
                      'speaker_character_identified':False})
    unresolved=[{'model':'A','word_index':x['index'],'time_ms':x['midpoint_ms'],
                 'verbatim_candidate':x['verbatim_text']} for x in a if x['index'] not in accepted_a]
    unresolved +=[{'model':'B','word_index':x['index'],'time_ms':x['midpoint_ms'],
                   'verbatim_candidate':x['verbatim_text']} for x in b if x['index'] not in accepted_b]
    unresolved.sort(key=lambda x:(x['time_ms'],x['model'],x['word_index']))
    return {'schema':'night-court-independent-asr-corroboration/1',
            'episode_id':spec['episode_id'],
            'original_video_sha256':spec['source_video_sha256'],
            'decoded_audio_sha256':spec['decoded_audio_sha256'],
            'source_window_ms':[start,end],
            'models':[{'model_id':m['model_id'],'architecture_family':m['architecture_family']}
                      for m in models],
            'counts':{'a_words':len(a),'b_words':len(b),'paired_words':len(aligned),
                      'corroborated_words':len(accepted_a),'corroborated_spans':len(spans),
                      'unresolved_word_candidates':len(unresolved)},
            'corroborated_spans':spans,'unresolved':unresolved,
            'two_models_do_not_prove_statistically_independent_errors':True,
            'original_source_audio_listened':False,
            'source_srt_verified':False,
            'speakers_or_full_screenplay_verified':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    x=p.parse_args()
    if x.output.exists():p.error('Refuse overwrite of prior ASR consensus evidence')
    report=compare(json.loads(x.input.read_text('utf-8')))
    x.output.parent.mkdir(parents=True,exist_ok=True)
    x.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n','utf-8')
    print(f"Corroborated {report['counts']['corroborated_words']} machine words across "
          f"{report['counts']['corroborated_spans']} spans; no original audio review claimed")

if __name__=='__main__':main()
