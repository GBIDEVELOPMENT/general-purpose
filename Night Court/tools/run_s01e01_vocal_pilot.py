#!/usr/bin/env python3
"""Bounded local audiovisual-to-acoustic S01E01 pilot, no remote access.

This does not perform ASR, diarization, video interpretation or edition validation.
Source must be a locally accessible owner-authorized original-series episode.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import wave
from measure_vocal_performance import analyse

ROOT=Path(__file__).resolve().parents[1]
MAX_SECONDS=30

def invoke(args,timeout=90):
    return subprocess.run(args,check=True,capture_output=True,text=True,timeout=timeout)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--media",required=True,type=Path)
    p.add_argument("--episode",default="S01E01")
    p.add_argument("--start-seconds",type=float,default=60)
    p.add_argument("--duration-seconds",type=float,default=15)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--confirm-original-series",action="store_true")
    p.add_argument("--confirm-rights",action="store_true")
    a=p.parse_args()
    if a.episode!="S01E01":
        raise ValueError("This pilot is intentionally S01E01 only")
    if not a.confirm_original_series or not a.confirm_rights:
        raise ValueError("Explicit series identity and media-rights confirmation required")
    if not a.media.is_file() or a.media.stat().st_size==0:
        raise ValueError("Source video does not exist")
    if not (0 <= a.start_seconds <= 7200 and 0 < a.duration_seconds <= MAX_SECONDS):
        raise ValueError("One excerpt of at most 30 seconds is permitted")
    if a.output.exists():
        raise ValueError("Refusing to overwrite prior pilot output")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    probe=json.loads(invoke(["ffprobe","-v","error","-show_entries",
        "format=duration,size:stream=index,codec_type,codec_name,sample_rate,channels",
        "-of","json",str(a.media)],timeout=35).stdout)
    if not any(x.get("codec_type")=="audio" for x in probe.get("streams",[])):
        raise ValueError("Source has no audio stream")
    length=float(probe.get("format",{}).get("duration",0))
    if a.start_seconds+a.duration_seconds>length:
        raise ValueError("Excerpt extends beyond source runtime")
    sourcehash=hashlib.sha256()
    with a.media.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            sourcehash.update(chunk)
    with tempfile.TemporaryDirectory(prefix="night-court-s01e01-") as tmp:
        wav=Path(tmp)/"audio-mono-16k.wav"
        invoke(["ffmpeg","-hide_banner","-nostdin","-loglevel","error",
                "-ss",str(a.start_seconds),"-i",str(a.media),"-t",str(a.duration_seconds),
                "-map","0:a:0","-vn","-ac","1","-ar","16000",
                "-c:a","pcm_s16le","-y",str(wav)])
        with wave.open(str(wav),"rb") as w:
            duration_ms=round(w.getnframes()*1000/w.getframerate())
        result=analyse(wav,0,duration_ms,"S01E01","unaligned-media-excerpt")
    manifest={
        "schema":"night-court-s01e01-vocal-pilot/1",
        "episode_id":"S01E01",
        "source_media_sha256":sourcehash.hexdigest(),
        "source_media_bytes":a.media.stat().st_size,
        "source_duration_seconds":length,
        "source_streams":probe["streams"],
        "excerpt_source_start_seconds":a.start_seconds,
        "excerpt_requested_duration_seconds":a.duration_seconds,
        "excerpt_actual_duration_ms":duration_ms,
        "audio_features":result,
        "source_video_identity_status":"owner_asserted_not_av_verified",
        "subtitle_alignment_status":"not_done",
        "speaker_identity_status":"unknown",
        "emotion_status":"not_measured",
        "scene_and_visual_annotation_status":"not_done",
        "source_media_not_exported":True,
        "review_status":"unreviewed_acoustic_first_pass"
    }
    a.output.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print("Bounded S01E01 pilot acoustic manifest written; no media exported or uploaded")

if __name__=="__main__":main()
