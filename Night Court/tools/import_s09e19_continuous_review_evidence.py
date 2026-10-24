#!/usr/bin/env python3
"""One-shot hash-pinned S09E19 original continuity/invalid-word research import.

Copies ONLY an exact previously measured source-once JSON report, requiring
original audiovisual SHA, immutable untimed source, verified sampled PTS,
a bounded unaccepted clip review plan and invalid-time research details.
Never fetches media or silently corrects original dialogue or word times.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

REPORT_SHA='b86f1de8be857216fa89102c43e8e0cf4ffce64106879ab7e8729ce505530318'
ZIP_SHA='49de244f965f07baa62b714984506ee55a1a6824e32d516196b8935dc64f064c'
VIDEO_SHA='51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649'
SOURCE_SHA='659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2'
PCM_SHA='7f3e3634c99469214360d59faf69c7838301e6ee94d5f08968382a74607b6711'
MAX_JSON_BYTES=150000


def validate_report(report):
    if (report.get('schema')!='night-court-s09e19-whole-source-once-cross-episode-benchmark/1'
        or report.get('original_series')!='night-court-1984'
        or report.get('episode_id')!='S09E19'
        or report.get('original_video_sha256')!=VIDEO_SHA
        or report.get('original_untimed_source_sha256')!=SOURCE_SHA
        or report.get('decoded_original_pcm_sha256')!=PCM_SHA
        or report.get('source_video_bytes')!=183377920
        or report.get('original_video_duration_ms')!=1320144
        or report.get('original_audio_duration_ms')!=1320144
        or report.get('original_source_paragraphs')!=347
        or report.get('original_source_paragraphs_with_source_timecodes')!=0
        or report.get('video_encoded_avg_fps')!='30000/1001'
        or report.get('original_video_download_count')!=1
        or report.get('original_audio_decoded_once') is not True
        or set(report.get('model_families',[]))!={'whisper','kaldi_hmm_wfst'}
        or report.get('model_was_primed_by_original_text') is not False
        or report.get('all_original_source_media_deleted_after_job') is not True
        or report.get('sampled_frames_original_pts_checked') is not True
        or report.get('source_untimed_paragraph_timestamps_created') is not False
        or report.get('human_original_audio_listened') is not False
        or report.get('speaker_identity_or_emotion_verified') is not False
        or report.get('episode_production_script_accepted') is not False
        or report.get('fleet_p95_episode_speed_verified') is not False):
        raise ValueError('Original AVI, transcript, model or acceptance provenance mismatch')
    if (report.get('source_processing_wall_seconds_excluding_job_startup_and_dependency_install')!=213.936
        or report.get('actual_source_frames_selected')!=202
        or report.get('actual_source_jpegs_bytes_ephemeral')!=999791
        or report.get('source_triads_with_pixel_change_features')!=31
        or report.get('source_triads_abstaining_for_pts_order')!=0
        or report.get('pixel_change_is_verified_physical_action') is not False
        or report.get('component_measured_seconds',{}).get('ephemeral_three_frame_pixel_difference_seconds')!=0.1
        or report['component_measured_seconds'].get('shot_candidate_bounded_review_planning_seconds')!=0.0):
        raise ValueError('Source once running cost or sampled pixel evidence changed')
    details=report.get('whisper_rejected_word_time_review')
    if (not isinstance(details,dict)
        or details.get('total_invalid_word_intervals')!=90
        or details.get('retained_bounded_invalid_time_proposals')!=90
        or details.get('unretained_diagnostics_over_cap')!=0
        or details.get('original_soundtrack_listened') is not False
        or details.get('separate_model_context_human_verified') is not False
        or not isinstance(details.get('rejection_details_no_source_time_promotion'),list)
        or len(details['rejection_details_no_source_time_promotion'])!=90):
        raise ValueError('Original invalid Whisper word-time evidence incomplete or promoted')
    for row in details['rejection_details_no_source_time_promotion']:
        if (row.get('model_proposed_original_source_word_interval_valid') is not False
            or row.get('original_soundtrack_word_human_verified') is not False
            or row.get('rejection_reason')!='zero_or_reversed_rounded_word_time'
            or not isinstance(row.get('same_time_other_model_context_unverified'),list)
            or len(row['same_time_other_model_context_unverified'])>4):
            raise ValueError('False repaired word-time or independently listened wording claim')
    plan=report.get('shot_bounded_selective_original_video_review')
    if (not isinstance(plan,dict)
        or plan.get('schema')!='night-court-shot-bounded-original-continuity-review-plan/1'
        or plan.get('source_video_sha256')!=VIDEO_SHA
        or plan.get('source_duration_ms')!=1320144
        or plan.get('requested_video_excerpt_count')!=12
        or plan.get('requested_total_video_excerpt_ms')!=32488
        or plan.get('source_cut_candidates_not_confirmed_shots')!=212
        or plan.get('source_triads_ranked')!=31
        or plan.get('source_triads_abstained_pts')!=0
        or plan.get('source_triads_deferred_actual_pts_cross_candidate_cut')!=0
        or plan.get('excerpt_media_decoded_or_retained') is not False
        or plan.get('human_continuous_video_review_done') is not False
        or plan.get('actor_gesture_voice_or_cut_verified') is not False
        or plan.get('scene_or_stage_directions_accepted') is not False
        or plan.get('full_original_episode_screenplay_accepted') is not False
        or not isinstance(plan.get('review_requests'),list)
        or len(plan['review_requests'])!=12
        or plan.get('deferred_review_requests')!=[]):
        raise ValueError('Continuous source video review manifest misrepresented')
    total=0
    for row in plan['review_requests']:
        window=row.get('time_window_ms_candidate_only')
        pts=row.get('contains_three_verified_original_source_pts_ms')
        if (not isinstance(window,list) or len(window)!=2
            or not isinstance(pts,list) or len(pts)!=3
            or any(type(x) is not int for x in window+pts)
            or not 0<=window[0]<=pts[0]<pts[1]<pts[2]<=window[1]<=1320144
            or row.get('original_shot_and_action_human_verified') is not False
            or row.get('speaking_identity_or_prosody_verified') is not False
            or row.get('draft_stage_direction_accepted') is not False):
            raise ValueError('Invalid original PTS clip or false screenplay assertion')
        total+=window[1]-window[0]
    if total!=plan['requested_total_video_excerpt_ms']:
        raise ValueError('Source-trace clip window duration sum altered')
    return {'source_video_sha256':VIDEO_SHA,'original_source_sha256':SOURCE_SHA,
            'original_audio_sha256':PCM_SHA,
            'original_source_processing_seconds':213.936,
            'source_verified_triplets':31,'proposed_video_review_windows':12,
            'total_proposed_original_video_review_ms':32488,
            'unrepaired_original_whisper_word_time_cases':90,
            'original_source_paragraphs_untimed':347,
            'real_video_performance_or_speaker_accepted':False}


def import_report(source:Path,outdir:Path):
    if not source.is_file() or outdir.exists():
        raise ValueError('Missing original research report or import destination exists')
    raw=source.read_bytes()
    if len(raw)>MAX_JSON_BYTES or hashlib.sha256(raw).hexdigest()!=REPORT_SHA:
        raise ValueError('Unapproved original source report JSON, hash or size')
    obj=json.loads(raw)
    summary=validate_report(obj)
    outdir.mkdir(parents=True)
    (outdir/'source-report.json').write_bytes(raw)
    (outdir/'source-review-summary.json').write_text(json.dumps({
        'schema':'night-court-s09e19-original-continuity-and-rejected-word-source-import/1',
        'trusted_original_source_run':40129675505,
        'trusted_original_source_artifact_id':12573968622,
        'original_report_json_sha256':REPORT_SHA,
        'original_report_artifact_zip_sha256':ZIP_SHA,
        'stage_metadata_only':True,
        'all_original_video_audio_jpegs_model_weights_excluded':True,
        'script_or_speaker_accepted':False,
        **summary},indent=2)+'\n','utf-8')
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args()
    report=import_report(a.input,a.output_dir)
    print('Preserved SHA-pinned original S09E19 clip review/invalid Whisper timing report: '
          f"{report['proposed_video_review_windows']} replay requests, "
          f"{report['unrepaired_original_whisper_word_time_cases']} rejected words, "
          '0 accepted scene directions; no source media or weights.')


if __name__=='__main__':main()
