#!/usr/bin/env python3
"""Promote the newest committed S01 v22 / S09 v19 pilots, source-exact, privately.

Use the already reproducible v16 -> v18/v17 baseline integrator, then admit
only the SHA-pinned and fully cross-checked episode editorial successors.
All speech/actor/turn claims remain provisional. Never alter source witnesses.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

from integrate_committed_editorial_pilots import (
    ROOT, SOURCE, assert_original_dialogue, integrate as baseline_integrate,
    read_json, read_jsonl, sha, write_json, write_jsonl,
)
from apply_manual_context_pilot_review_v16 import counts
from render_current_pilot_screenplays import original_reading_order
from plan_next_speaker_review_v9 import make_queue

S01 = ROOT / "saved-private/editorial-agent1-v22"
S01_PROOF = ROOT / "saved-private/editorial-agent1-v21/S01E01-editorial-provenance.jsonl"
S01_MANIFEST = S01 / "manifest.json"
S01_OVERLAY = ROOT / "seasons/S01/S01E01/derived/editorial-agent1-v22-three-source-picture-stage-patches.json"
S09 = ROOT / "seasons/S09/S09E19/derived/editorial-v19"
S09_V18 = ROOT / "seasons/S09/S09E19/derived/editorial-v18"


def github_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def signature(row: dict) -> tuple:
    return (row["reading_block_id"], row["source_reading_ref"],
            tuple(row["original_source_part_refs"]), row["caption_text"],
            row["original_source_sha256"])


def validate_stage_overlay(screenplay: str) -> str:
    overlay = read_json(S01_OVERLAY)
    assert overlay["baseline_manuscript_sha256"] == (
        "191ddc1766e59d3da3619307cdb2bb55710788905d3d67aecab181ec729e62ae")
    assert overlay["baseline_provenance_sha256"] == sha(S01_PROOF.read_bytes())
    assert overlay["frames_verified"] == 510 and overlay["contact_sheets_inspected"] == 11
    assert set(x["stage_id"] for x in overlay["revisions"]) == {
        "PIC-01", "PIC-03", "PIC-08", "PIC-09", "PIC-10"}
    # Three changes are already in the complete v22 manuscript; the last two
    # are a separately reviewed optional stage-only supplement, not dialogue.
    for note in overlay["revisions"]:
        marker = note["stage_id"]
        assert screenplay.count("`[" + marker + "]`") == 1
        if marker not in ("PIC-03", "PIC-10"):
            continue
        expression = r"(?m)^\*[^\n]+\* `\[" + marker + r"\]`"
        matches = list(re.finditer(expression, screenplay))
        assert len(matches) == 1, "Unmatched source-staging patch: " + marker
        replacement = "*" + note["revised"] + "* `[" + marker + "]`"
        screenplay = screenplay[:matches[0].start()] + replacement + screenplay[matches[0].end():]
    tags = re.findall(r"\[PIC-(\d+)\]", screenplay)
    assert len(tags) == len(set(tags)) == 27
    return screenplay


def integrate_s01(current: list[dict]) -> tuple[list[dict], list[dict], str, dict]:
    manifest = read_json(S01_MANIFEST)
    assert manifest["schema"] == "night-court-s01e01-picture-choreography-source-stable-v22/1"
    assert manifest["source_original_srt_sha256"] == SOURCE["S01E01"][0]
    assert manifest["baseline_v21_provenance_sha256"] == sha(S01_PROOF.read_bytes())
    assert (manifest["original_srt_cues"], manifest["source_speaking_unit_refs"],
            manifest["source_reader_rows"],manifest["provisionally_fully_named_source_units"],
            manifest["original_source_units_containing_UNKNOWN"],
            manifest["proposed_display_groups"]) == (336,404,405,390,14,275)
    assert manifest["independently_verified_actor_voices"] == 0
    assert manifest["independently_verified_performed_turns"] == 0
    assert manifest["full_continuous_original_Av_accepted"] is False
    raw = (S01 / "S01E01-editorial-screenplay.md").read_bytes()
    assert github_blob_sha(raw) == manifest["latest_full_screenplay_git_blob_sha"]
    screenplay = validate_stage_overlay(raw.decode("utf-8"))
    proof = read_jsonl(S01_PROOF)
    assert len(current) == len(proof) == 405
    prior = {r["reading_block_id"]:r for r in current}
    assert len(prior) == len(proof)
    updated, changes = [], []
    for p in proof:
        row = prior[p["reading_block_id"]]
        assert row["episode_id"] == "S01E01"
        assert row["original_source_sha256"] == p["source_sha256"] == SOURCE["S01E01"][0]
        assert row["source_reading_ref"] == p["source_reading_ref"]
        assert row["original_source_part_refs"] == p["original_source_part_refs"]
        assert sha(row["caption_text"].encode("utf-8")) == p["exact_rendered_caption_sha256"]
        assert row["speaker_turn_boundary_verified"] is False
        assert row["actor_face_or_voice_independently_verified"] is False
        assert p["actual_original_av_reviewer_accepted"] is False
        if p["source_reading_ref"] == "S01E01-C219-SOURCE-TURN-2":
            assert p["source_exact_character_span"]["start_char"] == 38
            assert p["source_exact_character_span"]["end_char"] == 45
        if row["candidate_role"] != p["candidate_role"]:
            changes.append((p["source_reading_ref"], row["candidate_role"], p["candidate_role"]))
        row = dict(row)
        row["candidate_role"] = p["candidate_role"]
        if row["source_reading_ref"] in {x[0] for x in changes}:
            row["role_attribution_status"] = "episode_editorial_context_not_original_AV_verified"
            row["attribution_full_provisional_label"] = (
                p["candidate_role"] + " · CONTEXT PROVISIONAL")
            row["editorial_evidence_manifest"] = "saved-private/editorial-agent1-v22/manifest.json"
        updated.append(row)
    assert sorted(changes) == sorted([
        ("C010.1",None,"BULL SHANNON"),
        ("C011.1",None,"PAINTER"),
        ("C084.1",None,"DAN FIELDING"),
        ("C102.1",None,"LANA WAGNER"),
        ("C103.1",None,"LANA WAGNER"),
        ("S01E01-C219-SOURCE-TURN-2",None,"PHIL KERR"),
    ]), ("Unexpected S01 role amendment",changes)
    gs=defaultdict(set)
    for p in proof:
        gs[p["display_group_id"]].add(p["candidate_role"])
    assert list(sorted(gs)) == list(range(1,276))
    assert all(len(g)==1 for g in gs.values())
    assert counts(updated)["fully_provisionally_named_source_units"] == 390
    assert_original_dialogue("S01E01", updated, screenplay)
    return updated, proof, screenplay, {
        "editorial_version":"Agent1-v22",
        "manifest_sha256":sha(S01_MANIFEST.read_bytes()),
        "contextually_updated_roles":len(changes),
        "sampled_picture_annotations":27,
        "frame_sha_verified":510,
        "no_independent_actor_voice_certification":True,
    }


def integrate_s09(current: list[dict]) -> tuple[list[dict], list[dict], str, dict]:
    data = read_json(S09 / "S09E19-v19-audit.json")
    assert data["original_source_sha256"] == SOURCE["S09E19"][0]
    assert (data["original_untimed_cues"],data["current_reading_blocks"],
            data["fully_provisionally_named_source_units"],
            data["units_containing_UNKNOWN"],data["v19_display_groups"]) == (347,323,273,74,234)
    assert data["original_AV_verified_speakers"] == data["original_AV_verified_turn_joins"] == 0
    rows = read_jsonl(S09 / "S09E19-v19-editorial-reader.jsonl")
    proof = read_jsonl(S09 / "S09E19-v19-provenance.jsonl")
    v18 = read_jsonl(S09_V18 / "S09E19-v18-editorial-reader.jsonl")
    assert len(current) == len(v18) == len(rows) == len(proof) == 323
    changed=[]
    for base,intermediate,row,p in zip(current,v18,rows,proof):
        assert signature(base) == signature(intermediate) == signature(row)
        assert intermediate["candidate_role"] == row["candidate_role"]
        assert p["source_reading_block_id"] == row["reading_block_id"]
        assert p["source_reading_ref"] == row["source_reading_ref"]
        assert p["original_source_parts"] == row["original_source_part_refs"]
        assert p["caption_text_exact"] == row["caption_text"]
        assert p["source_caption_sha256"] == SOURCE["S09E19"][0]
        assert p["provisional_role"] == row["candidate_role"]
        assert p["independent_audio_identity_review"] is False
        assert p["performed_turn_soundtrack_verified"] is False
        assert row["actor_face_or_voice_independently_verified"] is False
        assert row["speaker_turn_boundary_verified"] is False
        assert row["source_original_times_ms"] is None
        if base["candidate_role"] != row["candidate_role"]:
            changed.append((row["source_reading_ref"],base["candidate_role"],row["candidate_role"]))
    assert sorted(changed) == sorted([
        ("C051.1",None,"CHRISTINE SULLIVAN"),
        ("C229.1",None,"THE GUY (PLAYING ALEX)"),
    ]), ("Unexpected S09 v19 speaker amendments",changed)
    sizes=Counter(p["display_group_id"] for p in proof)
    assert sorted(sizes) == list(range(1,235))
    side=[]
    for row,p in zip(rows,proof):
        side.append({
            "reading_block_id":row["reading_block_id"],
            "source_reading_ref":row["source_reading_ref"],
            "original_source_part_refs":row["original_source_part_refs"],
            "source_sha256":SOURCE["S09E19"][0],
            "exact_rendered_caption_sha256":sha(row["caption_text"].encode("utf-8")),
            "candidate_role":row["candidate_role"],
            "display_group_id":p["display_group_id"],
            "display_join_not_performed_turn_proof":sizes[p["display_group_id"]]>1,
            "source_cue_times_not_subturn_times_ms":None,
            "source_exact_character_span":row.get("source_exact_character_span"),
            "original_source_unicode_spans_v13":row.get("original_source_unicode_spans_v13"),
            "actual_original_av_reviewer_accepted":False,
        })
    script=(S09/"S09E19-v19-working-screenplay.md").read_text("utf-8")
    assert SOURCE["S09E19"][0] in script
    assert_original_dialogue("S09E19",rows,script)
    assert counts(rows)["fully_provisionally_named_source_units"] == 273
    return rows,side,script,{
        "editorial_version":"Agent2-v19",
        "v19_audit_sha256":sha((S09/"S09E19-v19-audit.json").read_bytes()),
        "contextual_role_edits_from_v17":2,
        "anonymous_display_groups":234,
        "no_independent_actor_voice_certification":True,
    }


def integrate(output: Path) -> dict:
    # Every launch starts with a regenerated, exact source-grounded predecessor.
    baseline_integrate(output)
    prior=read_jsonl(output/"pilot-current-editorial-reader.jsonl")
    s01,p01,script01,info01=integrate_s01([r for r in prior if r["episode_id"]=="S01E01"])
    s09,p09,script09,info09=integrate_s09([r for r in prior if r["episode_id"]=="S09E19"])
    merged=original_reading_order(s01+s09)
    c=counts(merged)
    assert (len(merged),c["source_units"],c["fully_provisionally_named_source_units"],
            c["source_units_with_any_unknown_voice"]) == (728,751,663,88)
    reader=b"".join(json.dumps(r,ensure_ascii=False,sort_keys=True).encode("utf-8")+b"\n" for r in merged)
    (output/"pilot-current-editorial-reader.jsonl").write_bytes(reader)
    layout=read_json(output/"working-screenplay-layout-manifest.json")
    editorial=read_json(output/"pilot-current-editorial-manifest.json")
    for ep,rows,provenance,script,info,fully,unknown in [
        ("S01E01",s01,p01,script01,info01,390,14),
        ("S09E19",s09,p09,script09,info09,273,74),
    ]:
        groups=[x["display_group_id"] for x in provenance]
        assert groups == sorted(groups)
        assert sorted(set(groups)) == list(range(1,max(groups)+1))
        write_jsonl(output/f"{ep}-working-screenplay-provenance.jsonl",provenance)
        (output/f"{ep}-working-screenplay.md").write_text(script,"utf-8")
        layout["episodes"][ep].update(source_blocks=len(rows),display_groups=max(groups),
            display_joins_unverified=len(rows)-max(groups),full_original_audio_video_accepted=False)
        layout["manuscript_sha256"][ep]=sha(script.encode("utf-8"))
        editorial["episode_evidence"][ep]=dict(
            info,
            original_source_sha256=SOURCE[ep][0],
            original_units=SOURCE[ep][1],
            source_reading_blocks=len(rows),
            display_groups=max(groups),
            fully_named_units=fully,
            units_with_unknown=unknown,
            manuscript_sha256=layout["manuscript_sha256"][ep],
            canonical_provenance_sha256=sha(
                (output/f"{ep}-working-screenplay-provenance.jsonl").read_bytes()),
        )
    layout["current_editorial_reader_sha256"]=sha(reader)
    layout["source_unit_counts"]={"original_source_units":751,"named_provisional":663,"unknown":88}
    layout["episode_editorial_integrations"]={"S01E01":"Agent1-v22","S09E19":"Agent2-v19"}
    layout["provisional_contextual_roles_only"]=True
    layout["scene_review_complete"]=False
    layout["new_independently_verified_actor_voices"]=0
    layout["new_independently_verified_performed_turns"]=0
    editorial.update(
        current_editorial_reader_sha256=sha(reader),
        named_provisional=663,
        units_with_unknown_voice=88,
        provisional_reader_blocks=728,
        AV_accepted_actors=0,
        AV_accepted_performed_turns=0,
    )
    write_json(output/"working-screenplay-layout-manifest.json",layout)
    write_json(output/"pilot-current-editorial-manifest.json",editorial)
    review_dir=output/"private-review"
    for path in review_dir.glob("remaining-*-speaker-review*"):
        path.unlink()
    internal=read_json(ROOT/"research/probable-internal-speaker-switches-v1.json")
    queue,summary=make_queue(merged,{},internal,expected_named=663,expected_unknown=88)
    assert summary["remaining_unknown_original_source_units_by_episode"] == {"S01E01":14,"S09E19":74}
    summary["current_editorial_reader_sha256"]=sha(reader)
    summary["no_source_original_AV_reviewer_certification"]=True
    write_jsonl(review_dir/"remaining-88-speaker-review.jsonl",queue)
    write_json(review_dir/"remaining-88-speaker-review-summary.json",summary)
    (output/"READ_ME_FIRST.txt").write_text(
        "PRIVATE ORIGINAL-SERIES TWO-PILOT CURRENT SOURCE SCRIPT READER.\n"
        "S01E01 Agent1-v22 / S09E19 Agent2-v19, exact source and provenance.\n"
        "751 source units: 663 CONTEXTUALLY named, 88 still containing UNKNOWN.\n"
        "728 source-preserving reader blocks; 275/234 proposed display groups.\n"
        "All actual actor voices, delivery and performed turn boundaries remain unverified.\n"
        "No original soundtrack/continuous film editorial episode certified.\n"
        "193-episode retrieval output includes these two picture-enriched, provisional\n"
        "pilots and 191 source-only episode scaffolds. Do not publish as final scripts.\n",
        "utf-8",
    )
    return editorial


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--working-root",required=True,type=Path)
    args=p.parse_args()
    result=integrate(args.working_root.resolve(strict=True))
    print(json.dumps({
        "editions":{k:v["editorial_version"] for k,v in result["episode_evidence"].items()},
        "source_units":result["original_source_units"],
        "named_provisional":result["named_provisional"],
        "unknown":result["units_with_unknown_voice"],
        "reader_blocks":result["provisional_reader_blocks"],
        "AV_accepted":0,
    },sort_keys=True))


if __name__=="__main__":
    main()
