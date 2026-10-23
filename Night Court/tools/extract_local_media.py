#!/usr/bin/env python3
"""Extract text subtitles or optionally transcribe LOCAL Night Court media.

Only local, user-supplied lawfully accessible, DRM-free files. Never downloads
episodes, removes access controls, uploads video, or copies web transcripts.

Examples:
  python "Night Court/tools/extract_local_media.py" --media ~/Videos/S01E01.mkv --dry-run
  python "Night Court/tools/extract_local_media.py" --media ~/Videos/S01E01.mkv --episode S01E01 --edition "Owned DVD" --confirm-original-series --rights-basis lawfully_obtained_research_copy --confirm-rights
  python "Night Court/tools/extract_local_media.py" --directory ~/Videos/NightCourtOriginal --edition "Owned DVD" --confirm-original-series --rights-basis lawfully_obtained_research_copy --confirm-rights
  python "Night Court/tools/extract_local_media.py" --media S01E01.mp4 --mode asr --model /local/whisper-model --edition "Personal ASR v1" --episode S01E01 --confirm-original-series --rights-basis lawfully_obtained_research_copy --confirm-rights
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

import import_dialogue as D

TEXT_SUBTITLE_CODECS = {
    "subrip","srt","webvtt","mov_text","ass","ssa","text","ttml","sami","microdvd"
}
VIDEO_TYPES = {".mkv",".mp4",".m4v",".mov",".avi",".webm",".ts",".m2ts"}
MAX_BATCH_FILES = 500
CMD_TIMEOUT = 240

def run(command, timeout=CMD_TIMEOUT):
    try:
        return subprocess.run(command,check=True,capture_output=True,text=True,
                              timeout=timeout)
    except FileNotFoundError as exc:
        raise ValueError(f"Required executable unavailable: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ValueError(f"Timed out running {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"{command[0]} exited {exc.returncode}: {exc.stderr[-900:]}") from exc

def probe(media):
    media=Path(media)
    if not media.is_file() or media.stat().st_size<1:
        raise ValueError(f"Local media not found or empty: {media}")
    result=run(["ffprobe","-v","error","-show_streams","-show_format",
                "-of","json",str(media)],timeout=40)
    try:data=json.loads(result.stdout)
    except json.JSONDecodeError as exc:raise ValueError("ffprobe did not return JSON") from exc
    if not isinstance(data.get("streams"),list):raise ValueError("ffprobe found no streams")
    return data

def track_language(s):
    tags=s.get("tags") or {}
    value=str(tags.get("language") or "").lower().split("-")[0]
    return {"eng":"en","english":"en","en":"en","und":"und","":"und"}.get(value,value)

def select_text_tracks(data, requested="en", specific=None, all_tracks=False):
    subtitles=[s for s in data["streams"] if s.get("codec_type")=="subtitle"]
    text=[s for s in subtitles if str(s.get("codec_name","")).lower() in TEXT_SUBTITLE_CODECS]
    if specific is not None:
        selected=[s for s in text if s.get("index")==specific]
        if not selected:raise ValueError(f"Subtitle stream {specific} absent or not text-decodable")
        return selected
    if all_tracks:return sorted(text,key=lambda x:x["index"])
    matching=[s for s in text if track_language(s)==requested.lower()]
    if not matching and requested.lower()=="en":
        matching=[s for s in text if track_language(s)=="und"]
    # Prefer stream flagged default, otherwise stable stream index.
    return sorted(matching,key=lambda x:(-int(x.get("disposition",{}).get("default",0)),x["index"]))[:1]

def format_clock(seconds):
    if not math.isfinite(seconds) or seconds<0:
        raise ValueError("Invalid speech timing")
    ms=round(seconds*1000)
    h,rem=divmod(ms,3_600_000)
    m,rem=divmod(rem,60_000)
    s,sub=divmod(rem,1000)
    return f"{h:02d}:{m:02d}:{s:02d},{sub:03d}"

def srt_from_asr(segments):
    """ASR text belongs to a model output, NEVER an attributed spoken quotation."""
    lines=[]
    for item in segments:
        start,end=float(item.start),float(item.end)
        content=str(item.text).strip()
        if not content:continue
        if end<start:raise ValueError("ASR segment ends before start")
        lines.append(f"{len(lines)+1}\n{format_clock(start)} --> {format_clock(end)}\n{content}")
    if not lines:raise ValueError("ASR returned no segments")
    return "\n\n".join(lines)+"\n"

def recognize(media, destination, model_path, language, allow_model_download=False):
    if not model_path:raise ValueError("--mode asr requires --model (cached model name or local path)")
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise ValueError("Optional local ASR requires: python -m pip install faster-whisper") from exc
    # Default refuses model network downloads, preventing unexpected fetches.
    model=WhisperModel(model_path,device="auto",compute_type="int8",
                       local_files_only=not allow_model_download)
    segments,_info=model.transcribe(str(media),language=language,beam_size=5,
                                     vad_filter=True,condition_on_previous_text=False)
    destination.write_text(srt_from_asr(segments),encoding="utf-8")

def options_for(args,ep,edition,language,origin):
    return {
        "episode":ep,"edition":edition,"language":language,
        "rights_basis":args.rights_basis,"confirmed":args.confirm_rights,
        "complete":args.complete,
        "source_name":str(origin.name),
        "source_url":None,
        "notes":"Local DRM-free media; "+("faster-whisper ASR, unverified transcription"
               if args.mode=="asr" else "ffmpeg source-text subtitle stream extraction")
    }

def extract_one(media,args,ep=None):
    info=probe(media)
    text_streams=[s for s in info["streams"] if s.get("codec_type")=="subtitle"
                  and s.get("codec_name") in TEXT_SUBTITLE_CODECS]
    if args.dry_run:
        print(json.dumps({"source_media":media.name,"stream_inventory":[{
            "index":s.get("index"),"codec_type":s.get("codec_type"),
            "codec_name":s.get("codec_name"),"language":track_language(s),
            "text_subtitle_supported":s in text_streams}
            for s in info["streams"]],"note":"Inspection only; nothing imported or stored"},
            indent=2,ensure_ascii=False))
        return 0
    if not args.confirm_original_series:
        raise ValueError("Explicit --confirm-original-series required; 2023 reboot episode IDs overlap")
    if not args.confirm_rights or not args.rights_basis:
        raise ValueError("Explicit --rights-basis and --confirm-rights required")
    ep=ep or D.episode_id(args.episode or media.name)
    if args.mode=="subtitles":
        chosen=select_text_tracks(info,args.language,args.track_index,args.all_text_tracks)
        if not chosen:
            raise ValueError("No supported text subtitle stream; inspect with --dry-run or use --mode asr")
    else:
        chosen=[]
        if not any(s.get("codec_type")=="audio" for s in info["streams"]):
            raise ValueError("ASR requires local audio stream")
    imported=0
    with TemporaryDirectory(prefix="night-court-local-media-") as temp:
        root=Path(temp)
        if args.mode=="subtitles":
            for s in chosen:
                number=s["index"]
                track=root/f"{ep}.stream{number}.srt"
                run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
                    "-i",str(media),"-map",f"0:{number}","-c:s","srt",str(track)])
                if not track.is_file() or not track.stat().st_size:
                    raise ValueError(f"Subtitle stream {number} produced no source text")
                locale=track_language(s)
                if locale=="und":locale=args.language
                edition=f"{args.edition} text-track-{number} ({s.get('codec_name','unknown')})"
                D.import_one(track,options_for(args,ep,edition,locale,media))
                imported+=1
        else:
            transcript=root/f"{ep}.asr.srt"
            recognize(media,transcript,args.model,args.language,args.allow_model_download)
            edition=f"{args.edition} local-ASR ({args.model})"
            D.import_one(transcript,options_for(args,ep,edition,args.language,media))
            imported+=1
    D.rebuild_index()
    return imported

def main():
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    sources=p.add_mutually_exclusive_group(required=True)
    sources.add_argument("--media",type=Path,help="local DRM-free video/audio container")
    sources.add_argument("--directory",type=Path,help="recurse an owned local video directory")
    p.add_argument("--episode",help="explicit original-series SxxEyy; required if filename lacks it")
    p.add_argument("--edition",help="release/edition identifier, e.g. Own DVDs",default="local-media")
    p.add_argument("--language",default="en",help="preferred subtitle/ASR language code")
    p.add_argument("--mode",choices=["subtitles","asr"],default="subtitles")
    p.add_argument("--model",help="local faster-whisper model path or cached model name")
    p.add_argument("--allow-model-download",action="store_true",
                   help="explicitly allow fetching model weights when using ASR")
    p.add_argument("--track-index",type=int,help="absolute ffprobe subtitle stream index")
    p.add_argument("--all-text-tracks",action="store_true",
                   help="import every decodable text subtitle stream, keeping languages separate")
    p.add_argument("--dry-run",action="store_true",help="inspect streams, do not import")
    p.add_argument("--complete",action="store_true",help="submitter-declared complete only")
    p.add_argument("--rights-basis",choices=sorted(D.RIGHTS))
    p.add_argument("--confirm-rights",action="store_true")
    p.add_argument("--confirm-original-series",action="store_true")
    args=p.parse_args()
    if args.directory is not None and args.episode:
        p.error("--episode cannot identify a directory batch; filenames must identify each episode")
    if args.track_index is not None and args.all_text_tracks:
        p.error("Choose --track-index or --all-text-tracks, not both")
    if args.mode=="asr" and not args.dry_run and not args.model:
        p.error("--mode asr requires --model")
    if args.mode=="asr" and args.all_text_tracks:
        p.error("--all-text-tracks only applies to subtitle extraction")
    if args.directory:
        if not args.directory.is_dir():p.error("Local media directory not found")
        files=sorted(f for f in args.directory.rglob("*") if f.is_file() and f.suffix.lower() in VIDEO_TYPES)
        if len(files)>MAX_BATCH_FILES:p.error("Batch exceeds 500 files; split into smaller batches")
        completed=0;problems=[]
        for media in files:
            try:
                ep=D.episode_id(media.name)
                completed+=extract_one(media,args,ep)
            except (OSError,ValueError,RuntimeError) as exc:
                problems.append({"file":media.name,"reason":str(exc)})
        print(json.dumps({"media_files_scanned":len(files),"tracks_extracted":completed,
                          "media_errors":problems},ensure_ascii=False,indent=2))
        if problems:sys.exit(1)
    else:
        count=extract_one(args.media,args)
        if not args.dry_run:print(f"Extracted {count} source track(s). Run audit_dialogue_quality.py next.")

if __name__=="__main__":main()
