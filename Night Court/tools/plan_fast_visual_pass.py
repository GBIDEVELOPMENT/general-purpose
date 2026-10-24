#!/usr/bin/env python3
"""Budgeted, shot-aware *plan* for Night Court visual analysis; no media decoding.

Consumes source-fingerprinted timing candidates and nominal ffprobe frame rate.
A plan is a bounded set of requested frame times, NOT verified original frame PTS,
shot identity, stage direction or character recognition. Shot-cut proposals can
be false positives; avoiding them remains conservative.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from fractions import Fraction
import json
import math
from pathlib import Path
import re

MAX_SOURCE_DURATION_MS = 7_200_000
MAX_FRAMES = 240
MAX_BASELINE = 100
MAX_BURSTS = 32
MAX_TRANSITIONS = 12
BASELINE_SPACING_MS = 15_000
MAX_CUTS = 5000
MAX_EVENTS = 1000


def integer(value, name, minimum=0, maximum=MAX_SOURCE_DURATION_MS):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"Invalid {name}: expected integer in [{minimum}, {maximum}]")
    return value


def frame_rate(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{1,6}(?:/[0-9]{1,6})?", value):
        raise ValueError("Frame rate must be an ffprobe rational string")
    rate = Fraction(value)
    if not Fraction(12) <= rate <= Fraction(120):
        raise ValueError("Nominal frame rate outside supported 12-120 fps range")
    return rate


def nominal_at(frame_index, rate):
    return round(Fraction(1000 * frame_index, 1) / rate)


def snap(time_ms, rate):
    return round(Fraction(time_ms, 1000) * rate)


def require_source(spec):
    if spec.get("schema") != "night-court-fast-visual-input/1":
        raise ValueError("Unrecognized sampling input schema")
    episode = spec.get("episode_id")
    if not isinstance(episode, str) or not re.fullmatch(r"S0[1-9]E[0-9]{2}", episode):
        raise ValueError("Episode identifier must be original-series SxxExx")
    digest = spec.get("source_video_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("Expected immutable original-video SHA256")
    duration = integer(spec.get("duration_ms"), "duration_ms", 1000)
    window = spec.get("window_ms", [0, duration])
    if (not isinstance(window, list) or len(window) != 2):
        raise ValueError("Expected [start,end] source window")
    start = integer(window[0], "window start", 0, duration)
    end = integer(window[1], "window end", 0, duration)
    if start >= end:
        raise ValueError("Empty or reversed source window")
    fps = frame_rate(spec.get("avg_frame_rate"))
    rate_provenance = spec.get("frame_rate_provenance")
    if rate_provenance not in ("verified_local_ffprobe", "synthetic_unverified_assumption"):
        raise ValueError("Frame rate needs explicit measurement or synthetic provenance")
    cuts_raw = spec.get("cut_candidates", [])
    events_raw = spec.get("activity_events", [])
    if (not isinstance(cuts_raw, list) or len(cuts_raw) > MAX_CUTS
        or not isinstance(events_raw, list) or len(events_raw) > MAX_EVENTS):
        raise ValueError("Unbounded shot candidates or activity events")
    cuts = []
    for cut in cuts_raw:
        if not isinstance(cut, dict):
            raise ValueError("Invalid shot candidate")
        t = integer(cut.get("time_ms"), "cut candidate time", start + 1, end - 1)
        score = cut.get("image_change_score")
        if type(score) not in (float, int) or not math.isfinite(score) or not 0 <= score <= 1:
            raise ValueError("Shot image score outside [0,1]")
        cuts.append((t, float(score)))
    cuts.sort()
    if any(cuts[i][0] == cuts[i-1][0] for i in range(1, len(cuts))):
        raise ValueError("Duplicate proposed shot boundaries")
    events = []
    ids = set()
    for event in events_raw:
        if not isinstance(event, dict):
            raise ValueError("Invalid activity event")
        ident = event.get("event_id")
        if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,70}", ident) or ident in ids:
            raise ValueError("Unusable or duplicate activity event ID")
        ids.add(ident)
        t = integer(event.get("time_ms"), "event time", start, end - 1)
        priority = integer(event.get("priority"), "event priority", 1, 5)
        mode = event.get("mode", "gesture")
        if mode not in ("gesture", "adjacent"):
            raise ValueError("Unknown motion sampling mode")
        events.append({"event_id": ident, "time_ms": t, "priority": priority, "mode": mode})
    return episode, digest, duration, (start, end), fps, rate_provenance, cuts, events


def make_plan(spec):
    episode, digest, duration, (start, end), fps, rate_provenance, cuts, events = require_source(spec)
    boundaries = [start] + [t for t, _ in cuts] + [end]
    cuts_times = [t for t, _ in cuts]
    used = set()
    frames, bursts, transitions, baseline, skipped = [], [], [], [], []
    guard = Fraction(1000, 1) / fps

    def shot_slot(index):
        t = Fraction(index * 1000, 1) / fps
        if not start <= t < end:
            return None
        shot = bisect_right(cuts_times, t)
        # Leave a full nominal frame of margin at both ends, so no triad
        # silently claims continuity across a candidate edit or source cut.
        if not Fraction(boundaries[shot]) + guard <= t <= Fraction(boundaries[shot+1]) - guard:
            return None
        return shot

    def commit(indices, kind, event_id=None):
        if any(x < 0 or x in used or shot_slot(x) is None for x in indices):
            return None
        if len(used) + len(indices) > MAX_FRAMES:
            return None
        for i in indices:
            used.add(i)
            frames.append({"nominal_frame_index": i, "nominal_ms": nominal_at(i, fps),
                           "candidate_shot_partition": shot_slot(i), "role": kind,
                           "evidence_event_id": event_id})
        return [nominal_at(x, fps) for x in indices]

    # Prioritize activity before baseline: fallback stills must never consume
    # budget needed by a complete three-frame gesture.
    for event in sorted(events, key=lambda x: (-x["priority"], x["time_ms"], x["event_id"])):
        if len(bursts) >= MAX_BURSTS:
            skipped.append({"event_id": event["event_id"], "reason": "burst_cap"})
            continue
        center = snap(event["time_ms"], fps)
        stride = 1 if event["mode"] == "adjacent" else max(1, round(fps / 6))
        indices = [center-stride, center, center+stride]
        slots = [shot_slot(i) for i in indices]
        if None in slots or len(set(slots)) != 1:
            skipped.append({"event_id": event["event_id"], "reason": "near_or_crosses_cut"})
            continue
        times = commit(indices, "motion_burst", event["event_id"])
        if times is None:
            skipped.append({"event_id": event["event_id"], "reason": "duplicate_frame_or_budget"})
            continue
        bursts.append({"event_id": event["event_id"], "priority": event["priority"],
                       "candidate_shot_partition": slots[0], "nominal_frame_times_ms": times,
                       "frame_count": 3, "mode": event["mode"]})

    # Two images on opposite sides of a candidate edit are explicitly NOT a
    # motion sequence, and should not be sent to the continuity model as one.
    for t, score in sorted(cuts, key=lambda x: (-x[1], x[0])):
        if len(transitions) >= MAX_TRANSITIONS:
            break
        center = snap(t, fps)
        before = next((i for i in range(center-1, center-6, -1)
                       if shot_slot(i) is not None and shot_slot(i) == bisect_right(cuts_times, t)-1), None)
        after = next((i for i in range(center, center+6)
                      if shot_slot(i) is not None and shot_slot(i) == bisect_right(cuts_times, t)), None)
        if before is None or after is None:
            continue
        pair = commit([before, after], "transition_pair")
        if pair:
            transitions.append({"cut_candidate_ms": t, "image_change_score": score,
                                "frame_times_ms": pair,
                                "relation": "across_candidate_cut_not_continuous_motion"})

    # Uniform scene coverage, no accidental front-of-episode bias at cap.
    midpoints = list(range(start + BASELINE_SPACING_MS//2, end, BASELINE_SPACING_MS))
    if not midpoints:
        midpoints = [(start+end)//2]
    if len(midpoints) > MAX_BASELINE:
        midpoints = [midpoints[(i*(len(midpoints)-1))//(MAX_BASELINE-1)]
                     for i in range(MAX_BASELINE)]
    for t in midpoints:
        frame = snap(t, fps)
        result = commit([frame], "sparse_baseline")
        if result:
            baseline.append({"nominal_ms": result[0], "candidate_shot_partition": shot_slot(frame)})

    frames.sort(key=lambda x: x["nominal_frame_index"])
    assert len(frames) <= MAX_FRAMES
    return {
      "schema": "night-court-fast-visual-sampling-plan/1",
      "episode_id": episode,
      "source_video_sha256": digest,
      "source_duration_ms": duration,
      "window_ms": [start,end],
      "nominal_avg_frame_rate": str(fps),
      "frame_rate_provenance": rate_provenance,
      "frame_time_basis": "nominal_fps_seek_candidates_not_verified_decoded_original_frame_pts",
      "candidate_cuts_are_independently_verified": False,
      "bursts_are_continuous_original_video_reviews": False,
      "speaker_action_or_script_accepted": False,
      "budgets": {"max_frames": MAX_FRAMES, "max_baseline": MAX_BASELINE,
                  "max_three_frame_bursts": MAX_BURSTS,
                  "max_transition_pairs": MAX_TRANSITIONS,
                  "baseline_spacing_ms": BASELINE_SPACING_MS},
      "counts": {"frames": len(frames), "baseline": len(baseline), "bursts": len(bursts),
                 "transition_pairs": len(transitions), "cut_candidates": len(cuts),
                 "events_supplied": len(events), "events_deferred": len(skipped)},
      "motion_bursts": sorted(bursts, key=lambda x: x["nominal_frame_times_ms"][1]),
      "transition_pairs": sorted(transitions, key=lambda x: x["cut_candidate_ms"]),
      "baseline": baseline,
      "deferred_events": skipped,
      "frames": frames,
      "limitations": [
        "Plan only: no image decoded, inspected, retained or passed to a model.",
        "Nominal frame indices must be reconciled with actual decoded source frame PTS; variable cadence may differ.",
        "Shot cuts are image-change hypotheses; false positives can split true continuous gestures.",
        "Frame counts cap visual-model calls, not FFmpeg full-stream shot scan runtime or FTP transfer time.",
        "Consensus or frame detection does not independently certify character identity or full script completeness."
      ]
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    plan = make_plan(json.loads(args.input.read_text("utf-8")))
    if args.output.exists():
        parser.error("Refusing to overwrite existing planning evidence")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2, ensure_ascii=False)+"\n", "utf-8")
    print(f"{plan['episode_id']}: {plan['counts']['frames']} nominal images, "
          f"{plan['counts']['bursts']} triads, {plan['counts']['transition_pairs']} cut pairs; "
          "no original video was decoded")


if __name__ == "__main__":
    main()
