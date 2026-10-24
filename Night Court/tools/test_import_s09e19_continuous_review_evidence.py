#!/usr/bin/env python3
"""Credential-free original-source evidence import accept/reject invariants."""
from __future__ import annotations
import copy,json,tempfile,unittest
from pathlib import Path
from import_s09e19_continuous_review_evidence import (
  validate_report,import_report,VIDEO_SHA,SOURCE_SHA,PCM_SHA
)


def fixture():
    rows=[{'model_proposed_original_source_word_interval_valid':False,
           'original_soundtrack_word_human_verified':False,
           'rejection_reason':'zero_or_reversed_rounded_word_time',
           'same_time_other_model_context_unverified':[],
           'untrusted_raw_model_start_seconds':10.0,
           'untrusted_raw_model_end_seconds':10.0} for _ in range(90)]
    windows=[]
    for i in range(12):
        a=i*10000
        length=2700 if i<11 else 2788
        windows.append({
          'time_window_ms_candidate_only':[a,a+length],
          'contains_three_verified_original_source_pts_ms':[a+100,a+200,a+300],
          'original_shot_and_action_human_verified':False,
          'speaking_identity_or_prosody_verified':False,
          'draft_stage_direction_accepted':False})
    return {
      'schema':'night-court-s09e19-whole-source-once-cross-episode-benchmark/1',
      'original_series':'night-court-1984','episode_id':'S09E19',
      'original_video_sha256':VIDEO_SHA,'original_untimed_source_sha256':SOURCE_SHA,
      'decoded_original_pcm_sha256':PCM_SHA,'source_video_bytes':183377920,
      'original_video_duration_ms':1320144,'original_audio_duration_ms':1320144,
      'original_source_paragraphs':347,'original_source_paragraphs_with_source_timecodes':0,
      'video_encoded_avg_fps':'30000/1001','original_video_download_count':1,
      'original_audio_decoded_once':True,
      'model_families':['whisper','kaldi_hmm_wfst'],'model_was_primed_by_original_text':False,
      'all_original_source_media_deleted_after_job':True,
      'sampled_frames_original_pts_checked':True,
      'source_untimed_paragraph_timestamps_created':False,'human_original_audio_listened':False,
      'speaker_identity_or_emotion_verified':False,'episode_production_script_accepted':False,
      'fleet_p95_episode_speed_verified':False,
      'source_processing_wall_seconds_excluding_job_startup_and_dependency_install':213.936,
      'actual_source_frames_selected':202,'actual_source_jpegs_bytes_ephemeral':999791,
      'source_triads_with_pixel_change_features':31,'source_triads_abstaining_for_pts_order':0,
      'pixel_change_is_verified_physical_action':False,
      'component_measured_seconds':{
          'ephemeral_three_frame_pixel_difference_seconds':.1,
          'shot_candidate_bounded_review_planning_seconds':0.0},
      'whisper_rejected_word_time_review':{
           'total_invalid_word_intervals':90,
           'retained_bounded_invalid_time_proposals':90,
           'unretained_diagnostics_over_cap':0,
           'rejection_details_no_source_time_promotion':rows,
           'original_soundtrack_listened':False,
           'separate_model_context_human_verified':False},
      'shot_bounded_selective_original_video_review':{
           'schema':'night-court-shot-bounded-original-continuity-review-plan/1',
           'source_video_sha256':VIDEO_SHA,'source_duration_ms':1320144,
           'requested_video_excerpt_count':12,'requested_total_video_excerpt_ms':32488,
           'source_cut_candidates_not_confirmed_shots':212,
           'source_triads_ranked':31,'source_triads_abstained_pts':0,
           'source_triads_deferred_actual_pts_cross_candidate_cut':0,
           'excerpt_media_decoded_or_retained':False,
           'human_continuous_video_review_done':False,
           'actor_gesture_voice_or_cut_verified':False,
           'scene_or_stage_directions_accepted':False,
           'full_original_episode_screenplay_accepted':False,
           'review_requests':windows,'deferred_review_requests':[]}
    }


class ContinuityEvidenceImport(unittest.TestCase):
    def test_only_source_fingerprinted_unaccepted_clip_and_invalid_words(self):
        obj=fixture()
        result=validate_report(obj)
        self.assertEqual(result['source_verified_triplets'],31)
        self.assertEqual(result['proposed_video_review_windows'],12)
        self.assertEqual(result['total_proposed_original_video_review_ms'],32488)
        self.assertEqual(result['unrepaired_original_whisper_word_time_cases'],90)
        self.assertFalse(result['real_video_performance_or_speaker_accepted'])

    def test_refuse_forged_source_sha_and_repaired_audio_word(self):
        for kind in ('source','dialogue','word','clip','duration'):
            obj=fixture()
            if kind=='source':obj['original_video_sha256']='0'*64
            elif kind=='dialogue':obj['source_untimed_paragraph_timestamps_created']=True
            elif kind=='word':obj['whisper_rejected_word_time_review']['rejection_details_no_source_time_promotion'][0]['original_soundtrack_word_human_verified']=True
            elif kind=='clip':obj['shot_bounded_selective_original_video_review']['review_requests'][0]['draft_stage_direction_accepted']=True
            else:obj['shot_bounded_selective_original_video_review']['requested_total_video_excerpt_ms']+=1
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                validate_report(obj)

    def test_unpinned_json_cannot_be_imported_even_if_structurally_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);item=root/'report.json'
            item.write_text(json.dumps(fixture()),'utf-8')
            with self.assertRaisesRegex(ValueError,'Unapproved'):
                import_report(item,root/'export')


if __name__=='__main__':
    unittest.main()
