#!/usr/bin/env python3
"""Synthetic FTS5 controls: source provenance, evidence separation, no overwrite."""
import json
import tempfile
import unittest
from pathlib import Path

from fan_sqlite_index import SCHEMA, build_database, query, validate_evidence, apply_speaker_improvements, use_source_checked_context_roles, apply_current_source_turn_reunion_v10
from build_pilot_character_evidence import SCHEMA as ROLE_SCHEMA
from build_pilot_fan_beat_cards import CARD_SCHEMA
from search_fan_retrieval_chunks import SCHEMA as SCRIPT_SCHEMA


def fixtures():
    episode = "S01E01"
    witness = "b" * 64
    source = [{
        "schema": SCRIPT_SCHEMA, "episode_id": episode,
        "record_id": episode + ":retrieval:0001",
        "episode_title": "All You Need Is Love",
        "section_label": "court", "retrieval_text": "Harry examines a double-headed coin.",
        "script_sha256": "a" * 64, "caption_source_sha256": witness,
        "evidence_tier": "provisional_filmed_staging_working_script",
        "speaker_names_verified": False, "whole_episode_av_certified": False
    }]
    cards = [{
        "schema": CARD_SCHEMA, "id": episode + ":beat:coin",
        "episode_id": episode, "episode_title": "All You Need Is Love",
        "title": "The double-headed coin",
        "setup": "The judge proposes a coin flip.",
        "payoff": "The trick is explained by the heads on both sides.",
        "interpretation": "A comically rigged judicial procedure.",
        "mechanisms": ["prop_gag", "callback"],
        "semantic_text": "Coin of justice and a trick with two heads.",
        "source_witness_sha256": witness,
        "source_anchor_evidence": [{"caption_cue": 1, "caption_source_sha256": witness}],
        "candidate_characters": ["Harry Stone"],
        "original_audio_speaker_identities_verified": False,
        "vocal_delivery_verified": False,
        "film_staging_verified": False,
        "editorial_interpretation_not_original_script_fact": True
    }]
    roles = [{
        "schema": ROLE_SCHEMA, "episode_id": episode,
        "reading_block_id": episode + ":speaker-evidence:0001",
        "source_reading_ref": "C001.1",
        "original_source_part_refs": ["C001.1"],
        "original_source_sha256": witness,
        "speaker_turn_boundary_verified": False,
        "actor_face_or_voice_independently_verified": False,
        "candidate_role": "HARRY STONE",
        "role_attribution_status": "provisional_not_original_audio_verified",
        "caption_text": "Harry has the coin."
    }]
    return source, cards, roles


