#!/usr/bin/env python3
"""Fast independent model agreement regression; no real source or models required."""
import unittest
from compare_independent_asr import compare


def case():
    def words(texts,offset=0):
        return [{'text':v,'start_ms':i*400+offset+100,'end_ms':i*400+offset+380}
                for i,v in enumerate(texts)]
    return {'schema':'night-court-two-independent-asr-words/1',
            'episode_id':'S01E01','source_video_sha256':'1'*64,
            'decoded_audio_sha256':'2'*64,'source_window_ms':[0,15000],
            'models':[{'model_id':'Whisper-1','architecture_family':'whisper',
                       'free_decoding':True,'srt_or_other_model_prompt_used':False,
                       'words':words(['Does','a','bear','extiphesate','in','the','forest','Bye','Bull'])},
                      {'model_id':'CTC-1','architecture_family':'conformer_ctc',
                       'free_decoding':True,'srt_or_other_model_prompt_used':False,
                       'words':words(['Does','a','bear','extiphesate','in','the','forest','Come','on'],offset=125)}]}

class ASRConsensus(unittest.TestCase):
    def test_positive_corroboration_and_independent_disagreement(self):
        report=compare(case())
        self.assertEqual(report['counts']['corroborated_words'],7)
        self.assertEqual(len(report['corroborated_spans']),1)
        self.assertEqual(report['corroborated_spans'][0]['model_a_verbatim_candidate'],
                         'Does a bear extiphesate in the forest')
        self.assertEqual(report['counts']['unresolved_word_candidates'],4)
        self.assertFalse(report['source_srt_verified'])
        self.assertFalse(report['original_source_audio_listened'])

    def test_shared_model_family_or_subtitle_prompt_rejected(self):
        for mutation in ('family','prompt','hash','timestamp'):
            value=case()
            if mutation=='family':value['models'][1]['architecture_family']='whisper'
            if mutation=='prompt':value['models'][0]['srt_or_other_model_prompt_used']=True
            if mutation=='hash':value['decoded_audio_sha256']='missing'
            if mutation=='timestamp':value['models'][1]['words'][2]['start_ms']=0
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):compare(value)

    def test_single_common_word_does_not_become_confident_phrase(self):
        x=case()
        x['models'][1]['words']=x['models'][1]['words'][:1]
        r=compare(x)
        self.assertEqual(r['counts']['paired_words'],1)
        self.assertEqual(r['counts']['corroborated_words'],0)

    def test_thousands_of_words_bounded(self):
        x=case()
        for model in x['models']:
            model['words']=[{'text':f'unique{i}','start_ms':i*120+2,'end_ms':i*120+110}
                            for i in range(10000)]
        x['source_window_ms']=[0,1500000]
        r=compare(x)
        self.assertEqual(r['counts']['corroborated_words'],10000)
        self.assertEqual(len(r['corroborated_spans']),1)

if __name__=='__main__':unittest.main()
