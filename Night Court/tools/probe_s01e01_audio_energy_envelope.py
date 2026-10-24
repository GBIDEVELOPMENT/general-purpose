#!/usr/bin/env python3
"""Original S01E01 bounded mixed-TV-soundtrack level envelope, not voice truth.

Original AVI is SHA-pinned; decoded audio is held only in ephemeral process
memory, never written or uploaded. Level values include music/noise/laughter.
No word, speaker, emotion or utterance identity can be inferred from RMS.
"""
from __future__ import annotations
import argparse
from array import array
import ftplib
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile

from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate,retrieve

ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/"seasons/S01/S01E01/derived/editorial-review-v1/acceptance-worklist.json"
MANIFEST=ROOT/"seasons/S01/S01E01/derived/editorial-review-v1/review-cut-manifest.json"
SOURCE_VIDEO_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SOURCE_SRT_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
WINDOW=(56912,93074)
RATE=16000
STEP_SAMPLES=1600
MAX_PCM_BYTES=1_600_000

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def contract():
    m=json.loads(MANIFEST.read_text("utf-8"))
    packet=json.loads(PACKET.read_text("utf-8"))
    w=m.get("continuous_review_windows",[])
    if (m.get("source_video_sha256")!=SOURCE_VIDEO_SHA
        or m.get("source_caption_sha256")!=SOURCE_SRT_SHA
        or packet.get("source_video_sha256")!=SOURCE_VIDEO_SHA
        or packet.get("source_caption_sha256")!=SOURCE_SRT_SHA
        or len(w)!=1 or [w[0]["start_ms"],w[0]["end_ms"]]!=list(WINDOW)
        or len(packet.get("voice_review_tasks",[]))!=11
        or len(packet.get("visual_review_tasks",[]))!=6
        or m.get("source_video_size_bytes_candidate")!=183386112
        or m.get("publication_status")!="review_material_only_zero_av_acceptances"):
        raise ValueError("Original S01E01 source/time/editorial contract changed")
    return m,packet

def to_db(value):
    return round(max(-120.,20*math.log10(value)) if value>0 else -120.,3)

def envelope_pcm(raw,*,start_ms=WINDOW[0],rate=RATE,step_samples=STEP_SAMPLES):
    if len(raw)%2 or len(raw)>MAX_PCM_BYTES:
        raise ValueError("Decoded PCM exceeds small bounded audio window")
    if rate!=RATE or step_samples!=STEP_SAMPLES or start_ms<0:
        raise ValueError("Unrecognized timebase or measured resolution")
    pcm=array("h")
    pcm.frombytes(raw)
    if sys.byteorder!="little":
        pcm.byteswap()
    out=[]
    for idx in range(0,len(pcm),step_samples):
        window=pcm[idx:idx+step_samples]
        if not window:break
        mean_square=sum(int(x)*int(x) for x in window)/len(window)
        rms=math.sqrt(mean_square)/32768.
        peak=max(abs(int(x)) for x in window)/32768.
        begin=start_ms+round(idx*1000/rate)
        end=start_ms+round((idx+len(window))*1000/rate)
        out.append({
          "index":len(out),"nominal_start_ms":begin,"nominal_end_ms":end,
          "rms_dbfs":to_db(rms),"peak_dbfs":to_db(peak)
        })
    return out

def tasks_from_envelope(packet,rows):
    results=[]
    for task in packet["voice_review_tasks"]:
        a,b=task["source_caption_interval_ms"]
        bins=[r for r in rows if r["nominal_end_ms"]>a and r["nominal_start_ms"]<b]
        if not bins:
            raise ValueError("Speech source caption turn lies outside acoustic window")
        results.append({
          "source_task_id":task["task_id"],
          "original_source_caption_interval_ms":[a,b],
          "overlapping_mixed_audio_bin_count":len(bins),
          "mixed_soundtrack_rms_median_dbfs":round(statistics.median(x["rms_dbfs"] for x in bins),3),
          "mixed_soundtrack_peak_max_dbfs":max(x["peak_dbfs"] for x in bins),
          "original_speech_present_verified":False,
          "source_word_times_verified":False,
          "speaker_or_delivery_verified":False
        })
    if len(results)!=11:
        raise ValueError("Missing original caption-turn energy reviews")
    return results

