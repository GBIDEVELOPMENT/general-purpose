#!/usr/bin/env python3
"""Bounded FTP debris cleanup with exact inventory-pinned delete manifests.

No wildcard remote deletion. Archive suggestions are never automatically approved.
"""
import argparse, ftplib, json, os, re

from pathlib import Path, PurePosixPath

OWNER_MEDIA_BATCH = 'owner_media_20261101_289'
OWNER_MEDIA_REVIEW = Path('media-organizer/review/ftp-selected-title-delete-2026-11-01.json')
OWNER_MEDIA_BYTES = 463387620682
TV_DEDUPE_BATCH = "owner_tv_dedupe_20261102_080"
TV_DEDUPE_REVIEW = Path("media-organizer/review/ftp-tv-dedupe-2026-11-02.json")
TV_DEDUPE_BYTES = 119912139016
GL_BATCH = 'owner_green_lantern_20261102_002'
GL_REVIEW = Path('media-organizer/review/ftp-green-lantern-duplicate-2026-11-02.json')
GL_BYTES = 367457686

from organize import ROOT, VIDEO, connect, safe

IMAGE={".jpg",".jpeg",".png",".webp",".bmp",".gif"}
ARCHIVE=re.compile(r"(?i)(?:\.rar|\.r\d\d|\.part\d+\.rar|\.7z|\.zip)$")
SCREEN_FOLDER={"screens","screenshots","screen shots","screen caps","screencaps"}
SCREEN_FILE=re.compile(r"(?i)^(?:screen(?:shot)?[\s._-]*\d+|mpv-shot\d+|vlcsnap[-\d]+|thumbs?[-_ ]?\d+|.+[ ._-]screenshots?)\.(?:png|jpe?g|webp)$")
# User-authorized release samples and trailers, never an ordinary episode.
RELEASE_CLIP=re.compile(r"(?i)^(?:sample|trailer|teaser|.+[ ._-](?:sample|trailer|teaser))$")
EPISODE_ID=re.compile(r"(?i)S\d{1,2}E\d{1,3}")
def category(path):
    p=PurePosixPath(path)
    if p.suffix.lower()==".nfo":return "nfo"
    if p.suffix.lower()==".txt":return "txt"
    # Small non-media torrent packaging crumbs. Binary payloads (.bin), game
    # installer files, ISO checksums and playlists are NOT treated as debris.
    if p.suffix.lower() in {".url",".lnk",".diz",".sfv",".log"}:return "detritus"
    if p.name.casefold()=="rarbg_do_not_mirror.exe":return "detritus"
    if p.name.casefold()=="__ia_thumb.jpg" or re.search(r"(?i)_meta\.(?:sqlite|xml)$",p.name):return "detritus"
    if p.suffix.lower()==".vob" and p.parent.name.casefold()=="sample" and re.search(r"(?i)[._ -]sample$",p.stem):return "sample"
    if p.suffix.lower() in VIDEO and not EPISODE_ID.search(p.name):
        clip_name=p.stem
        if RELEASE_CLIP.fullmatch(clip_name):
            return "sample" if clip_name.lower()=="sample" or re.search(r"(?i)[ ._-]sample$",clip_name) else "trailer"
    if p.suffix.lower() in IMAGE and (
            any(x.lower() in SCREEN_FOLDER for x in p.parts) or SCREEN_FILE.fullmatch(p.name)):
        return "screenshot"
    return None

def assess(inv):
    files=inv["files"]; clean=[]; archives=[]; reserved=[]
    bydir={}
    for f in files:
        d=str(PurePosixPath(f["path"]).parent)
        bydir.setdefault(d,[]).append(f)
    for f in files:
        p=f["path"]
        if category(p) and f.get("size") is not None:
            clean.append({"from":p,"size":f["size"],"modify":f.get("modify"),
                          "category":category(p)})
        elif ARCHIVE.search(p):
            d=str(PurePosixPath(p).parent)
            media=[x["path"] for x in bydir[d] if PurePosixPath(x["path"]).suffix.lower() in VIDEO and (x.get("size") or 0)>0]
            record={"from":p,"size":f.get("size"),"modify":f.get("modify"),
                    "extracted_video_in_same_directory":media[:8]}
            if media: archives.append(record)
            else: reserved.append(record)
    return {"root":ROOT,"nfo":sum(x["category"]=="nfo" for x in clean),
            "samples":sum(x["category"]=="sample" for x in clean),
            "trailers":sum(x["category"]=="trailer" for x in clean),
            "screenshots":sum(x["category"]=="screenshot" for x in clean),
            "debris_candidates":clean,"archive_review":archives,"archive_without_local_video":reserved,
            "important":"Archive candidates are NEVER auto-delete candidates; verify extracted content and archive relationship separately."}

