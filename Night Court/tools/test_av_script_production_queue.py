#!/usr/bin/env python3
"""Source-only inputs must be complete; no sampled scene can claim full AV QA."""
import unittest
from build_av_script_production_queue import build

class WorkQueue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.j=build()
    def test_all_sources_accounted(self):
        x=self.j
        self.assertEqual(x["original_episode_records"],193)
        self.assertEqual(x["source_reading_scripts_ready"],193)
        self.assertEqual(x["source_voice_packets_ready"],193)
        self.assertEqual(x["source_participation_packets_ready"],193)
        self.assertEqual(x["filename_only_video_candidates"],193)
        self.assertEqual(x["original_caption_cues"],70804)
        self.assertEqual(x["source_only_dialogue_units"],72733)
        self.assertEqual(x["source_only_voice_attribution_units"],72823)
        self.assertEqual(x["provisional_scene_gap_clusters"],508)
    def test_no_false_audiovisual_acceptance(self):
        x=self.j
        self.assertEqual(x["episode_scripts_independently_av_verified"],0)
        self.assertEqual(len({r["episode_id"] for r in x["episodes"]}),193)
        for r in x["episodes"]:
            self.assertFalse(r["speaker_verified"])
            self.assertFalse(r["full_episode_screenplay_verified"])
            self.assertEqual(r["stage_acceptance"]["full_episode_independent_av_QA"],"not_verified")
            self.assertTrue(r["source_metadata"]["video_filename_identity_only"])
    def test_S01_pilot_and_untimed_exception(self):
        x=self.j
        self.assertEqual(x["episodes"][0]["episode_id"],"S01E01")
        self.assertEqual(x["episodes"][0]["status"],"S01E01_bounded_AV_experiment_only")
        untimed=next(z for z in x["episodes"] if z["episode_id"]=="S09E19")
        self.assertFalse(untimed["source_metadata"]["timed"])
        self.assertTrue(any("untimed" in z for z in untimed["next_tasks"]))
        self.assertFalse(untimed["speaker_verified"])

if __name__=="__main__":unittest.main()
