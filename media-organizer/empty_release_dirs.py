#!/usr/bin/env python3
"""Remove only exact, owner-reviewed, presently empty old release directories."""
from __future__ import annotations
import argparse
import json
import os
import re
from pathlib import Path, PurePosixPath
from organize import ROOT, connect, safe

def validate(document):
    if not isinstance(document, dict) or set(document)!={"root","batch_id","description","directories"}:
        raise ValueError("Bad release-directory removal manifest")
    if document["root"]!=ROOT:
        raise ValueError("Only /downloads is allowed")
    if not isinstance(document["batch_id"],str) or not re.fullmatch(r"[a-zA-Z0-9_-]{5,48}",document["batch_id"]):
        raise ValueError("Invalid batch ID")
    if not isinstance(document["description"],str) or len(document["description"])<15:
        raise ValueError("Document why the folders are obsolete")
    directories=document["directories"]
    if not isinstance(directories,list) or not 1<=len(directories)<=150:
        raise ValueError("Directory batch must contain 1..150 exact paths")
    seen=set()
    for folder in directories:
        if not isinstance(folder,str):raise ValueError("Directory must be a string")
        safe(folder)
        p=PurePosixPath(folder)
        if len(p.parts)<3 or folder==ROOT:
            raise ValueError("Never remove the Downloads root")
        if any(part.startswith(".") for part in p.parts[2:]):
            raise ValueError("Hidden or navigation folders are forbidden")
        if folder.casefold() in seen:
            raise ValueError("Duplicate folder")
        seen.add(folder.casefold())
    return sorted(directories,key=lambda x:(-len(PurePosixPath(x).parts),x.casefold()))

def matching_entry(ftp, directory, basename):
    ftp.cwd(directory)
    names=[(name,facts) for name,facts in ftp.mlsd() if name.casefold()==basename.casefold()]
    if len(names)!=1 or names[0][0]!=basename:
        return None
    return names[0][1]

def execute(ftp, document, audit):
    folders=validate(document)
    removed=[];skipped=[]
    audit.parent.mkdir(parents=True,exist_ok=True)
    def write(status):
        with audit.open("w",encoding="utf-8") as handle:
            json.dump({"batch_id":document["batch_id"],"status":status,"removed":removed,"skipped":skipped},handle,indent=2)
            handle.flush();os.fsync(handle.fileno())
    write("started")
    try:
        for directory in folders:
            p=PurePosixPath(directory)
            try:
                entry=matching_entry(ftp,str(p.parent),p.name)
                if not entry or entry.get("type")!="dir":
                    skipped.append({"path":directory,"reason":"missing, case-conflicted, or not directory"})
                    write("in_progress")
                    continue
                ftp.cwd(directory)
                children=[n for n,_ in ftp.mlsd() if n not in (".","..")]
                if children:
                    skipped.append({"path":directory,"reason":"nonempty"})
                    write("in_progress")
                    continue
                ftp.cwd(ROOT)
                ftp.rmd(directory)
                removed.append(directory)
            except Exception as exc:
                skipped.append({"path":directory,"reason":type(exc).__name__})
            write("in_progress")
    finally:
        write("complete" if not skipped else "complete_with_skips")
    return removed,skipped

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",default="media-organizer/approved-empty-release.json")
    p.add_argument("--audit",default="media-organizer/empty-release-output/completed.json")
    p.add_argument("--apply",action="store_true")
    args=p.parse_args()
    plan=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    folders=validate(plan)
    print("Validated",len(folders),"exact release directory removal candidates")
    if args.apply:
        with connect() as ftp:
            done,skipped=execute(ftp,plan,Path(args.audit))
            print("FTP_EMPTY_RELEASE_RESULT",json.dumps({"removed":len(done),"skipped":len(skipped)}))
if __name__=="__main__":main()
