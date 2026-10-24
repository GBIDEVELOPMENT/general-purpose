#!/usr/bin/env python3
"""Anonymous source-speech embedding similarity, never a character identifier.

Uses a pinned Apache-2 ECAPA model. Produces per-pair cosine similarities
ONLY, not raw speaker embeddings, biometric identities or unverified clusters.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import math
import tempfile
import wave

ROOT=Path(__file__).resolve().parents[1]
ASR=ROOT/"seasons/S01/S01E01/derived/scene-review-v1/asr-prosody-hypotheses.json"
MODEL="speechbrain/spkrec-ecapa-voxceleb"
REVISION="eac27266f68caa806381260bd44ace38b136c76a"
SOURCE_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SRT_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"

def allowed_segments():
    j=json.loads(ASR.read_text("utf-8"))
    if (j["source_media_sha256"]!=SOURCE_SHA or j["dialogue_source_sha256"]!=SRT_SHA
        or j["asr_model"]!="tiny.en" or j["source_window_ms"]!=[60000,90000]):
        raise ValueError("Unexpected media/ASR evidence source")
    result=[]
    for seg in j["asr_segments"]:
        duration=seg["end_ms"]-seg["start_ms"]
        if not 60000<=seg["start_ms"]<seg["end_ms"]<=90000:raise ValueError("ASR bounds drift")
        if duration>=1200:
            result.append({"asr_segment_index":seg["index"],
               "source_video_interval_ms":[seg["start_ms"],seg["end_ms"]],
               "candidate_audio_duration_ms":duration})
    if len(result)<4 or len(result)>10:raise ValueError("Unexpected candidate segment count")
    return result

def cosine(a,b):
    """No claim that similarity is calibrated same-speaker probability."""
    import numpy as np
    x=np.asarray(a,dtype=float).reshape(-1)
    y=np.asarray(b,dtype=float).reshape(-1)
    if x.size!=y.size or x.size<2 or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Invalid speaker similarity feature vectors")
    den=float(np.linalg.norm(x)*np.linalg.norm(y))
    if den<1e-9:raise ValueError("Degenerate speaker feature vector")
    return round(float(np.dot(x,y)/den),4)

def compare(embeddings):
    ids=sorted(embeddings)
    pairs=[]
    for i,one in enumerate(ids):
        for two in ids[i+1:]:
            pairs.append({
              "first_asr_segment_index":one,
              "second_asr_segment_index":two,
              "cosine_similarity_uncalibrated":cosine(embeddings[one],embeddings[two]),
              "same_character_or_actor_verified":False,
              "speaker_diarization_verified":False,
              "warning":"Short TV-mix utterances may include laughter, background music or multiple speakers"
            })
    return pairs

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--wav",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--model-cache",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError("Do not overwrite source voice comparison")
    audit=json.loads((a.wav.parent/"pcm-source-provenance.json").read_text("utf-8"))
    if audit["original_video_sha256"]!=SOURCE_SHA:
        raise ValueError("Unknown episode voice excerpt")
    if hashlib.sha256(a.wav.read_bytes()).hexdigest()!=audit["pcm_sha256"]:
        raise ValueError("Soundtrack PCM hash mismatch")
    import numpy as np
    import soundfile as sf
    import torch
    import speechbrain
    from speechbrain.inference.speaker import EncoderClassifier
    signal,sr=sf.read(str(a.wav),dtype="float32")
    if sr!=16000 or not 29.9<len(signal)/sr<30.1:
        raise ValueError("Expected fixed 30-second mono 16k WAV")
    model=EncoderClassifier.from_hparams(source=MODEL,revision=REVISION,
        savedir=str(a.model_cache),run_opts={"device":"cpu"})
    model.eval()
    candidates=allowed_segments()
    voices={}
    for seg in candidates:
        left,right=seg["source_video_interval_ms"]
        clip=signal[round((left-60000)*sr/1000):round((right-60000)*sr/1000)]
        if len(clip)<int(1.2*sr):
            raise ValueError("Cannot compute short-utterance voice embedding")
        with torch.inference_mode():
            vector=model.encode_batch(torch.tensor(clip,dtype=torch.float32).unsqueeze(0))
        flat=vector.detach().cpu().numpy().reshape(-1)
        if flat.size<64:raise ValueError("Bad model output dimensionality")
        voices[seg["asr_segment_index"]]=flat
    pairs=compare(voices)
    out={
       "schema":"night-court-s01e01-anonymous-voice-similarity/1",
       "episode_id":"S01E01","source_media_sha256":SOURCE_SHA,
       "source_caption_sha256":SRT_SHA,"source_pcm_sha256":audit["pcm_sha256"],
       "source_window_ms":[60000,90000],"sample_rate_hz":16000,
       "speaker_embedding_model":MODEL,"model_revision":REVISION,
       "license":"apache-2.0",
       "runtime_versions":{"speechbrain":speechbrain.__version__,
                           "torch":torch.__version__,"numpy":np.__version__},
       "eligible_source_spans":candidates,
       "excluded_spans":"ASR proposals shorter than 1200 ms or outside approved 30s evidence window",
       "pairwise_similarities":pairs,
       "raw_embeddings_persisted":False,
       "raw_audio_or_video_persisted":False,
       "known_speaker_labels":{},
       "speaker_identity_verified":False,
       "same_speaker_similarity_threshold_calibrated":False,
       "diarization_or_character_assignment_accepted":False,
       "scene_or_audio_editions_verified":False,
       "limitations":["TV mix and laugh-track alter embedding reliability",
                      "minimum duration chosen for research triage, not validation",
                      "cosine similarity is not an actor identity or calibrated likelihood",
                      "speaker turns and overlaps are ASR candidate boundaries only",
                      "full-video accuracy and performance inflection require independent listening"]
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+"\n","utf-8")
    print(f"Compared {len(candidates)} anonymous audio segments across {len(pairs)} uncalibrated voice-similarity pairs; no speaker names or stored embeddings")

if __name__=="__main__":main()
