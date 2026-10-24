#!/usr/bin/env python3
"""Owner-scope S09E19 five-window audiovisual timing pilot.

Acquire with FTP_SECRET ONLY in a credentialed job step. Analyze with no FTP
credentials in a later step. Retain ONLY compact source-hashed JSON, not media.
"""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, json, os, subprocess, tempfile, wave
from pathlib import Path
from match_s09e19_untimed_paragraphs import score_windows
from ftp_research_intake import connect
from pilot_ftp_video_acoustics import retrieve

ROOT=Path(__file__).resolve().parents[1]
EP=ROOT/"seasons"/"S09"/"S09E19"
EDITION="subtitle-cat-s09e19-original-caption-page-untime--659beb9c50fabdd1"
SOURCE=EP/"dialogue"/"versions"/EDITION
TXT_SHA="659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
FILENAME="Night Court - 9x19 - P.S. Do I Know You.avi"
REMOTE="/downloads/Night Court TVRip S1-S9/Night.Court.S09.DVDRip.DivX/"+FILENAME
BYTES=183377920
WINDOWS=((180,205),(405,430),(660,685),(900,925),(1200,1225))
SCHEMA="night-court-s09e19-untimed-source-av-anchor/1"

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def sources():
    m=json.loads((SOURCE/"manifest.json").read_text("utf-8"))
    if (m["episode_id"]!="S09E19" or m["format"]!="txt" or m["timecoded"] or
        m["cue_count"]!=347 or m["declared_complete"] or m["sha256"]!=TXT_SHA or
        digest(SOURCE/"original.txt")!=TXT_SHA):
        raise ValueError("Untimed original source identity/provenance mismatch")
    paragraphs=[json.loads(s) for s in (SOURCE/"segments.jsonl").read_text("utf-8").splitlines() if s.strip()]
    if len(paragraphs)!=347 or any(x.get("start_ms") is not None or x.get("end_ms") is not None
        or x["cue"]!=i+1 for i,x in enumerate(paragraphs)):
        raise ValueError("Original source paragraphs must remain untimed")
    return paragraphs

def exact_candidate():
    inv=json.loads((ROOT/"catalog/ftp-video-inventory-2026-10-23.json").read_text("utf-8"))
    hits=[x for x in inv["files"] if x["episode_id_from_filename"]=="S09E19"]
    if (inv["inventory_run_id"]!=40041061527 or len(hits)!=1
        or hits[0]["remote_path"]!=REMOTE or hits[0]["size_bytes"]!=BYTES
        or hits[0]["basename"]!=FILENAME):
        raise ValueError("Remote source differs from owner inventory; refuse broad search")
    return hits[0]

def run(args,timeout=120):
    return subprocess.run(args,check=True,capture_output=True,text=True,timeout=timeout)

def acquire(out):
    if out.exists():raise ValueError("Refuse to overwrite prior source windows")
    item=exact_candidate()
    sources()
    password=os.getenv("FTP_PASSWORD")
    if not password:raise ValueError("FTP_PASSWORD is needed only at acquisition")
    with tempfile.TemporaryDirectory(prefix="nc-s09e19-source-") as tmp:
        video=Path(tmp)/FILENAME
        ftp=connect(os.getenv("FTP_HOST","wood.seedhost.eu"),
            os.getenv("FTP_USER","ianseeds"),password,"ftp")
        try:
            actual_sha=retrieve(ftp,item,video)
        finally:
            import ftplib
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        probe=json.loads(run(["ffprobe","-v","error","-show_entries",
            "format=duration,size:stream=index,codec_type,codec_name,sample_rate,channels",
            "-of","json",str(video)],35).stdout)
        seconds=float(probe["format"]["duration"])
        if not 1320<=seconds<=1800 or max(end for _,end in WINDOWS)>seconds:
            raise ValueError("Unexpected S09E19 duration; do not invent transcript timing")
        if not any(x["codec_type"]=="audio" for x in probe["streams"]):
            raise ValueError("S09E19 candidate contains no sound")
        out.mkdir(parents=True)
        records=[]
        for start,end in WINDOWS:
            if end-start!=25:raise ValueError("Unexpected bounded sample")
            wav=out/f"source-{start}-{end}.wav"
            run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error",
                 "-ss",str(start),"-i",str(video),"-t","25","-map","0:a:0",
                 "-vn","-ac","1","-ar","16000","-c:a","pcm_s16le",
                 "-y",str(wav)],90)
            with wave.open(str(wav),"rb") as w:
                dur=w.getnframes()/w.getframerate()
                if w.getframerate()!=16000 or w.getnchannels()!=1 or not 24.90<=dur<=25.05:
                    raise ValueError("Decoded source sample invalid")
            records.append({"source_window_ms":[start*1000,end*1000],
                "source_wav_sha256":digest(wav),
                "local_file":wav.name})
        manifest={
          "schema":"night-court-s09e19-ephemeral-wav-manifest/1",
          "source_video_sha256":actual_sha,
          "source_video_size_bytes":video.stat().st_size,
          "source_duration_seconds":seconds,
          "source_streams":probe["streams"],
          "source_original_txt_sha256":TXT_SHA,
          "windows":records,
          "video_episode_identity_independently_verified":False,
          "original_text_complete_or_timecoded":False
        }
        (out/"ephemeral-source-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n","utf-8")
    print("S09E19 acquired 5 authorized 25s PCM windows; original AVI deleted; no media may be uploaded")

