#!/usr/bin/env python3
"""No-media, no-model unit checks for 3 independent research text witnesses."""
import copy
import hashlib
import unittest

from triangulate_whole_s01e01_asr_with_srt import srt_cues,parse_time,match_consensus_to_srt,SRT_SOURCE_BYTE_ENCODING,SOURCE_SRT,SRT_SHA


def fixture():
    def span(text,a,b):
        return {'word_count':len(text.split()),'model_a_verbatim_candidate':text,
                'time_interval_ms':[a,b]}
    return {'schema':'night-court-original-full-episode-dual-independent-asr-cost-and-agreement/1',
      'episode_id':'S01E01',
      'original_video_sha256':'5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962',
      'model_original_srt_prompted':False,'original_audio_human_listened':False,
      'source_audio_duration_ms':18000,
      'decoded_audio_sha256':'2'*64,
      'comparison':{
          'schema':'night-court-independent-asr-corroboration/1',
          'original_video_sha256':'5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962',
          'decoded_audio_sha256':'2'*64,'source_window_ms':[0,18000],
          'models':[{'architecture_family':'whisper'},{'architecture_family':'kaldi_hmm_wfst'}],
          'corroborated_spans':[
             span('Did you say Mercurial',1100,2500),
             span('Cinnamon electric platypus',4800,5500),
             span('There is no source',14500,15100)]
      }}


SMALL='''1
00:00:01,000 --> 00:00:03,000
Did you say Mercurial?

2
00:00:04,000 --> 00:00:06,000
- In the forest.
- Yes.
'''


class OriginalSRTTriangulation(unittest.TestCase):
    def test_immutable_original_DVD_caption_legacy_charset(self):
        original=SOURCE_SRT.read_bytes()
        self.assertEqual(hashlib.sha256(original).hexdigest(),SRT_SHA)
        self.assertEqual(SRT_SOURCE_BYTE_ENCODING,'cp1252')
        with self.assertRaises(UnicodeDecodeError):
            original.decode('utf-8-sig')
        decoded=original.decode(SRT_SOURCE_BYTE_ENCODING)
        self.assertGreater(len(srt_cues(decoded)),100)
        self.assertEqual(bytes([0xe0]).decode(SRT_SOURCE_BYTE_ENCODING),'à')

    def test_parser_strict_source_cues_and_timecodes(self):
        cues=srt_cues(SMALL)
        self.assertEqual(len(cues),2)
        self.assertEqual(cues[0]['source_caption_interval_ms'],[1000,3000])
        self.assertEqual(parse_time('00:01:03,120'),63120)
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            srt_cues(SMALL+'\n\n'+SMALL.split('\n\n')[0])
        with self.assertRaisesRegex(ValueError,'Invalid exact'):
            parse_time('01:02:03')

    def test_positive_model_model_source_cue_correspondence_and_mismatches(self):
        out=match_consensus_to_srt(fixture(),SMALL)
        self.assertEqual(out['original_srt_cues'],2)
        self.assertEqual(out['independent_model_consensus_spans'],3)
        self.assertEqual(out['classification_counts'],{
            'three_text_witness_correspondence_candidate':1,
            'two_model_agreement_caption_lexical_disagreement':1,
            'no_original_caption_in_candidate_interval':1})
        self.assertFalse(out['original_soundtrack_human_listening_completed'])
        self.assertFalse(out['source_character_speaker_identity_confirmed'])
        self.assertFalse(out['full_production_script_verified'])

    def test_reject_prompted_models_and_mismatched_source_audio(self):
        for flag in ('prompt','video','audio','span','family'):
            data=fixture()
            if flag=='prompt':data['model_original_srt_prompted']=True
            if flag=='video':data['original_video_sha256']='a'*64
            if flag=='audio':data['comparison']['decoded_audio_sha256']='f'*64
            if flag=='span':data['comparison']['corroborated_spans'][0]['time_interval_ms']=[0,20000]
            if flag=='family':data['comparison']['models'][1]['architecture_family']='whisper'
            with self.subTest(flag=flag),self.assertRaises(ValueError):
                match_consensus_to_srt(data,SMALL)


if __name__=='__main__':unittest.main()
