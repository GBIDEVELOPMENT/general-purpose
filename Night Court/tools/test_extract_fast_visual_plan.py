#!/usr/bin/env python3
"""End-to-end synthetic 24fps FFmpeg source image PTS tests, zero real video."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from plan_fast_visual_pass import make_plan
from extract_fast_visual_plan import extract,validate_plan


class FastOriginalFrameExtraction(unittest.TestCase):
    def test_real_ffmpeg_source_pts_and_hard_image_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            video=root/'source.avi'
            subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error',
                            '-f','lavfi','-i','testsrc2=size=160x90:rate=24:duration=6',
                            '-c:v','mpeg4','-q:v','10',str(video)],
                           check=True,capture_output=True,timeout=60)
            with video.open('rb') as f:source_sha=hashlib.file_digest(f,'sha256').hexdigest()
            source={'schema':'night-court-fast-visual-input/1',
                    'episode_id':'S01E01','source_video_sha256':source_sha,
                    'duration_ms':6000,'window_ms':[0,6000],
                    'avg_frame_rate':'24','frame_rate_provenance':'verified_local_ffprobe',
                    'cut_candidates':[{'time_ms':4000,'image_change_score':0.7}],
                    'activity_events':[{'event_id':'test-motion','time_ms':3000,
                                        'priority':5,'mode':'gesture'}]}
            plan=make_plan(source)
            self.assertGreaterEqual(plan['counts']['frames'],5)
            report=extract(video,plan,root/'images',expected_media_bytes=video.stat().st_size)
            self.assertEqual(report['extraction_frame_count'],plan['counts']['frames'])
            self.assertTrue(report['all_samples_within_source_pts_tolerance'],report)
            self.assertTrue(report['images_located_only_outside_checkout'])
            self.assertLess(report['total_image_bytes'],10_000_000)
            self.assertTrue((root/'images/index.json').is_file())
            self.assertEqual(report['frames'][0]['sha256'],
                hashlib.sha256((root/'images/frames/frame-001.jpg').read_bytes()).hexdigest())
            with self.assertRaisesRegex(ValueError,'missing, changed'):
                extract(video,plan,root/'another',expected_media_bytes=video.stat().st_size+1)

    def test_plan_must_have_actual_ffprobe_provenance_not_unverified_24fps(self):
        source={'schema':'night-court-fast-visual-input/1',
                'episode_id':'S01E01','source_video_sha256':'1'*64,
                'duration_ms':4000,'avg_frame_rate':'24',
                'frame_rate_provenance':'synthetic_unverified_assumption',
                'activity_events':[{'event_id':'x','time_ms':1500,'priority':5}]}
        plan=make_plan(source)
        with self.assertRaisesRegex(ValueError,'verified original ffprobe'):
            validate_plan(plan)
        plan['frame_rate_provenance']='verified_local_ffprobe'
        validate_plan(plan)
        broken=copy.deepcopy(plan)
        broken['frames'][0]['nominal_ms']+=500
        with self.assertRaisesRegex(ValueError,'inconsistent'):
            validate_plan(broken)
        broken=copy.deepcopy(plan)
        broken['frames'].append(copy.deepcopy(broken['frames'][-1]))
        broken['counts']['frames']+=1
        with self.assertRaisesRegex(ValueError,'unique'):
            validate_plan(broken)


if __name__=='__main__':unittest.main()
