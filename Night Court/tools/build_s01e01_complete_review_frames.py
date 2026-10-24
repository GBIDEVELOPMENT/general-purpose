#!/usr/bin/env python3
"""Trusted-source S01E01 reviewer contact sheets, never script acceptance.

Default operations are offline and credential-free. Trusted FTP retrieval
runs only when explicitly asked by an owner-only base-pinned GitHub workflow.
No original video/audio or identifiable voice model data are retained.
"""
from __future__ import annotations

import argparse
import ftplib
import hashlib
import json
import math
import os
import subprocess
import tempfile
from pathlib import Path

from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate, retrieve

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "seasons/S01/S01E01/derived/editorial-review-v1/review-cut-manifest.json"
SOURCE_SRT = ROOT / ("seasons/S01/S01E01/dialogue/versions/"
    "s01-internal-dvdrip-xvid-sprinter-english--aa9f77600cd9f2b6/original.srt")
ROOT_REPO = ROOT.parent.resolve()
RATE = 4
FRAME_STEP_MS = 250
PAGE_SIZE = 40
MAX_TOTAL_BYTES = 18_000_000


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_manifest():
    m = json.loads(MANIFEST.read_text("utf-8"))
    if (m.get("schema") != "night-court-source-hash-pinned-review-cut-manifest/1"
        or m.get("episode_id") != "S01E01"
        or m.get("source_video_sha256") !=
           "5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
        or m.get("source_caption_sha256") != sha(SOURCE_SRT)
        or m.get("publication_status") != "review_material_only_zero_av_acceptances"
        or m.get("voice_tasks") != 11 or m.get("visual_tasks") != 6
        or len(m.get("tasks", [])) != 17
        or len(m.get("continuous_review_windows", [])) != 1
        or len(set(t["task_id"] for t in m["tasks"])) != 17):
        raise ValueError("Untrusted or inconsistent original source review manifest")
    w = m["continuous_review_windows"][0]
    if (w["review_window_id"] != "S01E01-RW-01" or
        [w["start_ms"], w["end_ms"]] != [56912, 93074] or
        w["duration_ms"] != 36162 or
        set(w["task_ids"]) != {x["task_id"] for x in m["tasks"]}):
        raise ValueError("Original 17-task source window changed")
    for t in m["tasks"]:
        a, b = t["source_interval_ms"]
        if not (type(a) is int and type(b) is int and 56912 <= a < b <= 93074):
            raise ValueError("Source task falls outside exact original cut")
    return m


def sample_plan(m):
    w = m["continuous_review_windows"][0]
    start, end = w["start_ms"], w["end_ms"]
    # Four-hertz sampling of a source *cut* padded to the next 250ms tick;
    # nominal indexes do NOT certify original frame presentation timestamps.
    count = math.ceil((end - start) / FRAME_STEP_MS)
    if not 100 <= count <= 160:
        raise ValueError("Visual sampling cap exceeded")
    return {"start_ms": start, "end_required_ms": end,
            "end_sampling_ms": start + count * FRAME_STEP_MS,
            "sample_count": count, "sampling_hz": RATE}


def execute(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=160)


