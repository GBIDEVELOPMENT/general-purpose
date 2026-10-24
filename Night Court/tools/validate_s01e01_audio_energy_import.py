#!/usr/bin/env python3
"""Import strictly numeric real-source S01E01 TV-mix RMS/peak evidence, no audio.

Only the fixed owner-trusted successful run's exact JSON may be retained.
No PCM/WAV/AVI, spoken transcript, identifiable voice, or model weights.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"seasons/S01/S01E01/derived"
WORKLIST=BASE/"editorial-review-v1/acceptance-worklist.json"
DEST=BASE/"audio-energy-v1"
EXPECTED_SHA="1943f489cb29bdc4446984709e55866284c8aefcb53681e8f8cf4a252a54ad2a"
VIDEO_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SRT_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
START=56912
END=93074
N=362

def verify(data):
    q=json.loads(WORKLIST.read_text("utf-8"))
    if (q["source_video_sha256"]!=VIDEO_SHA
        or q["source_caption_sha256"]!=SRT_SHA
        or q["counts"]["source_speaking_turns"]!=11):
        raise ValueError("Original source editorial packet changed")
    if (data.get("schema")!="night-court-s01e01-mixed-soundtrack-envelope/1"
        or data.get("episode_id")!="S01E01"
        or data.get("original_video_sha256")!=VIDEO_SHA
        or data.get("original_source_srt_sha256")!=SRT_SHA
        or data.get("source_review_window_ms")!=[START,END]
        or data.get("nominal_decoded_time_origin_ms")!=START
        or data.get("decoded_sample_rate_hz")!=16000
        or data.get("sample_count")!=578592
        or data.get("duration_ms_derived_from_sample_count")!=36162
        or data.get("level_bin_width_ms")!=100
        or data.get("original_source_caption_turns")!=11):
        raise ValueError("Wrong original AVI, SRT or exact sample/time domain")
    abstain=("human_listened_original_audio","any_speech_words_verified",
             "speaker_identity_verified","vocal_delivery_or_emotion_verified",
             "original_audio_to_caption_alignment_verified",
             "episode_screenplay_complete","audio_PCM_or_AVI_exported")
    if any(data.get(x) is not False for x in abstain):
        raise ValueError("Mixed soundtrack measurements cannot claim speech or production acceptance")
    bins=data.get("level_bins")
    if not isinstance(bins,list) or len(bins)!=N:
        raise ValueError("Truncated or excessively long 100ms source bins")
    for i,b in enumerate(bins):
        if (set(b)!={"index","nominal_start_ms","nominal_end_ms","rms_dbfs","peak_dbfs"}
            or type(b["index"]) is not int or b["index"]!=i
            or b["nominal_start_ms"]!=START+i*100
            or b["nominal_end_ms"]!=min(END,START+(i+1)*100)
            or type(b["rms_dbfs"]) not in (float,int)
            or type(b["peak_dbfs"]) not in (float,int)
            or not -120<=b["rms_dbfs"]<=b["peak_dbfs"]<=0):
            raise ValueError("Audio level bin source index, time or signal range invalid")
    turns=data.get("caption_turn_mixed_audio")
    if not isinstance(turns,list) or len(turns)!=11:
        raise ValueError("Original 11 source-caption turn energy summaries missing")
    taskmap={t["task_id"]:t for t in q["voice_review_tasks"]}
    seen=set()
    for t in turns:
        id=t.get("source_task_id")
        if id not in taskmap or id in seen:
            raise ValueError("Unknown/duplicated original caption-turn level")
        seen.add(id)
        task=taskmap[id]
        a,z=task["source_caption_interval_ms"]
        window=[b for b in bins if b["nominal_end_ms"]>a and b["nominal_start_ms"]<z]
        if (t.get("original_source_caption_interval_ms")!=[a,z]
            or t.get("overlapping_mixed_audio_bin_count")!=len(window)
            or t.get("mixed_soundtrack_rms_median_dbfs")!=round(statistics.median(b["rms_dbfs"] for b in window),3)
            or t.get("mixed_soundtrack_peak_max_dbfs")!=max(b["peak_dbfs"] for b in window)):
            raise ValueError("Soundtrack level claim does not match actual source bins")
        for field in ("original_speech_present_verified","source_word_times_verified",
                      "speaker_or_delivery_verified"):
            if t.get(field) is not False:
                raise ValueError("Soundtrack energy cannot certify an original speaking turn")
    return len(bins),len(seen)

def import_file(source):
    raw=source.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA:
        raise ValueError("Artifact JSON differs from fixed original trusted source run")
    data=json.loads(raw)
    bin_count,turn_count=verify(data)
    if DEST.exists():
        old=DEST/"energy-envelope.json"
        memo=DEST/"energy-review.md"
        if (not old.is_file() or not memo.is_file() or
            hashlib.sha256(old.read_bytes()).hexdigest()!=EXPECTED_SHA):
            raise ValueError("Existing source-derived energy evidence is incomplete or changed")
        print("Exact original audio envelope already preserved; no overwrite attempted")
        return
    DEST.mkdir(parents=True)
    (DEST/"energy-envelope.json").write_bytes(raw)
    lines=[
        "# S01E01 | real original TV soundtrack amplitude review",
        "",
        "**Source AVI SHA-256:** "+VIDEO_SHA,
        "**Original source SRT SHA-256:** "+SRT_SHA,
        "**Source audio interval:** 00:56.912–01:33.074",
        "**Owner-trusted source run:** https://github.com/gamesbyian/general-purpose/actions/runs/40066968589",
        "**Artifact:** #12549956081, seven-day temporary; numeric JSON SHA-256 `"+EXPECTED_SHA+"`",
        "",
        "Measured 362 strictly source-time-indexed 100ms **mixed soundtrack** RMS/peak bins, representing 36.162s of decoded 16kHz mono original AVI audio. Original PCM and AVI were discarded; no raw media bytes or script acceptance are retained.",
        "",
        "| Original source turn | Caption source interval ms | Mixed RMS median dBFS | Mix peak max dBFS |",
        "|---|---|---:|---:|",
    ]
    for t in data["caption_turn_mixed_audio"]:
        a,b=t["original_source_caption_interval_ms"]
        lines.append(f"| {t['source_task_id']} | {a}–{b} | {t['mixed_soundtrack_rms_median_dbfs']:.3f} | {t['mixed_soundtrack_peak_max_dbfs']:.3f} |")
    lines.extend([
        "",
        "C19's two proposed speakers and C22's two proposed speakers **share original full-cue intervals**, so both inherit identical mixed-soundtrack level measurements. This is not vocal separation. The low C25/C26 median energy in some bins cannot establish an omitted/inaudible word, silence, voice identity or subtitle drift. The original source must be listened to.",
        "",
        "**Zero accepted audio-to-caption word times, isolated speakers, emotions, vocal delivery, stage actions or complete episode scripts.** Every level is a numeric original mixed soundtrack measurement, not speech truth.",
        ""
    ])
    (DEST/"energy-review.md").write_text("\n".join(lines),"utf-8")
    print(f"Source SHA verified: {bin_count} level samples; {turn_count} source turns; zero speech/voice/scene acceptance")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input",type=Path)
    args=p.parse_args()
    import_file(args.input)

if __name__=="__main__":
    main()