def tv_keepers(manifest):
    """Entire 80-file exact authorized review plus protected retained counterparts."""
    if manifest["batch_id"]!=TV_DEDUPE_BATCH:return {}
    review=json.loads(TV_DEDUPE_REVIEW.read_text(encoding="utf-8"))
    source=review.get("source",{})
    totals=review.get("totals",{})
    if (review.get("schema")!="owner-tv-dedupe-2026-11-02-v1"
            or source.get("inventory_git_blob_sha")!="93695dc4ad24d8dbf57c6637679609a8ea85b445"
            or source.get("run_id")!=41379794306 or source.get("errors")!=0
            or source.get("truncated")!=0 or source.get("files")!=2598
            or totals.get("duplicate_episode_groups")!=80
            or totals.get("video_deletions")!=80 or totals.get("bytes")!=TV_DEDUPE_BYTES):
        raise ValueError("Unrecognized owner-selected TV duplicate review or source")
    groups=review.get("groups",[])
    if len(groups)!=80:raise ValueError("Expected exactly 80 approved episode groups")
    allow_shows={"Brooklyn Nine-Nine","Friends","History of the Sitcom",
                 "Mitchell and Webb Are Not Helping","Ted Lasso","The Other Bennet Sister"}
    expected=[];keep_by_loser={};seen=set();keepers=set()
    for group in groups:
        if group.get("show") not in allow_shows:raise ValueError("Unapproved series")
        episode=(group["show"],group["season"],group["episode"])
        if episode in seen:raise ValueError("Repeated episode")
        seen.add(episode)
        keeper=group["retain"]
        if len(group["delete"])!=1:raise ValueError("One loser per approved episode")
        for obj in [keeper]+group["delete"]:
            if set(obj)!={"from","size","modify","resolution"}:raise ValueError("Unexpected episode metadata fields")
            path=PurePosixPath(safe(obj["from"]))
            if path.suffix.lower() not in (".mkv",".mp4",".avi",".m4v"):raise ValueError("Unexpected media extension")
            matches=list(re.finditer(r"(?i)s(\d{1,2})[._ -]*e(\d{1,3})(?!\d)",path.name))
            if len(matches)!=1 or int(matches[0].group(1))!=group["season"] or int(matches[0].group(2))!=group["episode"]:
                raise ValueError("Cross-episode or multipart release")
            if (not isinstance(obj["size"],int) or isinstance(obj["size"],bool) or obj["size"]<=0
                    or not isinstance(obj["modify"],str) or not re.fullmatch(r"\d{14}",obj["modify"])
                    or obj["resolution"] not in (2160,1080,720,576,480)):
                raise ValueError("Invalid pinned source or resolution")
            # Retained resolution is reported by the reviewed title parser; confirm
            # its single nominal release tier before trusting the ordering.
            tiers={int(x) for x in re.findall(r"(?i)(2160|1080|720|576|480)p",obj["from"])}
            if tiers!={obj["resolution"]}:raise ValueError("Ambiguous filename resolution")
        loser=group["delete"][0]
        if loser["resolution"]>keeper["resolution"] or (loser["resolution"]==keeper["resolution"] and loser["size"]<keeper["size"]):
            raise ValueError("Loser would outrank keeper")
        if keeper["from"]==loser["from"] or loser["from"] in keep_by_loser or keeper["from"] in keepers:
            raise ValueError("Reused or identical TV episode path")
        keepers.add(keeper["from"]);keep_by_loser[loser["from"]]=keeper
        expected.append({"from":loser["from"],"size":loser["size"],"modify":loser["modify"],"category":"owner_tv_dedupe"})
    if keepers.intersection(keep_by_loser):raise ValueError("Cannot delete a keeper")
    if expected!=manifest["entries"] or sum(e["size"] for e in expected)!=TV_DEDUPE_BYTES:
        raise ValueError("Approved deletion differs from the exact 80 reviewed files")
    return keep_by_loser

