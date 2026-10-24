#!/usr/bin/env python3
"""Reject voiceprints, fake speaker certainty and missing pairwise data."""
import copy,json,tempfile,unittest
from pathlib import Path
from import_s01e01_anonymous_voice_similarity import validate,AVI,SRT,SOURCE

class AnonymousImportTests(unittest.TestCase):
    def fixture(self):
        src=json.loads(SOURCE.read_text("utf-8"))
        xs=[]
        for i,s in enumerate(src["asr_segments"]):
            eligible=i in (0,1)
            xs.append({
                "asr_segment_index":i,
                "source_interval_ms":[s["start_ms"],s["end_ms"]],
                "source_voice_identity":None,
                "embedding_retained":False,
                "speaker_isolation_verified":False,
                "status":"anonymous_embedding_computed_not_speech_or_speaker_verified" if eligible else "abstain_near_silence"
            })
        return {
            "schema":"night-court-s01e01-anonymous-voice-similarity/1",
            "episode_id":"S01E01",
            "source_media_sha256":AVI,
            "source_caption_sha256":SRT,
            "source_audio_window_ms":[60000,90000],
            "candidate_ASR_speech_segments":10,
            "model":"speechbrain/spkrec-ecapa-voxceleb",
            "model_revision_sha":"a"*40,
            "raw_voice_embeddings_retained":False,
            "speaker_clusters_assigned":False,
            "speaker_identities_assigned":False,
            "same_speaker_pairs_verified":False,
            "voice_biometrics_or_source_media_in_artifact":False,
            "emotion_and_delivery_inferred":False,
            "source_voice_intervals":xs,
            "anonymous_pairs":[{"asr_segment_a":0,"asr_segment_b":1,
                  "anonymous_cosine_similarity_unreviewed":.534,
                  "same_speaker_conclusion":None,
                  "model_probability_calibrated":False}]
        }
    def check(self,doc):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"fixture.json"
            path.write_text(json.dumps(doc))
            return validate(path)
    def test_synthetic_valid_metadata_has_no_named_voice(self):
        j,eligible=self.check(self.fixture())
        self.assertEqual(eligible,[0,1])
        self.assertIsNone(j["anonymous_pairs"][0]["same_speaker_conclusion"])
    def test_source_hash_or_voiceprint_leak_rejected(self):
        for alteration in (
          lambda x:x.update(source_caption_sha256="0"*64),
          lambda x:x.update(raw_voice_embeddings_retained=True),
          lambda x:x.update(embeddings=[[1,2,3]]),
          lambda x:x["source_voice_intervals"][0].update(source_voice_identity="Bull"),
          lambda x:x["anonymous_pairs"][0].update(same_speaker_conclusion=True),
          lambda x:x["anonymous_pairs"][0].update(anonymous_cosine_similarity_unreviewed=1.2),
          lambda x:x.update(anonymous_pairs=[]),
        ):
            x=self.fixture();alteration(x)
            with self.subTest(alteration=alteration):
                with self.assertRaises(ValueError):self.check(x)

if __name__=="__main__":unittest.main()
