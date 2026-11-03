"""Sanitized, read-only tracker telemetry: no URLs, passkeys or network probes."""
from __future__ import annotations

FIELDS = (
    "t.is_enabled=", "t.failed_counter=", "t.success_counter=",
    "t.latest_sum_peers=", "t.scrape_complete=", "t.scrape_incomplete=",
    "t.failed_time_last=", "t.success_time_last=", "t.type=",
)
TYPE_LABELS = {1: "HTTP(S)", 2: "UDP", 3: "DHT"}

def sanitize_tracker_rows(rows: list, *, server: str, infohash: str,
                          name: str, limit: int = 30) -> dict:
    if not 1 <= limit <= 100:
        raise ValueError("Tracker limit must be between 1 and 100")
    if not isinstance(rows, (list, tuple)):
        raise ValueError("Malformed tracker collection")
    result = []
    for index, row in enumerate(rows):
        if not isinstance(row, (list, tuple)) or len(row) != len(FIELDS):
            raise ValueError("Malformed tracker metric row")
        try:
            enabled, failed, successful, peers, seeds, leechers, last_failed, last_success, kind = map(int, row)
        except (ValueError, TypeError, OverflowError):
            raise ValueError("Invalid numeric tracker metric") from None
        if min(enabled, failed, successful, peers, seeds, leechers, last_failed, last_success, kind) < 0:
            raise ValueError("Negative tracker metric")
        if index < limit:
            result.append({
                "index": index, "enabled": bool(enabled),
                "type": TYPE_LABELS.get(kind, "other"),
                "successful_requests_recorded": successful,
                "failed_requests_recorded": failed,
                "peers_from_latest_announce": peers,
                "scrape_seed_count": seeds if last_success else None,
                "scrape_leecher_count": leechers if last_success else None,
                "last_failed_at": last_failed or None,
                "last_succeeded_at": last_success or None,
            })
    return {
        "server": server, "hash": infohash, "name": name,
        "tracker_count": len(rows), "trackers": result,
        "truncated": len(rows) > limit,
        "notes": [
            "No tracker endpoint URLs, tracker passkeys, or peer IPs are included.",
            "Counts are the values retained by rTorrent; their lifetime can be limited by session restarts.",
            "Latest announce peer counts can be stale and do not establish current connected peers.",
            "Zero scrape counts can mean missing scrape data, not necessarily an empty swarm.",
            "Identical peers may appear through multiple trackers; do not sum their counts.",
            "All calls are read-only; no tracker announce, scrape, recheck or retry is initiated.",
        ],
    }
