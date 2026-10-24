#!/usr/bin/env python3
import copy,unittest
from validate_s01e01_audio_energy_import import verify,WORKLIST,START,END

class SourceSoundtrackEnvelope(unittest.TestCase):
    def fake(self):
        import json
        q=json.loads(WORKLIST.read_text("utf-8"))
        bins=[{"index":i,"nominal_start_ms":START+i*100,
               "nominal_end_ms":min(END,START+(i+1)*100),
               "rms_dbfs":-24.0,"peak_dbfs":-10.0} for i in range(362)]
        turns=[]
        for t in q["voice_review_tasks"]:
            a,b=t["source_caption_interval_ms"]
            selected=[x for x in bins if x["nominal_end_ms"]>a and x["nominal_start_ms"]<b]
            turns.append({
              "source_task_id":t["task_id"],
              "original_source_caption_interval_ms":[a,b],
              "overlapping_mixed_audio_bin_count":len(selected),
              "mixed_soundtrack_rms_median_dbfs":-24.0,
              "mixed_soundtrack_peak_max_dbfs":-10.0,
              "original_speech_present_verified":False,
              "source_word_times_verified":False,
              "speaker_or_delivery_verified":False,
            })
        return {
           "schema":"night-court-s01e01-mixed-soundtrack-envelope/1",
           "episode_id":"S01E01",
           "original_video_sha256":q["source_video_sha256"],
           "original_source_srt_sha256":q["source_caption_sha256"],
           "source_review_window_ms":[START,END],
           "nominal_decoded_time_origin_ms":START,
           "decoded_sample_rate_hz":16000,
           "sample_count":578592,
           "duration_ms_derived_from_sample_count":36162,
           "level_bin_width_ms":100,
           "original_source_caption_turns":11,
           "level_bins":bins,
           "caption_turn_mixed_audio":turns,
           "human_listened_original_audio":False,
           "any_speech_words_verified":False,
           "speaker_identity_verified":False,
           "vocal_delivery_or_emotion_verified":False,
           "original_audio_to_caption_alignment_verified":False,
           "episode_screenplay_complete":False,
           "audio_PCM_or_AVI_exported":False
        }

    def test_correctly_source_indexed_fake_level_only(self):
        self.assertEqual(verify(self.fake()),(362,11))

    def test_edited_bin_time_and_unreproducible_median_rejected(self):
        d=self.fake();d["level_bins"][21]["nominal_start_ms"]+=20
        with self.assertRaisesRegex(ValueError,"source index"):verify(d)
        d=self.fake();d["caption_turn_mixed_audio"][0]["mixed_soundtrack_rms_median_dbfs"]=-31
        with self.assertRaisesRegex(ValueError,"does not match"):verify(d)

    def test_voice_or_word_acceptance_cannot_be_faked(self):
        d=self.fake();d["vocal_delivery_or_emotion_verified"]=True
        with self.assertRaisesRegex(ValueError,"cannot claim"):verify(d)
        d=self.fake();d["caption_turn_mixed_audio"][0]["original_speech_present_verified"]=True
        with self.assertRaisesRegex(ValueError,"cannot certify"):verify(d)

    def test_missing_source_turn_and_wrong_video(self):
        d=self.fake();d["caption_turn_mixed_audio"].pop()
        with self.assertRaisesRegex(ValueError,"11 source"):verify(d)
        d=self.fake();d["original_video_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"Wrong original"):verify(d)

if __name__=="__main__":
    unittest.main()
