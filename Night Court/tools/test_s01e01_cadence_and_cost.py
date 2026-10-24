#!/usr/bin/env python3
"""Decode tiny synthetic sources to test cadence without owner video or FTP."""
import subprocess
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from probe_s01e01_cadence_and_cost import video_properties,sample_frame_cadence


class NativeCadenceTest(unittest.TestCase):
    def test_real_decoded_24_and_23976_fps(self):
        for rate in ('24','24000/1001'):
            with self.subTest(rate=rate),tempfile.TemporaryDirectory() as temp:
                video=Path(temp)/'cadence.avi'
                subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error',
                   '-f','lavfi','-i',f'testsrc2=size=160x90:rate={rate}:duration=6',
                   '-c:v','mpeg4','-q:v','20',str(video)],
                   check=True,capture_output=True,timeout=90)
                properties=video_properties(video,require_episode_duration=False)
                self.assertEqual(Fraction(properties['avg_frame_rate']),Fraction(rate))
                s=sample_frame_cadence(video,Fraction(rate),start_seconds=2)
                self.assertTrue(s['sample_interval_within_1pct_nominal'],s)
                self.assertFalse(s['whole_episode_cadence_verified'])
                self.assertGreaterEqual(s['pts_sample_count'],20)


if __name__=='__main__':
    unittest.main()
