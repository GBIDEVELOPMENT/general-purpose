#!/usr/bin/env python3
"""Preserve exact-SHA original S01E01 36s ASR hypothesis without granting truth."""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"seasons/S01/S01E01/derived"
WORK=BASE/"editorial-review-v1/acceptance-worklist.json"
OUT=BASE/"scene-review-v4/asr-full-cut-v1"
ORIGINAL_SRT=ROOT/"seasons/S01/S01E01/dialogue/versions/s01-internal-dvdrip-xvid-sprinter-english--aa9f77600cd9f2b6/segments.jsonl"
AVI="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SRT="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
ASR_JSON_SHA="277d3d473cb9b51f7df250849f3863754456fe8e32ef348a0d19acfeff965259"
START,END=56912,93074
EXPECTED_UNMATCHED_SEGMENT=11

def validate(d):
    work=json.loads(WORK.read_text("utf-8"))
    if (work["source_video_sha256"]!=AVI
        or work["source_caption_sha256"]!=SRT
        or len(work["voice_review_tasks"])!=11):
        raise ValueError("Original caption turn source changed")
    if (d.get("schema")!="night-court-s01e01-full-source-review-asr-proposals/1"
        or d.get("episode_id")!="S01E01"
        or d.get("original_video_sha256")!=AVI
        or d.get("original_english_srt_sha256")!=SRT
        or d.get("source_video_sample_window_ms")!=[START,END]
        or d.get("decoded_original_audio_duration_ms")!=36162
        or d.get("model")!="faster-whisper tiny.en"
        or d.get("faster_whisper_version")!="1.2.1"
        or d.get("model_result_count")!=12
        or d.get("original_source_caption_turns")!=11):
        raise ValueError("Imported model evidence does not match exact original source")
    for key in (
        "human_listened_to_complete_source_window","original_caption_words_independently_verified",
        "original_subtitle_sync_and_video_edition_verified","speaker_character_diarization_verified",
        "vocal_inflection_or_emotion_verified","production_scene_certified",
        "original_video_or_audio_or_weights_in_artifact"):
        if d.get(key) is not False:
            raise ValueError("Model inference cannot certify sound, actor, script or source sync")
    if not re.fullmatch("[0-9a-f]{64}",d.get("decoded_audio_wav_sha256","")):
        raise ValueError("Unverifiable temporary audio source fingerprint")
    segs=d.get("asr_segments")
    if not isinstance(segs,list) or len(segs)!=12:
        raise ValueError("Missing original audio model segment proposal")
    word_count=0
    for i,s in enumerate(segs):
        if (set(s)!={"index","start_ms","end_ms","text","avg_logprob","no_speech_prob",
                     "source_timecode_status","word_time_candidates",
                     "speaker_identity","human_original_audio_reviewed"}
            or s["index"]!=i or not START<=s["start_ms"]<s["end_ms"]<=END
            or not isinstance(s["text"],str) or not s["text"].strip()
            or s["source_timecode_status"]!="model_proposal_not_reviewed_video_source_alignment"
            or s["speaker_identity"] is not None
            or s["human_original_audio_reviewed"] is not False):
            raise ValueError("Unexpected original-cut ASR proposition structure")
        words=s["word_time_candidates"]
        if not isinstance(words,list) or len(words)>250:
            raise ValueError("Unbounded model word proposals")
        for w in words:
            if (set(w)!={"text","start_ms","end_ms","model_probability"}
                or not s["start_ms"]<=w["start_ms"]<w["end_ms"]<=s["end_ms"]
                or not w["text"].strip()
                or not 0<=w["model_probability"]<=1):
                raise ValueError("ASR word lacks bounded original WAV hypothesis")
            word_count+=1
    if word_count!=60:
        raise ValueError("Incomplete original-cut 60 word hypotheses")
    matches=d.get("turn_to_asr_overlap_proposals")
    if not isinstance(matches,list) or len(matches)!=11:
        raise ValueError("Missing source caption candidate comparisons")
    source={x["task_id"]:x for x in work["voice_review_tasks"]}
    matched=set()
    seen=set()
    for item in matches:
        id=item.get("task_id")
        if id not in source or id in seen:
            raise ValueError("Duplicated/unrecognized source caption task")
        seen.add(id)
        actual=source[id]
        ix=item["candidate_asr_segment_index"]
        if (item["original_source_caption_interval_ms"]!=actual["source_caption_interval_ms"]
            or item["exact_source_text_preserved"]!=actual["original_dialogue"]
            or item["source_cue"]!=actual["source_cue"]
            or type(ix) is not int or not 0<=ix<len(segs)
            or not .35<=item["candidate_similarity_score"]<=1
            or item["ASR_segment_to_source_text_matching"]!="lexical_and_overlap_proposal_only"
            or item["source_word_fidelity_independently_listened"] is not False
            or item["source_word_timings_verified"] is not False
            or item["speaking_character_verified"] is not False):
            raise ValueError("Original caption text or conservative ASR review contract changed")
        matched.add(ix)
    if len(matched)!=11 or set(range(12))-matched!={EXPECTED_UNMATCHED_SEGMENT}:
        raise ValueError("Model-unmatched source segment not preserved")
    # The final model segment overlaps the following original SRT C28,
    # which continues BEYOND the sampled AVI ending at 93.074s.
    all_cues=[json.loads(x) for x in ORIGINAL_SRT.read_text("utf-8").splitlines() if x.strip()]
    c28=next((c for c in all_cues if c["cue"]==28),None)
    if c28 is None or c28["start_ms"]!=92379 or c28["end_ms"]!=94108:
        raise ValueError("Original next-caption cue identity unexpectedly changed")
    if not segs[11]["start_ms"]<END<c28["end_ms"]:
        raise ValueError("The unreviewed final ASR segment no longer overlaps a clipped next cue")
    return {"candidate_segments":len(segs),"candidate_words":word_count,
            "matched_original_C19_C27_speaking_turns":len(matches),
            "one_model_segment_overlap_with_clipped_next_C28":True,
            "original_audio_listened_or_words_verified":False,
            "production_screenplay_accepted":False}

