#!/usr/bin/env python3
"""Remove one exact RAR volume set only when the extracted video is verified."""
import argparse, json, os, re
from pathlib import Path, PurePosixPath
from organize import connect, ROOT, safe

RAR_EXT=re.compile(r"(?i)\.(?:rar|r\d{2,3})$")
MAX_PARTS=110
def check(manifest):
    if set(manifest)!={"root","batch_id","description","video","volumes"} or manifest["root"]!=ROOT:
        raise ValueError("Unexpected archive approval structure")
    if not re.fullmatch("[A-Za-z0-9_-]{5,48}",manifest["batch_id"]):raise ValueError("Invalid batch id")
    if len(manifest["description"])<20:raise ValueError("Missing justification")
    vid=manifest["video"]
    if set(vid)!={"path","size","modify"}:raise ValueError("Bad video provenance")
    safe(vid["path"])
    suffix=PurePosixPath(vid["path"]).suffix.lower()
    if suffix not in (".mkv",".mp4",".avi",".m4v",".iso"):
        raise ValueError("Extracted TV video or DVD image not recognized")
    if suffix==".iso":
        # DVD disc ISO is an extracted media image, not a game-install ISO.
        # Demand exact same-stem RAR volumes and TV SxxDxx disc identity.
        directory=str(PurePosixPath(vid["path"]).parent)
        if (not re.search(r"(?i)S\d{2}D\d{2}",directory)
                or not re.search(r"(?i)S\d{2}D\d{2}",PurePosixPath(vid["path"]).name)):
            raise ValueError("Only TV DVD disc ISO images supported")
    if not isinstance(vid["size"],int) or vid["size"]<50000000:raise ValueError("Video too small")
    vols=manifest["volumes"]
    if not isinstance(vols,list) or not 2<=len(vols)<=MAX_PARTS:raise ValueError("Archive set must be bounded")
    seen=set()
    for item in vols:
        if set(item)!={"path","size","modify"}:raise ValueError("Bad volume metadata")
        safe(item["path"])
        p=PurePosixPath(item["path"])
        if str(p.parent)!=str(PurePosixPath(vid["path"]).parent):raise ValueError("Not co-located")
        if not RAR_EXT.search(p.name):raise ValueError("Not RAR volume")
        if p.name.lower() in seen:raise ValueError("Duplicate")
        seen.add(p.name.lower())
        if not isinstance(item["size"],int) or item["size"]<100:raise ValueError("Invalid volume size")
    if len({re.sub(r"(?i)\.(?:rar|r\d{2,3})$","",PurePosixPath(x["path"]).name).casefold() for x in vols})!=1:
        raise ValueError("Multiple unrelated archive stems")
    stem=re.sub(r"(?i)\.(?:rar|r\d{2,3})$","",PurePosixPath(vols[0]["path"]).name).casefold()
    if PurePosixPath(vid["path"]).stem.casefold()!=stem:
        raise ValueError("Extracted video name and RAR volume stem differ")
    for item in [vid]+vols:
        if not isinstance(item["modify"],str) or not re.fullmatch(r"\d{14}",item["modify"]):
            raise ValueError("Precise FTP MLSD modified date required for deletion")
    names=[PurePosixPath(x["path"]).suffix.lower() for x in vols]
    if ".rar" not in names:raise ValueError("First .rar volume missing")
    indices=sorted(int(n[2:]) for n in names if re.fullmatch(r"\.r\d{2,3}",n))
    if indices!=list(range(len(indices))):raise ValueError("Volume sequence incomplete")
    total=sum(x["size"] for x in vols)
    delta=total-vid["size"]
    if not 0<=delta<=1024*1024:raise ValueError("Archive sum not consistent with extracted video")
    return total
def listing(ftp,where):
    ftp.cwd(where)
    rows=list(ftp.mlsd())
    names={}
    for name,facts in rows:names.setdefault(name.casefold(),[]).append((name,facts))
    return names
