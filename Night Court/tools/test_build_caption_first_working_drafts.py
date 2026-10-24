#!/usr/bin/env python3
"""No-media complete dialogue working-draft acceptance, source SHA and specificity."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import tempfile
import unittest
from build_caption_first_working_drafts import (
    ROOT,PILOTS,SOURCE_SHA,render_episode,witness,sample_indices,
    visual_material
)


class CaptionFirstDraft(unittest.TestCase):
    def test_two_complete_original_source_witnesses_are_included(self):
        for episode,expected in (("S01E01",336),("S09E19",347)):
            with self.subTest(episode=episode):
                script,manifest,queue=render_episode(episode)
                self.assertEqual(manifest["source_caption_cues"],expected)
                self.assertEqual(manifest["written_source_cue_ids_in_order"],
                                 list(range(1,expected+1)))
                self.assertTrue(manifest["caption_source_is_default_dialogue"])
                self.assertFalse(manifest["asr_may_override_original_caption_automatically"])
                self.assertFalse(manifest["whole_episode_audiovisual_screenplay_accepted"])
                self.assertFalse(manifest["scene_spatial_and_physical_comedy_coverage_complete"])
                self.assertEqual(manifest["embedded_source_video_sampled_action_notes"],6)
                self.assertEqual(manifest["targeted_original_audio_review_requests"],len(queue))
                self.assertIn("WORKING SCREENPLAY DRAFT",script)
                self.assertIn(f"C{expected:03d}.1",script)
                self.assertIn("Full synchronized audiovisual scene audit: NOT DONE",script)

    def test_real_pilot_characteristically_specific_visuals(self):
        a,am,aq=render_episode("S01E01")
        self.assertIn("BOOK-LINED COURT OFFICE",a)
        self.assertIn("telephone",a)
        self.assertIn('Did you say "mercurial"?',a)
        self.assertIn("Tell the judge the mayor called.",a)
        self.assertEqual(am["targeted_asr_disagreement_requests"],16)
        self.assertTrue(all(x["original_text_preserved"] for x in aq))
        self.assertFalse(any(x["original_audio_listened_to_resolve"] for x in aq))
        b,bm,bq=render_episode("S09E19")
        self.assertIn("COUNTER AND TABLES",b)
        self.assertIn("It's a turkey sandwich.",b)
        self.assertIn("source 15:00",b)
        self.assertEqual(bm["targeted_asr_disagreement_requests"],0)
        self.assertFalse(bm["timed_original_source"])
        self.assertFalse(bm["source_paragraph_timestamps_invented"])
        self.assertNotIn("15:00.000 · C240",b)

    def test_deterministic_sampling_with_spread(self):
        self.assertEqual(sample_indices(347),sorted(sample_indices(347)))
        self.assertEqual(sample_indices(347)[0],1)
        self.assertEqual(sample_indices(347)[-1],347)
        self.assertEqual(len(sample_indices(347)),8)

    def test_source_fingerprints_and_original_timing_are_not_mutated(self):
        for episode in PILOTS:
            before=(ROOT/"seasons"/episode[:3]/episode/"episode.json").read_bytes()
            first=render_episode(episode)
            second=render_episode(episode)
            self.assertEqual(first,second)
            self.assertEqual(first[1]["original_caption_sha256"],SOURCE_SHA[episode])
            self.assertEqual(before,(ROOT/"seasons"/episode[:3]/episode/"episode.json").read_bytes())


if __name__=="__main__":
    unittest.main()
