#!/usr/bin/env python3
"""Read-only triage for risky mixed-library Plex paths. Never guesses file content."""
from __future__ import annotations
import argparse, json, re
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

ROOT="/downloads"
VIDEO={".mkv",".mp4",".avi",".m4v",".mov",".wmv",".ts",".mpg",".mpeg"}
STANDARD=re.compile(r"(?i)(?<![a-z0-9])S(\\d{1,2})[ ._-]*E(\\d{1,3})(?!\\d)")
LEGACY=re.compile(r"(?i)(?<![a-z0-9])(\\d{1,2})x(\\d{2,3})(?!\\d)")
CROSS=re.compile(r"(?i)S\\d{1,2}E\\d{1,3}S\\d{1,2}E\\d{1,3}")
MULTIPART=re.compile(r"(?i)S\\d{1,2}E\\d{1,3}(?:[ ._-]*E\\d{1,3})(?!\\d)")
DISC=re.compile(r"(?i)S\\d{1,2}D\\d{1,2}")
YEAR=re.compile(r"(?<!\\d)(?:19|20)\\d{2}(?!\\d)")
RELEASE=re.compile(r"(?i)(?:1080p|2160p|720p|480p|x26[45]|H[ ._-]*26[45]|HEVC|WEB[ ._-]*DL|WEBRip|BluRay|DVDRip|HDR|DDP\\d)")
SEASON_DIR=re.compile(r"(?i)^(?:Season[ ._-]*|S)(\\d{1,2})$")
SAMPLE=re.compile(r"(?i)^(?:sample|proof|screenshots?|preview)(?:[ ._-]|\\.)")
MISMATCH_YEAR=re.compile(r"(?i)S\\d{1,2}E\\d{1,3}[ ._-]+(?:19|20)\\d{2}(?:[ ._-]|$)")
PRIORITY={"high":0,"medium":1,"review":2,"info":3}

