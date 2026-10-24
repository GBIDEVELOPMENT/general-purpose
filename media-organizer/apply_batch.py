#!/usr/bin/env python3
"""Apply a bounded, explicitly committed owner-reviewed FTP move batch.

The workflow must run only on trusted main after an approved-batch.json PR merge.
There are no deletes, overwrites, local media downloads, or remote shell calls.
"""
from __future__ import annotations
import argparse, ftplib, json, os, re
from pathlib import Path, PurePosixPath
from organize import ROOT, VIDEO, SIDE, connect, safe

MAX_BATCH=80
# Non-executable media artwork and text annotations can accompany verified editions.
# All moves remain exact-source, size/mtime pinned and destination collision guarded.
MEDIA=VIDEO|SIDE|{".jpg",".jpeg",".png",".txt"}
EPISODE=re.compile(r"(?i)S(\d{1,2})E(\d{1,3})")
EXTRA_EPISODE=re.compile(r"(?i)^[ ._-]*E(\d{1,3})(?!\d)")
def parse_episode_identity(filename):
    """Return every represented episode, including E02 suffixes and cross-season spans.

    Recognition is conservative. A video carrying an ambiguous cross-season
    episode span must be routed for special handling instead of renamed.
    """
    stem=PurePosixPath(filename).stem
    spans=list(EPISODE.finditer(stem))
    identity=set()
    for match in spans:
        season=int(match.group(1))
        identity.add((season,int(match.group(2))))
        suffix=stem[match.end():]
        while True:
            extra=EXTRA_EPISODE.match(suffix)
            if not extra:break
            identity.add((season,int(extra.group(1))))
            suffix=suffix[extra.end():]
    return identity
def validation_error(s):raise ValueError(s)
def plan_validate(plan):
    if set(plan)!= {"root","batch_id","moves","description"}:
        validation_error("Plan requires exact root, batch_id, moves, description keys")
    if plan["root"]!=ROOT:validation_error("Only /downloads is allowed")
    if not isinstance(plan["batch_id"],str) or not re.fullmatch("[a-zA-Z0-9_-]{5,50}",plan["batch_id"]):
        validation_error("Invalid batch ID")
    if not isinstance(plan["description"],str) or len(plan["description"])<15:
        validation_error("Explain purpose of batch")
    if not isinstance(plan["moves"],list) or not 1<=len(plan["moves"])<=MAX_BATCH:
        validation_error("Expected 1..80 explicit moves")
    sources=set();targets=set();ops=[]
    for item in plan["moves"]:
        if not isinstance(item,dict) or set(item)!={"from","to","size","modify","reason"}:
            validation_error("Each move requires exact source, destination, size, modify and reason")
        src=safe(item["from"]);dst=safe(item["to"])
        if src==dst:validation_error("Source equals destination")
        if not isinstance(item["size"],int) or isinstance(item["size"],bool) or item["size"]<0:
            validation_error("Reliable numeric size required")
        if item["modify"] is not None and (not isinstance(item["modify"],str) or not re.fullmatch(r"\d{14}",item["modify"])):
            validation_error("Invalid MLSD modify stamp")
        if not isinstance(item["reason"],str) or len(item["reason"])<8:
            validation_error("Each move needs documented reason")
        a=PurePosixPath(src);b=PurePosixPath(dst)
        if a.suffix.casefold()!=b.suffix.casefold() or a.suffix.lower() not in MEDIA:
            validation_error("No content or extension changes")
        if any(x.startswith(".") for x in b.parts if x not in ("/",)):
            validation_error("Hidden directories or names forbidden")
        if len(b.name)>220 or len(str(b))>700:
            validation_error("Destination path too long")
        if src.casefold() in sources or dst.casefold() in targets:
            validation_error("Duplicate source or destination")
        sources.add(src.casefold());targets.add(dst.casefold())
        # Content grouping, not arbitrary relabeling: recognizable TV filenames
        # must continue to contain an episode identifier after relocation.
        source_episodes=parse_episode_identity(a.name)
        target_episodes=parse_episode_identity(b.name)
        if len({s for s,_ in source_episodes})>1:
            validation_error("Cross-season episode pack requires manual Plex mapping")
        if source_episodes and source_episodes!=target_episodes:
            validation_error("Cannot discard, change or invent episode identity")
        ops.append(item)
    if sources & targets:
        validation_error("Multi-stage chains/cycles not allowed in one batch")
    return ops

