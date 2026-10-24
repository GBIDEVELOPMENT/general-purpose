#!/usr/bin/env python3
"""Joined S01E01 original-source AV review agenda must not promote measurements."""
import json,unittest
from build_s01e01_review_agenda import build,OUTPUT

class SourceReviewAgenda(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q=build()

    def test_all_original_11_voice_6_visual_and_7_video_candidate_tasks(self):
        q=self.q
        self.assertEqual(q["original_caption_turn_review_tasks"],11)
        self.assertEqual(q["original_visual_stage_review_tasks"],6)
        self.assertEqual(q["extra_machine_transition_review_prompts"],7)
        self.assertEqual(q["total_chronological_review_entries"],24)
        self.assertTrue(q["all_original_editorial_tasks_still_unaccepted"])
        self.assertEqual(q["total_full_episode_screenplays_verified"],0)
        tasks=q["chronological_review_entries"]
        self.assertEqual(len(tasks),24)
        self.assertEqual(len({t["task_id"] for t in tasks}),24)
        self.assertEqual([x["source_interval_ms"][0] for x in tasks],
                         sorted(x["source_interval_ms"][0] for x in tasks))
        self.assertTrue(all(t["review_state"]=="pending" for t in tasks))
        self.assertTrue(all(not t["named_character_or_expressive_delivery_verified"] for t in tasks))

    def test_no_acoustic_mix_or_video_score_promotes_dialogue(self):
        q=self.q
        voice=[t for t in q["chronological_review_entries"] if t["kind"]=="caption_turn"]
        self.assertEqual(len(voice),11)
        self.assertTrue(all(t["mixed_soundtrack_level_only"]["speech_presence_cannot_be_inferred"] for t in voice))
        cuts=[t for t in q["chronological_review_entries"] if t["kind"]=="unverified_machine_image_change"]
        self.assertEqual([t["source_interval_ms"][0] for t in cuts],
                         [59026,60928,68268,74107,76777,80948,82382])
        self.assertTrue(all(not t["independent_original_audio_or_video_review_conducted"] for t in cuts))

    def test_derived_source_packet_is_reproducible(self):
        self.assertEqual(self.q,json.loads(OUTPUT.read_text("utf-8")))

if __name__=="__main__":
    unittest.main()
