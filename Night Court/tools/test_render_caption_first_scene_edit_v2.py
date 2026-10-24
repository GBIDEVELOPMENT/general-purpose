#!/usr/bin/env python3
"""Source photograph/complete-caption editorial script regressions."""
import unittest
from render_caption_first_scene_edit_v2 import edit,source_visuals,VIDEO_SHA


class SceneEditTests(unittest.TestCase):
    def test_original_dialogue_unchanged_and_photo_observations_present(self):
        for episode,count,cues in (("S01E01",17,336),("S09E19",16,347)):
            with self.subTest(episode=episode):
                script,m=edit(episode)
                self.assertEqual(m["directly_inspected_source_photo_observations"],count)
                self.assertEqual(m["original_rendered_caption_cues"],cues)
                self.assertEqual(m["original_video_sha256"],VIDEO_SHA[episode])
                self.assertFalse(m["original_dialogue_text_changed"])
                self.assertFalse(m["original_source_caption_timestamps_invented"])
                self.assertFalse(m["full_episode_editor_ready"])
                self.assertFalse(m["independent_archival_AV_acceptance"])
                self.assertIn(f"C{cues:03d}.1",script)
                self.assertIn("Directly observed original-video scene",script)
                self.assertEqual((script,m),edit(episode))

    def test_actual_scene_description_variation(self):
        a,ma=edit("S01E01")
        b,mb=edit("S09E19")
        self.assertIn("nighttime city skyline",a)
        self.assertIn("reclines along the judicial bench",a)
        self.assertIn("HARRY STONE · DIALOGUE-INFERRED",a)
        self.assertIn("LANA WAGNER · DIALOGUE-INFERRED",a)
        self.assertIn("The restaurant meeting",b)
        self.assertIn("bright spark or flame",b)
        self.assertIn("C347.1 · UNTIMED",b)
        self.assertIn("SELF-INTRODUCING AS ALEX PATTERSON",b)
        self.assertEqual(ma["inserted_original_timed_picture_notes"],17)
        self.assertEqual(mb["inserted_original_timed_picture_notes"],0)
        self.assertEqual(mb["source_transcript_story_beats"],8)

    def test_original_frame_review_is_never_mislabeled_acceptance(self):
        for episode in ("S01E01","S09E19"):
            items,digest,report=source_visuals(episode)
            self.assertTrue(all(len(x["source_thumbnail_sha256"])==64 for x in items))
            self.assertFalse(report["continuous_scene_boundaries_verified"])
            self.assertFalse(report["speaker_identity_from_picture_asserted"])


if __name__=="__main__":
    unittest.main()
