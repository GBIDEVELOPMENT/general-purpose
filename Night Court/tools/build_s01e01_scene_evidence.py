#!/usr/bin/env python3
"""Make one bounded, evidence-linked S01E01 audio/visual review packet.

Original AVI read only, 60..90 s only. JPEGs are private preview witnesses,
not proof of gestures or motion. Captions are candidate offsets, NOT aligned.
"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, tempfile, wave
from pathlib import Path
from measure_vocal_performance import analyse

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
EDITION="s01-internal-dvdrip-xvid-sprinter-english--aa9f77600cd9f2b6"
SRT_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
CAPTION_DIR=ROOT/"seasons"/"S01"/"S01E01"/"dialogue"/"versions"/EDITION
START=60
DURATION=30
FRAMES=[60,63,66,69,72,75,78,81,84,87]
MAX_IMAGE=200_000

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as inp:
        for chunk in iter(lambda: inp.read(1024*1024), b""):h.update(chunk)
    return h.hexdigest()

def run(args,timeout=120):
    return subprocess.run(args,check=True,capture_output=True,text=True,timeout=timeout)

def select_cues(rows,start_ms=START*1000,end_ms=(START+DURATION)*1000):
    result=[]
    for row in rows:
        if row["end_ms"]>start_ms and row["start_ms"]<end_ms:
            result.append({"cue":row["cue"],"start_ms":row["start_ms"],
                "end_ms":row["end_ms"],"text":row["text"],
                "caption_edition":EDITION,"offset_status":"not_audio_verified"})
    if not result:raise ValueError("No subtitles intersect requested interval")
    return result

def make_packet(media,out,*,strict=True):
    if not media.is_file():raise ValueError("Media file missing")
    if out.exists():raise ValueError("Refuse overwrite evidence directory")
    source_sha=digest(media)
    if strict and source_sha!=EXPECTED_SHA:raise ValueError("Unapproved source media SHA")
    source_srt=CAPTION_DIR/"original.srt"
    if digest(source_srt)!=SRT_SHA:raise ValueError("SRT source hash changed")
    rows=[json.loads(line) for line in (CAPTION_DIR/"segments.jsonl").read_text("utf-8").splitlines() if line.strip()]
    cues=select_cues(rows)
    source_meta=json.loads(run(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(media)]).stdout)
    length=float(source_meta["format"]["duration"])
    if length<START+DURATION:raise ValueError("Missing target media interval")
    out.mkdir(parents=True)
    frames=out/"frames"
    frames.mkdir()
    image_records=[]
    for t in FRAMES:
        path=frames/(f"source-{t:04d}s.jpg")
        # Source timestamp preserved. A single decoded frame proves no continuous action.
        run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-ss",str(t),
             "-i",str(media),"-frames:v","1","-vf","scale=480:-2","-q:v","5",
             "-y",str(path)],timeout=70)
        if not path.exists() or not 0<path.stat().st_size<MAX_IMAGE:
            raise ValueError("Frame missing or exceeds thumbnail size limit")
        image_records.append({"video_time_ms":t*1000,"file":"frames/"+path.name,
                              "sha256":digest(path),"observation_status":"not_reviewed",
                              "evidence_kind":"single_video_frame"})
    with tempfile.TemporaryDirectory(prefix="nc-scene-audio-") as temp:
        wav=Path(temp)/"excerpt.wav"
        run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-ss",str(START),
             "-i",str(media),"-t",str(DURATION),"-map","0:a:0","-vn",
             "-ac","1","-ar","16000","-c:a","pcm_s16le","-y",str(wav)],timeout=90)
        with wave.open(str(wav),"rb") as inp:
            available_ms=round(1000*inp.getnframes()/inp.getframerate())
        if not 29000<=available_ms<=30050:raise ValueError("Audio extraction duration changed")
        spans=[]
        for start,end in ((60,66),(66,72),(72,78),(78,84),(84,90)):
            record=analyse(wav,1000*(start-START),1000*(end-START),
                           "S01E01",f"source-mix-{start}-{end}s")
            record["source_video_interval_ms"]=[start*1000,end*1000]
            spans.append(record)
        wav_sha=digest(wav)
    packet={
        "schema":"night-court-s01e01-scene-evidence/1",
        "series":"night-court-1984","episode_id":"S01E01",
        "source_media_sha256":source_sha,"source_media_bytes":media.stat().st_size,
        "source_duration_ms":round(length*1000),
        "source_audio_wav_sha256":wav_sha,"source_audio_window_ms":[START*1000,(START+DURATION)*1000],
        "dialogue_source_sha256":SRT_SHA,"dialogue_version_id":EDITION,
        "caption_audio_alignment_status":"unverified_time_match_do_not_claim_synchronized",
        "source_identity_status":"filename_and_prior_media_sha_confirmed_video_not_independently_identified",
        "source_cues":cues,"frame_evidence":image_records,"mixed_audio_windows":spans,
        "candidate_scene_title":"unassigned_pending_visual_review",
        "confirmed_speakers":[],"stage_directions":[],
        "visual_observations_status":"awaiting_frame_review_and_bounded_motion_evidence",
        "speaker_diarization_status":"not_run","emotion_annotation_status":"not_run",
        "completeness_verified":False,
        "licensing":"private_owner_directed_research_no_republication_rights_asserted",
        "media_and_wav_in_artifact":False
    }
    (out/"evidence.json").write_text(json.dumps(packet,indent=2,ensure_ascii=False)+"\n","utf-8")
    header=["# S01E01 | source passage 01:00–01:30",
            "","> Evidence packet, not a verified screenplay. Caption times are SOURCE",
            "> estimates; images are individual sampled frames; speakers and actions unresolved.","",
            "## Original caption excerpt (unverified video edition alignment)",""]
    for cue in cues:
        t=cue["start_ms"]/1000
        header.extend([f'**C{cue["cue"]:04d} ({t:.3f}s):**',cue["text"],""])
    header.extend(["## Captured visual evidence",
                   "Frames: "+", ".join(f'{t}s' for t in FRAMES),
                   "Frame hashes, audio mix measurements and uncertainty flags: evidence.json.",
                   "No movement, emotion, physical comedy or speaker identity is asserted yet."])
    (out/"source-passage.md").write_text("\n".join(header)+"\n","utf-8")
    print(f"Prepared S01E01 bounded packet: {len(cues)} source cues, {len(image_records)} frames, {len(spans)} mix intervals")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--media",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    make_packet(a.media,a.out)

if __name__=="__main__":main()
