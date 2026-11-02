#!/usr/bin/env python3
"""Offline, non-mutating TV folder planner for a mixed FTP Downloads tree."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path, PurePosixPath
import re
from organize import ROOT, VIDEO, SIDE, EP, MULTI_EP, basename_clean, safe, RELEASE, LANGUAGE, YEAR

GENERIC={"downloads","tv","television","movies","shows","complete","video","media",
         "episodes","season","seasons","film","films","series"}
SEASON_DIR=re.compile(r"(?i)^(?:season|series|s)\s*0*\d{1,2}$")
SIDE_LANG=re.compile(r"(?i)^[._ -]+([a-z]{2,3})([._ -]+(?:forced|sdh|hi))?$")
EXTRA=re.compile(r"(?i)-(?:behindthescenes|deleted\d*|featurette|interview|scene|short|trailer|other)$")
def showinfo(path):
    p=PurePosixPath(path);m=EP.search(p.stem)
    if not m:return None,"No SxxEyy episode marker"
    tail=p.stem[m.end():]
    if MULTI_EP.match(tail):return None,"Multi-episode range requires deliberate mapping"
    if EXTRA.search(tail):return None,"Plex episode extra must keep its exact -type suffix"
    series=basename_clean(p.stem[:m.start()])
    ancestors=[x for x in p.parents if str(x).startswith(ROOT+"/")]
    if not series:
        for parent in ancestors:
            name=parent.name
            if name.lower() in GENERIC or SEASON_DIR.fullmatch(name):continue
            series=basename_clean(name);break
    if not series or series.lower() in GENERIC or len(series)>110:
        return None,"Cannot safely infer show title"
    season=int(m.group(1));episode=int(m.group(2))
    if season>60 or episode>400:return None,"Implausible episode number"
    return {"series":series,"season":season,"episode":episode,"tail":tail,"parent":str(p.parent)},None

def make_target(path,info):
    p=PurePosixPath(path);series=info["series"]
    # Existing show-folder ancestor wins; preserve category parents if supplied.
    matching=[a for a in p.parents if a.name.casefold()==series.casefold() and str(a).startswith(ROOT+"/")]
    base=str(matching[0]) if matching else ROOT+"/"+series
    base=safe(base+"/Season "+f'{info["season"]:02d}')
    title=basename_clean(RELEASE.split(info["tail"],1)[0])
    subtitle=""
    if p.suffix.lower() in SIDE:
        match=SIDE_LANG.fullmatch(info["tail"])
        if match:
            subtitle="."+match.group(1).lower()+(("." + match.group(2).strip(" ._-").lower()) if match.group(2) else "")
            title=""
        elif info["tail"].strip(" ._-"):
            return None
    stem=series+" - "+f'S{info["season"]:02d}E{info["episode"]:02d}'
    if title:stem+=" - "+title
    return safe(base+"/"+stem+subtitle+p.suffix)

def plan(inventory):
    videos=[];sidecars=[];review=[]
    for obj in inventory["files"]:
        p=obj["path"];ext=PurePosixPath(p).suffix.lower()
        if ext not in VIDEO|SIDE:continue
        if obj.get("size") is None:
            review.append({"path":p,"reason":"No size metadata"});continue
        info,error=showinfo(p)
        if error:
            if ext in VIDEO:
                category="Possible movie" if YEAR.search(PurePosixPath(p).stem) else "Unknown media"
                review.append({"path":p,"reason":error,"category":category})
            continue
        item={"source":p,"size":obj["size"],"info":info}
        if ext in VIDEO:videos.append(item)
        else:sidecars.append(item)
    keys=defaultdict(list)
    for item in videos:
        info=item["info"]
        key=(info["parent"].casefold(),info["series"].casefold(),info["season"],info["episode"])
        keys[key].append(item)
    moves=[];groups=defaultdict(lambda:{"video_count":0,"sidecar_count":0,"source_directories":set(),"samples":[]})
    existing={x["path"].casefold() for x in inventory["files"]}
    destinations=set()
    for item in videos+sidecars:
        info=item["info"];src=item["source"];p=PurePosixPath(src)
        key=(info["parent"].casefold(),info["series"].casefold(),info["season"],info["episode"])
        if p.suffix.lower() in SIDE and len(keys[key])!=1:
            review.append({"path":src,"reason":"Subtitle/metadata sidecar has no unique episode video in same folder"});continue
        target=make_target(src,info)
        if target is None:
            review.append({"path":src,"reason":"Unrecognized sidecar suffix; manual alignment required"});continue
        group=groups[info["series"]];group["source_directories"].add(info["parent"])
        if p.suffix.lower() in VIDEO:group["video_count"]+=1
        else:group["sidecar_count"]+=1
        if len(group["samples"])<3:group["samples"].append(src)
        if src==target:continue
        if target.casefold() in existing or target.casefold() in destinations:
            review.append({"path":src,"reason":"Destination already occupied or duplicated","proposed":target});continue
        destinations.add(target.casefold())
        moves.append({"from":src,"to":target,"size":item["size"],
                      "kind":"tv-series-folder-suggestion","confidence":"high" if any(a.name.casefold()==info["series"].casefold() for a in p.parents) else "medium"})
    outgroups=[]
    for name,g in groups.items():
        outgroups.append({"series":name,"videos":g["video_count"],"sidecars":g["sidecar_count"],
                          "directories":sorted(g["source_directories"]),"sample_paths":g["samples"]})
    outgroups.sort(key=lambda x:(-x["videos"],x["series"].casefold()))
    return {"root":ROOT,"suggested_folder_moves":moves,"series":outgroups,
            "review":review,"incomplete_scan":bool(inventory.get("failures") or inventory.get("truncated")),
            "notes":"Offline suggestions only. These cannot be applied by organize.py and require a reviewed next-generation executor."}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--inventory",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    report=plan(json.loads(Path(args.inventory).read_text()))
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print(json.dumps({"series":len(report["series"]),"move_suggestions":len(report["suggested_folder_moves"]),
                      "needs_review":len(report["review"]),"partial":report["incomplete_scan"]}))
if __name__=="__main__":main()
# Inventory refresh marker 2026-11-01: owner-requested read-only Downloads title catalog.
# Inventory refresh marker 2026-11-02: post-owner-deletion Star Trek and folder cleanup audit; read-only.
# Post-Star Trek relocation and GL duplicate deletion full read-only inventory, 2026-11-02.
# Post-relocation inventory retry after folder reconciliation compatibility fix, 2026-11-02.
