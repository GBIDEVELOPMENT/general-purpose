#!/usr/bin/env python3
"""No-media tests for full-episode source-once evidence pack gating."""
import copy
import unittest
from profile_s01e01_one_source_factory import compose_summary
from probe_s01e01_cadence_and_cost import SHA,SIZE


def samples():
    audio={
       'schema':'night-court-original-full-episode-dual-independent-asr-cost-and-agreement/1',
       'original_video_sha256':SHA,'original_video_bytes':SIZE,
       'decoded_audio_sha256':'3'*64,'source_audio_duration_ms':1448256,
       'model_original_srt_prompted':False,'original_audio_human_listened':False,
       'measured_wall_time_seconds':{
           'verified_source_ftp_transfer_seconds':4.0,
           'one_episode_pcm_decode_seconds':3.64,
           'whisper_tiny_en_full_episode_inference_seconds':43.8,
           'kaldi_wfst_vosk_full_episode_inference_seconds':79.6,
           'vosk_weight_download_unpack_seconds':4.0,
           'two_model_text_reconciliation_seconds':0.01
       },
       'comparison':{'counts':{'corroborated_words':1447,'corroborated_spans':200,
                              'unresolved_word_candidates':1673}},
       'models':[{'model_id':'vosk','architecture_family':'kaldi_hmm_wfst',
                  'rejected_word_timestamps':0,'rejected_word_reasons':{}},
                 {'model_id':'whisper','architecture_family':'whisper',
                  'rejected_word_timestamps':238,
                  'rejected_word_reasons':{'zero_or_reversed_rounded_word_time':238}}]}
    visual={
       'schema':'night-court-whole-source-visual-time-budget/1',
       'source_video_sha256':SHA,'original_video_bytes':SIZE,
       'source_video_duration_ms':1448256,'original_stream_avg_frame_rate':'30000/1001',
       'script_or_full_episode_accepted':False,'all_image_frame_pts_match_verified':True,
       'actual_extracted_frame_count':212,'actual_JPEG_bytes':908395,
       'image_change_candidates_not_verified_cuts':212,
       'measured_stage_seconds':{'ffprobe_metadata_seconds':.064,
           'full_episode_lowres_cut_proposal_scan_seconds':27.624,
           'source_plan_seconds':.009,
           'one_pass_ffmpeg_source_frame_extraction_seconds':23.453}}
    return audio,visual


class OneOwnerEpisode(unittest.TestCase):
    def test_same_source_serial_cost_accounting_and_no_acceptance(self):
        a,v=samples()
        expected=4.0+sum(a['measured_wall_time_seconds'].values())-4.0+sum(v['measured_stage_seconds'].values())
        report=compose_summary(a,v,4.0,expected+1.0)
        self.assertEqual(report['original_source_video_download_count'],1)
        self.assertEqual(report['original_audio_pcm_decode_count'],1)
        self.assertEqual(report['selected_JPEG_frames'],212)
        self.assertEqual(report['word_candidate_summary']['corroborated_words'],1447)
        self.assertFalse(report['visual_language_model_applied'])
        self.assertFalse(report['complete_production_screenplay_accepted'])
        self.assertAlmostEqual(report['actual_source_to_final_metadata_wall_seconds'],expected+1)

    def test_reject_different_audio_video_edition_or_media_promotion(self):
        for mutated in ('video_sha','duration','source_not_listened','video_pts','framecap','wrong_family','accepted'):
            a,v=samples()
            if mutated=='video_sha':v['source_video_sha256']='4'*64
            if mutated=='duration':v['source_video_duration_ms']+=1000
            if mutated=='source_not_listened':a['original_audio_human_listened']=True
            if mutated=='video_pts':v['all_image_frame_pts_match_verified']=False
            if mutated=='framecap':v['actual_extracted_frame_count']=241
            if mutated=='wrong_family':a['models'][0]['architecture_family']='whisper'
            if mutated=='accepted':v['script_or_full_episode_accepted']=True
            with self.subTest(mutated=mutated),self.assertRaises(ValueError):
                compose_summary(a,v,4.0,185.0)

    def test_reject_bad_clock_or_machine_claim(self):
        a,v=samples()
        with self.assertRaisesRegex(ValueError,'monotonic'):
            compose_summary(a,v,4.0,1000)
        a['comparison']['counts']['corroborated_words']=-1
        with self.assertRaisesRegex(ValueError,'consensus'):
            compose_summary(a,v,4.0,188)


if __name__=='__main__':
    unittest.main()
