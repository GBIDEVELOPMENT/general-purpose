#!/usr/bin/env python3
"""Bounded, read-only retrieval of explicitly listed S03/S04 English SRTs."""
import argparse
import csv
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 1_000_000
ALLOWED_HOST = "www.subtitlecat.com"
EPISODE = re.compile(r"^S0[34]E(?:0[1-9]|1[0-9]|2[0-2])$")
CUES = re.compile(rb"\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->")

def retrieve(url):
    p = urlsplit(url)
    if p.scheme != "https" or p.hostname != ALLOWED_HOST or p.username or p.password or p.port:
        raise ValueError("unexpected source host/protocol")
    req = Request(url, headers={"User-Agent": "NightCourtResearchSourceIntake/1.0", "Accept": "text/plain, application/x-subrip, */*"})
    with urlopen(req, timeout=25) as resp:
        if urlsplit(resp.url).hostname != ALLOWED_HOST or urlsplit(resp.url).scheme != "https":
            raise ValueError("unexpected redirect")
        if "text/html" in resp.headers.get("Content-Type", "").lower():
            raise ValueError("HTML returned instead of SRT")
        data = resp.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("download exceeds size limit")
    if not CUES.search(data):
        raise ValueError("missing SRT timecodes (or unexpected response)")
    return data

def run(manifest, outdir, live, delay):
    rows = list(csv.DictReader(manifest.open(encoding="utf-8-sig", newline="")))
    ids = [r["episode"] for r in rows]
    expected = {f"S{s:02d}E{e:02d}" for s in (3,4) for e in range(1,23)}
    if set(ids) != expected or len(ids) != 44:
        raise ValueError("manifest must have exactly the 44 unique S03/S04 episode IDs")
    outdir.mkdir(parents=True, exist_ok=True)
    audit = []
    errors = 0
    for i, row in enumerate(rows):
        episode = row["episode"]
        url = row["direct_srt_url"]
        record = {"episode_id": episode, "title": row["title"], "source_url": url,
                  "source_type": "third_party_download", "rights_status": "owner_research_assessment_required"}
        try:
            if not EPISODE.fullmatch(episode):
                raise ValueError("invalid episode ID")
            if not live:
                record["status"] = "not_downloaded_dry_run"
            else:
                data = retrieve(url)
                path = outdir / (episode + ".en.srt")
                path.write_bytes(data)
                record.update(status="downloaded_unreviewed", file=path.name,
                              size_bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                              cue_marker_count=len(CUES.findall(data)))
        except Exception as exc:
            errors += 1
            record.update(status="failed", error=str(exc)[:250])
        audit.append(record)
        print(f"{episode}: {record['status']}", flush=True)
        if live and i != len(rows)-1:
            time.sleep(delay)
    (outdir / "retrieval-report.json").write_text(json.dumps({
        "series": "night-court-1984", "attempted": len(rows), "failed": errors,
        "held_in_repository": False, "items": audit}, indent=2)+"\n", encoding="utf-8")
    return errors

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,default=ROOT/"research"/"s03-s04-direct-srt-links.csv")
    p.add_argument("--output",type=Path,default=ROOT/"incoming"/"s03-s04-download-staging")
    p.add_argument("--download",action="store_true")
    p.add_argument("--delay-seconds",type=float,default=1.5)
    args=p.parse_args()
    return 1 if run(args.manifest,args.output,args.download,args.delay_seconds) else 0

if __name__ == "__main__":
    sys.exit(main())
