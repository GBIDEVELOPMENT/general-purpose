#!/usr/bin/env python3
"""Produce a reproducible, reviewer-owned S01E01 audiovisual cut list.

No FTP access or media export is performed by default. --render requires a
local owner-held, SHA-verified original AVI and never writes media into Git.
Evidence clips are for source review; they are not independent acceptance.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKLIST = ROOT / "seasons/S01/S01E01/derived/editorial-review-v1/acceptance-worklist.json"
BOARD = ROOT / "catalog/av-script-reconstruction-queue.json"
SCENE = ROOT / "seasons/S01/S01E01/derived/scene-review-v3/scene-evidence-map.json"
OUT = ROOT / "seasons/S01/S01E01/derived/editorial-review-v1/review-cut-manifest.json"
SOURCE_RUNTIME_MS = 1448256
HANDLE_MS = 2000
MERGE_GAP_MS = 1000


def build(worklist=None, board=None, scene=None):
    p = copy.deepcopy(worklist if worklist is not None else json.loads(WORKLIST.read_text("utf-8")))
    q = board if board is not None else json.loads(BOARD.read_text("utf-8"))
    s = scene if scene is not None else json.loads(SCENE.read_text("utf-8"))
    if p.get("schema") != "night-court-s01e01-editorial-qa-packet/1" or p.get("episode_id") != "S01E01":
        raise ValueError("Wrong source editorial packet")
    ep = next((x for x in q["episodes"] if x["episode_id"] == "S01E01"), None)
    if ep is None or q.get("original_episode_records") != 193:
        raise ValueError("Source inventory missing original S01E01")
    meta = ep["source_metadata"]
    if (p["source_caption_sha256"] != meta["source_sha256"] or
        p["source_video_sha256"] != s["source_media_sha256"] or
        p["source_caption_sha256"] != s["original_subtitle_sha256"]):
        raise ValueError("Source AVI/SRT fingerprints disagree between worklist, scene and catalog")
    if p["review_scope_ms"] != [60000, 90000]:
        raise ValueError("Changed original pilot bounds")
    if (p["counts"]["source_speaking_turns"] != 11 or
        p["counts"]["visual_motion_observations"] != 6 or
        not meta["video_filename_identity_only"] or
        type(meta["video_size_bytes_candidate"]) is not int or
        meta["video_size_bytes_candidate"] <= 0):
        raise ValueError("Unreconciled original source review inventory")

    tasks = []
    for kind, rows, key, pending in (
        ("voice", p["voice_review_tasks"], "source_caption_interval_ms", "audio_text_confirmation"),
        ("visual", p["visual_review_tasks"], "source_interval_ms", "review_status"),
    ):
        for row in rows:
            interval = row[key]
            if (not isinstance(interval, list) or len(interval) != 2 or
                any(type(n) is not int for n in interval) or
                not 0 <= interval[0] < interval[1] <= SOURCE_RUNTIME_MS):
                raise ValueError("Invalid original source interval in " + row["task_id"])
            if kind == "voice" and row[pending] != "not_reviewed":
                raise ValueError("Source voice has already been accepted or changed")
            if kind == "visual" and row.get("continuous_video_observation_verified") is not False:
                raise ValueError("A sampled action cannot be declared continuous-video reviewed")
            tasks.append({
                "task_id": row["task_id"],
                "task_type": kind,
                "source_interval_ms": interval[:],
                "outside_existing_60000_90000_sample": interval[0] < 60000 or interval[1] > 90000,
            })
    if len(tasks) != 17 or len({x["task_id"] for x in tasks}) != 17:
        raise ValueError("Missing or duplicated voice/action review task")
    tasks.sort(key=lambda x: (x["source_interval_ms"][0], x["source_interval_ms"][1], x["task_id"]))
    windows = []
    for task in tasks:
        a, b = task["source_interval_ms"]
        start, end = max(0, a - HANDLE_MS), min(SOURCE_RUNTIME_MS, b + HANDLE_MS)
        if windows and start <= windows[-1]["end_ms"] + MERGE_GAP_MS:
            windows[-1]["end_ms"] = max(windows[-1]["end_ms"], end)
        else:
            windows.append({"start_ms": start, "end_ms": end})
    for i, w in enumerate(windows, 1):
        w["review_window_id"] = f"S01E01-RW-{i:02d}"
        w["duration_ms"] = w["end_ms"] - w["start_ms"]
        w["task_ids"] = [
            x["task_id"] for x in tasks
            if x["source_interval_ms"][0] >= w["start_ms"] and
               x["source_interval_ms"][1] <= w["end_ms"]
        ]
    assigned = [task_id for w in windows for task_id in w["task_ids"]]
    if len(assigned) != 17 or set(assigned) != {t["task_id"] for t in tasks}:
        raise ValueError("A review task is missing or duplicated across continuous clips")
    return {
        "schema": "night-court-source-hash-pinned-review-cut-manifest/1",
        "episode_id": "S01E01",
        "publication_status": "review_material_only_zero_av_acceptances",
        "source_video_sha256": p["source_video_sha256"],
        "source_caption_sha256": p["source_caption_sha256"],
        "source_video_filename_candidate": meta["video_filename_candidate"],
        "source_video_size_bytes_candidate": meta["video_size_bytes_candidate"],
        "source_runtime_ms": SOURCE_RUNTIME_MS,
        "existing_sample_scope_ms": p["review_scope_ms"],
        "preroll_postroll_ms": HANDLE_MS,
        "merge_gap_ms": MERGE_GAP_MS,
        "voice_tasks": 11,
        "visual_tasks": 6,
        "tasks": tasks,
        "continuous_review_windows": windows,
        "outside_existing_sample_task_ids": [
            x["task_id"] for x in tasks if x["outside_existing_60000_90000_sample"]
        ],
        "caveat": "Source timestamps are research cues. A cut list does not validate dialogue, cast identity, actions, inflection, or completeness.",
    }


def verify_local_video(path: Path, manifest: dict):
    if not path.is_file() or path.stat().st_size != manifest["source_video_size_bytes_candidate"]:
        raise ValueError("Owner source AVI missing or incorrect byte length")
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != manifest["source_video_sha256"]:
        raise ValueError("Owner source AVI checksum mismatch")


def render_owner_review_windows(source: Path, destination: Path, manifest: dict):
    """Render private local review media only after byte length and SHA verification."""
    verify_local_video(source, manifest)
    dest = destination.resolve()
    if dest == ROOT.parent.resolve() or ROOT.parent.resolve() in dest.parents:
        raise ValueError("Never generate copyrighted source excerpts inside repository checkout")
    dest.mkdir(parents=True, exist_ok=True)
    for w in manifest["continuous_review_windows"]:
        output = dest / (w["review_window_id"] + ".mp4")
        subprocess.run([
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-n",
            "-i", str(source.resolve()), "-ss", f'{w["start_ms"] / 1000:.3f}',
            "-t", f'{w["duration_ms"] / 1000:.3f}', "-map", "0:v:0",
            "-map", "0:a:0", "-c:v", "libx264", "-preset", "fast",
            "-crf", "20", "-c:a", "aac", "-movflags", "+faststart",
            str(output),
        ], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write metadata JSON only")
    parser.add_argument("--source-video", type=Path, help="owner-held original AVI")
    parser.add_argument("--render-to", type=Path, help="private destination outside git")
    args = parser.parse_args()
    manifest = build()
    if args.write:
        OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", "utf-8")
        print("Wrote safe metadata:", OUT)
    if bool(args.source_video) != bool(args.render_to):
        parser.error("--source-video and --render-to must be supplied together")
    if args.source_video:
        render_owner_review_windows(args.source_video, args.render_to, manifest)
    if not args.write and not args.source_video:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
