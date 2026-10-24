#!/usr/bin/env python3
"""One-fast-pass comparison of two ASR-decoder consensus with ORIGINAL subtitle.

This is a third *textual witness comparison*, not model word ground truth,
source-media synchronization, named speaker inference, script completion or
audio/listener verification. Neither ASR decoder may be prompted with subtitles.
"""
from __future__ import annotations
import argparse
from bisect import bisect_left,bisect_right
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SRT=ROOT/'seasons/S01/S01E01/dialogue/versions/s01-internal-dvdrip-xvid-sprinter-english--aa9f77600cd9f2b6/original.srt'
VIDEO_SHA='5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962'
SRT_SHA='aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496'
SRT_SOURCE_BYTE_ENCODING='cp1252'  # Legacy Western DVD transcription; SHA is of original bytes
MARGIN_MS=2000
MIN_WORDS=3
MAX_SPANS=4000


def sha(path:Path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def words(text):
    return re.findall(r"\w+(?:['’]\w+)?",text.casefold())


def parse_time(ts):
    m=re.fullmatch(r'(\d{2}):(\d{2}):(\d{2})[,\.](\d{3})',ts)
    if not m:raise ValueError('Invalid exact original subtitle timecode')
    h,minute,sec,ms=map(int,m.groups())
    if minute>=60 or sec>=60:raise ValueError('Invalid original subtitle clock')
    return ((h*60+minute)*60+sec)*1000+ms


def srt_cues(source):
    content=source.replace('\r\n','\n').replace('\r','\n')
    cues=[]
    seen=set()
    for raw in re.split(r'\n\s*\n',content.strip()):
        lines=raw.strip().splitlines()
        if not lines:continue
        if len(lines)<3 or not lines[0].strip().isdigit():
            raise ValueError('Malformed original caption cue')
        num=int(lines[0].strip())
        if num in seen:raise ValueError('Duplicate original cue number')
        seen.add(num)
        times=re.fullmatch(r'\s*(\S+)\s+-->\s+(\S+)(?:\s+.*)?',lines[1])
        if not times:raise ValueError('Malformed original subtitle timestamp')
        a,b=map(parse_time,times.groups())
        if not 0<=a<b<=7200000:raise ValueError('Bad SRT cue source interval')
        text=' '.join(x.strip() for x in lines[2:])
        if not text or not words(text):raise ValueError('Blank original subtitle witness')
        cues.append({'cue_id':num,'source_caption_interval_ms':[a,b],
                     'source_text':text,'normalized_tokens':words(text)})
    if not cues:raise ValueError('Empty original SRT')
    if any(cues[i]['source_caption_interval_ms'][0]<
           cues[i-1]['source_caption_interval_ms'][0] for i in range(1,len(cues))):
        raise ValueError('Original subtitle cues not time ordered')
    return cues


def match_consensus_to_srt(two_model_result,original_source_text):
    if (two_model_result.get('schema')!='night-court-original-full-episode-dual-independent-asr-cost-and-agreement/1'
        or two_model_result.get('episode_id')!='S01E01'
        or two_model_result.get('original_video_sha256')!=VIDEO_SHA
        or two_model_result.get('model_original_srt_prompted') is not False
        or two_model_result.get('original_audio_human_listened') is not False):
        raise ValueError('Untrusted original video or prompt-contaminated model dialogue')
    agreement=two_model_result.get('comparison',{})
    if (agreement.get('schema')!='night-court-independent-asr-corroboration/1'
        or agreement.get('original_video_sha256')!=VIDEO_SHA
        or agreement.get('source_window_ms')!=[0,two_model_result.get('source_audio_duration_ms')]
        or agreement.get('decoded_audio_sha256')!=two_model_result.get('decoded_audio_sha256')
        or {x.get('architecture_family') for x in agreement.get('models',[])}
             !={'whisper','kaldi_hmm_wfst'}):
        raise ValueError('Independent source audio/model family matching not established')
    raw=agreement.get('corroborated_spans')
    if not isinstance(raw,list) or len(raw)>MAX_SPANS:
        raise ValueError('Unbounded full original episode consensus spans')
    cue_entries=srt_cues(original_source_text)
    starts=[c['source_caption_interval_ms'][0] for c in cue_entries]
    results=[]
    for i,span in enumerate(raw):
        timecode=span.get('time_interval_ms')
        dialogue=span.get('model_a_verbatim_candidate')
        if (not isinstance(timecode,list) or len(timecode)!=2
            or any(type(t) is not int for t in timecode)
            or not 0<=timecode[0]<timecode[1]<=two_model_result['source_audio_duration_ms']
            or not isinstance(dialogue,str) or len(dialogue)>3000):
            raise ValueError('Invalid original source consensus interval/word span')
        tokens=words(dialogue)
        if span.get('word_count',0)<MIN_WORDS or len(tokens)<MIN_WORDS:
            raise ValueError('Insufficient independently agreeing consecutive model words')
        first=max(0,bisect_left(starts,timecode[0]-MARGIN_MS)-3)
        last=bisect_right(starts,timecode[1]+MARGIN_MS)
        pool=[c for c in cue_entries[first:last]
              if c['source_caption_interval_ms'][1]>=timecode[0]-MARGIN_MS]
        best=None
        for c in pool:
            common=SequenceMatcher(None,tokens,c['normalized_tokens'],autojunk=False).find_longest_match()
            fraction=common.size/len(tokens)
            if not best or (fraction,-abs(c['source_caption_interval_ms'][0]-timecode[0])) > (best[0],best[1]):
                best=(fraction,-abs(c['source_caption_interval_ms'][0]-timecode[0]),c)
        fraction=round(best[0],4) if best else 0.0
        cue=best[2] if best else None
        cls=('no_original_caption_in_candidate_interval'
             if not cue else 'three_text_witness_correspondence_candidate'
             if fraction>=.8 else 'two_model_agreement_caption_lexical_disagreement')
        results.append({'span_index':i,'model_agreed_text_candidate':dialogue,
            'model_word_count':span['word_count'],
            'model_consensus_interval_ms':timecode,
            'nearest_source_caption_cue_id':cue['cue_id'] if cue else None,
            'source_caption_interval_ms':cue['source_caption_interval_ms'] if cue else None,
            'source_caption_verbatim':cue['source_text'] if cue else None,
            'longest_contiguous_token_coverage':fraction,
            'review_tier':cls,
            'original_srt_changed':False,
            'source_audio_human_listened':False,
            'source_video_lip_or_speaker_identity_accepted':False})
    counts={k:sum(t['review_tier']==k for t in results) for k in
            ('three_text_witness_correspondence_candidate',
             'two_model_agreement_caption_lexical_disagreement',
             'no_original_caption_in_candidate_interval')}
    if sum(counts.values())!=len(results):
        raise ValueError('Missing any full episode consensus span classification')
    return {'schema':'night-court-whole-s01e01-two-independent-models-plus-original-caption/1',
        'original_video_sha256':VIDEO_SHA,'source_caption_sha256':SRT_SHA,
        'decoded_audio_sha256':two_model_result['decoded_audio_sha256'],
        'source_audio_duration_ms':two_model_result['source_audio_duration_ms'],
        'original_srt_cues':len(cue_entries),
        'independent_model_consensus_spans':len(raw),
        'classification_counts':counts,
        'review_spans':results,
        'original_source_srt_modified':False,
        'original_soundtrack_human_listening_completed':False,
        'subtitle_video_edition_sync_confirmed':False,
        'source_character_speaker_identity_confirmed':False,
        'full_production_script_verified':False,
        'limits':['Model consensus and source subtitle lexical/time proximity are research correspondence candidates.',
                  'Caption original clock may drift from the verified original AVI; ±2 seconds is an exploratory window.',
                  'A cue includes multiple speaker hyphen lines and may exceed a short model agreement span.',
                  'A third text witness reduces review effort but does not attest lips, names or physical actions.']}


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--source-two-model-json',required=True,type=Path)
    a.add_argument('--output',required=True,type=Path)
    args=a.parse_args()
    if args.output.exists():a.error('Refuse to overwrite source evidence')
    if sha(SOURCE_SRT)!=SRT_SHA:
        raise ValueError('Original subtitle bytes changed')
    data=json.loads(args.source_two_model_json.read_text('utf-8'))
    report=match_consensus_to_srt(data,SOURCE_SRT.read_bytes().decode(SRT_SOURCE_BYTE_ENCODING))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n','utf-8')
    print(f"{report['independent_model_consensus_spans']} original consensus spans vs "
          f"{report['original_srt_cues']} source subtitle cues: {report['classification_counts']}; "
          'no original dialogue/prompts altered')


if __name__=='__main__':
    main()
