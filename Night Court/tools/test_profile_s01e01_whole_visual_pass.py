#!/usr/bin/env python3
"""Full source image-scan test on synthetic edited video and original text hashes."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from profile_s01e01_whole_visual_pass import (
    parse_full_avi_scores,scan_video,source_activity_events,SHA
)
from plan_fast_visual_pass import make_plan


class WholeEpisodeSourceVideoPlan(unittest.TestCase):
    def test_score_parser_handles_reordered_actual_pts_and_duplicate_candidates(self):
        log="""[Parsed_metadata_2 @ xyz] frame:0    pts:900    pts_time:30.000
[Parsed_metadata_2 @ xyz] lavfi.scene_score=0.850000
[Parsed_metadata_2 @ xyz] frame:1 pts:1000 pts_time:33.333
[Parsed_metadata_2 @ xyz] lavfi.scene_score=0.500000
[Parsed_metadata_2 @ xyz] frame:2 pts:980 pts_time:32.666
[Parsed_metadata_2 @ xyz] lavfi.scene_score=0.650000
[Parsed_metadata_2 @ xyz] frame:3 pts:980 pts_time:32.666
[Parsed_metadata_2 @ xyz] lavfi.scene_score=0.750000"""
        rows,trace=parse_full_avi_scores(log,duration_ms=1448256)
        self.assertEqual([r['time_ms'] for r in rows],[30000,32666,33333])
        self.assertEqual(rows[1]['image_change_score'],.75)
        self.assertEqual(trace['duplicate_timestamp_rows'],1)
        self.assertEqual(trace['ordered_or_tied_timestamp_steps'],2)

    def test_source_event_planning_never_promotes_image_motion_or_speakers(self):
        cuts=[{'time_ms':59026,'image_change_score':.306},
              {'time_ms':60928,'image_change_score':.143},
              {'time_ms':68268,'image_change_score':.139}]
        events,count=source_activity_events(cuts,1448256)
        self.assertEqual(len([e for e in events if e['event_id'].startswith('OBS-')]),6)
        self.assertLessEqual(count,26)
        plan=make_plan({'schema':'night-court-fast-visual-input/1',
          'episode_id':'S01E01','source_video_sha256':SHA,
          'duration_ms':1448256,'window_ms':[0,1448256],
          'avg_frame_rate':'30000/1001','frame_rate_provenance':'verified_local_ffprobe',
          'cut_candidates':cuts,'activity_events':events})
        self.assertLessEqual(plan['counts']['frames'],240)
        self.assertEqual(plan['nominal_avg_frame_rate'],'30000/1001')
        self.assertFalse(plan['candidate_cuts_are_independently_verified'])
        self.assertFalse(plan['speaker_action_or_script_accepted'])

    def test_synthetic_hard_cuts_full_untrimmed_ffmpeg_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'hard-cuts.avi'
            subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error',
              '-f','lavfi','-i','color=black:s=160x90:r=24:d=5',
              '-f','lavfi','-i','color=white:s=160x90:r=24:d=3',
              '-f','lavfi','-i','color=blue:s=160x90:r=24:d=4',
              '-filter_complex','[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]',
              '-map','[v]','-c:v','mpeg4','-q:v','6',str(path)],
              check=True,capture_output=True,timeout=60)
            scores,trace=scan_video(path,duration_ms=1448256)
            times=[x['time_ms'] for x in scores]
            self.assertIn(5000,times)
            self.assertIn(8000,times)
            self.assertEqual(len(times),2)
            self.assertEqual(trace['duplicate_timestamp_rows'],0)


if __name__=='__main__':
    unittest.main()
