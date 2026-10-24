#!/usr/bin/env python3
"""Pure-source, no FTP, no Pillow original-video overview provenance tests."""
import unittest
from capture_whole_episode_scene_atlas import sample_targets,manifest,SOURCE_SHA


class Atlas(unittest.TestCase):
    def test_actual_two_pilots_and_period_bounds(self):
        for ep,duration in (('S01E01',1448256),('S09E19',1320144)):
            timestamps=sample_targets(duration)
            self.assertLessEqual(len(timestamps),84)
            self.assertTrue(all(x<duration for x in timestamps))
            self.assertEqual(timestamps[0],9000)
            self.assertEqual(timestamps[1]-timestamps[0],18000)
            frames=[{'frame_id':i+1,'requested_original_source_time_ms':t,
                     'original_video_sha256':SOURCE_SHA[ep],
                     'jpg_sha256':'a'*64} for i,t in enumerate(timestamps)]
            data=manifest(ep,SOURCE_SHA[ep],duration,frames,[])
            self.assertFalse(data['actual_frames_inspected_for_settings'])
            self.assertFalse(data['source_shot_boundaries_verified'])
            self.assertFalse(data['continuous_original_video_action_reviewed'])
            self.assertFalse(data['screenplay_or_episode_accepted'])

    def test_reject_missing_frame_or_wrong_source_or_invented_bounds(self):
        sha=SOURCE_SHA['S09E19']
        times=sample_targets(1320144)
        frames=[{'requested_original_source_time_ms':t,
                 'original_video_sha256':sha,'jpg_sha256':'c'*64}
                for t in times]
        for check in ('wrong_sha','lost_frame','made_up_time'):
            bad=[dict(x) for x in frames]
            digest=sha
            if check=='wrong_sha':digest='b'*64
            if check=='lost_frame':bad.pop()
            if check=='made_up_time':bad[0]['requested_original_source_time_ms']=0
            with self.subTest(check=check),self.assertRaises(ValueError):
                manifest('S09E19',digest,1320144,bad,[])

    def test_refuse_unbounded_source_or_dense_decode(self):
        with self.assertRaises(ValueError):sample_targets(1320144,100)
        with self.assertRaises(ValueError):sample_targets(9999999)
        with self.assertRaises(ValueError):sample_targets(1200000,12000)


if __name__=='__main__':
    unittest.main()
