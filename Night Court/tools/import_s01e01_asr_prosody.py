#!/usr/bin/env python3
"""Preflight one S01E01 alternative-ASR & mix prosody JSON from trusted CI.

Does not certify alignment, pitch identity, emotion or source completeness.
"""
from pathlib import Path
import json,re,sys,hashlib,shutil

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"seasons/S01/S01E01/derived/scene-review-v1"/"asr-prosody-hypotheses.json"
SOURCE="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SUBTITLE="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"

def validate(d):
    if d.get("schema")!="night-court-s01e01-asr-prosody/1":raise ValueError("Unknown evidence schema")
    if d.get("source_media_sha256")!=SOURCE or d.get("dialogue_source_sha256")!=SUBTITLE:
        raise ValueError("Wrong source media or subtitle edition")
    if d.get("source_window_ms")!=[60000,90000] or d.get("asr_model")!="tiny.en":
        raise ValueError("Unexpected inference interval or model")
    for flag in ("asr_hypothesis_only","all_model_outputs_need_audio_review"):
        if d.get(flag) is not True:raise ValueError("Missing mandatory uncertainty flag")
    for flag in ("voice_identity_verified","source_caption_alignment_verified",
                 "emotion_interpretation_verified","retained_media_audio_or_model_weights"):
        if d.get(flag) is not False:raise ValueError("Overclaimed inference evidence")
    segments=d.get("asr_segments",[])
    if not isinstance(segments,list) or len(segments)>100:raise ValueError("Unbounded ASR segments")
    for x in segments:
        if not (60000<=x["start_ms"]<=x["end_ms"]<=90100):
            raise ValueError("ASR text outside approved evidence window")
        if len(x.get("text",""))>500:
            raise ValueError("Unexpectedly long ASR segment")
        for word in x.get("word_candidates",[]):
            if not 60000<=word["start_ms"]<=word["end_ms"]<=90100:
                raise ValueError("Word timestamp outside approved window")
    if len(d.get("acoustic_mixed_audio_windows",[]))!=5:
        raise ValueError("Need all five mixed-audio feature windows")
    if len(d.get("alignment_candidates",[]))!=len(segments):
        raise ValueError("Missing alignment candidates")
    for result in d["alignment_candidates"]:
        if result["status"]!="automated_heuristic_not_verified":
            raise ValueError("Inappropriately asserted verified caption offset")
    if d.get("source_caption_cues"):
        seen={x["cue"] for x in d["source_caption_cues"]}
        if not set(range(19,28)).issubset(seen):raise ValueError("Missing source cues")
    return len(segments)

def main(source):
    d=json.loads(source.read_text("utf-8"))
    count=validate(d)
    if DEST.exists() and DEST.read_bytes()!=source.read_bytes():
        raise ValueError("Do not overwrite alternative inference witness")
    DEST.parent.mkdir(parents=True,exist_ok=True)
    if not DEST.exists():shutil.copyfile(source,DEST)
    print("Retained "+str(count)+" exploratory S01E01 ASR segments with five guarded mix-level prosody windows")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: import_s01e01_asr_prosody.py SOURCE_JSON")
    main(Path(sys.argv[1]))
