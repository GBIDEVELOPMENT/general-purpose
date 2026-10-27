"""Synthetic, no-source-media regressions for the single-pass episode finisher."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from episode_finish import make_packet, verify_decisions, verified_s09_candidate_locator, VIDEO_SHA, render_reviewed_screenplay


class OnePassEpisodeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source_sha = "b" * 64
        script = self.root / "S01E01-working-screenplay.md"
        script.write_text("# S01E01\nSource SHA " + self.source_sha + "\n", encoding="utf-8")
        def row(i, group, name, t):
            return {
                "reading_block_id": "S01E01:speaker-evidence:%04d" % i,
                "original_source_part_refs": ["C%03d.1" % i],
                "source_sha256": self.source_sha,
                "display_group_id": group,
                "candidate_role": name,
                "actual_original_av_reviewer_accepted": False,
                "exact_rendered_caption_sha256": ("%064d" % i),
                "source_cue_times_not_subturn_times_ms": t,
            }
        self.rows = [row(1, 1, "LANA", [1000, 2000]),
                     row(2, 1, "LANA", [2100, 3000]),
                     row(3, 2, None, [3300, 4900])]
        self.provenance = self.root / "S01E01-working-screenplay-provenance.jsonl"
        self.save_rows()
        reader = self.root / "pilot-current-editorial-reader.jsonl"
        self.caption_text = ["one", "two", "three"]
        for i, row in enumerate(self.rows):
            row["exact_rendered_caption_sha256"] = hashlib.sha256(
                self.caption_text[i].encode("utf-8")).hexdigest()
        self.save_rows()
        reader.write_text("".join(json.dumps({
            "episode_id": "S01E01", "reading_block_id": row["reading_block_id"],
            "caption_text": self.caption_text[i],
            "original_source_sha256": self.source_sha,
            "original_source_part_refs": row["original_source_part_refs"]
        }) + "\n" for i, row in enumerate(self.rows)), encoding="utf-8")
        self.manifest = {
            "manuscript_sha256": {
                "S01E01": hashlib.sha256(script.read_bytes()).hexdigest()},
            "episode_editorial_integrations": {"S01E01": "single-current"},
            "episodes": {"S01E01": {"source_units": 3, "source_blocks": 3,
                                    "display_groups": 2}},
        }
        self.save_manifest()

    def save_rows(self):
        self.provenance.write_text(
            "".join(json.dumps(x) + "\n" for x in self.rows), encoding="utf-8")

    def save_manifest(self):
        (self.root / "working-screenplay-layout-manifest.json").write_text(
            json.dumps(self.manifest), encoding="utf-8")

    def test_review_once_all_source_parts_boundaries_and_roles(self):
        p = make_packet(self.root, "S01E01")
        self.assertEqual(p["source_reader_blocks"], 3)
        self.assertEqual(p["sequential_one_pass_batches"][0]["reader_blocks"][0]["source_exact_dialogue"], "one")
        self.assertEqual(p["original_source_speaking_part_refs"], 3)
        self.assertEqual(len(p["all_adjacent_boundary_questions"]), 2)
        self.assertEqual(p["all_adjacent_boundary_questions"][0]["priority"],
                         "P0_UNVERIFIED_JOIN")
        self.assertEqual(p["all_adjacent_boundary_questions"][1]["priority"],
                         "P0_UNVERIFIED_BREAK")
        self.assertEqual(p["review_passes_required"], 1)
        self.assertEqual(p["sequential_one_pass_batches"][0]["source_window_candidate_ms"],
                         [0, 6100])
        self.assertFalse(p["script_final_or_full_episode_accepted"])

    def test_provenance_and_original_audio_claims_cannot_be_forged(self):
        self.rows[0]["actual_original_av_reviewer_accepted"] = True
        self.save_rows()
        with self.assertRaisesRegex(ValueError, "Unproven previous"):
            make_packet(self.root, "S01E01")
        self.rows[0]["actual_original_av_reviewer_accepted"] = False
        self.rows[0]["source_sha256"] = "0" * 64
        self.save_rows()
        with self.assertRaisesRegex(ValueError, "source witness"):
            make_packet(self.root, "S01E01")

    def test_canonical_drift_fails_closed(self):
        self.manifest["episodes"]["S01E01"]["source_blocks"] = 2
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "row count"):
            make_packet(self.root, "S01E01")

    def test_no_blanket_audio_acceptance(self):
        p = make_packet(self.root, "S01E01")
        d = {
            "packet_sha256": p["packet_sha256"],
            "episode_id": "S01E01",
            "original_video_sha256": p["original_video_sha256_expected"],
            "review_method": "continuous_original_synchronized_av",
            "reviewer": "Test fixture person",
            "boundaries": {},
            "roles": {},
            "batches": {},
        }
        with self.assertRaisesRegex(ValueError, "not fully reviewed"):
            verify_decisions(p, d)
        d["boundaries"] = {e["id"]: {"result": "same_speaker_continuation",
                                   "heard_on_original_audio": True}
                          for e in p["all_adjacent_boundary_questions"]}
        d["roles"] = {r["id"]: {"role": r["provisional_role"] or "UNIDENTIFIED VOICE",
                                  "original_audio_voice_reviewed": True}
                      for batch in p["sequential_one_pass_batches"]
                      for r in batch["reader_blocks"]}
        d["batches"] = {batch["id"]: {
            "synchronized_original_video_and_sound_reviewed": True,
            "performance_notes": [], "visible_props_and_wardrobe": [],
            "observed_actor_action_target": []}
                        for batch in p["sequential_one_pass_batches"]}
        self.assertTrue(verify_decisions(p, d)["editorial_decisions_complete"])
        d["boundaries"]["B0001"]["heard_on_original_audio"] = False
        with self.assertRaisesRegex(ValueError, "requires original sound"):
            verify_decisions(p, d)

    def test_source_exact_original_av_reviewed_script_render_after_all_decisions(self):
        p = make_packet(self.root, "S01E01")
        d = {
            "packet_sha256": p["packet_sha256"],
            "episode_id": "S01E01",
            "original_video_sha256": p["original_video_sha256_expected"],
            "review_method": "continuous_original_synchronized_av",
            "reviewer": "synthetic fixture",
            "boundaries": {
                "B0001": {"result": "same_speaker_continuation",
                           "heard_on_original_audio": True},
                "B0002": {"result": "new_speaker",
                           "heard_on_original_audio": True}
            },
            "roles": {row["id"]: {
                "role": row["provisional_role"] or "UNIDENTIFIED VOICE",
                "original_audio_voice_reviewed": True
            } for batch in p["sequential_one_pass_batches"]
              for row in batch["reader_blocks"]},
            "batches": {p["sequential_one_pass_batches"][0]["id"]: {
                "synchronized_original_video_and_sound_reviewed": True,
                "performance_notes": ["test delivery"], "visible_props_and_wardrobe": [],
                "observed_actor_action_target": ["test observed action"]
            }}
        }
        script = render_reviewed_screenplay(p, d)
        self.assertEqual(script.count("### LANA"), 1)
        self.assertEqual(script.count("### UNIDENTIFIED VOICE"), 1)
        self.assertLess(script.index("    one"), script.index("    two"))
        self.assertLess(script.index("    two"), script.index("    three"))
        self.assertIn(self.source_sha, script)
        self.assertIn("test observed action", script)
        d["boundaries"]["B0002"]["result"] = "same_speaker_continuation"
        with self.assertRaisesRegex(ValueError, "conflicting P1"):
            render_reviewed_screenplay(p, d)

    def test_s09_original_machine_locator_has_no_faked_subtitle_times(self):
        path = self.root / "s09-source-audio.json"
        rows = [{
            "original_paragraph_id": n,
            "candidate_original_audio_window_ms": [n * 1000, n * 1000 + 900],
            "original_paragraph_timecode_ms": None,
            "original_film_audio_timing_independently_verified": False,
            "spoken_character_identity_verified": False
        } for n in range(1, 232)]
        data = {
            "schema": "night-court-s09-original-film-untimed-paragraph-audio-locator/1",
            "episode_id": "S09E19",
            "original_video_sha256": VIDEO_SHA["S09E19"],
            "original_untimed_source_sha256":
                "659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2",
            "original_source_untimed_paragraph_count": 347,
            "original_soundtrack_processed": True,
            "original_speaker_identities_verified": 0,
            "candidate_source_paragraphs_given_audio_window": 231,
            "matches": rows
        }
        path.write_text(json.dumps(data), encoding="utf-8")
        hints, digest = verified_s09_candidate_locator(path)
        self.assertEqual(len(hints), 231)
        self.assertEqual(hints[12], [12000, 12900])
        self.assertEqual(len(digest), 64)
        data["matches"][2]["original_paragraph_timecode_ms"] = 3000
        path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Fake original S09 paragraph timing"):
            verified_s09_candidate_locator(path)



if __name__ == "__main__":
    unittest.main()
