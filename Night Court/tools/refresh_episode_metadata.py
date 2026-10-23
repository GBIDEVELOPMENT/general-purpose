#!/usr/bin/env python3
"""Enrich local factual episode records using TVmaze's public API.

No script dialogue, website article text, reviews or subtitle files are downloaded.
Offline tests and --check require no network. Run against a clean checkout.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED = [13, 22, 22, 22, 22, 22, 24, 24, 22]
URL = "https://api.tvmaze.com/shows/1489/episodes"

def records():
    return sorted((ROOT / "seasons").glob("S*/S*/episode.json"))

def check():
    files = records()
    expected = sum(EXPECTED)
    assert len(files) == expected, f"Expected {expected} files, got {len(files)}"
    for s, count in enumerate(EXPECTED, 1):
        for e in range(1, count + 1):
            identifier = f"S{s:02d}E{e:02d}"
            p = ROOT / "seasons" / f"S{s:02d}" / identifier / "episode.json"
            assert p.exists(), f"Missing {identifier}"
            obj = json.loads(p.read_text(encoding="utf-8"))
            assert obj["id"] == identifier
            assert obj["season"] == s and obj["episode"] == e
            assert len(obj.get("episode_sources", [])) >= 6, identifier
    print(f"Valid: {expected} episode records across {len(EXPECTED)} seasons")
    return files

def enrich(download=True):
    files = check()
    with urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "NightCourtCorpusResearch/0.1 (metadata only)"}), timeout=30) as response:
        remote = json.load(response)
    by_id = {}
    for row in remote:
        s, e = row.get("season"), row.get("number")
        if isinstance(s, int) and isinstance(e, int):
            by_id[f"S{s:02d}E{e:02d}"] = row
    updated = 0
    for p in files:
        obj = json.loads(p.read_text(encoding="utf-8"))
        r = by_id.get(obj["id"])
        if not r:
            print(f"No TVmaze match: {obj['id']}", file=sys.stderr)
            continue
        changed = False
        if not obj.get("title") and r.get("name"):
            obj["title"] = r["name"]; obj["title_status"] = "tvmaze_api_factual_metadata"; changed=True
        elif obj.get("title") and r.get("name") and r["name"].casefold()!=obj["title"].casefold():
            arr=obj.setdefault("title_aliases",[])
            if r["name"] not in arr: arr.append(r["name"]); changed=True
        if not obj.get("original_air_date") and r.get("airdate"):
            obj["original_air_date"]=r["airdate"]; obj["original_air_date_status"]="tvmaze_api_factual_metadata"; changed=True
        if r.get("id") and obj.get("tvmaze_episode_id") != r["id"]:
            obj["tvmaze_episode_id"]=r["id"]; changed=True
        if r.get("url") and not any(x["provider"]=="TVmaze" and x.get("level")=="episode_in_index" for x in obj["episode_sources"]):
            obj["episode_sources"].append({"kind":"episode_guide","provider":"TVmaze","url":r["url"],"level":"episode_in_index","verified":True,"content_imported":False});changed=True
        if changed:
            p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
            updated+=1
    lines = []
    for p in files:
        o=json.loads(p.read_text(encoding="utf-8"))
        lines.append(json.dumps({"id":o["id"],"season":o["season"],"episode":o["episode"],"title":o["title"],"original_air_date":o["original_air_date"],"source_count":len(o["episode_sources"])},ensure_ascii=False))
    (ROOT / "catalog" / "episodes.jsonl").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"Enriched {updated} records with TVmaze title/date/ID/page pointers; full dialogue never fetched")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true",help="Check local corpus without network")
    args=ap.parse_args()
    if args.check: check()
    else: enrich()

if __name__=="__main__": main()