class SqliteFanCorpusTests(unittest.TestCase):
    def test_full_private_build_and_three_kinds(self):
        src, cards, roles = fixtures()
        with tempfile.TemporaryDirectory() as temp:
            paths = [Path(temp) / x for x in ("source.jsonl", "cards.jsonl", "roles.jsonl")]
            for rows, path in zip((src, cards, roles), paths):
                path.write_text("".join(json.dumps(item) + "\n" for item in rows), "utf-8")
            db = Path(temp) / "search.sqlite"
            summary = build_database(db, *paths, require_full=False)
            self.assertEqual(summary["source_episodes"], 1)
            self.assertEqual(summary["indexed_documents"], 3)
            results = query(db, "Harry coin")
            self.assertEqual(results["schema"], SCHEMA)
            self.assertEqual([len(results["results_by_evidence_kind"][k]) for k in (
                "script_witness", "provisional_character_dialogue", "editorial_comedy_and_story"
            )], [1, 1, 1])
            results = query(db, "Harry coin", episode="S01E01", role="WRONG")
            self.assertFalse(results["results_by_evidence_kind"]["provisional_character_dialogue"])
            self.assertTrue(results["results_by_evidence_kind"]["script_witness"])
            with self.assertRaises(FileExistsError):
                build_database(db, *paths, require_full=False)

    def test_v6_override_replaces_unknown_without_double_indexing(self):
        from hashlib import sha256
        src, cards, roles = fixtures()
        original = "Your Honor, this is highly irregular."
        role = roles[0]
        role["candidate_role"] = None
        role["role_attribution_status"] = "unidentified"
        role["source_reading_ref"] = "C001.1"
        role["caption_text"] = original
        new_label = "DAN FIELDING · EXTERNALLY QUOTE-ATTRIBUTED; AUDIO UNVERIFIED"
        src[0]["retrieval_text"] += "\n" + new_label + "\n" + original
        revision = {
            "schema": "night-court-original-pilot-external-attribution-application/1",
            "episode_id": "S01E01", "source_ref": "C001.1",
            "source_witness_sha256": "b" * 64,
            "source_cue_sha256": sha256(original.encode()).hexdigest(),
            "start_char": 0, "end_char": len(original),
            "text": original, "candidate_role": "DAN FIELDING",
            "reader_label": new_label,
            "original_soundtrack_verified": False,
            "character_identity_status": "external_or_context_editorial_proposal",
            "external_episode_quote_url": "https://example.test/quotes"
        }
        mapped = apply_speaker_improvements(src, roles, [revision], require_full=False)
        self.assertEqual(len(mapped), len(roles))
        self.assertEqual(mapped[0]["candidate_role"], "DAN FIELDING")
        self.assertEqual(mapped[0]["role_attribution_status"], "external_or_context_editorial_proposal")
        self.assertFalse(mapped[0]["speaker_turn_boundary_verified"])
        changed = dict(revision, text="invented text")
        with self.assertRaisesRegex(ValueError, "alter or omit source words"):
            apply_speaker_improvements(src, roles, [changed], require_full=False)
        with tempfile.TemporaryDirectory() as folder:
            paths = [Path(folder)/n for n in ("source.jsonl","cards.jsonl","roles.jsonl")]
            for rows, path in zip((src,cards,roles),paths):
                path.write_text("".join(json.dumps(x)+"\n" for x in rows), "utf-8")
            overrides = Path(folder)/"overrides.jsonl"
            overrides.write_text(json.dumps(revision)+"\n","utf-8")
            db=Path(folder)/"source-fts.sqlite"
            report=build_database(db,*paths,require_full=False,speaker_override_path=overrides)
            self.assertEqual(report["post_speaker_improvement_blocks"],1)
            result=query(db,"irregular",role="DAN FIELDING")
            self.assertEqual(len(result["results_by_evidence_kind"]["provisional_character_dialogue"]),1)
            self.assertEqual(result["results_by_evidence_kind"]["provisional_character_dialogue"][0]["evidence"]["candidate_role"],"DAN FIELDING")

    def test_private_v7_name_replaces_unknown_only_with_matching_source_text(self):
        import hashlib
        src, cards, roles = fixtures()
        roles[0]["candidate_role"] = None
        roles[0]["role_attribution_status"] = "unidentified"
        revised = dict(roles[0])
        revised.update({
            "candidate_role": "HARRY STONE",
            "role_attribution_status": "narrative_context_candidate_not_voice_verified",
            "actor_face_or_voice_independently_verified": False,
            "original_audio_reviewed": False,
        })
        src[0]["retrieval_text"] += (
            "\nHARRY STONE · narrative_context_candidate_not_voice_verified\n"
            + revised["caption_text"]
        )
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "v7.jsonl"
            raw = json.dumps(revised) + "\n"
            path.write_text(raw, "utf-8")
            (path.parent / "pilot-contextual-speaker-manifest.json").write_text(
                json.dumps({"reading_record_sha256": hashlib.sha256(raw.encode()).hexdigest()}),
                "utf-8"
            )
            newer, report = use_source_checked_context_roles(src, roles, path, full=False)
            self.assertEqual(report["v7_provisionally_named_original_units"],1)
            self.assertEqual(newer[0]["candidate_role"],"HARRY STONE")
            original=path.read_text()
            path.write_text(original+" ", "utf-8")
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                use_source_checked_context_roles(src, roles, path, full=False)
            path.write_text(original, "utf-8")
            tampered=dict(revised, caption_text="Fabricated source words")
            tampered_raw=json.dumps(tampered)+"\n"
            path.write_text(tampered_raw, "utf-8")
            (path.parent / "pilot-contextual-speaker-manifest.json").write_text(
                json.dumps({"reading_record_sha256":hashlib.sha256(tampered_raw.encode()).hexdigest()}),
                "utf-8"
            )
            with self.assertRaisesRegex(ValueError,"altered an original spoken text"):
                use_source_checked_context_roles(src, roles, path, full=False)

    def test_v10_joins_exact_two_source_parts_into_one_fts_speaking_turn(self):
        import hashlib
        from build_s09_source_turns_v10 import merge_v9,EXPECTED_FIRST,EXPECTED_SECOND,SHA
        old=[
            {"episode_id":"S09E19","source_reading_ref":"C266.1",
             "original_source_part_refs":["C266.1"],"reading_block_id":"s09:266",
             "original_source_sha256":SHA,
             "caption_text":EXPECTED_FIRST,"candidate_role":None,
             "role_attribution_status":"unidentified",
             "source_original_times_ms":None,"original_source_untimed":True,
             "speaker_turn_boundary_verified":False,
             "actor_face_or_voice_independently_verified":False},
            {"episode_id":"S09E19","source_reading_ref":"C267.1",
             "original_source_part_refs":["C267.1"],"reading_block_id":"s09:267",
             "original_source_sha256":SHA,
             "caption_text":EXPECTED_SECOND,"candidate_role":"ROZ RUSSELL",
             "role_attribution_status":"original_soundtrack_acoustic_context_proposal_not_independent_avi_id",
             "source_original_times_ms":None,"original_source_untimed":True,
             "speaker_turn_boundary_verified":False,
             "actor_face_or_voice_independently_verified":False,
             "speaker_identity_provisional_from_model_and_context":True}
        ]
        new,manifest=merge_v9(old,strict=False)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"source-v10.jsonl"
            data="".join(json.dumps(x,sort_keys=True)+"\n" for x in new)
            path.write_text(data,"utf-8")
            (path.parent/"pilot-current-source-turns-v10-manifest.json").write_text(
                json.dumps({"current_source_role_records_sha256":
                            hashlib.sha256(data.encode()).hexdigest()}),"utf-8")
            speaker=new[0]
            script=[{"episode_id":"S09E19",
                     "retrieval_text":speaker["candidate_role"]+" · "+
                         speaker["role_attribution_status"]+"\n"+speaker["caption_text"]}]
            merged,out=apply_current_source_turn_reunion_v10(script,old,path,full=False)
            self.assertEqual(len(merged),1)
            self.assertEqual(out["v10_named_original_caption_source_units"],2)
            self.assertEqual(out["v10_independent_avi_voice_turns_accepted"],0)
            self.assertEqual(merged[0]["original_source_part_refs"],["C266.1","C267.1"])
            script[0]["retrieval_text"]="Unsupported replacement words"
            with self.assertRaisesRegex(ValueError,"missing from actual indexed script"):
                apply_current_source_turn_reunion_v10(script,old,path,full=False)
            script[0]["retrieval_text"]=speaker["candidate_role"]+" · "+speaker["role_attribution_status"]+"\n"+speaker["caption_text"]
            new[0]["caption_text"]="Fabricated source speech"
            bad="".join(json.dumps(x,sort_keys=True)+"\n" for x in new)
            path.write_text(bad,"utf-8")
            (path.parent/"pilot-current-source-turns-v10-manifest.json").write_text(
                json.dumps({"current_source_role_records_sha256":
                             hashlib.sha256(bad.encode()).hexdigest()}),"utf-8")
            with self.assertRaisesRegex(ValueError,"Incorrectly verified/merged"):
                apply_current_source_turn_reunion_v10(script,old,path,full=False)

    def test_no_false_verified_role_or_mixed_episode(self):
        src, cards, roles = fixtures()
        roles[0]["actor_face_or_voice_independently_verified"] = True
        with self.assertRaises(ValueError):
            validate_evidence(src, cards, roles, require_full=False)
        roles[0]["actor_face_or_voice_independently_verified"] = False
        roles[0]["original_source_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            validate_evidence(src, cards, roles, require_full=False)

    def test_untrusted_episode_and_empty_query(self):
        with tempfile.TemporaryDirectory() as temp:
            src, cards, roles = fixtures()
            paths = [Path(temp) / x for x in ("source.jsonl", "cards.jsonl", "roles.jsonl")]
            for rows, path in zip((src, cards, roles), paths):
                path.write_text("".join(json.dumps(item) + "\n" for item in rows), "utf-8")
            db = Path(temp) / "search.sqlite"
            build_database(db, *paths, require_full=False)
            with self.assertRaises(ValueError):
                query(db, "the episode night court")
            with self.assertRaises(ValueError):
                query(db, "Harry", episode="DROP TABLE episodes")


if __name__ == "__main__":
    unittest.main()
