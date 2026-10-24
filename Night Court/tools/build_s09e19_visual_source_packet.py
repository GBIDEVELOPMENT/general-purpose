#!/usr/bin/env python3
"""Produce SHA-pinned S09E19 15:00–15:25 silent, time-indexed image evidence.

Only one source AVI. No source media/audio, speaker identity, visual action
inference or show episode completeness is uploaded. Individual frame state
remains unreviewed until images are actually inspected.
"""
from __future__ import annotations
import argparse,ftplib,hashlib,json,os,subprocess,tempfile
from pathlib import Path
from ftp_research_intake import connect
from pilot_ftp_video_acoustics import retrieve
from s09e19_untimed_video_anchor_pilot import exact_candidate

ROOT=Path(__file__).resolve().parents[1]
SHA="51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649"
START=900
DURATION=25
FPS=4
FRAMES=FPS*DURATION

def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def run(*args):
    return subprocess.run(args,check=True,capture_output=True,text=True,timeout=130)

def capture(source,out,*,start=START,approved_sha=SHA):
    if out.exists():raise ValueError("Refuse to overwrite visual evidence")
    if not source.is_file() or digest(source)!=approved_sha:
        raise ValueError("Original S09E19 episode source media fingerprint mismatch")
    out.mkdir(parents=True)
    frames=out/"frames"
    frames.mkdir()
    run("ffmpeg","-hide_banner","-nostdin","-loglevel","error",
        "-ss",str(start),"-i",str(source),"-t",str(DURATION),
        "-an","-vf",f"fps={FPS},scale=320:-2",
        "-q:v","6","-y",str(frames/"frame-%03d.jpg"))
    entries=[]
    imgs=sorted(frames.glob("frame-*.jpg"))
    if len(imgs)!=FRAMES:
        raise ValueError(f"Expected {FRAMES} extracted video samples; got {len(imgs)}")
    for i,path in enumerate(imgs):
        if path.name!=f"frame-{i+1:03d}.jpg" or not 100<path.stat().st_size<150_000:
            raise ValueError("Unsafe or unexpectedly large sample frame")
        entries.append({
          "sample_index":i+1,
          "approx_source_time_ms":start*1000+i*250,
          "source_time_qualification":"nominal_4fps_sample_not_original_frame_pts",
          "sha256":digest(path),"file":"frames/"+path.name,
          "reviewed_for_scene_content":False,
          "motion_interpolation_verified":False
        })
    montage=out/"contact-sheet.jpg"
    run("ffmpeg","-hide_banner","-nostdin","-loglevel","error",
        "-framerate",str(FPS),"-i",str(frames/"frame-%03d.jpg"),
        "-vf","tile=10x10","-frames:v","1","-y",str(montage))
    if not montage.exists() or not 1000<montage.stat().st_size<2_000_000:
        raise ValueError("Invalid photo-sheet preview")
    if sum(p.stat().st_size for p in out.rglob("*") if p.is_file())>12_000_000:
        raise ValueError("Original TV image sample archive exceeded safety size")
    obj={
      "schema":"night-court-s09e19-video-frame-samples/1",
      "episode_id":"S09E19",
      "source_original_avi_sha256":SHA,
      "source_window_ms":[start*1000,(start+DURATION)*1000],
      "nominal_sampling_hz":FPS,"sample_count":FRAMES,
      "frames":entries,"contact_sheet_sha256":digest(montage),
      "original_untimed_text_sha256":"659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2",
      "cross_reference_audio_source":"source-timing-review-v1/sparse-source-paragraph-candidates.json",
      "source_paragraph_timecode_verified":False,
      "scene_setting_reviewed":False,
      "physical_action_continuous_video_reviewed":False,
      "character_speaker_identified":False,
      "episode_audiovisual_complete":False,
      "original_video_or_audio_in_artifact":False,
      "limitations":["Frames are sampled snapshots; may miss fast motion and shot transitions.",
         "Nominal 4fps timestamps do not independently prove source presentation times.",
         "The previous five-window ASR-to-paragraph proposals are lexical research only.",
         "No named actor, speaker, scene setting or physical action has been reviewed."]
    }
    (out/"frame-source-index.json").write_text(json.dumps(obj,indent=2)+"\n","utf-8")
    print("S09E19: 100 sampled and SHA-indexed source images for private visual review. No AV claims.")

def ftp_capture(out):
    item=exact_candidate()
    password=os.getenv("FTP_PASSWORD")
    if not password:raise ValueError("FTP_PASSWORD is needed only in trusted workflow")
    with tempfile.TemporaryDirectory(prefix="night-court-s09e19-frame-") as temp:
        video=Path(temp)/item["basename"]
        f=connect(os.getenv("FTP_HOST","wood.seedhost.eu"),
                  os.getenv("FTP_USER","ianseeds"),password,"ftp")
        try:received=retrieve(f,item,video)
        finally:
            try:f.quit()
            except ftplib.all_errors:f.close()
        if received!=SHA:raise ValueError("S09E19 original source changed since text matching")
        capture(video,out)
    print("Video file deleted from private temporary source directory")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--ftp",action="store_true")
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    if not args.ftp:parser.error("Only fixed-file trusted FTP mode is permitted")
    ftp_capture(args.output)
