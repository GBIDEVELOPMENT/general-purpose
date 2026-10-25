#!/usr/bin/env python3
"""One trusted-source SHA-bound original-film Qwen visual-description pilot.

Only two pinned original Night Court episodes and bounded pre-reviewed picture
regions. No episode media, soundtrack, decoded stills, model weights, or FTP
credentials leave temporary owner-controlled runner storage. Output is compact
unreviewed video-model text + measurements, NOT a certified stage direction.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from time import perf_counter

from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate as pilot_candidate, retrieve
from s09e19_untimed_video_anchor_pilot import exact_candidate as late_candidate
from run_headless_video_description import benchmark, normalize

SOURCES = {
    "S01E01": {
        "sha256": "5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962",
        "duration_ms": 1448256,
        "candidate_starts_ms": tuple(range(75000, 88001, 1000)),
        "picture_context": "court-office-phone-original-reviewed-neighborhood",
        "physical_comedy_candidate_starts_ms": (845800, 846000, 845600, 846200, 847000),
        "physical_comedy_context": "court-bench-visible-hand-motion-source-sampled-neighborhood",
    },
    "S09E19": {
        "sha256": "51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649",
        "duration_ms": 1320144,
        "candidate_starts_ms": tuple(range(812000, 830001, 1000)),
        "picture_context": "restaurant-seated-guests-original-reviewed-neighborhood",
        "physical_comedy_candidate_starts_ms": (555800, 556000, 555600, 556200, 559000),
        "physical_comedy_context": "court-bench-object-handling-source-sampled-neighborhood",
    },
}
CLIP_MS = 2000
CUT_THRESHOLD = 0.18
MODEL_ID = "Qwen/Qwen3-VL-2B-Instruct"
MODEL_SHA = "89644892e4d85e24eaac8bacfd4f463576704203"
MAX_OUTPUT = 120_000


def sample_source(episode: str):
    if episode not in SOURCES:
        raise ValueError("Original source evidence limited to two exact pilot episodes")
    expected = SOURCES[episode]
    source = pilot_candidate() if episode == "S01E01" else late_candidate()
    if not isinstance(source, dict) or source.get("size_bytes", 0) > 350_000_000:
        raise ValueError("Owner original AVI size unbounded")
    remote = source.get("remote_path")
    if not isinstance(remote, str) or not remote.startswith("/downloads/Night Court TVRip S1-S9/"):
        raise ValueError("Unrecognized original video FTP inventory path")
    return expected, source


def candidate_cut_check(media: Path, start_ms: int, duration_ms: int = CLIP_MS):
    """Count *candidate* discontinuities in five-Hz low-resolution source video.

    FFmpeg's built-in scene expression reproducibly emitted a spurious change
    in every source-AVI excerpt (33/33 original windows), despite stable
    source-hashed 4/5-Hz source thumbnails. Compare neighboring decoded
    luminance frames instead, with 1 second of decoder pre-roll. This is an
    inexpensive selector, NEVER native-PTS or shot-continuity certification.
    """
    if type(start_ms) is not int or not 1000 <= start_ms <= 7_200_000:
        raise ValueError("Invalid original-source time or missing decoder pre-roll")
    if duration_ms != CLIP_MS:
        raise ValueError("Only two-second candidate windows allowed")
    fps, width, height, prior_ms = 5, 160, 90, 1000
    frame_bytes = width * height
    # A 5fps monochrome scan uses only 216KB of decoded temporary frame
    # bytes; no frame, soundtrack or source movie is stored as an artifact.
    result = subprocess.run([
        "ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error",
        "-threads", "1", "-filter_threads", "1",
        "-ss", f"{(start_ms-prior_ms)/1000:.3f}", "-i", str(media),
        "-t", f"{(duration_ms+prior_ms)/1000:.3f}", "-map", "0:v:0",
        "-an", "-sn", "-dn",
        "-vf", f"fps={fps},scale={width}:{height}:flags=bilinear,format=gray",
        "-pix_fmt", "gray", "-f", "rawvideo", "-"
    ], capture_output=True, timeout=90, check=True)
    raw = result.stdout
    if len(raw) != frame_bytes * 15:
        raise ValueError("Original cut scan frame-count mismatch; abstain")
    frames = [memoryview(raw)[i:i + frame_bytes]
              for i in range(0, len(raw), frame_bytes)]
    # Frames 0-4 seed the decoder/reference; consecutive pairs ending at
    # indices 5..14 correspond to the requested two-second source region.
    # Using all pixels is deterministic and much less brittle on compressed
    # legacy AVI than FFmpeg's uncalibrated scene score at an arbitrary seek.
    # Historical source-SHA-backed stills: low-motion S01 spans ~1-3 mean
    # 8-bit luma units, abrupt visual changes ~17-33; S09 jumps ~10-17.
    threshold = 9.5
    changes = 0
    for i in range(5, len(frames)):
        mean_abs = sum(abs(b - a) for a, b in zip(frames[i-1], frames[i])) / frame_bytes
        if mean_abs > threshold:
            changes += 1
    return changes

def candidate_offsets(episode: str, focus: str):
    if episode not in SOURCES or focus not in ("observational", "physical_comedy"):
        raise ValueError("Only two source-verified original pilot modes permitted")
    key = "candidate_starts_ms" if focus == "observational" else "physical_comedy_candidate_starts_ms"
    return SOURCES[episode][key]


def select_bounded_candidate(media: Path, episode: str, focus: str = "observational"):
    if episode not in SOURCES:
        raise ValueError("Unrecognized episode")
    offsets = candidate_offsets(episode, focus)
    report = []
    selected = None
    for start in offsets:
        count = candidate_cut_check(media, start)
        report.append({"start_ms": start, "candidate_image_changes": count})
        if count == 0:
            selected = start
            break
    if selected is None:
        # Safe numeric probe: no film pixels or model captions in exception.
        raise ValueError("No proposed source-shot-safe interval: " + json.dumps(report, separators=(',', ':')))
    return selected, report


def source_benchmark_manifest(episode: str, start_ms: int, focus: str = "observational"):
    source = SOURCES.get(episode)
    if source is None or start_ms not in candidate_offsets(episode, focus):
        raise ValueError("Only fixed pilot original-picture region is permitted")
    return normalize({
        "schema": "night-court-video-benchmark-windows/1",
        "episode_id": episode,
        "source_video_sha256": source["sha256"],
        "duration_ms": source["duration_ms"],
        "caption_source_sha256": None,  # S09 original witness is untimed.
        "windows": [{
            "id": f"{episode}-REAL-PICTURE-CANDIDATE-01",
            "start_ms": start_ms,
            "end_ms": start_ms + CLIP_MS,
            "selection_reason": source["picture_context"] if focus == "observational" else source["physical_comedy_context"],
            "candidate_cut_crossing": False,  # FFmpeg scan checked only.
        }],
    })


def trusted_owner_run(episode: str, output: Path, focus: str = "observational"):
    expected, item = sample_source(episode)
    password = os.environ.get("FTP_PASSWORD")
    if not password:
        raise ValueError("Owner-secret source mode only; no anonymous source access")
    if output.exists():
        raise ValueError("Never overwrite real original-video research evidence")
    started = perf_counter()
    with tempfile.TemporaryDirectory(prefix="night-court-original-qwen-") as scratch:
        video = Path(scratch) / item["basename"]
        ftp = connect(os.environ.get("FTP_HOST", "wood.seedhost.eu"),
                      os.environ.get("FTP_USER", "ianseeds"),
                      password, "ftp")
        try:
            actual = retrieve(ftp, item, video)
        finally:
            try:
                ftp.quit()
            except Exception:
                ftp.close()
        # Model subprocesses must not receive FTP_PASSWORD after source read.
        os.environ.pop("FTP_PASSWORD", None)
        password = None
        if actual != expected["sha256"]:
            raise ValueError("Original source SHA mismatch, no visual inference")
        elapsed_fetch = perf_counter() - started
        clip_start, scan = select_bounded_candidate(video, episode, focus)
        selected = source_benchmark_manifest(episode, clip_start, focus)
        result = benchmark(selected, "qwen3vl", media=video,
                           revision=MODEL_SHA, device="cpu",
                           fps=1, width=256, max_new_tokens=256)
        result.update({
            "owner_source_pilot_schema": "night-court-original-qwen-picture-pilot/1",
            "source_reference_model_schema": "night-court-headless-video-description/1",
            "original_avi_download_count": 1,
            "source_focus": focus,
            "original_avi_sha256_verified": actual,
            "original_source_retrieval_wall_seconds": round(elapsed_fetch, 3),
            "pre_model_original_cut_candidate_checks": scan,
            "cut_candidate_detector": "5fps_gray160x90_mean_absolute_frame_change_gt_9.5_with_one_second_preroll",
            "cut_detector_method_not_source_PTS_verified": True,
            "cut_detection_is_editorial_proposal_only": True,
            "original_native_decoded_frame_pts_human_verified": False,
            "original_srt_or_dialogue_modified": False,
            "original_soundtrack_listened_to_or_uploaded": False,
            "actor_identity_or_voice_verified": False,
            "no_source_clip_or_still_uploaded": True,
            "whole_episode_visual_coverage_accepted": False,
            "original_series_production_screenplay_accepted": False,
        })
        if any(row.get("independently_accepted") is not False
               for row in result["windows"]):
            raise ValueError("Model cannot certify original video physical action")
        encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
        if len(encoded) > MAX_OUTPUT:
            raise ValueError("Original derived model report exceeds text budget")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(encoded)
    # All source AVI bytes, temporary clips and weights stay outside Git.
    print(episode, "source-SHA-correct original Qwen visual inference",
          len(result["windows"]), "unaccepted model windows,",
          round(result["wall_seconds"], 3), "model-tool seconds")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode", choices=sorted(SOURCES), required=True)
    parser.add_argument("--focus", choices=("observational", "physical_comedy"), default="observational")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--owner-confirm-original-source", action="store_true")
    args = parser.parse_args()
    if not args.owner_confirm_original_source:
        parser.error("This job requires explicit trusted original-series source confirmation")
    trusted_owner_run(args.episode, args.output, args.focus)


if __name__ == "__main__":
    main()
