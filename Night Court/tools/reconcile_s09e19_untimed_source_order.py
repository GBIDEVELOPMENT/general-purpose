#!/usr/bin/env python3
"""Bounded source-text ordering QA for S09E19 original 347 untimed paragraphs.

Consumes already independently corroborated original-AUDIO hypotheses and
lexically compares at most 40 snippets to retained genuine untimed source text.
An alignment is NOT an original source caption timestamp or speaking identity.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import time
from match_s09e19_untimed_paragraphs import assess,candidates
from s09e19_untimed_video_anchor_pilot import sources,TXT_SHA

VIDEO_SHA='51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649'
MAX_PROBES=40


def verify(source):
    if (source.get('schema')!='night-court-s09e19-whole-source-once-cross-episode-benchmark/1'
        or source.get('episode_id')!='S09E19'
        or source.get('original_video_sha256')!=VIDEO_SHA
        or source.get('original_untimed_source_sha256')!=TXT_SHA
        or source.get('original_source_paragraphs')!=347
        or source.get('original_source_paragraphs_with_source_timecodes')!=0
        or source.get('source_untimed_paragraph_timestamps_created') is not False
        or source.get('episode_production_script_accepted') is not False
        or source.get('human_original_audio_listened') is not False):
        raise ValueError('Source S09E19 original untimed witness contract changed')
    rows=source.get('untimed_paragraph_lexical_candidates')
    if not isinstance(rows,list) or len(rows)>MAX_PROBES:
        raise ValueError('Too many original audio-to-untimed-source requests')
    duration=source.get('original_audio_duration_ms')
    if type(duration) is not int or not 1200000<=duration<=1800000:
        raise ValueError('Wrong original audiovisual source duration')
    last_index=-1;last_start=-1
    for entry in rows:
        if type(entry.get('consensus_span_index')) is not int or entry['consensus_span_index']<=last_index:
            raise ValueError('Consensus words not ordered by model output')
        last_index=entry['consensus_span_index']
        times=entry.get('original_avi_audio_time_proposal_ms')
        if (not isinstance(times,list) or len(times)!=2
            or any(type(x) is not int for x in times)
            or not 0<=times[0]<times[1]<=duration or times[0]<last_start):
            raise ValueError('Invalid original-AUDIO source interval hypothesis')
        last_start=times[0]
        if (entry.get('original_source_paragraph_time_ms') is not None
            or entry.get('word_identity_original_audio_human_verified') is not False):
            raise ValueError('Untimed original paragraph cannot inherit audio time')
        candidate=entry.get('untimed_original_source_paragraph_candidate')
        if candidate is not None and (not isinstance(candidate,dict)
            or type(candidate.get('first')) is not int
            or type(candidate.get('last')) is not int
            or not 1<=candidate['first']<=candidate['last']<=347):
            raise ValueError('Bad original source paragraph index candidate')
    return rows


def reconcile(source):
    rows=verify(source)
    paragraphs=sources()
    bank=candidates(paragraphs)
    begin=time.monotonic()
    review=[]
    for index,row in enumerate(rows):
        text=row.get('independent_model_agreed_text_hypothesis')
        if not isinstance(text,str) or len(text)>1000 or not text.strip():
            raise ValueError('No candidate independent model text evidence')
        evaluated=assess({'index':index,'text':text},bank)
        original_candidate=row['untimed_original_source_paragraph_candidate']
        if evaluated['source_paragraph_candidate']!=original_candidate:
            raise ValueError('Original whole-episode suggestion not reproducible from immutable untimed text')
        review.append({
          'source_agreement_span_index':row['consensus_span_index'],
          'model_source_audio_time_proposal_ms':row['original_avi_audio_time_proposal_ms'],
          'source_original_paragraph_candidate':original_candidate,
          'source_original_paragraph_timecode_ms':None,
          'best_independent_model_lexical_similarity':evaluated.get('best_lexical_similarity'),
          'next_nonoverlapping_lexical_similarity':evaluated.get('runner_up_similarity_nonoverlapping'),
          'lexical_match_decision':evaluated['decision'],
          'candidate_in_global_original_paragraph_order':False,
          'original_source_dialogue_human_verified':False,
          'speaking_character_identified':False
        })
    # Max-weight increasing subsequence of *unique* candidate paragraphs,
    # allowing missed source text, without hallucinating a one-to-one alignment.
    valid=[i for i,row in enumerate(review)
           if row['source_original_paragraph_candidate'] is not None]
    weight={i:max(.01,review[i]['best_independent_model_lexical_similarity']-.70) for i in valid}
    dp={};prev={}
    for i in valid:
        first=review[i]['source_original_paragraph_candidate']['first']
        choices=[j for j in valid if j<i and
                 review[j]['source_original_paragraph_candidate']['last']<first]
        best=max(choices,key=lambda j:dp[j],default=None)
        dp[i]=weight[i]+(dp[best] if best is not None else 0)
        prev[i]=best
    selected=set()
    if valid:
        at=max(valid,key=lambda i:(dp[i],-i))
        while at is not None:
            selected.add(at)
            at=prev[at]
    for i,row in enumerate(review):
        row['candidate_in_global_original_paragraph_order']=i in selected
        row['review_status']=('order_consistent_lexical_anchor_candidate'
             if i in selected else 'unresolved_or_out_of_order_model_lexical_hypothesis')
    return {
      'schema':'night-court-s09e19-untimed-ordered-machine-anchors/1',
      'episode_id':'S09E19',
      'original_source_video_sha256':VIDEO_SHA,
      'original_untimed_source_sha256':TXT_SHA,
      'source_paragraph_count':347,
      'original_source_paragraphs_with_timecodes':0,
      'independent_agreement_spans_considered':len(rows),
      'uniquely_lexical_matches_before_ordering':len(valid),
      'order_consistent_candidate_anchors':len(selected),
      'candidate_anchor_sort_stage_wall_seconds':round(time.monotonic()-begin,3),
      'source_original_text_modified':False,
      'new_original_source_timecodes_created':False,
      'speakers_and_continuous_actions_verified':False,
      'production_script_accepted':False,
      'review_cases':review,
      'limitations':[
         'Order-consistent candidates align audio-model claims to paragraphs; original paragraphs remain untimed.',
         'Machine-audio agreement can repeat shared errors and source text may differ from exact original dialogue.',
         'Unique lexical evidence and monotonicity are not proof of audio/source synchronization or omitted text.',
         'All candidate text is research; speaker identity, delivery and full screenplay acceptance are separate.'
      ]
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error('Refuse evidence overwrite')
    result=reconcile(json.loads(args.input.read_text('utf-8')))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print('Original 347 paragraphs retained untimed; '
          f"{result['order_consistent_candidate_anchors']} of "
          f"{result['independent_agreement_spans_considered']} input model spans "
          'offer ordered lexical anchors; source dialogue not accepted')


if __name__=='__main__':
    main()
