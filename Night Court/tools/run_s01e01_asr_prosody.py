#!/usr/bin/env python3
"""Exploratory real S01E01 source-audio ASR & pitch; never speaker/emotion truth.

Only trusted fixed 60–90s original-media excerpt. Downloads an explicitly
named public tiny.en Whisper model to temporary ephemeral runner cache.
Returns small provenance-linked text JSON, no WAV/video/model weights.
"""
import argparse, hashlib, importlib.metadata, json, re, subprocess, tempfile, wave
from difflib import SequenceMatcher
from pathlib import Path
from build_s01e01_scene_evidence import EXPECTED_SHA,SRT_SHA,CAPTION_DIR,digest,select_cues
from measure_vocal_prosody_optional import process as prosody

START=60
DURATION=30
MODEL="tiny.en"
def normalized(s):
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]"," ",s.casefold())).strip()

def propose_alignment(segments,cues):
    out=[]
    for seg in segments:
        sample=normalized(seg["text"])
        options=[]
        for cue in cues:
            similarity=SequenceMatcher(None,sample,normalized(cue["text"])).ratio()
            options.append((similarity,cue))
        value,best=max(options,key=lambda pair:pair[0])
        out.append({
            "asr_segment_index":seg["index"],
            "candidate_caption_cue":best["cue"] if value>=0.30 else None,
            "text_similarity_heuristic":round(value,4),
            "suggested_offset_ms":round(seg["start_ms"]-best["start_ms"]) if value>=0.55 else None,
            "status":"automated_heuristic_not_verified",
            "caution":"Caption and model segment boundaries differ; a text match does not prove exact sync."
        })
    return out

def run(media,output):
    if digest(media)!=EXPECTED_SHA:raise ValueError("Not the approved S01E01 original AVI")
    if digest(CAPTION_DIR/"original.srt")!=SRT_SHA:raise ValueError("Original SRT changed")
    if output.exists():raise ValueError("Refuse overwrite")
    captions=[json.loads(line) for line in (CAPTION_DIR/"segments.jsonl").read_text("utf-8").splitlines() if line.strip()]
    cues=select_cues(captions)
    with tempfile.TemporaryDirectory(prefix="nc-s01e01-asr-") as tmp:
        wav=Path(tmp)/"source-60-90.wav"
        subprocess.run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error",
                        "-ss",str(START),"-i",str(media),"-t",str(DURATION),
                        "-map","0:a:0","-vn","-ac","1","-ar","16000",
                        "-c:a","pcm_s16le","-y",str(wav)],
                       check=True,timeout=90,capture_output=True)
        with wave.open(str(wav),"rb") as f:
            audio_ms=round(f.getnframes()*1000/f.getframerate())
        if not 29000<=audio_ms<=30050:raise ValueError("30s excerpt failed")
        audio_sha=digest(wav)
        from faster_whisper import WhisperModel
        model=WhisperModel(MODEL,device="cpu",compute_type="int8",
                           download_root=str(Path(tmp)/"model-cache"))
        segments,info=model.transcribe(str(wav),language="en",beam_size=3,
                     word_timestamps=True,vad_filter=False,
                     condition_on_previous_text=False)
        recognized=[]
        for i,seg in enumerate(segments):
            recognized.append({
                "index":i,"start_ms":round(START*1000+seg.start*1000),
                "end_ms":round(START*1000+seg.end*1000),
                "text":seg.text.strip(),
                "log_probability":round(float(seg.avg_logprob),4),
                "no_speech_prob":round(float(seg.no_speech_prob),4),
                "word_candidates":[{"word":w.word.strip(),
                    "start_ms":round(START*1000+w.start*1000),
                    "end_ms":round(START*1000+w.end*1000),
                    "model_probability":round(float(w.probability),4)}
                    for w in (seg.words or [])]
            })
        acoustic=[]
        for start,end in ((0,6000),(6000,12000),(12000,18000),(18000,24000),(24000,30000)):
            p=prosody(wav,start,end)
            acoustic.append({
                "source_video_interval_ms":[START*1000+start,START*1000+end],
                "f0_yin_median_hz":p["f0_yin_median_hz"],
                "f0_yin_tenth_percentile_hz":p["f0_yin_tenth_percentile_hz"],
                "f0_yin_ninetieth_percentile_hz":p["f0_yin_ninetieth_percentile_hz"],
                "pitch_reliability_note":p["pitch_reliability_note"],
                "egemaps_v02_functionals":p["egemaps_v02_functionals"]
            })
    report={
        "schema":"night-court-s01e01-asr-prosody/1",
        "source_media_sha256":EXPECTED_SHA,"dialogue_source_sha256":SRT_SHA,
        "audio_wav_sha256":audio_sha,"source_window_ms":[60000,90000],
        "asr_engine":"faster-whisper","asr_model":MODEL,
        "faster_whisper_version":importlib.metadata.version("faster-whisper"),
        "asr_hypothesis_only":True,
        "asr_segments":recognized,
        "alignment_candidates":propose_alignment(recognized,cues),
        "source_caption_cues":[{"cue":x["cue"],"start_ms":x["start_ms"],
                                 "end_ms":x["end_ms"]} for x in cues],
        "acoustic_feature_engine":"librosa YIN + openSMILE eGeMAPSv02",
        "acoustic_mixed_audio_windows":acoustic,
        "voice_identity_verified":False,
        "source_caption_alignment_verified":False,
        "emotion_interpretation_verified":False,
        "all_model_outputs_need_audio_review":True,
        "rights":"owner-directed private research, no public audio/video distribution",
        "retained_media_audio_or_model_weights":False
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n","utf-8")
    print("S01E01 exploratory 30s ASR/prosody complete: "+str(len(recognized))+" candidate ASR segments; no AV verification claimed")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--media",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    run(args.media,args.output)
if __name__=="__main__":main()
