#!/usr/bin/env python3
"""Read-only, episode-exact evidence for all Studio 60 TV versions on FTP."""
from __future__ import annotations
import json, re, argparse
from collections import Counter, defaultdict
from pathlib import Path
from organize import connect

ROOT="/downloads"
SHOW="Studio 60 on the Sunset Strip (2006)"
SEASON=f"{ROOT}/{SHOW}/Season 01"
VIDEO_TYPES={
    "1080p.mp4","720p.mp4","XviD DVDRip.avi","DVD.avi"
}
REQUIRED=VIDEO_TYPES|{"DVD.idx","DVD.sub"}
EPISODE=re.compile(
    r"^Studio 60 on the Sunset Strip \(2006\) - S01E(\d{2}) - (.+) - "
    r"(1080p\.mp4|720p\.mp4|XviD DVDRip\.avi|DVD\.(?:avi|idx|sub))$"
)
EXTRAS={
    "Other":("Pilot commentary audio track",),
    "Featurettes":("Making of Studio 60 on the Sunset Strip",),
}
LEGACY=[
    f"{ROOT}/S60/1080p",
    f"{ROOT}/S60/720p",
    f"{ROOT}/S60/DVD",
    f"{ROOT}/Studio 60 on the Sunset Strip/Season 01"
]

def analyze(names):
    grouped=defaultdict(list)
    unrecognized=[]
    for name in names:
        m=EPISODE.fullmatch(name)
        if not m:
            unrecognized.append(name)
            continue
        n=int(m.group(1));title=m.group(2);edition=m.group(3)
        grouped[n].append((title,edition))
    failures=[];episodes=[]
    for n in range(1,23):
        records=grouped.get(n,[])
        titles={name for name,_ in records}
        editions=[kind for _,kind in records]
        missing=sorted(REQUIRED-set(editions))
        duplicates=[k for k,v in Counter(editions).items() if v>1]
        if len(titles)!=1 or missing or duplicates:
            failures.append({"episode":n,"titles":sorted(titles),
                             "missing":missing,"duplicate_editions":duplicates})
        episodes.append({"episode":n,"titles":sorted(titles),
                         "editions":sorted(editions),"missing":missing})
    for n in sorted(grouped):
        if n<1 or n>22:
            failures.append({"episode":n,"error":"unexpected episode identifier"})
    return {"episode_count":22,"files_recognized":sum(len(v) for v in grouped.values()),
            "edition_counts":dict(sorted(Counter(kind for v in grouped.values() for _,kind in v).items())),
            "episodes":episodes,"unrecognized":sorted(unrecognized),"failures":failures}

def list_folder(ftp,path):
    try:
        ftp.cwd(path)
        return {"exists":True,"entries":sorted(
            [{"name":name,"type":facts.get("type"),
              "size":facts.get("size")} for name,facts in ftp.mlsd()
             if name not in (".","..")],key=lambda e:e["name"].casefold())}
    except Exception as exc:
        # Explicitly document uncertainty rather than treating a failed FTP
        # listing as proof the directory is empty.
        return {"exists":False,"error":type(exc).__name__,"entries":[]}

def audit(ftp):
    canonical=list_folder(ftp,SEASON)
    found=analyze(e["name"] for e in canonical["entries"] if e["type"]=="file")
    extras={}
    for folder,(stem,) in EXTRAS.items():
        info=list_folder(ftp,f"{ROOT}/{SHOW}/{folder}")
        actual={e["name"] for e in info["entries"] if e["type"]=="file"}
        wanted={stem+ext for ext in (".avi",".idx",".sub")}
        extras[folder]={"exists":info["exists"],"wanted":sorted(wanted),
                        "missing":sorted(wanted-actual),"unrecognized":sorted(actual-wanted)}
    legacy={path:list_folder(ftp,path) for path in LEGACY}
    errors=list(found["failures"])
    if not canonical["exists"]:errors.append({"error":"Canonical season directory inaccessible"})
    for k,v in extras.items():
        if not v["exists"] or v["missing"]:
            errors.append({"extra":k,"error":"Missing matching extra components"})
    return {"show":SHOW,"root":ROOT,"canonical":SEASON,
            "status":"complete" if not errors else "incomplete",
            "episodes":found,"extras":extras,
            "legacy_folder_occupancy":{path:{"exists":v["exists"],
                "entry_count":len(v["entries"]),
                "entries":v["entries"]} for path,v in legacy.items()},
            "errors":errors}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="media-organizer/studio60-output/studio60-verified.json")
    args=p.parse_args()
    with connect() as ftp: result=audit(ftp)
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("STUDIO60_FTP_AUDIT",json.dumps({"status":result["status"],
        "files_recognized":result["episodes"]["files_recognized"],
        "edition_counts":result["episodes"]["edition_counts"],
        "error_count":len(result["errors"])}))
    if result["errors"]:raise SystemExit("Missing or conflicting Studio 60 media; review artifact")
if __name__=="__main__":main()