def entries(ftp,directory):
    ftp.cwd(directory)
    result={}
    for name,facts in ftp.mlsd():
        result.setdefault(name.casefold(),[]).append((name,facts))
    return result
def exact_entry(ftp,directory,name):
    matches=entries(ftp,directory).get(name.casefold(),[])
    if not matches:return None
    if len(matches)!=1 or matches[0][0]!=name:
        validation_error("Ambiguous or case-colliding FTP path")
    return matches[0][1]
def stat_existing(ftp,path):
    p=PurePosixPath(path)
    return exact_entry(ftp,str(p.parent),p.name)
def ensure_folder(ftp,path):
    current=ROOT
    for part in PurePosixPath(path).parts[2:]:
        if part.startswith("."):validation_error("Hidden target directory")
        existing=exact_entry(ftp,current,part)
        child=current.rstrip("/")+"/"+part
        if existing:
            if existing.get("type")!="dir":validation_error("Target parent not an ordinary directory")
        else:
            ftp.mkd(child)
        current=child
def audit_write(path,entries_data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8") as output:
        json.dump(entries_data,output,indent=2,ensure_ascii=False)
        output.flush();os.fsync(output.fileno())
def execute(ftp,plan,audit_file):
    ops=plan_validate(plan);completed=[]
    # Preflight all source entries BEFORE performing any change. The server can
    # still change afterwards, so every rename rechecks both ends.
    for x in ops:
        source=stat_existing(ftp,x["from"])
        if not source or source.get("type")!="file":
            validation_error("Source missing or not a regular file: "+x["from"])
        if str(source.get("size",""))!=str(x["size"]):
            validation_error("Source size changed: "+x["from"])
        if x["modify"] and source.get("modify")!=x["modify"]:
            validation_error("Source modification time changed: "+x["from"])
    audit_write(audit_file,{"batch_id":plan["batch_id"],"completed":[],"status":"preflight_passed"})
    try:
        for x in ops:
            destination=PurePosixPath(x["to"])
            ensure_folder(ftp,str(destination.parent))
            state=stat_existing(ftp,x["from"])
            if not state or str(state.get("size"))!=str(x["size"]):
                validation_error("Source changed before move: "+x["from"])
            if x["modify"] and state.get("modify")!=x["modify"]:
                validation_error("Source timestamp changed before move: "+x["from"])
            if stat_existing(ftp,x["to"]) is not None:
                validation_error("Destination occupied: "+x["to"])
            ftp.rename(x["from"],x["to"])
            # Record the remote ACK before another network operation. If the
            # verification request fails, evidence retains the uncertain move
            # rather than inviting the next run to replay it.
            completed.append({**x,"destination_verified":False})
            audit_write(audit_file,{"batch_id":plan["batch_id"],"completed":completed,"status":"in_progress"})
            after=stat_existing(ftp,x["to"])
            if not after or after.get("type")!="file" or str(after.get("size"))!=str(x["size"]):
                raise RuntimeError("Post-rename verification failed; preserve journal for manual review")
            completed[-1]["destination_verified"]=True
            audit_write(audit_file,{"batch_id":plan["batch_id"],"completed":completed,"status":"in_progress"})
    finally:
        all_verified=(len(completed)==len(ops) and all(m.get("destination_verified") for m in completed))
        audit_write(audit_file,{"batch_id":plan["batch_id"],"completed":completed,
                               "status":"complete" if all_verified else "partial_or_failed"})
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--plan",default="media-organizer/approved-batch.json")
    ap.add_argument("--audit",default="media-organizer/apply-output/completed.json")
    ap.add_argument("--validate-only",action="store_true")
    args=ap.parse_args()
    plan=json.loads(Path(args.plan).read_text(encoding="utf-8"))
    ops=plan_validate(plan)
    print(f"Validated {len(ops)} reviewed moves in batch {plan['batch_id']}")
    if args.validate_only:return
    with connect() as ftp:execute(ftp,plan,Path(args.audit))
if __name__=="__main__":main()
