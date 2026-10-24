#!/usr/bin/env python3
"""Offline provenance and source-time regression for the first continuous AV review cut."""
import copy
import unittest
from build_s01e01_review_cut_manifest import build, verify_local_video
from pathlib import Path
import json
from build_s01e01_review_cut_manifest import WORKLIST, BOARD, SCENE

class ReviewCuts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=build()

    def test_all_tasks_have_full_contiguous_review_coverage(self):
        m=self.manifest
        self.assertEqual(m["voice_tasks"],11)
        self.assertEqual(m["visual_tasks"],6)
        self.assertEqual(len(m["tasks"]),17)
        self.assertEqual(len(m["continuous_review_windows"]),1)
        w=m["continuous_review_windows"][0]
        self.assertEqual((w["start_ms"],w["end_ms"]),(56912,93074))
        self.assertEqual(w["duration_ms"],36162)
        self.assertEqual(len(w["task_ids"]),17)
        for task in m["tasks"]:
            a,b=task["source_interval_ms"]
            self.assertLessEqual(w["start_ms"],a)
            self.assertGreaterEqual(w["end_ms"],b)

    def test_outside_pilot_margins_are_mandatory(self):
        self.assertEqual(self.manifest["outside_existing_sample_task_ids"],
                         ["S01E01:C00019.1","S01E01:C00019.2","S01E01:C00027.1"])
        self.assertEqual(self.manifest["publication_status"],
                         "review_material_only_zero_av_acceptances")

    def test_cross_source_identity_tampering_rejected(self):
        packet=json.loads(WORKLIST.read_text())
        board=json.loads(BOARD.read_text())
        scene=json.loads(SCENE.read_text())
        scene["source_media_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"fingerprints disagree"):
            build(packet,board,scene)
        packet["voice_review_tasks"][0]["source_caption_interval_ms"]=[0,True]
        with self.assertRaisesRegex(ValueError,"Invalid original source interval"):
            build(packet,board,json.loads(SCENE.read_text()))

    def test_unknown_or_repeated_tasks_and_false_acceptance_rejected(self):
        packet=json.loads(WORKLIST.read_text())
        packet["voice_review_tasks"][1]["task_id"]=packet["voice_review_tasks"][0]["task_id"]
        with self.assertRaisesRegex(ValueError,"duplicated"):
            build(packet)
        packet=json.loads(WORKLIST.read_text())
        packet["voice_review_tasks"][0]["audio_text_confirmation"]="confirmed_by_model_only"
        with self.assertRaisesRegex(ValueError,"already been accepted"):
            build(packet)

    def test_wrong_local_video_cannot_be_used_for_review(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/"source.avi"
            file.write_bytes(b"not the original")
            with self.assertRaisesRegex(ValueError,"incorrect byte length"):
                verify_local_video(file,self.manifest)

if __name__=="__main__":
    unittest.main()
