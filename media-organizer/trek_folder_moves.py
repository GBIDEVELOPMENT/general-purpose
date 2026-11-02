#!/usr/bin/env python3
"""Exact-inventory-pinned, non-destructive Star Trek directory relocations.

A single source directory is renamed atomically by the FTP server. The reviewed
directory is shallow and its entire file inventory is verified before and after
RNFR/RNTO. No content deletion, recursive rename traversal, or overwriting.
"""
from __future__ import annotations
import ftplib
import json
import os
import re
from pathlib import Path, PurePosixPath
from organize import ROOT, connect, safe

REVIEW=Path("media-organizer/review/trek-folders-2026-11-02.json")
EXPECTED_ID="trek_folders_12_20261102"
EXPECTED_SHA="93695dc4ad24d8dbf57c6637679609a8ea85b445"
EXPECTED_FILES=200
EXPECTED_BYTES=158506008493

def expected_target(root):
    if root=="star-trek-ds9-laserdisc-720p-24":
        return "/downloads/Star Trek/Star Trek Deep Space Nine/Alternate Editions/"+root
    if root=="Star Trek Voyager 1995.S01.1080p.NTSC DVD Upscale.H265.10bit.DDP5.1-Zero00":
        return "/downloads/Star Trek/Star Trek Voyager/Alternate Editions/"+root
    if re.fullmatch(r"Star[ .]Trek[ .]Strange[ .]New[ .]Worlds[ .]S04E(?:0[1-9]|10).*",root):
        return "/downloads/Star Trek/Star Trek Strange New Worlds (2022)/Season 04/"+root
    raise ValueError("Not an approved legacy or season-04 Trek release folder")

def validate(plan):
    reviewed=json.loads(REVIEW.read_text(encoding="utf-8"))
    if plan!=reviewed:raise ValueError("Move manifest differs from frozen reviewed plan")
    if set(plan)!={"root","batch_id","description","snapshot","totals","trek_folder_moves"}:
        raise ValueError("Invalid Trek folder batch envelope")
    if plan["root"]!=ROOT or plan["batch_id"]!=EXPECTED_ID or len(plan["description"])<25:
        raise ValueError("Unexpected owner-approved folder batch")
    s=plan["snapshot"]
    if (s!={"inventory_blob_sha":EXPECTED_SHA,"files":2598,"directories":442,"failures":0,"truncated":0}):
        raise ValueError("Wrong audited source snapshot")
    totals=plan["totals"]
    if totals!={"folders":12,"files":EXPECTED_FILES,"bytes":EXPECTED_BYTES}:
        raise ValueError("Wrong expected 12-folder move totals")
    moves=plan["trek_folder_moves"]
    if not isinstance(moves,list) or len(moves)!=12:
        raise ValueError("Expected exactly 12 approved release directories")
    sources=set();dests=set();allbytes=0;allfiles=0
    for move in moves:
        if set(move)!={"from","to","reason","files"}:raise ValueError("Unexpected directory move fields")
        source=safe(move["from"]);dest=safe(move["to"])
        src=PurePosixPath(source)
        if str(src.parent)!=ROOT or source.startswith("/downloads/Star Trek/"):
            raise ValueError("Only stray top-level Trek release folders")
        if dest!=expected_target(src.name):raise ValueError("Unapproved franchise/series destination")
        if source.casefold() in sources or dest.casefold() in dests:
            raise ValueError("Repeated source or destination")
        sources.add(source.casefold());dests.add(dest.casefold())
        if not isinstance(move["reason"],str) or len(move["reason"])<15:
            raise ValueError("Missing alternate-edition preservation rationale")
        children=move["files"]
        if not isinstance(children,list) or len(children)<1 or len(children)>200:
            raise ValueError("Invalid exact direct-child inventory")
        seen=set()
        for child in children:
            if set(child)!={"name","size","modify"}:raise ValueError("Unexpected child facts")
            name=child["name"]
            if (not isinstance(name,str) or not name or name in (".","..") or
                    "/" in name or "\\" in name or name.startswith(".")):
                raise ValueError("No hidden, nested, or unsafe direct children")
            if name.casefold() in seen:raise ValueError("Duplicate child name")
            seen.add(name.casefold())
            if not isinstance(child["size"],int) or isinstance(child["size"],bool) or child["size"]<0:
                raise ValueError("Invalid pinned child size")
            if not isinstance(child["modify"],str) or not re.fullmatch(r"\d{14}",child["modify"]):
                raise ValueError("Missing pinned child modified time")
            allfiles+=1;allbytes+=child["size"]
    if len(sources)!=12 or len(dests)!=12 or allfiles!=EXPECTED_FILES or allbytes!=EXPECTED_BYTES:
        raise ValueError("Whole 200-file source inventory does not match")
    return moves

