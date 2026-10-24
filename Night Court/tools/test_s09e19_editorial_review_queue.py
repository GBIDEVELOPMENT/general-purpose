#!/usr/bin/env python3
import copy,json,unittest
from build_s09e19_editorial_review_queue import build,SCENE,FRAMES,OUT

class S09EditorQueue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q=build()

    def test_two_sources_one_honest_unaccepted_review_queue(self):
        d=self.q
        self.assertEqual(d["individual_review_tasks"],11)
        self.assertEqual(d["source_asr_candidate_count"],5)
        self.assertEqual(d["sampled_video_event_count"],6)
        self.assertEqual(d["original_paragraph_count"],347)
        self.assertEqual(d["original_source_paragraphs_with_actual_timecodes"],0)
        self.assertEqual(d["independently_accepted_dialogue_matches"],0)
        self.assertEqual(d["independently_accepted_physical_actions"],0)
        self.assertTrue(all(t.get("source_paragraph_timestamp_ms") is None
                            for t in d["tasks"] if t["kind"]=="proposed_dialogue_match"))
        self.assertEqual(self.q,json.loads(OUT.read_text("utf-8")))

    def test_fake_original_timestamp_or_verified_voice_rejected(self):
        scene=json.loads(SCENE.read_text("utf-8"))
        first=next(t for t in scene["events"] if t["source_kind"]=="original_untimed_source_paragraph_candidate")
        first["original_source_paragraph_has_no_timecodes"]=False
        with self.assertRaisesRegex(ValueError,"timed, or falsely accepted"):
            build(scene=scene)
        first["original_source_paragraph_has_no_timecodes"]=True
        first["candidate_speaking_character"]="unverified person"
        with self.assertRaisesRegex(ValueError,"timed, or falsely accepted"):
            build(scene=scene)

    def test_wrong_frame_SHA_is_rejected(self):
        scene=json.loads(SCENE.read_text("utf-8"))
        visual=next(t for t in scene["events"] if t["source_kind"]=="sampled_original_video_observation")
        visual["frame_evidence"][0]["sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"frame SHA/time mismatch"):
            build(scene=scene)

    def test_source_text_changed_is_not_silently_accepted(self):
        scene=json.loads(SCENE.read_text("utf-8"))
        voice=next(t for t in scene["events"] if t["source_kind"]=="original_untimed_source_paragraph_candidate")
        voice["original_source_text"]="plausible but invented text"
        with self.assertRaisesRegex(ValueError,"modified, timed, or falsely accepted"):
            build(scene=scene)

if __name__=="__main__":
    unittest.main()
