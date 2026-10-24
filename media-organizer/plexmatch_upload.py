#!/usr/bin/env python3
"""Create exact Plex match-hint files from reviewed, source-verified records.

No media rename/download/deletion and no existing .plexmatch overwrite.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path, PurePosixPath
import argparse, ftplib, json, os, re
from organize import ROOT, VIDEO, connect, safe

def validate(manifest):
    if not isinstance(manifest,dict) or set(manifest)!={"batch_id","entries"}:
        raise ValueError("Only batch_id and entries are permitted")
    if not re.fullmatch(r"[a-z0-9_-]{5,64}",manifest["batch_id"]):
        raise ValueError("Bad batch ID")
    if not isinstance(manifest["entries"],list) or not 1<=len(manifest["entries"])<=5:
        raise ValueError("1-5 exact locations required")
    paths=set()
    for e in manifest["entries"]:
        if not isinstance(e,dict) or set(e)!={"directory","show","year","season","episodes"}:
            raise ValueError("Unexpected hint item keys")
        directory=safe(e["directory"]+"/.plexmatch")
        if not isinstance(e["show"],str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 '().,&:-]{2,95}",e["show"]):
            raise ValueError("Unsupported show name")
        if not isinstance(e["year"],int) or not 1900<=e["year"]<=2100:
            raise ValueError("Unsupported show year")
        if not isinstance(e["season"],int) or not 0<=e["season"]<=60:
            raise ValueError("Unsupported season number")
        if directory.casefold() in paths:raise ValueError("Duplicate folder")
        paths.add(directory.casefold())
        if not isinstance(e["episodes"],list) or not 1<=len(e["episodes"])<=250:
            raise ValueError("Missing or oversized episode list")
        eps=set();names=set()
        for ep in e["episodes"]:
            if not isinstance(ep,dict) or set(ep)!={"number","filename","size","modify"}:
                raise ValueError("Unexpected episode fields")
            number=ep["number"];name=ep["filename"]
            if not isinstance(number,int) or isinstance(number,bool) or not 1<=number<=400 or number in eps:
                raise ValueError("Invalid or repeated episode")
            if not isinstance(name,str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._ ()'&,\-]{0,220}",name):
                raise ValueError("Unsafe episode basename")
            if PurePosixPath(name).suffix.lower() not in VIDEO or name.casefold() in names:
                raise ValueError("Unsupported or duplicate video")
            if not isinstance(ep["size"],int) or ep["size"]<=0:
                raise ValueError("Missing/invalid episode size")
            if ep["modify"] is not None and (not isinstance(ep["modify"],str) or not re.fullmatch(r"\d{14}",ep["modify"])):
                raise ValueError("Bad modification timestamp")
            eps.add(number);names.add(name.casefold())
    return manifest["entries"]

def contents(entry):
    lines=["# Verified Plex match hints; preserve original media filenames",
           "Title: "+entry["show"],"Year: "+str(entry["year"]),
           "Season: "+str(entry["season"])]
    lines.extend("ep: S%02dE%02d: %s"%(entry["season"],ep["number"],ep["filename"])
                 for ep in sorted(entry["episodes"],key=lambda e:e["number"]))
    return ("\n".join(lines)+"\n").encode("utf-8")

def apply(ftp,manifest,output):
    entries=validate(manifest)
    # All source witnesses are checked before writing ANY hints.
    for item in entries:
        ftp.cwd(item["directory"])
        listing={}
        for name,facts in ftp.mlsd():
            listing.setdefault(name.casefold(),[]).append((name,facts))
        for ep in item["episodes"]:
            matches=listing.get(ep["filename"].casefold(),[])
            if len(matches)!=1 or matches[0][0]!=ep["filename"] or matches[0][1].get("type")!="file":
                raise ValueError("Missing or ambiguous original episode filename")
            facts=matches[0][1]
            if str(facts.get("size"))!=str(ep["size"]):
                raise ValueError("Episode size changed")
            if ep["modify"] and facts.get("modify")!=ep["modify"]:
                raise ValueError("Episode modification time changed")
        matching=listing.get(".plexmatch",[])
        if matching:raise ValueError("Existing .plexmatch requires manual reconciliation")
    record={"batch_id":manifest["batch_id"],"completed":[],"status":"started"}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(record,indent=2))
    try:
        for item in entries:
            ftp.cwd(item["directory"])
            # A final direct read probes hidden files which some MLSD listings omit.
            existing=bytearray()
            try:
                ftp.retrbinary("RETR .plexmatch",existing.extend)
            except ftplib.error_perm as exc:
                if not str(exc).startswith("550"):raise
            else:
                if bytes(existing)==contents(item):
                    record["completed"].append({"path":item["directory"]+"/.plexmatch","result":"already-identical"})
                    output.write_text(json.dumps(record,indent=2))
                    continue
                raise ValueError("Existing .plexmatch content differs")
            payload=contents(item)
            ftp.storbinary("STOR .plexmatch",BytesIO(payload))
            recovered=bytearray()
            ftp.retrbinary("RETR .plexmatch",recovered.extend)
            if bytes(recovered)!=payload:raise ValueError("FTP uploaded hint failed readback")
            record["completed"].append({"path":item["directory"]+"/.plexmatch","result":"verified-upload","bytes":len(payload)})
            output.write_text(json.dumps(record,indent=2))
    finally:
        record["status"]="complete" if len(record["completed"])==len(entries) else "partial_or_failed"
        output.write_text(json.dumps(record,indent=2))
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",default="media-organizer/plexmatch/approved.json")
    ap.add_argument("--validate-only",action="store_true")
    args=ap.parse_args()
    manifest=json.loads(Path(args.manifest).read_text())
    entries=validate(manifest)
    print("Verified Plex match-hint manifest entries:",len(entries))
    if not args.validate_only:
        with connect() as ftp:
            apply(ftp,manifest,Path("media-organizer/plexmatch-output/completed.json"))
if __name__=="__main__":main()
