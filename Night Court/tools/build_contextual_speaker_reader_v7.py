#!/usr/bin/env python3
"""Apply source-bound, *unreviewed* context-derived Night Court speaker proposals.

Private v7 speaker-first readers give explicit source provenance for every cue
and keep alternatives / unknowns truthful. Do not mistake editorial dialogue
reasoning for AV verification. The original caption and v5/v6 scripts are never
modified. A later reviewer may accept, correct, or reject each proposal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from build_pilot_character_evidence import ROOT, records_for_episode
from build_pilot_fan_beat_cards import load_witness
from fan_sqlite_index import apply_speaker_improvements

SCHEMA = "night-court-original-pilot-contextual-speaker-proposals/1"
RECORD_SCHEMA = "night-court-private-contextual-speaker-reading/1"
SEED = ROOT / "research/pilot-contextual-speaker-proposals-v1.json"
CAST = ROOT / "research/pilot-episode-credited-cast-v1.json"
ALLOWED_DESCRIPTIVE = {"BATHROBE SPECTATOR"}
EXPECTED = {"S01E01": 59, "S09E19": 34}


def source_unit_list(row: dict) -> list[str]:
    value = row.get("original_source_part_refs")
    if not isinstance(value, list) or not value or any(
        re.fullmatch(r"C\d{3}\.\d+", ref) is None for ref in value
    ):
        raise ValueError("Reading record lacks reversible original source parts")
    return value


def apply_candidates(rows: list[dict], proposals: dict,
                     cast: dict, source_shas: dict,
                     strict: bool = True) -> tuple[list[dict], dict]:
    if proposals.get("schema") != SCHEMA:
        raise ValueError("Wrong contextual speaker candidate schema")
    for ep in ("S01E01", "S09E19"):
        if proposals.get("source_witnesses", {}).get(ep) != source_shas[ep]:
            raise ValueError("Proposals point to different original source edition")
    roles = {}
    for ep, data in cast.get("episodes", {}).items():
        roles[ep] = {x["character"] for x in data["people"]}
    # This is an actor's cameo role, a fictional dialogue label not an
    # attempt to identify the uncredited real-life actor.
    roles["S01E01"] |= ALLOWED_DESCRIPTIVE
    roles["S09E19"] |= {
        "ALEX PATTERSON", "THE GUY (PLAYING ALEX)"
    }
    by_key = {}
    for index, row in enumerate(rows):
        ep, source_ref = row["episode_id"], row["source_reading_ref"]
        key = (ep, source_ref)
        # The prior C034.1 explicit split creates two records with the same
        # original source locator; proposals must not overwrite it.
        by_key.setdefault(key, []).append(index)

    seen = set()
    changes = []
    added_unit_refs = set()
    for proposal in proposals.get("proposals", []):
        ep = proposal.get("episode_id")
        ref = proposal.get("source_ref")
        role = proposal.get("proposed_role")
        key = (ep, ref)
        if key in seen or ep not in roles or role not in roles[ep]:
            raise ValueError("Duplicate, wrong-episode or unlisted named character")
        seen.add(key)
        matches = by_key.get(key, [])
        if len(matches) != 1:
            raise ValueError("Ambiguous original source block or already split cue: " + str(key))
        idx = matches[0]
        old = rows[idx]
        if old["candidate_role"] is not None or old["role_attribution_status"] != "unidentified":
            raise ValueError("Cannot override an existing speaker attribution")
        if (proposal.get("original_audio_reviewed") is not False
            or proposal.get("character_verified") is not False
            or proposal.get("evidence_tier") not in (
                "narrative_context_proposal", "episode_specific_external_quote_context"
            )):
            raise ValueError("False AV certainty or unsupported evidence tier")
        if (proposal["evidence_tier"] == "episode_specific_external_quote_context"
            and proposal.get("source_url") !=
                "https://en.wikiquote.org/wiki/Night_Court_(season_1)"):
            raise ValueError("Published external speaker claim lacks source URL")
        refs = source_unit_list(old)
        if any((ep, unit) in added_unit_refs for unit in refs):
            raise ValueError("Source cue reused by several contextual proposals")
        added_unit_refs.update((ep, unit) for unit in refs)
        changes.append((idx, proposal))
    if strict:
        count = Counter(ep for ep, unit in added_unit_refs)
        if dict(count) != EXPECTED or len(changes) != 90:
            raise ValueError("Contextual proposal source-unit count drift")
    result = [dict(r) for r in rows]
    for idx, proposed in changes:
        row = result[idx]
        row["candidate_role"] = proposed["proposed_role"]
        row["role_attribution_status"] = "narrative_context_candidate_not_voice_verified"
        row["editorial_confidence_group"] = proposed.get("confidence_group")
        row["attribution_evidence_tier"] = proposed["evidence_tier"]
        row["external_character_quote_source_url"] = proposed.get("source_url")
        row["original_audio_reviewed"] = False
        row["speaker_turn_boundary_verified"] = False
        row["actor_face_or_voice_independently_verified"] = False
    unit_roles = {}
    source_unique = set()
    for row in result:
        ep = row["episode_id"]
        for unit in source_unit_list(row):
            key = (ep, unit)
            source_unique.add(key)
            unit_roles.setdefault(key, set()).add(row["candidate_role"])
    source_named = sum(None not in vals for vals in unit_roles.values())
    report = {
        "schema": RECORD_SCHEMA,
        "source_units_total": len(source_unique),
        "source_units_provisionally_named": source_named,
        "source_units_unknown": len(source_unique) - source_named,
        "new_contextual_source_units_proposed": len(added_unit_refs),
        "new_contextual_reading_blocks": len(changes),
        "audio_confirmed_by_this_pass": 0,
        "one_original_cue_s09_two_named_speakers": "S09E19:C034.1",
        "source_unit_distribution": {ep: sum(k[0] == ep for k in source_unique)
                                     for ep in ("S01E01", "S09E19")},
    }
    if strict and (len(source_unique), source_named, len(source_unique)-source_named) != (751, 583, 168):
        raise ValueError("Original source coverage or candidate identity ledger drift")
    return result, report


def build(root: Path, previous_v6: Path, proposals_path: Path, out: Path) -> dict:
    if out.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private text-bearing speaker manuscripts must stay outside repository")
    v6_manifest = json.loads((previous_v6 / "speaker-improvement-manifest.json").read_text("utf-8"))
    if (v6_manifest.get("remaining_unidentified_source_units") != 261 or
        v6_manifest.get("new_provisional_named_source_units") != 490 or
        v6_manifest.get("original_audio_speaker_identities_verified_by_this_change") != 0):
        raise ValueError("Source-checked initial 440 speaker correction absent")
    old = [r for ep in ("S01E01", "S09E19") for r in records_for_episode(root, ep)]
    public_source = [
        {"episode_id": ep,
         "retrieval_text":(previous_v6 / ep / "screenplay-external-speakers-v6.md").read_text("utf-8")}
        for ep in ("S01E01", "S09E19")
    ]
    base = [
        json.loads(line)
        for line in (previous_v6 / "speaker-improvement-overrides.jsonl").read_text("utf-8").splitlines()
        if line.strip()
    ]
    baseline = apply_speaker_improvements(public_source, old, base, require_full=True)
    cast = json.loads((root / CAST.relative_to(ROOT)).read_text("utf-8"))
    proposal_bytes = proposals_path.read_bytes()
    proposals = json.loads(proposal_bytes)
    source_shas = {
        ep: load_witness(root, ep)[0]["sha256"]
        for ep in ("S01E01", "S09E19")
    }
    records, report = apply_candidates(baseline, proposals, cast, source_shas, strict=True)
    report["proposal_ledger_sha256"] = hashlib.sha256(proposal_bytes).hexdigest()
    report["all_identity_statuses_are_provisional"] = True
    report["source_only_character_reader_not_av_staged"] = True
    out.mkdir(parents=True, exist_ok=True)
    raw_roles = "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in records)
    (out / "pilot-provisional-context-character-reads.jsonl").write_text(raw_roles, "utf-8")
    report["reading_record_sha256"] = hashlib.sha256(raw_roles.encode("utf-8")).hexdigest()
    report["generated_reader_sha256_by_episode"] = {}
    for ep in ("S01E01","S09E19"):
        lines = [
            f"# {ep}: private source-first named-character working reader (v7)",
            "",
            "Not audio verified. Original held cue/parts preserved. Every name is provisional;",
            "names introduced by contextual inference are editorial hypotheses. ",
            "This is the priority speaker-reading view, not verified filmed stage direction.",
            f"Original caption source SHA256: {source_shas[ep]}",
            "",
        ]
        for row in records:
            if row["episode_id"] != ep:
                continue
            parts = row["original_source_part_refs"]
            role = row["candidate_role"] or "UNIDENTIFIED SPEAKER"
            lines.extend([
                "### " + row["source_reading_ref"] + " (" + ", ".join(parts) + ")",
                role + " · " + row["role_attribution_status"],
                row["caption_text"],
                "",
            ])
        finished_reader = "\n".join(lines).rstrip() + "\n"
        (out / f"{ep}-private-speaker-first-v7.md").write_text(finished_reader, "utf-8")
        report["generated_reader_sha256_by_episode"][ep] = hashlib.sha256(
            finished_reader.encode("utf-8")).hexdigest()
    (out / "pilot-contextual-speaker-manifest.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", "utf-8"
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--v6",type=Path,required=True)
    parser.add_argument("--ledger",type=Path,default=SEED)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    r=build(a.root,a.v6,a.ledger,a.output)
    print(f"{r['source_units_provisionally_named']}/{r['source_units_total']} "
          "source units now have proposed names, "
          f"{r['source_units_unknown']} unidentified; no independent AV identity confirmed")


if __name__ == "__main__":
    main()
