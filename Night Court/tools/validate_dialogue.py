#!/usr/bin/env python3
"""Cross-check all held Night Court dialogue witnesses against episodes and bytes."""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
COUNTS=[13,22,22,22,22,22,24,24,22]
def expected_ids():
    return {f"S{s:02d}E{n:02d}" for s, count in enumerate(COUNTS,1) for n in range(1,count+1)}

def main():
    lookup=ROOT/"catalog"/"dialogue-index.jsonl"
    entries=[json.loads(s) for s in lookup.read_text("utf-8").splitlines() if s.strip()] if lookup.exists() else []
    actual=list((ROOT/"seasons").glob("S*/S*/dialogue/versions/*/manifest.json"))
    indexed_paths={r["manifest"] for r in entries}
    physical_paths={str(f.relative_to(ROOT)) for f in actual}
    if indexed_paths!=physical_paths:raise ValueError("Dialogue index/physical witness divergence")
    valid=expected_ids()
    found={}
    for row in entries:
        ep=row["episode_id"]
        if ep not in valid:raise ValueError("Cross-series episode ID "+str(ep))
        f=ROOT/row["manifest"]
        m=json.loads(f.read_text("utf-8"))
        epath=ROOT/"seasons"/ep[:3]/ep/"episode.json"
        obj=json.loads(epath.read_text("utf-8"))
        if m["episode_id"]!=ep or m["sha256"]!=row["sha256"] or m["version_id"]!=row["version_id"]:
            raise ValueError("Index/manifest mismatch for "+ep)
        key=(ep,m["version_id"])
        if key in found:raise ValueError("Duplicate version "+str(key))
        found[key]=m
        base=epath.parent
        original=base/m["original_path"]
        normalized=base/m["segments_path"]
        human=base/m["readable_path"]
        for required in (original,normalized,human):
            if not required.is_file():raise ValueError("Missing dialogue witness derivative "+str(required))
        if hashlib.sha256(original.read_bytes()).hexdigest()!=m["sha256"]:
            raise ValueError("Source bytes failed SHA-256 verification: "+ep)
        cues=[json.loads(x) for x in normalized.read_text("utf-8").splitlines() if x.strip()]
        if len(cues)!=m["cue_count"] or not cues:
            raise ValueError("Cue count mismatch")
        assert all(c["cue"]==i+1 for i,c in enumerate(cues))
        if m["timecoded"] and not all(isinstance(c["start_ms"],int) and isinstance(c["end_ms"],int) and
                                      0<=c["start_ms"]<=c["end_ms"] for c in cues):
            raise ValueError("Invalid timecoded cue")
        if not m["timecoded"] and not all(c["start_ms"] is None and c["end_ms"] is None for c in cues):
            raise ValueError("Invented text timing")
        category="caption_files" if m["timecoded"] else ("full_transcripts" if m["declared_complete"] else "other")
        matches=[x for x in obj["holdings"][category] if x.get("version_id")==m["version_id"]]
        if len(matches)!=1 or matches[0]["sha256"]!=m["sha256"]:
            raise ValueError("Missing episode holding reference for "+ep)
        if m["completeness_status"] not in ("submitter_declared_complete_unverified","unknown_unverified"):
            raise ValueError("Overclaimed transcript completeness")
    print("PASS: verified",len(entries),"preserved dialogue witnesses across",
          len({x["episode_id"] for x in entries}),"episodes; checksum and holding integrity intact")

if __name__=="__main__":
    main()
