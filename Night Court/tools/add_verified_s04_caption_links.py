#!/usr/bin/env python3
"""Reconcile 22 source-verified original Night Court S04 caption page URLs.

No network access, no downloaded dialogue. Attaches only URL/provenance metadata,
without overwriting other research or accidentally importing the 2023 revival.
"""
from pathlib import Path
from urllib.parse import urlparse, unquote
import json
import re

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"research"/"season04-caption-page-locations.json"
COLLECTION=ROOT/"catalog"/"subtitlecat-discovery.json"
EXPECTED={f"S04E{i:02d}" for i in range(1,23)}

def norm(url):
    x=urlparse(url)
    return (x.hostname or "").lower(),unquote(x.path).lower()

def save(path,value):
    data=json.dumps(value,indent=2,ensure_ascii=False)+"\n"
    if not path.exists() or path.read_text("utf-8")!=data:
        path.write_text(data,"utf-8")
        return True
    return False

def main():
    doc=json.loads(INPUT.read_text("utf-8"))
    assert doc["series"]=="night-court-1984" and doc["season"]==4
    rows=doc["items"]
    if len(rows)!=22 or {x["episode_id"] for x in rows}!=EXPECTED:
        raise ValueError("S04 requires exactly 22 unique episode IDs")
    touched=0
    attached=0
    for row in rows:
        ep=row["episode_id"]
        url=row["source_page"]
        host,path=norm(url)
        expected_prefix=f"/subs/1120/night_court_{ep.lower()}_"
        if host!="www.subtitlecat.com" or not path.startswith(expected_prefix) or not path.endswith(".html"):
            raise ValueError("Unconfirmed or mismatched episode URL: "+url)
        index_host,index_path=norm(row["source_index"])
        if index_host!="www.subtitlecat.com" or index_path!="/list_page.php":
            raise ValueError("Unexpected source index URL")
        episode=ROOT/"seasons"/"S04"/ep/"episode.json"
        item=json.loads(episode.read_text("utf-8"))
        if item.get("id")!=ep:raise ValueError("Wrong 1984 series episode object")
        found=next((r for r in item["episode_sources"]
                    if r.get("provider")=="Subtitle Cat" and norm(r.get("url",""))==(host,path)),None)
        if found is None:
            item["episode_sources"].append({
                "kind":"subtitle_index","provider":"Subtitle Cat",
                "url":url,"level":"episode_page","verified":True,
                "content_imported":False,
                "source_index":row["source_index"],
                "verification":"public_upload_listing_and_direct_episode_page",
                "source_label":row["source_label"],
                "note":"Original 1984 series episode-matched caption display page. URL only; no subtitle text imported; reuse rights not established."
            })
            attached+=1
            touched+=int(save(episode,item))
        elif found.get("level")!="episode_page" or found.get("verified") is not True:
            found["verified"]=True
            found["level"]="episode_page"
            found["content_imported"]=False
            found["verification"]="public_upload_listing_and_direct_episode_page"
            touched+=int(save(episode,item))
    # Rebuild source link index from full 193-episode record set, not merely
    # old static seeds. Variants remain separate; normalized URL duplicates do not.
    grouped={}
    seen=set()
    for file in sorted((ROOT/"seasons").glob("S*/S*/episode.json")):
        e=json.loads(file.read_text("utf-8"))
        for r in e["episode_sources"]:
            if r.get("provider")!="Subtitle Cat" or "/subs/" not in r.get("url",""):continue
            identity=(e["id"],norm(r["url"]))
            if identity in seen:continue
            seen.add(identity)
            grouped.setdefault(e["id"],[]).append({
              "provider":"Subtitle Cat","episode_id":e["id"],
              "source_page":r["url"],"index_page":r.get("source_index"),
              "display_label":r.get("source_label",e["id"]),
              "source_locator_status":r.get("verification","episode_page"),
              "full_caption_file_imported":bool(r.get("content_imported"))
            })
    index=json.loads(COLLECTION.read_text("utf-8"))
    index["episodes_with_indexed_pages"]=len(grouped)
    index["page_versions_indexed"]=sum(len(v) for v in grouped.values())
    index["episodic_page_versions"]=dict(sorted(grouped.items()))
    index["manually_verified_page_count"]=index["page_versions_indexed"]
    index["season04_source_index_urls"]=doc["source_indexes"]
    index["season04_direct_url_manifest"]="research/season04-caption-page-locations.json"
    index["restriction"]="URLs only; caption text is not held and reuse rights remain unassessed"
    save(COLLECTION,index)
    print(f"Validated 22/22 S04 page URLs; {attached} new URL entries; {touched} episode files changed; {len(grouped)} episodes overall have Subtitle Cat source locators")

if __name__=="__main__":
    main()
