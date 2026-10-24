#!/usr/bin/env python3
"""Source-free segment budget, shot-candidate guard and low-score control QA."""
import copy
import unittest
from plan_fast_visual_pass import make_plan
from plan_continuous_action_review import plan_continuous_review


def synthetic(events, cuts=None, duration=30000):
    cuts=cuts or []
    plan=make_plan({
      'schema':'night-court-fast-visual-input/1',
      'episode_id':'S01E01','source_video_sha256':'5'*64,
      'duration_ms':duration,'avg_frame_rate':'24',
      'frame_rate_provenance':'verified_local_ffprobe',
      'cut_candidates':cuts,'activity_events':events
    })
    ranked=[]
    for i,event in enumerate(plan['motion_bursts']):
        ranked.append({'event_id':event['event_id'],
               'candidate_shot_partition':event['candidate_shot_partition'],
               'source_frame_pts_ms_actual':event['nominal_frame_times_ms'],
               'mean_temporal_pixel_change_score':round(.9-i*.03,6)})
    pixels={
      'schema':'night-court-ephemeral-triad-pixel-change-metadata/1',
      'source_video_sha256':'5'*64,'true_cuts_or_character_actions_verified':False,
      'production_script_accepted':False,'triple_count':len(ranked),
      'analyzed_three_frame_groups':len(ranked),'review_priority':ranked,
      'abstentions':[]
    }
    return plan,pixels


class ContinuousVideoReview(unittest.TestCase):
    def test_six_original_events_high_motion_and_low_score_holdouts(self):
        events=[{'event_id':f'motion-{i:02d}','time_ms':1000+i*1750,
                 'priority':5 if i<6 else 1} for i in range(15)]
        plan,pixels=synthetic(events)
        review=plan_continuous_review(plan,pixels,[])
        self.assertEqual(review['requested_video_excerpt_count'],12)
        self.assertLessEqual(review['requested_total_video_excerpt_ms'],12*2800)
        counts={}
        for row in review['review_requests']:
            counts[row['selection_reason']]=counts.get(row['selection_reason'],0)+1
            self.assertFalse(row['original_shot_and_action_human_verified'])
            self.assertFalse(row['draft_stage_direction_accepted'])
            a,b=row['time_window_ms_candidate_only']
            self.assertTrue(0<=a<b<=30000)
        self.assertEqual(counts['editorial_original_source_task'],6)
        self.assertEqual(counts['high_pixel_change_review'],4)
        self.assertEqual(counts['low_pixel_change_control'],2)
        self.assertFalse(review['human_continuous_video_review_done'])

    def test_crossing_actual_source_cut_must_not_be_presented_as_continuity(self):
        cuts=[{'time_ms':5000,'image_change_score':.95}]
        events=[{'event_id':'safe','time_ms':3400,'priority':5}]
        plan,pixels=synthetic(events,cuts,10000)
        pixels['review_priority'][0]['source_frame_pts_ms_actual']=[4900,5000,5100]
        out=plan_continuous_review(plan,pixels,cuts)
        self.assertEqual(out['requested_video_excerpt_count'],0)
        self.assertEqual(out['source_triads_deferred_actual_pts_cross_candidate_cut'],1)
        self.assertEqual(out['deferred_review_requests'][0]['reason'],
                         'actual_source_pts_cross_candidate_cut')

    def test_do_not_extend_narrow_visual_probe_across_candidate_cut(self):
        cuts=[{'time_ms':5000,'image_change_score':.9}]
        events=[{'event_id':'near-cut','time_ms':4800,'priority':5}]
        plan,pixels=synthetic(events,cuts,10000)
        self.assertEqual(len(plan['motion_bursts']),1)
        output=plan_continuous_review(plan,pixels,cuts)
        self.assertEqual(output['requested_video_excerpt_count'],0)
        self.assertEqual(output['deferred_review_requests'][0]['reason'],
                         'insufficient_candidate_shot_continuity')

    def test_source_hash_cut_count_and_real_pts_reject_forgery(self):
        cuts=[{'time_ms':10000,'image_change_score':.8}]
        plan,pixels=synthetic([{'event_id':'a','time_ms':3500,'priority':4}],cuts)
        self.assertEqual(plan_continuous_review(plan,pixels,cuts)['requested_video_excerpt_count'],1)
        corrupted=copy.deepcopy(pixels);corrupted['source_video_sha256']='a'*64
        with self.assertRaisesRegex(ValueError,'incompatible'):
            plan_continuous_review(plan,corrupted,cuts)
        with self.assertRaisesRegex(ValueError,'cuts differ'):
            plan_continuous_review(plan,pixels,[])
        corrupted=copy.deepcopy(pixels)
        corrupted['review_priority'][0]['source_frame_pts_ms_actual']=[3000,3000,3100]
        with self.assertRaisesRegex(ValueError,'malformed'):
            plan_continuous_review(plan,corrupted,cuts)


if __name__=='__main__':
    unittest.main()
