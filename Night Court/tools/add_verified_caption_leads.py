#!/usr/bin/env python3
"""Merge manually verified 1984 Night Court caption *page URLs*, never dialogue.

Reads the openly indexed Season 3 external page manifest. No HTTP requests,
downloads, caption text or DRM access. Idempotent across URL-encoding variants.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
from urllib.parse import urlparse, unquote

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"research"/"season03-caption-page-locations.json"
SUMMARY=ROOT/"catalog"/"subtitlecat-discovery.json"
EXPECTED={f"S03E{i:02d}" for i in range(1,23)}

def normalized(url):
    parsed=urlparse(url)
    return (parsed.hostname or "").casefold(),unquote(parsed.path).casefold().replace("  "," ")

def save(path,value):
    data=json.dumps(value,indent=2,ensure_ascii=False)+"\n"
    if not path.exists() or path.read_text("utf-8")!=data:
        path.write_text(data,"utf-8")
        return 1
    return 0

def main():
    artifact=json.loads(INPUT.read_text("utf-8"))
    if artifact.get("series_id")!="night-court-1984":raise ValueError("Wrong source series")
    rows=artifact["items"]
    if len(rows)!=22 or {r["episode_id"] for r in rows}!=EXPECTED:
        raise ValueError("Expected exactly the 22 original season-3 episodes")
    new=0
    changed=0
    for item in rows:
        key=item["episode_id"]
        source_url=item["source_url"]
        host,path=normalized(source_url)
        if host!="www.subtitlecat.com" or not path.startswith("/subs/1081/"):
            raise ValueError(f"Unexpected third-party source page: {source_url}")
        if key.casefold() not in path or "night court (1984)" not in path:
            raise ValueError(f"Missing source-confirmed 1984 identity: {key}")
        if item["source_index"]!=artifact["source_index"]:
            raise ValueError("Index provenance differs across manifest rows")
        episode=ROOT/"seasons"/"S03"/key/"episode.json"
        data=json.loads(episode.read_text("utf-8"))
        sources=data["episode_sources"]
        previously=next((x for x in sources if x.get("provider")=="Subtitle Cat" and
            normalized(x.get("url",""))==(host,path)),None)
        if previously is not None:
            previously["level"]="episode_page"
            previously["verified"]=True
            previously["content_imported"]=False
            previously.setdefault("source_index",artifact["source_index"])
            previously["verification"]="public_upload_listing_plus_individual_episode_page"
        else:
            sources.append({
                "kind":"subtitle_index","provider":"Subtitle Cat",
                "url":source_url,"level":"episode_page","verified":True,
                "content_imported":False,
                "source_index":artifact["source_index"],
                "verification":"public_upload_listing_plus_individual_episode_page",
                "source_label":item["source_label"],
                "note":"Original 1984-series English DVD caption display URL. Source bytes NOT archived. Reuse rights not established."
            })
            new+=1
        changed+=save(episode,data)

    # Rebuild the independent link-only source summary from actual episode
    # records, so later runs cannot silently report only the original 13 seeds.
    pathlist=[]
    for episode in sorted((ROOT/"seasons").glob("S*/S*/episode.json")):
        source=json.loads(episode.read_text("utf-8"))
        for rec in source["episode_sources"]:
            if rec.get("provider")!="Subtitle Cat" or "/subs/" not in rec.get("url",""):
                continue
            pathlist.append((source["id"],rec))
    by_episode={}
    seen=set()
    for key,rec in pathlist:
        norm=(key,normalized(rec["url"]))
        if norm in seen:continue
        seen.add(norm)
        by_episode.setdefault(key,[]).append({
           "provider":"Subtitle Cat","episode_id":key,
           "source_page":rec["url"],
           "index_page":rec.get("source_index"),
           "display_label":rec.get("source_label",key),
           "source_locator_status":rec.get("verification","episode_page"),
           "full_caption_file_imported":bool(rec.get("content_imported"))
        })
    report=json.loads(SUMMARY.read_text("utf-8"))
    report["manually_verified_page_count"]=sum(len(v) for v in by_episode.values())
    report["episodes_with_indexed_pages"]=len(by_episode)
    report["page_versions_indexed"]=sum(map(len,by_episode.values()))
    report["episodic_page_versions"]=dict(sorted(by_episode.items()))
    report["additional_verification_index"]=artifact["source_index"]
    report["external_index_permission_note"]="Public browser-index research only; HTTP collector robots restrictions remain in force."
    changed+=save(SUMMARY,report)
    print(f"S03 verified caption source pages: {len(rows)}; added {new} distinct links; updated {changed} artifacts; globally indexed {report['episodes_with_indexed_pages']} episodes")
if __name__=="__main__":
    main()
