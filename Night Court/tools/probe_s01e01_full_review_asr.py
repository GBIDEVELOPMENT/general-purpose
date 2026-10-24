#!/usr/bin/env python3
"""Fixed S01E01 36.162s original-AVI listening-prep ASR, not dialogue verification.

The input source and SRT are SHA pinned. A tiny.en Whisper hypothesis is a
second reading, NOT independently listened original dialogue. No speaker or
emotion identity; source word fidelity and subtitle-video sync remain open.
"""
from __future__ import annotations
import argparse
import ftplib
import hashlib
import importlib.metadata
import json
import os
import re
import subprocess
import tempfile
import wave
from difflib import SequenceMatcher
from pathlib import Path

from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate,retrieve
from build_s01e01_review_cut_manifest import build as review_build

ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/"seasons/S01/S01E01/derived/editorial-review-v1/acceptance-worklist.json"
SOURCE_VIDEO_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SOURCE_SRT_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
START_MS=56912
END_MS=93074
MODEL="tiny.en"

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def norm(text):
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]"," ",text.casefold())).strip()

def original_packet():
    packet=json.loads(PACKET.read_text("utf-8"))
    m=review_build()
    if (packet.get("source_video_sha256")!=SOURCE_VIDEO_SHA
        or packet.get("source_caption_sha256")!=SOURCE_SRT_SHA
        or packet.get("counts",{}).get("source_speaking_turns")!=11
        or m["source_video_sha256"]!=SOURCE_VIDEO_SHA
        or m["source_caption_sha256"]!=SOURCE_SRT_SHA
        or m["continuous_review_windows"][0]["start_ms"]!=START_MS
        or m["continuous_review_windows"][0]["end_ms"]!=END_MS):
        raise ValueError("Original audiovisual source and review cut no longer match")
    return packet,m

def compare_turns(packet,segments):
    out=[]
    seen=set()
    for t in packet["voice_review_tasks"]:
        id=t["task_id"]
        if id in seen:raise ValueError("Duplicate original source caption speaking turn")
        seen.add(id)
        src=t["original_dialogue"]
        start,end=t["source_caption_interval_ms"]
        if not START_MS<=start<end<=END_MS:
            raise ValueError("Original source caption not fully covered in ASR sample")
        nearby=[x for x in segments if x["start_ms"]<end+1500 and x["end_ms"]>start-1500]
        ranked=sorted(
           [(SequenceMatcher(None,norm(src),norm(x["text"]),autojunk=False).ratio(),x)
            for x in nearby if norm(x["text"])],
           key=lambda z:z[0],reverse=True
        )
        best=ranked[0] if ranked else None
        out.append({
            "task_id":id,
            "source_cue":t["source_cue"],
            "original_source_caption_interval_ms":[start,end],
            "exact_source_text_preserved":src,
            "candidate_asr_segment_index":best[1]["index"] if best and best[0]>=.35 else None,
            "candidate_similarity_score":round(best[0],4) if best else None,
            "ASR_segment_to_source_text_matching":"lexical_and_overlap_proposal_only",
            "multiple_original_typographic_turns_may_share_cue_interval":sum(
                x["source_caption_interval_ms"]==[start,end]
                for x in packet["voice_review_tasks"])>1,
            "source_word_fidelity_independently_listened":False,
            "source_word_timings_verified":False,
            "speaking_character_verified":False
        })
    if len(out)!=11:
        raise ValueError("Missing source caption speaking turn")
    return out

