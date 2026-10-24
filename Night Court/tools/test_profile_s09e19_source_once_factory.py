#!/usr/bin/env python3
"""Credential-free second source-once episode pilot integrity and resampling QA."""
import hashlib
import unittest
from plan_fast_visual_pass import make_plan
from profile_s09e19_source_once_factory import (
    SHA,BYTES,TXT_SHA,original_events,review_untimed_paragraphs
)
from s09e19_untimed_video_anchor_pilot import (
    exact_candidate,sources
)


class UntimedOriginalSecondEpisode(unittest.TestCase):
    def test_s09_avi_owner_inventory_and_original_347_untimed_text(self):
        source=exact_candidate()
        self.assertEqual(source['episode_id_from_filename'],'S09E19')
        self.assertEqual(source['size_bytes'],BYTES)
        self.assertEqual(SHA,'51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649')
        paragraphs=sources()
        self.assertEqual(len(paragraphs),347)
        self.assertTrue(all(p.get('start_ms') is None and p.get('end_ms') is None
                            for p in paragraphs))

    def test_six_existing_source_visual_tasks_in_safe_second_episode_plan(self):
        import json
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]
        path=root/'seasons/S09/S09E19/derived/editorial-review-v1/untimed-scene-review-queue.json'
        packet=json.loads(path.read_text('utf-8'))
        changes=[{'time_ms':910000,'image_change_score':.9},
                 {'time_ms':913130,'image_change_score':.7}]
        events=original_events(changes,1320144,packet)
        self.assertEqual(len([x for x in events if x['event_id'].startswith('S09-V')]),6)
        plan=make_plan({
           'schema':'night-court-fast-visual-input/1','episode_id':'S09E19',
           'source_video_sha256':SHA,'duration_ms':1320144,
           'window_ms':[0,1320144],
           'avg_frame_rate':'30000/1001',
           'frame_rate_provenance':'synthetic_unverified_assumption',
           'cut_candidates':changes,'activity_events':events})
        self.assertLessEqual(plan['counts']['frames'],240)
        self.assertLessEqual(plan['counts']['bursts'],32)
        self.assertFalse(plan['candidate_cuts_are_independently_verified'])
        self.assertFalse(plan['speaker_action_or_script_accepted'])

    def test_independent_asr_cannot_create_times_for_untimed_paragraphs(self):
        paragraphs=sources()
        text=paragraphs[240]['text']
        spans=[{'model_a_verbatim_candidate':text,'time_interval_ms':[550000,554000]}]
        report=review_untimed_paragraphs(spans,paragraphs)
        self.assertEqual(len(report),1)
        self.assertIsNone(report[0]['original_source_paragraph_time_ms'])
        self.assertFalse(report[0]['word_identity_original_audio_human_verified'])
        self.assertIn('lexical',report[0]['lexical_uniqueness_status'])
        self.assertEqual(report[0]['independent_model_agreed_text_hypothesis'],text)


if __name__=='__main__':
    unittest.main()
