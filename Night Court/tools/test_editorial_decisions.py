#!/usr/bin/env python3
"""Refuse ungrounded scene, speaker or delivery claims with synthetic decisions."""
import copy,unittest
from validate_editorial_decisions import load_packet,template,validate

class ReviewEvidenceGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet,cls.tasks=load_packet()
    def blank(self):
        return template(self.packet,self.tasks)
    def evidence(self,method):
        return {"method":method,
                "source_video_sha256":self.packet["source_video_sha256"],
                "interval_ms":[82500,84500]}
    def edit(self,data,kind):
        x=next(x for x in data["decisions"] if x["task_type"]==kind)
        x.update(status="accepted_by_reviewer",reviewer_identifier="sample-reviewer",
                 reviewer_attested=True,review_note="Synthetic unit test, not an actual review")
        return x
    def test_blank_17_gate_is_clean(self):
        p=self.blank()
        self.assertEqual(len(p["decisions"]),17)
        r=validate(self.packet,self.tasks,p)
        self.assertEqual(r["reviewer_attested_claims"],0)
        self.assertFalse(r["independent_av_verification_conducted_by_this_validator"])
    def test_voice_requires_original_audio_and_source_cue_reading(self):
        data=self.blank();task=self.edit(data,"voice")
        with self.assertRaises(ValueError):validate(self.packet,self.tasks,data)
        task["evidence"]=[self.evidence("listened_original_audio"),
                          self.evidence("audited_source_caption")]
        self.assertEqual(validate(self.packet,self.tasks,data)["reviewer_attested_claims"],1)
        task["accepted_speaker_identity"]="unverified-role"
        with self.assertRaises(ValueError):validate(self.packet,self.tasks,data)
        task["evidence"] += [self.evidence("watched_continuous_original_video"),
                             self.evidence("synchronized_mouth_voice_review")]
        self.assertEqual(validate(self.packet,self.tasks,data)["reviewer_attested_claims"],1)
        task["accepted_vocal_delivery"]="overconfident-anger-label"
        with self.assertRaises(ValueError):validate(self.packet,self.tasks,data)
        task["evidence"].append(self.evidence("reviewed_isolated_voice"))
        self.assertEqual(validate(self.packet,self.tasks,data)["reviewer_attested_claims"],1)
    def test_visual_stills_cannot_certify_action(self):
        d=self.blank();t=self.edit(d,"visual")
        t["evidence"]=[self.evidence("audited_source_caption")]
        with self.assertRaises(ValueError):validate(self.packet,self.tasks,d)
        t["evidence"]=[self.evidence("watched_continuous_original_video")]
        self.assertEqual(validate(self.packet,self.tasks,d)["reviewer_attested_claims"],1)
        t["accepted_speaker_identity"]="anyone"
        with self.assertRaises(ValueError):validate(self.packet,self.tasks,d)
    def test_source_and_record_tampering_rejected(self):
        d=self.blank()
        d["source_caption_sha256"]="0"*64
        with self.assertRaises(ValueError):validate(self.packet,self.tasks,d)
        d=self.blank();d["decisions"].pop()
        with self.assertRaises(ValueError):validate(self.packet,self.tasks,d)
        d=self.blank();d["decisions"][0]["accepted_speaker_identity"]="arbitrary"
        with self.assertRaises(ValueError):validate(self.packet,self.tasks,d)
        d=self.blank();t=self.edit(d,"voice")
        t["evidence"]=[{"method":"listened_original_audio",
                       "source_video_sha256":"0"*64,
                       "interval_ms":[0,4000]},self.evidence("audited_source_caption")]
        with self.assertRaises(ValueError):validate(self.packet,self.tasks,d)

if __name__=="__main__":unittest.main()
