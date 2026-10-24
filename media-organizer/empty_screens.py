#!/usr/bin/env python3
"""Remove explicitly listed empty screenshot folders, without recursive deletion."""
import argparse,json,re
from pathlib import Path,PurePosixPath
from organize import ROOT,connect,safe
SCREEN={"screens","screenshots","screen shots","screen caps","screencaps"}
def validate(plan):
    if set(plan)!={"root","batch_id","directories","description"} or plan["root"]!=ROOT:raise ValueError("Invalid plan")
    if not re.fullmatch("[A-Za-z0-9_-]{5,48}",plan["batch_id"]):raise ValueError("Invalid ID")
    if not isinstance(plan["description"],str) or len(plan["description"])<12:raise ValueError("No description")
    folders=plan["directories"]
    if not isinstance(folders,list) or not 1<=len(folders)<=150:raise ValueError("Limit 150")
    seen=set()
    for p in folders:
        safe(p)
        pp=PurePosixPath(p)
        if pp.name.casefold() not in SCREEN or len(pp.parts)<4:raise ValueError("Not a screenshot directory")
        if p.casefold() in seen:raise ValueError("Duplicate")
        seen.add(p.casefold())
    return folders
def execute(ftp,plan,audit):
    folders=validate(plan);audit.parent.mkdir(parents=True,exist_ok=True);done=[];skipped=[]
    def save(status):
        audit.write_text(json.dumps({"status":status,"batch_id":plan["batch_id"],"removed":done,"not_empty_or_changed":skipped},indent=2))
    try:
        for d in folders:
            parent=str(PurePosixPath(d).parent)
            ftp.cwd(parent)
            listing=list(ftp.mlsd())
            name=PurePosixPath(d).name
            if len([n for n,_ in listing if n.casefold()==name.casefold()])!=1:
                skipped.append({"path":d,"reason":"case-conflict or missing"});save("partial");continue
            try:
                ftp.cwd(d)
                entries=[n for n,_ in ftp.mlsd() if n not in (".","..")]
                if entries:
                    skipped.append({"path":d,"reason":"still contains files or directories"});save("partial");continue
                ftp.cwd(ROOT)
                ftp.rmd(d)
                done.append(d)
                save("partial")
            except Exception:
                skipped.append({"path":d,"reason":"FTP refused empty-dir removal"})
                save("partial")
    finally:save("complete")
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--plan",default="media-organizer/approved-empty-screens.json");ap.add_argument("--apply",action="store_true")
    a=ap.parse_args();plan=json.loads(Path(a.plan).read_text());folders=validate(plan)
    print("Validated",len(folders),"explicit screenshot folders")
    if a.apply:
        with connect() as ftp:execute(ftp,plan,Path("media-organizer/screens-folder-output/completed.json"))
if __name__=="__main__":main()
