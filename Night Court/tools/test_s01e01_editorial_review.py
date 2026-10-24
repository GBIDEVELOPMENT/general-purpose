#!/usr/bin/env python3
"""Original-source editorial audit: no model data can self-certify a screenplay."""
import unittest
from build_s01e01_editorial_review import build,summary,validate_sources

class AcceptanceWorklist(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.packet=build()
    def test_counts_and_source_coverage(self):
        p=self.packet
        self.assertEqual(p["counts"]["source_caption_cues"],9)
        self.assertEqual(p["counts"]["source_speaking_turns"],11)
        self.assertEqual(p["counts"]["source_words"],55)
        self.assertEqual(p["counts"]["visual_motion_observations"],6)
        self.assertEqual(p["counts"]["voice_turns_human_accepted"],0)
        self.assertEqual(p["counts"]["visual_events_continuous_video_accepted"],0)
        self.assertEqual(len(set(x["task_id"] for x in p["voice_review_tasks"])),11)
    def test_no_invented_identity_or_emotion(self):
        p=self.packet
        self.assertFalse(p["speaker_identity_verified"])
        self.assertFalse(p["acting_emotion_verified"])
        self.assertFalse(p["episode_audiovisual_complete"])
        for x in p["voice_review_tasks"]:
            self.assertIsNone(x["speaker_identity"])
            self.assertFalse(x["independent_human_acceptance"])
            self.assertFalse(x["visual_context_alone_proves_speaker"])
            self.assertEqual(x["audio_delivery_review"],"not_reviewed")
        for x in p["visual_review_tasks"]:
            self.assertIsNone(x["spoken_voice_from_visual_evidence"])
            self.assertFalse(x["continuous_video_observation_verified"])
            self.assertTrue(all(len(f["sha256"])==64 for f in x["supporting_source_frames"]))
    def test_unresolved_source_words_get_priority(self):
        p=self.packet
        word={x["original_normalized_word"]:x for t in p["voice_review_tasks"] for x in t["source_words"]}
        self.assertEqual(word["MINIMIFIDIAN"]["source_review_priority"],"no_usable_word_timing_candidate")
        self.assertTrue(p["voice_review_tasks"][0]["priority_score_for_editor_only"]>=
                        p["voice_review_tasks"][-1]["priority_score_for_editor_only"])
        doc=summary(p)
        self.assertIn("Needs continuous-video independent review",doc)
        self.assertIn("independently listen",doc)
    def test_cross_modal_source_integrity(self):
        self.assertEqual(len(validate_sources()),6)
        self.assertIn("source_model_comparison_categories",self.packet["counts"])
        self.assertEqual(sum(self.packet["counts"]["source_model_comparison_categories"].values()),55)

if __name__=="__main__":unittest.main()