def exact(ftp,parent,name):
    ftp.cwd(parent)
    matches=[(entry,facts) for entry,facts in ftp.mlsd() if entry.casefold()==name.casefold()]
    if not matches:return None
    if len(matches)!=1 or matches[0][0]!=name:
        raise ValueError("Case-conflicted or ambiguous remote path")
    return matches[0][1]

def optional(ftp,parent,name):
    try:return exact(ftp,parent,name)
    except ftplib.error_perm as exc:
        if str(exc).startswith("550"):return None
        raise

def exact_children(ftp,directory,expected):
    ftp.cwd(directory)
    listing=[(name,facts) for name,facts in ftp.mlsd() if name not in (".","..")]
    names={x["name"]:x for x in expected}
    if len(listing)!=len(names) or {n for n,_ in listing}!=set(names):
        raise ValueError("Unexpected, missing, extra or hidden directory entries: "+directory)
    for name,facts in listing:
        baseline=names[name]
        if (facts.get("type")!="file" or str(facts.get("size"))!=str(baseline["size"]) or
                facts.get("modify")!=baseline["modify"]):
            raise ValueError("Directory child type/size/mtime changed: "+directory+"/"+name)

def ensure_parent(ftp,parent):
    current=ROOT
    for name in PurePosixPath(parent).parts[2:]:
        if name.startswith("."):raise ValueError("Hidden destination folder")
        here=optional(ftp,current,name)
        nextpath=current.rstrip("/")+"/"+name
        if here is None:ftp.mkd(nextpath)
        elif here.get("type")!="dir":raise ValueError("Destination parent is not a folder")
        current=nextpath

def persist(path,plan,completed,status):
    path.parent.mkdir(parents=True,exist_ok=True)
    payload={"batch_id":plan["batch_id"],"status":status,
             "total_folders":len(plan["trek_folder_moves"]),
             "completed":completed}
    with path.open("w",encoding="utf-8") as f:
        json.dump(payload,f,indent=2,ensure_ascii=False)
        f.flush();os.fsync(f.fileno())

def execute(ftp,plan,audit_path):
    moves=validate(plan)
    # Before touching a file or creating a directory, inventory EVERY source
    # and check existing destination branches are collision-free.
    for move in moves:
        src=PurePosixPath(move["from"]);dst=PurePosixPath(move["to"])
        source=exact(ftp,str(src.parent),src.name)
        if source is None or source.get("type")!="dir":
            raise ValueError("Source release folder absent: "+str(src))
        exact_children(ftp,str(src),move["files"])
        if optional(ftp,str(dst.parent),dst.name) is not None:
            raise ValueError("Destination already exists: "+str(dst))
    done=[]
    persist(audit_path,plan,done,"preflight_passed")
    try:
        for move in moves:
            src=PurePosixPath(move["from"]);dst=PurePosixPath(move["to"])
            exact_children(ftp,str(src),move["files"])
            ensure_parent(ftp,str(dst.parent))
            if optional(ftp,str(dst.parent),dst.name) is not None:
                raise ValueError("Destination appeared while moving: "+str(dst))
            ftp.rename(str(src),str(dst))
            # Persist acknowledgement BEFORE attempting post-rename checks.
            done.append({"from":str(src),"to":str(dst),"files":len(move["files"]),
                         "bytes":sum(x["size"] for x in move["files"]),
                         "destination_verified":False})
            persist(audit_path,plan,done,"in_progress")
            facts=exact(ftp,str(dst.parent),dst.name)
            if facts is None or facts.get("type")!="dir":
                raise RuntimeError("Moved directory not found; inspect durable journal")
            exact_children(ftp,str(dst),move["files"])
            if optional(ftp,str(src.parent),src.name) is not None:
                raise RuntimeError("Original directory still present; inspect journal")
            done[-1]["destination_verified"]=True
            persist(audit_path,plan,done,"in_progress")
    finally:
        good=(len(done)==len(moves) and all(x["destination_verified"] for x in done))
        persist(audit_path,plan,done,"complete" if good else "partial_or_failed")
    return done