def scan_inventory(inventory):
    if inventory.get("root")!=ROOT or not isinstance(inventory.get("files"),list):
        raise ValueError("Expected FTP /downloads inventory")
    issues=[]
    def add(severity,category,file,note,suggestion=None):
        row={"severity":severity,"category":category,"path":file,"note":note}
        if suggestion:row["suggestion"]=suggestion
        issues.append(row)
    rows=[f for f in inventory["files"] if PurePosixPath(f["path"]).suffix.lower() in VIDEO]
    for obj in rows:
        path=obj["path"]
        p=PurePosixPath(path);stem=p.stem;parent=p.parent.name
        standard=STANDARD.search(stem);legacy=LEGACY.search(stem)
        if legacy and not standard:
            season=int(legacy.group(1));episode=int(legacy.group(2))
            add("high","legacy_1x_episode",path,"TV episode code uses 1x01 instead of S01E01",
                "Rename to S%02dE%02d with verified show/year, keep alternate releases distinct"%(season,episode))
        if CROSS.search(stem):
            add("high","cross_season_episode",path,"File spans two seasons; do not lose second episode code",
                "Preserve unchanged pending manual Plex mapping or lossless split")
        elif MULTIPART.search(stem):
            add("review","multiple_episodes",path,"File contains more than one episode",
                "Preserve every episode number, e.g. S01E01-E02")
        if DISC.search(stem) and not standard:
            add("high","disc_not_episode",path,"Season/disc marker S01D01 is not S01E01",
                "Determine whether this is a DVD image, episode or disc before naming")
        if SAMPLE.search(stem) or parent.casefold() in {"sample","samples","proof","screens","screenshots"}:
            add("high","sample_or_proof_video",path,"Non-feature media can be falsely matched as a film or episode",
                "Quarantine sample/proof as extras where appropriate; never assume full feature")
        if standard:
            season=int(standard.group(1))
            if season>60 or int(standard.group(2))>400:
                add("high","implausible_episode",path,"Season or episode number outside normal range")
            direct=SEASON_DIR.fullmatch(parent)
            if direct and int(direct.group(1))!=season:
                add("high","season_folder_mismatch",path,"Season folder disagrees with episode filename")
            if MISMATCH_YEAR.search(stem):
                add("medium","year_after_episode_code",path,
                    "Year after episode marker may be an airing/release year, not show premiere year",
                    "Move show premiere year before SxxEyy only after confirming show identity")
            prefix=stem[:standard.start()].strip(" ._-")
            if not prefix:
                add("medium","series_missing_from_basename",path,
                    "Episode file omits show title; depends on correct parent show/season folders")
            elif RELEASE.search(prefix):
                add("review","release_tokens_in_series_prefix",path,
                    "Codec/resolution/source token occurs before episode marker; may obscure show title")
        elif not legacy:
            if SEASON_DIR.fullmatch(parent) or re.search(r"(?i)S\\d{1,2}(?:[ ._-]|$)",parent):
                add("medium","episode_unrecognized_in_season",path,
                    "TV season container but media name lacks standard SxxEyy identification")
            elif not YEAR.search(stem) and YEAR.search(parent):
                add("medium","movie_year_only_in_folder",path,
                    "Likely film lacks title/year in its own basename; review with Plex film rules")
        if re.search(r"(?i)(?:S\\d{2}E\\d{2})[ ._-]+(?:H[ ._-]?26[45]|x[ ._-]?26[45])",stem):
            add("info","codec_immediately_after_episode",path,
                "Codec label follows episode number; normal release tag, not independently verified metadata")
    issues.sort(key=lambda row:(PRIORITY[row["severity"]],row["category"],row["path"].casefold()))
    summary=dict(Counter(x["category"] for x in issues))
    priority=dict(Counter(x["severity"] for x in issues))
    return {"root":ROOT,"inventory_files":len(inventory["files"]),"video_files":len(rows),
            "inventory_complete":not inventory.get("truncated") and not inventory.get("failures"),
            "truncated":inventory.get("truncated",[]),"scan_failures":inventory.get("failures",[]),
            "summary":summary,"priorities":priority,"issues":issues}

def markdown(report,limit=12):
    chunks=["# Plex filename risk audit","",
        "Read-only filename heuristics. A flagged file is **not proven mislabeled**;",
        "verify title, episode identity and codec with authoritative media data before moving.",
        "No files were moved or deleted by this audit.","",
        "Inventory fully covered: **%s**."%("yes" if report["inventory_complete"] else "no; scan was truncated or failed"),
        "Videos examined: **%s**."%report["video_files"],"",
        "## Counts by category",""]
    for category,count in sorted(report["summary"].items(),key=lambda x:(-x[1],x[0])):
        chunks.append("- **%s**: %d"%(category,count))
    chunks+=["","## Highest-risk examples",""]
    for issue in report["issues"][:limit]:
        chunks.append("- **%s / %s**: \\%s\\  %s"%(issue["severity"],issue["category"],issue["path"],issue["note"]))
    chunks+=["","## Known constraints","",
        "- This library deliberately mixes movies and TV shows at /downloads, which Plex warns may cause mismatching.",
        "- Codec strings in filenames are claims by uploaders; they do not establish actual stream codec or resolution.",
        "- Multi-edition episodes and subtitles require coordinated moves, never deduplication by episode code.",
        "- No recommendation here authorizes automatic deletion or renaming.",
        ""]
    return "\n".join(chunks)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--inventory",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--markdown")
    args=ap.parse_args()
    inv=json.loads(Path(args.inventory).read_text(encoding="utf-8"))
    report=scan_inventory(inv)
    dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if args.markdown:
        target=Path(args.markdown);target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(markdown(report)+"\n",encoding="utf-8")
    print("PLEX_FILENAME_AUDIT",json.dumps({"videos":report["video_files"],
          "complete":report["inventory_complete"],"summary":report["summary"]},sort_keys=True))
if __name__=="__main__":main()
