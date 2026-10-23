#!/usr/bin/env python3
"""Conservative FTP /downloads inventory and Plex-oriented rename planner."""
import argparse, ftplib, hashlib, json, os, re
from collections import deque
from pathlib import PurePosixPath
from pathlib import Path

ROOT="/downloads"
VIDEO={".mkv",".mp4",".avi",".m4v",".mov",".wmv",".ts",".mpg",".mpeg"}
SIDE={".srt",".ass",".ssa",".sub",".idx",".nfo"}
EP=re.compile(r"(?i)(?<![a-z0-9])s(\d{1,2})[ ._-]*e(\d{1,3})(?!\d)")
YEAR=re.compile(r"(?<!\d)(19\d\d|20\d\d)(?!\d)")
RELEASE=re.compile(r"(?i)[ ._-]+(?:1080p|720p|2160p|480p|webrip|web-dl|bluray|brrip|dvdrip|hdtv|x26[45]|h26[45]|hevc|aac|dts|proper|repack|yify|rarbg)(?:[ ._-]|$)")
def safe(p):
    if not isinstance(p,str) or not p.startswith(ROOT+"/") or any(x in (".","..") for x in p.split("/")) or "\\" in p or "\x00" in p:
        raise ValueError("unsafe FTP path")
    return p
def connect():
    host=os.environ["FTP_HOST"]; user=os.environ["FTP_USER"]; passwd=os.environ["FTP_PASSWORD"]
    protocol=os.environ.get("FTP_PROTOCOL","ftp")
    ftp=ftplib.FTP_TLS(timeout=30) if protocol=="ftps" else ftplib.FTP(timeout=30)
    ftp.connect(host,21); ftp.login(user,passwd)
    if protocol=="ftps": ftp.prot_p()
    return ftp
def scan(ftp,max_dirs=1200,max_files=25000,max_depth=7):
    pending=deque([(ROOT,0)]); seen=set(); out=[]; failures=[]
    while pending:
        path,depth=pending.popleft()
        if path in seen: continue
        if len(seen)>=max_dirs or len(out)>=max_files: raise RuntimeError("inventory bound reached; increase bounds deliberately")
        seen.add(path)
        try:
            ftp.cwd(path); rows=list(ftp.mlsd())
        except (ftplib.all_errors, OSError) as err:
            failures.append({"directory":path,"error_type":type(err).__name__});continue
        for name,facts in rows:
            if name in (".","..") or "/" in name or "\\" in name or name.startswith("."):continue
            full=safe(path.rstrip("/")+"/"+name)
            kind=facts.get("type")
            if kind=="dir" and depth<max_depth: pending.append((full,depth+1))
            elif kind=="file":
                out.append({"path":full,"size":int(facts["size"]) if facts.get("size","").isdigit() else None,"modify":facts.get("modify")})
    return {"root":ROOT,"directories":len(seen),"files":sorted(out,key=lambda x:x["path"].casefold()),"failures":failures}
def basename_clean(s):
    return re.sub(r"\s+"," ",re.sub(r"[._]+"," ",s)).strip(" -")
def propose(inv):
    files=inv["files"]; changes=[]; review=[]
    known={x["path"].casefold() for x in files};destinations=set()
    for item in files:
        old=item["path"]; path=PurePosixPath(old); ext=path.suffix.lower()
        if ext not in VIDEO|SIDE:continue
        stem=path.stem; m=EP.search(stem)
        if not m:
            if ext in VIDEO:
                year=YEAR.search(stem)
                if year: review.append({"path":old,"reason":"Movie/year candidate needs title identification"})
                else: review.append({"path":old,"reason":"Unrecognized video naming; manual identification required"})
            continue
        prefix=basename_clean(stem[:m.start()]);season=int(m.group(1));episode=int(m.group(2))
        if not prefix or season>60 or episode>400:
            review.append({"path":old,"reason":"Episode number/title uncertain"});continue
        # If filename begins with SxxEyy and series is supplied by parent, use parent as title.
        # Never infer a show from release tags or a generic parent.
        if not prefix or prefix.casefold() in {"the","show","tv"}:continue
        if YEAR.search(prefix) and len(prefix)<6:continue
        label=f"S{season:02d}E{episode:02d}"
        suffix=stem[m.end():];suffix=RELEASE.split(suffix,1)[0]
        suffix=basename_clean(suffix).strip(" -")
        # Preserve episode titles where plausible; avoid release-tag confusion.
        if suffix and re.search(r"(?i)\b(?:x264|x265|webrip|hdtv|bluray|1080p)\b",suffix):suffix=""
        canonical=f"{prefix} - {label}"+(f" - {suffix}" if suffix else "")+ext
        # Keep directories unchanged in first pass. Series/franchise moves require verified mapping.
        dest=str(path.with_name(canonical))
        if dest==old:continue
        if dest.casefold() in known or dest.casefold() in destinations:
            review.append({"path":old,"proposed":dest,"reason":"Destination collision"});continue
        destinations.add(dest.casefold())
        changes.append({"from":old,"to":dest,"size":item["size"],"reason":"episode token normalization; candidate only"})
    return {"root":ROOT,"moves":changes,"review":review,"source_file_count":len(files),"failure_count":len(inv["failures"]),"notice":"Candidates are not authorized for automatic execution without explicit approved plan."}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--mode",choices=("inventory","apply"),default="inventory")
    ap.add_argument("--plan",default="media-organizer/output/approved-plan.json")
    args=ap.parse_args();out=Path("media-organizer/output");out.mkdir(parents=True,exist_ok=True)
    with connect() as ftp:
        inv=scan(ftp); (out/"inventory.json").write_text(json.dumps(inv,indent=2,ensure_ascii=False))
        plan=propose(inv); (out/"suggestions.json").write_text(json.dumps(plan,indent=2,ensure_ascii=False))
        print(f"Inventory: {len(inv['files'])} files, {inv['directories']} directories; {len(plan['moves'])} candidates, {len(plan['review'])} review; errors {len(inv['failures'])}")
        if args.mode=="inventory":return
        if inv["failures"]:raise SystemExit("Apply blocked: partial inventory")
        approved=json.loads(Path(args.plan).read_text())
        if approved.get("root")!=ROOT or not isinstance(approved.get("moves"),list):raise SystemExit("Invalid approved plan")
        filemap={x["path"]:x for x in inv["files"]}
        completed=[]
        try:
            for move in approved["moves"]:
                src=safe(move["from"]);dst=safe(move["to"])
                if src not in filemap or filemap[src]["size"]!=move["size"]:raise RuntimeError("Source changed or disappeared")
                if dst.casefold() in {p.casefold() for p in filemap}:raise RuntimeError("Destination exists")
                if PurePosixPath(src).parent!=PurePosixPath(dst).parent:raise RuntimeError("Cross-directory move requires separate review")
                if PurePosixPath(src).suffix.lower()!=PurePosixPath(dst).suffix.lower():raise RuntimeError("Extension mismatch")
                ftp.rename(src,dst);completed.append({"from":src,"to":dst,"size":move["size"]})
                (out/"completed.json").write_text(json.dumps(completed,indent=2))
        finally:
            (out/"completed.json").write_text(json.dumps(completed,indent=2))
if __name__=="__main__":main()
