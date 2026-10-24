#!/usr/bin/env python3
"""Bounded original-frame-rate S01E01 shot-boundary hypotheses, not screenplay truth.

Runs only on a complete AVI with the established original SHA-256 and exact
inventory size. The source-video process returns small metadata scores and
original-stream PTS candidates. It exports NO original picture/audio bytes.
"""
from __future__ import annotations
import argparse
from decimal import Decimal, ROUND_HALF_UP
import ftplib
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate, retrieve

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"seasons/S01/S01E01/derived/editorial-review-v1/review-cut-manifest.json"
AVI_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SRT_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
WINDOW=(56912,93074)
THRESHOLD=Decimal("0.12")
FRAME_RE=re.compile(r"\bframe:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:\s*(-?\d+(?:\.\d+)?)")
SCORE_RE=re.compile(r"\blavfi\.scene_score=([0-9]+(?:\.[0-9]+)?)")

def sha(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda:source.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def contract():
    m=json.loads(MANIFEST.read_text("utf-8"))
    w=m.get("continuous_review_windows",[])
    if (m.get("schema")!="night-court-source-hash-pinned-review-cut-manifest/1"
        or m.get("episode_id")!="S01E01"
        or m.get("source_video_sha256")!=AVI_SHA
        or m.get("source_caption_sha256")!=SRT_SHA
        or m.get("source_video_size_bytes_candidate")!=183386112
        or len(w)!=1
        or [w[0]["start_ms"],w[0]["end_ms"]]!=list(WINDOW)
        or len(m.get("tasks",[]))!=17
        or set(w[0]["task_ids"])!={t["task_id"] for t in m["tasks"]}
        or m.get("publication_status")!="review_material_only_zero_av_acceptances"):
        raise ValueError("Original S01E01 source/scene review contract changed")
    return m

def parse_scores(stderr:str,*,start_ms:int,end_ms:int):
    if not (0<=start_ms<end_ms):
        raise ValueError("Invalid bounded video source interval")
    rows=[]
    pending=None
    for line in stderr.splitlines():
        match=FRAME_RE.search(line)
        if match and "Parsed_metadata_" in line:
            if pending is not None:
                raise ValueError("Missing original scored video frame evidence")
            pending=(int(match[1]),match[3])
            continue
        score_match=SCORE_RE.search(line)
        if score_match and "Parsed_metadata_" in line:
            if pending is None:
                raise ValueError("Unpaired scene score")
            n,timecode=pending
            when=int((Decimal(timecode)*1000).quantize(Decimal("1"),rounding=ROUND_HALF_UP))
            score=Decimal(score_match[1])
            if not (0<score<=1):
                raise ValueError("Scene score outside FFmpeg scene range")
            if not (start_ms-100 <= when <= end_ms+100):
                raise ValueError("Frame PTS outside requested original-video window")
            if rows and (when<=rows[-1]["original_stream_pts_candidate_ms"]
                         or n<=rows[-1]["selected_frame_index"]):
                raise ValueError("Shot candidate PTS or sample index not increasing")
            rows.append({
                "selected_frame_index":n,
                "original_stream_pts_candidate_ms":when,
                "ffmpeg_scene_score":float(score),
                "source_time_status":"decoded_avi_presentation_timestamp_candidate_not_independently_verified_cut"
            })
            pending=None
    if pending is not None:
        raise ValueError("Incomplete scene score output")
    if len(rows)>300:
        raise ValueError("Unbounded original scene candidates")
    return rows

def ffmpeg_candidates(media:Path,start_ms:int,end_ms:int,threshold:Decimal=THRESHOLD):
    if not (0<=start_ms<end_ms and end_ms-start_ms<=45000):
        raise ValueError("Analysis restricted to 45 seconds of source")
    if not (Decimal("0.05")<=threshold<=Decimal("0.7")):
        raise ValueError("Scene threshold outside bounded review range")
    filtergraph=f"select='gt(scene,{threshold})',metadata=print:key=lavfi.scene_score"
    argv=["ffmpeg","-nostdin","-hide_banner","-loglevel","info",
          "-i",str(media),"-ss",f"{start_ms/1000:.3f}",
          "-t",f"{(end_ms-start_ms)/1000:.3f}",
          "-map","0:v:0","-an","-vf",filtergraph,
          "-fps_mode","vfr","-f","null","-"]
    job=subprocess.run(argv,capture_output=True,text=True,timeout=160,check=True)
    if len(job.stderr)>3_000_000:
        raise ValueError("Excessively verbose scene score output")
    return parse_scores(job.stderr,start_ms=start_ms,end_ms=end_ms)

def analyze(original:Path,m=None):
    m=contract() if m is None else m
    if (not original.is_file() or
        original.stat().st_size!=m["source_video_size_bytes_candidate"]):
        raise ValueError("Original source AVI byte count mismatch")
    if sha(original)!=m["source_video_sha256"]:
        raise ValueError("Original source AVI SHA-256 mismatch")
    rows=ffmpeg_candidates(original,*WINDOW)
    return {
       "schema":"night-court-s01e01-avi-shot-change-candidates/1",
       "episode_id":"S01E01",
       "source_original_video_sha256":m["source_video_sha256"],
       "source_original_caption_sha256":m["source_caption_sha256"],
       "source_video_expected_size_bytes":m["source_video_size_bytes_candidate"],
       "source_window_ms":list(WINDOW),
       "original_srt_source_turns_in_scope":11,
       "sampled_visual_action_tasks_in_scope":6,
       "detector":"FFmpeg select(scene) contrast-based candidate threshold",
       "detector_threshold":float(THRESHOLD),
       "candidate_count":len(rows),
       "candidate_shot_changes":rows,
       "original_video_audio_or_frames_exported":False,
       "independent_human_video_review":False,
       "speaker_or_character_identity_verified":False,
       "continuous_stage_action_verified":False,
       "scene_boundaries_verified":False,
       "original_video_to_subtitle_alignment_verified":False,
       "production_script_accepted":False,
       "limits":[
         "Scene scores flag changes in adjacent decoded image frames, including edits, flashes or fast action.",
         "A thresholded candidate is NOT a verified shot cut, dissolve or real story scene change.",
         "Decoded AVI presentation timestamps are research proposals, not independently accepted source-cut sync.",
         "No soundtrack was listened to, and no voice or acting delivery was attributed."
       ]
    }

def run_ftp(out:Path):
    m=contract()
    item=candidate()
    if (item["basename"]!=m["source_video_filename_candidate"] or
        item["size_bytes"]!=m["source_video_size_bytes_candidate"]):
        raise ValueError("Pinned FTP video candidate no longer matches source contract")
    if out.exists():
        raise ValueError("Refuse to overwrite past capture evidence")
    if not os.environ.get("FTP_PASSWORD"):
        raise ValueError("Trusted source job missing secret")
    with tempfile.TemporaryDirectory(prefix="night-court-shot-pts-") as temp:
        video=Path(temp)/item["basename"]
        ftp=connect(os.getenv("FTP_HOST","wood.seedhost.eu"),
                    os.getenv("FTP_USER","ianseeds"),os.environ["FTP_PASSWORD"],"ftp")
        try:
            digest=retrieve(ftp,item,video)
        finally:
            try: ftp.quit()
            except ftplib.all_errors: ftp.close()
        if digest!=AVI_SHA:
            raise ValueError("FTP original source changed")
        result=analyze(video,m)
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(result,indent=2)+"\n","utf-8")
    print(f"Original S01E01 AVI scene candidates: {result['candidate_count']}; all stage and speaker acceptance pending")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ftp",action="store_true")
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    if not a.ftp:p.error("Only trusted pinned-source FTP capture is exposed by CLI")
    run_ftp(a.output)

if __name__=="__main__":
    main()