def gl_keepers(manifest):
    """Two exact Green Lantern S01 episodes, with measured video dimensions."""
    if manifest["batch_id"] != GL_BATCH:return {}
    document=json.loads(GL_REVIEW.read_text(encoding="utf-8"))
    source=document.get("source",{})
    if (document.get("schema")!="owner-green-lantern-verified-2026-11-02-v1"
            or source.get("inventory_blob_sha")!="93695dc4ad24d8dbf57c6637679609a8ea85b445"
            or source.get("inventory_run")!=41379794306 or source.get("probe_run")!=41381393287
            or source.get("probe_artifact_id")!=13113212678 or source.get("probed_all_four") is not True
            or document.get("totals",{}).get("episodes")!=2
            or document.get("totals",{}).get("delete_files")!=2
            or document.get("totals",{}).get("bytes")!=GL_BYTES):
        raise ValueError("Unrecognized read-only stream metadata source or review")
    entries=[];keep_map={};seen=set()
    groups=document["groups"]
    if len(groups)!=2:raise ValueError("Expected exactly two observed duplicate episodes")
    expected_dimensions={3:((1920,1080),(624,352)),5:((1920,1080),(720,400))}
    for group in groups:
        ep=group["episode"]
        if group["show"]!="Green Lantern The Animated Series" or group["season"]!=1 or ep not in expected_dimensions or ep in seen:
            raise ValueError("Unapproved series/season/episode identity")
        seen.add(ep)
        if len(group["delete"])!=1:raise ValueError("Unexpected duplicate count")
        keeper=group["retain"];loser=group["delete"][0]
        for obj,expected_dims,extension in ((keeper,expected_dimensions[ep][0],".mkv"),(loser,expected_dimensions[ep][1],".avi")):
            if set(obj)!={"from","size","modify","width","height"}:raise ValueError("Unreviewed metadata fields")
            p=PurePosixPath(safe(obj["from"]))
            if p.suffix.lower()!=extension or (obj["width"],obj["height"])!=expected_dims:
                raise ValueError("Probe resolution or media class mismatch")
            matches=list(re.finditer(r"(?i)s(\d{2})e(\d{2})",p.name))
            if len(matches)!=1 or matches[0].group(1)!="01" or int(matches[0].group(2))!=ep:
                raise ValueError("Filename episode mismatch")
            if not isinstance(obj["size"],int) or obj["size"]<=0 or not isinstance(obj["modify"],str) or not re.fullmatch(r"\d{14}",obj["modify"]):
                raise ValueError("Invalid pinned FTP file facts")
        if not keeper["from"].startswith("/downloads/Green Lantern The Animated Series/Season 01/"):
            raise ValueError("Unapproved keeper directory")
        if not loser["from"].startswith("/downloads/Green Lantern The Animated Series S01/"):
            raise ValueError("Unapproved loser directory")
        keep_map[loser["from"]]=keeper
        entries.append({"from":loser["from"],"size":loser["size"],"modify":loser["modify"],"category":"owner_green_lantern"})
    if len(keep_map)!=2 or entries!=manifest["entries"] or sum(x["size"] for x in entries)!=GL_BYTES:
        raise ValueError("Cannot expand observed duplicate deletion set")
    return keep_map

def validate(manifest):
    if set(manifest)!={"root","batch_id","entries","description"} or manifest["root"]!=ROOT:
        raise ValueError("Invalid manifest envelope")
    if not isinstance(manifest["batch_id"],str) or not re.fullmatch("[a-zA-Z0-9_-]{5,48}",manifest["batch_id"]):
        raise ValueError("Invalid batch id")
    if not isinstance(manifest["description"],str) or len(manifest["description"])<15:raise ValueError("Missing rationale")
    entries=manifest["entries"]
    if not isinstance(entries,list) or not 1<=len(entries)<=300:raise ValueError("Batch must have 1..300 entries")
    if manifest["batch_id"] == GL_BATCH:
        gl_keepers(manifest)
    elif manifest["batch_id"] == TV_DEDUPE_BATCH:
        tv_keepers(manifest)
    elif manifest["batch_id"] == OWNER_MEDIA_BATCH:
        # The exception for full-sized media is restricted to the owner's one
        # signed-off review set. It does not relax ordinary debris validation.
        reviewed=json.loads(OWNER_MEDIA_REVIEW.read_text(encoding="utf-8"))
        if (reviewed.get("schema_version")!="review-only-2026-11-01-v1"
                or reviewed.get("snapshot",{}).get("inventory_blob_sha")!="079f857e4c717c2801b76c2132e5b8a996b62fe0"
                or reviewed.get("snapshot",{}).get("scan_failures")!=0
                or reviewed.get("snapshot",{}).get("scan_truncated")!=0
                or reviewed.get("totals",{}).get("files")!=289
                or reviewed.get("totals",{}).get("bytes")!=OWNER_MEDIA_BYTES):
            raise ValueError("Original owner-reviewed inventory/provenance mismatch")
        expected=[{"from":f["path"],"size":f["size_bytes"],"modify":f["modify_ftp"],"category":"owner_media"}
                  for group in reviewed["groups"] for f in group["files"]]
        if len(expected)!=289 or sum(f["size"] for f in expected)!=OWNER_MEDIA_BYTES or entries!=expected:
            raise ValueError("Approved media manifest differs from the exact 289 owner-reviewed paths")
        roots=[root for group in reviewed["groups"] for root in group["matched_roots"]]
        if any(not any(f["from"].startswith(root+"/") for root in roots) for f in expected):
            raise ValueError("Selected path outside approved release roots")
        if any("/rtorrent/" in f["from"] or "/watch/rtorrent/" in f["from"] or "/Night Court/" in f["from"] for f in expected):
            raise ValueError("Protected path in selected files")
    elif any(entry.get("category") in ("owner_media","owner_tv_dedupe","owner_green_lantern") for entry in entries if isinstance(entry,dict)):
        raise ValueError("Media exception requires exact owner-approved batch id")
    seen=set()
    for entry in entries:
        if not isinstance(entry,dict) or set(entry)!={"from","size","modify","category"}:raise ValueError("Unexpected entry keys")
        p=safe(entry["from"])
        if (manifest["batch_id"] == OWNER_MEDIA_BATCH and entry["category"] == "owner_media") or (manifest["batch_id"] == TV_DEDUPE_BATCH and entry["category"] == "owner_tv_dedupe") or (manifest["batch_id"] == GL_BATCH and entry["category"] == "owner_green_lantern"):
            pass  # Already matched the complete exact reviewed set above.
        elif category(p)!=entry["category"] or entry["category"] not in ("nfo","screenshot","sample","trailer","txt","detritus"):
            raise ValueError("Not an exact approved debris class")
        if p.casefold() in seen:raise ValueError("Duplicate delete")
        seen.add(p.casefold())
        if not isinstance(entry["size"],int) or isinstance(entry["size"],bool) or entry["size"]<0:raise ValueError("Invalid size")
        if entry["modify"] is not None and not re.fullmatch(r"\d{14}",entry["modify"]):raise ValueError("Invalid date")
    return entries
