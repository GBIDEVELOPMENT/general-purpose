#!/usr/bin/env python3
"""Conservative FTP /downloads inventory and Plex-oriented rename planner."""
import argparse, ftplib, json, os, re, time
from collections import deque
from pathlib import PurePosixPath
from pathlib import Path

ROOT="/downloads"
VIDEO={".mkv",".mp4",".avi",".m4v",".mov",".wmv",".ts",".mpg",".mpeg"}
SIDE={".srt",".ass",".ssa",".sub",".idx",".nfo"}
EP=re.compile(r"(?i)(?<![a-z0-9])s(\d{1,2})[ ._-]*e(\d{1,3})(?!\d)")
MULTI_EP=re.compile(r"(?i)^\s*[ ._-]*(?:e\d{1,3}|-[ ._-]*e?\d{1,3}|&[ ._-]*e?\d{1,3})")
LANGUAGE=re.compile(r"(?i)^[._ -]+([a-z]{2,3})([._ -]+(?:forced|sdh|hi))?$")
YEAR=re.compile(r"(?<!\d)(19\d\d|20\d\d)(?!\d)")
RELEASE=re.compile(r"(?i)[ ._-]+(?:1080p|720p|2160p|480p|webrip|web-dl|bluray|brrip|dvdrip|hdtv|x26[45]|h26[45]|hevc|aac|dts|proper|repack|yify|rarbg)(?:[ ._-]|$)")
def safe(p):
    if not isinstance(p,str) or not p.startswith(ROOT+"/") or any(x in (".","..") for x in p.split("/")) or "\\" in p or "\x00" in p:
        raise ValueError("unsafe FTP path")
    return p
def connect():
    host=os.environ["FTP_HOST"]; user=os.environ["FTP_USER"]; passwd=os.environ["FTP_PASSWORD"]
    protocol=os.environ.get("FTP_PROTOCOL","ftp")
    if protocol not in ("ftp","ftps"):raise ValueError("Unknown FTP protocol")
    # Only retry connection-stage transient faults. The file-move executors
    # never retry individual RNFR/RNTO or DELE operations, preserving audit safety.
    for attempt in range(3):
        ftp=ftplib.FTP_TLS(timeout=30) if protocol=="ftps" else ftplib.FTP(timeout=30)
        try:
            ftp.connect(host,21); ftp.login(user,passwd)
            if protocol=="ftps":ftp.prot_p()
            return ftp
        except (OSError, EOFError, ftplib.error_temp) as error:
            try:ftp.close()
            except Exception:pass
            if attempt==2:raise
            print(f"FTP_CONNECTION_RETRY attempt={attempt+1} error_type={type(error).__name__}",flush=True)
            time.sleep(2*(attempt+1))
        except Exception:
            try:ftp.close()
            except Exception:pass
            raise
def scan(ftp,max_dirs=1200,max_files=25000,max_depth=7,max_seconds=420):
    pending=deque([(ROOT,0)]); seen=set(); out=[]; failures=[]; truncated=[];folder_records=[];started=time.monotonic()
    while pending:
        path,depth=pending.popleft()
        if path in seen: continue
        if len(seen)>=max_dirs or len(out)>=max_files or (len(seen)>0 and time.monotonic()-started>=max_seconds):
            truncated.append(path)
            truncated.extend(p for p,_ in pending if p not in seen)
            break
        seen.add(path)
        if len(seen)%25==0:print(f"FTP_SCAN_PROGRESS directories={len(seen)} files={len(out)} elapsed_seconds={int(time.monotonic()-started)}",flush=True)
        try:
            ftp.cwd(path); rows=list(ftp.mlsd())
        except (ftplib.all_errors, OSError) as err:
            failures.append({"directory":path,"error_type":type(err).__name__});continue
        visible=[(n,f) for n,f in rows if n not in (".","..")]
        folder_records.append({"path":path,"entries":len(visible),
                               "file_entries":sum(f.get("type")=="file" for _,f in visible),
                               "directory_entries":sum(f.get("type")=="dir" for _,f in visible),
                               "hidden_entries":sum(n.startswith(".") for n,_ in visible),
                               "hidden_name_samples":[n for n,_ in visible if n.startswith(".")][:12]})
        for name,facts in rows:
            if name in (".","..") or "/" in name or "\\" in name or name.startswith("."):continue
            full=safe(path.rstrip("/")+"/"+name)
            kind=facts.get("type")
            if kind=="dir":
                if depth<max_depth: pending.append((full,depth+1))
                else: truncated.append(full)
            elif kind=="file":
                out.append({"path":full,"size":int(facts["size"]) if facts.get("size","").isdigit() else None,"modify":facts.get("modify")})
    if len(out)>max_files:truncated.append(ROOT+"/[file-count-limit]")
    return {"root":ROOT,"directories":len(seen),"folders":sorted(folder_records,key=lambda x:x["path"].casefold()),
            "files":sorted(out,key=lambda x:x["path"].casefold()),"failures":failures,"truncated":sorted(set(truncated))}
