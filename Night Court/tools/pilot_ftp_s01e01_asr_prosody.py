#!/usr/bin/env python3
"""Trusted PR target worker. One hardcoded AVI; ephemeral voice/ASR model files."""
import argparse,ftplib,json,os,tempfile
from pathlib import Path
from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate,retrieve
from build_s01e01_scene_evidence import EXPECTED_SHA
from run_s01e01_asr_prosody import run

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if not os.environ.get("FTP_PASSWORD"):raise ValueError("Existing repo FTP credential missing")
    selected=candidate()
    with tempfile.TemporaryDirectory(prefix="night-court-trusted-asr-") as tmp:
        media=Path(tmp)/selected["basename"]
        ftp=connect(os.environ.get("FTP_HOST","wood.seedhost.eu"),
                    os.environ.get("FTP_USER","ianseeds"),
                    os.environ["FTP_PASSWORD"],"ftp")
        try:digest=retrieve(ftp,selected,media)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        if digest!=EXPECTED_SHA:raise ValueError("Wrong source AVI digest")
        run(media,args.output)
        j=json.loads(args.output.read_text())
        assert j["source_media_sha256"]==EXPECTED_SHA
    print("No audio, video, or model cache persisted after ASR study")
if __name__=="__main__":main()