def analyze(video,destination):
    p,m=original_packet()
    if (not video.is_file() or video.stat().st_size!=m["source_video_size_bytes_candidate"]
        or digest(video)!=SOURCE_VIDEO_SHA):
        raise ValueError("Original AVI SHA or byte size mismatch")
    if destination.exists():raise ValueError("Refuse existing ASR evidence output")
    with tempfile.TemporaryDirectory(prefix="night-court-full-cut-asr-") as tmp:
        wav=Path(tmp)/"original-source-audio.wav"
        subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
           "-i",str(video),"-ss",f"{START_MS/1000:.3f}",
           "-t",f"{(END_MS-START_MS)/1000:.3f}",
           "-map","0:a:0","-vn","-ac","1","-ar","16000",
           "-c:a","pcm_s16le",str(wav)],
           check=True,capture_output=True,timeout=150)
        with wave.open(str(wav),"rb") as f:
            frames=f.getnframes();rate=f.getframerate()
        actual_duration_ms=round(frames*1000/rate)
        if rate!=16000 or not 36050<=actual_duration_ms<=36250:
            raise ValueError("Wrong original-source WAV duration")
        wavsha=digest(wav)
        from faster_whisper import WhisperModel
        model=WhisperModel(MODEL,device="cpu",compute_type="int8",
                           download_root=str(Path(tmp)/"model-cache"))
        candidates,info=model.transcribe(str(wav),language="en",
           beam_size=3,word_timestamps=True,vad_filter=False,
           condition_on_previous_text=False)
        results=[]
        for seg in candidates:
            if len(results)>=40:raise ValueError("ASR segment list exceeds one bounded source window")
            start=max(START_MS,round(START_MS+seg.start*1000))
            end=min(END_MS,round(START_MS+seg.end*1000))
            if start>=end or not seg.text.strip():continue
            text=seg.text.strip()
            if len(text)>1200:raise ValueError("Unexpectedly long model text hypothesis")
            words=[]
            for word in seg.words or []:
                if len(words)>=250:raise ValueError("ASR proposed word list unsafe")
                a=max(START_MS,round(START_MS+word.start*1000))
                b=min(END_MS,round(START_MS+word.end*1000))
                if a>=b:continue
                words.append({"text":word.word.strip(),"start_ms":a,"end_ms":b,
                             "model_probability":round(float(word.probability),4)})
            results.append({
                "index":len(results),"start_ms":start,"end_ms":end,
                "text":text,"avg_logprob":round(float(seg.avg_logprob),4),
                "no_speech_prob":round(float(seg.no_speech_prob),4),
                "source_timecode_status":"model_proposal_not_reviewed_video_source_alignment",
                "word_time_candidates":words,
                "speaker_identity":None,
                "human_original_audio_reviewed":False
            })
        matches=compare_turns(p,results)
    obj={
      "schema":"night-court-s01e01-full-source-review-asr-proposals/1",
      "episode_id":"S01E01",
      "original_video_sha256":SOURCE_VIDEO_SHA,
      "original_english_srt_sha256":SOURCE_SRT_SHA,
      "source_video_sample_window_ms":[START_MS,END_MS],
      "decoded_original_audio_duration_ms":actual_duration_ms,
      "decoded_audio_wav_sha256":wavsha,
      "model":"faster-whisper tiny.en",
      "faster_whisper_version":importlib.metadata.version("faster-whisper"),
      "model_result_count":len(results),
      "asr_segments":results,
      "original_source_caption_turns":11,
      "turn_to_asr_overlap_proposals":matches,
      "human_listened_to_complete_source_window":False,
      "original_caption_words_independently_verified":False,
      "original_subtitle_sync_and_video_edition_verified":False,
      "speaker_character_diarization_verified":False,
      "vocal_inflection_or_emotion_verified":False,
      "production_scene_certified":False,
      "original_video_or_audio_or_weights_in_artifact":False,
      "limitations":[
        "Original C19 and C27 are fully inside new model sample, unlike prior 60–90s research excerpt.",
        "Model-reported source times are rough hypotheses, not human-verified word or video synchronization.",
        "C19/C22 caption typography can include multiple speakers within one source timestamp interval.",
        "Sitcom music, sound effects and laughter may cause hallucinations or voice segment mistakes.",
        "No actor, character, sarcasm, anger, emphasis or scene completeness can be certified by this ASR."
      ]
    }
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n","utf-8")
    print(f"Generated {len(results)} original-cut tiny.en hypotheses and 11 pending cue comparisons, no script acceptance")

def run_ftp(output):
    p,m=original_packet()
    item=candidate()
    if (item["basename"]!=m["source_video_filename_candidate"]
        or item["size_bytes"]!=m["source_video_size_bytes_candidate"]):
        raise ValueError("Historical FTP source identity changed")
    password=os.getenv("FTP_PASSWORD")
    if not password:raise ValueError("FTP access restricted to trusted source runner")
    with tempfile.TemporaryDirectory(prefix="night-court-complete-original-asr-") as tmp:
        original=Path(tmp)/item["basename"]
        ftp=connect(os.getenv("FTP_HOST","wood.seedhost.eu"),
                    os.getenv("FTP_USER","ianseeds"),password,"ftp")
        try:source_sha=retrieve(ftp,item,original)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        if source_sha!=SOURCE_VIDEO_SHA:raise ValueError("Source FTP AVI bytes changed")
        analyze(original,output)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ftp",action="store_true")
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    if not a.ftp:ap.error("Trusted original AVI source job only")
    run_ftp(a.output)

if __name__=="__main__":
    main()
