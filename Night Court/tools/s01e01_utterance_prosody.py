#!/usr/bin/env python3
"""Bounded per-ASR-turn mixed-track acoustic extraction for S01E01 60–90s.

YIN F0 and signal measurements are *mixed soundtrack* candidates, not
speaker-isolated prosody, emotional state, or a new source transcript.
"""
from __future__ import annotations
import argparse, ftplib, hashlib, json, math, os, subprocess, tempfile
from pathlib import Path
from pilot_ftp_video_acoustics import candidate,retrieve
from ftp_research_intake import connect

import numpy as np
import librosa
import soundfile as sf

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"seasons"/"S01"/"S01E01"/"derived"/"scene-review-v1"/"asr-prosody-hypotheses.json"
SOURCE_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SRT_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
WINDOW=[60000,90000]

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def load_source():
    obj=json.loads(SOURCE.read_text("utf-8"))
    if (obj["source_media_sha256"]!=SOURCE_SHA or
        obj["dialogue_source_sha256"]!=SRT_SHA or
        obj["source_window_ms"]!=WINDOW or
        obj["asr_model"]!="tiny.en" or not obj["asr_hypothesis_only"] or
        len(obj["asr_segments"])!=10):
        raise ValueError("Unexpected ASR source, model provenance or media edition")
    indices=[x["index"] for x in obj["asr_segments"]]
    if indices!=list(range(10)):raise ValueError("Unexpected segment identity")
    mapping={}
    for entry in obj["alignment_candidates"]:
        k=entry["asr_segment_index"]
        if k in mapping or k not in indices:raise ValueError("Duplicated ASR cue hint")
        mapping[k]=entry["candidate_caption_cue"]
    if len(mapping)!=10:raise ValueError("Missing ASR source cue hints")
    for seg in obj["asr_segments"]:
        if not(60000<=seg["start_ms"]<seg["end_ms"]<=90000):
            raise ValueError("ASR candidate out of 60–90s window")
    return obj,mapping

