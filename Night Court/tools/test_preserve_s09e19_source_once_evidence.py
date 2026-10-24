#!/usr/bin/env python3
"""Never turn original untimed paragraph audio hypotheses into source timestamps."""
import json
import unittest
from match_s09e19_untimed_paragraphs import candidates,assess
from s09e19_untimed_video_anchor_pilot import sources
from preserve_s09e19_source_once_evidence import (
  validate,outputs,SHA,TXT_SHA,AVI_SHA,PCM_SHA
)


def fake():
    text=sources()[240]['text']
    a=assess({'index':0,'text':text},candidates(sources()))
    return {
      'schema':'night-court-s09e19-whole-source-once-cross-episode-benchmark/1',
      'episode_id':'S09E19','original_video_sha256':AVI_SHA,
      'source_video_bytes':183377920,'original_untimed_source_sha256':TXT_SHA,
      'decoded_original_pcm_sha256':PCM_SHA,
      'original_source_paragraphs':347,
      'original_source_paragraphs_with_source_timecodes':0,
      'original_video_duration_ms':1320144,'original_audio_duration_ms':1320144,
      'video_encoded_avg_fps':'30000/1001',
      'original_video_download_count':1,'original_audio_decoded_once':True,
      'model_families':['kaldi_hmm_wfst','whisper'],
      'model_was_primed_by_original_text':False,
      'source_untimed_paragraph_timestamps_created':False,
      'all_original_source_media_deleted_after_job':True,
      'sampled_frames_original_pts_checked':True,
      'human_original_audio_listened':False,
      'episode_production_script_accepted':False,
      'untimed_paragraph_lexical_candidates':[
         {'consensus_span_index':0,'original_avi_audio_time_proposal_ms':[300000,302000],
          'independent_model_agreed_text_hypothesis':text,
          'untimed_original_source_paragraph_candidate':a['source_paragraph_candidate'],
          'original_source_paragraph_time_ms':None,
          'word_identity_original_audio_human_verified':False}
      ],
      'reviewed_untimed_source_lexical_probe_count':1,
      'source_consensus_word_counts':{'corroborated_words':5,'corroborated_spans':1},
      'model_invalid_word_time_counts':{'whisper':0,'vosk':0},
      'model_rejection_reasons':{'whisper':{},'vosk':{}},
      'source_video_cut_change_candidates_unverified':2,
      'actual_source_frames_selected':12,
      'actual_source_jpegs_bytes_ephemeral':20000,
      'source_processing_wall_seconds_excluding_job_startup_and_dependency_install':280,
      'component_measured_seconds':{'single_original_ftp_transfer_and_sha_seconds':4.2}
    }


class SourceArchive(unittest.TestCase):
    def test_untimed_source_pinned_and_offline_derivation_is_research_only(self):
        src=fake();raw=(json.dumps(src)+'\n').encode()
        self.assertTrue(validate(src,raw,strict=False))
        written=outputs(raw,strict=False)
        self.assertEqual(len(written),4)
        ordered=json.loads(written['untimed-model-paragraph-order.json'])
        summary=json.loads(written['source-once-evidence-summary.json'])
        self.assertIsNone(ordered['review_cases'][0]['source_original_paragraph_timecode_ms'])
        self.assertEqual(summary['original_source_paragraphs_with_timestamps'],0)
        self.assertFalse(summary['complete_original_episode_screenplay_accepted'])
        with self.assertRaisesRegex(ValueError,'exact downloaded'):
            validate(src,raw,strict=True)

    def test_refuse_source_mutation_fake_acceptance_and_unbounded_images(self):
        from copy import deepcopy
        for field in ('video','txt','timed','reviewed','frames','pcm'):
            d=fake()
            if field=='video':d['original_video_sha256']='a'*64
            if field=='txt':d['original_untimed_source_sha256']='b'*64
            if field=='timed':d['source_untimed_paragraph_timestamps_created']=True
            if field=='reviewed':d['human_original_audio_listened']=True
            if field=='frames':d['actual_source_frames_selected']=241
            if field=='pcm':d['decoded_original_pcm_sha256']='c'*64
            with self.subTest(field=field),self.assertRaises(ValueError):
                validate(d,json.dumps(d).encode(),strict=False)


if __name__=='__main__':
    unittest.main()