def live(ftp,manifest):
    where=str(PurePosixPath(manifest["video"]["path"]).parent)
    rows=listing(ftp,where)
    def verify(obj):
        name=PurePosixPath(obj["path"]).name
        matches=rows.get(name.casefold(),[])
        if len(matches)!=1 or matches[0][0]!=name:raise ValueError("Missing or case-conflicted source")
        facts=matches[0][1]
        if facts.get("type")!="file" or str(facts.get("size"))!=str(obj["size"]) or (obj["modify"] and facts.get("modify")!=obj["modify"]):
            raise ValueError("Source size/date/type changed")
    verify(manifest["video"])
    for entry in manifest["volumes"]:verify(entry)
    # No additional unapproved archive volume can exist in this source directory.
    approved={PurePosixPath(v["path"]).name.casefold() for v in manifest["volumes"]}
    stem=re.sub(r"(?i)\.(?:rar|r\d{2,3})$","",PurePosixPath(manifest["volumes"][0]["path"]).name).casefold()
    for name,fs in rows.items():
        if re.sub(r"(?i)\.(?:rar|r\d{2,3})$","",name)==stem and RAR_EXT.search(name) and name not in approved:
            raise ValueError("Archive volume absent from approved manifest")
def execute(ftp,manifest,path):
    check(manifest)
    path.parent.mkdir(parents=True,exist_ok=True);completed=[]
    def save(state):
        with path.open("w") as output:
            json.dump({"batch_id":manifest["batch_id"],"status":state,"completed":completed},output,indent=2)
            output.flush();os.fsync(output.fileno())
    live(ftp,manifest);save("preflight_passed")
    try:
        for item in manifest["volumes"]:
            # Verify the extracted video and all as-yet-unremoved volumes every time;
            # the full-set guard applies only to the initial preflight.
            rows=listing(ftp,str(PurePosixPath(item["path"]).parent))
            movie=manifest["video"]
            name=PurePosixPath(movie["path"]).name
            actual=rows.get(name.casefold(),[])
            if len(actual)!=1 or actual[0][0]!=name or str(actual[0][1].get("size"))!=str(movie["size"]):
                raise ValueError("Extracted video disappeared or changed")
            name=PurePosixPath(item["path"]).name
            actual=rows.get(name.casefold(),[])
            if len(actual)!=1 or actual[0][0]!=name or str(actual[0][1].get("size"))!=str(item["size"]) or (item["modify"] and actual[0][1].get("modify")!=item["modify"]):
                raise ValueError("Volume modified before deletion")
            ftp.delete(item["path"]);completed.append(item["path"]);save("partial")
    finally:save("complete" if len(completed)==len(manifest["volumes"]) else "partial")
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--manifest",default="media-organizer/approved-archive-delete.json");ap.add_argument("--apply",action="store_true")
    args=ap.parse_args();document=json.loads(Path(args.manifest).read_text())
    if "groups" in document:
        if set(document)!={"root","batch_id","description","groups"} or document["root"]!=ROOT:
            raise ValueError("Invalid archive group batch")
        groups=document["groups"]
        if not isinstance(groups,list) or not 1<=len(groups)<=25:
            raise ValueError("Only 1..25 exact reviewed archive groups")
        paths=set()
        for group in groups:
            check(group)
            key=str(PurePosixPath(group["video"]["path"]).parent).casefold()
            if key in paths:raise ValueError("Duplicate archive directory")
            paths.add(key)
        total=sum(len(g["volumes"]) for g in groups)
        if total>850:raise ValueError("Too many archive volumes in one batch")
        print("Validated archive group batch",document["batch_id"],len(groups),"sets",total,"volumes",flush=True)
    else:
        check(document);groups=[document]
        print("Validated extracted RAR set",document["batch_id"],len(document["volumes"]),"volumes",flush=True)
    if args.apply:
        with connect() as ftp:
            # Verify every group's extraction evidence before deleting any volumes.
            for group in groups:live(ftp,group)
            for i,group in enumerate(groups):
                print("Deleting approved archive group",i+1,"of",len(groups),group["batch_id"],flush=True)
                execute(ftp,group,Path("media-organizer/archive-delete-output")/f"group-{i+1:03d}.json")
if __name__=="__main__":main()
