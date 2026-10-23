#!/usr/bin/env python3
"""Read-only FTP video *filename and size* inventory for original Night Court.

No media bytes transferred, decrypted, watched, transcribed or committed.
Requires the existing FTP_PASSWORD Actions secret. User-specified source root.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from pathlib import PurePosixPath
import json,os,re,ftplib
from ftp_research_intake import connect,clean_path,list_here,is_night_court_dir

VIDEO={".mkv",".mp4",".avi",".m4v",".mov",".wmv",".ts",".mpg",".mpeg"}
SEASON_COUNTS=[13,22,22,22,22,22,24,24,22]
PATTERN=re.compile(r"(?i)(?:^|[^a-z0-9])s(?:eason)?[\s._-]*0?([1-9])[\s._-]*e(?:p(?:isode)?)?[\s._-]*0?([0-9]{1,2})(?:[^0-9]|$)")
MAX_DIRECTORIES=28
MAX_VIDEO_ROWS=350

def scan(ftp,root):
    root=clean_path(root)
    if not any(is_night_court_dir(part) for part in PurePosixPath(root).parts):
        raise ValueError("Root must contain a Night Court directory component")
    queue=[root];visited=set();found=[];errors=[]
    while queue and len(visited)<MAX_DIRECTORIES:
        current=queue.pop(0)
        if current in visited:continue
        visited.add(current)
        try:listing=list_here(ftp,current)
        except (ftplib.error_perm,ValueError) as exc:
            errors.append({"directory":current,"error_class":type(exc).__name__})
            continue
        for name,facts in listing:
            if name in (".","..") or "/" in name or "\\" in name:continue
            child=clean_path(current.rstrip("/")+"/"+name)
            if facts.get("type")=="dir":
                if len(queue)+len(visited)<MAX_DIRECTORIES:
                    queue.append(child)
                continue
            if PurePosixPath(name).suffix.casefold() not in VIDEO:continue
            if "2023" in name or "reboot" in name.lower():continue
            match=PATTERN.search(name)
            epid=None
            if match:
                season,number=int(match.group(1)),int(match.group(2))
                if 1<=season<=9 and 1<=number<=SEASON_COUNTS[season-1]:
                    epid=f"S{season:02d}E{number:02d}"
            count=facts.get("size")
            if count is None:
                try:count=ftp.size(child)
                except ftplib.all_errors:count=None
            found.append({"remote_path":child,
                          "basename":name,
                          "size_bytes":int(count) if count is not None and str(count).isdigit() else None,
                          "episode_id_from_filename":epid,
                          "identity_status":"filename_candidate_not_video_verified" if epid else "episode_id_not_resolved"})
            if len(found)>MAX_VIDEO_ROWS:raise ValueError("Video listing exceeds 350 file safety bound")
    byseason=Counter(x["episode_id_from_filename"][:3] for x in found if x["episode_id_from_filename"])
    distinct={x["episode_id_from_filename"] for x in found if x["episode_id_from_filename"]}
    return {"series":"night-court-1984","source_host":"wood.seedhost.eu","source_root":root,
            "mode":"metadata_only_never_downloads_video",
            "directories_visited":len(visited),"directory_cap":MAX_DIRECTORIES,
            "cap_reached":bool(queue),"media_file_count":len(found),
            "unique_episode_ids_in_filenames":len(distinct),
            "season_file_counts":dict(sorted(byseason.items())),
            "unmatched_video_files":sum(x["episode_id_from_filename"] is None for x in found),
            "errors":errors,"files":found,
            "warning":"Filenames do not establish 1984 original-series identity or edition; source subtitles are separate; no video bytes downloaded."}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root",default="/downloads/Night Court TVRip S1-S9")
    ap.add_argument("--protocol",choices=["ftp","ftps"],default="ftp")
    args=ap.parse_args()
    ftp=connect(os.environ.get("FTP_HOST","wood.seedhost.eu"),
                os.environ.get("FTP_USER","ianseeds"),
                os.environ.get("FTP_PASSWORD",""),args.protocol)
    try:
        result=scan(ftp,args.root)
    finally:
        try:ftp.quit()
        except ftplib.all_errors:ftp.close()
    # This report contains only media filenames and sizes, never credentials or contents.
    print("NIGHT_COURT_MEDIA_METADATA_JSON")
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
