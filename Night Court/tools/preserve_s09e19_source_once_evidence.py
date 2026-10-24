#!/usr/bin/env python3
"""Hash-bound import of actual S09E19 second full episode AV research run.

Creates immutable source numeric/lexical witness + monotonic original
UN-TIMED paragraph evidence + conservative compact source report.
Never exports original AVI, PCM, stills, weights, named voices or acceptance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from reconcile_s09e19_untimed_source_order import reconcile

SHA='14e721068a10ceb1c84b62ef04169364edb2a58741aaf889afe4a5ef90daa51c'
ZIP_SHA='95af07bd3a2f5ad62a252fcb4171662b90e8ad926237479ad259280ee22eb0ca'
AVI_SHA='51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649'
TXT_SHA='659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2'
PCM_SHA='7f3e3634c99469214360d59faf69c7838301e6ee94d5f08968382a74607b6711'
RUN=40126128202
ARTIFACT_ID=12572627835


def validate(source,raw,*,strict=True):
    if strict and hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError('Unexpected exact downloaded S09E19 source report SHA')
    if (source.get('schema')!='night-court-s09e19-whole-source-once-cross-episode-benchmark/1'
        or source.get('episode_id')!='S09E19' or source.get('original_video_sha256')!=AVI_SHA
        or source.get('source_video_bytes')!=183377920
        or source.get('original_untimed_source_sha256')!=TXT_SHA
        or source.get('decoded_original_pcm_sha256')!=PCM_SHA
        or source.get('original_source_paragraphs')!=347
        or source.get('original_source_paragraphs_with_source_timecodes')!=0
        or source.get('original_video_duration_ms')!=1320144
        or source.get('original_audio_duration_ms')!=1320144
        or source.get('original_video_download_count')!=1
        or source.get('original_audio_decoded_once') is not True
        or set(source.get('model_families',[]))!={'whisper','kaldi_hmm_wfst'}
        or source.get('model_was_primed_by_original_text') is not False
        or source.get('source_untimed_paragraph_timestamps_created') is not False
        or source.get('all_original_source_media_deleted_after_job') is not True
        or source.get('sampled_frames_original_pts_checked') is not True
        or source.get('human_original_audio_listened') is not False
        or source.get('episode_production_script_accepted') is not False):
        raise ValueError('Original media, independent model, or unverified source status mismatch')
    probes=source.get('untimed_paragraph_lexical_candidates')
    if (not isinstance(probes,list) or len(probes)>40
        or source.get('reviewed_untimed_source_lexical_probe_count')!=len(probes)):
        raise ValueError('Unbounded source untimed lexical proposals')
    counts=source.get('source_consensus_word_counts',{})
    if (type(counts.get('corroborated_words')) is not int or
        not 0<=counts['corroborated_words']<=15000
        or type(counts.get('corroborated_spans')) is not int or
        not 0<=counts['corroborated_spans']<=5000):
        raise ValueError('Impossible independent source recognition counts')
    if (source.get('actual_source_frames_selected',0)>240
        or source.get('actual_source_jpegs_bytes_ephemeral',0)>10000000):
        raise ValueError('Original 240-frame/image budget violated')
    return True


def outputs(raw:bytes,*,strict=True):
    report=json.loads(raw)
    validate(report,raw,strict=strict)
    anchors=reconcile(report)
    summary={
      'schema':'night-court-s09e19-source-once-permanent-speed-summary/1',
      'episode_id':'S09E19',
      'original_video_sha256':AVI_SHA,
      'original_video_bytes':183377920,
      'decoded_original_audio_sha256':PCM_SHA,
      'original_untimed_source_sha256':TXT_SHA,
      'original_source_paragraphs':347,
      'original_source_paragraphs_with_timestamps':0,
      'full_original_video_and_audio_duration_ms':1320144,
      'original_stream_avg_fps':report['video_encoded_avg_fps'],
      'independent_recognizer_families':report['model_families'],
      'original_source_retrieval_count':1,
      'actual_source_processing_wall_seconds_excludes_job_startup':report['source_processing_wall_seconds_excluding_job_startup_and_dependency_install'],
      'component_measured_seconds':report['component_measured_seconds'],
      'model_model_word_agreement_counts':report['source_consensus_word_counts'],
      'rejected_model_word_timestamps':report['model_invalid_word_time_counts'],
      'model_rejection_reasons':report['model_rejection_reasons'],
      'source_full_video_image_change_candidates_not_verified_cuts':report['source_video_cut_change_candidates_unverified'],
      'original_native_pts_verified_jpeg_frames':report['actual_source_frames_selected'],
      'original_ephemeral_JPEG_bytes':report['actual_source_jpegs_bytes_ephemeral'],
      'untimed_source_text_exploratory_spans':anchors['independent_agreement_spans_considered'],
      'distinct_original_paragraph_lexical_hypotheses':anchors['uniquely_lexical_matches_before_ordering'],
      'original_paragraph_order_consistent_hypotheses':anchors['order_consistent_candidate_anchors'],
      'original_source_paragraph_times_created':False,
      'original_dialogue_or_stage_human_reviewed':False,
      'named_actors_or_voice_performance_verified':False,
      'actual_camera_shot_edits_verified':False,
      'complete_original_episode_screenplay_accepted':False,
      'p95_on_193_episodes_verified':False,
      'private_source_workflow_run':RUN,
      'private_source_artifact_id':ARTIFACT_ID,
      'private_source_zip_sha256':ZIP_SHA,
      'private_original_source_json_sha256':hashlib.sha256(raw).hexdigest(),
      'private_source_artifact_expires_at_utc':'2026-10-31T19:41:32Z',
      'limitations':[
       'Two episodes under four minutes are actual fast source evidence pilots, NOT a 193-episode p95.',
       'No visual-language understanding of frames or physical performance audio/video completion yet.',
       'Original source 347 paragraphs are untimed; source audio windows only belong to model output.',
       'Machine lexical similarity and global paragraph order do not independently confirm dialogue.'
      ]
    }
    m=[
      '# S09E19 real source-once AV throughput and untimed dialogue review',
      '',
      'Trusted owner-only [source run #40126128202](https://github.com/gamesbyian/general-purpose/actions/runs/40126128202).',
      f'Exact original source report SHA: `{hashlib.sha256(raw).hexdigest()}`.',
      '',
      f"**Actual complete original-source stage time:** {summary['actual_source_processing_wall_seconds_excludes_job_startup']:.3f} seconds. S09E19 encodes at {summary['original_stream_avg_fps']}, runs 1320.144 seconds, and retains exactly 347 original untimed source paragraphs.",
      '',
      f"Two independent recognizers corroborated **{summary['model_model_word_agreement_counts']['corroborated_words']}** word hypotheses in **{summary['model_model_word_agreement_counts']['corroborated_spans']}** model-model agreement spans.",
      f"The full decoded-video difference scan proposed **{summary['source_full_video_image_change_candidates_not_verified_cuts']}** image changes; **{summary['original_native_pts_verified_jpeg_frames']}** private scratch JPEGs ({summary['original_ephemeral_JPEG_bytes']} bytes) were source-PTS checked and deleted.",
      f"The cheap text-only source alignment considered {summary['untimed_source_text_exploratory_spans']} model span hypotheses and found {summary['distinct_original_paragraph_lexical_hypotheses']} distinctive paragraph matches; **{summary['original_paragraph_order_consistent_hypotheses']}** were consistent with source paragraph order.",
      '',
      'All source paragraph timestamps remain **null**. Source-video shot scoring, inferred motion, named characters, spoken-word fidelity, inflection and finished screenplay acceptance are entirely separate pending gates.',
      '',
      'The exact original machine metadata and bounded transcript candidates are preserved in `source-once-original-report.json` and all 40 order-audited proposals in `untimed-model-paragraph-order.json`. No AVI, WAV, source frame or model weights are committed.',
      ''
    ]
    return {
      'source-once-original-report.json':raw,
      'untimed-model-paragraph-order.json':(json.dumps(anchors,indent=2,ensure_ascii=False)+'\n').encode(),
      'source-once-evidence-summary.json':(json.dumps(summary,indent=2,ensure_ascii=False)+'\n').encode(),
      'source-review.md':('\n'.join(m)).encode(),
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args()
    if a.output_dir.exists():p.error('Refuse original evidence overwrite')
    raw=a.input.read_bytes()
    if len(raw)>180000:raise ValueError('Unbounded derived source dialogue metadata')
    result=outputs(raw)
    a.output_dir.mkdir(parents=True)
    for name,data in result.items():
        (a.output_dir/name).write_bytes(data)
    print('SHA-pinned S09E19 real original full-episode stage cost and source-untimed order preserved without AV acceptance')


if __name__=='__main__':
    main()