def analyze(folder,output):
    if output.exists():raise ValueError("Refuse to overwrite report")
    if os.getenv("FTP_PASSWORD"):
        raise ValueError("Run speech-model analysis in a separate step WITHOUT FTP_PASSWORD")
    paragraphs=sources()
    manifest=json.loads((folder/"ephemeral-source-manifest.json").read_text("utf-8"))
    if (manifest["schema"]!="night-court-s09e19-ephemeral-wav-manifest/1"
        or manifest["source_original_txt_sha256"]!=TXT_SHA
        or len(manifest["windows"])!=len(WINDOWS)
        or not all(isinstance(manifest[k],str) and len(manifest[k])==64
                for k in ("source_video_sha256","source_original_txt_sha256"))):
        raise ValueError("Unexpected ephemeral media manifest")
    for i,row in enumerate(manifest["windows"]):
        start,end=WINDOWS[i]
        if (row["source_window_ms"]!=[start*1000,end*1000]
            or row["local_file"]!=f"source-{start}-{end}.wav"
            or digest(folder/row["local_file"])!=row["source_wav_sha256"]):
            raise ValueError("Audio sample identity drifted during model setup")
    from faster_whisper import WhisperModel
    model=WhisperModel("tiny.en",device="cpu",compute_type="int8",cpu_threads=2)
    windows=[]
    for i,row in enumerate(manifest["windows"]):
        a,b=WINDOWS[i]
        segments,_=model.transcribe(str(folder/row["local_file"]),language="en",
            beam_size=3,word_timestamps=False,vad_filter=False,
            condition_on_previous_text=False)
        clips=[]
        for raw in segments:
            start=round(a*1000+raw.start*1000)
            end=round(a*1000+raw.end*1000)
            clamped_a=max(a*1000,start)
            clamped_b=min(b*1000,end)
            if clamped_a>=clamped_b:continue
            clips.append({
               "index":len(clips),"start_ms":clamped_a,"end_ms":clamped_b,
               "segment_boundary_clipped":clamped_a!=start or clamped_b!=end,
               "text":raw.text.strip(),
               "model_average_log_probability":round(float(raw.avg_logprob),4),
               "model_no_speech_probability":round(float(raw.no_speech_prob),4)
            })
        windows.append({"source_window_ms":[a*1000,b*1000],
            "source_audio_sha256":row["source_wav_sha256"],"asr_segments":clips})
    reviewed=score_windows(windows,paragraphs)
    ordered=[m["source_paragraph_candidate"]["first"] for w in reviewed
        for m in w["text_alignment_candidates"] if m["source_paragraph_candidate"]]
    source_monotonic=all(x<y for x,y in zip(ordered,ordered[1:]))
    report={
       "schema":SCHEMA,"episode_id":"S09E19",
       "source_video_sha256":manifest["source_video_sha256"],
       "source_video_size_bytes":manifest["source_video_size_bytes"],
       "source_duration_seconds":manifest["source_duration_seconds"],
       "original_untimed_transcript_sha256":TXT_SHA,
       "original_paragraphs":347,
       "model":"faster-whisper tiny.en",
       "faster_whisper_version":importlib.metadata.version("faster-whisper"),
       "windows":reviewed,
       "candidate_paragraphs_monotonic_across_windows":source_monotonic,
       "distinct_high_lexical_match_candidates_total":sum(
          w["distinct_high_lexical_match_candidates"] for w in reviewed),
       "segments_reviewed":sum(len(w["asr_segments"]) for w in reviewed),
       "original_source_cue_times_introduced":False,
       "original_transcript_modified":False,
       "all_347_paragraphs_time_aligned":False,
       "source_edition_audiovisually_verified":False,
       "words_speaker_and_emotion_verified":False,
       "all_audio_or_video_complete":False,
       "raw_source_media_wav_or_model_weights_retained_in_artifact":False,
       "limitations":[
         "Five sparse 25s audio windows do not verify full 24-minute source cut.",
         "Independent ASR can hallucinate dialogue; explicit lexical uniqueness required.",
         "A plausible matching source paragraph is not an original timecode.",
         "Laughter, effects and overlapping speech may destroy lexical match.",
         "The retained 347 HTML-derived paragraphs have no source cue timestamps.",
         "No source video content or speaker identity has been independently reviewed."
       ]
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n","utf-8")
    print("S09E19 sparse untimed source match:",report["segments_reviewed"],
          "ASR segments,",report["distinct_high_lexical_match_candidates_total"],
          "tentative unique lexical paragraph candidates. No source timecodes created.")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--acquire",action="store_true")
    p.add_argument("--analyze",action="store_true")
    p.add_argument("--scratch",required=True,type=Path)
    p.add_argument("--output",type=Path)
    opts=p.parse_args()
    if opts.acquire==opts.analyze:p.error("Choose exactly one processing phase")
    if opts.acquire:
        if opts.output:p.error("Acquisition never emits a report")
        acquire(opts.scratch)
    else:
        if not opts.output:p.error("Analysis requires --output")
        analyze(opts.scratch,opts.output)
