#!/usr/bin/env python3
"""Manual S01E01-only FTP video acquisition to ephemeral runner memory/disk.

Never stores source AVI, decoded audio, or credentials in Git or an artifact.
Reads the exact 193-item inventory's S01E01 path and size, not caller input.
No recursive lookup and no website interaction. Intended for manual Actions.
"""
import argparse, ftplib, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
from ftp_research_intake import connect
from run_s01e01_vocal_pilot import main as run_local_pilot

ROOT=Path(__file__).resolve().parents[1]
LIMIT=210_000_000
ID="S01E01"

def candidate():
    inv=json.loads((ROOT/"catalog/ftp-video-inventory-2026-10-23.json").read_text())
    matches=[x for x in inv["files"] if x["episode_id_from_filename"]==ID]
    if inv.get("inventory_run_id")!=40041061527 or len(matches)!=1:
        raise ValueError("S01E01 source must be unique in accepted owner FTP inventory")
    x=matches[0]
    if x["size_bytes"]!=183386112 or x["basename"]!="Night Court - 1x01 - All You Need Is Love.avi":
        raise ValueError("Unexpected S01E01 edition/file-size change")
    if x["remote_path"]!="/downloads/Night Court TVRip S1-S9/Night.Court.S01.DVDRip.DivX/Night Court - 1x01 - All You Need Is Love.avi":
        raise ValueError("Unexpected remote video path")
    return x

def retrieve(ftp, item, output):
    expected=item["size_bytes"]
    if expected>LIMIT:raise ValueError("AVI would exceed retrieval safety limit")
    actual=0
    sha=hashlib.sha256()
    with output.open("wb") as f:
        def write(chunk):
            nonlocal actual
            actual+=len(chunk)
            if actual>LIMIT or actual>expected:raise ValueError("FTP bytes exceed declared size")
            sha.update(chunk)
            f.write(chunk)
        ftp.retrbinary("RETR "+item["remote_path"],write,blocksize=131072)
    if actual!=expected:raise ValueError("FTP transfer truncated or changed")
    return sha.hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--protocol",choices=["ftp","ftps"],default="ftp")
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--start-seconds",type=float,default=60)
    p.add_argument("--duration-seconds",type=float,default=15)
    a=p.parse_args()
    if not (0<=a.start_seconds<=7200 and 0<a.duration_seconds<=30):
        raise ValueError("Pilot excerpt must be 1–30 seconds at a valid start")
    item=candidate()
    if a.output.exists():raise ValueError("Refuse overwrite")
    password=os.environ.get("FTP_PASSWORD")
    if not password:raise ValueError("FTP_PASSWORD was not provided to manual workflow")
    with tempfile.TemporaryDirectory(prefix="night-court-original-pilot-") as temp:
        media=Path(temp)/item["basename"]
        ftp=connect(os.environ.get("FTP_HOST","wood.seedhost.eu"),
                    os.environ.get("FTP_USER","ianseeds"),password,a.protocol)
        try:
            actualsha=retrieve(ftp,item,media)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        # Rather than ingesting a new media copy into Git, invoke the already
        # CI-accepted local pilot with explicit owner-authorized research flags.
        evidence=Path(temp)/"pilot.json"
        original=sys.argv
        try:
            sys.argv=["run_s01e01_vocal_pilot.py","--media",str(media),
                "--start-seconds",str(a.start_seconds),
                "--duration-seconds",str(a.duration_seconds),
                "--episode","S01E01","--output",str(evidence),
                "--confirm-original-series","--confirm-rights"]
            run_local_pilot()
        finally:
            sys.argv=original
        report=json.loads(evidence.read_text())
        if report["source_media_sha256"]!=actualsha:
            raise ValueError("FTP transfer and media pilot hash disagreement")
        report["owner_inventory_workflow_run"]=40041061527
        report["ftp_manifest_size_bytes"]=item["size_bytes"]
        report["source_edition_filename"]=item["basename"]
        report["credential_use"]="manual_dispatch_only_existing_repo_secret"
        report["media_bytes_retained_in_artifact"]=False
        report["external_transcript_alignment"]="not_done"
        report["audiovisual_identity_verification"]="not_done"
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(report,indent=2)+"\n")
    print("S01E01: bounded original AVI inspected and ephemeral audio metrics calculated. No media retained.")

if __name__=="__main__":main()
