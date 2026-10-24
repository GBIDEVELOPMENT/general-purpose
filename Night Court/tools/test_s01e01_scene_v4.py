#!/usr/bin/env python3
import json,unittest
from validate_s01e01_scene_v4 import validate,SCRIPT,EDITION

class S01IntegratedSceneV4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md=SCRIPT.read_text("utf-8")
        cls.j=json.loads(EDITION.read_text("utf-8"))

    def test_all_source_events_preserved_zero_acceptances(self):
        r=validate()
        self.assertEqual(r["original_dialogue_turns_preserved"],11)
        self.assertEqual(r["source_frame_and_action_observations"],17)
        self.assertEqual(r["raw_image_difference_candidates"],7)
        self.assertEqual(r["integrated_timeline_events"],28)
        self.assertFalse(r["complete_original_episode_script_verified"])

    def test_script_cannot_alter_single_original_dialogue_turn(self):
        bad=self.md.replace('Did you say "mercurial"?','Did you say "mercury"?')
        with self.assertRaisesRegex(ValueError,"source caption turn"):validate(script=bad)

    def test_missing_original_frame_id_rejected(self):
        bad=self.md.replace("| S01-V3-06 |","| non-original-observation |")
        with self.assertRaisesRegex(ValueError,"source AVI frame evidence"):validate(script=bad)

    def test_no_false_script_promotion(self):
        d=dict(self.j);d["speaker_and_character_identity_verified"]=True
        with self.assertRaisesRegex(ValueError,"cannot self-certify"):validate(version=d)
        d=dict(self.j);d["complete_episode_production_screenplay_verified"]=True
        with self.assertRaisesRegex(ValueError,"cannot self-certify"):validate(version=d)

if __name__=="__main__":
    unittest.main()
