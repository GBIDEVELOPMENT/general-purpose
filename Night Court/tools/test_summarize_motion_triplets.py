#!/usr/bin/env python3
"""Offline JPEG-triplet action-review prioritization and provenance regression."""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from PIL import Image

from summarize_motion_triplets import summarize


SHA='5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962'


def fixture(directory):
    folder=directory/'frames'
    folder.mkdir()
    proposed=[]
    captured=[]
    for i,value in enumerate((0,255,255),start=1):
        file=folder/f'frame-{i:03d}.jpg'
        Image.new('L',(96,64),color=value).save(file,format='JPEG',quality=90)
        ms=i*100
        proposed.append({'nominal_frame_index':i,'nominal_ms':ms,
                         'candidate_shot_partition':0,'role':'motion_burst',
                         'evidence_event_id':'gesture'})
        captured.append({'source_frame_index_nominal':i,'source_frame_pts_ms_actual':ms,
                         'nominal_ms':ms,'matched_within_125ms':True,
                         'candidate_shot_partition':0,'role':'motion_burst','event_id':'gesture',
                         'frame_filename':file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
                         'bytes':file.stat().st_size})
    plan={'schema':'night-court-fast-visual-sampling-plan/1',
          'source_video_sha256':SHA,'frame_rate_provenance':'verified_local_ffprobe',
          'candidate_cuts_are_independently_verified':False,'frames':proposed,
          'motion_bursts':[{'event_id':'gesture','frame_count':3,
                            'candidate_shot_partition':0,'nominal_frame_times_ms':[100,200,300]}]}
    evidence={'schema':'night-court-budgeted-original-source-frame-execution/1',
             'original_video_sha256':SHA,'all_samples_within_source_pts_tolerance':True,
             'all_scene_and_action_verification_pending':True,
             'extraction_frame_count':3,'frames':captured}
    return plan,evidence,folder


class MotionTriplets(unittest.TestCase):
    def test_actual_jpegs_measure_change_without_claiming_stage_action(self):
        with tempfile.TemporaryDirectory() as root:
            plan,capture,folder=fixture(Path(root))
            report=summarize(plan,capture,folder)
            self.assertEqual(report['triple_count'],1)
            self.assertEqual(report['pts_order_abstentions'],0)
            self.assertEqual(report['analyzed_three_frame_groups'],1)
            event=report['review_priority'][0]
            self.assertGreater(event['first_temporal_pixel_difference']['mean_normalized_abs_delta'],.95)
            self.assertEqual(event['second_temporal_pixel_difference']['mean_normalized_abs_delta'],0)
            self.assertFalse(report['true_cuts_or_character_actions_verified'])
            self.assertFalse(report['production_script_accepted'])
            self.assertFalse(report['retained_source_image_pixels'])

    def test_reversed_pts_must_abstain_not_fabricate_continuity(self):
        with tempfile.TemporaryDirectory() as root:
            plan,capture,folder=fixture(Path(root))
            capture['frames'][1]['source_frame_pts_ms_actual']=100
            result=summarize(plan,capture,folder)
            self.assertEqual(result['analyzed_three_frame_groups'],0)
            self.assertEqual(result['pts_order_abstentions'],1)
            self.assertEqual(result['abstentions'][0]['interpretation_status'],
                             'abstain_non_increasing_actual_source_pts')

    def test_reject_wrong_shot_partition_and_modified_image(self):
        with tempfile.TemporaryDirectory() as root:
            plan,capture,folder=fixture(Path(root))
            plan['frames'][1]['candidate_shot_partition']=1
            with self.assertRaisesRegex(ValueError,'identity'):
                summarize(plan,capture,folder)
            plan['frames'][1]['candidate_shot_partition']=0
            (folder/'frame-002.jpg').write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'byte count|SHA mismatch'):
                summarize(plan,capture,folder)

    def test_reject_unverified_fps_and_forged_movie_sha(self):
        with tempfile.TemporaryDirectory() as root:
            plan,capture,folder=fixture(Path(root))
            plan['frame_rate_provenance']='synthetic_unverified_assumption'
            with self.assertRaisesRegex(ValueError,'verified-source'):
                summarize(plan,capture,folder)
            plan['frame_rate_provenance']='verified_local_ffprobe'
            capture['original_video_sha256']='f'*64
            with self.assertRaisesRegex(ValueError,'verified-source'):
                summarize(plan,capture,folder)


if __name__=='__main__':
    unittest.main()
