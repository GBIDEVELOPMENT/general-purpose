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


def structural_speaker_parts(text: str) -> list[dict]:
    """Reversibly partition source Unicode at distinct line-leading voice dashes.

    A first and ONLY leading dash doesn't establish two performers, so keep
    that cue whole. However an undashed opening statement followed by one
    later line-leading dash DOES propose two source voices: the second dash
    is explicitly positioned after an earlier voice. Preserve all characters
    and keep the proposed source-turn boundary AV-unverified.
    """
    starts = [m.start() for m in re.finditer(r"(?m)^[ \t]*[-–—][ \t]+\S", text)]
    cuts = [0]
    # The first *internal* dash changes speaker after undashed opening text.
    # E.g. "...about what I said before.\n- Oh, don't worry." exactly splits.
    # A lone dash at the very start does NOT introduce a second source turn.
    if starts and text[:starts[0]].strip():
        cuts.append(starts[0])
    if len(starts) >= 2:
        cuts.extend(starts[1:])
    cuts.append(len(text))
    parts = [{
        "id": f"P{i:02d}", "start": start, "end": end,
        "text": text[start:end],
        "source_text_sha256": sha(text[start:end].encode("utf-8")),
        "source_indicates_possible_speaker_change": i > 1,
        "actual_speaker_boundary_verified": False,
    } for i, (start, end) in enumerate(zip(cuts, cuts[1:]), 1)]
    if (not parts or any(p["start"] >= p["end"] for p in parts)
        or "".join(p["text"] for p in parts) != text):
        raise ValueError("Original caption character conservation failed at P0 split")
    return parts


def contextual_exact_parts(text: str, offsets: list[int]) -> list[dict]:
    """Partition one caption at manually reasoned Unicode character offsets.

    A validated editorial offset is not an audio-heard speaker boundary.
    """
    boundaries = [0, *offsets, len(text)]
    parts = []
    for i, (start, end) in enumerate(zip(boundaries, boundaries[1:]), 1):
        part = text[start:end]
        if not part.strip():
            raise ValueError("Contextual speaker split produces empty dialogue")
        parts.append({
            "id": f"P{i:02d}", "start": start, "end": end,
            "text": part, "source_text_sha256": sha(part.encode("utf-8")),
            "source_indicates_possible_speaker_change": i > 1,
            "actual_speaker_boundary_verified": False,
            "split_basis": "contextual_source_exact_lexical_handoff",
        })
    if "".join(x["text"] for x in parts) != text:
        raise ValueError("Contextual P0 text conservation failed")
    return parts


def source_syntactic_continuation(left: str, right: str,
                                  gap_ms: int | None) -> str | None:
    """Narrow, unverified same-voice P0 grammar hypothesis for timed captions.

    An ending '...' followed by leading '...', or an unterminated
    lowercase continuation, can propose a merge. A dash on ANY line,
    including a single second-speaker dash, must veto whole-cue joins.
    Original words, timings and speaker truth are never changed.
    """
    if type(gap_ms) is not int or gap_ms < -1000:
        return None
    if re.search(r"(?m)^[ \t]*[-–—][ \t]+\S", left):
        return None
    if re.search(r"(?m)^[ \t]*[-–—][ \t]+\S", right):
        return None
    a, b = left.strip(), right.strip()
    if not a or not b:
        return None
    if gap_ms <= 1600 and a.endswith("...") and re.match(r"^\.\.\.\S", b):
        return "matched_ellipsis_source_continuation_unverified"
    if (gap_ms <= 900 and re.match(r"^[a-z]", b)
        and not re.search(r'[.?!…][)\]}\x27"]*$', a)):
        return "lowercase_unfinished_sentence_continuation_unverified"
    return None


def multi_voice_typography(text: str) -> bool:
    return len(structural_speaker_parts(text)) > 1


