"""Regression tests for one-command source-exact private screenplay delivery."""
import json
import tempfile
import unittest
from pathlib import Path

from script_factory import (
    ROOT, PILOTS, construct, multi_voice_typography, run,
    source_index, source_role, source_rows, sha,
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
                self.assertEqual(data["evidence_tier"], "source_only_reading_draft")
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