def lookup(ftp,path):
    p=PurePosixPath(path)
    try:ftp.cwd(str(p.parent))
    except ftplib.error_perm as err:
        if str(err).startswith("550"):return None
        raise
    matches=[facts for name,facts in ftp.mlsd() if name==p.name]
    if not matches:return None
    if len(matches)!=1:raise ValueError("Ambiguous exact FTP source")
    return matches[0]
def execute(ftp,manifest,audit_path):
    batch=validate(manifest)
    audit_path.parent.mkdir(parents=True,exist_ok=True)
    completed=[];skipped=[]
    def save(status):
        with audit_path.open("w") as f:
            json.dump({"batch_id":manifest["batch_id"],"status":status,"completed":completed,"skipped":skipped},f,indent=2)
            f.flush();os.fsync(f.fileno())
    keepers=tv_keepers(manifest) if manifest["batch_id"]==TV_DEDUPE_BATCH else gl_keepers(manifest) if manifest["batch_id"]==GL_BATCH else {}
    for keeper in keepers.values():
        facts=lookup(ftp,keeper["from"])
        if (facts is None or facts.get("type")!="file" or
                str(facts.get("size"))!=str(keeper["size"]) or facts.get("modify")!=keeper["modify"]):
            raise ValueError("Retained episode missing or changed, refusing all removals")
    active=[]
    for item in batch:
        facts=lookup(ftp,item["from"])
        if facts is None:
            skipped.append({"from":item["from"],"reason":"already absent"})
            continue
        if facts.get("type")!="file" or str(facts.get("size"))!=str(item["size"]) or (item["modify"] and facts.get("modify")!=item["modify"]):
            raise ValueError("Preflight refused changed file")
        active.append(item)
    save("preflight_passed")
    try:
        for item in active:
            if keepers:
                keeper=keepers[item["from"]]
                kfacts=lookup(ftp,keeper["from"])
                if (kfacts is None or kfacts.get("type")!="file" or
                        str(kfacts.get("size"))!=str(keeper["size"]) or kfacts.get("modify")!=keeper["modify"]):
                    raise ValueError("Retained episode no longer exact; stop deletions")
            facts=lookup(ftp,item["from"])
            if facts.get("type")!="file" or str(facts.get("size"))!=str(item["size"]) or (item["modify"] and facts.get("modify")!=item["modify"]):
                raise ValueError("Changed between preflight and deletion")
            ftp.delete(item["from"])
            completed.append(item)
            save("in_progress")
    finally:save("complete_with_skips" if len(completed)==len(active) and skipped else
                 "complete" if len(completed)==len(batch) else "partial")
def main():
    p=argparse.ArgumentParser();p.add_argument("--inventory");p.add_argument("--report");p.add_argument("--manifest");p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    if a.inventory:
        report=assess(json.loads(Path(a.inventory).read_text()))
        Path(a.report).write_text(json.dumps(report,indent=2,ensure_ascii=False))
        print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in report.items() if k!="important"}))
    if a.manifest:
        m=json.loads(Path(a.manifest).read_text());validate(m)
        if a.apply:
            with connect() as ftp:execute(ftp,m,Path("media-organizer/delete-output/completed.json"))
if __name__=="__main__":main()
