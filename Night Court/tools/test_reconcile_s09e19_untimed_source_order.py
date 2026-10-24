#!/usr/bin/env python3
"""Text-only untimed original-source order and non-invention regression tests."""
import copy
import unittest
from match_s09e19_untimed_paragraphs import assess,candidates
from reconcile_s09e19_untimed_source_order import reconcile,verify,TXT_SHA,VIDEO_SHA
from s09e19_untimed_video_anchor_pilot import sources


def fixture():
    paragraphs=sources()
    bank=candidates(paragraphs)
    records=[]
    for i,index in enumerate((50,150,240)):
        text=paragraphs[index]['text']
        result=assess({'index':i,'text':text},bank)
        records.append({
           'consensus_span_index':i*2,
           'original_avi_audio_time_proposal_ms':[200000+i*120000,201200+i*120000],
           'independent_model_agreed_text_hypothesis':text,
           'untimed_original_source_paragraph_candidate':result['source_paragraph_candidate'],
           'original_source_paragraph_time_ms':None,
           'word_identity_original_audio_human_verified':False
        })
    return {
        'schema':'night-court-s09e19-whole-source-once-cross-episode-benchmark/1',
        'episode_id':'S09E19','original_video_sha256':VIDEO_SHA,
        'original_untimed_source_sha256':TXT_SHA,
        'original_source_paragraphs':347,
        'original_source_paragraphs_with_source_timecodes':0,
        'source_untimed_paragraph_timestamps_created':False,
        'episode_production_script_accepted':False,
        'human_original_audio_listened':False,
        'original_audio_duration_ms':1320144,
        'untimed_paragraph_lexical_candidates':records
    }


class UntimedOrdering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.real=fixture()

    def test_positive_original_order_only_proposed_and_null(self):
        r=reconcile(copy.deepcopy(self.real))
        self.assertEqual(r['independent_agreement_spans_considered'],3)
        self.assertEqual(r['source_paragraph_count'],347)
        self.assertLessEqual(r['order_consistent_candidate_anchors'],3)
        self.assertFalse(r['new_original_source_timecodes_created'])
        self.assertFalse(r['speakers_and_continuous_actions_verified'])
        self.assertTrue(all(x['source_original_paragraph_timecode_ms'] is None for x in r['review_cases']))
        self.assertTrue(all(x['original_source_dialogue_human_verified'] is False for x in r['review_cases']))

    def test_input_must_never_replace_untimed_source_with_video_times(self):
        for field in ('time','video','accept','order','count'):
            x=copy.deepcopy(self.real)
            if field=='time':x['untimed_paragraph_lexical_candidates'][0]['original_source_paragraph_time_ms']=200000
            if field=='video':x['original_video_sha256']='f'*64
            if field=='accept':x['episode_production_script_accepted']=True
            if field=='order':x['untimed_paragraph_lexical_candidates'][1]['consensus_span_index']=0
            if field=='count':x['original_source_paragraphs']=346
            with self.subTest(field=field),self.assertRaises(ValueError):
                verify(x)


if __name__=='__main__':
    unittest.main()
