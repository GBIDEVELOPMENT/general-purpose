#!/usr/bin/env python3
"""Reject invented original-untimed timecodes, cast identities and wrong media evidence."""
import copy
import unittest
from validate_s09e19_review_decisions import load_worklist,template,validate

class S09ReviewDecisions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p,cls.tasks=load_worklist()

    def blank(self):
        return template(self.p,self.tasks)

    def accepted(self,d,kind):
        row=next(t for t in d["decisions"] if t["kind"]==kind)
        row.update(status="accepted_by_reviewer",reviewer_identifier="synthetic-unit-test",
                   review_note="Synthetic source evidence acceptance fixture only",
                   reviewer_attested=True)
        return row

    def evidence(self,task,method):
        record=self.tasks[task["task_id"]]
        span=(record["model_proposed_video_time_interval_ms"] if task["kind"]=="proposed_dialogue_match"
              else record["sampled_video_interval_ms"])
        return {"method":method,"source_video_sha256":self.p["original_video_sha256"],
                "original_untimed_source_sha256":self.p["original_untimed_source_sha256"],
                "interval_ms":span[:]}

    def attest(self,d):
        d["record_status"]="source_review_attestations_present"

    def test_all_eleven_untimed_records_stay_pending(self):
        d=self.blank()
        report=validate(self.p,self.tasks,d)
        self.assertEqual(report["reviewed_claim_records"],11)
        self.assertEqual(report["reviewer_attested_acceptances"],0)
        self.assertTrue(report["source_original_paragraphs_still_untimed"])
        self.assertFalse(report["production_script_certified"])

    def test_only_listened_and_audited_paragraph_can_be_attested(self):
        d=self.blank();t=self.accepted(d,"proposed_dialogue_match");self.attest(d)
        with self.assertRaises(ValueError):validate(self.p,self.tasks,d)
        t["evidence"]=[self.evidence(t,"listened_original_audio"),
                       self.evidence(t,"audited_original_untimed_paragraph")]
        self.assertEqual(validate(self.p,self.tasks,d)["reviewer_attested_acceptances"],1)
        t["accepted_speaker_identity"]="some character"
        with self.assertRaisesRegex(ValueError,"No named speaker"):
            validate(self.p,self.tasks,d)
        t["evidence"]+=[self.evidence(t,"watched_continuous_original_video"),
                        self.evidence(t,"synchronized_mouth_voice_review")]
        self.assertEqual(validate(self.p,self.tasks,d)["reviewer_attested_acceptances"],1)
        t["accepted_vocal_delivery"]="loud dramatic emphasis"
        with self.assertRaisesRegex(ValueError,"Mixed soundtrack"):
            validate(self.p,self.tasks,d)
        t["evidence"].append(self.evidence(t,"reviewed_isolated_original_voice"))
        self.assertEqual(validate(self.p,self.tasks,d)["reviewer_attested_acceptances"],1)

    def test_visual_still_is_not_continuous_video(self):
        d=self.blank();t=self.accepted(d,"sampled_visual_stage_claim");self.attest(d)
        t["evidence"]=[self.evidence(t,"audited_original_untimed_paragraph")]
        with self.assertRaisesRegex(ValueError,"sampled frames"):validate(self.p,self.tasks,d)
        t["evidence"]=[self.evidence(t,"watched_continuous_original_video")]
        self.assertEqual(validate(self.p,self.tasks,d)["reviewer_attested_acceptances"],1)

    def test_unrelated_source_times_and_fake_media_rejected(self):
        d=self.blank();t=self.accepted(d,"proposed_dialogue_match");self.attest(d)
        t["evidence"]=[self.evidence(t,"listened_original_audio"),
                       self.evidence(t,"audited_original_untimed_paragraph")]
        t["evidence"][0]["interval_ms"]=[5000,6000]
        with self.assertRaisesRegex(ValueError,"partial or unrelated"):validate(self.p,self.tasks,d)
        t["evidence"][0]["interval_ms"]=t["evidence"][1]["interval_ms"][:]
        t["evidence"][0]["original_untimed_source_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"SHA"):validate(self.p,self.tasks,d)

    def test_no_new_source_paragraph_timecode_or_hidden_claim(self):
        d=self.blank()
        d["decisions"][0]["source_paragraph_timestamp_ms"]=900000
        with self.assertRaisesRegex(ValueError,"unknown or missing claim fields"):validate(self.p,self.tasks,d)
        d=self.blank();d["source_original_untimed_text_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"original source identity"):validate(self.p,self.tasks,d)
        d=self.blank();d["decisions"].pop()
        with self.assertRaisesRegex(ValueError,"Incomplete"):validate(self.p,self.tasks,d)

if __name__=="__main__":
    unittest.main()
