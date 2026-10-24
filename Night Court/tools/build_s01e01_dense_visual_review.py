#!/usr/bin/env python3
"""Dense but bounded 4 Hz time-sequence from S01E01 75–90s.

No sound/video distributed. A sequence is visual evidence of sampled states,
not proof of a gesture's precise onset, meaning or performer identity.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path
from pilot_ftp_video_acoustics import candidate, retrieve
from ftp_research_intake import connect
import ftplib, os

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
T0=75
DURATION=15
RATE=4
COUNT=DURATION*RATE

def hashfile(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def run(*args):
    return subprocess.run(args,capture_output=True,text=True,check=True,timeout=110)

def capture(video,dest):
    if dest.exists():raise ValueError("No overwriting existing review packages")
    if not video.is_file() or hashfile(video)!=SOURCE_SHA:
        raise ValueError("Source media file does not match accepted AVI fingerprint")
    dest.mkdir(parents=True)
    frames=dest/"sampled-frames"
    frames.mkdir()
    run("ffmpeg","-hide_banner","-nostdin","-loglevel","error",
        "-ss",str(T0),"-i",str(video),"-t",str(DURATION),
        "-an","-vf",f"fps={RATE},scale=320:-2",
        "-q:v","6","-y",str(frames/"frame-%03d.jpg"))
    paths=sorted(frames.glob("frame-*.jpg"))
    if len(paths)!=COUNT:
        raise ValueError(f"Expected {COUNT} frame stills, received {len(paths)}")
    rows=[]
    for i,path in enumerate(paths):
        if path.stat().st_size<100 or path.stat().st_size>150_000:
            raise ValueError("Invalid thumbnail size")
        rows.append({
            "frame":i+1,"approximate_video_time_ms":T0*1000+i*(1000//RATE),
            "timestamp_qualification":"nominal_four_hz_filter_index_not_independently_frame_PTS_verified",
            "file":"sampled-frames/"+path.name,"sha256":hashfile(path),
            "observation_status":"not_reviewed",
            "continuous_motion_proven":False
        })
    # A montage is for review navigation; stills are individually hash-preserved.
    contact=dest/"contact-sheet.jpg"
    run("ffmpeg","-hide_banner","-nostdin","-loglevel","error",
        "-framerate",str(RATE),"-i",str(frames/"frame-%03d.jpg"),
        "-vf","tile=6x10","-frames:v","1","-y",str(contact))
    if not contact.is_file() or contact.stat().st_size>1_500_000:
        raise ValueError("Contact-sheet output is invalid or oversized")
    result={
        "schema":"night-court-s01e01-dense-visual-sampling/1",
        "episode_id":"S01E01",
        "source_media_sha256":SOURCE_SHA,
        "source_time_window_ms":[75000,90000],
        "sampling_frames_per_second":RATE,
        "frames_expected":COUNT,"frames_actual":len(rows),
        "frame_evidence":rows,
        "contact_sheet_sha256":hashfile(contact),
        "source_video_audio_bytes_in_artifact":False,
        "scene_action_observations":[],
        "character_speaker_identities_confirmed":False,
        "source_SRT_audio_alignment_confirmed":False,
        "pose_to_pose_interpretation":"requires_a_separate_frame_review",
        "visual_continuity_limitation":"sampling_4fps_can_miss_fast_entrances_gestures_and_reactions",
        "audiovisual_episode_completeness_verified":False
    }
    (dest/"dense-frame-index.json").write_text(json.dumps(result,indent=2)+"\n","utf-8")
    print(f"S01E01 dense visual evidence: {len(rows)} private 320px stills; AV ID unchanged")

def ftp_main(destination):
    item=candidate()
    with tempfile.TemporaryDirectory(prefix="night-court-dense-source-") as t:
        source=Path(t)/item["basename"]
        pwd=os.environ.get("FTP_PASSWORD")
        if not pwd:raise ValueError("FTP_PASSWORD is required for trusted owner-only run")
        ftp=connect(os.environ.get("FTP_HOST","wood.seedhost.eu"),
            os.environ.get("FTP_USER","ianseeds"),pwd,"ftp")
        try:hash_v=retrieve(ftp,item,source)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        if hash_v!=SOURCE_SHA:raise ValueError("Remote source changed")
        capture(source,destination)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--media",type=Path)
    ap.add_argument("--ftp",action="store_true")
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    if a.ftp==bool(a.media):ap.error("Choose exactly one of --ftp or --media")
    if a.ftp:ftp_main(a.output)
    else:capture(a.media,a.output)

if __name__=="__main__":
    main()
