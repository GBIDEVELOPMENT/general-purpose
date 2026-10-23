#!/usr/bin/env python3
"""Optional F0 and eGeMAPS analysis for one verified local mono PCM16 WAV span.

Requires separately installed vocal-requirements-acoustics.txt. Never infer
emotion or speaker identity. openSMILE licensing applies to downstream usage.
"""
import argparse, hashlib, json, math, wave
from pathlib import Path

def process(path, start_ms, end_ms):
    import librosa
    import numpy as np
    import opensmile
    import soundfile as sf
    if path.stat().st_size > 300_000_000:
        raise ValueError("Source file exceeds bounded analysis limit")
    if start_ms < 0 or end_ms <= start_ms or end_ms-start_ms > 30000:
        raise ValueError("Audio interval must be positive and <=30 s")
    with wave.open(str(path),"rb") as w:
        if w.getnchannels()!=1 or w.getsampwidth()!=2 or w.getframerate() not in (16000,48000):
            raise ValueError("Expected mono 16-bit PCM WAV, 16k or 48k")
        sr=w.getframerate()
        if end_ms > w.getnframes()/sr*1000:raise ValueError("Audio window past EOF")
    audio,rate=sf.read(str(path),dtype="float32",always_2d=False)
    selection=audio[round(start_ms*rate/1000):round(end_ms*rate/1000)]
    if len(selection)<int(.25*rate):raise ValueError("Need at least 250ms for acoustic analysis")
    # Silence, audience laughter and simultaneous speech can corrupt F0 extraction.
    if float(np.sqrt(np.mean(selection**2))) < 0.001:
        f0=[]
        reason="near_silence"
    else:
        pitch=librosa.yin(selection,fmin=65,fmax=650,sr=rate)
        f0=[float(x) for x in pitch if math.isfinite(float(x)) and 65<float(x)<650]
        reason="unreviewed_pitch_candidates_mix_contamination_possible"
    # ComParE/eGeMAPS features summarize the whole interval; not emotion labels.
    sm=opensmile.Smile(feature_set=opensmile.FeatureSet.eGeMAPSv02,
                      feature_level=opensmile.FeatureLevel.Functionals)
    vector=sm.process_signal(selection, rate).iloc[0].to_dict()
    clean={str(k):(round(float(v),5) if math.isfinite(float(v)) else None)
           for k,v in vector.items()}
    return {
       "schema":"night-court-prosody-optional/1",
       "source_wav_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
       "start_ms":start_ms,"end_ms":end_ms,
       "extractor_versions":{"librosa":librosa.__version__,"opensmile":opensmile.__version__,
                             "soundfile":sf.__version__},
       "f0_yin_median_hz":round(float(np.median(f0)),2) if f0 else None,
       "f0_yin_tenth_percentile_hz":round(float(np.percentile(f0,10)),2) if f0 else None,
       "f0_yin_ninetieth_percentile_hz":round(float(np.percentile(f0,90)),2) if f0 else None,
       "pitch_reliability_note":reason,
       "egemaps_v02_functionals":clean,
       "delivery_interpretation":None,"speaker_identity":None,
       "review_status":"machine_acoustic_measurements_unreviewed",
       "limitations":["YIN_pitch_is_not_speaker_separated",
                      "eGeMAPS_measures_the_television_mix_not_pure_character_speech",
                      "emotion_and_delivery_require_separate_review"]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--wav",required=True,type=Path)
    p.add_argument("--start-ms",required=True,type=int)
    p.add_argument("--end-ms",required=True,type=int)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=process(args.wav,args.start_ms,args.end_ms)
    data=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(data,encoding="utf-8")
    else:print(data,end="")
if __name__=="__main__":main()
