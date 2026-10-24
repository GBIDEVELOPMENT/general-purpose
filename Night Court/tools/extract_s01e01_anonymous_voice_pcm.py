#!/usr/bin/env python3
"""Fetch one owner-approved S01E01 AVI and retain only 60–90s PCM on runner.

This runs in the credentialed *download step*. Speaker model loading runs in
a separate step without FTP_PASSWORD. Neither WAV nor AVI is an artifact.
"""
import argparse
import ftplib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import wave
from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate,retrieve

MEDIA_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda:file.read(1<<20),b""):h.update(block)
    return h.hexdigest()

def extract(video,pcm):
    if pcm.exists():raise ValueError("Refuse to overwrite PCM evidence")
    if digest(video)!=MEDIA_SHA:raise ValueError("Not the accepted S01E01 AVI edition")
    pcm.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error",
        "-ss","60","-i",str(video),"-t","30","-map","0:a:0",
        "-vn","-ac","1","-ar","16000","-c:a","pcm_s16le","-y",str(pcm)],
        capture_output=True,check=True,timeout=110)
    with wave.open(str(pcm),"rb") as w:
        if w.getnchannels()!=1 or w.getsampwidth()!=2 or w.getframerate()!=16000:
            raise ValueError("Unexpected PCM representation")
        length=w.getnframes()/w.getframerate()
        if not 29.9<=length<=30.05:raise ValueError("Truncated sample")
    (pcm.parent/"pcm-source-provenance.json").write_text(json.dumps({
      "original_video_sha256":MEDIA_SHA,
      "pcm_sha256":digest(pcm),
      "source_video_window_ms":[60000,90000],
      "sample_rate_hz":16000,
      "source_media_audio_not_persistent":True
    },indent=2)+"\n")
    print("Extracted temporary SHA-indexed 30s source audio; this file must not be uploaded")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-pcm",type=Path,required=True)
    a=p.parse_args()
    if a.output_pcm.exists():raise ValueError("Existing PCM cannot be overwritten")
    password=os.environ.get("FTP_PASSWORD")
    if not password:raise ValueError("Owner repo secret required only for media source step")
    with tempfile.TemporaryDirectory(prefix="nc-temporary-approved-avi-") as temp:
        item=candidate()
        source=Path(temp)/item["basename"]
        ftp=connect(os.environ.get("FTP_HOST","wood.seedhost.eu"),
            os.environ.get("FTP_USER","ianseeds"),password,"ftp")
        try:sourcehash=retrieve(ftp,item,source)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        if sourcehash!=MEDIA_SHA:raise ValueError("Owner source media SHA changed")
        extract(source,a.output_pcm)
    print("Original source AVI deleted from temporary runner directory")

if __name__=="__main__":main()