def preserve(path):
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=ASR_JSON_SHA:
        raise ValueError("Unrecognized original-source Whisper JSON artifact digest")
    report=json.loads(raw)
    state=validate(report)
    if OUT.exists():
        target=OUT/"asr-proposals.json"
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=ASR_JSON_SHA:
            raise ValueError("Existing original source ASR edition was modified")
        print("Already preserved exact original-cut ASR hypotheses; no overwrite")
        return
    OUT.mkdir(parents=True)
    (OUT/"asr-proposals.json").write_bytes(raw)
    lines=[
       "# S01E01 complete source AVI 36.162s ASR: editorial listening priority",
       "",
       "Original video SHA-256: `"+AVI+"`",
       "Original English SRT SHA-256: `"+SRT+"`",
       "Trusted source run: https://github.com/gamesbyian/general-purpose/actions/runs/40067972923",
       "Original bounded source interval: **00:56.912–01:33.074**.",
       "Numeric original mixed-TV-audio and video-frame evidence are preserved separately.",
       "",
       "Twelve **model-proposed** audio segments and sixty word-time candidates were recovered. All eleven original caption-turn tasks C19–C27 have candidate lexical overlap, including the previously clipped first and last turns. Lexical similarity and model-timed spoken words are hypotheses, not listened-to source truth.",
       "",
       "| Original source review task | tiny.en segment index | Lexical similarity (heuristic only) | Original subtitle words accepted? |",
       "|---|---:|---:|---|"
    ]
    for item in report["turn_to_asr_overlap_proposals"]:
        lines.append(f"| {item['task_id']} | {item['candidate_asr_segment_index']} | {item['candidate_similarity_score']:.4f} | No |")
    lines+= [
       "",
       "**Important new mismatch at the excerpt edge:** a twelfth tiny.en segment is timed 01:32.412–01:33.052 (model's hypothesis). The next original SRT cue C28 begins 01:32.379 and ends 01:34.108, **outside this sample**. Its original subtitle wording is different from the model's proposal. This could be source edition mismatch, transcription error, mixing, or truncated context. Do not rewrite C28 or accept a new word without listening to the original source beyond 01:34.108.",
       "",
       "Independent follow-through: review original C19 and C27 with sound/mouth correspondence and compare C22's two voices, rare C24 comic vocabulary, C25/C26 short answers, and the C28 out-of-window margin. The C28 discrepancy requires a **separate longer source sample** before reliable conclusion.",
       "",
       "**All 17 S01E01 editorial review decisions and all 193 full-episode screenplay publication checks remain pending.** The original AVI/SRT and all human acceptance records were not changed.",
       ""
    ]
    (OUT/"review-of-model-differences.md").write_text("\n".join(lines),"utf-8")
    print(f"Imported {state['candidate_segments']} source-cut ASR proposals with no speaker/word acceptance; next C28 spans outside sample")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input",type=Path)
    a=p.parse_args()
    preserve(a.input)

if __name__=="__main__":
    main()