def basename_clean(s):
    return re.sub(r"\s+"," ",re.sub(r"[._]+"," ",s)).strip(" -")
def propose(inv):
    files=inv["files"]; changes=[]; review=[]
    known={x["path"].casefold() for x in files};destinations=set()
    for item in files:
        old=item["path"]; path=PurePosixPath(old); ext=path.suffix.lower()
        if ext not in VIDEO|SIDE:continue
        if item["size"] is None:
            review.append({"path":old,"reason":"Missing source size; cannot validate rename"});continue
        stem=path.stem; m=EP.search(stem)
        if not m:
            if ext in VIDEO:
                year=YEAR.search(stem)
                if year: review.append({"path":old,"reason":"Movie/year candidate needs title identification"})
                else: review.append({"path":old,"reason":"Unrecognized video naming; manual identification required"})
            continue
        prefix=basename_clean(stem[:m.start()]);season=int(m.group(1));episode=int(m.group(2))
        tail=stem[m.end():]
        if MULTI_EP.match(tail):
            review.append({"path":old,"reason":"Multi-episode file requires review"});continue
        if not prefix:
            for parent in list(path.parents)[:-1]:
                candidate=parent.name
                if candidate.lower().startswith(("season ", "series ", "s01", "s02", "s03")):continue
                if candidate.lower() in {"downloads","tv","television","movies","shows","complete","video"}:continue
                prefix=basename_clean(candidate);break
        if not prefix or prefix.casefold() in {"the","show","tv"} or season>60 or episode>400:
            review.append({"path":old,"reason":"Episode number/title uncertain"});continue
        if YEAR.search(prefix) and len(prefix)<6:continue
        label=f"S{season:02d}E{episode:02d}"
        suffix=tail
        lang=""
        if ext in SIDE:
            lm=LANGUAGE.fullmatch(suffix)
            if lm:
                lang="."+lm.group(1).lower()+(("."+lm.group(2).strip(" ._-").lower()) if lm.group(2) else "")
                suffix=""
        suffix=RELEASE.split(suffix,1)[0]
        suffix=basename_clean(suffix).strip(" -")
        # Preserve episode titles where plausible; avoid release-tag confusion.
        if suffix and re.search(r"(?i)\b(?:x264|x265|webrip|hdtv|bluray|1080p)\b",suffix):suffix=""
        canonical=f"{prefix} - {label}"+(f" - {suffix}" if suffix else "")+lang+ext
        # Keep directories unchanged in first pass. Series/franchise moves require verified mapping.
        dest=str(path.with_name(canonical))
        if dest==old:continue
        if dest.casefold() in known or dest.casefold() in destinations:
            review.append({"path":old,"proposed":dest,"reason":"Destination collision"});continue
        destinations.add(dest.casefold())
        changes.append({"from":old,"to":dest,"size":item["size"],"reason":"episode token normalization; candidate only"})
    return {"root":ROOT,"moves":changes,"review":review,"source_file_count":len(files),"failure_count":len(inv["failures"]),"truncated_count":len(inv.get("truncated",[])),"notice":"Candidates are not authorized for automatic execution without explicit approved plan."}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--mode",choices=("inventory","apply"),default="inventory")
    ap.add_argument("--plan",default="media-organizer/output/approved-plan.json")
    args=ap.parse_args();out=Path("media-organizer/output");out.mkdir(parents=True,exist_ok=True)
    with connect() as ftp:
        inv=scan(ftp); (out/"inventory.json").write_text(json.dumps(inv,indent=2,ensure_ascii=False))
        # Small shard files allow GitHub browsing without huge API responses.
        shards=out/"inventory-shards";shards.mkdir(exist_ok=True)
        for n in range(0,len(inv["files"]),150):
            (shards/f"files-{n//150+1:04d}.json").write_text(json.dumps(inv["files"][n:n+150],indent=2,ensure_ascii=False))
        plan=propose(inv); (out/"suggestions.json").write_text(json.dumps(plan,indent=2,ensure_ascii=False))
        # Filename-only grouping signals, no external metadata or speculative moves.
        groups={}
        for move in plan["moves"]:
            name=PurePosixPath(move["to"]).name.split(" - S",1)[0]
            node=groups.setdefault(name,{"series":name,"suggested_episode_renames":0,"samples":[]})
            node["suggested_episode_renames"]+=1
            if len(node["samples"])<3:node["samples"].append(move["from"])
        (out/"series-groups.json").write_text(json.dumps(sorted(groups.values(),key=lambda x:(-x["suggested_episode_renames"],x["series"])),indent=2,ensure_ascii=False))
        summary={"files":len(inv["files"]),"directories":inv["directories"],"rename_candidates":len(plan["moves"]),"review_queue":len(plan["review"]),"scan_errors":len(inv["failures"]),"truncated_dirs":len(inv["truncated"]),"empty_folders":sum(f["entries"]==0 for f in inv["folders"]),"folders_with_hidden_entries":sum(f["hidden_entries"]>0 for f in inv["folders"])}
        (out/"summary.json").write_text(json.dumps(summary,indent=2))
        print("MEDIA_INVENTORY_SUMMARY "+json.dumps(summary))
        if args.mode=="inventory":return
        if inv["failures"] or inv["truncated"]:raise SystemExit("Apply blocked: partial inventory")
        approved=json.loads(Path(args.plan).read_text())
        if approved.get("root")!=ROOT or not isinstance(approved.get("moves"),list):raise SystemExit("Invalid approved plan")
        filemap={x["path"]:x for x in inv["files"]}
        completed=[]
        proposed=propose(inv)
        # A committed plan is permitted to select a subset only from the current safe
        # suggestions. It cannot invent a path, rename a movie, or overwrite a file.
        allowed={(x["from"],x["to"],x["size"]) for x in proposed["moves"]}
        if len(approved["moves"])>500:raise SystemExit("Apply capped at 500 reviewed moves")
        ops=[]
        for move in approved["moves"]:
            entry=(move.get("from"),move.get("to"),move.get("size"))
            if entry not in allowed:raise SystemExit("Apply plan contains unrecognized or stale rename")
            ops.append(entry)
        if len(set(ops))!=len(ops):raise SystemExit("Duplicate operations in plan")
        try:
            for move in approved["moves"]:
                src=safe(move["from"]);dst=safe(move["to"])
                if src not in filemap or filemap[src]["size"]!=move["size"]:raise RuntimeError("Source changed or disappeared")
                if dst.casefold() in {p.casefold() for p in filemap}:raise RuntimeError("Destination exists")
                # Re-read the destination directory before every change. FTP RNTO can
                # overwrite an existing file on some servers if a new file arrived.
                parent=str(PurePosixPath(dst).parent);ftp.cwd(parent)
                if any(name.casefold()==PurePosixPath(dst).name.casefold() for name,_ in ftp.mlsd()):
                    raise RuntimeError("Destination appeared during execution")
                if PurePosixPath(src).parent!=PurePosixPath(dst).parent:raise RuntimeError("Cross-directory move requires separate review")
                if PurePosixPath(src).suffix.lower()!=PurePosixPath(dst).suffix.lower():raise RuntimeError("Extension mismatch")
                ftp.rename(src,dst);completed.append({"from":src,"to":dst,"size":move["size"]})
                filemap.pop(src);filemap[dst]={"path":dst,"size":move["size"]}
                (out/"completed.json").write_text(json.dumps(completed,indent=2))
        finally:
            (out/"completed.json").write_text(json.dumps(completed,indent=2))
if __name__=="__main__":main()
