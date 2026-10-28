"""Regression tests for one-command source-exact private screenplay delivery."""
import json
import tempfile
import unittest
from pathlib import Path

from script_factory import (
    ROOT, PILOTS, construct, multi_voice_typography, run,
    source_index, source_role, source_rows, sha, contextual_role_overlay, structural_speaker_parts,
)


class ScriptFactoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = source_index(ROOT)

    def test_explicit_speaker_only_never_converts_addressee_to_voice(self):
        self.assertEqual(source_role("HARRY: Hello, Dan"), "HARRY")
        self.assertEqual(source_role("<v Roz>Hey, Harry"), "Roz")
        self.assertIsNone(source_role("Hey, Harry, come over here"))
        self.assertIsNone(source_role("MUSIC: trumpet riff"))
        self.assertTrue(multi_voice_typography("- Hello\n- What's new?"))
        self.assertFalse(multi_voice_typography("- Hello\nAre you there?"))

    def test_multi_dash_voice_segments_preserve_exact_source_unicode(self):
        samples = [
            ("- Hello, Dan.\n- Hello, Harry.", 2),
            ("- First speaker\nwraps onto another line\n– Second speaker", 2),
            ("A previous voice speaks.\n- A second voice\n- A third voice", 3),
            ("- Only one leading dash; continuation is unmarked", 1),
            ("An ordinary hyphen - in a sentence", 1),
            ("— Bonjour, café.\n— Voilà, niño.", 2),
            ("- Hello\n- There\n- Friend", 3),
        ]
        for raw, expected in samples:
            with self.subTest(source=raw):
                parts = structural_speaker_parts(raw)
                self.assertEqual(len(parts), expected)
                self.assertEqual("".join(p["text"] for p in parts), raw)
                self.assertEqual(parts[0]["start"], 0)
                self.assertEqual(parts[-1]["end"], len(raw))
                self.assertEqual([p["start"] for p in parts[1:]],
                                 [p["end"] for p in parts[:-1]])
                self.assertTrue(all(sha(p["text"].encode("utf-8")) ==
                                    p["source_text_sha256"] for p in parts))
                self.assertTrue(all(not p["actual_speaker_boundary_verified"] for p in parts))

    def test_pilots_reuse_source_checked_canonical_manuscripts(self):
        for ep in PILOTS:
            with self.subTest(ep=ep):
                files, data = construct(ROOT, ep, self.index[ep])
                raw = (ROOT / "saved-private/pilot-current" /
                       (ep + "-working-screenplay.md")).read_bytes()
                self.assertEqual(sha(files["screenplay.md"].encode()), sha(raw))
                self.assertEqual(data["evidence_tier"], "canonical_provisional_editorial_script")
                self.assertFalse(data["actual_av_verified"])
                self.assertFalse(data["independent_editorial_acceptance"])
                rows = [json.loads(x) for x in files["provenance.jsonl"].splitlines()]
                self.assertEqual(len(rows), data["provisional_reader_blocks"])
                self.assertEqual(len(json.loads(files["review-queue.json"])["boundary_review_questions"]),
                                 len(rows) - 1)
                self.assertTrue(all(sha(x["source_text"].encode()) == x["source_text_sha256"]
                                    for x in rows))

    def test_generic_maintains_all_actual_original_cues_and_never_invents_time(self):
        for ep in ("S05E05", "S09E18"):
            with self.subTest(ep=ep):
                manifest, _, cues = source_rows(ROOT, self.index[ep])
                files, data = construct(ROOT, ep, self.index[ep])
                self.assertEqual(data["evidence_tier"],
                                 "contextual_provisional_reading_draft" if ep == "S05E05"
                                 else "source_only_reading_draft")
                self.assertEqual(data["source_units"], manifest["cue_count"])
                rows = [json.loads(x) for x in files["provenance.jsonl"].splitlines()]
                self.assertEqual([x["source_text"] for x in rows], [x["text"] for x in cues])
                self.assertEqual([x["source_start_ms"] for x in rows],
                                 [x["start_ms"] for x in cues])
                self.assertEqual([x["source_end_ms"] for x in rows],
                                 [x["end_ms"] for x in cues])
                self.assertTrue(all(x["original_dialogue_sha256"] == manifest["sha256"]
                                    for x in rows))
                self.assertFalse(data["actual_av_verified"])

    def test_s05_contextual_review_is_used_without_fake_audio_witness(self):
        ep = "S05E05"
        files, data = construct(ROOT, ep, self.index[ep])
        overlay = data["contextual_overlay"]
        self.assertEqual(overlay["high_medium_single_role_hypotheses"], 259)
        self.assertEqual(overlay["mixed_voice_internal_review_cues"], 7)
        self.assertEqual(overlay["weak_or_abstained_cues"], 34)
        self.assertFalse(overlay["original_audio_verified"])
        self.assertEqual(data["unknown_label_cues"], 41)
        rows = [json.loads(x) for x in files["provenance.jsonl"].splitlines()]
        self.assertEqual(rows[34]["candidate_display_role"], "Dan Fielding")
        self.assertTrue(rows[34]["provisional_continuation_of_previous"])
        self.assertIsNone(rows[35]["candidate_display_role"])
        self.assertEqual(rows[35]["contextual_intra_cue_voice_roles"],
                         ["Dan Fielding", "Harry Stone"])
        self.assertIsNone(rows[148]["candidate_display_role"])  # LOW confidence abstains
        self.assertTrue(all(not r["candidate_role_original_soundtrack_verified"] for r in rows))
        review = json.loads(files["review-queue.json"])
        self.assertEqual(len(review["contextual_role_review"]), 300)
        self.assertIn(36, review["review_internal_voice_changes"])
        self.assertIn("contextual hypothesis, unverified", files["screenplay.md"])
        self.assertIn("MULTIPLE UNIDENTIFIED VOICES", files["screenplay.md"])
        witness, _, captions = source_rows(ROOT, self.index[ep])
        with self.assertRaisesRegex(ValueError, "stale/malformed contextual role"):
            contextual_role_overlay(ROOT, ep, {**witness, "sha256": "0" * 64}, captions)

    def test_all_193_episodes_generate_and_second_run_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d)
            first = run(ROOT, output, "all")
            self.assertEqual(len(first), 193)
            self.assertEqual(sum(x["changed_files"] for x in first), 193 * 4)
            again = run(ROOT, output, "all")
            self.assertTrue(all(x["changed_files"] == 0 for x in again))
            for ep in self.index:
                with self.subTest(ep=ep):
                    folder = output / ep
                    manifest = json.loads((folder / "manifest.json").read_text("utf-8"))
                    script = (folder / "screenplay.md").read_bytes()
                    provenance = (folder / "provenance.jsonl").read_bytes()
                    queue = (folder / "review-queue.json").read_bytes()
                    self.assertEqual(manifest["script_sha256"], sha(script))
                    self.assertEqual(manifest["source_provenance_sha256"], sha(provenance))
                    self.assertEqual(manifest["p0_review_queue_sha256"], sha(queue))
                    self.assertTrue(manifest["source_only_claims_never_promoted_to_av_truth"])
                    if ep not in PILOTS:
                        rows = [json.loads(s) for s in provenance.decode("utf-8").splitlines()]
                        cut_count = 0
                        for row in rows:
                            parts = row["source_speaker_parts"]
                            self.assertGreaterEqual(len(parts), 1)
                            self.assertEqual(parts[0]["source_character_start"], 0)
                            self.assertEqual(parts[-1]["source_character_end"], len(row["source_text"]))
                            self.assertEqual(
                                "".join(row["source_text"][p["source_character_start"]:
                                                            p["source_character_end"]] for p in parts),
                                row["source_text"])
                            for p in parts:
                                self.assertIsNone(p["original_audio_subcue_time_ms"])
                                self.assertFalse(p["original_audio_boundary_verified"])
                                self.assertEqual(sha(row["source_text"][
                                    p["source_character_start"]:p["source_character_end"]
                                ].encode("utf-8")), p["source_text_sha256"])
                            cut_count += len(parts) - 1
                        self.assertEqual(manifest["source_dash_candidate_p0_boundaries"], cut_count)
                        review = json.loads(queue)
                        self.assertEqual(len(review["within_cue_structural_turn_questions"]), cut_count)
                        self.assertTrue(all(not q["source_audio_performed_turn_verified"]
                                            for q in review["within_cue_structural_turn_questions"]))

    def test_cannot_silently_mutate_original_transcript(self):
        import shutil
        ep = "S05E05"
        index = self.index[ep]
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            folder = ROOT / "seasons/S05/S05E05"
            dest = root / "seasons/S05/S05E05"
            source_manifest = ROOT / index["manifest"]
            new_manifest = root / index["manifest"]
            new_manifest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_manifest, new_manifest)
            manifest = json.loads(source_manifest.read_text("utf-8"))
            for part in ("episode.json", manifest["original_path"], manifest["segments_path"]):
                src = folder / part
                target = dest / part
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, target)
            original = dest / manifest["original_path"]
            original.write_bytes(original.read_bytes() + b"\nsource damage")
            with self.assertRaisesRegex(ValueError, "immutable original transcript"):
                source_rows(root, index)


if __name__ == "__main__":
    unittest.main()
