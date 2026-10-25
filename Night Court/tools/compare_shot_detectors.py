#!/usr/bin/env python3
"""Compare candidate shot transitions on SHA-verified video without scene-claim promotion.

Optional PySceneDetect 0.7 backend is compared to EXISTING FFmpeg scored
candidates. FrameTimecode is nominal stream timing, not native decoded PTS.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import time

SHA = re.compile(r"[0-9a-f]{64}\Z")
MAX_CUTS = 4000
MAX_DURATION_MS = 2_400_000
SCHEMA = "night-court-shot-benchmark/1"


def source_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def valid_cuts(values, duration, name):
    if not isinstance(values, list) or len(values) > MAX_CUTS:
        raise ValueError(f"{name} must be a bounded list")
    if any(type(v) is not int or not 0 < v < duration for v in values):
        raise ValueError(f"Invalid {name} cut time")
    if values != sorted(set(values)):
        raise ValueError(f"{name} cuts must be sorted and unique")
    return values


def validate(m):
    if m.get("schema") != "night-court-shot-benchmark-input/1":
        raise ValueError("Wrong input schema")
    if not re.fullmatch(r"S0[1-9]E[0-9]{2}", str(m.get("episode_id"))):
        raise ValueError("Invalid original-series episode ID")
    sha = m.get("source_video_sha256")
    duration = m.get("duration_ms")
    if not isinstance(sha, str) or not SHA.fullmatch(sha):
        raise ValueError("Invalid source SHA256")
    if type(duration) is not int or not 1000 <= duration <= MAX_DURATION_MS:
        raise ValueError("Invalid bounded source duration")
    baseline = valid_cuts(m.get("existing_ffmpeg_cuts_ms", []), duration, "FFmpeg")
    reviewed = m.get("independently_reviewed_cuts_ms")
    if reviewed is not None:
        reviewed = valid_cuts(reviewed, duration, "ground truth")
    return {"episode_id": m["episode_id"], "source_video_sha256": sha,
            "duration_ms": duration, "existing_ffmpeg_cuts_ms": baseline,
            "independently_reviewed_cuts_ms": reviewed}


def compare(predicted, reference, tolerance_ms=200):
    """One-to-one minimum-error greedy match; no duplicate credit for a cut."""
    if type(tolerance_ms) is not int or not 0 <= tolerance_ms <= 1000:
        raise ValueError("Bad cut-match tolerance")
    pairs = sorted((abs(a-b), i, j) for i, a in enumerate(predicted)
                   for j, b in enumerate(reference)
                   if abs(a-b) <= tolerance_ms)
    used_p, used_r, matches = set(), set(), []
    for delta, i, j in pairs:
        if i not in used_p and j not in used_r:
            used_p.add(i)
            used_r.add(j)
            matches.append({"candidate_ms": predicted[i],
                            "reference_ms": reference[j], "absolute_delta_ms": delta})
    tp = len(matches)
    fp, fn = len(predicted) - tp, len(reference) - tp
    return {
        "matched": tp, "false_positive_cuts": fp, "missed_reference_cuts": fn,
        "precision": round(tp / (tp+fp), 6) if tp+fp else None,
        "recall": round(tp / (tp+fn), 6) if tp+fn else None,
        "pairs": sorted(matches, key=lambda x: x["candidate_ms"]),
    }


def probe_duration(media):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", str(media)],
        capture_output=True, text=True, check=True, timeout=30,
    )
    sec = float(result.stdout.strip())
    if not math.isfinite(sec):
        raise ValueError("Unreliable video duration")
    return round(sec * 1000)


def scenedetect_cuts(media, detector):
    from scenedetect import detect, AdaptiveDetector, ContentDetector
    instance = ContentDetector(threshold=27.0) if detector == "content" else AdaptiveDetector()
    scenes = detect(str(media), instance, show_progress=False)
    # Returned FrameTimecode represents nominal frame-rate time. The source
    # pipeline must independently check native PTS before accepting any cut.
    candidates = [round(pair[0].seconds * 1000) for pair in scenes[1:]]
    return sorted(set(candidates))


def run(m, backend, media=None, tolerance_ms=200, scene_detector=None):
    started = time.perf_counter()
    result = {"schema": SCHEMA, **m, "detector": backend,
              "shot_boundaries_are_source_pts_verified": False,
              "dramatic_scenes_identified": False,
              "production_script_accepted": False,
              "reference_review_state": "independent_review" if m["independently_reviewed_cuts_ms"] is not None else "not_reviewed",
              "candidates": {}}
    existing = m["existing_ffmpeg_cuts_ms"]
    result["candidates"]["ffmpeg_existing"] = existing
    if backend != "existing":
        if media is None or not media.is_file() or media.stat().st_size > 2_000_000_000:
            raise ValueError("Bounded local original media is required")
        if source_hash(media) != m["source_video_sha256"]:
            raise ValueError("Original source SHA256 mismatch")
        if abs(probe_duration(media) - m["duration_ms"]) > 5000:
            raise ValueError("Original source duration mismatch")
        t = time.perf_counter()
        detected = scene_detector(media, backend) if scene_detector else scenedetect_cuts(media, backend)
        valid_cuts(detected, m["duration_ms"], "PySceneDetect")
        result["candidates"][f"pyscenedetect_{backend}"] = detected
        result["detector_seconds"] = round(time.perf_counter() - t, 3)
        result["verified_source_sha256"] = m["source_video_sha256"]
    if m["independently_reviewed_cuts_ms"] is not None:
        result["accuracy"] = {name: compare(cuts, m["independently_reviewed_cuts_ms"], tolerance_ms)
                              for name, cuts in result["candidates"].items()}
    else:
        result["accuracy"] = None
    result["wall_seconds"] = round(time.perf_counter() - started, 3)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--media", type=Path)
    p.add_argument("--detector", choices=["existing", "content", "adaptive"], default="existing")
    p.add_argument("--tolerance-ms", type=int, default=200)
    p.add_argument("--confirm-owner-media", action="store_true")
    args = p.parse_args()
    if args.output.exists():
        p.error("Refusing to overwrite evidence")
    if args.detector != "existing" and not args.confirm_owner_media:
        p.error("PySceneDetect requires confirmed authorized local source video")
    raw = args.manifest.read_bytes()
    if len(raw) > 100000:
        p.error("Oversize benchmark input")
    manifest = validate(json.loads(raw))
    result = run(manifest, args.detector, args.media, args.tolerance_ms)
    result["source_manifest_sha256"] = hashlib.sha256(raw).hexdigest()
    serialized = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    if len(serialized) > 200000:
        raise ValueError("Evidence file too large")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(serialized)
    print(args.detector, "shot proposals", len(result["candidates"].get(f"pyscenedetect_{args.detector}", manifest["existing_ffmpeg_cuts_ms"])),
          "reviewed ground truth present:", result["accuracy"] is not None)


if __name__ == "__main__":
    main()
