#!/usr/bin/env python3
"""Synthetic checksum/unsupported claim importer regression; no original video."""
import json,tempfile,unittest
from pathlib import Path
import import_s09e19_visual_review as I

def fixture(folder):
    (folder/"frames").mkdir()
    images=[]
    for i in range(100):
        name=f"frames/frame-{i+1:03d}.jpg"
        image=folder/name
        image.write_bytes(bytes([i%240])+b"synthetic review fixture"*10)
        images.append({
         "file":name,"sample_index":i+1,
         "approx_source_time_ms":900000+250*i,
         "source_time_qualification":"nominal_4fps_sample_not_original_frame_pts",
         "sha256":I.sha(image),
         "reviewed_for_scene_content":False,
         "motion_interpolation_verified":False})
    montage=folder/"contact-sheet.jpg"
    montage.write_bytes(b"synthetic montage only"*80)
    report={
      "schema":"night-court-s09e19-video-frame-samples/1",
      "episode_id":"S09E19",
      "source_original_avi_sha256":I.SOURCE_SHA,
      "original_untimed_text_sha256":I.TXT_SHA,
      "source_window_ms":[900000,925000],
      "nominal_sampling_hz":4,"sample_count":100,
      "frames":images,"contact_sheet_sha256":I.sha(montage),
      "source_paragraph_timecode_verified":False,
      "scene_setting_reviewed":False,
      "physical_action_continuous_video_reviewed":False,
      "character_speaker_identified":False,
      "episode_audiovisual_complete":False,
      "original_video_or_audio_in_artifact":False
    }
    (folder/"frame-source-index.json").write_text(json.dumps(report),"utf-8")
    return report

class VisualImporter(unittest.TestCase):
    def run_case(self,mutate=None):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)
            j=fixture(source)
            if mutate:mutate(j,source)
            (source/"frame-source-index.json").write_text(json.dumps(j),"utf-8")
            return I.validate(source)
    def test_unreviewed_exact_sample_passes(self):
        report,match=self.run_case()
        self.assertEqual(report["sample_count"],100)
        self.assertEqual(match["distinct_high_lexical_match_candidates"],5)
        self.assertFalse(report["scene_setting_reviewed"])
    def test_falsely_accepted_scene_rejected(self):
        with self.assertRaises(ValueError):self.run_case(lambda j,_:j.update(scene_setting_reviewed=True))
    def test_extra_media_file_rejected(self):
        def mut(j,p):(p/"episode-video.mp4").write_bytes(b"not authorized")
        with self.assertRaises(ValueError):self.run_case(mut)
    def test_frame_checksum_corruption_rejected(self):
        def mut(j,p):(p/"frames/frame-049.jpg").write_bytes(b"corrupted"*35)
        with self.assertRaises(ValueError):self.run_case(mut)
    def test_wrong_source_window_rejected(self):
        with self.assertRaises(ValueError):self.run_case(lambda j,_:j.update(source_window_ms=[0,25000]))
    def test_false_speaker_attribution_rejected(self):
        with self.assertRaises(ValueError):self.run_case(lambda j,_:j.update(character_speaker_identified=True))

if __name__=="__main__":unittest.main()