def analyze(original,manifest,packet):
    if (not original.is_file() or original.stat().st_size!=manifest["source_video_size_bytes_candidate"]
        or sha(original)!=SOURCE_VIDEO_SHA):
        raise ValueError("Original S01E01 AVI checksum or size mismatch")
    cmd=["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
         "-i",str(original),"-ss",f"{WINDOW[0]/1000:.3f}",
         "-t",f"{(WINDOW[1]-WINDOW[0])/1000:.3f}",
         "-map","0:a:0","-vn","-ac","1","-ar",str(RATE),
         "-f","s16le","-"]
    p=subprocess.run(cmd,check=True,capture_output=True,timeout=140)
    pcm=p.stdout
    if not 34*RATE*2<=len(pcm)<=38*RATE*2:
        raise ValueError("Original cut audio did not cover 36-second bounded excerpt")
    rows=envelope_pcm(pcm)
    summary=tasks_from_envelope(packet,rows)
    return {
        "schema":"night-court-s01e01-mixed-soundtrack-envelope/1",
        "episode_id":"S01E01",
        "original_video_sha256":SOURCE_VIDEO_SHA,
        "original_source_srt_sha256":SOURCE_SRT_SHA,
        "source_review_window_ms":list(WINDOW),
        "source_audio_extraction":"FFmpeg original AVI 16kHz mono PCM in ephemeral memory only",
        "nominal_decoded_time_origin_ms":WINDOW[0],
        "decoded_sample_rate_hz":RATE,
        "sample_count":len(pcm)//2,
        "duration_ms_derived_from_sample_count":round((len(pcm)//2)*1000/RATE),
        "level_bin_width_ms":100,
        "level_bins":rows,
        "caption_turn_mixed_audio":summary,
        "original_source_caption_turns":11,
        "human_listened_original_audio":False,
        "any_speech_words_verified":False,
        "speaker_identity_verified":False,
        "vocal_delivery_or_emotion_verified":False,
        "original_audio_to_caption_alignment_verified":False,
        "episode_screenplay_complete":False,
        "audio_PCM_or_AVI_exported":False,
        "limits":[
          "Audio is the MONO television mix, including music, laughter, noise and overlapping voices.",
          "RMS/peak energy cannot establish whether a caption word was spoken or identify a speaker.",
          "Nominal decoded time bins require independent source-edition AV synchronization review.",
          "ASR, isolated voices, emotional delivery and complete dialogue are not inferred by this worker."
        ]
    }

def ftp_main(out):
    if out.exists():raise ValueError("Refuse overwrite of acoustic source evidence")
    m,packet=contract()
    item=candidate()
    if (item["size_bytes"]!=m["source_video_size_bytes_candidate"]
        or item["basename"]!=m["source_video_filename_candidate"]):
        raise ValueError("Historical FTP candidate changed")
    pwd=os.getenv("FTP_PASSWORD")
    if not pwd:raise ValueError("Expected tightly scoped owner FTP source secret")
    with tempfile.TemporaryDirectory(prefix="night-court-audio-energy-") as temp:
        media=Path(temp)/item["basename"]
        ftp=connect(os.getenv("FTP_HOST","wood.seedhost.eu"),
                    os.getenv("FTP_USER","ianseeds"),pwd,"ftp")
        try:received=retrieve(ftp,item,media)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        if received!=SOURCE_VIDEO_SHA:raise ValueError("Original AVI source changed")
        obj=analyze(media,m,packet)
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(obj,indent=2)+"\n","utf-8")
    print("S01E01 mixed audio amplitude envelope and 11 source-turn energy summaries; all voice/word claims pending")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ftp",action="store_true")
    ap.add_argument("--output",required=True,type=Path)
    opts=ap.parse_args()
    if not opts.ftp:ap.error("Trusted owner source workflow only")
    ftp_main(opts.output)

if __name__=="__main__":
    main()
