#!/usr/bin/env python3
"""Measure *source SRT word-position* coverage by three textual witnesses.

Never report 184/200 model spans as 92% of a complete episode's speech.
No media, additional models or FTP are used. Every original cue token is
counted at most once; matches remain machine correspondence, not listening.
"""
from __future__ import annotations
import argparse
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path

from preserve_s01e01_three_witness import validate_source,SOURCE_JSON_SHA
from triangulate_whole_s01e01_asr_with_srt import (
    SOURCE_SRT,SRT_SOURCE_BYTE_ENCODING,SRT_SHA,srt_cues,words
)

ROOT=Path(__file__).resolve().parents[1]
DERIVED=ROOT/'seasons/S01/S01E01/derived/three-witness-v1/three-text-witness-review.json'
POSITIVE='three_text_witness_correspondence_candidate'


def calculate(raw:bytes, original_srt_bytes:bytes,*,strict=True):
    fingerprint=hashlib.sha256(raw).hexdigest()
    report=json.loads(raw)
    validate_source(report,fingerprint,strict_original=strict)
    if hashlib.sha256(original_srt_bytes).hexdigest()!=SRT_SHA:
        raise ValueError('Original S01E01 SRT source changed')
    cues=srt_cues(original_srt_bytes.decode(SRT_SOURCE_BYTE_ENCODING))
    if len(cues)!=336:
        raise ValueError('Original cue coverage changed')
    indexed={c['cue_id']:c for c in cues}
    total=sum(len(c['normalized_tokens']) for c in cues)
    covered=set()
    coverage_by_span=[]
    for span in report['review_spans']:
        ids=span['source_caption_cue_ids']
        status=span['review_tier']
        if not ids:continue
        group=[indexed[cid] for cid in ids]
        if ' '.join(c['source_text'] for c in group)!=span['source_caption_verbatim']:
            raise ValueError('Model correspondence distorted original SRT witness')
        if status!=POSITIVE:
            continue
        tokens=words(span['model_agreed_text_candidate'])
        positions=[(entry['cue_id'],i) for entry in group
                   for i in range(len(entry['normalized_tokens']))]
        source_tokens=[w for entry in group for w in entry['normalized_tokens']]
        matched=set()
        for block in SequenceMatcher(None,tokens,source_tokens,autojunk=False).get_matching_blocks():
            for i in range(block.b,block.b+block.size):
                matched.add(positions[i])
        if not matched or len(matched)>sum(len(c['normalized_tokens']) for c in group):
            raise ValueError('Invalid source-only token agreement')
        covered.update(matched)
        coverage_by_span.append({'span_index':span['span_index'],
                                 'candidate_source_tokens_aligned':len(matched)})
    cues_with=set(i for i,_ in covered)
    if not 0<len(covered)<=total:
        raise ValueError('Source SRT token coverage impossible')
    return {
       'schema':'night-court-s01e01-source-srt-unique-three-witness-word-coverage/1',
       'original_srt_sha256':SRT_SHA,
       'original_three_witness_derived_json_sha256':fingerprint,
       'original_srt_cues_total':len(cues),
       'original_srt_word_tokens_total':total,
       'original_srt_unique_word_positions_with_independent_2asr_and_srt_correspondence_candidate':len(covered),
       'source_srt_word_position_correspondence_fraction':round(len(covered)/total,4),
       'original_srt_cues_with_any_correspondence_candidate':len(cues_with),
       'original_srt_cues_without_correspondence_candidate':len(cues)-len(cues_with),
       'independent_two_model_consensus_spans':200,
       'three_text_witness_correspondence_spans':184,
       'two_model_agreement_needing_original_audio_listening':16,
       'positive_span_word_alignment_counts':coverage_by_span,
       'independent_original_source_audio_human_verified':False,
       'complete_original_srt_dialogue_verified':False,
       'srt_source_automatically_changed':False,
       'speaker_identity_and_vocal_delivery_verified':False,
       'complete_episode_production_script_accepted':False,
       'limits':[
          'This proportion counts unique original SRT token positions covered by textual correspondence candidates, NOT independently heard spoken-word accuracy.',
          'The 184/200 span agreement proportion is NOT a percentage of original dialogue confirmed.',
          'Only 184 positive source-model-model spans contribute to strict token-position coverage; 16 flags still need source listening.',
          'Repeated model passages cannot double count original subtitle word positions.',
          'Word order/source-SRT edition drift, laughter and short unrecognized phrases may reduce this conservative coverage.',
          'No actual speaker, acting performance, scene editing or AV complete script is established.'
       ]
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():
        p.error('Refuse to overwrite previous original source measurement')
    raw=DERIVED.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_JSON_SHA:
        raise ValueError('Original imported derived three-witness source hash changed')
    output=calculate(raw,SOURCE_SRT.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n','utf-8')
    print('S01E01: %d/%d unique original source SRT tokens (~%.1f%%) have three-text-witness correspondence candidates across %d of 336 source cues. Dialogue not source-listened.'%
      (output['original_srt_unique_word_positions_with_independent_2asr_and_srt_correspondence_candidate'],
       output['original_srt_word_tokens_total'],
       output['source_srt_word_position_correspondence_fraction']*100,
       output['original_srt_cues_with_any_correspondence_candidate']))


if __name__=='__main__':
    main()