def features(signal,sample_rate):
    duration=len(signal)/sample_rate
    if duration<.25 or duration>5:
        raise ValueError("Only .25–5s hypothesized turns are supported")
    signal=np.asarray(signal,dtype=np.float32)
    rms=float(np.sqrt(np.mean(signal**2)))
    peak=float(np.max(np.abs(signal)))
    # These are mixed-soundtrack metrics; neither amplitude nor f0 is
    # representative of a speaker until separated, identified and reviewed.
    rate_db=20*math.log10(max(rms,1e-9))
    pitch=np.asarray(librosa.yin(signal,sr=sample_rate,
        fmin=65,fmax=550,frame_length=2048,hop_length=256),dtype=np.float64)
    frame_rms=np.asarray(librosa.feature.rms(y=signal,frame_length=2048,
        hop_length=256,center=True)[0],dtype=np.float64)
    frames=min(len(pitch),len(frame_rms))
    # Gate synthetic F0 guesses produced on very quiet frames. Still not VAD.
    valid=pitch[:frames][(frame_rms[:frames]>.012)&np.isfinite(pitch[:frames])&
        (pitch[:frames]>=65)&(pitch[:frames]<=550)]
    result={
      "rms_dbfs":round(rate_db,2),"peak_dbfs":round(20*math.log10(max(peak,1e-9)),2),
      "mix_pitch_median_hz":round(float(np.median(valid)),2) if len(valid) else None,
      "mix_pitch_p10_hz":round(float(np.percentile(valid,10)),2) if len(valid) else None,
      "mix_pitch_p90_hz":round(float(np.percentile(valid,90)),2) if len(valid) else None,
      "mix_pitch_frames_passing_energy_gate":int(len(valid)),
      "mix_pitch_frame_count":int(frames),
      "mix_pitch_first_to_last_change_semitones":None,
      "pitch_reliability":"unreviewed_sitcom_audio_mix_non_voice_noise_and_overlapping_speakers_possible",
      "acoustic_duration_ms":round(duration*1000),
    }
    if len(valid)>=10:
        width=max(2,len(valid)//5)
        early=float(np.median(valid[:width]))
        late=float(np.median(valid[-width:]))
        result["mix_pitch_first_to_last_change_semitones"]=round(
            12*math.log2(late/early),2)
    if duration<.7:
        result["pitch_reliability"]="too_short_for_trustworthy_delivery_label_or_stable_voice_baseline"
    return result

def generate(video,output):
    if output.exists():raise ValueError("Refuse to overwrite")
    if not video.is_file() or sha(video)!=SOURCE_SHA:raise ValueError("Original S01E01 AVI SHA mismatch")
    src,mapping=load_source()
    with tempfile.TemporaryDirectory(prefix="night-court-per-turn-") as temp:
        wav=Path(temp)/"s01e01-mono-16k.wav"
        subprocess.run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error",
            "-ss","60","-i",str(video),"-t","30","-map","0:a:0",
            "-ac","1","-ar","16000","-c:a","pcm_s16le","-y",str(wav)],
            check=True,capture_output=True,timeout=110)
        y,sr=sf.read(str(wav),dtype="float32",always_2d=False)
        if sr!=16000 or not 29.9<=len(y)/sr<=30.05:raise ValueError("Unexpected PCM duration")
        entries=[]
        for seg in src["asr_segments"]:
            start=seg["start_ms"]-60000;end=seg["end_ms"]-60000
            signal=y[round(start*sr/1000):round(end*sr/1000)]
            entry={"asr_segment_index":seg["index"],
                "caption_cue_hint":mapping[seg["index"]],
                "asr_source_audio_interval_ms":[seg["start_ms"],seg["end_ms"]],
                "model_word_timing_source":"faster-whisper_tiny.en_unverified_word_timestamps",
                "speech_utterance_identity":None,
                "acoustics":features(signal,sr),
                "speaker_isolated":False,
                "delivery_interpretation":None,
                "emotion_interpretation":None,
                "source_text_unchanged":True}
            entries.append(entry)
        pcm_sha=sha(wav)
    report={
        "schema":"night-court-s01e01-utterance-mix-prosody/1",
        "episode_id":"S01E01","source_media_sha256":SOURCE_SHA,
        "source_caption_sha256":SRT_SHA,
        "asr_evidence":"scene-review-v1/asr-prosody-hypotheses.json",
        "asr_model":"faster-whisper tiny.en","asr_segments":len(entries),
        "source_window_ms":WINDOW,"audio_wav_sha256":pcm_sha,
        "extractors":{"librosa":librosa.__version__,"soundfile":sf.__version__,
                      "numpy":np.__version__},
        "audio_source_persistent_in_repo":False,
        "utterance_prosody_hypotheses":entries,
        "source_edition_aligned_verified":False,
        "speaker_diarized_or_identified":False,
        "pitch_from_isolated_voice":False,
        "emotion_or_character_tone_inferred":False,
        "quality_limitations":["YIN_generates_F0_even_for_non_voice_so_energy_gating_is_only_a_heuristic",
          "audience_laughter_music_effects_and_speaker_overlap_contaminate_pitch",
          "short_segments_have_unstable_pitch_baselines",
          "ASR_times_are_model_candidates_not_manual_word_or_edition_alignment"],
        "review_status":"real_audio_measurements_unreviewed"
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+"\n","utf-8")
    print(f"Measured {len(entries)} real S01E01 source-mix ASR-timed candidate utterances; no speakers or emotions assigned")

def from_ftp(output):
    item=candidate()
    pwd=os.environ.get("FTP_PASSWORD")
    if not pwd:raise ValueError("Existing FTP_PASSWORD secret required")
    with tempfile.TemporaryDirectory(prefix="nc-owner-utterance-") as t:
        media=Path(t)/item["basename"]
        ftp=connect(os.environ.get("FTP_HOST","wood.seedhost.eu"),
           os.environ.get("FTP_USER","ianseeds"),pwd,"ftp")
        try:received=retrieve(ftp,item,media)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        if received!=SOURCE_SHA:raise ValueError("FTP source differs from previously verified hash")
        generate(media,output)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ftp",action="store_true")
    p.add_argument("--media",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.ftp==bool(args.media):p.error("Exactly one of --ftp or --media is required")
    if args.ftp:from_ftp(args.output)
    else:generate(args.media,args.output)

if __name__=="__main__":main()