TEXTUAL_TONE_TAGS = frozenset({"playful", "teasing", "dry", "sarcastic", "exasperated", "defiant", "hesitant", "reassuring", "concerned", "indignant", "incredulous", "angry", "reflective", "stern", "bitter", "contrite", "gentle", "speculative", "mock-solemn", "urgent"})


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
        "weak_or_abstained_cues": 0, "original_audio_verified": False,
        "exact_contextual_internal_handoffs": 0,
        "unlocated_contextual_internal_handoffs": 0,
        "text_only_performance_tone_hypotheses": 0,
        "any_performed_tone_original_audio_verified": False
    }
    overlay = {}
    for cue, record in zip(cues, records):
        n = cue["cue"]
        status = record.get("status")
        mixed = status == "proposed_internal_voice_switch_unverified"
        names = record.get("proposed_ordered_speaker_parts", [])
        role = record.get("proposed_speaker")
        confidence = record.get("confidence")
        offsets = record.get("utf8_or_unicode_split_offsets")
        if offsets is not None and (
            not mixed or not isinstance(offsets, list) or len(offsets) != len(names) - 1
            or any(type(n) is not int for n in offsets)
            or sorted(set(offsets)) != offsets
            or any(not 0 < n < len(cue["text"]) for n in offsets)
        ):
            raise ValueError(ep + f": invalid contextual Unicode handoff offsets for cue {n}")
        if offsets is not None:
            contextual_exact_parts(cue["text"], offsets)
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
        delivery = record.get("provisional_delivery")
        if delivery is not None:
            if (not strong or len(structural_speaker_parts(cue["text"])) != 1
                or not isinstance(delivery, dict)
                or set(delivery) != {"tone", "basis", "original_soundtrack_verified"}
                or delivery.get("tone") not in TEXTUAL_TONE_TAGS
                or not isinstance(delivery.get("basis"), str)
                or not 12 <= len(delivery["basis"]) <= 500
                or delivery.get("original_soundtrack_verified") is not False):
                raise ValueError(ep + f": invalid/unverified contextual delivery proposal at {n}")
            report["text_only_performance_tone_hypotheses"] += 1
        if not mixed and confidence in ("high", "medium") and not strong:
            raise ValueError(ep + ": strong contextual role missing")
        if strong:
            report["high_medium_single_role_hypotheses"] += 1
        elif mixed:
            report["mixed_voice_internal_review_cues"] += 1
            report["exact_contextual_internal_handoffs"] += len(offsets or [])
            report["unlocated_contextual_internal_handoffs"] += int(offsets is None)
        else:
            report["weak_or_abstained_cues"] += 1
        overlay[n] = {
            "provisional_role": role.strip() if strong else None,
            "internal_voice_roles": names, "exact_character_offsets": offsets or [],
            "confidence": confidence,
            "basis": record.get("basis", ""),
            "alternatives": record.get("alternative_speakers", []),
            "textual_delivery": delivery,
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
        delivery = hint.get("textual_delivery")
        internal = hint.get("internal_voice_roles", [])
        offsets = hint.get("exact_character_offsets", [])
        parts = contextual_exact_parts(raw, offsets) if offsets else structural_speaker_parts(raw)
        # Even a confident whole-cue name must never absorb two distinct
        # dash-marked voices; P0 before P1. No guessed subcue timecodes.
        role = None if internal or len(parts) > 1 else (label or candidate)
        suspect = len(parts) > 1 or bool(internal)
        multi += int(suspect)
        named += int(label is not None)
        start, end = cue["start_ms"], cue["end_ms"]
        gap = start - last["source_end_ms"] if last and start is not None and last["source_end_ms"] is not None else None
        scene_hint = last is None or (gap is not None and gap > 12000)
        if scene_hint:
            group += 1
            lines.extend([f"## Passage {group} (dialogue-gap cluster, NOT an observed scene)", ""])
        # Exact in-cue editorial parts have independently proposed entrance
        # and exit roles. Preserve continuity *across* the cue boundary when
        # the proposed entry/exit role matches, without claiming the internal
        # switch was heard. Unlocated/dash-only multi-voice cues still abstain.
        entry_role = internal[0] if offsets else role
        exit_role = internal[-1] if offsets else role
        if last:
            previous_label = last["candidate_exit_voice_role"]
            syntactic = (
                source_syntactic_continuation(last["source_text"], raw, gap)
                if not entry_role and not previous_label and not suspect
                and not last["multiple_voice_dashes"]
                and not last["contextual_unlocated_internal_handoff"]
                else None
            )
            contextual_continuation = bool(
                entry_role and previous_label == entry_role and gap is not None
                and -1000 <= gap <= 2500 and (not suspect or bool(offsets))
                and not last["multiple_voice_dashes"]
                and not last["contextual_unlocated_internal_handoff"]
            )
            continuing = bool(contextual_continuation or syntactic)
            edge_kind = (
                "source_syntactic_provisional_same_voice" if syntactic
                else "same_provisional_entry_voice_candidate_continuation" if continuing and offsets
                else "same_provisional_role_candidate_continuation" if continuing
                else "different_provisional_roles_candidate_change"
                if entry_role and previous_label and entry_role != previous_label
                else "unresolved_turn_boundary"
            )
            edges.append({
                "between_cues": [num - 1, num], "decision": edge_kind,
                "left_provisional_exit_role": previous_label,
                "right_provisional_entry_role": entry_role,
                "source_syntactic_continuation_hypothesis": syntactic,
                "source_audio_verified": False,
                "review_priority": "P0" if edge_kind == "unresolved_turn_boundary" else "P0_CONFIRM"
            })
        else:
            continuing = False
            syntactic = None
        row = {
            "cue": num, "source_text": raw, "source_text_sha256": sha(raw.encode("utf-8")),
            "source_start_ms": start, "source_end_ms": end, "source_label": label,
            "candidate_display_role": role, "contextual_role": candidate,
            "contextual_confidence": hint.get("confidence"),
            "contextual_evidence": hint.get("basis"),
            "contextual_alternatives": hint.get("alternatives", []),
            "contextual_textual_tone": delivery["tone"] if delivery else None,
            "contextual_textual_tone_basis": delivery["basis"] if delivery else None,
            "performed_tone_original_soundtrack_verified": False,
            "contextual_intra_cue_voice_roles": internal,
            "source_label_verified_against_film": False,
            "candidate_role_original_soundtrack_verified": False,
            "multiple_voice_dashes": len(parts) > 1 and not offsets,
            "contextual_unlocated_internal_handoff": bool(internal and not offsets),
            "candidate_entry_voice_role": entry_role, "candidate_exit_voice_role": exit_role,
            "contextual_unicode_split_offsets": offsets,
            "source_speaker_parts": [{
                "source_part_id": f"C{num:05d}.{p['id']}",
                "source_character_start": p["start"],
                "source_character_end": p["end"],
                "source_text_sha256": p["source_text_sha256"],
                "provisional_part_role": internal[i] if offsets else None,
                "provisional_part_role_evidence": "contextual_lexical_hypothesis_not_audio_verified" if offsets else None,
                "proposed_voice_change_before_part": p["source_indicates_possible_speaker_change"],
                "candidate_split_basis": p.get("split_basis", "caption_leading_dash"),
                "original_audio_boundary_verified": False,
                "original_audio_subcue_time_ms": None,
            } for i, p in enumerate(parts)],
            "passage_candidate": group, "provisional_continuation_of_previous": continuing,
            "source_syntactic_continuation_hypothesis": syntactic,
            "original_dialogue_sha256": source_sha,
        }
        rows.append(row)
        if len(parts) > 1:
            # One visual character heading per *proposed* source speaker part.
            # An unordered/single contextual cue label cannot prove part roles.
            for i, p in enumerate(parts):
                heading = (f"{internal[i]} (contextual lexical turn hypothesis; audio unverified)"
                           if offsets else
                           f"UNIDENTIFIED VOICE (caption-marked P0 candidate {p['id']}; audio unverified)")
                # The first provisional voice may be a continuation of the
                # preceding cue. A second in-cue voice always gets a heading.
                if not (i == 0 and continuing and offsets):
                    lines.extend(["### " + heading, ""])
                lines.extend("    " + line for line in p["text"].split("\n"))
                lines.append("")
        else:
            if not continuing:
                if internal:
                    heading = ("MULTIPLE UNIDENTIFIED VOICES (context proposes " +
                               " / ".join(internal) + "; internal boundary unverified)")
                else:
                    heading = (role or "UNIDENTIFIED VOICE") + (
                        " (source label, unverified)" if label else
                        " (contextual hypothesis, unverified)" if candidate else "")
                lines.extend(["### " + heading, ""])
            if delivery:
                # A textual suggestion, never a claim about audible acting.
                lines.extend([f"*(Textual delivery hypothesis: {delivery['tone']}; original performance unverified.)*", ""])
            lines.extend("    " + line for line in raw.split("\n"))
            lines.append("")
        last = row
    lines.extend([
        "## Source and editorial limits", "",
        f"- Source edition: `{manifest['version_id']}`; {len(captions)} of {len(captions)} cues present.",
        f"- {named} cues have source-explicit voice labels; {len(captions) - named} have no explicit source role.",
        f"- {context_report['high_medium_single_role_hypotheses'] if context_report else 0} high/medium contextual whole-cue names are hypotheses, NOT source-heard identities.",
        f"- {multi} cues have possible internal voice changes (dash-marked or context-only).",
        f"- {sum(len(r['source_speaker_parts']) - 1 for r in rows)} candidate within-cue boundaries (dash or source-exact contextual) are reversible speaker parts.",
        f"- {sum(len(r['contextual_unicode_split_offsets']) for r in rows)} manually reasoned contextual exact-word handoffs carry provisional part-specific names, never witnessed voices.",
        f"- {sum(bool(r['contextual_textual_tone']) for r in rows)} textual P2 delivery suggestions are NOT witnessed original performances.",
        f"- {len(edges)} adjacent boundaries remain original-audio unverified.",
        f"- {sum(bool(r['source_syntactic_continuation_hypothesis']) for r in rows)} narrow source-punctuation candidate same-voice joins are unverified; mixed-dash cues and untimed sources abstain.",
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
        "proposed_source_speaker_parts": sum(len(r["source_speaker_parts"]) for r in rows),
        "source_dash_candidate_p0_boundaries": sum(
            len(r["source_speaker_parts"]) - 1 for r in rows
            if not r["contextual_unicode_split_offsets"]),
        "source_contextual_exact_p0_boundaries": sum(
            len(r["contextual_unicode_split_offsets"]) for r in rows),
        "contextual_provisional_named_parts": sum(
            bool(p["provisional_part_role"]) for r in rows for p in r["source_speaker_parts"]),
        "text_only_contextual_delivery_proposals": sum(bool(r["contextual_textual_tone"]) for r in rows),
        "original_audio_performed_delivery_accepted": False,
        "adjacent_p0_unverified": len(edges),
        "source_syntactic_p0_provisional_continuations": sum(
            bool(r["source_syntactic_continuation_hypothesis"]) for r in rows),
        "provisional_passages_not_verified_scenes": group,
        "original_dialogue_sha256": source_sha,
        "source_has_timecodes": manifest["timecoded"],
        "actual_av_verified": False, "independent_editorial_acceptance": False,
    })


def apply_existing_original_audio_p0(root: Path, ep: str, source_sha: str,
                                     canonical_text: str, edges: list, rows: list) -> tuple[dict, list]:
    """Attach already-measured original-soundtrack similarities to exact P0 edges.

    Numeric acoustic features only prioritize re-listening. They never
    authenticate performed turns, names, joins, or independent acceptance.
    Stale script-specific reports are excluded rather than applied blindly.
    """
    from episode_finish import VIDEO_SHA
    path = (root / "saved-private/episode-finish-current" /
            (ep + "-original-audio-p0p1-evidence.json"))
    if not path.is_file():
        return {"status": "source_audio_report_absent", "matched_p0_pairs": 0,
                "priority_original_audio_p0_conflicts": 0,
                "previously_unknown_original_voice_windows": 0}, []
    raw = path.read_bytes()
    report = json.loads(raw)
    if (report.get("schema") != "night-court-canonical-original-audio-p0-p1-evidence/1"
        or report.get("episode_id") != ep
        or report.get("immutable_original_dialogue_sha256") != source_sha
        or report.get("original_video_sha256") != VIDEO_SHA[ep]
        or report.get("independent_performed_turns_accepted") != 0
        or report.get("independent_original_actor_voice_accepted") != 0
        or report.get("original_video_watched_by_human") is not False
        or report.get("provisional_role_holdout_threshold_passed") is not False):
        raise ValueError(ep + ": existing original-soundtrack report is unsafe or has wrong source")
    base = {
        "file": str(path.relative_to(root)), "sha256": sha(raw),
        "original_video_sha256": VIDEO_SHA[ep], "original_audio_model_only": True,
        "speaker_or_turn_audio_accepted": False,
    }
    if report.get("canonical_manuscript_sha256") != sha(canonical_text.encode("utf-8")):
        return {**base, "status": "stale_canonical_manuscript_not_applied",
                "matched_p0_pairs": 0, "priority_original_audio_p0_conflicts": 0,
                "previously_unknown_original_voice_windows": 0}, []
    pairs = report.get("adjacent_P0_original_audio_voice_similarity")
    if not isinstance(pairs, list) or len(pairs) > 1500:
        raise ValueError(ep + ": malformed P0 soundtrack comparison")
    by_boundary = {tuple(x["between_block_ids"]): x for x in edges}
    matched = set()
    focus = 0
    for pair in pairs:
        key = (pair.get("source_left"), pair.get("source_right"))
        score = pair.get("machine_acoustic_voice_similarity")
        if (key in matched or not isinstance(score, (int, float))
            or type(score) is bool or not -1 <= score <= 1
            or pair.get("source_audio_p0_performed_boundary_independently_verified") is not False
            or type(pair.get("provisional_display_join")) is not bool):
            raise ValueError(ep + ": malformed original-audio adjacent pair")
        matched.add(key)
        edge = by_boundary.get(key)
        if edge is None:
            # The source model only sampled usable clean, genuinely adjacent
            # excerpts; do not graft arbitrary non-adjacent data onto edges.
            continue
        if pair["provisional_display_join"] != edge["provisional_continuation"]:
            raise ValueError(ep + ": acoustic report disagrees with source-bound display groups")
        # Heuristic only, NOT a learned calibrated same-speaker probability.
        discrepancy = (score <= .55 if edge["provisional_continuation"]
                       else score >= .80)
        edge["original_soundtrack_machine_similarity"] = score
        edge["acoustic_same_voice_model_hint"] = (
            "investigate_provisional_join" if discrepancy and edge["provisional_continuation"]
            else "investigate_provisional_split" if discrepancy
            else "no_priority_signal_unverified"
        )
        edge["original_audio_performed_boundary_verified"] = False
        edge["original_audio_candidate_model_report_sha256"] = base["sha256"]
        if discrepancy:
            edge["review_priority"] = "P0_FOCUS_MODEL_CONTRADICTION"
            focus += 1
    # P1 comes after P0. These acoustic matches were NOT calibrated well
    # enough to name a speaker: only re-listening questions, never screenplay
    # labels. Crucially S09's source paragraphs are UNTIMED; the independently
    # recorded original-video seek range is not a transcript timestamp.
    unknown = report.get("unknown_original_soundtrack_proposals")
    if not isinstance(unknown, list) or len(unknown) > len(rows):
        raise ValueError(ep + ": missing or unbounded unknown-voice model proposals")
    by_id = {row["reading_block_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError(ep + ": duplicate P1 source reading block")
    p1_review = []
    seen_voices = set()
    for cand in unknown:
        key = cand.get("source_reading_block_id")
        row = by_id.get(key)
        ref = cand.get("source_ref")
        score = cand.get("speaker_similarity")
        runner = cand.get("runner_up_similarity")
        margin = cand.get("voice_model_margin")
        source_timing = cand.get("source_original_timecode_ms")
        s09_seek = cand.get("unverified_s09_original_audio_seek_hint_ms")
        if (not isinstance(cand, dict) or key in seen_voices or row is None
            or row["provisional_role"] is not None
            or not isinstance(ref, str) or ref not in row["original_source_part_refs"]
            or not isinstance(cand.get("uncertified_best_role"), str)
            or not cand["uncertified_best_role"].strip()
            or cand.get("acoustic_candidate") is not None
            or cand.get("actor_voice_original_soundtrack_independently_verified") is not False
            or cand.get("global_and_role_holdout_pass") is not False
            or any(type(v) not in (int, float) or not 0 <= v <= 1
                   for v in (score, runner, margin))
            or abs((score - runner) - margin) > .00003
            or (ep == "S01E01" and (source_timing is None or s09_seek is not None))
            or (ep == "S09E19" and (source_timing is not None or s09_seek is None))):
            raise ValueError(ep + ": malformed or falsely certified P1 source voice")
        seek = source_timing if ep == "S01E01" else s09_seek
        if (not isinstance(seek, list) or len(seek) != 2
            or any(type(t) is not int for t in seek)
            or not 0 <= seek[0] < seek[1] <= 7_200_000):
            raise ValueError(ep + ": invalid source audio listening envelope")
        seen_voices.add(key)
        p1_review.append({
            "reading_block_id": key, "source_original_part_ref": ref,
            "source_exact_dialogue_sha256": row["source_text_sha256"],
            "uncertified_machine_nearest_role": cand["uncertified_best_role"],
            "machine_nearest_voice_similarity": score,
            "machine_runner_up_similarity": runner, "machine_margin": margin,
            "low_discrimination_requires_extra_skepticism": margin < .05,
            "source_caption_time_ms": source_timing,
            "unverified_original_movie_seek_hint_ms": s09_seek,
            "source_video_sha256": base["original_video_sha256"],
            "model_source_report_sha256": base["sha256"],
            "original_soundtrack_heard_by_editor": False,
            "actual_character_voice_verified": False,
            "eligible_for_automatic_role_promotion": False,
            "review_priority": "P1_UNIDENTIFIED_ORIGINAL_AUDIO_LISTEN",
        })
    p1_review.sort(key=lambda item: (
        item["unverified_original_movie_seek_hint_ms"] or item["source_caption_time_ms"],
        item["reading_block_id"]))
    return {
        **base, "status": "canonical_source_audio_model_linked",
        "model_measured_adjacent_pairs": len(pairs),
        "matched_p0_pairs": sum("original_soundtrack_machine_similarity" in e for e in edges),
        "priority_original_audio_p0_conflicts": focus,
        "model_similarity_thresholds_only_review_triage_not_calibrated": True,
        "previously_unknown_original_voice_windows": len(p1_review),
        "unknown_voice_model_automatically_promoted": 0,
    }, p1_review


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
    acoustic, p1_review = apply_existing_original_audio_p0(root, ep, witness, text, edges, rows)
    count = layout["episodes"][ep]
    return text, rows, edges, {
        "original_audio_p0_triage": acoustic,
        "_source_audio_p1_review_queue": p1_review,
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


def original_film_visual_model_review(root: Path, ep: str) -> tuple[dict, list]:
    """Reuse only source-checked original video observations as *review questions*.

    Two seconds of model vision is nowhere near whole-film coverage, and its
    scene/action descriptions are not separately witnessed stage directions.
    Do not insert the text into the production screenplay automatically.
    """
    if ep not in PILOTS:
        return {"status": "no_original_film_visual_model_evidence", "sampled_windows": 0}, []
    from preserve_original_qwen_model_reports import (
        review_original_qwen_report, validate_bundle
    )
    folder = root / "saved-private/episode-finish-current"
    report_path = folder / f"{ep}-original-qwen-visual-proposals.json"
    pending_path = folder / f"{ep}-original-qwen-review-pending.json"
    metrics_path = folder / f"{ep}-original-qwen-safe-metrics.json"
    if not any(p.exists() for p in (report_path, pending_path, metrics_path)):
        return {"status": "no_original_film_visual_model_evidence", "sampled_windows": 0}, []
    if not all(p.is_file() for p in (report_path, pending_path, metrics_path)):
        raise ValueError(ep + ": partial original film vision evidence, refusing unlinked proposal")
    # The source private publisher has validated the exact model-proposal
    # bundle; recheck all source film, model, deferred reviews and report SHA
    # before referencing it from the one-click final product review queue.
    import tempfile
    with tempfile.TemporaryDirectory(prefix="night-court-qwen-sha-reverify-") as scratch:
        working = Path(scratch)
        for dest, src in (
            (f"nc-qwen-original-{ep}.json", report_path),
            (f"nc-qwen-pending-{ep}.json", pending_path),
            (f"nc-qwen-safe-metrics-{ep}.json", metrics_path),
        ):
            (working / dest).write_bytes(src.read_bytes())
        validate_bundle(ep, working)
    raw = report_path.read_bytes()
    original = json.loads(raw)
    windows = review_original_qwen_report(ep, original)
    pointers = [{
        "source_original_video_sha256": original["source_video_sha256"],
        "model_id": original["model_id"],
        "model_revision": original["model_revision"],
        "source_window_ms": [row["start_ms"], row["end_ms"]],
        "window_id": row["id"],
        "visual_model_status": row["status"],
        "unverified_description": row["model_hypothesis"],
        "original_video_human_verified": False,
        "whole_episode_picture_analyzed": False,
        "original_stage_direction_accepted": False,
        "source_report_sha256": sha(raw),
        "review_priority": "P3_P4_SOURCE_VIDEO_CONFIRMED_ONLY_AFTER_REVIEW",
    } for row in windows if row.get("model_hypothesis") is not None]
    return {
        "status": "original_source_model_proposals_unverified",
        "file": str(report_path.relative_to(root)),
        "sha256": sha(raw),
        "sampled_windows": len(windows),
        "model_review_questions": len(pointers),
        "original_source_video_sha256": original["source_video_sha256"],
        "model_load_seconds": original["model_load_seconds"],
        "total_model_inference_seconds": round(sum(
            row.get("inference_seconds", 0) for row in windows), 3),
        "human_film_reviewer_accepted": False,
        "whole_episode_video_covered": False,
    }, pointers


def construct(root: Path, ep: str, index: dict):
    if ep in PILOTS:
        script, rows, edges, details = pilot_episode(root, ep, index)
    else:
        script, rows, edges, details = generic_episode(root, ep, index)
    if not rows or not script.strip():
        raise ValueError(ep + ": empty script or source lineage")
    visual_evidence, visual_review = original_film_visual_model_review(root, ep)
    raw = script.encode("utf-8")
    records = json_lines(rows)
    reviews = json_text({"schema": SCHEMA, "episode_id": ep,
                         "priorities": ["P0_turns", "P1_identity", "P2_delivery",
                                        "P3_props_wardrobe", "P4_actions", "P5_coarse_time"],
                         "all_original_audio_boundaries_unverified": True,
                         "original_film_visual_model_only_review": visual_review,
                         "boundary_review_questions": edges,
                         "original_audio_model_p1_unknown_voice_review": details.get("_source_audio_p1_review_queue", []),
                         "original_audio_model_priority_p0": [{
                             "between_block_ids": x["between_block_ids"],
                             "machine_acoustic_voice_similarity": x["original_soundtrack_machine_similarity"],
                             "possible_issue": x["acoustic_same_voice_model_hint"],
                             "film_heard_turn_confirmed": False,
                         } for x in sorted(
                             [z for z in edges if z.get("review_priority") == "P0_FOCUS_MODEL_CONTRADICTION"],
                             key=lambda z: (
                                 z["original_soundtrack_machine_similarity"] if z["provisional_continuation"]
                                 else -z["original_soundtrack_machine_similarity"],
                                 z["between_block_ids"][0]))],
                         "review_internal_voice_changes": [x.get("cue") for x in rows
                                                          if x.get("multiple_voice_dashes") or
                                                          x.get("contextual_intra_cue_voice_roles")],
                         "within_cue_structural_turn_questions": [{
                             "source_cue": row["cue"],
                             "left_part": left["source_part_id"],
                             "right_part": right["source_part_id"],
                             "source_character_boundary": right["source_character_start"],
                             "candidate_split_basis": right["candidate_split_basis"],
                             "boundary_proposed_by_caption_dash": right["candidate_split_basis"] == "caption_leading_dash",
                             "source_audio_performed_turn_verified": False,
                             "priority": "P0",
                         } for row in rows if "source_speaker_parts" in row
                           for left, right in zip(row["source_speaker_parts"], row["source_speaker_parts"][1:])],
                         "textual_delivery_p2_review": [{
                             "source_cue": x["cue"], "provisional_role": x["candidate_display_role"],
                             "provisional_text_tone": x["contextual_textual_tone"],
                             "dialogue_context_basis": x["contextual_textual_tone_basis"],
                             "original_audio_tone_verified": False,
                             "eligible_for_performed_stage_direction": False,
                             "priority": "P2_TEXTUAL_DELIVERY_VERIFY_IN_ORIGINAL_FILM",
                         } for x in rows if x.get("contextual_textual_tone")],
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
        **{key: value for key, value in details.items() if not key.startswith("_")},
        "original_film_visual_model_evidence": visual_evidence,
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
