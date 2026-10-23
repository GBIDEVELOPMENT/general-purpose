#!/usr/bin/env python3
"""Deterministic acoustic measurements on local 16-bit mono PCM WAV.

No ASR, pitch, speaker identity or emotion inference. No network calls.
Use source timestamps only after caption-to-media alignment is verified.
"""
import argparse, array, hashlib, json, math, struct, sys, wave
from pathlib import Path

def analyse(path, start_ms, end_ms, episode, source_id):
    if not path.is_file() or path.stat().st_size > 300_000_000:
        raise ValueError("WAV missing or exceeds 300MB; bound media derivatives")
    with wave.open(str(path), "rb") as wav:
        channels, width, rate, frames = wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getnframes()
        if channels != 1 or width != 2 or rate not in (16000, 48000):
            raise ValueError("Expected mono PCM16 WAV at 16000 or 48000 Hz")
        if start_ms < 0 or end_ms <= start_ms or end_ms-start_ms>30000:
            raise ValueError("Select a bounded positive interval <=30s")
        begin, stop = round(start_ms*rate/1000), round(end_ms*rate/1000)
        if stop>frames: raise ValueError("Interval exceeds WAV duration")
        wav.setpos(begin)
        payload=wav.readframes(stop-begin)
    samples=array.array("h")
    samples.frombytes(payload)
    if sys.byteorder=="big":samples.byteswap()
    if not samples:raise ValueError("No samples")
    rms=math.sqrt(sum(float(v)*v for v in samples)/len(samples))/32768
    peak=max(abs(int(v)) for v in samples)/32768
    # 20 ms windows, relative to digital full scale. This is mix activity, not speaker VAD.
    size=max(1,rate//50)
    windows=[]
    for i in range(0,len(samples),size):
        window=samples[i:i+size]
        e=math.sqrt(sum(float(x)*x for x in window)/len(window))/32768
        windows.append(e)
    threshold=10**(-40/20)
    activity=sum(v>threshold for v in windows)/len(windows)
    return {
        "schema":"night-court-vocal-acoustic-baseline/1",
        "episode_id":episode, "source_cue_or_window_id":source_id,
        "wav_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
        "segment_pcm_sha256":hashlib.sha256(payload).hexdigest(),
        "start_ms":start_ms,"end_ms":end_ms,
        "sample_rate_hz":rate,"channels":channels,
        "features":{
            "rms_dbfs":round(20*math.log10(max(rms,1e-12)),2),
            "peak_dbfs":round(20*math.log10(max(peak,1e-12)),2),
            "mix_activity_fraction_above_minus_40_dbfs":round(activity,4),
            "f0_median_hz":None,"emotion_label":None,"speaker_id":None},
        "status":"unreviewed_mix_level_metrics_only",
        "limitations":["audience_laughter_music_and_mixed_speakers_contaminate_features",
                       "not_a_voice_activity_detector",
                       "not_pitch_or_emotion_recognition",
                       "not_source_edition_or_caption_alignment_verification"]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--wav",type=Path,required=True)
    p.add_argument("--episode",required=True)
    p.add_argument("--source-id",required=True)
    p.add_argument("--start-ms",type=int,required=True)
    p.add_argument("--end-ms",type=int,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    if not __import__("re").fullmatch(r"S(?:0[1-9])E(?:0[1-9]|1\d|2[0-4])",a.episode):
        raise ValueError("Invalid original-series episode ID")
    result=analyse(a.wav,a.start_ms,a.end_ms,a.episode,a.source_id)
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(text,encoding="utf-8")
    else:print(text,end="")
if __name__=="__main__":main()
