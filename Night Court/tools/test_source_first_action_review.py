#!/usr/bin/env python3
"""No-video tests for human-only source-bound action evidence."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_first_action_review import template,summarize,load,SCHEMA
from test_prepare_video_stage_review import model,digest


def reviewed():
    m=model()
    m["windows"][0]["shot_partition_verified"] = False
    record=template(m,digest(m))
    record["reviewer_id"]="film-editor"
    return m,record


class SourceActionEvidenceTests(unittest.TestCase):
    def test_initial_all_unknown_not_accepting_model_hypothesis(self):
        m,r=reviewed()
        out=summarize(m,digest(m),r,"b"*64)
        self.assertEqual(r["schema"],SCHEMA)
        self.assertEqual(out["action_status_counts"]["pending"],1)
        self.assertFalse(out["source_action_review_complete"])
        self.assertEqual(out["directed_actions_reviewed"],0)
        self.assertEqual(out["stage_directions_automatically_accepted"],0)
        self.assertNotIn("A person moves toward",json.dumps(out))
        self.assertTrue(all(r["actions"][0][k] is None for k in
             ("initiator","action_verb","recipient_or_object","visible_evidence")))

    def test_source_edition_or_report_or_window_swap_fails(self):
        m,r=reviewed()
        for field,wrong in (("episode_id","S09E19"),
             ("source_video_sha256","c"*64),("source_model_report_sha256","f"*64),
             ("source_window_ms",[75001,76500])):
            with self.subTest(field=field):
                bad=copy.deepcopy(r)
                bad[field]=wrong
                with self.assertRaisesRegex(ValueError,"mismatch"):
                    summarize(m,digest(m),bad,"b"*64)

    def test_unviewed_movie_cannot_claim_observed_or_complete(self):
        m,r=reviewed()
        r["source_action_review_complete"]=True
        with self.assertRaisesRegex(ValueError,"without source moving video"):
            summarize(m,digest(m),r,"b"*64)
        r["source_action_review_complete"]=False
        r["actions"][0]["status"]="observed"
        with self.assertRaisesRegex(ValueError,"Unviewed original film"):
            summarize(m,digest(m),r,"b"*64)

    def test_completed_original_review_must_be_explicit_and_directional(self):
        m,r=reviewed()
        r.update(original_continuous_video_viewed=True,
                 original_synchronized_sound_reviewed=True,
                 source_action_review_complete=True)
        with self.assertRaisesRegex(ValueError,"pending"):
            summarize(m,digest(m),r,"b"*64)
        row=r["actions"][0]
        row.update(status="observed",initiator="person_1",action_verb="touches",
             recipient_or_object="person_2 cheek",
             visible_evidence="Observed direct original movie window in motion",
             reviewer_confidence="medium")
        score=summarize(m,digest(m),r,"b"*64)
        self.assertEqual(score["directed_actions_reviewed"],1)
        self.assertFalse(score["complete_original_episode_certified"])
        self.assertNotIn("cheek",json.dumps(score))
        row["recipient_or_object"]=None
        with self.assertRaisesRegex(ValueError,"actor/verb/recipient"):
            summarize(m,digest(m),r,"b"*64)

    def test_unresolved_actor_cannot_beguile_into_evidence(self):
        m,r=reviewed()
        r["original_continuous_video_viewed"]=True
        row=r["actions"][0]
        row.update(status="uncertain",initiator="person_1",visible_evidence="Ambiguous hand",reviewer_confidence="low")
        with self.assertRaisesRegex(ValueError,"cannot assert"):
            summarize(m,digest(m),r,"b"*64)
        row["initiator"]=None
        score=summarize(m,digest(m),r,"b"*64)
        self.assertEqual(score["action_status_counts"]["uncertain"],1)
        self.assertFalse(score["source_action_review_complete"])

    def test_cli_source_safe_roundtrip_and_refuse_overwrite(self):
        m,r=reviewed()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            pm=root/"untrusted.json"
            pm.write_text(json.dumps(m,sort_keys=True))
            form=root/"private-form.json"
            out=root/"safe.json"
            script=Path(__file__).with_name("source_first_action_review.py")
            cmd=[sys.executable,str(script),"--model-report",str(pm),
                 "--new-private-form",str(form)]
            subprocess.run(cmd,check=True,capture_output=True,text=True)
            completed=json.loads(form.read_text())
            self.assertEqual(completed["source_model_report_sha256"],hashlib.sha256(pm.read_bytes()).hexdigest())
            cmd=[sys.executable,str(script),"--model-report",str(pm),
                 "--private-review",str(form),"--safe-summary",str(out)]
            subprocess.run(cmd,check=True,capture_output=True,text=True)
            self.assertEqual(json.loads(out.read_text())["directed_actions_reviewed"],0)
            again=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(again.returncode,0)
            self.assertIn("overwrite",again.stderr)


if __name__=="__main__":
    unittest.main()
