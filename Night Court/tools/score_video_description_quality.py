#!/usr/bin/env python3
"""Source-linked, blinded per-window video-description quality scorecard.

Model text is untrusted. Reviewer labels are independently supplied and never
fabricated by this program. In particular, null reference coverage is NOT zero
false positives, zero missed physical comedy, or a source-video certification.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

MODEL_SCHEMA = "night-court-headless-video-description/1"
LABEL_SCHEMA = "night-court-visual-quality-review-labels/1"
OUT_SCHEMA = "night-court-video-description-quality-scorecard/1"
SHA = re.compile(r"[0-9a-f]{64}\Z")
IDENT = re.compile(r"[A-Za-z0-9_.-]{1,80}\Z")
KINDS = {"action", "entrance_exit", "prop", "physical_comedy", "reaction", "setting", "camera"}
MAX_INPUT_BYTES = 200_000
MAX_LABELS = 256


def require_sha(value, what):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError(f"Invalid {what} SHA256")
    return value


def load_bounded(path):
    raw = path.read_bytes()
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("Quality input exceeds byte limit")
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def validate_pair(model, labels):
    if not isinstance(model, dict) or model.get("schema") != MODEL_SCHEMA:
        raise ValueError("Expected a real video description run")
    if model.get("script_or_claim_independently_accepted") is not False:
        raise ValueError("Model cannot certify a screenplay")
    video_sha = require_sha(model.get("source_video_sha256"), "model source video")
    if model.get("verified_source_sha256") != video_sha:
        raise ValueError("Model input source has not passed actual SHA verification")
    if not isinstance(labels, dict) or labels.get("schema") != LABEL_SCHEMA:
        raise ValueError("Expected independent reviewer labels")
    if labels.get("source_video_sha256") != video_sha or labels.get("episode_id") != model.get("episode_id"):
        raise ValueError("Human source reference does not match model episode/edition")
    reviewer = labels.get("reviewer_id")
    if not isinstance(reviewer, str) or not IDENT.fullmatch(reviewer):
        raise ValueError("Reviewer reference ID required")
    windows = model.get("windows")
    if not isinstance(windows, list) or not 1 <= len(windows) <= 12:
        raise ValueError("Invalid bounded model windows")
    indexed = {}
    for w in windows:
        if not isinstance(w, dict) or not isinstance(w.get("id"), str) or not IDENT.fullmatch(w["id"]):
            raise ValueError("Invalid model source window")
        a, b = w.get("start_ms"), w.get("end_ms")
        if type(a) is not int or type(b) is not int or not 0 <= a < b <= model.get("duration_ms", 0):
            raise ValueError("Invalid model timing")
        if w["id"] in indexed:
            raise ValueError("Duplicate model window")
        if w.get("candidate_cut_crossing") is not False or w.get("independently_accepted") is not False:
            raise ValueError("Unaccepted original-source shot was self-promoted")
        if w.get("status") not in ("machine_proposed", "requires_review"):
            raise ValueError("Not an actual inference result")
        if type(w.get("inference_seconds")) not in (int, float) or not math.isfinite(w["inference_seconds"]) or w["inference_seconds"] < 0:
            raise ValueError("Missing measured inference time")
        indexed[w["id"]] = w
    annotations = labels.get("observations")
    if not isinstance(annotations, list) or len(annotations) > MAX_LABELS:
        raise ValueError("Invalid or unbounded independent labels")
    seen = set()
    for item in annotations:
        if not isinstance(item, dict):
            raise ValueError("Invalid reviewed event")
        wid = item.get("window_id")
        event_id = item.get("event_id")
        if wid not in indexed or not isinstance(event_id, str) or not IDENT.fullmatch(event_id):
            raise ValueError("Unmatched reference event")
        key = (wid, event_id)
        if key in seen:
            raise ValueError("Duplicate independent event reference")
        seen.add(key)
        if item.get("source_window_ms") != [indexed[wid]["start_ms"], indexed[wid]["end_ms"]]:
            raise ValueError("Original source reference window mismatch")
        if item.get("kind") not in KINDS:
            raise ValueError("Unrecognized visual claim class")
        if item.get("reference_truth") not in ("present", "absent"):
            raise ValueError("Reference must explicitly classify present/absent")
        if item.get("model_claim") not in ("present", "absent", "unclear"):
            raise ValueError("Reviewer must classify actual model claim or abstention")
        if item.get("direct_original_visual_review_attested") is not True:
            raise ValueError("Cannot use unreviewed AV as independent truth")
        note = item.get("reference_note")
        if not isinstance(note, str) or not 1 <= len(note.strip()) <= 500:
            raise ValueError("Source-grounded reference note required")
    if labels.get("full_original_video_coverage_verified") is not False:
        raise ValueError("A bounded sample cannot attest whole episode coverage")
    return video_sha, indexed, annotations


def divide(numer, denom):
    return round(numer / denom, 6) if denom else None


def score(model, labels):
    sha, indexed, observations = validate_pair(model, labels)
    counts = {
        "true_positive": 0, "false_positive": 0,
        "false_negative": 0, "true_negative": 0,
        "unclear_present": 0, "unclear_absent": 0,
    }
    by_kind = {kind: dict.fromkeys(counts, 0) for kind in sorted(KINDS)}
    for item in observations:
        truth, claim = item["reference_truth"], item["model_claim"]
        if claim == "unclear":
            key = "unclear_present" if truth == "present" else "unclear_absent"
        elif claim == "present":
            key = "true_positive" if truth == "present" else "false_positive"
        else:
            key = "false_negative" if truth == "present" else "true_negative"
        counts[key] += 1
        by_kind[item["kind"]][key] += 1
    def metrics(c):
        return {
            "precision_explicit_claims": divide(c["true_positive"], c["true_positive"] + c["false_positive"]),
            "recall_explicit_claims": divide(c["true_positive"], c["true_positive"] + c["false_negative"] + c["unclear_present"]),
            "false_positive_rate_negative_controls": divide(c["false_positive"], c["false_positive"] + c["true_negative"] + c["unclear_absent"]),
            "abstention_rate_labeled": divide(c["unclear_present"] + c["unclear_absent"], sum(c.values())),
        }
    inferred = [w["inference_seconds"] for w in indexed.values()]
    verified_ms = sum(w["end_ms"] - w["start_ms"] for w in indexed.values())
    output = {
        "schema": OUT_SCHEMA,
        "episode_id": model["episode_id"],
        "source_video_sha256": sha,
        "model_id": model.get("model_id"),
        "model_revision": model.get("model_revision"),
        "reviewer_id": labels["reviewer_id"],
        "sample_windows": len(indexed),
        "window_runtime_requested_ms_before_overlap": verified_ms,
        "sample_events_independently_labeled": len(observations),
        "expected_visible_events": sum(x["reference_truth"] == "present" for x in observations),
        "negative_control_absences": sum(x["reference_truth"] == "absent" for x in observations),
        "confusion_counts": counts,
        "metrics": metrics(counts),
        "per_kind": {k: {"counts": v, "metrics": metrics(v)} for k, v in by_kind.items()},
        "valid_model_json_windows": sum(w["status"] == "machine_proposed" for w in indexed.values()),
        "structured_json_success_fraction": divide(sum(w["status"] == "machine_proposed" for w in indexed.values()), len(indexed)),
        "average_inference_seconds_per_window": round(statistics.mean(inferred), 3),
        "total_inference_seconds": round(sum(inferred), 3),
        "model_load_seconds": model.get("model_load_seconds"),
        "runner_wall_seconds_if_available": model.get("wall_seconds"),
        "independent_original_video_observations_reported": True,
        "whole_episode_visual_coverage_certified": False,
        "source_srt_or_original_dialogue_modified": False,
        "model_generated_screenplay_accepted": False,
        "label_quality_limitations": (
            "Reference labels are reviewer-attested and not cryptographically independently audited; "
            "null metrics mean no eligible reference examples, never perfect scores."
        )
    }
    return output


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-report", required=True, type=Path)
    ap.add_argument("--reference-labels", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    a = ap.parse_args()
    if a.output.exists() or a.output.resolve() in {a.model_report.resolve(), a.reference_labels.resolve()}:
        ap.error("Refusing to overwrite reviewer or model evidence")
    model, mhash = load_bounded(a.model_report)
    labels, lhash = load_bounded(a.reference_labels)
    if labels.get("exact_model_report_sha256") != mhash:
        raise ValueError("Reference labels do not match exact model report bytes")
    result = score(model, labels)
    result["model_report_sha256"] = mhash
    result["reviewer_labels_sha256"] = lhash
    encoded = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    if len(encoded) > MAX_INPUT_BYTES:
        raise ValueError("Quality metric report too large")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_bytes(encoded)
    print(result["episode_id"], "independent labels:", result["sample_events_independently_labeled"],
          "model JSON valid windows:", result["valid_model_json_windows"], "of", result["sample_windows"],
          "episode certified: False")


if __name__ == "__main__":
    main()
