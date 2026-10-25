#!/usr/bin/env python3
"""Source-free acceptance tests for bounded local video semantics and original SHA gates."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_headless_video_description import (
    SCHEMA, benchmark, normalize, parse_hypothesis, sha_file, ffprobe_info,
)


class FakeModel:
    def __init__(self):
        self.calls = []

    def describe(self, path):
        self.calls.append({"size": path.stat().st_size, "suffix": path.suffix})
        return json.dumps({
            "setting": "A staged room.", "camera": "Static shot.",
            "people_and_positions": "person_1 at left.",
            "actions": "person_1 raises an object.", "props": "An object.",
            "entrances_exits": "", "physical_comedy": "", "reactions": "",
            "uncertainty": "Object shape uncertain.",
            "proposed_stage_direction": "A figure raises an object.",
        })


def manifest(sha="a" * 64, duration=6000):
    return {
        "schema": "night-court-video-benchmark-windows/1",
        "episode_id": "S01E01",
        "source_video_sha256": sha,
        "caption_source_sha256": "b" * 64,
        "duration_ms": duration,
        "windows": [
            {"id": "shot-A", "start_ms": 500, "end_ms": 2200,
             "selection_reason": "editorial", "candidate_cut_crossing": False},
            {"id": "control-2", "start_ms": 3500, "end_ms": 5000,
             "selection_reason": "low_motion_control", "candidate_cut_crossing": False},
        ],
    }


class ManifestTests(unittest.TestCase):
    def test_normalized_plan_is_only_unreviewed(self):
        result = benchmark(normalize(manifest()), "plan")
        self.assertEqual(result["schema"], SCHEMA)
        self.assertEqual(len(result["windows"]), 2)
        self.assertFalse(result["script_or_claim_independently_accepted"])
        self.assertEqual(result["windows"][0]["status"], "awaiting_source_model_pass")

    def test_existing_project_packet_input(self):
        packet = {
            "schema": "night-court-multigoal-original-AV-review/1",
            "episode_id": "S09E19", "original_video_sha256": "c" * 64,
            "original_duration_ms": 1320144,
            "script_or_claim_independently_accepted": False,
            "requests": [{
                "id": "S09E19-AV-01", "source_window_ms": [1000, 2000],
                "selection_reason": "low_pixel_change_control",
                "candidate_shot_partition_not_verified": True,
                "independently_accepted": False,
                "original_continuous_AV_review_done": False,
            }],
        }
        m = normalize(packet)
        self.assertEqual(m["episode_id"], "S09E19")
        self.assertIsNone(m["caption_source_sha256"])
        self.assertEqual(m["windows"][0]["start_ms"], 1000)

    def test_bad_source_and_status_rejected(self):
        bad = manifest()
        bad["source_video_sha256"] = "../private/episode.avi"
        with self.assertRaises(ValueError):
            normalize(bad)
        bad = manifest()
        bad["windows"][0]["candidate_cut_crossing"] = True
        with self.assertRaises(ValueError):
            normalize(bad)
        bad = manifest()
        bad["windows"][0]["end_ms"] = 45000
        with self.assertRaises(ValueError):
            normalize(bad)
        bad = manifest()
        bad["windows"][0]["id"] = "../unsafe"
        with self.assertRaises(ValueError):
            normalize(bad)
        bad = manifest()
        bad["windows"][1]["id"] = "shot-A"
        with self.assertRaises(ValueError):
            normalize(bad)

    def test_packet_claimed_accepted_rejected(self):
        packet = {
            "schema": "night-court-multigoal-original-AV-review/1",
            "episode_id": "S01E01", "original_video_sha256": "a" * 64,
            "original_duration_ms": 1448256,
            "script_or_claim_independently_accepted": True,
            "requests": [],
        }
        with self.assertRaises(ValueError):
            normalize(packet)

    def test_model_text_requires_exact_safe_json_fields(self):
        obj = {k: "" for k in (
            "setting", "camera", "people_and_positions", "actions", "props",
            "entrances_exits", "physical_comedy", "reactions",
            "uncertainty", "proposed_stage_direction"
        )}
        data, err = parse_hypothesis(json.dumps(obj))
        self.assertIsNone(err)
        self.assertEqual(data, obj)
        self.assertEqual(parse_hypothesis("not json")[1], "non_json_model_output")
        self.assertEqual(parse_hypothesis('{"setting":"office"}')[1], "bad_model_fields")
        self.assertEqual(parse_hypothesis('{"setting":' )[1], "non_json_model_output")


@unittest.skipUnless(subprocess.run(["bash", "-lc", "command -v ffmpeg && command -v ffprobe"],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0,
                     "ffmpeg/ffprobe unavailable")
class SyntheticRealDecodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="nc-synthetic-benchmark-")
        cls.media = Path(cls.tmp.name) / "silent-test-pattern.mp4"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
            "-i", "testsrc2=size=160x120:rate=12:duration=6",
            "-c:v", "mpeg4", "-q:v", "10", "-pix_fmt", "yuv420p", "-y", str(cls.media)
        ], check=True, timeout=45)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_real_ffmpeg_source_and_transient_clip(self):
        self.assertAlmostEqual(ffprobe_info(self.media)["duration_ms"], 6000, delta=100)
        source_sha = sha_file(self.media)
        fake = FakeModel()
        result = benchmark(normalize(manifest(source_sha)), "smolvlm2",
                           media=self.media, revision="0" * 40, model=fake)
        self.assertEqual(result["verified_source_sha256"], source_sha)
        self.assertEqual(len(fake.calls), 2)
        self.assertEqual(len(result["windows"]), 2)
        self.assertTrue(all(item["size"] > 0 for item in fake.calls))
        self.assertTrue(all(item["model_hypothesis"]["actions"] for item in result["windows"]))
        self.assertTrue(all(item["status"] == "machine_proposed" for item in result["windows"]))
        self.assertFalse(result["script_or_claim_independently_accepted"])
        self.assertFalse(result["windows"][0]["independently_accepted"])
        self.assertNotIn(str(self.media), json.dumps(result))
        self.assertLess(result["wall_seconds"], 45)

    def test_wrong_original_sha_fails_closed_before_model(self):
        fake = FakeModel()
        with self.assertRaisesRegex(ValueError, "SOURCE SHA256 MISMATCH"):
            benchmark(normalize(manifest()), "smolvlm2", media=self.media,
                      revision="0" * 40, model=fake)
        self.assertEqual(fake.calls, [])

    def test_duration_forgery_fails_closed(self):
        fake = FakeModel()
        with self.assertRaisesRegex(ValueError, "duration mismatch"):
            benchmark(normalize(manifest(sha_file(self.media), 12000)),
                      "smolvlm2", media=self.media, revision="0" * 40, model=fake)
        self.assertEqual(fake.calls, [])


if __name__ == "__main__":
    unittest.main()
# One-shot synthetic actual model load trigger; do not merge into main.
