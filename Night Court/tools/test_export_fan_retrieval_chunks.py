#!/usr/bin/env python3
"""Offline synthetic regression tests for fan retrieval seed export."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from export_fan_retrieval_chunks import (
    PILOT_SCRIPTS, chunk_section, export, partition_sections, sha256,
)


def fixture(root: Path, bad_source_sha: bool = False) -> dict:
    episodes = []
    for episode, title, is_timed in (
        ("S01E01", "All You Need Is Love", True),
        ("S09E19", "P.S. Do I Know You?", False),
        ("S02E01", "The Next Episode", True),
    ):
        sha = str({"S01E01": "a", "S09E19": "b", "S02E01": "c"}[episode]) * 64
        path = (
            PILOT_SCRIPTS[episode] if episode in PILOT_SCRIPTS
            else f"seasons/{episode[:3]}/{episode}/derived/source-script-scaffold-v1.md"
        )
        document = (
            f"# {episode} · {title}\n\nOriginal source SHA: {sha}\n\n"
            "### First reading scene or caption gap\n\n"
            "UNIDENTIFIED SPEAKER\nA deliberately short first remark.\n\n"
            "UNIDENTIFIED SPEAKER\nAnother line from a source witness.\n\n"
            "### Second candidate scene\n\n"
            "UNIDENTIFIED SPEAKER\nEnd of episode sample.\n"
        )
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document, "utf-8")
        episodes.append({
            "episode_id": episode, "title": title,
            "source_metadata": {
                "source_sha256": "f" * 64 if bad_source_sha and episode == "S01E01" else sha,
                "source_only_script": f"seasons/{episode[:3]}/{episode}/derived/source-script-scaffold-v1.md",
                "timed": is_timed,
            }
        })
    queue = {"original_episode_records": 3, "episodes": episodes}
    catalog = root / "catalog"
    catalog.mkdir(parents=True)
    (catalog / "av-script-reconstruction-queue.json").write_text(json.dumps(queue), "utf-8")
    return queue


class RetrievalExportTests(unittest.TestCase):
    def test_section_round_trip(self):
        raw = "preamble\n\n### Scene 1\nLine A\n\n### Scene 2\nLine B"
        self.assertEqual("".join(partition_sections(raw)), raw)

    def test_chunk_long_turn_not_truncated(self):
        raw = "### The source\n\n" + "Long untorn cue " * 100 + "\n\nNext line."
        chunks = chunk_section(raw, 220)
        self.assertEqual("".join(chunks), raw)
        self.assertTrue(any(len(c) > 220 for c in chunks))

    def test_small_limit_rejected(self):
        with self.assertRaises(ValueError):
            chunk_section("hello", 199)

    def test_pilot_and_full_export(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "Night Court"
            fixture(root)
            output = Path(folder) / "private-output"
            selected = export(root, output, pilot_only=True, max_chars=220)
            self.assertEqual(selected["episode_count"], 2)
            rows = [json.loads(x) for x in (output / "fan-retrieval-chunks.jsonl").read_text().splitlines()]
            self.assertEqual({r["episode_id"] for r in rows}, {"S01E01", "S09E19"})
            self.assertTrue(all(r["evidence_tier"] == "provisional_filmed_staging_working_script" for r in rows))
            self.assertTrue(all(not r["speaker_names_verified"] for r in rows))
            self.assertTrue(all(not r["section_is_verified_visual_scene"] for r in rows))
            self.assertFalse(next(r for r in rows if r["episode_id"] == "S09E19")["dialogue_timed_original"])
            for episode in ("S01E01", "S09E19"):
                original = (root / PILOT_SCRIPTS[episode]).read_text("utf-8")
                restored = "".join(r["retrieval_text"] for r in rows if r["episode_id"] == episode)
                self.assertEqual(restored, original)
                self.assertEqual(sha256(original.encode()), next(
                    r for r in rows if r["episode_id"] == episode)["script_sha256"])
            all_episodes = export(root, output, max_chars=220)
            self.assertEqual(all_episodes["episode_count"], 3)
            self.assertTrue(any(r["evidence_tier"] == "source_only_dialogue_scaffold"
                for r in (json.loads(x) for x in
                (output / "fan-retrieval-chunks.jsonl").read_text().splitlines())))

    def test_current_factory_packages_replace_older_anonymous_fan_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "Night Court"
            queue = fixture(root)
            factory = root / "saved-private/script-factory-current"
            for ep in ("S01E01", "S02E01"):
                source = next(e["source_metadata"] for e in queue["episodes"]
                              if e["episode_id"] == ep)
                source["source_version_id"] = "fixture-original-v1"
                draft = factory / ep
                draft.mkdir(parents=True)
                document = (
                    f"# Night Court (1984) · {ep} · Current researched reader\n\n"
                    f"Original transcript SHA-256: `{source['source_sha256']}`\n"
                    "### HARRY STONE (source-context proposal, original AV unverified)\n"
                    "    Hello from the current factory.\n"
                )
                content = document.encode("utf-8")
                (draft / "screenplay.md").write_bytes(content)
                manifest = {
                    "schema": "night-court-one-click-script-factory/1",
                    "episode_id": ep,
                    "source_witness_sha256": source["source_sha256"],
                    "original_dialogue_sha256": source["source_sha256"],
                    "source_version_id": source["source_version_id"],
                    "source_has_timecodes": source["timed"],
                    "dialogue_source_changed": False,
                    "source_only_claims_never_promoted_to_av_truth": True,
                    "actual_av_verified": False,
                    "evidence_tier": "contextual_provisional_reading_draft",
                    "script_sha256": sha256(content),
                }
                (draft / "manifest.json").write_text(json.dumps(manifest), "utf-8")
            (root / "catalog/av-script-reconstruction-queue.json").write_text(
                json.dumps(queue), "utf-8")
            out = Path(folder) / "new-retrieval"
            result = export(root, out, factory_root=factory)
            self.assertEqual(result["episode_count"], 3)
            source_by_ep = {e["episode_id"]: e for e in result["episodes"]}
            self.assertEqual(source_by_ep["S01E01"]["evidence_tier"],
                             "contextual_provisional_reading_draft")
            self.assertEqual(source_by_ep["S02E01"]["evidence_tier"],
                             "contextual_provisional_reading_draft")
            self.assertEqual(source_by_ep["S09E19"]["evidence_tier"],
                             "provisional_filmed_staging_working_script")
            self.assertIn("script-factory-current/S02E01/screenplay.md",
                          source_by_ep["S02E01"]["script_path"])
            rows = [json.loads(x) for x in
                    (out / "fan-retrieval-chunks.jsonl").read_text().splitlines()]
            self.assertTrue(any("Hello from the current factory." in r["retrieval_text"]
                                for r in rows if r["episode_id"] == "S02E01"))
            self.assertTrue(all(not r["speaker_names_verified"]
                                and not r["whole_episode_av_certified"] for r in rows))
            self.assertFalse(next(r for r in rows if r["episode_id"] == "S09E19")[
                "dialogue_timed_original"])
            # Script bytes cannot be silently changed after the factory SHA.
            target = factory / "S02E01" / "screenplay.md"
            target.write_text(target.read_text("utf-8") + "tampered", "utf-8")
            with self.assertRaisesRegex(ValueError, "stale, tampered"):
                export(root, out, factory_root=factory)
            target.write_text(target.read_text("utf-8")[:-8], "utf-8")
            # Even matching script bytes cannot excuse a forged actor-AV claim.
            meta_path = factory / "S02E01" / "manifest.json"
            m = json.loads(meta_path.read_text("utf-8"))
            m["actual_av_verified"] = True
            meta_path.write_text(json.dumps(m), "utf-8")
            with self.assertRaisesRegex(ValueError, "stale, tampered"):
                export(root, out, factory_root=factory)

    def test_private_speaker_v6_scripts_can_replace_both_pilots_without_source_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "Night Court"
            fixture(root)
            private = Path(folder) / "generated-speakers-v6"
            proofs = {}
            for episode in ("S01E01", "S09E19"):
                text = (root / PILOT_SCRIPTS[episode]).read_text("utf-8")
                text += "\nPROVISIONAL SOURCE-ATTESTED SPEAKER CORRECTION\n"
                target = private / episode / "screenplay-external-speakers-v6.md"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, "utf-8")
                proofs[episode] = {
                    "sha256": sha256(text.encode()),
                    "generated_path": f"{episode}/screenplay-external-speakers-v6.md",
                }
            manifest = {
                "original_source_speaking_units": 751,
                "new_provisional_named_source_units": 490,
                "remaining_unidentified_source_units": 261,
                "original_audio_speaker_identities_verified_by_this_change": 0,
                "pilot_scripts": proofs,
            }
            (private / "speaker-improvement-manifest.json").write_text(json.dumps(manifest), "utf-8")
            result = export(root, Path(folder)/"retrieval", pilot_only=True, v6_root=private)
            self.assertEqual(result["episode_count"], 2)
            self.assertTrue(all(e["evidence_tier"] == "provisional_external_quote_speaker_reader_v6"
                                for e in result["episodes"]))
            self.assertTrue(all(e["script_path"].startswith("private-source-speaker-v6/")
                                for e in result["episodes"]))
            modified = private / "S09E19" / "screenplay-external-speakers-v6.md"
            modified.write_text(modified.read_text("utf-8") + "tamper", "utf-8")
            with self.assertRaisesRegex(ValueError, "SHA mismatch"):
                export(root, Path(folder)/"retrieval", pilot_only=True, v6_root=private)

    def test_current_private_screenplay_layout_round_trips_to_fan_retrieval(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/"Night Court"
            fixture(root)
            current=Path(folder)/"current-chronological-working-pilots"
            current.mkdir()
            proofs={}
            for episode in ("S01E01","S09E19"):
                original=(root/PILOT_SCRIPTS[episode]).read_text("utf-8")
                draft=current/f"{episode}-working-screenplay.md"
                draft.write_text(original,"utf-8")
                proofs[episode]=sha256(original.encode())
            report={
                "schema":"night-court-private-pilot-screenplay-layout/1",
                "source_unit_counts":{"original_source_units":751,
                                      "named_provisional":621,"unknown":130},
                "source_v15_reader_sha256":"a"*64,
                "new_independently_verified_actor_voices":0,
                "new_independently_verified_performed_turns":0,
                "scene_review_complete":False,
                "manuscript_sha256":proofs,
                "episodes":{
                    "S01E01":{"source_blocks":405,"source_units":404,
                              "original_caption_timed":True},
                    "S09E19":{"source_blocks":321,"source_units":347,
                              "original_caption_timed":False},
                },
            }
            manifest=current/"working-screenplay-layout-manifest.json"
            manifest.write_text(json.dumps(report),"utf-8")
            target=Path(folder)/"private-output"
            exported=export(root,target,pilot_only=True,working_pilot_root=current)
            self.assertEqual(exported["episode_count"],2)
            self.assertTrue(all(x["evidence_tier"]=="provisional_source_first_chronological_screenplay_layout"
                                for x in exported["episodes"]))
            self.assertTrue(all(x["script_path"].startswith("private-current-working-screenplays/")
                                for x in exported["episodes"]))
            records=[json.loads(x) for x in (target/"fan-retrieval-chunks.jsonl").read_text().splitlines()]
            for episode in ("S01E01","S09E19"):
                original=(current/f"{episode}-working-screenplay.md").read_text("utf-8")
                self.assertEqual("".join(x["retrieval_text"] for x in records
                                         if x["episode_id"]==episode),original)
            self.assertTrue(all(x["speaker_names_verified"] is False for x in records))
            self.assertTrue(all(x["whole_episode_av_certified"] is False for x in records))
            self.assertFalse(next(x for x in records if x["episode_id"]=="S09E19")["dialogue_timed_original"])
            draft=current/"S01E01-working-screenplay.md"
            draft.write_text(draft.read_text("utf-8")+"tampered","utf-8")
            with self.assertRaisesRegex(ValueError,"chronological pilot screenplay SHA mismatch"):
                export(root,target,pilot_only=True,working_pilot_root=current)
            draft.write_text((root/PILOT_SCRIPTS["S01E01"]).read_text("utf-8"),"utf-8")
            report["scene_review_complete"]=True
            manifest.write_text(json.dumps(report),"utf-8")
            with self.assertRaisesRegex(ValueError,"provenance failed"):
                export(root,target,pilot_only=True,working_pilot_root=current)

    def test_sha_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "Night Court"
            fixture(root, bad_source_sha=True)
            with self.assertRaisesRegex(ValueError, "expected original caption SHA"):
                export(root, Path(folder) / "private", pilot_only=True)

    def test_private_output_cannot_be_written_under_source_root(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "Night Court"
            fixture(root)
            with self.assertRaisesRegex(ValueError, "outside the Night Court source tree"):
                export(root, root / "generated", pilot_only=True)

    def test_cross_episode_template_preamble_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "Night Court"
            fixture(root)
            target = root / PILOT_SCRIPTS["S01E01"]
            target.write_text(target.read_text("utf-8").replace(
                "Original source SHA:", "The S09 original source SHA:"), "utf-8")
            with self.assertRaisesRegex(ValueError, "Wrong-season pilot prose"):
                export(root, Path(folder) / "private", pilot_only=True)

    def test_unknown_script_not_substituted_silently(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "Night Court"
            fixture(root)
            (root / PILOT_SCRIPTS["S01E01"]).unlink()
            with self.assertRaises(FileNotFoundError):
                export(root, Path(folder) / "private", pilot_only=True)


if __name__ == "__main__":
    unittest.main()
