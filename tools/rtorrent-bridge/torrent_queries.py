"""Bounded sorting, filtering, pagination, and exact-hash health explanations."""
from __future__ import annotations

SORT_KEYS = {
    "name": "name", "size": "size_bytes", "ratio": "ratio",
    "uploaded": "uploaded_bytes", "downloaded": "downloaded_bytes",
    "first_started": "first_started_at", "finished": "finished_at",
    "upload_speed": "up_bytes_per_sec", "download_speed": "down_bytes_per_sec",
}
HEALTH_FIELDS = ("d.hash=", "d.peers_connected=", "d.peers_not_connected=",
                 "d.left_bytes=", "d.tracker_size=", "d.hashing=",
                 "d.is_open=", "d.connection_current=")

def select_page(rows: list[dict], *, query: str = "", sort_by: str = "name",
                descending: bool = False, offset: int = 0, limit: int = 50,
                complete: bool | None = None, active: bool | None = None,
                min_ratio: float | None = None) -> dict:
    if sort_by not in SORT_KEYS:
        raise ValueError("Unknown sort key")
    if not 0 <= offset <= 1000000 or not 1 <= limit <= 100:
        raise ValueError("Invalid pagination boundary")
    if len(query) > 256:
        raise ValueError("Query is too long")
    if min_ratio is not None and not 0 <= min_ratio <= 100000:
        raise ValueError("min_ratio is outside the supported range")
    matches = [
        r for r in rows
        if query.casefold() in r["name"].casefold()
        and (complete is None or bool(r["complete"]) == complete)
        and (active is None or bool(r["active"]) == active)
        and (min_ratio is None or r["ratio"] >= min_ratio)
    ]
    # Stable hash tie-breaker ensures reproducible paging, independent of rTorrent view order.
    matches.sort(key=lambda r: r["hash"])
    field = SORT_KEYS[sort_by]
    known = [r for r in matches if r.get(field) is not None]
    unknown = [r for r in matches if r.get(field) is None]
    known.sort(key=lambda r: r[field].casefold() if field == "name" else r[field],
               reverse=descending)
    ordered = known + unknown
    page = ordered[offset:offset+limit]
    next_offset = offset+len(page) if offset+len(page) < len(ordered) else None
    return {"total": len(rows), "matching": len(ordered), "sort_by": sort_by,
            "descending": descending, "offset": offset,
            "next_offset": next_offset, "has_more": next_offset is not None,
            "torrents": page}

def explain_health(row: dict, fields: list) -> dict:
    if not isinstance(fields, (list, tuple)) or len(fields) != len(HEALTH_FIELDS):
        raise ValueError("Malformed health response")
    if str(fields[0]).upper() != row["hash"].upper():
        raise ValueError("Health record does not match requested torrent")
    peers_connected, peers_pending, left, trackers, hashing, is_open = map(int, fields[1:7])
    mode = str(fields[7])
    if min(peers_connected, peers_pending, left, trackers) < 0:
        raise ValueError("Negative numeric metric in health response")
    observations = []
    if not row["complete"] and row["down_bytes_per_sec"] == 0:
        observations.append("Currently incomplete with zero instantaneous download rate; a single sample does not establish a persistent stall.")
    if peers_connected == 0:
        observations.append("No peers connected at the instant of this query; tracker success and swarm availability are unknown.")
    if not row["complete"] and row["size_bytes"] <= 1:
        observations.append("Likely unresolved metadata placeholder; actual payload size is unknown.")
    if not row["active"]:
        observations.append("rTorrent currently reports the torrent as inactive.")
    return {
        "hash": row["hash"], "name": row["name"],
        "complete": row["complete"], "active": row["active"],
        "size_bytes": row["size_bytes"], "downloaded_bytes": row["downloaded_bytes"],
        "download_bytes_per_sec": row["down_bytes_per_sec"],
        "upload_bytes_per_sec": row["up_bytes_per_sec"],
        "peers_connected": peers_connected, "peers_not_connected": peers_pending,
        "bytes_remaining": left, "tracker_entry_count": trackers,
        "hashing_state": hashing, "is_open": bool(is_open),
        "connection_mode": mode, "observations": observations,
        "caveats": [
            "No tracker URLs, tracker passkeys or peers' IP addresses are exposed.",
            "Connected peer counts and download speeds are instantaneous.",
            "Tracker entry count does not establish tracker reachability or health.",
            "This tool never changes the torrent, its files, tracker configuration or connection state."
        ],
    }
