#!/usr/bin/env python3
"""Bounded, source-SHA-checked, headless original-video description benchmark.

Consumes existing multigoal review packets or a small explicit benchmark manifest.
Does not fetch FTP/media, change captions, identify actors or certify scripts.
An optional local model generates *unreviewed* scene-action hypotheses only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

SCHEMA = "night-court-headless-video-description/1"
PACKET_SCHEMA = "night-court-multigoal-original-AV-review/1"
INPUT_SCHEMA = "night-court-video-benchmark-windows/1"
MODELS = {
    "smolvlm2": "HuggingFaceTB/SmolVLM2-500M-Video-Instruct",
    "qwen3vl": "Qwen/Qwen3-VL-2B-Instruct",
}
MAX_WINDOWS = 12
MAX_DURATION_MS = 15000
MAX_TOTAL_MS = 120000
MAX_FRAMES = 36
MAX_VIDEO_BYTES = 2_000_000_000
MAX_CLIP_BYTES = 40_000_000
SHA = re.compile(r"[0-9a-f]{64}\Z")
EPISODE = re.compile(r"S0[1-9]E[0-9]{2}\Z")
REVISION = re.compile(r"[0-9a-f]{40,64}\Z")

PROMPT = (
    "Describe only observable visual content in this short, silent television "
    "video in chronological order. Respond as a JSON object with exactly these "
    "keys: setting, camera, people_and_positions, actions, props, entrances_exits, "
    "physical_comedy, reactions, uncertainty, proposed_stage_direction. Each "
    "value must be a concise string, or an empty string if unseen. Describe "
    "people anonymously (person_1 etc), never name actors or characters. "
    "Do not invent dialogue, sounds, motives, inner feelings, offscreen events "
    "or causes. A camera cut is not proof of a scene change. Make uncertain "
    "visual claims explicit. Stage directions are proposed, not verified."
)
FIELDS = (
    "setting", "camera", "people_and_positions", "actions", "props",
    "entrances_exits", "physical_comedy", "reactions", "uncertainty",
    "proposed_stage_direction",
)


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for buf in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(buf)
    return digest.hexdigest()


def bounded_int(value, lo, hi, name):
    if type(value) is not int or not lo <= value <= hi:
        raise ValueError(f"Invalid {name}, expected integer in [{lo}, {hi}]")
    return value


def normalize(raw):
    if not isinstance(raw, dict):
        raise ValueError("Manifest must be an object")
    schema = raw.get("schema")
    if schema == PACKET_SCHEMA:
        if raw.get("script_or_claim_independently_accepted") is not False:
            raise ValueError("Source review packet falsely accepted")
        episode = raw.get("episode_id")
        digest = raw.get("original_video_sha256")
        duration = raw.get("original_duration_ms")
        windows = []
        for row in raw.get("requests", []):
            if row.get("independently_accepted") is not False or row.get("original_continuous_AV_review_done") is not False:
                raise ValueError("Review status cannot be promoted")
            times = row.get("source_window_ms")
            windows.append({
                "id": row.get("id"), "start_ms": times[0] if isinstance(times, list) and len(times) == 2 else None,
                "end_ms": times[1] if isinstance(times, list) and len(times) == 2 else None,
                "selection_reason": row.get("selection_reason"),
                "candidate_cut_crossing": False if row.get("candidate_shot_partition_not_verified") is not None else None,
            })
        caption_digest = None
    elif schema == INPUT_SCHEMA:
        episode = raw.get("episode_id")
        digest = raw.get("source_video_sha256")
        duration = raw.get("duration_ms")
        caption_digest = raw.get("caption_source_sha256")
        windows = raw.get("windows")
    else:
        raise ValueError("Unknown benchmark manifest schema")
    if not isinstance(episode, str) or not EPISODE.fullmatch(episode):
        raise ValueError("Invalid original-series episode")
    if not isinstance(digest, str) or not SHA.fullmatch(digest):
        raise ValueError("Missing source video SHA256")
    if caption_digest is not None and (not isinstance(caption_digest, str) or not SHA.fullmatch(caption_digest)):
        raise ValueError("Invalid caption witness SHA256")
    bounded_int(duration, 1000, 7_200_000, "source duration")
    if not isinstance(windows, list) or not 1 <= len(windows) <= MAX_WINDOWS:
        raise ValueError("Expected 1-12 candidate review windows")
    cleaned, ids = [], set()
    total = 0
    for row in windows:
        if not isinstance(row, dict):
            raise ValueError("Window must be an object")
        ident = row.get("id")
        a = bounded_int(row.get("start_ms"), 0, duration - 1, "start_ms")
        b = bounded_int(row.get("end_ms"), 1, duration, "end_ms")
        if a >= b or b - a > MAX_DURATION_MS or not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", ident) or ident in ids:
            raise ValueError("Bad, long or repeated review window")
        if row.get("candidate_cut_crossing") is not False:
            raise ValueError("Unknown or cross-cut video sequence: abstain")
        ids.add(ident)
        total += b - a
        cleaned.append({
            "id": ident, "start_ms": a, "end_ms": b,
            "selection_reason": str(row.get("selection_reason") or "unspecified")[:100],
            "candidate_cut_crossing": False,
        })
    if total > MAX_TOTAL_MS:
        raise ValueError("Excessive original clip sampling requested")
    return {
        "episode_id": episode, "source_video_sha256": digest,
        "caption_source_sha256": caption_digest, "duration_ms": duration,
        "windows": cleaned, "total_requested_ms": total,
    }


def ffprobe_info(media: Path):
    raw = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=avg_frame_rate,r_frame_rate,time_base:format=duration",
         "-of", "json", str(media)],
        check=True, capture_output=True, text=True, timeout=45,
    )
    data = json.loads(raw.stdout)
    if not data.get("streams"):
        raise ValueError("Source video stream missing")
    duration = float(data["format"]["duration"])
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("Invalid ffprobe source duration")
    return {"duration_ms": round(duration * 1000), "stream": data["streams"][0]}


def make_clip(media: Path, window: dict, output: Path, fps: int, width: int):
    start = window["start_ms"] / 1000
    length = (window["end_ms"] - window["start_ms"]) / 1000
    if math.ceil(length * fps) > MAX_FRAMES:
        raise ValueError("Requested decoder frame budget exceeded")
    command = [
        "ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error",
        "-ss", f"{start:.3f}", "-i", str(media), "-t", f"{length:.3f}",
        "-map", "0:v:0", "-an", "-sn", "-dn",
        "-vf", f"fps={fps},scale={width}:-2",
        "-frames:v", str(MAX_FRAMES), "-c:v", "libx264",
        "-preset", "ultrafast", "-crf", "32", "-pix_fmt", "yuv420p",
        "-y", str(output),
    ]
    subprocess.run(command, check=True, capture_output=True, timeout=120)
    if not output.is_file() or not 0 < output.stat().st_size <= MAX_CLIP_BYTES:
        raise ValueError("Temporary video exceeds clip budget or missing")


def parse_hypothesis(text):
    # Model output is treated as untrusted source data, never commands or facts.
    if not isinstance(text, str):
        raise ValueError("Model output must be text")
    raw = text.strip()[:12000]
    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        return None, "non_json_model_output"
    try:
        item = json.loads(match.group(0))
    except (ValueError, TypeError):
        return None, "malformed_model_json"
    if not isinstance(item, dict) or set(item) != set(FIELDS) or any(not isinstance(item[k], str) or len(item[k]) > 1200 for k in FIELDS):
        return None, "bad_model_fields"
    return {field: item[field] for field in FIELDS}, None


class LocalVideoModel:
    """Actual Transformers local-video inference, lazily initialized; no remote API."""

    def __init__(self, backend: str, revision: str, device: str):
        import torch
        from transformers import AutoProcessor
        model_id = MODELS[backend]
        self.processor = AutoProcessor.from_pretrained(model_id, revision=revision, trust_remote_code=False)
        if backend == "smolvlm2":
            from transformers import AutoModelForImageTextToText
            self.model = AutoModelForImageTextToText.from_pretrained(
                model_id, revision=revision, trust_remote_code=False,
                torch_dtype=torch.float32 if device == "cpu" else torch.float16,
            ).to(device)
        else:
            from transformers import Qwen3VLForConditionalGeneration
            self.model = Qwen3VLForConditionalGeneration.from_pretrained(
                model_id, revision=revision, trust_remote_code=False,
                dtype="auto", device_map="cpu" if device == "cpu" else "auto",
            )
        self.model.eval()
        self.torch = torch

    def describe(self, clip: Path) -> str:
        messages = [{"role": "user", "content": [
            {"type": "video", "path": str(clip)}, {"type": "text", "text": PROMPT}
        ]}]
        inputs = self.processor.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=True,
            return_dict=True, return_tensors="pt",
        ).to(self.model.device)
        with self.torch.inference_mode():
            out = self.model.generate(**inputs, do_sample=False, max_new_tokens=384)
        trimmed = [
            row[len(prompt):] for prompt, row in zip(inputs["input_ids"], out)
        ]
        return self.processor.batch_decode(trimmed, skip_special_tokens=True)[0]


def benchmark(manifest, backend, media=None, revision=None, device="cpu",
              fps=2, width=320, model=None):
    started = time.perf_counter()
    output = {
        "schema": SCHEMA, **{k: manifest[k] for k in (
            "episode_id", "source_video_sha256", "caption_source_sha256",
            "duration_ms", "total_requested_ms"
        )},
        "backend": backend, "model_id": MODELS.get(backend),
        "model_revision": revision, "prompt_sha256": hashlib.sha256(PROMPT.encode()).hexdigest(),
        "video_sampling_fps": fps, "video_width_pixels": width,
        "source_original_media_is_ephemeral": True, "script_or_claim_independently_accepted": False,
        "windows": [],
    }
    if backend == "plan":
        for w in manifest["windows"]:
            output["windows"].append({**w, "status": "awaiting_source_model_pass",
                "independently_accepted": False, "source_AV_human_review_done": False})
        output["wall_seconds"] = round(time.perf_counter() - started, 3)
        return output
    if not media or not media.is_file() or not media.stat().st_size <= MAX_VIDEO_BYTES:
        raise ValueError("Original local video absent or unbounded")
    t = time.perf_counter()
    actual = sha_file(media)
    if actual != manifest["source_video_sha256"]:
        raise ValueError("SOURCE SHA256 MISMATCH; no inference permitted")
    info = ffprobe_info(media)
    if abs(info["duration_ms"] - manifest["duration_ms"]) > 5000:
        raise ValueError("Original source duration mismatch")
    output["verified_source_sha256"] = actual
    output["source_ffprobe"] = info
    output["verify_seconds"] = round(time.perf_counter() - t, 3)
    if model is None:
        model = LocalVideoModel(backend, revision, device)
    with tempfile.TemporaryDirectory(prefix="night-court-video-") as tmp:
        for index, window in enumerate(manifest["windows"]):
            name = Path(tmp) / f"window_{index:02d}.mp4"
            begin = time.perf_counter()
            make_clip(media, window, name, fps, width)
            decode_seconds = round(time.perf_counter() - begin, 3)
            begin = time.perf_counter()
            try:
                response = model.describe(name)
                inference_seconds = round(time.perf_counter() - begin, 3)
                parsed, error = parse_hypothesis(response)
                row = {**window, "status": "machine_proposed" if parsed else "requires_review",
                       "model_hypothesis": parsed, "model_output_error": error,
                       "model_response_excerpt": None if parsed else response[:800],
                       "clip_sha256_ephemeral": sha_file(name),
                       "decode_seconds": decode_seconds,
                       "inference_seconds": inference_seconds,
                       "independently_accepted": False, "source_AV_human_review_done": False}
            finally:
                name.unlink(missing_ok=True)
            output["windows"].append(row)
    output["wall_seconds"] = round(time.perf_counter() - started, 3)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--backend", choices=["plan", *MODELS], default="plan")
    parser.add_argument("--media", type=Path)
    parser.add_argument("--model-revision", help="Immutable full model commit SHA, required for inference")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--fps", type=int, choices=[1, 2, 3], default=2)
    parser.add_argument("--width", type=int, choices=[256, 320, 448], default=320)
    parser.add_argument("--confirm-owner-media", action="store_true")
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve() == args.manifest.resolve():
        parser.error("Refusing to overwrite existing evidence")
    if args.backend != "plan":
        if not args.confirm_owner_media or not args.media:
            parser.error("Local model inference requires explicit owner media consent")
        if not args.model_revision or not REVISION.fullmatch(args.model_revision):
            parser.error("An immutable model commit SHA is required")
        if args.fps * MAX_DURATION_MS // 1000 > MAX_FRAMES:
            parser.error("Frame budget exceeded")
    raw = args.manifest.read_bytes()
    if len(raw) > 150000:
        parser.error("Manifest exceeds budget")
    manifest = normalize(json.loads(raw))
    result = benchmark(manifest, args.backend, args.media, args.model_revision,
                       args.device, args.fps, args.width)
    result["source_manifest_sha256"] = hashlib.sha256(raw).hexdigest()
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    if len(encoded) > 100000:
        raise ValueError("Output evidence exceeds byte budget")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(f"{manifest['episode_id']}: {len(result['windows'])} "
          f"{args.backend} windows; source script remains unaccepted")


if __name__ == "__main__":
    main()
