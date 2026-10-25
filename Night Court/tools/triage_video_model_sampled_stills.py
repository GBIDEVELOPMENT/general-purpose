#!/usr/bin/env python3
"""Score source-linked model claims against sampled stills, never moving-video truth.

This narrow *triage* layer uses human-annotated nominal-frame evidence. It is
NOT a substitute for the independently observed original picture/audio review
required by review_video_stage_directions.py or score_video_description_quality.py.
Output intentionally excludes all model/reference prose and original images.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from run_headless_video_description import FIELDS, SCHEMA as MODEL_SCHEMA

SCHEMA = "night-court-sampled-frame-claim-review/1"
OUT_SCHEMA = "night-court-sampled-frame-model-triage/1"
SHA = re.compile(r"[0-9a-f]{64}\Z")
IDENT = re.compile(r"[A-Za-z0-9_.-]{1,80}\Z")
KINDS = (
    "visibly_consistent", "mixed_claim", "contradicted_in_samples",
    "unsupported_interpretation", "not_resolvable", "model_absent"
)
MAX_SIZE = 200_000
MAX_SOURCE_ARTIFACT = 30_000_000


def check_sha(value, label):
    if not isinstance(value, str) or SHA.fullmatch(value) is None:
        raise ValueError("Invalid " + label)
    return value


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def bounded_file(path, max_size=MAX_SIZE):
    if not path.is_file() or path.stat().st_size > max_size:
        raise ValueError("Missing or unbounded sampled review input")
    return path.read_bytes()


def review(model, raw_model_sha, annotations, material_sha):
    if not isinstance(model, dict) or model.get("schema") != MODEL_SCHEMA:
        raise ValueError("Wrong source model report")
    if model.get("script_or_claim_independently_accepted") is not False:
        raise ValueError("Unreviewed model is self-certified")
    episode = model.get("episode_id")
    original = check_sha(model.get("source_video_sha256"), "source AVI SHA")
    if model.get("verified_source_sha256") != original:
        raise ValueError("Model video was not source-SHA verified")
    if not isinstance(annotations, dict) or annotations.get("schema") != SCHEMA:
        raise ValueError("Unknown sampled-frame review schema")
    if annotations.get("episode_id") != episode or annotations.get("source_video_sha256") != original:
        raise ValueError("Sampled evidence source edition mismatch")
    if annotations.get("exact_model_report_sha256") != check_sha(raw_model_sha, "model report SHA"):
        raise ValueError("Sampled review refers to different model bytes")
    if annotations.get("sampled_source_material_sha256") != check_sha(material_sha, "sample material SHA"):
        raise ValueError("Sample-frame evidence bytes changed")
    if annotations.get("original_moving_video_reviewed") is not False or annotations.get("original_soundtrack_reviewed") is not False:
        raise ValueError("Sampled stills must not claim original AV review")
    if annotations.get("native_frame_pts_independently_verified") is not False:
        raise ValueError("Nominal sampled frame times are not verified native PTS")
    if annotations.get("episode_independently_certified") is not False:
        raise ValueError("Sampled frames cannot certify a whole episode")
    if annotations.get("sampled_stills_visually_inspected") is not True:
        raise ValueError("Sampling reviewer must attest inspecting stills")
    reviewer = annotations.get("reviewer_id")
    if not isinstance(reviewer, str) or IDENT.fullmatch(reviewer) is None:
        raise ValueError("Invalid sampled-still reviewer identifier")
    fps = annotations.get("nominal_sampling_fps")
    if type(fps) is not int or not 1 <= fps <= 10:
        raise ValueError("Bad source sampled-frame rate")
    windows = model.get("windows")
    if not isinstance(windows, list) or len(windows) != 1:
        raise ValueError("Triage permits exactly one bounded original model window")
    w = windows[0]
    if w.get("status") != "machine_proposed" or w.get("candidate_cut_crossing") is not False:
        raise ValueError("No completed shot-candidate model evidence")
    if w.get("shot_partition_verified") is not False or w.get("independently_accepted") is not False:
        raise ValueError("Model cannot certify original frame/shot truth")
    start, end = w.get("start_ms"), w.get("end_ms")
    if type(start) is not int or type(end) is not int or not 0 <= start < end <= model.get("duration_ms", 0):
        raise ValueError("Original source time window invalid")
    if end-start > 15000:
        raise ValueError("Unbounded source window")
    frames = annotations.get("nominal_sample_times_ms")
    if not isinstance(frames, list) or not 2 <= len(frames) <= 50:
        raise ValueError("Sampled source frame times absent")
    if any(type(v) is not int or not start <= v < end for v in frames):
        raise ValueError("Sampled source time outside model window")
    if sorted(set(frames)) != frames:
        raise ValueError("Sample frame times must be unique and chronological")
    if annotations.get("window_id") != w.get("id"):
        raise ValueError("Mismatch in original source sample window ID")
    hypothesis = w.get("model_hypothesis")
    if not isinstance(hypothesis, dict) or set(hypothesis) != set(FIELDS):
        raise ValueError("Incomplete model claims")
    field_rows = annotations.get("field_reviews")
    if not isinstance(field_rows, list) or len(field_rows) != len(FIELDS):
        raise ValueError("Require all ten model visual fields to be evaluated")
    seen, counts, decisions = set(), Counter(), []
    for row in field_rows:
        if not isinstance(row, dict) or row.get("field") not in FIELDS:
            raise ValueError("Unknown sampled visual field")
        field = row["field"]
        if field in seen:
            raise ValueError("Duplicate sampled visual field")
        seen.add(field)
        kind = row.get("status")
        if kind not in KINDS:
            raise ValueError("Unknown still-evidence classification")
        note = row.get("sampled_frame_observation")
        if not isinstance(note, str) or not 1 <= len(note.strip()) <= 500:
            raise ValueError("Require bounded sampled image observation for each field")
        if (kind == "model_absent") != (not hypothesis[field].strip()):
            raise ValueError("Empty model field cannot be scored as an observed positive")
        counts[kind] += 1
        decisions.append({"field": field, "sampled_frame_status": kind})
    return {
        "schema": OUT_SCHEMA,
        "episode_id": episode,
        "source_video_sha256": original,
        "exact_private_model_report_sha256": raw_model_sha,
        "source_sample_material_sha256": material_sha,
        "nominal_model_window_ms": [start, end],
        "nominal_frames_examined": len(frames),
        "nominal_sampling_fps": fps,
        "sampled_still_reviewer_id": reviewer,
        "field_statuses": [next(d for d in decisions if d["field"] == name) for name in FIELDS],
        "field_counts": {kind: counts[kind] for kind in KINDS},
        "field_count": len(FIELDS),
        "reference_is_original_full_motion_video": False,
        "native_frame_pts_independently_verified": False,
        "source_video_editorial_staging_approved": False,
        "quality_accuracy_or_model_recall_established": False,
        "no_model_or_reviewer_prose_copied": True,
        "note": ("Partial visual-support triage from nominally timed source-derived sampled stills; "
                 "unseen content is NOT proven absent between frames, no sound/motion validation, "
                 "no source-video acceptance or episode certification."),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-report", required=True, type=Path)
    ap.add_argument("--sampled-review", required=True, type=Path)
    ap.add_argument("--sample-material", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    inputs = (args.model_report, args.sampled_review, args.sample_material)
    if args.output.exists() or args.output.resolve() in {x.resolve() for x in inputs}:
        ap.error("Refusing to overwrite source evidence or existing output")
    model_raw = bounded_file(args.model_report)
    labels_raw = bounded_file(args.sampled_review)
    source_raw = bounded_file(args.sample_material, MAX_SOURCE_ARTIFACT)
    result = review(json.loads(model_raw), sha_bytes(model_raw),
                    json.loads(labels_raw), sha_bytes(source_raw))
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    if len(encoded) > MAX_SIZE:
        raise ValueError("Triage output exceeds limit")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(result["episode_id"], "sampled stills", result["nominal_frames_examined"],
          "fields", result["field_count"], "film stage accepted: 0")


if __name__ == "__main__":
    main()
