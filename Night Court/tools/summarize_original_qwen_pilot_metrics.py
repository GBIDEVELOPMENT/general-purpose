#!/usr/bin/env python3
"""Validate private owner-only Qwen original-film outputs and retain metrics ONLY.

Converts expiring private owner source model reports into small provenance and
numeric results. Never retains model prose, camera/body/stage descriptions,
original movie, caption words, decoded frame paths, or soundtrack.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from owner_qwen_original_video_pilot import SOURCES, MODEL_SHA, MODEL_ID, CLIP_MS, candidate_offsets

IN_SCHEMA = "night-court-headless-video-description/1"
ORIGINAL_PILOT = "night-court-original-qwen-picture-pilot/1"
OUT_SCHEMA = "night-court-original-qwen-source-safe-metrics/1"
MAX_INPUT_BYTES = 150_000
MAX_OUTPUT_BYTES = 20_000


def _finite_second(value, field):
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 3600:
        raise ValueError(f"Bad measured stage time: {field}")
    return round(value, 3)


def source_safe_record(source: dict, raw_sha: str):
    if not isinstance(source, dict) or source.get("schema") != IN_SCHEMA:
        raise ValueError("Expected original headless model JSON")
    if source.get("owner_source_pilot_schema") != ORIGINAL_PILOT:
        raise ValueError("Source never came from bounded owner Qwen pilot")
    episode = source.get("episode_id")
    spec = SOURCES.get(episode)
    if spec is None:
        raise ValueError("Only two pinned original pilot editions supported")
    media_sha = spec["sha256"]
    if (source.get("source_video_sha256") != media_sha
        or source.get("verified_source_sha256") != media_sha
        or source.get("original_avi_sha256_verified") != media_sha):
        raise ValueError("Source original video SHA changed")
    if source.get("duration_ms") != spec["duration_ms"]:
        raise ValueError("Source film duration changed")
    if source.get("model_id") != MODEL_ID or source.get("model_revision") != MODEL_SHA:
        raise ValueError("Video model identity/revision does not match verified pilot")
    required_false = (
        "script_or_claim_independently_accepted",
        "cut_detection_is_editorial_proposal_only",  # must be True; checked separately
        "original_native_decoded_frame_pts_human_verified",
        "original_srt_or_dialogue_modified",
        "original_soundtrack_listened_to_or_uploaded",
        "actor_identity_or_voice_verified",
        "whole_episode_visual_coverage_accepted",
        "original_series_production_screenplay_accepted",
    )
    for key in required_false:
        if key == "cut_detection_is_editorial_proposal_only":
            if source.get(key) is not True:
                raise ValueError("Original cut detector truth state was promoted")
        elif source.get(key) is not False:
            raise ValueError(f"Unsupported original-source certification or change: {key}")
    if source.get("no_source_clip_or_still_uploaded") is not True or source.get("original_avi_download_count") != 1:
        raise ValueError("Original source capture/export requirements not met")
    if source.get("source_frame_pts_independently_verified") is not False:
        raise ValueError("Native frame presentation times cannot be independently confirmed")
    windows = source.get("windows")
    if not isinstance(windows, list) or len(windows) != 1:
        raise ValueError("Only one owner Qwen original clip was authorized")
    win = windows[0]
    start, end = win.get("start_ms"), win.get("end_ms")
    focus = source.get("source_focus", "observational")
    offsets = candidate_offsets(episode, focus)
    if (type(start) is not int or type(end) is not int
        or end-start != CLIP_MS or start not in offsets):
        raise ValueError("Source clip is not one authorized 2-second candidate")
    if win.get("candidate_cut_crossing") is not False or win.get("shot_partition_verified") is not False:
        raise ValueError("Source shot continuity must remain candidate-only")
    if win.get("independently_accepted") is not False or win.get("source_AV_human_review_done") is not False:
        raise ValueError("Model cannot certify source visual actions")
    status = win.get("status")
    if status not in ("machine_proposed", "requires_review"):
        raise ValueError("Original model inference did not produce a bounded result")
    scans = source.get("pre_model_original_cut_candidate_checks")
    if not isinstance(scans, list) or not 1 <= len(scans) <= 5:
        raise ValueError("No bounded original cut scans")
    for i, item in enumerate(scans):
        if (not isinstance(item, dict)
            or item.get("start_ms") != offsets[i]
            or type(item.get("candidate_image_changes")) is not int
            or not 0 <= item["candidate_image_changes"] <= 100):
            raise ValueError("Source cut check sequence invalid")
    if scans[-1]["start_ms"] != start or scans[-1]["candidate_image_changes"] != 0:
        raise ValueError("Selected original excerpt had detected cut or wrong offset")
    seconds = {
        "original_source_retrieval": _finite_second(source.get("original_source_retrieval_wall_seconds"), "source retrieval"),
        "model_load": _finite_second(source.get("model_load_seconds"), "model load"),
        "temporary_clip_decode": _finite_second(win.get("decode_seconds"), "clip decode"),
        "visual_model_inference": _finite_second(win.get("inference_seconds"), "visual model"),
        "model_tool": _finite_second(source.get("wall_seconds"), "model tool"),
    }
    if seconds["model_tool"] + 0.1 < sum(seconds[k] for k in ("model_load", "temporary_clip_decode", "visual_model_inference")):
        raise ValueError("Measured model wall smaller than stages")
    if not isinstance(raw_sha, str) or len(raw_sha) != 64:
        raise ValueError("Missing exact source-model-report SHA")
    # Deliberately do NOT copy model_hypothesis or model_response_excerpt.
    return {
        "episode_id": episode,
        "source_video_sha256": media_sha,
        "exact_private_owner_model_report_sha256": raw_sha,
        "model_id": MODEL_ID,
        "model_revision_sha": MODEL_SHA,
        "source_focus": focus,
        "original_excerpt_start_ms": start,
        "original_excerpt_end_ms": end,
        "cut_candidate_windows_tested": len(scans),
        "selected_cut_candidate_count": scans[-1]["candidate_image_changes"],
        "inference_schema_valid": status == "machine_proposed",
        "original_source_human_stage_reviewed": False,
        "independently_verified_shot_or_gag": False,
        "processing_seconds": seconds,
        "original_source_video_download_count": 1,
        "source_media_copied_to_git": False,
        "factual_stage_direction_published": False,
    }


def aggregate(rows):
    if not isinstance(rows, list) or not 1 <= len(rows) <= 2:
        raise ValueError("One or two original source reports expected")
    ids = [r["episode_id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("Repeated original episode report")
    return {
        "schema": OUT_SCHEMA,
        "pilot_episodes_with_verified_source_and_model": len(rows),
        "episodes": sorted(rows, key=lambda row: row["episode_id"]),
        "original_source_media_or_audio_retained": False,
        "machine_video_semantics_independently_accepted": False,
        "production_screenplay_complete": False,
        "no_movie_or_inference_prose_embedded": True,
        "source_truth_limit": (
            "This reports SHA-linked model runtime and output schema only. "
            "Original observed film action, physical comedy, people and setting "
            "require direct human/source-video review; never promote machine "
            "text based on this metric ledger."
        ),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report", type=Path, action="append", required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.output.exists() or any(a.output.resolve() == item.resolve() for item in a.report):
        p.error("Refuse to overwrite private report or existing evidence")
    if not 1 <= len(a.report) <= 2:
        p.error("Expected one or two private original Qwen reports")
    rows = []
    for item in a.report:
        if not item.is_file() or item.stat().st_size > MAX_INPUT_BYTES:
            raise ValueError("Private original model result missing or unbounded")
        raw = item.read_bytes()
        rows.append(source_safe_record(json.loads(raw), hashlib.sha256(raw).hexdigest()))
    result = aggregate(rows)
    output = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    if len(output) > MAX_OUTPUT_BYTES:
        raise ValueError("Durable numeric output unexpectedly large")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_bytes(output)
    print("Original source-backed Qwen metric reports:", result["pilot_episodes_with_verified_source_and_model"],
          "video interpretations accepted: 0")


if __name__ == "__main__":
    main()
