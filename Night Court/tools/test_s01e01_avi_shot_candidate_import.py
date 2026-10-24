#!/usr/bin/env python3
import copy,json,unittest
from validate_s01e01_avi_shot_candidate_import import validate,RESULT

class OriginalAVPTSImport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.j=json.loads(RESULT.read_text("utf-8"))

    def test_seven_source_shot_candidates_only(self):
        r=validate()
        self.assertEqual(r["original_frame_rate_candidate_count"],7)
        self.assertEqual(r["verified_edits_or_source_speakers"],0)
        self.assertFalse(r["production_script_verified"])
        self.assertEqual(r["absolute_candidate_PTS_ms"],[59026,60928,68268,74107,76777,80948,82382])

    def test_wrong_original_video_sha_or_source_range(self):
        d=copy.deepcopy(self.j);d["source_original_video_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"provenance"):validate(d)
        d=copy.deepcopy(self.j);d["source_window_ms"]=[0,36000]
        with self.assertRaisesRegex(ValueError,"provenance"):validate(d)

    def test_mutated_score_or_PTS_rejected(self):
        d=copy.deepcopy(self.j);d["candidate_shot_changes"][0]["ffmpeg_scene_score"]=.9999
        with self.assertRaisesRegex(ValueError,"time/score"):validate(d)
        d=copy.deepcopy(self.j);d["candidate_shot_changes"][1]["original_stream_pts_candidate_ms"]=59026
        with self.assertRaisesRegex(ValueError,"time/score"):validate(d)

    def test_no_script_promotion_from_image_diff(self):
        for key in ("scene_boundaries_verified","production_script_accepted",
                    "speaker_or_character_identity_verified",
                    "original_video_to_subtitle_alignment_verified"):
            with self.subTest(key=key):
                d=copy.deepcopy(self.j);d[key]=True
                with self.assertRaisesRegex(ValueError,"cannot accept"):validate(d)

if __name__=="__main__":
    unittest.main()
