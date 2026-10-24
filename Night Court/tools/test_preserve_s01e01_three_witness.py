#!/usr/bin/env python3
"""Original-series S01E01 exact SHA and 200-span evidence integrity tests."""
import copy
import hashlib
import json
import unittest
from preserve_s01e01_three_witness import (
    AVI_SHA,AUDIO_SHA,SRT_SHA,SOURCE_JSON_SHA,ORIGINAL_SRT,
    make_outputs,validate_source
)


def fake():
    rows=[]
    for i in range(200):
        conflict=i>=184
        rows.append({
          'span_index':i,'model_agreed_text_candidate':'I can hear the original',
          'model_word_count':5,'model_consensus_interval_ms':[i*5000,i*5000+1700],
          'source_caption_cue_ids':[1],
          'source_caption_interval_ms':[i*5000,i*5000+1800],
          'source_caption_verbatim':'I can hear the original',
          'ordered_matched_model_token_fraction':0.2 if conflict else 1.0,
          'longest_contiguous_token_coverage':0.2 if conflict else 1.0,
          'review_tier':('two_model_agreement_caption_lexical_disagreement' if conflict
                         else 'three_text_witness_correspondence_candidate'),
          'original_srt_changed':False,'source_audio_human_listened':False,
          'source_video_lip_or_speaker_identity_accepted':False
        })
    return {
       'schema':'night-court-whole-s01e01-two-independent-models-plus-original-caption/1',
       'original_video_sha256':AVI_SHA,'source_caption_sha256':SRT_SHA,
       'decoded_audio_sha256':AUDIO_SHA,'source_audio_duration_ms':1448256,
       'original_srt_cues':336,'independent_model_consensus_spans':200,
       'classification_counts':{
          'three_text_witness_correspondence_candidate':184,
          'two_model_agreement_caption_lexical_disagreement':16,
          'no_original_caption_in_candidate_interval':0},
       'review_spans':rows,
       'original_source_srt_modified':False,
       'original_soundtrack_human_listening_completed':False,
       'subtitle_video_edition_sync_confirmed':False,
       'source_character_speaker_identity_confirmed':False,
       'full_production_script_verified':False
    }


class ExactWitness(unittest.TestCase):
    def test_source_srt_and_archived_json_digest_both_pinned(self):
        self.assertEqual(hashlib.sha256(ORIGINAL_SRT.read_bytes()).hexdigest(),SRT_SHA)
        self.assertEqual(len(SOURCE_JSON_SHA),64)
        self.assertNotEqual(SOURCE_JSON_SHA,'0'*64)

    def test_synthetic_200_witnesses_produce_ranked_16_task_queue(self):
        raw=(json.dumps(fake(),ensure_ascii=False)+'\n').encode('utf-8')
        results=make_outputs(raw,strict_original=False)
        self.assertEqual(results['three-text-witness-review.json'],raw)
        summary=json.loads(results['three-witness-summary.json'])
        self.assertEqual(summary['span_level_classification_counts']['three_text_witness_correspondence_candidate'],184)
        self.assertEqual(summary['requires_targeted_source_audio_review'],16)
        self.assertFalse(summary['complete_original_episode_screenplay_accepted'])
        queue=json.loads(results['targeted-audio-review-queue.json'])
        self.assertEqual(len(queue),16)
        self.assertEqual(queue[0]['source_span_index'],184)
        self.assertFalse(queue[0]['episode_subtitle_or_script_auto_changed'])
        self.assertFalse(queue[0]['model_error_or_srt_error_determined'])
        with self.assertRaisesRegex(ValueError,'hash changed'):
            make_outputs(raw,strict_original=True)

    def test_reject_acceptance_renames_reordering_or_counter_mutation(self):
        for mutation in ('source','human','speaker','span','clock','count','unverified'):
            data=fake()
            if mutation=='source':data['original_video_sha256']='a'*64
            if mutation=='human':data['original_soundtrack_human_listening_completed']=True
            if mutation=='speaker':data['source_character_speaker_identity_confirmed']=True
            if mutation=='span':data['review_spans'][0]['span_index']=100
            if mutation=='clock':data['review_spans'][0]['model_consensus_interval_ms']=[1448255,1448256]
            if mutation=='count':data['classification_counts']['three_text_witness_correspondence_candidate']=185
            if mutation=='unverified':data['review_spans'][0]['source_audio_human_listened']=True
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                validate_source(data,'0'*64,strict_original=False)


if __name__=='__main__':
    unittest.main()
