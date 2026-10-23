#!/usr/bin/env python3
"""Map manually observed S05-S09 public caption *index listings*, without scraping.

Each record is an episode-specific listing in a shared upload-index page.
No item is claimed to be a verified direct caption display page or a held SRT.
"""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"research"/"later-season-2025-caption-upload-listings.json"
EXPECTED={f"S{s:02d}E{i:02d}" for s,size in [(5,22),(6,22),(7,24),(8,24),(9,22)] for i in range(1,size+1)}
ALLOWED_FROM={"1710550","1710600","1710650","1710700","1710750","1710800"}

def write_if_changed(path,value):
    content=json.dumps(value,ensure_ascii=False,indent=2)+"\n"
    if path.exists() and path.read_text("utf-8")==content:return False
    path.write_text(content,"utf-8")
    return True

def main():
    data=json.loads(MANIFEST.read_text("utf-8"))
    if data.get("series_id")!="night-court-1984" or "June 22 2025" not in data.get("source",""):
        raise ValueError("Unsupported source batch or series")
    items=data["entries"]
    if not items or len(items)>120:raise ValueError("Unexpected manifest size")
    if len({x["episode_id"] for x in items})!=len(items):
        raise ValueError("Duplicate episode in manually observed listing manifest")
    for item in items:
        key=item["episode_id"]
        if key not in EXPECTED:raise ValueError("Unexpected 1984 original-series episode "+key)
        parsed=urlparse(item["index_url"])
        qs=parse_qs(parsed.query)
        if (parsed.scheme!="https" or parsed.hostname!="www.subtitlecat.com" or
            parsed.path!="/list_page.php" or qs.get("from",[])!=[str(qs.get("from",[""])[0])] or
            qs.get("from",[""])[0] not in ALLOWED_FROM):
            raise ValueError("Unapproved index source: "+item["index_url"])
        if item.get("status")!="episode_label_observed_in_public_2025_upload_index":
            raise ValueError("Unverified index-listing status")
    changes=0
    added=0
    for item in items:
        key=item["episode_id"]
        episode_path=ROOT/"seasons"/key[:3]/key/"episode.json"
        ep=json.loads(episode_path.read_text("utf-8"))
        if ep.get("id")!=key:raise ValueError("Episode ID mismatch")
        source={
            "kind":"subtitle_index","provider":"Subtitle Cat",
            "url":item["index_url"],"level":"episode_in_index",
            "verified":True,"content_imported":False,
            "verification":"episode_label_verified_in_public_upload_index_only",
            "source_upload_date":"2025-06-22",
            "episode_id_in_listing":key,
            "note":"Index page contains episode-named original-series English subtitle listing. Direct caption page not individually inspected; subtitle text not archived. Reuse rights not established."
        }
        if not any(s.get("provider")=="Subtitle Cat" and
                   s.get("url")==item["index_url"] and
                   s.get("episode_id_in_listing")==key for s in ep["episode_sources"]):
            ep["episode_sources"].append(source)
            added+=1
            changes+=write_if_changed(episode_path,ep)
    counts=dict(sorted(Counter(x["episode_id"][:3] for x in items).items()))
    print(f"Reconciled {len(items)} verified, source-index-only episode rows; added {added} refs; updated {changes} files; per season {counts}")
if __name__=="__main__":main()
