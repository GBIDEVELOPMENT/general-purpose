#!/usr/bin/env python3
"""Source-SHA-guarded preservation of bounded original-film Qwen *proposals*.

Only the owner-only, trusted-base original-source workflow can run this import
with its two private artifacts. No media, frame, PCM, credentials, or accepted
screenplay claims are imported. Never promote these two-second guesses to AV
facts. Reruns replace the same small paths, not vNN manuscripts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from owner_qwen_original_video_pilot import MODEL_ID, MODEL_SHA, SOURCES
from run_headless_video_description import FIELDS

ROOT = Path(__file__).resolve().parents[1]
MAX_REPORT = 12_000
MAX_PENDING = 10_000
MAX_METRICS = 5_000


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_json(path: Path, max_bytes: int) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    if not 0 < len(raw) <= max_bytes:
        raise ValueError("Original source proposal missing or oversized")
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError("Original source proposal is not a JSON object")
    return obj, raw


def review_original_qwen_report(ep: str, raw: dict) -> list[dict]:
    """Guard original-film lineage and every visible unverified-claim field."""
    if ep not in SOURCES:
        raise ValueError("Nonpilot original source model import")
    pin = SOURCES[ep]["sha256"]
    if (raw.get("schema") != "night-court-headless-video-description/1"
        or raw.get("owner_source_pilot_schema") != "night-court-original-qwen-picture-pilot/1"
        or raw.get("episode_id") != ep
        or raw.get("source_video_sha256") != pin
        or raw.get("verified_source_sha256") != pin
        or raw.get("original_avi_sha256_verified") != pin
        or raw.get("backend") != "qwen3vl"
        or raw.get("model_id") != MODEL_ID
        or raw.get("model_revision") != MODEL_SHA
        or raw.get("original_avi_download_count") != 1
        or raw.get("source_original_media_is_ephemeral") is not True
        or raw.get("no_source_clip_or_still_uploaded") is not True
        or raw.get("original_srt_or_dialogue_modified") is not False
        or raw.get("original_soundtrack_listened_to_or_uploaded") is not False
        or raw.get("actor_identity_or_voice_verified") is not False
        or raw.get("original_series_production_screenplay_accepted") is not False
        or raw.get("script_or_claim_independently_accepted") is not False
        or raw.get("whole_episode_visual_coverage_accepted") is not False):
        raise ValueError(ep + ": untrusted/misidentified/accepted source video report")
    windows = raw.get("windows")
    if not isinstance(windows, list) or len(windows) != 1:
        raise ValueError(ep + ": unbounded original-video window evidence")
    for w in windows:
        a, b = w.get("start_ms"), w.get("end_ms")
        if (type(a) is not int or type(b) is not int
            or not 0 <= a < b <= SOURCES[ep]["duration_ms"]
            or b - a != 2000 or w.get("candidate_cut_crossing") is not False
            or w.get("shot_partition_verified") is not False
            or w.get("source_AV_human_review_done") is not False
            or w.get("independently_accepted") is not False
            or w.get("status") not in ("machine_proposed", "requires_review")
            or not isinstance(w.get("id"), str) or not w["id"].startswith(ep + "-REAL-PICTURE-")):
            raise ValueError(ep + ": unbounded or falsely witnessed original-film interval")
        proposal = w.get("model_hypothesis")
        if proposal is not None and (
            not isinstance(proposal, dict) or set(proposal) != set(FIELDS)
            or any(not isinstance(value, str) or len(value) > 512
                   for value in proposal.values())):
            raise ValueError(ep + ": invalid/surprisingly large model description")
    return windows


def validate_bundle(episode: str, folder: Path) -> dict:
    report, report_bytes = checked_json(folder / f"nc-qwen-original-{episode}.json", MAX_REPORT)
    pending, pending_bytes = checked_json(folder / f"nc-qwen-pending-{episode}.json", MAX_PENDING)
    metrics, metric_bytes = checked_json(folder / f"nc-qwen-safe-metrics-{episode}.json", MAX_METRICS)
    windows = review_original_qwen_report(episode, report)
    pin = SOURCES[episode]["sha256"]
    if (pending.get("schema") != "night-court-visual-review-decisions/1"
        or pending.get("episode_id") != episode
        or pending.get("source_video_sha256") != pin
        or pending.get("model_report_sha256") != sha(report_bytes)
        or pending.get("reviewer_id") != "original-film-pending"
        or not isinstance(pending.get("decisions"), list)
        or len(pending["decisions"]) != len(FIELDS) * len(windows)):
        raise ValueError(episode + ": pending source-video decision ledger is not linked")
    fields_seen = set()
    for decision in pending["decisions"]:
        key = (decision.get("window_id"), decision.get("field"))
        if (key in fields_seen or key[0] not in {w["id"] for w in windows}
            or key[1] not in FIELDS or decision.get("verdict") != "deferred"
            or decision.get("direct_original_video_review_attested") is not False
            or decision.get("reviewer_text") is not None):
            raise ValueError(episode + ": forged/duplicated visual editorial acceptance")
        fields_seen.add(key)
    metric_entries = metrics.get("episodes")
    if (metrics.get("schema") != "night-court-original-qwen-source-safe-metrics/1"
        or metrics.get("machine_video_semantics_independently_accepted") is not False
        or metrics.get("production_screenplay_complete") is not False
        or metrics.get("original_source_media_or_audio_retained") is not False
        or not isinstance(metric_entries, list) or len(metric_entries) != 1
        or metric_entries[0].get("episode_id") != episode
        or metric_entries[0].get("source_video_sha256") != pin
        or metric_entries[0].get("exact_private_owner_model_report_sha256") != sha(report_bytes)
        or metric_entries[0].get("original_source_human_stage_reviewed") is not False):
        raise ValueError(episode + ": metrics cannot authenticate this model report")
    return {
        f"{episode}-original-qwen-visual-proposals.json": report_bytes,
        f"{episode}-original-qwen-review-pending.json": pending_bytes,
        f"{episode}-original-qwen-safe-metrics.json": metric_bytes,
    }


def preserve(artifact_root: Path, output: Path, episodes=("S01E01", "S09E19")) -> dict:
    # Validate the COMPLETE batch before touching any trusted saved state.
    bundles = {}
    for ep in episodes:
        if ep not in SOURCES or ep in bundles:
            raise ValueError("Invalid/duplicate owner-original-video episode")
        bundles[ep] = validate_bundle(ep, artifact_root / ep)
    output.mkdir(parents=True, exist_ok=True)
    changed = 0
    for ep in episodes:
        for name, raw in bundles[ep].items():
            path = output / name
            if not path.exists() or path.read_bytes() != raw:
                tmp = path.with_suffix(path.suffix + ".tmp")
                tmp.write_bytes(raw)
                tmp.replace(path)
                changed += 1
    return {"episodes": list(episodes), "files_changed": changed,
            "source_media_written": False, "independent_stage_actions_accepted": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", required=True, type=Path)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "saved-private/episode-finish-current")
    args = parser.parse_args()
    print(json.dumps(preserve(args.artifact_root, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
