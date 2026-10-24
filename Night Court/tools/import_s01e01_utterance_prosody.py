#!/usr/bin/env python3
"""Preflight and retain the exact S01E01 ten-turn mixed prosody evidence.

No trained emotion model, no voice identity, no source audio, and no model
weights. The spoken time intervals are ASR candidates, not AV-certified.
"""
from __future__ import annotations
import hashlib,json,math,shutil,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"seasons"/"S01"/"S01E01"/"derived"/"scene-review-v1"/"asr-prosody-hypotheses.json"
DEST=ROOT/"seasons"/"S01"/"S01E01"/"derived"/"scene-review-v3"
SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SRT="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
RUN=40048178210
CAPTIONS=[19,20,21,22,22,23,24,25,26,27]

def validate(src):
    if src.stat().st_size>300_000:
        raise ValueError("Unexpectedly large compact prosody JSON")
    j=json.loads(src.read_text("utf-8"))
    if (j.get("schema")!="night-court-s01e01-utterance-mix-prosody/1"
        or j.get("episode_id")!="S01E01" or j.get("source_media_sha256")!=SHA
        or j.get("source_caption_sha256")!=SRT
        or j.get("source_window_ms")!=[60000,90000]
        or j.get("asr_segments")!=10 or j.get("asr_model")!="faster-whisper tiny.en"
        or j.get("audio_source_persistent_in_repo") is not False
        or j.get("source_edition_aligned_verified") is not False
        or j.get("speaker_diarized_or_identified") is not False
        or j.get("pitch_from_isolated_voice") is not False
        or j.get("emotion_or_character_tone_inferred") is not False):
        raise ValueError("Wrong source, unsupported claims or mismatched experiment")
    original=json.loads(SOURCE.read_text("utf-8"))
    if original.get("source_media_sha256")!=SHA:
        raise ValueError("Source ASR media fingerprint changed")
    if not isinstance(j.get("audio_wav_sha256"),str) or len(j["audio_wav_sha256"])!=64:
        raise ValueError("No original decoded WAV hash")
    xs=j["utterance_prosody_hypotheses"]
    if len(xs)!=10:raise ValueError("Expected ten bounded candidate turns")
    for i,(obs,asr) in enumerate(zip(xs,original["asr_segments"])):
        if (obs["asr_segment_index"]!=i or obs["caption_cue_hint"]!=CAPTIONS[i]
            or obs["asr_source_audio_interval_ms"]!=[asr["start_ms"],asr["end_ms"]]
            or obs.get("speech_utterance_identity") is not None
            or obs.get("delivery_interpretation") is not None
            or obs.get("emotion_interpretation") is not None
            or obs.get("speaker_isolated") is not False):
            raise ValueError("Unverified voice, changed turn timing or altered cue")
        f=obs["acoustics"]
        if not -150<f["rms_dbfs"]<=0 or not -150<f["peak_dbfs"]<=0:
            raise ValueError("Digital amplitude is implausible")
        if f["mix_pitch_frame_count"]<f["mix_pitch_frames_passing_energy_gate"]:
            raise ValueError("Energy gating count impossible")
        for key in ("mix_pitch_median_hz","mix_pitch_p10_hz","mix_pitch_p90_hz"):
            if f[key] is not None and not 65<=f[key]<=550:
                raise ValueError("Pitch escaped bounded model range")
        if f["mix_pitch_first_to_last_change_semitones"] is not None and abs(f["mix_pitch_first_to_last_change_semitones"])>50:
            raise ValueError("Implausible pitch contour") # beyond 4 octaves is not useful
    return j

def main(path):
    if (DEST/"utterance-mix-prosody.json").exists():
        raise ValueError("Refuse to overwrite a prior evidence edition")
    obj=validate(path)
    DEST.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(path,DEST/"utterance-mix-prosody.json")
    out=[
      "# S01E01 01:00–01:30 | real utterance acoustic review",
      "",
      "Mixed-TV-soundtrack measurements anchored to **ASR candidate spans**,",
      "**not** isolated actor voices, verified caption timing or emotion.",
      "",
      "| ASR | Caption hint | Time | Mix RMS dBFS | Candidate F0 median | Pitch change (semitones) | Reliability caution |",
      "|---:|---|---|---:|---:|---:|---|"]
    for x in obj["utterance_prosody_hypotheses"]:
        a=x["acoustics"];ms=x["asr_source_audio_interval_ms"]
        med="unreliable / unavailable" if a["mix_pitch_median_hz"] is None else str(a["mix_pitch_median_hz"])
        change="unavailable" if a["mix_pitch_first_to_last_change_semitones"] is None else str(a["mix_pitch_first_to_last_change_semitones"])
        caution=("too short for trustworthy delivery" if "too_short" in a["pitch_reliability"]
                 else "large pitch jump: octave/mix artifact possible"
                 if a["mix_pitch_first_to_last_change_semitones"] is not None
                 and abs(a["mix_pitch_first_to_last_change_semitones"])>12
                 else "mixed, unreviewed source audio")
        out.append(
            f'| {x["asr_segment_index"]} | C{x["caption_cue_hint"]:04d} (candidate) | '
            f'{ms[0]/1000:.3f}–{ms[1]/1000:.3f}s | {a["rms_dbfs"]:.2f} | {med} | {change} | {caution} |')
    out.extend(["",
      "These measurements combine whatever speech, laugh-track, music and effects",
      "are present. Differences in pitch can arise from a changed speaker or",
      "non-speech contamination, not just a character's expressive inflection.",
      "Do not assign character identity or interpret anger, sarcasm, or embarrassment",
      "until an independent listener/voice review supports the annotation.",
      "",
      f"Source AVI SHA-256: {SHA}",
      f"Source SRT SHA-256: {SRT}",
      f"Trusted real-audio Actions run: #{RUN}.",
      "",
      "Independent AV completeness verified: **No**.",""])
    (DEST/"utterance-acoustic-review.md").write_text("\n".join(out),"utf-8")
    print("Retained ten source-verified ASR-span mix acoustic feature records; no speaker/emotion inference")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: import_s01e01_utterance_prosody.py ARTIFACT_JSON")
    main(Path(sys.argv[1]))
