"""Read-only rTorrent inventory analysis.

All findings are suggestions grounded in current snapshots, never proof that
payload bytes can be safely reclaimed or that a transfer is permanently stalled.
"""
from __future__ import annotations
from datetime import datetime, timezone

def _summary(row: dict) -> dict:
    keys = ("hash", "name", "size_bytes", "downloaded_bytes", "uploaded_bytes",
            "ratio", "active", "started", "complete", "down_bytes_per_sec",
            "up_bytes_per_sec", "first_started_at", "finished_at")
    return {key: row.get(key) for key in keys}

def analyze(rows: list[dict], server: str, *, target_ratio: float = 1.0,
            limit: int = 20, now: int | None = None) -> dict:
    if not 0 <= target_ratio <= 100000:
        raise ValueError("target_ratio must be between 0 and 100000")
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    if now is None:
        now = int(datetime.now(timezone.utc).timestamp())
    finished = [r for r in rows if r["complete"]]
    incomplete = [r for r in rows if not r["complete"]]
    metadata = [r for r in incomplete if r["size_bytes"] <= 1]
    zero_rate = [r for r in incomplete if r["down_bytes_per_sec"] == 0]
    below_ratio = [r for r in finished if r["ratio"] < target_ratio]
    eligible = [r for r in finished if r["ratio"] >= target_ratio]
    eligible.sort(key=lambda r: (not r["active"], r["size_bytes"]), reverse=True)
    def age(row):
        stamp = row.get("first_started_at")
        return max(0, now - stamp) if isinstance(stamp, int) and stamp > 0 and stamp <= now else None
    return {
        "server": server, "snapshot_at": now, "total": len(rows),
        "logical_size_bytes": sum(r["size_bytes"] for r in rows),
        "downloaded_bytes": sum(r["downloaded_bytes"] for r in rows),
        "uploaded_bytes": sum(r["uploaded_bytes"] for r in rows),
        "currently_uploading_bytes_per_sec": sum(r["up_bytes_per_sec"] for r in rows),
        "currently_downloading_bytes_per_sec": sum(r["down_bytes_per_sec"] for r in rows),
        "complete_count": len(finished), "incomplete_count": len(incomplete),
        "inactive_count": sum(not r["active"] for r in rows),
        "incomplete_zero_download_rate_count": len(zero_rate),
        "metadata_placeholder_count": len(metadata),
        "complete_below_target_ratio_count": len(below_ratio),
        "complete_meeting_target_ratio_count": len(eligible),
        "incomplete_zero_download_rate": [_summary(r) for r in zero_rate[:limit]],
        "metadata_placeholders": [_summary(r) for r in metadata[:limit]],
        "below_target_ratio": [_summary(r) for r in sorted(below_ratio, key=lambda r:r["ratio"])[:limit]],
        "retention_review": [
            dict(_summary(r), recorded_start_age_seconds=age(r))
            for r in eligible[:limit]
        ],
        "truncated": {
            "incomplete_zero_download_rate": len(zero_rate) > limit,
            "metadata_placeholders": len(metadata) > limit,
            "below_target_ratio": len(below_ratio) > limit,
            "retention_review": len(eligible) > limit,
        },
        "caveats": [
            "A zero instantaneous download rate is not proof a torrent is stalled.",
            "Ratio and recorded start age do not establish tracker retention compliance.",
            "Retention review candidates are complete and meet the requested ratio; they are NOT approved for removal.",
            "Logical torrent size is not verified actual disk usage; files may overlap or be sparse.",
            "Removing the torrent record does not remove payload data; actual recoverable disk space is unknown.",
            "first_started_at is a recorded start timestamp, not a verified date-added or total seed time.",
        ]
    }

def compare(inventories: dict[str, list[dict]], errors: dict[str, str] | None = None,
            limit: int = 50) -> dict:
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    by_hash: dict[str, list[dict]] = {}
    for server, rows in inventories.items():
        for r in rows:
            by_hash.setdefault(r["hash"], []).append({"server": server, **_summary(r)})
    duplicates = [entries for entries in by_hash.values() if len({r["server"] for r in entries}) > 1]
    duplicates.sort(key=lambda entries: (-max(r["size_bytes"] for r in entries), entries[0]["hash"]))
    return {
        "configured_or_checked_servers": len(inventories) + len(errors or {}),
        "successful_servers": sorted(inventories),
        "errors": errors or {},
        "server_summaries": [
            {"server": key, "total": len(value),
             "logical_size_bytes": sum(r["size_bytes"] for r in value),
             "complete_count": sum(r["complete"] for r in value)}
            for key, value in sorted(inventories.items())
        ],
        "duplicate_infohash_group_count": len(duplicates),
        "duplicate_infohash_groups": duplicates[:limit],
        "truncated": len(duplicates) > limit,
        "caveats": [
            "Duplicates are exact identical infohashes on separate configured servers, not filename matches.",
            "Logical size duplicated across servers is not proof of local disk duplication or reclaimable bytes.",
            "Inaccessible servers are reported explicitly and excluded from comparisons.",
            "No torrent or payload changes have been made."
        ]
    }
