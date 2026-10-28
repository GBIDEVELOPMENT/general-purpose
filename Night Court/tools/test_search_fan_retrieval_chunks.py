#!/usr/bin/env python3
"""Deterministic, offline search acceptance tests on invented source text."""
import json
import hashlib
import tempfile
import unittest
from pathlib import Path
from search_fan_retrieval_chunks import (
    SCHEMA, SEARCH_SCHEMA, load_records, score_records, search, words,
)


def records():
    examples = (
        ("S01E01", "All You Need Is Love", "the office", "A painter watches through the office window."),
        ("S01E01", "All You Need Is Love", "the office", "Lana asks a painter why he stops painting."),
        ("S01E01", "All You Need Is Love", "another source moment", "Bull invents enormous vocabulary words."),
        ("S09E19", "P.S. Do I Know You?", "pen pal", "Roz writes to her pen pal Alex and explains the letters."),
        ("S09E19", "P.S. Do I Know You?", "campaign", "Dan complains while Christine arranges a political advertisement."),
    )
    out = []
    for ep, title, heading, text in examples:
        number = 1 + sum(r["episode_id"] == ep for r in out)
        out.append({
            "schema": SCHEMA,
            "episode_id": ep,
            "episode_title": title,
            "section_label": heading,
            "record_id": f"{ep}:retrieval:{number:04d}",
            "script_sha256": ep + "-sample",
            "caption_source_sha256": ep + "-witness",
            "evidence_tier": "source_only_dialogue_scaffold",
            "speaker_names_verified": False,
            "whole_episode_av_certified": False,
            "retrieval_text": text,
        })
    return out


class FanSearchTests(unittest.TestCase):
    def test_relevant_episode_ranks_first(self):
        result = search(records(), "Roz pen pal Alex", limit=3)
        self.assertEqual(result["schema"], SEARCH_SCHEMA)
        self.assertEqual(result["hits"][0]["episode_id"], "S09E19")
        self.assertEqual(result["hits"][0]["match_id"], "S09E19:retrieval:0001")
        self.assertFalse(result["hits"][0]["speaker_names_verified"])

    def test_neighbor_context_is_same_episode(self):
        result = search(records(), "Bull vocabulary", limit=1, neighbors=3)
        hit = result["hits"][0]
        self.assertEqual(hit["episode_id"], "S01E01")
        self.assertEqual({c["record_id"] for c in hit["adjacent_source_context"]},
                         {"S01E01:retrieval:0001", "S01E01:retrieval:0002"})

    def test_episode_filter_not_ignored(self):
        result = search(records(), "Roz Alex", episode="S01E01")
        self.assertFalse(result["hits"])
        with self.assertRaises(ValueError):
            search(records(), "Roz", episode="night court pilot")

    def test_stop_words_not_query(self):
        self.assertEqual(words("What did the character say in Night Court?"), [])
        with self.assertRaisesRegex(ValueError, "no significant words"):
            search(records(), "What did the character say in Night Court?")

    def test_result_limits(self):
        with self.assertRaises(ValueError):
            search(records(), "painter", limit=0)
        with self.assertRaises(ValueError):
            search(records(), "painter", neighbors=7)

    def test_schema_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "private.jsonl"
            rows = records()
            path.write_text("".join(json.dumps(r) + "\n" for r in rows), "utf-8")
            self.assertEqual(len(load_records(path)), len(rows))
            rows.append(dict(rows[0]))
            path.write_text("".join(json.dumps(r) + "\n" for r in rows), "utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicated record IDs"):
                load_records(path)
            rows[-1] = dict(rows[-1], schema="incorrect-schema")
            path.write_text("".join(json.dumps(r) + "\n" for r in rows), "utf-8")
            with self.assertRaisesRegex(ValueError, "Unexpected retrieval schema"):
                load_records(path)

    def test_source_av_reviewed_reader_supersedes_only_its_episode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"saved-private"
            baseline=root/"pilot-current"
            fan=baseline/"private-fan-retrieval"
            fan.mkdir(parents=True)
            review=root/"episode-finish-current"
            review.mkdir()
            original=records()
            for row in original:
                if row["episode_id"]=="S01E01":
                    row["caption_source_sha256"]="a"*64
            corpus=fan/"fan-retrieval-chunks.jsonl"
            corpus.write_text("".join(json.dumps(r)+"\\n" for r in original),encoding="utf-8")
            ledger=review/"S01E01-original-av-decisions.json"
            ledger.write_text('{"original_AV_viewed":true}\\n',encoding="utf-8")
            # A partial reviewer ledger is NOT a published final screenplay.
            self.assertEqual(len(load_records(corpus)),len(original))
            prior=baseline/"S01E01-working-screenplay.md"
            prior.write_text("# Pilot manuscript\\n"+"a"*64+"\\n")
            sha=lambda text:hashlib.sha256(text).hexdigest()
            (baseline/"working-screenplay-layout-manifest.json").write_text(
                json.dumps({"manuscript_sha256":{"S01E01":sha(prior.read_bytes())}}))
            final=review/"S01E01-original-av-reviewed-screenplay.md"
            final.write_text("# S01E01: source-AV reviewed screenplay\\n\\n"+
                             "Original immutable dialogue SHA-256: "+"a"*64+
                             "\\n\\n### LANA\\n\\n    sampled prop seen during source audio and film.\\n")
            manifest=review/"S01E01-original-av-reviewed-manifest.json"
            data={
              "schema":"night-court-original-av-stable-reviewed-screenplay-publication/1",
              "episode_id":"S01E01",
              "original_film_sha256":"5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962",
              "immutable_original_dialogue_sha256":"a"*64,
              "reviewed_manuscript_sha256":sha(final.read_bytes()),
              "actual_editorial_ledger_sha256":sha(ledger.read_bytes()),
              "canonical_input_manuscript_sha256":sha(prior.read_bytes()),
              "caption_witness_remains_immutable":True,
              "software_does_not_prove_human_attention":True,
              "evidence_tier":"original_av_reviewer_attested_pending_independent_editor"
            }
            manifest.write_text(json.dumps(data))
            active=load_records(corpus)
            self.assertTrue(any("sampled prop" in rec["retrieval_text"]
                                for rec in active if rec["episode_id"]=="S01E01"))
            self.assertFalse(any("painter watches" in rec["retrieval_text"]
                                 for rec in active if rec["episode_id"]=="S01E01"))
            self.assertEqual([x["retrieval_text"] for x in active if x["episode_id"]=="S09E19"],
                             [x["retrieval_text"] for x in original if x["episode_id"]=="S09E19"])
            reviewed=[rec for rec in active if rec["episode_id"]=="S01E01"]
            self.assertTrue(all(not rec["speaker_names_verified"] and
                                not rec["whole_episode_av_certified"] for rec in reviewed))
            self.assertEqual(search(active,"sampled prop",episode="S01E01")["hits"][0]["episode_id"],
                             "S01E01")
            data["reviewed_manuscript_sha256"]="f"*64
            manifest.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"provenance mismatch"):
                load_records(corpus)

    def test_deterministic_scores(self):
        a = score_records(records(), "painter painting")
        b = score_records(records(), "painter painting")
        self.assertEqual(a, b)
        self.assertGreater(a[0][0], 0)


if __name__ == "__main__":
    unittest.main()