def capture(original: Path, output: Path, manifest):
    p = sample_plan(manifest)
    if not original.is_file() or original.stat().st_size != manifest["source_video_size_bytes_candidate"]:
        raise ValueError("Original AVI byte count mismatch")
    if sha(original) != manifest["source_video_sha256"]:
        raise ValueError("Original AVI fingerprint mismatch")
    dest = output.resolve()
    if dest == ROOT_REPO or ROOT_REPO in dest.parents:
        raise ValueError("Never save derived original-video frames inside the Git checkout")
    if output.exists():
        raise ValueError("Refuse existing output directory")
    output.mkdir(parents=True)
    frames = output / "frames"
    frames.mkdir()
    execute(
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
        "-ss", f'{p["start_ms"] / 1000:.3f}', "-i", str(original),
        "-t", f'{(p["end_sampling_ms"] - p["start_ms"]) / 1000:.3f}',
        "-map", "0:v:0", "-an", "-vf", f"fps={RATE},scale=320:-2",
        "-q:v", "7", "-frames:v", str(p["sample_count"]), str(frames / "frame-%03d.jpg"),
    )
    actual = sorted(frames.glob("frame-*.jpg"))
    if len(actual) != p["sample_count"]:
        raise ValueError("Missing original-video sampled frames")
    entries = []
    for ix, image in enumerate(actual):
        if (image.name != f"frame-{ix+1:03d}.jpg"
            or not 100 < image.stat().st_size < 150_000):
            raise ValueError("Missing or unexpectedly large JPEG still")
        nominal_ms = p["start_ms"] + ix * FRAME_STEP_MS
        entries.append({
            "index": ix + 1,
            "nominal_video_time_ms": nominal_ms,
            "time_basis": "nominal_four_hz_source_cut_index_not_verified_original_frame_pts",
            "path": "frames/" + image.name,
            "sha256": sha(image),
            "source_task_candidates_not_verified": [
                t["task_id"] for t in manifest["tasks"]
                if t["source_interval_ms"][0] <= nominal_ms <= t["source_interval_ms"][1]
            ],
            "content_reviewed": False,
            "continuous_motion_verified": False,
            "speaker_identity_verified": False
        })
    sheets = []
    for first in range(0, p["sample_count"], PAGE_SIZE):
        page = len(sheets) + 1
        sheet = output / f"contact-{page:02d}.jpg"
        execute(
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
            "-start_number", str(first + 1), "-i", str(frames / "frame-%03d.jpg"),
            "-vf", "tile=8x5", "-frames:v", "1", str(sheet),
        )
        if not 1000 < sheet.stat().st_size < 3_000_000:
            raise ValueError("Missing/oversized review sheet")
        sheets.append({
            "path": sheet.name,
            "sha256": sha(sheet),
            "first_frame_index": first + 1,
            "last_frame_index": min(first + PAGE_SIZE, p["sample_count"]),
        })
    if sum(x.stat().st_size for x in output.rglob("*") if x.is_file()) > MAX_TOTAL_BYTES:
        raise ValueError("Owner review image artifact exceeds compact package size cap")
    result = {
        "schema": "night-court-s01e01-complete-bounded-review-frames/1",
        "source_episode": "S01E01",
        "source_video_sha256": manifest["source_video_sha256"],
        "source_caption_sha256": manifest["source_caption_sha256"],
        "original_media_size_bytes": manifest["source_video_size_bytes_candidate"],
        "review_window_id": "S01E01-RW-01",
        "source_review_window_ms": [p["start_ms"], p["end_required_ms"]],
        "sample_extraction_window_ms": [p["start_ms"], p["end_sampling_ms"]],
        "nominal_frames_per_second": RATE,
        "frames": entries,
        "contact_sheets": sheets,
        "relevant_review_task_ids": sorted(t["task_id"] for t in manifest["tasks"]),
        "audio_or_original_movie_in_artifact": False,
        "sampled_frame_contents_independently_reviewed": False,
        "original_video_mouth_and_voice_synchronization_verified": False,
        "continuous_video_action_timing_verified": False,
        "source_cue_audio_synchronization_verified": False,
        "actor_identity_or_emotional_delivery_verified": False,
        "production_script_accepted": False,
        "caveats": [
            "4fps stills are discontinuous, even across a complete original review interval.",
            "Frame time indexes are nominal; original presentation timestamps require separate inspection.",
            "A frame adjacent to original caption time cannot establish that a visible person spoke it.",
            "No audio, voiceprint, personal credential, AVI, or raw model weights in output."
        ],
    }
    (output / "frame-index.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", "utf-8"
    )
    return result


def ftp_capture(output):
    item = candidate()
    manifest = source_manifest()
    if (item["basename"] != manifest["source_video_filename_candidate"]
        or item["size_bytes"] != manifest["source_video_size_bytes_candidate"]):
        raise ValueError("S01E01 FTP candidate changed; resolve video identity first")
    password = os.getenv("FTP_PASSWORD")
    if not password:
        raise ValueError("Trusted source step requires owner FTP_PASSWORD")
    with tempfile.TemporaryDirectory(prefix="night-court-source-cut-") as tmp:
        media = Path(tmp) / item["basename"]
        ftp = connect(os.getenv("FTP_HOST", "wood.seedhost.eu"),
                      os.getenv("FTP_USER", "ianseeds"), password, "ftp")
        try:
            received = retrieve(ftp, item, media)
        finally:
            try:
                ftp.quit()
            except ftplib.all_errors:
                ftp.close()
        if received != manifest["source_video_sha256"]:
            raise ValueError("Retrieved source AVI differs from approved hash")
        capture(media, output, manifest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ftp", action="store_true")
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    if not args.ftp:
        ap.error("Source collection only runs in the trusted owner FTP workflow")
    ftp_capture(args.output)
    print("Source-approved 36.25s silent still packet; review gates remain unaccepted")


if __name__ == "__main__":
    main()
