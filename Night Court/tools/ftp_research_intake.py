#!/usr/bin/env python3
"""Bounded owner-authorized Night Court FTP discovery and file staging.

Connection settings mirror gamesbyian/S60's ftp-inventory.yml:
  FTP_HOST, FTP_USER, FTP_PASSWORD; login root normally contains /downloads.

This has no periodic scheduler, and never retrieves video, logs credentials,
uploads to FTP, executes remote content, or downloads unrequested files.
'stage' requires one precise explicitly requested remote subtitle/archive path.
Plain FTP mirrors S60 but sends credentials without transport encryption:
prefer --protocol ftps if the server supports explicit FTPS.
"""
from __future__ import annotations

import argparse
from collections import deque
import ftplib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
from tempfile import NamedTemporaryFile

ROOT=Path(__file__).resolve().parents[1]
DOWNLOAD_ROOT="/downloads"
ALLOWED={".srt",".vtt",".txt",".zip",".rar"}
STAGE_LIMIT=90_000_000
MAX_DIRS=180
MAX_DEPTH=3
MAX_ENTRIES=600
ARCHIVES=ROOT/"research"/"source-archives"
STAGING=ROOT/"incoming"
MANIFEST=ROOT/"research"/"ftp-staging-records.jsonl"
SUBTITLE_NAME=re.compile(r"(?i)\.(?:srt|vtt|txt|zip|rar)$")
ORIGINAL_NAME=re.compile(r"(?i)(?:night[\W_]*court|^s0?[1-9][._ -]*e\d{1,2}\b)")

def clean_path(path,*,file=False):
    if not isinstance(path,str) or not path.startswith("/") or "\x00" in path or "\\" in path:
        raise ValueError("FTP path must be an absolute POSIX path")
    pos=PurePosixPath(path)
    if any(p in ("..",".") for p in path.split("/")):
        raise ValueError("FTP path traversal rejected")
    if not str(pos).startswith(DOWNLOAD_ROOT+"/"):
        if str(pos)!=DOWNLOAD_ROOT or file:
            raise ValueError("Access limited to /downloads")
    if any(p.startswith(".") for p in pos.parts if p not in ("/",)):
        raise ValueError("Hidden FTP paths are not requested")
    if file:
        basename=pos.name
        if len(basename)>180 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._ ()+\-']*",basename):
            raise ValueError("Unsupported or unsafe source filename")
        if pos.suffix.casefold() not in ALLOWED:raise ValueError("Only subtitle/text/RAR/ZIP sources may be staged")
        if "2023" in path.casefold() or "reboot" in path.casefold():
            raise ValueError("Possible 2023 revival source: not original series")
        # Avoid silently copying unrelated resources under the same FTP account.
        if not any("nightcourt" in re.sub(r"[^a-z0-9]","",part.casefold()) for part in pos.parts):
            raise ValueError("Source must reside inside a Night Court-named FTP directory")
    return str(pos)

def is_night_court_dir(name):
    simplified=re.sub(r"[^a-z0-9]","",name.casefold())
    return "nightcourt" in simplified

def list_here(ftp,path):
    path=clean_path(path)
    ftp.cwd(path)
    try:
        rows=[(name,facts) for name,facts in ftp.mlsd() if name not in (".","..")]
        if len(rows)>MAX_ENTRIES:raise ValueError("FTP folder entry limit exceeded")
        return sorted(rows,key=lambda x:x[0].casefold())
    except (ftplib.error_perm,AttributeError):
        # As in S60, support servers without MLSD, with guarded NLST fallback.
        names=ftp.nlst()
        if len(names)>MAX_ENTRIES:raise ValueError("FTP folder entry limit exceeded")
        out=[]
        for remote in names:
            name=remote.rstrip("/").rsplit("/",1)[-1]
            if name in (".","..") or not name:continue
            try:
                ftp.cwd(clean_path(path.rstrip("/")+"/"+name))
                kind="dir"
            except (ftplib.error_perm,ValueError):
                kind="file"
            out.append((name,{"type":kind}))
        ftp.cwd(path)
        return sorted(out,key=lambda x:x[0].casefold())

