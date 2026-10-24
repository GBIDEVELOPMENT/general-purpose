#!/usr/bin/env python3
"""Hash-pinned source-video/untimed AV triplet numeric cost record QA."""
import json
from pathlib import Path
import unittest

FILE=Path(__file__).resolve().parents[1]/'research/s09e19-original-triad-stage-speed-2026-10-24.json'


class OriginalTriadTiming(unittest.TestCase):
    def test_real_episode_hash_cost_and_nonacceptance(self):
        v=json.loads(FILE.read_text('utf-8'))
        self.assertEqual(v['schema'],'night-court-s09e19-source-triad-stage-cost-summary/1')
        self.assertEqual(v['episode_id'],'S09E19')
        p=v['source_provenance']
        self.assertEqual(p['trusted_github_run'],40128021777)
        self.assertEqual(p['source_artifact_id'],12572964697)
        self.assertEqual(p['artifact_json_sha256'],'9032cd9308e904d2c52da261c6f8b2538565555a0588cbef0ff7388e390dfa57')
        self.assertEqual(p['artifact_zip_sha256'],'1098410992cd41e9a488ba93273e33c947568becda1eeaba73beee8e8db3084a')
        self.assertEqual(p['original_video_sha256'],'51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649')
        self.assertEqual(p['original_untimed_dialogue_sha256'],'659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2')
        self.assertEqual(v['original_source_paragraph_count'],347)
        self.assertEqual(v['original_source_paragraph_timestamps'],0)
        self.assertEqual(v['source_encoded_fps'],'30000/1001')
        wall=v['processing']['source_once_wall_seconds_excluding_install_and_job_startup']
        steps=v['processing']['components_seconds']
        self.assertEqual(wall,170.522)
        self.assertEqual(steps['ephemeral_three_frame_pixel_difference_seconds'],.053)
        self.assertLess(abs(sum(steps.values())-wall),.02)
        counts=v['evidence_counts']
        self.assertEqual(counts['triads_with_pixel_change_scores'],31)
        self.assertEqual(counts['triads_pts_order_abstentions'],0)
        self.assertEqual(counts['source_pts_verified_jpegs'],202)
        self.assertLessEqual(counts['source_pts_verified_jpegs'],240)
        self.assertLessEqual(counts['ephemeral_jpeg_bytes'],10_000_000)
        self.assertEqual(counts['source_avi_retrievals'],1)
        self.assertEqual(counts['pcm_decodes'],1)
        self.assertEqual(set(counts['independent_model_families']),{'whisper','kaldi_hmm_wfst'})
        self.assertEqual(len(v['pixel_change_ranked_top12']),12)
        last=float('inf')
        for event in v['pixel_change_ranked_top12']:
            times=event['source_frame_pts_ms_actual']
            self.assertEqual(len(times),3)
            self.assertTrue(0<=times[0]<times[1]<times[2]<v['original_video_duration_ms'])
            score=event['mean_temporal_pixel_change_score']
            self.assertTrue(0<=score<=last<=1)
            last=score
        self.assertTrue(all(flag is False for key,flag in v['limitations'].items()
            if key.endswith('_verified') or key.endswith('_created') or key.endswith('_committed') or key.endswith('_accepted')))
        self.assertEqual(v['limitations']['older_s09e19_wall_seconds'],215.14)


if __name__=='__main__':
    unittest.main()
