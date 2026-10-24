#!/usr/bin/env python3
import copy,unittest
from probe_s01e01_full_review_asr import compare_turns,original_packet,START_MS,END_MS,norm

class FullOriginalSceneASR(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet,cls.manifest=original_packet()

    def test_full_original_source_turns_inside_36_second_sample(self):
        self.assertEqual((START_MS,END_MS),(56912,93074))
        self.assertEqual(len(self.packet["voice_review_tasks"]),11)
        self.assertTrue(all(START_MS<=t["source_caption_interval_ms"][0]
                           and t["source_caption_interval_ms"][1]<=END_MS
                           for t in self.packet["voice_review_tasks"]))

    def test_matching_never_accepts_voice_or_original_audio(self):
        segments=[{"index":0,"start_ms":58900,"end_ms":62000,"text":'Did you say mercurial?'},
                  {"index":1,"start_ms":88900,"end_ms":91000,"text":'Tell the judge the mayor called.'}]
        rows=compare_turns(self.packet,segments)
        self.assertEqual(len(rows),11)
        c19=next(x for x in rows if x["task_id"]=="S01E01:C00019.1")
        c27=next(x for x in rows if x["task_id"]=="S01E01:C00027.1")
        self.assertEqual(c19["candidate_asr_segment_index"],0)
        self.assertEqual(c27["candidate_asr_segment_index"],1)
        self.assertTrue(c19["multiple_original_typographic_turns_may_share_cue_interval"])
        self.assertTrue(all(not x["source_word_fidelity_independently_listened"] for x in rows))
        self.assertTrue(all(not x["speaking_character_verified"] for x in rows))

    def test_empty_source_model_must_abstain_not_reinvent_dialogue(self):
        rows=compare_turns(self.packet,[])
        self.assertTrue(all(x["candidate_asr_segment_index"] is None for x in rows))
        self.assertTrue(all(x["exact_source_text_preserved"] for x in rows))
        self.assertEqual(norm("Mini-mifidian?!"),"mini mifidian")

    def test_changed_out_of_window_cue_is_rejected(self):
        packet=copy.deepcopy(self.packet)
        packet["voice_review_tasks"][0]["source_caption_interval_ms"]=[0,5000]
        with self.assertRaisesRegex(ValueError,"not fully covered"):
            compare_turns(packet,[])

if __name__=="__main__":
    unittest.main()
