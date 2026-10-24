#!/usr/bin/env python3
"""No model word, speaker or original subtitle acceptance through full-cut ASR import."""
import copy,json,unittest
from validate_s01e01_full_asr_import import validate

class Original36sWhisperImport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Only the real source job artifact may be imported. Tests must use
        # a harmless synthetic record with the same shape and source IDs.
        from pathlib import Path
        p=Path(__file__).resolve().parents[1]/"seasons/S01/S01E01/derived/editorial-review-v1/acceptance-worklist.json"
        tasks=json.loads(p.read_text())["voice_review_tasks"]
        segs=[]
        for i,t in enumerate(tasks):
            a,b=t["source_caption_interval_ms"]
            segs.append({
              "index":i,"start_ms":max(56912,a),"end_ms":min(93074,b),
              "text":"synthetic unit test only",
              "avg_logprob":-.5,"no_speech_prob":0.1,
              "source_timecode_status":"model_proposal_not_reviewed_video_source_alignment",
              "word_time_candidates":[],"speaker_identity":None,
              "human_original_audio_reviewed":False})
        # Real source ASR importer strictly expects all 60 word hypotheses,
        # so use a minimal adversarial structure to test positive/negative
        # acceptance without original audio/media bytes.
        for i,s in enumerate(segs):
            words=6 if i<5 else 5
            for j in range(words):
                a=s["start_ms"]+(j*(s["end_ms"]-s["start_ms"]))//words
                b=s["start_ms"]+((j+1)*(s["end_ms"]-s["start_ms"]))//words
                s["word_time_candidates"].append({
                  "text":"synthetic","start_ms":a,"end_ms":b,
                  "model_probability":.5
                })
        segs.append({
          "index":11,"start_ms":92412,"end_ms":93052,
          "text":"synthetic test","avg_logprob":-.5,"no_speech_prob":.1,
          "source_timecode_status":"model_proposal_not_reviewed_video_source_alignment",
          "word_time_candidates":[],"speaker_identity":None,
          "human_original_audio_reviewed":False})
        matches=[]
        for i,t in enumerate(tasks):
            matches.append({
             "task_id":t["task_id"],
             "source_cue":t["source_cue"],
             "original_source_caption_interval_ms":t["source_caption_interval_ms"],
             "exact_source_text_preserved":t["original_dialogue"],
             "candidate_asr_segment_index":i,
             "candidate_similarity_score":.6,
             "ASR_segment_to_source_text_matching":"lexical_and_overlap_proposal_only",
             "multiple_original_typographic_turns_may_share_cue_interval":True,
             "source_word_fidelity_independently_listened":False,
             "source_word_timings_verified":False,
             "speaking_character_verified":False
            })
        cls.sample={
          "schema":"night-court-s01e01-full-source-review-asr-proposals/1",
          "episode_id":"S01E01",
          "original_video_sha256":"5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962",
          "original_english_srt_sha256":"aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496",
          "source_video_sample_window_ms":[56912,93074],
          "decoded_original_audio_duration_ms":36162,
          "decoded_audio_wav_sha256":"a"*64,
          "model":"faster-whisper tiny.en",
          "faster_whisper_version":"1.2.1",
          "model_result_count":12,"asr_segments":segs,
          "original_source_caption_turns":11,
          "turn_to_asr_overlap_proposals":matches,
          "human_listened_to_complete_source_window":False,
          "original_caption_words_independently_verified":False,
          "original_subtitle_sync_and_video_edition_verified":False,
          "speaker_character_diarization_verified":False,
          "vocal_inflection_or_emotion_verified":False,
          "production_scene_certified":False,
          "original_video_or_audio_or_weights_in_artifact":False
        }

    def test_source_shape_and_no_accepted_words(self):
        d=copy.deepcopy(self.sample)
        result=validate(d)
        self.assertEqual(result["candidate_segments"],12)
        self.assertEqual(result["candidate_words"],60)
        self.assertTrue(result["one_model_segment_overlap_with_clipped_next_C28"])
        self.assertFalse(result["production_screenplay_accepted"])

    def test_wrong_video_source_or_fake_speaker_rejected(self):
        d=copy.deepcopy(self.sample);d["original_video_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"exact original source"):validate(d)
        d=copy.deepcopy(self.sample);d["asr_segments"][0]["speaker_identity"]="Harry"
        with self.assertRaisesRegex(ValueError,"proposition structure"):validate(d)
        d=copy.deepcopy(self.sample);d["original_caption_words_independently_verified"]=True
        with self.assertRaisesRegex(ValueError,"cannot certify"):validate(d)

    def test_omitted_unmatched_c28_model_proposal_rejected(self):
        d=copy.deepcopy(self.sample);d["asr_segments"].pop()
        with self.assertRaisesRegex(ValueError,"Missing original audio model"):validate(d)
        d=copy.deepcopy(self.sample);d["asr_segments"][-1]["end_ms"]=93100
        with self.assertRaisesRegex(ValueError,"proposition structure"):validate(d)

    def test_changed_original_caption_wording_rejected(self):
        d=copy.deepcopy(self.sample);d["turn_to_asr_overlap_proposals"][0]["exact_source_text_preserved"]="synthetic alteration"
        with self.assertRaisesRegex(ValueError,"Original caption text"):validate(d)

if __name__=="__main__":
    unittest.main()