def inventory(ftp,from_dir=DOWNLOAD_ROOT):
    from_dir=clean_path(from_dir)
    q=deque([(from_dir,0)])
    visited=0
    found=[]
    seen=set()
    while q and visited<MAX_DIRS:
        where,depth=q.popleft()
        if where in seen:continue
        seen.add(where);visited+=1
        try:items=list_here(ftp,where)
        except (ftplib.error_perm,ValueError) as exc:
            # No credential text or FTP exception (which may embed the remote
            # directory) is printed. The path itself was user-selected.
            print("INACCESSIBLE",where,exc.__class__.__name__)
            continue
        if any(is_night_court_dir(part) for part in PurePosixPath(where).parts):
            sources=[]
            for name,detail in items:
                if not SUBTITLE_NAME.search(name) or detail.get("type")=="dir":continue
                if len(name)>180:continue
                sources.append({"name":name,
                                "size_bytes":int(detail["size"]) if
                                    str(detail.get("size","")).isdigit() else None,
                                "path":where.rstrip("/")+"/"+name})
            found.append({"directory":where,"eligible_source_files":sources,
                          "eligible_count":len(sources)})
        if depth<MAX_DEPTH:
            for name,detail in items:
                if detail.get("type")!="dir":continue
                # Avoid escaping the declared subtree via listing oddities.
                if name in (".","..") or "/" in name or "\\" in name:continue
                nextdir=clean_path(where.rstrip("/")+"/"+name)
                q.append((nextdir,depth+1))
    report={"scan_root":from_dir,"directories_inspected":visited,
            "directory_limit":MAX_DIRS,"max_depth":MAX_DEPTH,
            "night_court_directories":found,
            "matching_source_files":sum(x["eligible_count"] for x in found),
            "bound_reached":bool(q),
            "note":"Metadata inventory only. File contents, credentials and unrelated FTP directory filenames are not logged."}
    print("NIGHT_COURT_FTP_INVENTORY_JSON")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return report

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda:source.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def stage(ftp,path):
    remote=clean_path(path,file=True)
    name=PurePosixPath(remote).name
    STAGING.mkdir(parents=True,exist_ok=True)
    archived=ARCHIVES/name
    if archived.exists():
        print("ALREADY_ARCHIVED",name,sha(archived))
        return {"action":"already_archived","name":name,"sha256":sha(archived)}
    destination=STAGING/name
    if destination.exists():
        print("ALREADY_STAGED",name,sha(destination))
        return {"action":"already_staged","name":name,"sha256":sha(destination)}
    try:
        remote_size=ftp.size(remote)
    except ftplib.all_errors:
        remote_size=None
    if remote_size is not None and (remote_size<1 or remote_size>STAGE_LIMIT):
        raise ValueError("FTP file exceeds 90 MB staged-source limit")
    count=0
    tmp=None
    try:
        with NamedTemporaryFile(mode="wb",prefix=".nc-ftp-",dir=STAGING,delete=False) as temp:
            tmp=Path(temp.name)
            def write(data):
                nonlocal count
                count+=len(data)
                if count>STAGE_LIMIT:raise ValueError("Remote file exceeds bounded transfer size")
                temp.write(data)
            ftp.retrbinary("RETR "+remote,write,blocksize=64*1024)
        if count<1:raise ValueError("Remote source file empty")
        if destination.exists():raise ValueError("Stage destination created during transfer")
        tmp.rename(destination)
        tmp=None
    finally:
        if tmp and tmp.exists():tmp.unlink()
    digest=sha(destination)
    row={
        "source":"owner_requested_ftp_staging",
        "source_ftp_path":remote,
        "file":str(destination.relative_to(ROOT)),
        "sha256":digest,
        "size_bytes":count,
        "content_type_suffix":destination.suffix.lower(),
        "rights_note":"Owner explicitly dispatched read from private FTP; no automatic licensing conclusion",
        "status":"staged_only_not_automatically_proven_to_be_original_1984_or_complete",
        "secret_storage":"GitHub Actions FTP_PASSWORD repository secret, never serialized here"
    }
    lines=[json.loads(s) for s in MANIFEST.read_text("utf-8").splitlines() if s.strip()] if MANIFEST.exists() else []
    if not any(item.get("sha256")==digest and item.get("file")==row["file"] for item in lines):
        lines.append(row)
        MANIFEST.parent.mkdir(parents=True,exist_ok=True)
        MANIFEST.write_text("\n".join(json.dumps(x,sort_keys=True,ensure_ascii=False) for x in lines)+"\n",encoding="utf-8")
    print("STAGED",json.dumps({"filename":name,"sha256":digest,"size_bytes":count},ensure_ascii=False))
    # Explicit review comes before attempting format-dependent importer and
    # episode identity assignment; no source bytes are printed.
    return row

def connect(host,user,password,protocol):
    if not password:
        raise ValueError("FTP_PASSWORD GitHub Actions secret is missing or empty")
    if not host or not user:raise ValueError("FTP server/user configuration missing")
    ftp=ftplib.FTP_TLS(timeout=30) if protocol=="ftps" else ftplib.FTP(timeout=30)
    ftp.connect(host,21,timeout=30)
    ftp.login(user,password)
    if protocol=="ftps":ftp.prot_p()
    ftp.set_pasv(True)
    return ftp

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode",choices=["inventory","stage"],default="inventory")
    parser.add_argument("--protocol",choices=["ftp","ftps"],default="ftp",
                        help="ftp matches S60 but is cleartext; ftps is preferable if supported")
    parser.add_argument("--root",default=DOWNLOAD_ROOT,help="inventory-only base, within /downloads")
    parser.add_argument("--remote-file",help="one explicit Night Court path, stage mode only")
    args=parser.parse_args()
    if args.mode=="stage" and not args.remote_file:
        parser.error("stage requires an explicit --remote-file")
    if args.mode=="inventory" and args.remote_file:
        parser.error("--remote-file is only permitted in stage mode")
    ftp=connect(os.environ.get("FTP_HOST","wood.seedhost.eu"),
                os.environ.get("FTP_USER","ianseeds"),
                os.environ.get("FTP_PASSWORD",""),args.protocol)
    try:
        if args.mode=="inventory":inventory(ftp,args.root)
        else:stage(ftp,args.remote_file)
    finally:
        try:ftp.quit()
        except ftplib.all_errors:ftp.close()
if __name__=="__main__":
    main()
