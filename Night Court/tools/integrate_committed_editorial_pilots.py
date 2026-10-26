#!/usr/bin/env python3
"""Integrate committed, SHA-bound episode-editor work into PRIVATE current pilots.

Keep immutable v16 intact. Fail closed unless every existing reading block,
source character and role change matches the episode editors' durable evidence.
No original soundtrack or performed turn is independently authenticated here.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from build_pilot_fan_beat_cards import ROOT
from apply_manual_context_pilot_review_v16 import counts
from render_current_pilot_screenplays import SOURCE, original_reading_order
from plan_next_speaker_review_v9 import make_queue
from validate_private_pilot_snapshot import ORIGINAL_CANDIDATE_PARTS, canonical_dialogue

S01_DIR = ROOT / "saved-private/editorial-agent1-v18"
S09_DIR = ROOT / "seasons/S09/S09E19/derived/editorial-v17"
S01_MANIFEST = S01_DIR / "manifest.json"
S09_MANIFEST = S09_DIR / "S09E19-v17-source-first-reader-manifest.json"
S09_LEDGER = S09_DIR / "s09e19-source-exact-editorial-overlay-v17.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text("utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line]


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", "utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in rows), "utf-8")


def assert_original_dialogue(ep: str, rows: list[dict], screenplay: str) -> None:
    original = read_jsonl(ROOT / ORIGINAL_CANDIDATE_PARTS[ep])
    original.sort(key=lambda x: (x["cue"], x["part"]))
    witness = "".join(x["source_text"] for x in original)
    ordered = original_reading_order(rows)
    source_text = "".join(x["caption_text"] for x in ordered)
    assert canonical_dialogue(witness) == canonical_dialogue(source_text), (
        ep + ": source witness and edited reader differ"
    )
    # Neither paragraph-style scripts nor those with sampled-frame italic notes
    # may introduce/drop an original word or punctuation character. Only source
    # dialogue is indented, while headings and observational prose remain plain.
    manuscript_speech = "".join(
        line[4:] for line in screenplay.splitlines(keepends=True) if line.startswith("    ")
    )
    assert canonical_dialogue(source_text) == canonical_dialogue(manuscript_speech), (
        ep + ": edited manuscript differs from source reader characters"
    )


def integrate_s01(root: Path, old: list[dict]) -> tuple[list[dict], list[dict], str, dict]:
    manifest = read_json(S01_MANIFEST)
    assert manifest["schema"] == "night-court-private-s01-editorial-picture-v18/1"
    assert manifest["source_srt_sha256"] == SOURCE["S01E01"][0]
    assert manifest["source_part_refs"] == 404 and manifest["reader_blocks"] == 405
    assert manifest["source_units_fully_provisionally_named"] == 384
    assert manifest["source_units_with_UNKNOWN_voice"] == 20
    assert manifest["display_groups"] == 276
    assert manifest["independent_original_audio_actor_verifications"] == 0
    assert manifest["independent_performed_turn_verifications"] == 0
    assert manifest["full_episode_visual_verified"] is False
    assert manifest["original_script_generation_integrated"] is False
    script_bytes = (S01_DIR / "S01E01-editorial-screenplay.md").read_bytes()
    proof_bytes = (S01_DIR / "S01E01-editorial-provenance.jsonl").read_bytes()
    assert sha(script_bytes) == manifest["manuscript_sha256"]
    assert sha(proof_bytes) == manifest["provenance_sha256"]
    proof = [json.loads(line) for line in proof_bytes.decode("utf-8").splitlines() if line]
    assert len(proof) == 405
    original = {x["reading_block_id"]: x for x in old}
    assert len(original) == len(proof)
    assert {x["reading_block_id"] for x in proof} == set(original)
    new = []
    changes = []
    for side in proof:
        src = original[side["reading_block_id"]]
        assert src["episode_id"] == "S01E01"
        assert src["original_source_sha256"] == side["source_sha256"] == SOURCE["S01E01"][0]
        assert src["original_source_part_refs"] == side["original_source_part_refs"]
        assert src["source_reading_ref"] == side["source_reading_ref"]
        assert sha(src["caption_text"].encode("utf-8")) == side["exact_rendered_caption_sha256"]
        assert side["actual_original_av_reviewer_accepted"] is False
        assert src["speaker_turn_boundary_verified"] is False
        assert src["actor_face_or_voice_independently_verified"] is False
        if src["candidate_role"] != side["candidate_role"]:
            changes.append((src["source_reading_ref"], src["candidate_role"], side["candidate_role"]))
        row = dict(src)
        row["candidate_role"] = side["candidate_role"]
        if src["candidate_role"] != side["candidate_role"]:
            row["role_attribution_status"] = "episode_editorial_context_only_not_original_AV_verified"
            row["editorial_evidence_manifest"] = "saved-private/editorial-agent1-v18/manifest.json"
        new.append(row)
    assert sorted(changes) == sorted([
        ("C028.1", "BULL SHANNON", "LANA WAGNER"),
        ("C101.1", None, "SHEILA GARDINER"),
    ]), ("Unexpected S01 v18 speaker role edits", changes)
    g = defaultdict(set)
    for row in proof:
        g[row["display_group_id"]].add(row["candidate_role"])
    assert list(sorted(g)) == list(range(1,277))
    assert all(len(x) == 1 for x in g.values())
    assert next(x for x in proof if x["source_reading_ref"]=="C175.1")["display_group_id"] == next(
        x for x in proof if x["source_reading_ref"]=="C175.2")["display_group_id"]
    assert_original_dialogue("S01E01", new, script_bytes.decode("utf-8"))
    assert counts(new)["fully_provisionally_named_source_units"] == 384
    return new, proof, script_bytes.decode("utf-8"), {
        "editorial_version": "Agent1-v18",
        "manifest_sha256": sha(S01_MANIFEST.read_bytes()),
        "new_named_role_edits": len(changes),
        "sampled_picture_annotations": manifest["visual_annotation_count"],
        "no_independent_actor_voice_certification": True,
    }


def integrate_s09(old: list[dict], v16_binary: bytes) -> tuple[list[dict], list[dict], str, dict]:
    manifest = read_json(S09_MANIFEST)
    overlay = read_json(S09_LEDGER)
    assert manifest["schema"] == "night-court-s09e19-editorial-v17-source-reader/1"
    assert manifest["original_source_sha256"] == SOURCE["S09E19"][0]
    assert manifest["input_durable_v16_reader_sha256"] == sha(v16_binary)
    assert manifest["original_source_untimed"] is True
    assert (manifest["source_units"], manifest["provisional_editorial_reader_blocks"],
            manifest["fully_named_source_units"], manifest["source_units_with_unknown"]) == (347,323,271,76)
    assert manifest["role_edit_count"] == 11 and manifest["source_exact_split_count"] == 1
    assert manifest["original_audio_actor_identifications_independently_verified"] == 0
    assert manifest["original_performed_turns_verified"] == 0
    assert overlay["schema"] == "night-court-s09e19-source-exact-editorial-overlay/1"
    assert overlay["original_source_sha256"] == SOURCE["S09E19"][0]
    assert overlay["source_original_untimed"] is True

    rows = read_jsonl(S09_DIR / "S09E19-v17-source-first-reader.jsonl")
    episode_proof = read_jsonl(S09_DIR / "S09E19-editorial-v17-provenance.jsonl")
    assert len(rows) == len(episode_proof) == 323
    old_by_id = {row["reading_block_id"]: row for row in old}
    grouped = defaultdict(list)
    for row, p in zip(rows, episode_proof):
        ancestor = row["source_v16_reading_block_id"]
        assert ancestor in old_by_id
        grouped[ancestor].append(row)
        assert row["episode_id"] == "S09E19"
        assert row["original_source_sha256"] == p["original_source_sha256"] == SOURCE["S09E19"][0]
        assert row["original_source_part_refs"] == p["original_source_part_refs"]
        assert row["caption_text"] == p["caption_text_exact"]
        assert row["candidate_role"] == p["provisional_role"]
        assert row["source_original_times_ms"] is None and row["original_source_untimed"] is True
        assert p["source_times"] is None and p["source_turn_and_role_independent_AV_verified"] is False
        assert row["speaker_turn_boundary_verified"] is False
        assert row["actor_face_or_voice_independently_verified"] is False
    assert set(grouped) == set(old_by_id)
    changed = []
    for parent_id, parts in grouped.items():
        src = old_by_id[parent_id]
        assert "".join(p["caption_text"] for p in parts) == src["caption_text"]
        assert all(p["original_source_part_refs"] == src["original_source_part_refs"] for p in parts)
        if len(parts) == 1:
            assert parts[0]["reading_block_id"] == parent_id
            if parts[0]["candidate_role"] != src["candidate_role"]:
                changed.append((src["source_reading_ref"],src["candidate_role"],parts[0]["candidate_role"]))
        else:
            assert len(parts) == 2 and src["source_reading_ref"] == "C291.1"
            assert [p["caption_text"] for p in parts] == ["He. ","He was me."]
            assert [p["candidate_role"] for p in parts] == [None,"ALEX PATTERSON"]
    expected = [(p["source_reading_ref"],p["expected_prior_role"],p["new_provisional_role"]) for p in overlay["role_edits"]]
    assert sorted(changed) == sorted(expected), ("Unexpected S09 v17 role edits",changed)
    # Ensure alternate-identity confusion remains explicitly unresolved.
    assert next(x for x in rows if x["source_reading_ref"] == "C129.1")["candidate_role"] is None
    assert next(x for x in rows if x["source_reading_ref"] == "C305.1")["candidate_role"] == "ROZ RUSSELL"
    assert next(x for x in rows if x["source_reading_ref"] == "C306.1")["candidate_role"] == "ALEX PATTERSON"

    sidecars = []
    group_sizes = Counter(p["reading_group_id"] for p in episode_proof)
    for row, p in zip(rows, episode_proof):
        sidecars.append({
            "reading_block_id": row["reading_block_id"],
            "source_reading_ref": row["source_reading_ref"],
            "original_source_part_refs": row["original_source_part_refs"],
            "source_sha256": SOURCE["S09E19"][0],
            "exact_rendered_caption_sha256": sha(row["caption_text"].encode("utf-8")),
            "candidate_role": row["candidate_role"],
            "display_group_id": p["reading_group_id"],
            "display_join_not_performed_turn_proof":group_sizes[p["reading_group_id"]]>1,
            "source_cue_times_not_subturn_times_ms": None,
            "source_exact_character_span": row.get("source_exact_character_span"),
            "original_source_unicode_spans_v13": row.get("original_source_unicode_spans_v13"),
            "actual_original_av_reviewer_accepted":False,
        })
    script_bytes = (S09_DIR / "S09E19-editorial-v17-working-screenplay.md").read_bytes()
    assert "659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2" in script_bytes.decode("utf-8")
    assert_original_dialogue("S09E19", rows, script_bytes.decode("utf-8"))
    assert len(set(p["reading_group_id"] for p in episode_proof)) == 244
    assert counts(rows)["fully_provisionally_named_source_units"] == 271
    return rows, sidecars, script_bytes.decode("utf-8"), {
        "editorial_version": "Agent2-v17",
        "manifest_sha256":sha(S09_MANIFEST.read_bytes()),
        "role_edits":len(changed),
        "c291_source_exact_split": True,
        "no_independent_actor_voice_certification":True,
    }


def integrate(output: Path) -> dict:
    output = output.resolve(strict=True)
    if output.is_relative_to(ROOT.resolve()):
        raise ValueError("Private generated corpus must be outside tracked Night Court source tree")
    old_bytes = (output / "pilot-manual-context-speaker-v16.jsonl").read_bytes()
    old = [json.loads(line) for line in old_bytes.decode("utf-8").splitlines() if line]
    layout = read_json(output / "working-screenplay-layout-manifest.json")
    assert layout["schema"] == "night-court-private-pilot-screenplay-layout/2"
    assert sha(old_bytes) == layout["source_manual_v16_reader_sha256"]
    assert len(old) == 727 and counts(old)["fully_provisionally_named_source_units"] == 651
    first, first_side, first_script, first_info = integrate_s01(output, [x for x in old if x["episode_id"]=="S01E01"])
    second, second_side, second_script, second_info = integrate_s09(
        [x for x in old if x["episode_id"]=="S09E19"], old_bytes
    )
    new = original_reading_order(first + second)
    after = counts(new)
    assert (len(new),after["source_units"],after["fully_provisionally_named_source_units"],
            after["source_units_with_any_unknown_voice"]) == (728,751,655,96)
    source_raw = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True)+"\n" for row in new).encode("utf-8")
    (output / "pilot-current-editorial-reader.jsonl").write_bytes(source_raw)
    episodes = {"S01E01":(first_side,first_script,first_info),
                "S09E19":(second_side,second_script,second_info)}
    editorial_manifest = {"schema":"night-court-private-two-pilot-integrated-editorial/1",
                          "base_v16_reader_sha256":sha(old_bytes),
                          "current_editorial_reader_sha256":sha(source_raw),
                          "original_source_units":751,
                          "named_provisional":655,"units_with_unknown_voice":96,
                          "provisional_reader_blocks":728,
                          "episode_evidence":{},"AV_accepted_actors":0,
                          "AV_accepted_performed_turns":0}
    for ep,(side,script,info) in episodes.items():
        groups = [x["display_group_id"] for x in side]
        assert groups == sorted(groups)
        assert set(groups) == set(range(1,max(groups)+1))
        layout["episodes"][ep] = {
            "source_units":SOURCE[ep][1],
            "source_blocks":len(side),
            "display_groups":max(groups),
            "display_joins_unverified":len(side)-max(groups),
            "original_caption_timed":SOURCE[ep][2],
            "full_original_audio_video_accepted":False,
        }
        manuscript=(output/f"{ep}-working-screenplay.md")
        manuscript.write_text(script,"utf-8")
        write_jsonl(output/f"{ep}-working-screenplay-provenance.jsonl",side)
        layout["manuscript_sha256"][ep]=sha(manuscript.read_bytes())
        editorial_manifest["episode_evidence"][ep]=dict(info,
            manuscript_sha256=layout["manuscript_sha256"][ep],
            canonical_provenance_sha256=sha((output/f"{ep}-working-screenplay-provenance.jsonl").read_bytes()),
            original_source_sha256=SOURCE[ep][0],
            original_units=SOURCE[ep][1],
            source_reading_blocks=len(side),
            display_groups=max(groups),
            fully_named_units=384 if ep=="S01E01" else 271,
            units_with_unknown=20 if ep=="S01E01" else 76,
        )
    layout["current_editorial_reader_sha256"]=sha(source_raw)
    layout["source_unit_counts"]={"original_source_units":751,"named_provisional":655,"unknown":96}
    layout["episode_editorial_integrations"]={"S01E01":"Agent1-v18","S09E19":"Agent2-v17"}
    layout["provisional_contextual_roles_only"]=True
    layout["scene_review_complete"]=False
    layout["new_independently_verified_actor_voices"]=0
    layout["new_independently_verified_performed_turns"]=0
    write_json(output/"working-screenplay-layout-manifest.json",layout)
    write_json(output/"pilot-current-editorial-manifest.json",editorial_manifest)

    # The original 100-unit queue remains an archived v16 baseline outside
    # this current snapshot. Regenerate exactly from updated source rows.
    private_review=output/"private-review"
    assert private_review.is_dir()
    for prior in private_review.glob("remaining-*-speaker-review*"):
        prior.unlink()
    internal = read_json(ROOT/"research/probable-internal-speaker-switches-v1.json")
    review,summary=make_queue(new,{},internal,expected_named=655,expected_unknown=96)
    assert summary["remaining_unknown_original_source_units_by_episode"] == {"S01E01":20,"S09E19":76}
    assert any(x["episode_id"]=="S09E19" and x["source_reading_ref"]=="C129.1" for x in review)
    summary["current_editorial_reader_sha256"]=sha(source_raw)
    summary["s09_candidate_audio_locator_loaded"]=False
    summary["new_automatic_roles_proposed_from_editorial_review"]=0
    write_jsonl(private_review/"remaining-96-speaker-review.jsonl",review)
    write_json(private_review/"remaining-96-speaker-review-summary.json",summary)
    (output/"READ_ME_FIRST.txt").write_text(
        "PRIVATE Night Court original-series source-dialogue editorial scripts.\n"
        "S01E01 Agent1-v18 (11 historical original-source sampled-picture annotations), "
        "S09E19 Agent2-v17 (11 role edits, cautious C291 source split).\n"
        "751 immutable source units; 655 wholly PROVISIONALLY named; 96 with UNKNOWN "
        "voices; 728 proposed reader blocks; display groups not verified performed turns.\n"
        "Every original source word and punctuation character retained. "
        "No independent original-soundtrack actor or turn acceptance. "
        "No full episode independently AV certified. S09 source entirely untimed.\n"
        "Canonical two-pilot manifests and per-row provenance are adjacent. "
        "193-episode private fan retrieval is generated from these current manuscripts "
        "plus 191 source-only episode readings; staging and speaker roles provisional.\n",
        "utf-8"
    )
    return editorial_manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--working-root",required=True,type=Path)
    args=ap.parse_args()
    manifest=integrate(args.working_root)
    print(json.dumps({
        "current_reader_blocks":manifest["provisional_reader_blocks"],
        "current_fully_named_source_units":manifest["named_provisional"],
        "unknown_source_units":manifest["units_with_unknown_voice"],
        "episodes":{k:v["editorial_version"] for k,v in manifest["episode_evidence"].items()},
        "independent_av_verifications":0,
    },sort_keys=True))


if __name__=="__main__":
    main()
