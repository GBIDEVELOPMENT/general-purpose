#!/usr/bin/env python3
"""One original AV playback window, ten review goals. All unverified by default.

Input: private source-once numeric report, no media or model weights.
Output: compact SHA-linked review instructions and honest runtime coverage.
"""
import argparse
import hashlib
import json
from pathlib import Path

GOALS = (
    "scene_location", "real_camera_cut", "visible_participants",
    "entrance_exit", "gesture_blocking", "prop_business",
    "physical_comedy", "nonverbal_sound", "vocal_delivery",
    "speaker_mouth_link", "stage_directions"
)


def unique_coverage(intervals):
    total = 0
    end = 0
    for start, stop in sorted(intervals):
        total += max(0, stop - max(end, start))
        end = max(end, stop)
    return total


def build(source):
    episode = source.get("episode_id")
    if episode not in ("S01E01", "S09E19"):
        raise ValueError("Only measured original pilots are supported")
    s09 = episode == "S09E19"
    video = source.get("original_video_sha256")
    duration = source.get("original_video_duration_ms" if s09
                          else "source_audio_video_duration_ms")
    families = source.get("model_families" if s09 else "model_independent_families")
    accepted = source.get("episode_production_script_accepted" if s09
                          else "complete_production_screenplay_accepted")
    plan = source.get("shot_bounded_selective_original_video_review" if s09
                      else "shot_bounded_original_video_review")
    if (not isinstance(video, str) or len(video) != 64 or
        any(c not in "0123456789abcdef" for c in video) or
        type(duration) is not int or not 1200000 <= duration <= 1800000 or
        sorted(families or []) != ["kaldi_hmm_wfst", "whisper"] or
        accepted is not False or not isinstance(plan, dict) or
        plan.get("source_video_sha256") != video or
        plan.get("source_duration_ms") != duration or
        plan.get("human_continuous_video_review_done") is not False or
        plan.get("full_original_episode_screenplay_accepted") is not False or
        plan.get("excerpt_media_decoded_or_retained") is not False):
        raise ValueError("Source, model or nonacceptance invariants failed")
    requests = plan.get("review_requests")
    if not isinstance(requests, list) or not 1 <= len(requests) <= 12:
        raise ValueError("Excessive or missing original review windows")
    if len(requests) != plan.get("requested_video_excerpt_count"):
        raise ValueError("Source review-count mismatch")
    entries = []
    intervals = []
    identifiers = set()
    for i, row in enumerate(requests):
        window = row.get("time_window_ms_candidate_only")
        ident = row.get("event_id")
        if (not isinstance(window, list) or len(window) != 2 or
            any(type(t) is not int for t in window) or
            not 0 <= window[0] < window[1] <= duration or
            window[1]-window[0] > 5000 or
            not isinstance(ident, str) or not 1 <= len(ident) <= 100 or
            ident in identifiers or
            row.get("original_shot_and_action_human_verified") is not False or
            row.get("speaking_identity_or_prosody_verified") is not False or
            row.get("draft_stage_direction_accepted") is not False):
            raise ValueError("Invalid or falsely accepted review window")
        identifiers.add(ident)
        intervals.append(tuple(window))
        entries.append({
            "id": f"{episode}-AV-{i+1:02d}",
            "event_id": ident,
            "original_video_sha256": video,
            "source_window_ms": window,
            "selection_reason": row.get("selection_reason"),
            "candidate_shot_partition_not_verified":
                row.get("candidate_shot_partition_unverified"),
            "goals": {g: "PENDING_ORIGINAL_AV_REVIEW" for g in GOALS},
            "original_continuous_AV_review_done": False,
            "independently_accepted": False
        })
    requested = sum(b-a for a, b in intervals)
    if requested != plan.get("requested_total_video_excerpt_ms"):
        raise ValueError("Source excerpt lengths disagree")
    coverage = unique_coverage(intervals)
    return {
        "schema": "night-court-multigoal-original-AV-review/1",
        "episode_id": episode, "original_video_sha256": video,
        "original_duration_ms": duration, "requests": entries,
        "selected_window_count": len(entries),
        "requested_before_overlap_ms": requested,
        "distinct_selected_runtime_ms": coverage,
        "original_runtime_unselected_ms": duration - coverage,
        "fraction_original_runtime_selected": round(coverage / duration, 6),
        "script_or_claim_independently_accepted": False,
        "instructions": "Play original synchronized picture and soundtrack; "
                        "adjudicate several goals per window. Unselected "
                        "runtime requires additional coverage before completion."
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-report", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        p.error("Refusing to overwrite original research packet")
    raw = args.source_report.read_bytes()
    result = build(json.loads(raw))
    result["original_research_report_sha256"] = hashlib.sha256(raw).hexdigest()
    out = (json.dumps(result, indent=2) + "\n").encode()
    if len(out) > 150000:
        raise ValueError("Review output exceeds safety budget")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(out)
    print(result["episode_id"], result["selected_window_count"],
          "unaccepted AV windows;", result["fraction_original_runtime_selected"],
          "of original runtime selected")


if __name__ == "__main__":
    main()
