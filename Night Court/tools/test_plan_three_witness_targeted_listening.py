#!/usr/bin/env python3
"""Zero-media tests for all sixteen original S01E01 three-witness listening cases."""
import copy,json,unittest
from plan_three_witness_targeted_listening import SUMMARY,QUEUE,windows


class OriginalThreeWitnessListening(unittest.TestCase):
    def setup_data(self):
        return json.loads(SUMMARY.read_text('utf-8')),json.loads(QUEUE.read_text('utf-8'))

    def test_all_sixteen_cases_are_bounded_and_retain_original_srt(self):
        source,rows=self.setup_data()
        result=windows(source,rows)
        self.assertEqual(result['all_existing_disagreement_cases'],16)
        self.assertTrue(1<=result['distinct_short_listening_windows']<=16)
        self.assertLess(result['playback_request_total_ms'],200000)
        self.assertEqual({case['review_rank_not_certainty'] for case in result['ordered_by_disagreement_priority']},
                         set(range(1,17)))
        flattened=[rank for clip in result['playback_windows_chronological']
                   for rank in clip['linked_review_ranks']]
        self.assertEqual(sorted(flattened),list(range(1,17)))
        self.assertFalse(result['original_source_srt_modified'])
        self.assertFalse(result['dialogue_verified_or_speakers_identified'])
        self.assertFalse(result['complete_original_episode_screenplay_accepted'])
        for clip in result['playback_windows_chronological']:
            a,b=clip['playback_request_ms']
            self.assertTrue(0<=a<b<=result['source_duration_ms'])
            self.assertFalse(clip['original_video_source_human_listened'])

    def test_altered_original_sha_or_forged_human_review_rejected(self):
        source,rows=self.setup_data()
        source['original_srt_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'identity'):
            windows(source,rows)
        source,rows=self.setup_data()
        rows[0]['model_error_or_srt_error_determined']=True
        with self.assertRaisesRegex(ValueError,'misrepresented'):
            windows(source,rows)

    def test_duplicate_priorities_and_unbounded_time_rejected(self):
        source,rows=self.setup_data()
        rows[1]['review_rank_not_certainty']=rows[0]['review_rank_not_certainty']
        with self.assertRaisesRegex(ValueError,'misrepresented'):
            windows(source,rows)
        source,rows=self.setup_data()
        rows[0]['original_source_audio_time_ms']=[10,900000]
        with self.assertRaisesRegex(ValueError,'Unbounded'):
            windows(source,rows)

    def test_original_machine_agreement_not_permitted_to_overwrite_srt(self):
        source,rows=self.setup_data()
        rows[0]['episode_subtitle_or_script_auto_changed']=True
        with self.assertRaisesRegex(ValueError,'misrepresented'):
            windows(source,rows)


if __name__=='__main__':
    unittest.main()
