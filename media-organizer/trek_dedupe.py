#!/usr/bin/env python3
"""Delete reviewed duplicate Star Trek videos ONLY with an exact retained counterpart."""
from __future__ import annotations
import argparse,ftplib,json,os,re
from pathlib import Path,PurePosixPath
from organize import ROOT,connect,safe
VIDEO={".mkv",".mp4",".avi",".m4v"}
SERIES={"discovery":"discovery","lower_decks":"lower decks","strange_new_worlds":"strange new worlds"}
EP=re.compile(r"(?i)S(\d{2})E(\d{2})")
def info(path):
    p=PurePosixPath(safe(path))
    if p.suffix.lower() not in VIDEO:raise ValueError("Expected video file")
    s=str(p).lower().replace("."," ").replace("_"," ").replace("-"," ")
    if re.search(r"star\s+trek\s+enterprise",s):raise ValueError("Enterprise excluded")
    if re.search(r"star\s+trek\s+lower\s+decks",s):show="lower_decks"
    elif re.search(r"star\s+trek\s+strange\s+new\s+worlds?",s):show="strange_new_worlds"
    elif re.search(r"star\s+trek\s+discovery",s):show="discovery"
    else:raise ValueError("Unrecognized Trek subseries")
    token=EP.search(str(p.name))
    if not token:raise ValueError("No filename SxxEyy identity")
    return show,token.group(1),token.group(2)
def validate(m):
    if set(m)!={"root","batch_id","description","groups"} or m["root"]!=ROOT:raise ValueError("Invalid envelope")
    if not re.fullmatch(r"[A-Za-z0-9_-]{5,48}",m["batch_id"]):raise ValueError("Invalid batch id")
    if len(m["description"])<20:raise ValueError("Explain user-approved selection rationale")
    if not isinstance(m["groups"],list) or not 1<=len(m["groups"])<=25:raise ValueError("Expected 1..25 duplicate groups")
    seen=set(); winners=set(); losses=[]
    for g in m["groups"]:
        if set(g)!={"show","season","episode","retain","delete","reason"}:raise ValueError("Unexpected group keys")
        if g["show"] not in SERIES or not re.fullmatch(r"\d{2}",g["season"]) or not re.fullmatch(r"\d{2}",g["episode"]):raise ValueError("Bad episode identity")
        if not isinstance(g["reason"],str) or len(g["reason"])<25:raise ValueError("Document quality preference")
        if not isinstance(g["delete"],list) or not g["delete"]:raise ValueError("Missing losers")
        for item in [g["retain"]]+g["delete"]:
            if set(item)!={"from","size","modify"}:raise ValueError("Unexpected metadata")
            if not isinstance(item["size"],int) or isinstance(item["size"],bool) or item["size"]<1:raise ValueError("Bad media size")
            if not isinstance(item["modify"],str) or not re.fullmatch(r"\d{14}",item["modify"]):raise ValueError("Exact FTP mtime required")
            if info(item["from"])!=(g["show"],g["season"],g["episode"]):raise ValueError("Cross-show or cross-episode match")
            if item["from"].casefold() in seen:raise ValueError("File appears in multiple roles/groups")
            seen.add(item["from"].casefold())
        winners.add(g["retain"]["from"]);losses.extend(g["delete"])
    if len(losses)>100:raise ValueError("Max 100 explicit deletions")
    return losses
def lookup(ftp,path):
    p=PurePosixPath(path);ftp.cwd(str(p.parent))
    matches=[facts for name,facts in ftp.mlsd() if name==p.name]
    if len(matches)!=1:raise ValueError("Missing/ambiguous source or keeper: "+path)
    return matches[0]
def match_exact(ftp,item):
    facts=lookup(ftp,item["from"])
    if facts.get("type")!="file" or str(facts.get("size"))!=str(item["size"]) or facts.get("modify")!=item["modify"]:
        raise ValueError("File changed: "+item["from"])
def execute(ftp,m,audit):
    validate(m);audit.parent.mkdir(parents=True,exist_ok=True)
    done=[]
    def save(status):
        with audit.open("w",encoding="utf-8") as out:
            json.dump({"batch_id":m["batch_id"],"status":status,"deleted":done},out,indent=2)
            out.flush();os.fsync(out.fileno())
    # Preflight EVERY loser AND intended keeper before touching any file.
    for group in m["groups"]:
        for item in [group["retain"]]+group["delete"]:match_exact(ftp,item)
    save("preflight_passed")
    try:
        for group in m["groups"]:
            for loser in group["delete"]:
                match_exact(ftp,group["retain"])
                match_exact(ftp,loser)
                ftp.delete(loser["from"])
                done.append(loser["from"]);save("in_progress")
    finally:
        required=sum(len(g["delete"]) for g in m["groups"])
        save("complete" if len(done)==required else "partial_or_failed")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",default="media-organizer/approved-trek-dedupe.json")
    p.add_argument("--audit",default="media-organizer/trek-dedupe-output/completed.json")
    p.add_argument("--apply",action="store_true")
    args=p.parse_args()
    m=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    losers=validate(m)
    print("Validated",len(m["groups"]),"Trek episodes and",len(losers),"explicit duplicate videos")
    if args.apply:
        with connect() as ftp:execute(ftp,m,Path(args.audit))
if __name__=="__main__":main()
