#!/usr/bin/env python3
"""Source-traceable paired visual model review yield and cost report.

Requires already produced video model JSON *and* corresponding explicit
reviewer-stage audit JSON. No media, model weights, FTP or credentials.
Reviewer acceptance is editorial, NEVER independent episode certification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

MODEL_SCHEMA = "night-court-headless-video-description/1"
AUDIT_SCHEMA = "night-court-reviewed-visual-staging/1"
OUT_SCHEMA = "night-court-paired-visual-review-yield/1"
MAX_INPUT = 200_000
MAX_MODELS = 4
SHA = re.compile(r"[0-9a-f]{64}\Z")
LABEL = re.compile(r"[A-Za-z0-9_.-]{1,40}\Z")
VERDICTS = ("accepted", "corrected", "rejected", "deferred")
FIELDS = ("setting", "camera", "people_and_positions", "actions", "props",
          "entrances_exits", "physical_comedy", "reactions", "uncertainty",
          "proposed_stage_direction")


def check_sha(value):
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def read_limited(path):
    if not isinstance(path, Path) or not path.is_file() or path.stat().st_size > MAX_INPUT:
        raise ValueError("Missing or oversized review input")
    raw = path.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def validated_pair(label, model, model_sha, audit):
    if not isinstance(label, str) or not LABEL.fullmatch(label):
        raise ValueError("Invalid model label")
    if model.get("schema") != MODEL_SCHEMA or audit.get("schema") != AUDIT_SCHEMA:
        raise ValueError("Incompatible model/audit schemas")
    if model.get("script_or_claim_independently_accepted") is not False or audit.get("full_episode_av_certified") is not False:
        raise ValueError("Visual evidence may not self-certify an episode")
    if audit.get("model_outputs_were_not_automatically_accepted") is not True:
        raise ValueError("Review must explicitly prohibit automatic model acceptance")
    episode = model.get("episode_id")
    sha = model.get("source_video_sha256")
    if not isinstance(episode, str) or not re.fullmatch(r"S0[1-9]E[0-9]{2}", episode):
        raise ValueError("Invalid original-series episode")
    if not check_sha(sha) or model.get("verified_source_sha256") != sha:
        raise ValueError("Model lacks verified source identity")
    if audit.get("episode_id") != episode or audit.get("source_video_sha256") != sha or audit.get("model_report_sha256") != model_sha:
        raise ValueError("Reviewer audit does not match exact model report")
    reviewer = audit.get("reviewer_id")
    if not isinstance(reviewer, str) or not LABEL.fullmatch(reviewer):
        raise ValueError("Missing reviewer identity")
    windows = model.get("windows")
    if not isinstance(windows, list) or not 1 <= len(windows) <= 12:
        raise ValueError("Unbounded video windows")
    seen, clip_map, proposed = set(), {}, set()
    inference = 0.0
    clip_decode = 0.0
    for window in windows:
        key = window.get("id")
        start, stop = window.get("start_ms"), window.get("end_ms")
        if not isinstance(key, str) or not LABEL.fullmatch(key) or key in seen:
            raise ValueError("Invalid/duplicate model window")
        seen.add(key)
        if type(start) is not int or type(stop) is not int or not 0 <= start < stop:
            raise ValueError("Invalid model window timestamps")
        if window.get("independently_accepted") is not False or window.get("source_AV_human_review_done") is not False:
            raise ValueError("Unreviewed model input falsely accepted")
        if window.get("candidate_cut_crossing") is not False:
            raise ValueError("Unverified/cut-spanning continuous action window")
        clip_map[key] = (start, stop)
        candidate = window.get("model_hypothesis")
        if candidate is not None:
            if not isinstance(candidate, dict) or set(candidate) != set(FIELDS):
                raise ValueError("Invalid model visual claims")
            for field, value in candidate.items():
                if not isinstance(value, str) or len(value) > 1200:
                    raise ValueError("Unbounded model prose")
                if value.strip():
                    proposed.add((key, field))
        for metric, attr in (("inference_seconds", "inference"), ("decode_seconds", "decode")):
            value = window.get(metric)
            if type(value) not in (int, float) or not 0 <= value <= 3600:
                raise ValueError("Missing model runtime measurement")
            if attr == "inference":
                inference += value
            else:
                clip_decode += value
    decisions = audit.get("field_decisions")
    if not isinstance(decisions, list) or len(decisions) > 120:
        raise ValueError("Invalid editor decision count")
    by_key = {}
    for decision in decisions:
        wid, field, verdict = decision.get("window_id"), decision.get("field"), decision.get("verdict")
        key = (wid, field)
        if wid not in clip_map or field not in FIELDS or key in by_key or verdict not in VERDICTS:
            raise ValueError("Duplicate/invalid atomic reviewer decision")
        if decision.get("source_video_sha256") != sha or decision.get("source_window_ms") != list(clip_map[wid]):
            raise ValueError("Review decision source-time mismatch")
        if verdict != "deferred" and decision.get("direct_original_video_review_attested") is not True:
            raise ValueError("Missing actual source-video reviewer attestation")
        if verdict == "accepted" and key not in proposed:
            raise ValueError("Reviewer accepted a model claim that was never proposed")
        by_key[key] = verdict
    counted = {v: sum(x == v for x in by_key.values()) for v in VERDICTS}
    stage_notes = audit.get("editorial_stage_directions")
    if not isinstance(stage_notes, list):
        raise ValueError("Missing editorial stage notes")
    expected_stage = {k[0] for k, v in by_key.items()
                      if k[1] == "proposed_stage_direction" and v in ("accepted", "corrected")}
    if len(stage_notes) != len(expected_stage) or {x.get("window_id") for x in stage_notes} != expected_stage:
        raise ValueError("Stage appendix and audited reviewer decisions disagree")
    usable_stage = len(stage_notes)
    wall = model.get("wall_seconds")
    if type(wall) not in (int, float) or not 0 <= wall <= 100_000:
        raise ValueError("Missing total wall-time metric")
    return {
        "label": label, "episode_id": episode, "source_video_sha256": sha,
        "reviewer_id": reviewer,
        "windows": clip_map, "proposed_fields": proposed, "decisions": by_key,
        "decision_counts": counted, "proposed_nonempty_fields": len(proposed),
        "reviewed_fields": len(by_key),
        "usable_reviewed_stage_directions": usable_stage,
        "source_video_model_inference_seconds": round(inference, 3),
        "temporary_video_decode_seconds": round(clip_decode, 3),
        "observed_process_wall_seconds": round(wall, 3),
        "output_status": "reviewer_attested_not_independently_certified",
    }


def summarize(pairs):
    if not isinstance(pairs, list) or not 1 <= len(pairs) <= MAX_MODELS:
        raise ValueError("Expected 1-4 compared models")
    if len({p["label"] for p in pairs}) != len(pairs):
        raise ValueError("Duplicated model label")
    source = {(p["episode_id"], p["source_video_sha256"]) for p in pairs}
    if len(source) != 1:
        raise ValueError("Comparisons must use the exact same original film")
    common_windows = set.intersection(*(set(p["windows"].items()) for p in pairs))
    common_ids = {w for w, _ in common_windows}
    common_reviewed = set.intersection(*(set(k for k,v in p["decisions"].items()
                                         if v != "deferred" and k[0] in common_ids) for p in pairs))
    comparable_reviewers = len({p["reviewer_id"] for p in pairs}) == 1
    rows = []
    for p in pairs:
        counts = p["decision_counts"]
        source_checked = sum(counts[k] for k in ("accepted", "corrected", "rejected"))
        shared = {k: p["decisions"][k] for k in common_reviewed}
        stage = p["usable_reviewed_stage_directions"]
        rows.append({
            "label": p["label"], "reviewer_id": p["reviewer_id"],
            "candidate_windows": len(p["windows"]), "model_nonempty_fields": p["proposed_nonempty_fields"],
            "reviewed_fields": p["reviewed_fields"], "source_reviewed_fields": source_checked,
            "unresolved_deferred_fields": counts["deferred"],
            "accepted_model_fields": counts["accepted"],
            "corrected_model_fields": counts["corrected"],
            "rejected_model_fields": counts["rejected"],
            "accepted_fraction_of_source_reviewed": round(counts["accepted"]/source_checked, 6) if source_checked else None,
            "unsupported_rejection_fraction": round(counts["rejected"]/source_checked, 6) if source_checked else None,
            "usable_reviewed_stage_directions": stage,
            "paired_review_fields": len(common_reviewed),
            "paired_accepted": sum(v=="accepted" for v in shared.values()),
            "paired_corrected": sum(v=="corrected" for v in shared.values()),
            "paired_rejected": sum(v=="rejected" for v in shared.values()),
            "clip_inference_seconds": p["source_video_model_inference_seconds"],
            "clip_decode_seconds": p["temporary_video_decode_seconds"],
            "total_process_wall_seconds": p["observed_process_wall_seconds"],
            "process_seconds_per_usable_stage_direction": round(p["observed_process_wall_seconds"]/stage, 3) if stage else None,
        })
    return {
        "schema": OUT_SCHEMA,
        "episode_id": pairs[0]["episode_id"],
        "source_video_sha256": pairs[0]["source_video_sha256"],
        "model_count": len(pairs),
        "paired_identical_time_windows": len(common_windows),
        "paired_source_reviewed_field_count": len(common_reviewed),
        "same_reviewer_id": comparable_reviewers,
        "fair_comparison_supported": len(pairs)>1 and bool(common_reviewed) and comparable_reviewers,
        "models": rows,
        "episode_independently_av_certified": False,
        "calibrated_visual_model_accuracy_claimed": False,
        "notice": "Only reviewer-attested proposal yield; not a blinded population accuracy estimate. Do not rank when reviewed fields/windows differ.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comparison", type=Path, required=True,
                        help="JSON with [{label,model_report,review_audit}] pairs")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve() == args.comparison.resolve():
        parser.error("Refusing to overwrite source or existing output")
    manifest, _ = read_limited(args.comparison)
    if manifest.get("schema") != "night-court-review-yield-comparison-input/1":
        raise ValueError("Unknown comparison manifest")
    records = manifest.get("models")
    if not isinstance(records, list) or not 1 <= len(records) <= MAX_MODELS:
        raise ValueError("Expected 1-4 source-linked models")
    base = args.comparison.parent
    pairs = []
    for record in records:
        label = record.get("label")
        paths = []
        for name in ("model_report", "review_audit"):
            value = record.get(name)
            if not isinstance(value, str) or not value or len(value)>300:
                raise ValueError("Missing model or reviewer report path")
            path = (base / value).resolve()
            if path == args.output.resolve():
                raise ValueError("Output would overwrite source evidence")
            paths.append(path)
        model, model_sha = read_limited(paths[0])
        audit, _ = read_limited(paths[1])
        pairs.append(validated_pair(label, model, model_sha, audit))
    result = summarize(pairs)
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    if len(encoded)>100_000:
        raise ValueError("Comparison output exceeds byte budget")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(result["episode_id"], "review yield for", result["model_count"], "models;", 
          "fair paired comparison:", result["fair_comparison_supported"])


if __name__ == "__main__":
    main()
