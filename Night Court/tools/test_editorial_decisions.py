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
    def evidence(self,method,decision):
        _,task=self.tasks[decision["task_id"]]
        field=("source_caption_interval_ms" if decision["task_type"]=="voice"
               else "source_interval_ms")
        return {"method":method,
                "source_video_sha256":self.packet["source_video_sha256"],
                "interval_ms":task[field][:]}
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
        task["evidence"]=[self.evidence("listened_original_audio",task),
                          self.evidence("audited_source_caption",task)]
        self.assertEqual(validate(self.packet,self.tasks,data)["reviewer_attested_claims"],1)
        task["accepted_speaker_identity"]="unverified-role"
        with self.assertRaises(ValueError):validate(self.packet,self.tasks,data)
        task["evidence"] += [self.evidence("watched_continuous_original_video",task),
                             self.evidence("synchronized_mouth_voice_review",task)]
        self.assertEqual(validate(self.packet,self.tasks,data)["reviewer_attested_claims"],1)
        task["accepted_vocal_delivery"]="overconfident-anger-label"
        with self.assertRaises(ValueError):validate(self.packet,self.tasks,data)
        task["evidence"].append(self.evidence("reviewed_isolated_voice",task))
        self.assertEqual(validate(self.packet,self.tasks,data)["reviewer_attested_claims"],1)
    def test_visual_stills_cannot_certify_action(self):
        d=self.blank();t=self.edit(d,"visual")
        t["evidence"]=[self.evidence("audited_source_caption",t)]
        with self.assertRaises(ValueError):validate(self.packet,self.tasks,d)
        t["evidence"]=[self.evidence("watched_continuous_original_video",t)]
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
                       "interval_ms":[0,4000]},self.evidence("audited_source_caption",t)]
        with self.assertRaises(ValueError):validate(self.packet,self.tasks,d)

    def test_accepted_review_rejects_unrelated_source_time_windows(self):
        for kind in ("voice","visual"):
            with self.subTest(kind=kind):
                d=self.blank(); t=self.edit(d,kind)
                methods=(["listened_original_audio","audited_source_caption"]
                         if kind=="voice" else ["watched_continuous_original_video"])
                t["evidence"]=[self.evidence(method,t) for method in methods]
                self.assertEqual(validate(self.packet,self.tasks,d)["reviewer_attested_claims"],1)
                # Same valid original AVI SHA, but a clip nowhere near this task.
                t["evidence"][0]["interval_ms"]=[0,1000]
                with self.assertRaisesRegex(ValueError,"does not cover its source task"):
                    validate(self.packet,self.tasks,d)

    def test_partial_source_window_cannot_accept_complete_claim(self):
        for kind in ("voice","visual"):
            with self.subTest(kind=kind):
                d=self.blank(); t=self.edit(d,kind)
                methods=(["listened_original_audio","audited_source_caption"]
                         if kind=="voice" else ["watched_continuous_original_video"])
                t["evidence"]=[self.evidence(method,t) for method in methods]
                start,end=t["evidence"][0]["interval_ms"]
                t["evidence"][0]["interval_ms"]=[start+1,end]
                with self.assertRaisesRegex(ValueError,"does not cover its source task"):
                    validate(self.packet,self.tasks,d)
                t["evidence"][0]["interval_ms"]=[start,end-1]
                with self.assertRaisesRegex(ValueError,"does not cover its source task"):
                    validate(self.packet,self.tasks,d)

    def test_boolean_evidence_timestamp_is_not_an_integer(self):
        d=self.blank();t=self.edit(d,"voice")
        t["evidence"]=[self.evidence("listened_original_audio",t),
                       self.evidence("audited_source_caption",t)]
        t["evidence"][0]["interval_ms"][0]=True
        with self.assertRaisesRegex(ValueError,"outside original episode duration"):
            validate(self.packet,self.tasks,d)

if __name__=="__main__":unittest.main()
