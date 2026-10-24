#!/usr/bin/env python3
"""Preserve SHA-pinned original-series two-ASR-plus-SRT research evidence.

Accepts only the known 200-span original S01E01 source research artifact.
Never accepts screenplay completion, speaker names or human listening claims.
Exports a full *derived* review witness and a compact, independently ranked
16-case triage queue. Original SRT remains untouched.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL_SRT=ROOT/'seasons/S01/S01E01/dialogue/versions/s01-internal-dvdrip-xvid-sprinter-english--aa9f77600cd9f2b6/original.srt'
SOURCE_JSON_SHA='4203b5550bad8e0a56bc9316144011f53e3e677fea3545dd3eab868a2f0019e5'
AVI_SHA='5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962'
SRT_SHA='aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496'
AUDIO_SHA='7fd284e99af1d69ca429496060c876241f181738666a86e8cb1335d5b869861a'
SOURCE_RUN=40116865728
ARTIFACT_ID=12569465735
ARTIFACT_ZIP_SHA='5130d3b61375e94b08165e7dec2dc9aa74423a9a13de6d499e32cd4d3fc1cd6d'
STATUS_KEYS=('three_text_witness_correspondence_candidate',
             'two_model_agreement_caption_lexical_disagreement',
             'no_original_caption_in_candidate_interval')


def digest(blob:bytes):
    return hashlib.sha256(blob).hexdigest()


def validate_source(data:dict,raw_sha:str,*,strict_original=True):
    if strict_original and raw_sha!=SOURCE_JSON_SHA:
        raise ValueError('S01E01 source three-witness JSON hash changed')
    if (not isinstance(data,dict)
        or data.get('schema')!='night-court-whole-s01e01-two-independent-models-plus-original-caption/1'
        or data.get('original_video_sha256')!=AVI_SHA
        or data.get('source_caption_sha256')!=SRT_SHA
        or data.get('decoded_audio_sha256')!=AUDIO_SHA
        or data.get('source_audio_duration_ms')!=1448256
        or data.get('original_srt_cues')!=336
        or data.get('independent_model_consensus_spans')!=200):
        raise ValueError('Unexpected original source witness fingerprint or coverage')
    for name in ('original_source_srt_modified','original_soundtrack_human_listening_completed',
                 'subtitle_video_edition_sync_confirmed',
                 'source_character_speaker_identity_confirmed','full_production_script_verified'):
        if data.get(name) is not False:
            raise ValueError('Unverified production or source claim must remain false: '+name)
    if (not isinstance(data.get('review_spans'),list)
        or len(data['review_spans'])!=200):
        raise ValueError('Original source model agreement requires exactly 200 spans')
    summary={key:0 for key in STATUS_KEYS}
    previous=-1
    for expected_index,row in enumerate(data['review_spans']):
        if not isinstance(row,dict) or row.get('span_index')!=expected_index:
            raise ValueError('Non-unique or out-of-sequence original ASR agreement span')
        interval=row.get('model_consensus_interval_ms')
        if (not isinstance(interval,list) or len(interval)!=2
            or any(type(x) is not int for x in interval)
            or not 0<=interval[0]<interval[1]<=1448256
            or interval[0]<previous):
            raise ValueError('Invalid source-audio presentation interval')
        previous=interval[0]
        if (type(row.get('model_word_count')) is not int
            or not 3<=row['model_word_count']<=200
            or not isinstance(row.get('model_agreed_text_candidate'),str)
            or not row['model_agreed_text_candidate'].strip()
            or len(row['model_agreed_text_candidate'])>3000):
            raise ValueError('Malformed model agreement text/word count')
        status=row.get('review_tier')
        if status not in summary:
            raise ValueError('Unknown original caption agreement category')
        summary[status]+=1
        source_ids=row.get('source_caption_cue_ids')
        if (not isinstance(source_ids,list) or len(source_ids)>4
            or any(type(x) is not int or not 1<=x<=336 for x in source_ids)):
            raise ValueError('Invalid source SRT cue IDs')
        for f in ('ordered_matched_model_token_fraction','longest_contiguous_token_coverage'):
            s=row.get(f)
            if type(s) not in (float,int) or not 0<=s<=1:
                raise ValueError('Invalid caption overlap candidate fraction')
        if (row.get('original_srt_changed') is not False
            or row.get('source_audio_human_listened') is not False
            or row.get('source_video_lip_or_speaker_identity_accepted') is not False):
            raise ValueError('Candidate may not promote human AV acceptance')
    if summary!={STATUS_KEYS[0]:184,STATUS_KEYS[1]:16,STATUS_KEYS[2]:0}:
        raise ValueError('Unexpected original 200-span / 16-conflict proportions')
    if data.get('classification_counts')!=summary:
        raise ValueError('Source header classifications disagree with individual spans')
    return summary


def make_outputs(raw_bytes:bytes,*,strict_original=True):
    data=json.loads(raw_bytes)
    sha=digest(raw_bytes)
    summary=validate_source(data,sha,strict_original=strict_original)
    if digest(ORIGINAL_SRT.read_bytes())!=SRT_SHA:
        raise ValueError('Immutable original S01E01 SRT bytes changed')
    conflicts=[r for r in data['review_spans']
               if r['review_tier']!='three_text_witness_correspondence_candidate']
    # A shorter conflict span has weaker lexical support, but low similarity
    # does not establish the models or caption are wrong: human/source task.
    conflicts.sort(key=lambda r:(r['ordered_matched_model_token_fraction'],
                                 r['model_consensus_interval_ms'][0]))
    queue=[]
    for rank,case in enumerate(conflicts,1):
        queue.append({
            'review_rank_not_certainty':rank,
            'source_span_index':case['span_index'],
            'original_source_audio_time_ms':case['model_consensus_interval_ms'],
            'original_srt_cue_ids':case['source_caption_cue_ids'],
            'caption_source_interval_ms':case['source_caption_interval_ms'],
            'two_model_agreed_words_hypothesis':case['model_agreed_text_candidate'],
            'original_srt_verbatim_for_comparison':case['source_caption_verbatim'],
            'ordered_model_token_fraction_in_srt':case['ordered_matched_model_token_fraction'],
            'classification':'targeted_original_audio_listening_required',
            'model_error_or_srt_error_determined':False,
            'episode_subtitle_or_script_auto_changed':False
        })
    meta={
        'schema':'night-court-s01e01-three-text-witness-preserved-summary/1',
        'episode_id':'S01E01',
        'original_video_sha256':AVI_SHA,
        'original_audio_pcm_sha256':AUDIO_SHA,
        'original_srt_sha256':SRT_SHA,
        'original_three_witness_json_sha256':sha,
        'original_three_witness_private_zip_sha256':ARTIFACT_ZIP_SHA,
        'trusted_original_source_run_id':SOURCE_RUN,
        'original_private_artifact_id':ARTIFACT_ID,
        'original_private_artifact_expiry_utc':'2026-10-31T17:36:24Z',
        'original_srt_cues':336,
        'independent_model_agreement_spans':200,
        'span_level_classification_counts':summary,
        'model_consensus_spans_with_srt_correspondence_fraction':184/200,
        'requires_targeted_source_audio_review':len(queue),
        'model_two_model_agreement_is_positive_machine_corroboration':True,
        'original_srt_immutable':True,
        'words_independently_human_listened':False,
        'speaker_character_identity_accepted':False,
        'complete_original_episode_screenplay_accepted':False,
        'per_episode_production_run_time_not_measured_here':True,
        'limits':[
            '184/200 is span-level source subtitle correspondence, not a word-error-rate or precision estimate.',
            'Two recognizers and a third source SRT are three text witnesses, not three statistically independent acoustical transcriptions.',
            'Sixteen short lexical mismatch windows may be partial caption phrases; do not rewrite source without listening.',
            'All source video/audio edition matching and character/performance validation remain pending.'
        ]
    }
    report=[
      '# S01E01 whole-episode three-text witness evidence: 16 targeted reviews',
      '',
      'Exact owner source: [run #40116865728](https://github.com/gamesbyian/general-purpose/actions/runs/40116865728).',
      f'Original derived JSON SHA-256: `{sha}`. Source AVI/SRT hashes are independently checked.',
      '',
      '**Result:** 184 of 200 independently ASR-corroborated dialogue spans correspond substantially to the immutable original SRT. **Sixteen** are lexical investigation candidates; none of those sixteen is evidence by itself that the subtitles are wrong. 0/193 completed AV production scripts.',
      '',
      'Prioritize weak model/SRT overlap, rare vocabulary, subtitle timing drift, cue-boundary mergers and possible laughter/overlaps. The full exact text/PTS witness is preserved as `three-text-witness-review.json` and a sortable machine-readable list in `targeted-audio-review-queue.json`.',
      '',
      '| Priority | Source time | Span | Original subtitle cues | Ordered token fraction |',
      '|---:|---|---:|---|---:|'
    ]
    for case in queue:
        mid=case['original_source_audio_time_ms'][0]
        clock=f'{mid//60000:02d}:{(mid//1000)%60:02d}.{mid%1000:03d}'
        cue_ids=','.join(map(str,case['original_srt_cue_ids'])) or 'none'
        report.append(f"| {case['review_rank_not_certainty']} | {clock} | {case['source_span_index']} | {cue_ids} | {case['ordered_model_token_fraction_in_srt']:.4f} |")
    report+=['',
      'Model transcript agreement is genuine machine corroboration, but character names, emotional tone, phonetic authenticity, actions and screenplay completeness are not accepted from these text comparisons.',
      '']
    return {'three-text-witness-review.json':raw_bytes,
            'three-witness-summary.json':(json.dumps(meta,indent=2,ensure_ascii=False)+'\n').encode(),
            'targeted-audio-review-queue.json':(json.dumps(queue,indent=2,ensure_ascii=False)+'\n').encode(),
            'targeted-review.md':('\n'.join(report)).encode()}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args()
    if args.output_dir.exists():
        ap.error('Refusing overwrite of imported original source review evidence')
    data=args.input.read_bytes()
    if len(data)>300_000:
        raise ValueError('Unbounded imported text witness')
    outputs=make_outputs(data)
    args.output_dir.mkdir(parents=True)
    for name,bytes_ in outputs.items():
        (args.output_dir/name).write_bytes(bytes_)
    print('Retained exact SHA-pinned 200 original dialogue correspondence spans and 16 targeted reviews; no human acceptance')


if __name__=='__main__':
    main()
