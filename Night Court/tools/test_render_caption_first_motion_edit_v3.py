#!/usr/bin/env python3
"""Real sourced motion stills in both complete original-dialogue screenplay revisions."""
import copy
import json
import unittest

from render_caption_first_motion_edit_v3 import render,evidence,WINDOWS
from render_caption_first_scene_edit_v2 import edit as prior_edit


class SourceMotionDraftTests(unittest.TestCase):
    def test_all_caption_dialogue_kept_with_picture_action(self):
        for episode,cues,frames in (("S01E01",336,210),("S09E19",347,200)):
            with self.subTest(episode=episode):
                previous,_=prior_edit(episode)
                newer,manifest=render(episode)
                self.assertEqual(manifest["complete_original_held_caption_cues"],cues)
                self.assertEqual(manifest["source_motion_frames_reviewed_in_bounded_sequences"],frames)
                self.assertEqual(manifest["reviewed_picture_windows"],2)
                self.assertTrue(manifest["all_original_dialogue_preserved_from_v2"])
                self.assertFalse(manifest["source_original_audio_listened_for_four_sequences"])
                self.assertFalse(manifest["untimed_paragraph_source_timecode_fabricated"])
                self.assertFalse(manifest["speaker_name_from_original_picture_guessed"])
                self.assertFalse(manifest["editor_ready"])
                self.assertFalse(manifest["independent_AV_certified"])
                self.assertIn(f"C{cues:03d}.1",newer)
                self.assertIn("Actual source-picture physical business",newer)
                self.assertGreater(len(newer),len(previous))
                self.assertEqual((newer,manifest),render(episode))
                self.assertEqual(newer.count("PHYSICAL ACTION SAMPLE"),
                                 2 if episode=="S01E01" else 0)

    def test_scene_descriptions_from_original_images(self):
        s,_=render("S01E01")
        self.assertIn("padded ledge beneath the office windows",s)
        self.assertIn("The image alternates between her approach",s)
        s,_=render("S09E19")
        self.assertIn("A thin dark length on the floor begins spitting bright sparks",s)
        self.assertIn("woman in a burgundy dress",s)
        self.assertIn("347",json.dumps(render("S09E19")[1]))
        self.assertIn("C347.1 · UNTIMED",s)

    def test_photo_source_never_as_verified_action_or_voice(self):
        for episode in WINDOWS:
            seq,digest,manifest=evidence(episode)
            self.assertEqual(len(seq),2)
            self.assertFalse(manifest["source_original_audio_listened_during_picture_annotation"])
            self.assertFalse(manifest["named_actors_or_voices_identified"])
            self.assertTrue(all(x["source_picture_observation_status"]==
                                "reviewed_bounded_still_sequence_not_audio_verified"
                                for x in seq))


if __name__=="__main__":
    unittest.main()
