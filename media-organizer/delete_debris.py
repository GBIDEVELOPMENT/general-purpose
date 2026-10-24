#!/usr/bin/env python3
"""Bounded FTP debris cleanup with exact inventory-pinned delete manifests.

No wildcard remote deletion. Archive suggestions are never automatically approved.
"""
import argparse, ftplib, json, os, re
from pathlib import Path, PurePosixPath
from organize import ROOT, VIDEO, connect, safe

IMAGE={".jpg",".jpeg",".png",".webp",".bmp",".gif"}
ARCHIVE=re.compile(r"(?i)(?:\.rar|\.r\d\d|\.part\d+\.rar|\.7z|\.zip)$")
SCREEN_FOLDER={"screens","screenshots","screen shots","screen caps","screencaps"}
SCREEN_FILE=re.compile(r"(?i)^(?:screen(?:shot)?[\s._-]*\d+|mpv-shot\d+|vlcsnap[-\d]+|thumbs?[-_ ]?\d+)\.(?:png|jpe?g|webp)$")
def category(path):
    p=PurePosixPath(path)
    if p.suffix.lower()==".nfo":return "nfo"
    if p.suffix.lower() in IMAGE and (
            any(x.lower() in SCREEN_FOLDER for x in p.parts) or SCREEN_FILE.fullmatch(p.name)):
        return "screenshot"
    return None

def assess(inv):
    files=inv["files"]; clean=[]; archives=[]; reserved=[]
    bydir={}
    for f in files:
        d=str(PurePosixPath(f["path"]).parent)
        bydir.setdefault(d,[]).append(f)
    for f in files:
        p=f["path"]
        if category(p) and f.get("size") is not None:
            clean.append({"from":p,"size":f["size"],"modify":f.get("modify"),
                          "category":category(p)})
        elif ARCHIVE.search(p):
            d=str(PurePosixPath(p).parent)
            media=[x["path"] for x in bydir[d] if PurePosixPath(x["path"]).suffix.lower() in VIDEO and (x.get("size") or 0)>0]
            record={"from":p,"size":f.get("size"),"modify":f.get("modify"),
                    "extracted_video_in_same_directory":media[:8]}
            if media: archives.append(record)
            else: reserved.append(record)
    return {"root":ROOT,"nfo":sum(x["category"]=="nfo" for x in clean),
            "screenshots":sum(x["category"]=="screenshot" for x in clean),
            "debris_candidates":clean,"archive_review":archives,"archive_without_local_video":reserved,
            "important":"Archive candidates are NEVER auto-delete candidates; verify extracted content and archive relationship separately."}
def validate(manifest):
    if set(manifest)!={"root","batch_id","entries","description"} or manifest["root"]!=ROOT:
        raise ValueError("Invalid manifest envelope")
    if not isinstance(manifest["batch_id"],str) or not re.fullmatch("[a-zA-Z0-9_-]{5,48}",manifest["batch_id"]):
        raise ValueError("Invalid batch id")
    if not isinstance(manifest["description"],str) or len(manifest["description"])<15:raise ValueError("Missing rationale")
    entries=manifest["entries"]
    if not isinstance(entries,list) or not 1<=len(entries)<=300:raise ValueError("Batch must have 1..300 entries")
    seen=set()
    for entry in entries:
        if not isinstance(entry,dict) or set(entry)!={"from","size","modify","category"}:raise ValueError("Unexpected entry keys")
        p=safe(entry["from"])
        if category(p)!=entry["category"] or entry["category"] not in ("nfo","screenshot"):
            raise ValueError("Not an exact approved debris class")
        if p.casefold() in seen:raise ValueError("Duplicate delete")
        seen.add(p.casefold())
        if not isinstance(entry["size"],int) or isinstance(entry["size"],bool) or entry["size"]<0:raise ValueError("Invalid size")
        if entry["modify"] is not None and not re.fullmatch(r"\d{14}",entry["modify"]):raise ValueError("Invalid date")
    return entries
def lookup(ftp,path):
    p=PurePosixPath(path);ftp.cwd(str(p.parent))
    matches=[facts for name,facts in ftp.mlsd() if name==p.name]
    if len(matches)!=1:raise ValueError("Path missing or ambiguous")
    return matches[0]
def execute(ftp,manifest,audit_path):
    batch=validate(manifest)
    audit_path.parent.mkdir(parents=True,exist_ok=True)
    completed=[]
    def save(status):
        with audit_path.open("w") as f:
            json.dump({"batch_id":manifest["batch_id"],"status":status,"completed":completed},f,indent=2)
            f.flush();os.fsync(f.fileno())
    for item in batch:
        facts=lookup(ftp,item["from"])
        if facts.get("type")!="file" or str(facts.get("size"))!=str(item["size"]) or (item["modify"] and facts.get("modify")!=item["modify"]):
            raise ValueError("Preflight refused changed file")
    save("preflight_passed")
    try:
        for item in batch:
            facts=lookup(ftp,item["from"])
            if facts.get("type")!="file" or str(facts.get("size"))!=str(item["size"]) or (item["modify"] and facts.get("modify")!=item["modify"]):
                raise ValueError("Changed between preflight and deletion")
            ftp.delete(item["from"])
            completed.append(item)
            save("in_progress")
    finally:save("complete" if len(completed)==len(batch) else "partial")
def main():
    p=argparse.ArgumentParser();p.add_argument("--inventory");p.add_argument("--report");p.add_argument("--manifest");p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    if a.inventory:
        report=assess(json.loads(Path(a.inventory).read_text()))
        Path(a.report).write_text(json.dumps(report,indent=2,ensure_ascii=False))
        print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in report.items() if k!="important"}))
    if a.manifest:
        m=json.loads(Path(a.manifest).read_text());validate(m)
        if a.apply:
            with connect() as ftp:execute(ftp,m,Path("media-organizer/delete-output/completed.json"))
if __name__=="__main__":main()
