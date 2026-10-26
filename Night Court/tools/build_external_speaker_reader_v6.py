#!/usr/bin/env python3
"""Produce S01E01/S09E19 speaker-improved *private* v6 reader scripts.

These are source-exact editorial overrides, NOT actual original-audio identity
certifications. One original S09 paragraph contains two proposed voices.
Source held caption files and the tracked v5 manuscripts never change.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from build_pilot_character_evidence import INDEXES, records_for_episode
from build_pilot_fan_beat_cards import ROOT, load_witness

LEDGER = ROOT / "research/pilot-speaker-external-quote-improvements-v1.json"
V5 = {
    ep: ROOT / "seasons" / ep[:3] / ep /
        "derived/additional-original-film-staged-reader-v5/screenplay-extra-observed-business.md"
    for ep in ("S01E01", "S09E19")
}
SCHEMA = "night-court-original-pilot-external-attribution-application/1"
BASELINE_NAMED = 487
BASELINE_UNKNOWN = 264
BASELINE_SOURCE_UNITS = 751


def sha(binary: bytes) -> str:
    return hashlib.sha256(binary).hexdigest()


def cue_number(ref: str) -> int:
    match = re.fullmatch(r"C(\d{3})\.1", ref)
    if not match:
        raise ValueError("Only single-part original caption source referrals supported")
    return int(match.group(1))


def verify_overrides(root: Path, ledger: dict, existing: dict | None = None) -> list[dict]:
    if (ledger.get("schema") !=
            "night-court-episode-specific-external-quote-speaker-improvements/1"
        or ledger.get("original_captions_unchanged") is not True
        or ledger.get("original_audio_reviewed") is not False):
        raise ValueError("Unsafe or unexpected external quote editorial ledger")
    if set(ledger.get("episodes", {})) != set(V5):
        raise ValueError("Wrong pilot edition roster")
    if existing is None:
        existing = {ep: records_for_episode(root, ep) for ep in V5}
    by_ep = {}
    for ep in V5:
        meta, cues = load_witness(root, ep)
        if meta["sha256"] != ledger["episodes"][ep]["source_sha256"]:
            raise ValueError("External quote ledger attached to a changed original source")
        if (ep == "S09E19") != (not meta["timecoded"]):
            raise ValueError("Original S09 transcript timecoded without original evidence")
        by_ep[ep] = (cues, {x["source_reading_ref"]: x for x in existing[ep]})
    seen = set()
    validated = []
    for item in ledger.get("overrides", []):
        ep, ref = item.get("episode_id"), item.get("source_ref")
        if ep not in by_ep or (ep, ref) in seen:
            raise ValueError("Unknown or duplicated source speaker override")
        seen.add((ep, ref))
        cues, previous = by_ep[ep]
        n = cue_number(ref)
        if n < 1 or n > len(cues):
            raise ValueError("Invalid original cue for speaker proposal")
        original = item.get("original_cue_text")
        if not isinstance(original, str) or original != cues[n-1]["text"]:
            raise ValueError("Exact original source paragraph drift")
        prior = previous.get(ref)
        if (prior is None or prior["candidate_role"] is not None
            or prior["caption_text"] != original
            or item.get("legacy_candidate") != "UNIDENTIFIED SPEAKER"):
            raise ValueError("Cannot overwrite an existing named role or nonexact source block")
        spans = item.get("proposed_spans")
        if not isinstance(spans, list) or not spans or len(spans) > 2:
            raise ValueError("Expected one or two proposed speaker subspans")
        position = 0
        rebuilt = []
        for index, part in enumerate(spans, 1):
            start, end = part.get("start"), part.get("end")
            role = part.get("role")
            if (type(start) is not int or type(end) is not int
                or start < position or end <= start or end > len(original)
                or not isinstance(role, str) or not role
                or part.get("basis") not in (
                    "episode_specific_external_exact_quote_attribution",
                    "episode_specific_external_paraphrased_question_in_same_conversation",
                    "episode_specific_external_quote_exact_attribution",
                    "syntactic_continuation_from_provisionally_attributed_preceding_C033"
                )
                or not isinstance(part.get("reader_label"), str)
                or not part["reader_label"].startswith(role + " · ")
                or "UNVERIFIED" not in part["reader_label"]):
                raise ValueError("Invalid or overconfident speaker segment")
            if original[position:start].strip():
                raise ValueError("Speaker segment skipped non-whitespace source characters")
            text = original[start:end]
            if not text.strip():
                raise ValueError("Empty speaker segment")
            rebuilt.append({
                "schema": SCHEMA,
                "episode_id": ep, "source_ref": ref,
                "source_cue_sha256": sha(original.encode("utf-8")),
                "source_witness_sha256": ledger["episodes"][ep]["source_sha256"],
                "proposed_segment_id": f"{ep}:{ref}:p{index}",
                "start_char": start, "end_char": end,
                "text": text, "candidate_role": role,
                "reader_label": part["reader_label"],
                "evidence_basis": part["basis"],
                "external_episode_quote_url": ledger["episodes"][ep]["external_url"],
                "source_quote_dependency_possible": True,
                "original_soundtrack_verified": False,
                "character_identity_status": "external_or_context_editorial_proposal",
                "original_timecoded": ep == "S01E01",
                "original_caption_unit_split": len(spans) > 1,
            })
            position = end
        if original[position:].strip():
            raise ValueError("Uncovered original dialogue after proposed speaker subspans")
        if (ep == "S09E19" and ref == "C034.1"):
            if (len(rebuilt) != 2 or rebuilt[0]["candidate_role"] != "ROZ RUSSELL"
                or rebuilt[1]["candidate_role"] != "CHRISTINE SULLIVAN"):
                raise ValueError("Unreviewed or misplaced two-voice original paragraph")
        validated.extend(rebuilt)
    if (len(seen) != 3 or len(validated) != 4
        or {ref for ep, ref in seen if ep == "S01E01"} != {"C142.1"}
        or {ref for ep, ref in seen if ep == "S09E19"} != {"C027.1", "C034.1"}):
        raise ValueError("Missing or newly invented original dialogue proposal")
    return validated


def improved_readers(root: Path, ledger: dict, entries: list[dict]) -> dict[str, str]:
    readers = {}
    for ep in V5:
        path = root / V5[ep].relative_to(ROOT)
        doc = path.read_text("utf-8")
        if ledger["episodes"][ep]["source_sha256"] not in doc:
            raise ValueError("Original v5 screenplay not tied to held caption edition")
        for item in ledger["overrides"]:
            if item["episode_id"] != ep:
                continue
            old = ("UNIDENTIFIED SPEAKER · UNRESOLVED SOURCE VOICE\n"
                   + item["original_cue_text"])
            selected = [part for part in entries
                        if part["episode_id"] == ep and part["source_ref"] == item["source_ref"]]
            replacement = "\n\n".join(
                part["reader_label"] + "\n" + part["text"] for part in selected
            )
            if doc.count(old) != 1:
                raise ValueError("V5 reader lacks unique original UNKNOWN cue for " + item["source_ref"])
            doc = doc.replace(old, replacement, 1)
        if ep == "S09E19" and "transcript is UNTIMED" not in doc:
            raise ValueError("No original S09 timing caveat in corrected reader")
        readers[ep] = doc
    return readers


def create(root: Path, ledger_path: Path, output: Path) -> dict:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private source-bearing speaker materials cannot be written into the repo")
    binary = ledger_path.read_bytes()
    ledger = json.loads(binary)
    verified = verify_overrides(root, ledger)
    scripts = improved_readers(root, ledger, verified)
    source_cues_resolved = {(part["episode_id"], part["source_ref"]) for part in verified}
    if len(source_cues_resolved) != 3:
        raise ValueError("Must improve exactly three original caption source units")
    overview = {
        "schema": SCHEMA,
        "external_ledger_sha256": sha(binary),
        "original_source_speaking_units": BASELINE_SOURCE_UNITS,
        "original_provisional_named_source_units": BASELINE_NAMED,
        "original_unknown_source_units": BASELINE_UNKNOWN,
        "new_provisional_named_source_units": BASELINE_NAMED + len(source_cues_resolved),
        "remaining_unidentified_source_units": BASELINE_UNKNOWN - len(source_cues_resolved),
        "original_cue_units_with_new_editorial_role_proposals": len(source_cues_resolved),
        "provisional_speaker_segments_from_these_cues": len(verified),
        "previously_unsplit_two_speaker_original_paragraphs_represented": 1,
        "original_audio_speaker_identities_verified_by_this_change": 0,
        "full_episode_film_reviewed": False,
        "unverified_v5_role_labels_left_unchanged_except_explicit_overrides": True,
        "pilot_scripts": {
            ep: {
                "generated_path": f"{ep}/screenplay-external-speakers-v6.md",
                "sha256": sha(doc.encode("utf-8")),
                "original_v5_source_path": str(V5[ep].relative_to(ROOT)),
            } for ep, doc in scripts.items()
        },
        "additional_review_flags": ledger.get("additional_review_flags", []),
    }
    output.mkdir(parents=True, exist_ok=True)
    for ep, content in scripts.items():
        (output / ep).mkdir(parents=True, exist_ok=True)
        (output / ep / "screenplay-external-speakers-v6.md").write_text(content, "utf-8")
    (output / "speaker-improvement-overrides.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in verified), "utf-8")
    (output / "speaker-improvement-manifest.json").write_text(
        json.dumps(overview, indent=2, ensure_ascii=False, sort_keys=True) + "\n", "utf-8")
    return overview


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--ledger", type=Path, default=LEDGER)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    summary = create(a.root, a.ledger, a.output)
    print(f"{summary['original_cue_units_with_new_editorial_role_proposals']} original source "
          f"cues newly given provisional names; {summary['remaining_unidentified_source_units']} "
          "source units unresolved; private v6 readers saved without source text in logs")


if __name__ == "__main__":
    main()
