#!/usr/bin/env python3
"""Trusted workflow only: collect one FTP AVI, create a tiny private review packet."""
import argparse, ftplib, json, os, tempfile
from pathlib import Path
from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate,retrieve
from build_s01e01_scene_evidence import EXPECTED_SHA,make_packet

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--protocol",choices=["ftp","ftps"],default="ftp")
    args=ap.parse_args()
    if not os.environ.get("FTP_PASSWORD"):
        raise ValueError("Existing FTP_PASSWORD secret is required")
    item=candidate()
    if args.output.exists():raise ValueError("Refuse to overwrite evidence")
    with tempfile.TemporaryDirectory(prefix="nc-scene-source-") as t:
        media=Path(t)/item["basename"]
        conn=connect(os.environ.get("FTP_HOST","wood.seedhost.eu"),
                     os.environ.get("FTP_USER","ianseeds"),
                     os.environ["FTP_PASSWORD"],args.protocol)
        try:actual=retrieve(conn,item,media)
        finally:
            try:conn.quit()
            except ftplib.all_errors:conn.close()
        if actual!=EXPECTED_SHA:
            raise ValueError("New FTP bytes differ from previous verified source fingerprint")
        make_packet(media,args.output)
        data=json.loads((args.output/"evidence.json").read_text("utf-8"))
        if data["source_media_sha256"]!=EXPECTED_SHA or len(data["frame_evidence"])!=10:
            raise ValueError("Incomplete scene evidence")
    print("Private bounded S01E01 30-second packet complete; source media deleted")

if __name__=="__main__":main()
