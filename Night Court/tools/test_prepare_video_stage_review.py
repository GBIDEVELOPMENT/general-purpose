#!/usr/bin/env python3
"""Source-free reviewers-template tests. Generated model prose remains untrusted."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare_video_stage_review import prepare, render_packet, review_priority_hints, escape_untrusted_markdown
from review_video_stage_directions import adjudicate
from run_headless_video_description import FIELDS

SHA = "a"*64


def model():
    data = {k: "" for k in FIELDS}
    data["setting"] = "An office with a desk."
    data["proposed_stage_direction"] = "A person moves toward a desk."
    return {
        "schema": "night-court-headless-video-description/1",
        "episode_id": "S01E01", "source_video_sha256": SHA,
        "verified_source_sha256": SHA,
        "duration_ms": 1448256,
        "script_or_claim_independently_accepted": False,
        "windows": [{
            "id": "S01E01-AV-01",
            "start_ms": 75000, "end_ms": 76500,
            "selection_reason": "editorial_action",
            "candidate_cut_crossing": False,
            "status": "machine_proposed",
            "model_hypothesis": data,
            "independently_accepted": False,
            "source_AV_human_review_done": False,
        }],
    }


def digest(m):
    return hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()


class ReviewPacketTests(unittest.TestCase):
    def test_all_ten_questions_are_deferred_without_claim_promotions(self):
        m = model()
        sha = digest(m)
        output, windows = prepare(m, sha, "original-film-editor")
        self.assertEqual(len(output["decisions"]), len(FIELDS))
        self.assertTrue(all(x["verdict"] == "deferred" for x in output["decisions"]))
        self.assertTrue(all(x["direct_original_video_review_attested"] is False for x in output["decisions"]))
        self.assertEqual(output["source_video_sha256"], SHA)
        self.assertFalse(output["_original_full_episode_independently_certified"])
        self.assertEqual(output["model_report_sha256"], sha)
        validated = adjudicate(m, output, sha)
        self.assertEqual(validated["editorial_stage_directions"], [])
        self.assertEqual(validated["decision_counts"]["deferred"], 10)
        self.assertEqual(validated["unreviewed_field_count"], 0)

    def test_malformed_model_output_still_becomes_explicit_review_problem(self):
        m = model()
        m["windows"][0]["status"] = "requires_review"
        m["windows"][0]["model_hypothesis"] = None
        m["windows"][0]["model_response_excerpt"] = "<script>alert('x')</script>"
        output, windows = prepare(m, digest(m))
        report = render_packet(m, windows, output)
        self.assertIn("&lt;script&gt;", report)
        self.assertNotIn("<script>", report)
        self.assertIn("invalid or incomplete", report)
        self.assertNotIn("accepted stage direction", json.dumps(output).lower())

    def test_model_speculation_propagates_only_as_review_priority_not_acceptance(self):
        self.assertIn("motive_or_unverified_audio",
                      review_priority_hints("proposed_stage_direction",
                          "The scene may be a confrontation while he listens intently."))
        self.assertIn("speculative_wording",
                      review_priority_hints("proposed_stage_direction",
                          "The scene may be a confrontation while he listens intently."))
        self.assertIn("never_copy_model_stage_prose_without_source_review",
                      review_priority_hints("proposed_stage_direction", "He raises his hand."))
        self.assertIn("inspect_fine_prop_identity",
                      review_priority_hints("props", "Possibly a red pocket square and a glass of water."))
        self.assertIn("absence_requires_full_clip_review",
                      review_priority_hints("physical_comedy", "None."))
        self.assertEqual(review_priority_hints("camera", ""), ["missing_model_observation"])
        self.assertEqual(review_priority_hints("camera", "The camera is steady."),
                         ["normal_original_video_check"])
        with self.assertRaises(ValueError):
            review_priority_hints("arbitrary", "Some guessed action")

    def test_malicious_markdown_prose_cannot_embed_active_image_link(self):
        raw = "![download this](https://bad.invalid/frame?secret=123)<script>alert(1)</script>"
        escaped = escape_untrusted_markdown(raw)
        self.assertNotIn("![", escaped)
        self.assertNotIn("<script>", escaped)
        self.assertIn(r"\!\[", escaped)
        m = model()
        m["windows"][0]["model_hypothesis"]["props"] = raw
        out,windows = prepare(m,digest(m))
        packet = render_packet(m,windows,out)
        self.assertNotIn("![download this]", packet)
        self.assertNotIn("<script>", packet)
        self.assertIn("Review priorities (heuristic, not verdicts)", packet)
        self.assertTrue(all(d["verdict"] == "deferred" for d in out["decisions"]))

    def test_no_automatic_source_acceptance_or_actor_identity(self):
        m = model()
        m["script_or_claim_independently_accepted"] = True
        with self.assertRaisesRegex(ValueError, "cannot certify"):
            prepare(m, digest(m))
        m = model()
        m["verified_source_sha256"] = "b"*64
        with self.assertRaisesRegex(ValueError, "SHA not verified"):
            prepare(m, digest(m))

    def test_cross_cut_and_repeated_window_rejected(self):
        m = model()
        m["windows"][0]["candidate_cut_crossing"] = True
        with self.assertRaisesRegex(ValueError, "Cross-cut"):
            prepare(m, digest(m))
        m = model()
        m["windows"].append(copy.deepcopy(m["windows"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate model window"):
            prepare(m, digest(m))

    def test_any_missing_or_forged_reviewer_metadata_rejected(self):
        m = model()
        with self.assertRaises(ValueError):
            prepare(m, digest(m), "not a valid reviewer id")
        with self.assertRaises(ValueError):
            prepare(m, "invalid-model-sha")
        m["source_video_sha256"] = "not-sha"
        with self.assertRaises(ValueError):
            prepare(m, digest(m))

    def test_cli_roundtrip_to_review_bridge_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root)
            m = model()
            raw = (json.dumps(m,sort_keys=True)+"\n").encode()
            src = p / "model.json"
            src.write_bytes(raw)
            out = p / "pending.json"
            preview = p / "preview.md"
            script = Path(__file__).with_name("prepare_video_stage_review.py")
            args = [sys.executable,str(script),"--model-report",str(src),
                    "--decisions",str(out),"--review-packet",str(preview),
                    "--reviewer-id","editor-trial"]
            subprocess.run(args,check=True,capture_output=True,text=True)
            data = json.loads(out.read_text())
            self.assertEqual(data["model_report_sha256"],hashlib.sha256(raw).hexdigest())
            self.assertEqual(len(data["decisions"]),10)
            self.assertIn("editorial_action",preview.read_text())
            self.assertEqual(src.read_bytes(),raw)
            attempt = subprocess.run(args,capture_output=True,text=True)
            self.assertNotEqual(attempt.returncode,0)
            self.assertIn("overwrite",attempt.stderr)


if __name__ == "__main__":
    unittest.main()
