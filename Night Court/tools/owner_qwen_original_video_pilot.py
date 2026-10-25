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
        "candidate_starts_ms": (86000, 82000, 84000, 88000, 80000),
        "picture_context": "court-office-phone-original-reviewed-neighborhood",
    },
    "S09E19": {
        "sha256": "51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649",
        "duration_ms": 1320144,
        "candidate_starts_ms": (820000, 816000, 818000, 824000, 826000),
        "picture_context": "restaurant-seated-guests-original-reviewed-neighborhood",
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
    """Full native frame-rate low-resolution cut-candidate scan on source AVI.

    This does NOT prove there is no true shot cut. It only rejects detected
    large image changes so inferred continuous action is less misleading.
    """
    if type(start_ms) is not int or not 0 <= start_ms <= 7_200_000:
        raise ValueError("Invalid original-source time")
    if duration_ms != CLIP_MS:
        raise ValueError("Only two-second candidate windows allowed")
    result = subprocess.run([
        "ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "info",
        "-threads", "1", "-filter_threads", "1",
        "-ss", f"{start_ms/1000:.3f}", "-i", str(media),
        "-t", f"{duration_ms/1000:.3f}", "-map", "0:v:0",
        "-an", "-sn", "-dn",
        "-vf", f"scale=160:-2,select='gt(scene,{CUT_THRESHOLD})',showinfo",
        "-f", "null", "-"
    ], capture_output=True, text=True, timeout=90, check=True)
    # showinfo processes only selected image-change frames after the select.
    return len(re.findall(r"Parsed_showinfo[^\n]*\bn:\s*\d+", result.stderr))


def select_bounded_candidate(media: Path, episode: str):
    if episode not in SOURCES:
        raise ValueError("Unrecognized episode")
    report = []
    selected = None
    for start in SOURCES[episode]["candidate_starts_ms"]:
        count = candidate_cut_check(media, start)
        report.append({"start_ms": start, "candidate_image_changes": count})
        if count == 0:
            selected = start
            break
    if selected is None:
        raise ValueError("No proposed source-shot-safe interval from bounded candidate set")
    return selected, report


def source_benchmark_manifest(episode: str, start_ms: int):
    source = SOURCES.get(episode)
    if source is None or start_ms not in source["candidate_starts_ms"]:
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
            "selection_reason": source["picture_context"],
            "candidate_cut_crossing": False,  # FFmpeg scan checked only.
        }],
    })


def trusted_owner_run(episode: str, output: Path):
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
        clip_start, scan = select_bounded_candidate(video, episode)
        selected = source_benchmark_manifest(episode, clip_start)
        result = benchmark(selected, "qwen3vl", media=video,
                           revision=MODEL_SHA, device="cpu",
                           fps=1, width=256, max_new_tokens=256)
        result.update({
            "owner_source_pilot_schema": "night-court-original-qwen-picture-pilot/1",
            "source_reference_model_schema": "night-court-headless-video-description/1",
            "original_avi_download_count": 1,
            "original_avi_sha256_verified": actual,
            "original_source_retrieval_wall_seconds": round(elapsed_fetch, 3),
            "pre_model_original_cut_candidate_checks": scan,
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
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--owner-confirm-original-source", action="store_true")
    args = parser.parse_args()
    if not args.owner_confirm_original_source:
        parser.error("This job requires explicit trusted original-series source confirmation")
    trusted_owner_run(args.episode, args.output)


if __name__ == "__main__":
    main()
