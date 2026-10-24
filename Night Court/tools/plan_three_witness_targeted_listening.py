#!/usr/bin/env python3
"""Source-pinned, overlap-deduplicated listening windows for 16 S01E01 conflicts.

The ASR agreement and the SRT timings are investigative pointers; listening
is required to determine words. Never correct or overwrite original subtitles.
No source audio/AVI is decoded, stored or published by this planner.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SUMMARY=ROOT/'seasons/S01/S01E01/derived/three-witness-v1/three-witness-summary.json'
QUEUE=ROOT/'seasons/S01/S01E01/derived/three-witness-v1/targeted-audio-review-queue.json'
VIDEO='5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962'
PCM='7fd284e99af1d69ca429496060c876241f181738666a86e8cb1335d5b869861a'
SRT='aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496'
DURATION_MS=1448256
CONTEXT_MS=600
MERGE_GAP_MS=250


def windows(summary, queue):
    if (summary.get('schema')!='night-court-s01e01-three-text-witness-preserved-summary/1'
        or summary.get('episode_id')!='S01E01'
        or summary.get('original_video_sha256')!=VIDEO
        or summary.get('original_audio_pcm_sha256')!=PCM
        or summary.get('original_srt_sha256')!=SRT
        or summary.get('original_srt_immutable') is not True
        or summary.get('words_independently_human_listened') is not False
        or summary.get('complete_original_episode_screenplay_accepted') is not False
        or summary.get('requires_targeted_source_audio_review')!=16):
        raise ValueError('Original three-witness S01E01 source identity changed')
    if not isinstance(queue,list) or len(queue)!=16:
        raise ValueError('Expected exact sixteen original-source disagreement cases')
    choices=[];seen_spans=set();seen_rank=set()
    for row in queue:
        if not isinstance(row,dict):
            raise ValueError('Malformed three-witness original source case')
        rank=row.get('review_rank_not_certainty')
        span=row.get('source_span_index')
        times=row.get('original_source_audio_time_ms')
        caption=row.get('caption_source_interval_ms')
        cues=row.get('original_srt_cue_ids')
        similarity=row.get('ordered_model_token_fraction_in_srt')
        if (type(rank) is not int or not 1<=rank<=16 or rank in seen_rank
            or type(span) is not int or not 0<=span<200 or span in seen_spans
            or not isinstance(times,list) or len(times)!=2
            or not isinstance(caption,list) or len(caption)!=2
            or any(type(x) is not int for x in times+caption)
            or not 0<=times[0]<times[1]<=DURATION_MS
            or not 0<=caption[0]<caption[1]<=DURATION_MS
            or not isinstance(cues,list) or not 1<=len(cues)<=4
            or any(type(c) is not int or not 1<=c<=336 for c in cues)
            or type(similarity) not in (int,float) or not 0<=similarity<1
            or row.get('classification')!='targeted_original_audio_listening_required'
            or row.get('model_error_or_srt_error_determined') is not False
            or row.get('episode_subtitle_or_script_auto_changed') is not False):
            raise ValueError('Original research disagreement was misrepresented')
        seen_rank.add(rank);seen_spans.add(span)
        lo=max(0,min(times[0],caption[0])-CONTEXT_MS)
        hi=min(DURATION_MS,max(times[1],caption[1])+CONTEXT_MS)
        if hi-lo>16000:
            raise ValueError('Unbounded individual original-source listening proposal')
        choices.append({'review_rank_not_certainty':rank,
            'two_model_agreement_span_index':span,
            'original_srt_cue_ids':cues,
            'model_audio_time_proposal_ms':times,
            'original_srt_time_reference_ms':caption,
            'caption_model_lexical_overlap_fraction':similarity,
            'playback_request_ms':[lo,hi],
            'original_performance_wording_human_verified':False,
            'corrected_caption_or_script_accepted':False})
    if seen_rank!=set(range(1,17)):
        raise ValueError('Original disagreement priorities are incomplete')
    groups=[]
    for item in sorted(choices,key=lambda i:i['playback_request_ms'][0]):
        a,z=item['playback_request_ms']
        if groups and a<=groups[-1]['playback_request_ms'][1]+MERGE_GAP_MS:
            group=groups[-1]
            group['playback_request_ms'][1]=max(group['playback_request_ms'][1],z)
            group['linked_review_ranks'].append(item['review_rank_not_certainty'])
            group['source_span_indices'].append(item['two_model_agreement_span_index'])
            group['caption_cue_ids']=sorted(set(group['caption_cue_ids']+item['original_srt_cue_ids']))
        else:
            groups.append({'playback_request_ms':[a,z],
                           'linked_review_ranks':[item['review_rank_not_certainty']],
                           'source_span_indices':[item['two_model_agreement_span_index']],
                           'caption_cue_ids':list(item['original_srt_cue_ids']),
                           'original_video_source_human_listened':False,
                           'disagreement_resolved':False,
                           'named_speaker_verified':False})
    if len(groups)>16:
        raise ValueError('Too many source audio review windows')
    return {
      'schema':'night-court-s01e01-three-witness-targeted-listening-plan/1',
      'episode_id':'S01E01',
      'original_video_sha256':VIDEO,'original_pcm_sha256':PCM,
      'original_srt_sha256':SRT,
      'source_duration_ms':DURATION_MS,
      'all_existing_disagreement_cases':len(choices),
      'distinct_short_listening_windows':len(groups),
      'playback_request_total_ms':sum(x['playback_request_ms'][1]-x['playback_request_ms'][0]
                                      for x in groups),
      'original_source_srt_modified':False,
      'new_original_source_speech_timestamps_created':False,
      'original_source_audio_listened':False,
      'dialogue_verified_or_speakers_identified':False,
      'complete_original_episode_screenplay_accepted':False,
      'ordered_by_disagreement_priority':sorted(choices,key=lambda i:i['review_rank_not_certainty']),
      'playback_windows_chronological':groups,
      'instructions':[
        'Directly listen to these short windows from the exact original AVI before adjudicating any wording.',
        'Audio ASR proposal intervals are not verified source word times; SRT timings are original caption references.',
        'Compare 16 disagreement cases without modifying the original SRT or claiming a verified speaker.',
        'Partially matched words, overlapping voices, omissions and timing drift must be evaluated separately.'
      ]
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error('Refusing overwrite of existing review evidence')
    result=windows(json.loads(SUMMARY.read_text('utf-8')),
                   json.loads(QUEUE.read_text('utf-8')))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(f"Sixteen real original-source disagreement cases in "
          f"{result['distinct_short_listening_windows']} overlapping-deduplicated "
          f"short windows ({result['playback_request_total_ms']/1000:.1f}s proposed listening); "
          "no original episode media decoded")


if __name__=='__main__':main()
