#!/usr/bin/env python3
"""Index five manually verified Night Court 1984 caption-display URLs.

Pure offline metadata reconciliation: never fetches subtitle text, bypasses
access controls, or infers rights to reproduce a third-party transcript.
"""
from pathlib import Path
from urllib.parse import urlparse,unquote
import json

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"research"/"s07-s09-remaining-direct-pages.json"
COLLECTION=ROOT/"catalog"/"subtitlecat-discovery.json"
EXPECTED={"S07E03","S07E04","S09E06","S09E20","S09E21"}

def norm(url):
    u=urlparse(url)
    return (u.hostname or "").casefold().removeprefix("www."),unquote(u.path).lower()

def write(path,obj):
    content=json.dumps(obj,indent=2,ensure_ascii=False)+"\n"
    if not path.exists() or path.read_text("utf-8")!=content:
        path.write_text(content,"utf-8")
        return True
    return False

def main():
    source=json.loads(INPUT.read_text("utf-8"))
    if source["series"]!="night-court-1984":raise ValueError("Wrong series")
    items=source["items"]
    if {x["episode_id"] for x in items}!=EXPECTED or len(items)!=5:
        raise ValueError("Unexpected original episode identities or duplicates")
    attached=0
    for r in items:
        eid,url=r["episode_id"],r["source_page"]
        host,path=norm(url)
        if host!="subtitlecat.com" or not path.startswith("/subs/1121/") or eid.lower() not in path:
            raise ValueError("Mismatched source page identity "+eid)
        target=ROOT/"seasons"/eid[:3]/eid/"episode.json"
        episode=json.loads(target.read_text("utf-8"))
        if episode.get("id")!=eid or episode.get("title")!=r["catalog_title"]:
            raise ValueError("Source-to-episode title/identity mismatch "+eid)
        references=episode["episode_sources"]
        current=next((x for x in references if x.get("provider")=="Subtitle Cat" and norm(x.get("url",""))==(host,path)),None)
        if current:
            if current.get("level")!="episode_page" or not current.get("verified"):
                current.update({"level":"episode_page","verified":True,"content_imported":False})
                write(target,episode)
            continue
        references.append({
            "kind":"subtitle_index","provider":"Subtitle Cat","url":url,
            "level":"episode_page","verified":True,
            "content_imported":False,
            "verification":"individually_checked_public_caption_display_page",
            "source_index":None,
            "note":"Original-series episode page; URL only, no transcript bytes. "+(r["alternate_title_note"] or "")
        })
        attached+=1
        write(target,episode)
    # Derive catalog summary from episode-specific sources.
    groups={}
    seen=set()
    for efile in sorted((ROOT/"seasons").glob("S*/S*/episode.json")):
        ep=json.loads(efile.read_text("utf-8"))
        for record in ep["episode_sources"]:
            if record.get("provider")!="Subtitle Cat" or "/subs/" not in record.get("url",""):
                continue
            k=(ep["id"],norm(record["url"]))
            if k in seen:continue
            seen.add(k)
            groups.setdefault(ep["id"],[]).append({
                "provider":"Subtitle Cat",
                "episode_id":ep["id"],"source_page":record["url"],
                "index_page":record.get("source_index"),
                "display_label":record.get("source_label",ep["id"]),
                "source_locator_status":record.get("verification","episode_page"),
                "full_caption_file_imported":bool(record.get("content_imported"))
            })
    archive=json.loads(COLLECTION.read_text("utf-8"))
    archive["episodes_with_indexed_pages"]=len(groups)
    archive["page_versions_indexed"]=sum(map(len,groups.values()))
    archive["episodic_page_versions"]=dict(sorted(groups.items()))
    archive["s07_s09_verified_pages_manifest"]="research/s07-s09-remaining-direct-pages.json"
    write(COLLECTION,archive)
    print("Attached",attached,"new confirmed source URLs; Subtitle Cat total:",len(groups),
          "episodes with links, no proprietary caption bytes copied")

if __name__=="__main__":main()
