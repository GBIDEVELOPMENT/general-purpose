#!/usr/bin/env python3
"""Compare fixed-prompt Qwen trials on EXACT same original film segment.

Input contains PRIVATE model text. Output contains only source/provenance,
timings and structured JSON validity, NEVER model prose or source image bytes.
Stage accuracy cannot be calculated until independent moving-AV reviewer labels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

from run_headless_video_description import PROMPTS
from summarize_original_qwen_pilot_metrics import source_safe_record

SCHEMA = "night-court-original-video-fixed-prompt-ab/1"
INPUT_MAX = 150_000
OUTPUT_MAX = 30_000
FIXED_INPUTS = ("episode_id", "source_video_sha256", "verified_source_sha256",
                "duration_ms", "model_id", "model_revision", "video_sampling_fps",
                "video_width_pixels", "max_generated_tokens", "source_focus")
ERROR_CODES = {None, "non_json_model_output", "malformed_model_json",
               "bad_model_fields", "duplicate_model_json_key"}


def load_private(path: Path):
    if not path.is_file() or not 0 < path.stat().st_size <= INPUT_MAX:
        raise ValueError("Original source-run model report missing or oversized")
    raw = path.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def compare(control: dict, control_sha: str, treatment: dict, treatment_sha: str):
    a = source_safe_record(control, control_sha)
    b = source_safe_record(treatment, treatment_sha)
    for key in FIXED_INPUTS:
        if control.get(key) != treatment.get(key):
            raise ValueError(f"Matched original-film prompt comparison has confounded {key}")
    if control.get("source_focus") != "physical_comedy":
        raise ValueError("This is not a controlled physical-business trial")
    if (a["prompt_profile"], b["prompt_profile"]) != ("standard", "action_compact"):
        raise ValueError("Exact control/compact treatment profiles and order required")
    if control["prompt_sha256"] != a["prompt_sha256"] or treatment["prompt_sha256"] != b["prompt_sha256"]:
        raise ValueError("Immutable selected profile hash changed")
    if a["source_video_sha256"] != b["source_video_sha256"] or a["original_excerpt_start_ms"] != b["original_excerpt_start_ms"] or a["original_excerpt_end_ms"] != b["original_excerpt_end_ms"]:
        raise ValueError("Input original source movie and exact windows must match")
    aw,bw=control.get("windows",[]),treatment.get("windows",[])
    if len(aw) != 1 or len(bw) != 1:
        raise ValueError("One model-inference window per episode only")
    if (aw[0]["start_ms"], aw[0]["end_ms"]) != (bw[0]["start_ms"], bw[0]["end_ms"]):
        raise ValueError("Original time windows do not match")
    if any(w.get("model_output_error") not in ERROR_CODES for w in (aw[0],bw[0])):
        raise ValueError("Unknown model parser status code")
    for report,score in ((control,a),(treatment,b)):
        win=report["windows"][0]
        if (score["inference_schema_valid"] and win.get("model_output_error") is not None
            or not score["inference_schema_valid"] and win.get("model_output_error") is None):
            raise ValueError("Invalid model-output parser state combination")
    baseline = a["processing_seconds"]
    test = b["processing_seconds"]
    if any(type(t.get("video_sampling_fps")) is not int or t["video_sampling_fps"] not in (1,2,3) for t in (control,treatment)):
        raise ValueError("Unbounded model-video sample rate")
    if any(type(t.get("max_generated_tokens")) is not int or not 32 <= t["max_generated_tokens"] <= 512 for t in (control,treatment)):
        raise ValueError("Unbounded model generation token cap")
    return {
        "schema": SCHEMA,
        "episode_id": a["episode_id"],
        "source_video_sha256": a["source_video_sha256"],
        "exact_original_video_window_ms": [a["original_excerpt_start_ms"],a["original_excerpt_end_ms"]],
        "same_original_episode_video_and_window_verified": True,
        "model_id": control["model_id"],
        "model_revision": control["model_revision"],
        "video_sampling_fps": control["video_sampling_fps"],
        "video_width_pixels": control["video_width_pixels"],
        "max_generated_tokens": control["max_generated_tokens"],
        "fixed_dimensions_other_than_prompt_identical": True,
        "runs": [
            {"role":"control", "prompt_profile":a["prompt_profile"],"prompt_sha256":a["prompt_sha256"],
             "exact_private_model_report_sha256":control_sha,"strict_ten_field_json_valid":a["inference_schema_valid"],
             "model_output_error":aw[0].get("model_output_error"),
             "model_loading_seconds":baseline["model_load"],"model_inference_seconds":baseline["visual_model_inference"],
             "model_tool_seconds":baseline["model_tool"]},
            {"role":"treatment","prompt_profile":b["prompt_profile"],"prompt_sha256":b["prompt_sha256"],
             "exact_private_model_report_sha256":treatment_sha,"strict_ten_field_json_valid":b["inference_schema_valid"],
             "model_output_error":bw[0].get("model_output_error"),
             "model_loading_seconds":test["model_load"],"model_inference_seconds":test["visual_model_inference"],
             "model_tool_seconds":test["model_tool"]},
        ],
        "difference_treatment_minus_control_model_inference_seconds":round(test["visual_model_inference"]-baseline["visual_model_inference"],3),
        "difference_treatment_minus_control_tool_seconds":round(test["model_tool"]-baseline["model_tool"],3),
        "identical_ephemeral_encoded_clip_sha256":aw[0].get("clip_sha256_ephemeral") == bw[0].get("clip_sha256_ephemeral")
            if aw[0].get("clip_sha256_ephemeral") and bw[0].get("clip_sha256_ephemeral") else None,
        "direct_original_moving_video_review_complete":False,
        "stage_direction_approval_count":0,
        "model_factual_action_quality_comparison_established":False,
        "contains_original_film_images_or_model_prose":False,
        "limitations":"Exact source and model input matching allows a prompt-versus-structure/runtime comparison, not actor-direction accuracy. Both movie outputs require independent moving audiovisual review to estimate physical-action acceptance.",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--standard",type=Path,required=True)
    p.add_argument("--action-compact",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if len({a.standard.resolve(),a.action_compact.resolve(),a.output.resolve()}) != 3 or a.output.exists():
        p.error("Refuse input/output alias or overwrite")
    control,control_sha=load_private(a.standard)
    trial,trial_sha=load_private(a.action_compact)
    report=compare(control,control_sha,trial,trial_sha)
    out=(json.dumps(report,sort_keys=True,indent=2)+"\n").encode()
    if len(out)>OUTPUT_MAX:
        raise ValueError("Source-safe comparison unexpectedly oversized")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(out)
    print(report["episode_id"], "original prompt A/B source matched, AV stage acceptance: 0")


if __name__=="__main__":
    main()
