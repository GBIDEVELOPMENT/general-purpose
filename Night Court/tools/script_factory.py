#!/usr/bin/env python3
"""One-command, private, source-exact Night Court screenplay factory.

Best available screenplay for any of the 193 original-series episodes.
For the two pilots, reuse the canonical deeply edited manuscript (or a fully
validated source-AV reviewed promotion); for other episodes produce an honest,
complete caption-first reading draft with a reversible cue/turn review queue.
This command does not infer unheard voices, invent scene action, run an LLM,
or certify original audiovisual playback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "night-court-one-click-script-factory/1"
PILOTS = ("S01E01", "S09E19")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def json_lines(values) -> str:
    return "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in values)


def source_index(root: Path) -> dict:
    path = root / "catalog/dialogue-index.jsonl"
    records = [json.loads(s) for s in path.read_text("utf-8").splitlines() if s.strip()]
    found = {}
    for row in records:
        episode = row["episode_id"]
        if not re.fullmatch(r"S\d{2}E\d{2}", episode) or episode in found:
            raise ValueError("Invalid or duplicate original-series episode ID")
        found[episode] = row
    if len(found) != 193:
        raise ValueError("Source corpus must contain exactly 193 unique original episodes")
    return found


def source_rows(root: Path, index: dict):
    ep = index["episode_id"]
    folder = root / "seasons" / ep[:3] / ep
    manifest = json.loads((root / index["manifest"]).read_text("utf-8"))
    episode = json.loads((folder / "episode.json").read_text("utf-8"))
    if (manifest["episode_id"] != ep or episode["id"] != ep
            or manifest["sha256"] != index["sha256"]
            or manifest["version_id"] != index["version_id"]
            or manifest["cue_count"] != index["cue_count"]
            or manifest["declared_complete"] is not False):
        raise ValueError(ep + ": dialogue source/catalog drift")
    original = folder / manifest["original_path"]
    if sha(original.read_bytes()) != manifest["sha256"]:
        raise ValueError(ep + ": immutable original transcript bytes changed")
    rows = [json.loads(s) for s in (folder / manifest["segments_path"])
            .read_text("utf-8").splitlines() if s.strip()]
    if len(rows) != manifest["cue_count"] or [x["cue"] for x in rows] != list(range(1, len(rows) + 1)):
        raise ValueError(ep + ": original cues lost, duplicated or reordered")
    for row in rows:
        a, b = row["start_ms"], row["end_ms"]
        if not isinstance(row["text"], str) or not row["text"].strip():
            raise ValueError(ep + ": empty caption")
        if manifest["timecoded"]:
            if any(type(x) is not int for x in (a, b)) or not 0 <= a < b:
                raise ValueError(ep + ": invalid source timestamp")
        elif a is not None or b is not None:
            raise ValueError(ep + ": invented time on untimed source")
    return manifest, episode, rows


def source_role(text: str) -> str | None:
    """Only typographically explicit voice labels; never interpret vocatives."""
    m = re.match(r"^\s*(?:<v\s+([^>]+)>|([A-Z][A-Z0-9 '.-]{1,32}):\s+)", text)
    if not m:
        return None
    name = (m.group(1) or m.group(2)).strip()
    return name if name and not re.fullmatch(r"(MUSIC|LAUGHTER|APPLAUSE|SOUND|SFX)", name) else None


def multi_voice_typography(text: str) -> bool:
    lines = [line for line in text.splitlines() if line.strip()]
    return sum(bool(re.match(r"^\s*[-–—]\s+\S", line)) for line in lines) >= 2


def contextual_role_overlay(root: Path, ep: str, manifest: dict, cues: list):
    """Use latest existing source-SHA-pinned full-episode editorial reasoning.

    Contextual names are hypotheses, not observed voices; low-confidence roles
    and mixed-voice cues are left for P0/P1 AV investigation.
    """
    folder = root / "seasons" / ep[:3] / ep / "derived"
    paths = sorted(folder.glob("text-only-speaker-proposals-v*.json"),
                   key=lambda p: int(re.search(r"-v(\d+)\.json$", p.name).group(1)))
    if not paths:
        return {}, None
    selected = paths[-1]
    data = json.loads(selected.read_text("utf-8"))
    version = re.search(r"-v(\d+)\.json$", selected.name).group(1)
    src = data.get("source", {})
    records = data.get("records")
    if (data.get("schema") != "night_court_manual_context_speaker_proposals_v" + version
        or data.get("episode_id") != ep or src.get("source_sha256") != manifest["sha256"]
        or src.get("source_caption_units") != len(cues)
        or not isinstance(records, list) or len(records) != len(cues)):
        raise ValueError(ep + ": stale/malformed contextual role ledger")
    report = {
        "file": str(selected.relative_to(root)), "sha256": sha(selected.read_bytes()),
        "high_medium_single_role_hypotheses": 0,
        "mixed_voice_internal_review_cues": 0,
        "weak_or_abstained_cues": 0, "original_audio_verified": False
    }
    overlay = {}
    for cue, record in zip(cues, records):
        n = cue["cue"]
        status = record.get("status")
        mixed = status == "proposed_internal_voice_switch_unverified"
        names = record.get("proposed_ordered_speaker_parts", [])
        role = record.get("proposed_speaker")
        confidence = record.get("confidence")
        if (record.get("cue_id") != f"C{n:05d}.1"
            or record.get("source_unit_index") != n
            or confidence not in ("high", "medium", "low", "abstain")
            or (role is not None and (not isinstance(role, str) or not role.strip()))
            or not isinstance(names, list)
            or any(not isinstance(x, str) or not x.strip() for x in names)
            or (mixed and (role is not None or len(names) < 2))
            or (not mixed and names)
            or (confidence == "abstain" and role is not None)):
            raise ValueError(ep + f": contextual source cue {n} is malformed")
        strong = not mixed and confidence in ("high", "medium") and role is not None
        if not mixed and confidence in ("high", "medium") and not strong:
            raise ValueError(ep + ": strong contextual role missing")
        if strong:
            report["high_medium_single_role_hypotheses"] += 1
        elif mixed:
            report["mixed_voice_internal_review_cues"] += 1
        else:
            report["weak_or_abstained_cues"] += 1
        overlay[n] = {
            "provisional_role": role.strip() if strong else None,
            "internal_voice_roles": names, "confidence": confidence,
            "basis": record.get("basis", ""),
            "alternatives": record.get("alternative_speakers", []),
        }
    return overlay, report


def generic_episode(root: Path, ep: str, index: dict):
    manifest, meta, captions = source_rows(root, index)
    title = meta["title"]
    source_sha = manifest["sha256"]
    contextual, context_report = contextual_role_overlay(root, ep, manifest, captions)
    guests = [x.get("character", {}).get("name") for x in meta.get("credits", {}).get("guest_cast", [])]
    guests = sorted(set(x for x in guests if isinstance(x, str) and x))
    rows, edges, lines = [], [], [
        f"# Night Court (1984) · {ep} · {title}", "",
        "**COMPLETE AVAILABLE SOURCE-DIALOGUE DRAFT · NOT AV-CERTIFIED**", "",
        "Original transcript SHA-256: `" + source_sha + "`  ",
        "Evidence: intact original captions plus source-SHA-bound textual role hypotheses if available.",
        "All candidate names, dialogue boundaries, actual scenes, performance and visual blocking remain unverified.", "",
        "## Dialogue in source order", "",
    ]
    last = None
    group = 0
    named = 0
    multi = 0
    for cue in captions:
        num = cue["cue"]
        raw = cue["text"]
        label = source_role(raw)
        hint = contextual.get(num, {})
        candidate = hint.get("provisional_role")
        internal = hint.get("internal_voice_roles", [])
        # A mixed cue cannot be given one name until a source-heard P0 split.
        role = None if internal else (label or candidate)
        suspect = multi_voice_typography(raw) or bool(internal)
        multi += int(suspect)
        named += int(label is not None)
        start, end = cue["start_ms"], cue["end_ms"]
        gap = start - last["source_end_ms"] if last and start is not None and last["source_end_ms"] is not None else None
        scene_hint = last is None or (gap is not None and gap > 12000)
        if scene_hint:
            group += 1
            lines.extend([f"## Passage {group} (dialogue-gap cluster, NOT an observed scene)", ""])
        if last:
            previous_label = last["candidate_display_role"]
            continuing = bool(role and previous_label == role and gap is not None
                              and -1000 <= gap <= 2500 and not suspect and not last["multiple_voice_dashes"])
            edge_kind = ("same_provisional_role_candidate_continuation" if continuing
                         else "different_provisional_roles_candidate_change"
                         if role and previous_label and role != previous_label
                         else "unresolved_turn_boundary")
            edges.append({"between_cues": [num - 1, num], "decision": edge_kind,
                          "source_audio_verified": False,
                          "review_priority": "P0" if edge_kind == "unresolved_turn_boundary" else "P0_CONFIRM"})
        else:
            continuing = False
        row = {
            "cue": num, "source_text": raw, "source_text_sha256": sha(raw.encode("utf-8")),
            "source_start_ms": start, "source_end_ms": end, "source_label": label,
            "candidate_display_role": role, "contextual_role": candidate,
            "contextual_confidence": hint.get("confidence"),
            "contextual_evidence": hint.get("basis"),
            "contextual_alternatives": hint.get("alternatives", []),
            "contextual_intra_cue_voice_roles": internal,
            "source_label_verified_against_film": False,
            "candidate_role_original_soundtrack_verified": False,
            "multiple_voice_dashes": suspect,
            "passage_candidate": group, "provisional_continuation_of_previous": continuing,
            "original_dialogue_sha256": source_sha,
        }
        rows.append(row)
        if not continuing:
            if internal:
                heading = ("MULTIPLE UNIDENTIFIED VOICES (context proposes " +
                           " / ".join(internal) + "; internal boundary unverified)")
            else:
                heading = (role or "UNIDENTIFIED VOICE") + (
                    " (source label, unverified)" if label else
                    " (contextual hypothesis, unverified)" if candidate else "")
            lines.extend(["### " + heading, ""])
        lines.extend("    " + line for line in raw.split("\n"))
        lines.append("")
        last = row
    lines.extend([
        "## Source and editorial limits", "",
        f"- Source edition: `{manifest['version_id']}`; {len(captions)} of {len(captions)} cues present.",
        f"- {named} cues have source-explicit voice labels; {len(captions) - named} have no explicit source role.",
        f"- {context_report['high_medium_single_role_hypotheses'] if context_report else 0} high/medium contextual whole-cue names are hypotheses, NOT source-heard identities.",
        f"- {multi} cues contain multiple leading-dash voice hints and need internal P0 examination.",
        f"- {len(edges)} adjacent boundaries remain original-audio unverified.",
        f"- Episode-credited guest roles (not speaker assignments): {', '.join(guests) if guests else 'none listed'}.",
        "- Passage boundaries are caption-gap heuristics. Scene headings, wardrobe, props,",
        "  acting and physical business require observation of the original film.",
        "- Original words and original cue timing are preserved in provenance.jsonl.",
        "",
    ])
    return ("\n".join(lines), rows, edges, {
        "evidence_tier": "contextual_provisional_reading_draft" if context_report else "source_only_reading_draft",
        "contextual_overlay": context_report,
        "caption_cues": len(captions), "source_units": len(captions),
        "provisional_reader_blocks": len(rows),
        "source_explicit_label_cues": named,
        "unknown_label_cues": sum(x["candidate_display_role"] is None for x in rows),
        "internal_voice_handoff_review_cues": multi,
        "adjacent_p0_unverified": len(edges),
        "provisional_passages_not_verified_scenes": group,
        "original_dialogue_sha256": source_sha,
        "source_has_timecodes": manifest["timecoded"],
        "actual_av_verified": False, "independent_editorial_acceptance": False,
    })


def pilot_episode(root: Path, ep: str, index: dict):
    from episode_finish import load_episode
    snapshot = root / "saved-private/pilot-current"
    layout, source, witness = load_episode(snapshot, ep)
    if witness != index["sha256"]:
        raise ValueError(ep + ": pilot editorial source differs from corpus index")
    path = snapshot / (ep + "-working-screenplay.md")
    text = path.read_text("utf-8")
    tier = "canonical_provisional_editorial_script"
    independent = False
    review = root / "saved-private/episode-finish-current"
    decision = review / (ep + "-original-av-decisions.json")
    if decision.is_file():
        # Upgrade only from the existing strict P0/P1/P2/P3/P4 film and
        # independent-editor validator; never trust an arbitrary nearby MD.
        from publish_current_original_av import process
        status = process(ep, snapshot, review, review, write=False)
        if status.get("reviewed_sha256"):
            candidate = review / (ep + "-original-av-reviewed-screenplay.md")
            filed = review / (ep + "-original-av-reviewed-manifest.json")
            if candidate.is_file() and filed.is_file():
                metadata = json.loads(filed.read_text("utf-8"))
                if (sha(candidate.read_bytes()) == status["reviewed_sha256"]
                    and metadata.get("reviewed_manuscript_sha256") == status["reviewed_sha256"]):
                    text = candidate.read_text("utf-8")
                    tier = status["status"]
                    independent = status["independent_sample"] == "independent_editor_spotcheck_attested"
    rows = [{
        "reading_block_id": row["reading_block_id"],
        "original_source_part_refs": row["original_source_part_refs"],
        "source_text": row["source_exact_dialogue_for_private_av_review"],
        "source_text_sha256": row["exact_rendered_caption_sha256"],
        "provisional_role": row["candidate_role"],
        "candidate_display_group": row["display_group_id"],
        "source_original_cue_times_ms": row["source_cue_times_not_subturn_times_ms"],
        "original_dialogue_sha256": witness,
        "machine_candidate_is_original_av_certification": False,
    } for row in source]
    edges = [{
        "between_block_ids": [rows[i - 1]["reading_block_id"], rows[i]["reading_block_id"]],
        "provisional_continuation": rows[i - 1]["candidate_display_group"] == rows[i]["candidate_display_group"],
        "source_audio_verified_by_factory": False,
        "review_priority": "P0",
    } for i in range(1, len(rows))]
    count = layout["episodes"][ep]
    return text, rows, edges, {
        "evidence_tier": tier,
        "source_units": count["source_units"],
        "provisional_reader_blocks": len(rows),
        "provisional_display_groups": count["display_groups"],
        "unknown_label_blocks": sum(x["provisional_role"] is None for x in rows),
        "adjacent_p0_unverified": len(edges),
        "original_dialogue_sha256": witness,
        "source_has_timecodes": count["original_caption_timed"],
        "actual_av_verified": tier != "canonical_provisional_editorial_script",
        "independent_editorial_acceptance": independent,
    }


def construct(root: Path, ep: str, index: dict):
    if ep in PILOTS:
        script, rows, edges, details = pilot_episode(root, ep, index)
    else:
        script, rows, edges, details = generic_episode(root, ep, index)
    if not rows or not script.strip():
        raise ValueError(ep + ": empty script or source lineage")
    raw = script.encode("utf-8")
    records = json_lines(rows)
    reviews = json_text({"schema": SCHEMA, "episode_id": ep,
                         "priorities": ["P0_turns", "P1_identity", "P2_delivery",
                                        "P3_props_wardrobe", "P4_actions", "P5_coarse_time"],
                         "all_original_audio_boundaries_unverified": True,
                         "boundary_review_questions": edges,
                         "review_internal_voice_changes": [x.get("cue") for x in rows
                                                          if x.get("multiple_voice_dashes")],
                         "contextual_role_review": [{
                             "source_cue": x["cue"], "provisional_role": x["contextual_role"],
                             "confidence": x["contextual_confidence"],
                             "evidence": x["contextual_evidence"],
                             "alternatives": x["contextual_alternatives"],
                             "internal_voice_role_hypotheses": x["contextual_intra_cue_voice_roles"],
                             "original_audio_verified": False,
                         } for x in rows if x.get("contextual_confidence")],
                         "requires_original_av_and_independent_check": True})
    evidence = {
        "schema": SCHEMA, "episode_id": ep, "source_version_id": index["version_id"],
        "source_witness_sha256": index["sha256"],
        "script_sha256": sha(raw), "source_provenance_sha256": sha(records.encode("utf-8")),
        "p0_review_queue_sha256": sha(reviews.encode("utf-8")),
        **details,
        "dialogue_source_changed": False,
        "source_only_claims_never_promoted_to_av_truth": True,
    }
    return {
        "screenplay.md": script,
        "provenance.jsonl": records,
        "review-queue.json": reviews,
        "manifest.json": json_text(evidence),
    }, evidence


def write_episode(output: Path, episode: str, files: dict):
    target = output / episode
    target.mkdir(parents=True, exist_ok=True)
    changed = 0
    for filename, content in files.items():
        dest = target / filename
        if not dest.is_file() or dest.read_text("utf-8") != content:
            temporary = dest.with_name(dest.name + ".tmp")
            temporary.write_text(content, encoding="utf-8")
            temporary.replace(dest)
            changed += 1
    return changed


def run(root: Path, output: Path, episode: str):
    index = source_index(root)
    selected = sorted(index) if episode == "all" else [episode]
    if any(x not in index for x in selected):
        raise ValueError("Unknown original-series episode: " + episode)
    summary = []
    for ep in selected:
        files, report = construct(root, ep, index[ep])
        changed = write_episode(output, ep, files)
        summary.append({"episode": ep, "tier": report["evidence_tier"],
                        "source_units": report["source_units"], "changed_files": changed})
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode", required=True,
                        help="SXXEXX for any of 193 episodes, or all")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path,
                        help="Private stable output (default: Night Court/saved-private/script-factory-current)")
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output or root / "saved-private/script-factory-current").resolve()
    if output == root or output.is_relative_to(root / "seasons"):
        parser.error("Output must never overwrite original-series source dialogue")
    results = run(root, output, args.episode)
    print(json.dumps({"episodes": len(results), "output": str(output),
                      "changed_files": sum(x["changed_files"] for x in results),
                      "episode_results": results if len(results) <= 5 else [],
                      "all_original_av_certifications_are_source_bound": True},
                     sort_keys=True))


if __name__ == "__main__":
    main()
