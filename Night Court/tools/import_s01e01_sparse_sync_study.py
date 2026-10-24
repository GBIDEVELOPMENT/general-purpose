#!/usr/bin/env python3
"""Retain source-hash-verified five-window S01E01 ASR cut-drift *hypotheses*.

The AVI+SRT are immutable. No window, caption, speaker or episode is marked
complete from lexical matching without independent audiovisual examination.
"""
import argparse, json, re, shutil
from pathlib import Path
from s01e01_sparse_asr_drift_study import WINDOWS,sources,caption_candidates,compare_windows

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"seasons"/"S01"/"S01E01"/"derived"/"source-sync-review-v1"
MEDIA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SUB="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"

def validate(path):
    if not path.is_file() or path.stat().st_size>300_000:
        raise ValueError("Missing or oversized bounded drift JSON")
    x=json.loads(path.read_text("utf-8"))
    if (x.get("schema")!="night-court-s01e01-multisite-asr-drift/1" or
        x.get("episode_id")!="S01E01" or x.get("original_media_sha256")!=MEDIA or
        x.get("original_caption_sha256")!=SUB or
        x.get("ASR_model")!="faster-whisper tiny.en" or
        x.get("source_video_duration_ms")!=1448256 or
        x.get("original_caption_times_independently_verified") is not False or
        x.get("source_edition_audio_sync_verified") is not False or
        x.get("audiovisual_episode_completeness_verified") is not False or
        x.get("identifiable_speakers_or_expressive_emotions_claimed") is not False or
        x.get("media_wav_and_model_weights_retained") is not False):
        raise ValueError("Wrong source, model or unsupported AV confidence claim")
    allcues=sources()
    windows=x.get("windows",[])
    if len(windows)!=len(WINDOWS):raise ValueError("Incomplete source sample plan")
    recounted=[]
    for entry,(start,end) in zip(windows,WINDOWS):
        if entry["source_window_ms"]!=[start*1000,end*1000]:
            raise ValueError("Noncanonical audio sample times")
        if not re.fullmatch(r"[0-9a-f]{64}",entry["source_audio_sha256"]):
            raise ValueError("No decoded WAV provenance")
        cues=caption_candidates(allcues,start,end)
        validids=[q["cue"] for q in cues]
        if entry["expected_source_caption_cues"]!=validids or entry["source_cues_in_window"]!=len(cues):
            raise ValueError("Missing/changed immutable caption cues")
        segments=entry["asr_segments"]
        links=entry["alignment_candidates"]
        if not isinstance(segments,list) or len(segments)>60 or len(links)!=len(segments):
            raise ValueError("Unbounded/missing model transcript evidence")
        for i,(seg,link) in enumerate(zip(segments,links)):
            if (seg["index"]!=i or
                not start*1000<=seg["start_ms"]<=seg["end_ms"]<=end*1000+100 or
                len(seg["text"])>500 or
                (link is not None and (link["asr_segment_index"]!=i or
                    link["review_state"]!="heuristic_text_match_not_verified_audio" or
                    link["source_caption_cue"] not in validids+[None]))):
                raise ValueError("ASR segment or source cue evidence mismatch")
        if entry["source_caption_alignment_status"]!="unverified_candidate_only" or entry["scene_and_speaker_identity_verified"]:
            raise ValueError("AV verification overclaimed")
        recounted.append({k:v for k,v in entry.items()})
    recalculated=compare_windows(recounted)
    summary=x.get("drift_hypothesis_summary",{})
    for field in ("qualified_windows_with_2plus_lexical_anchors",
                  "spread_between_window_median_start_differences_ms",
                  "global_drift_verified","global_video_to_subtitle_offset_verified"):
        if summary.get(field)!=recalculated[field]:
            raise ValueError("Reported source-to-caption drift statistics are inconsistent")
    return x

def write(path):
    if DEST.exists():raise ValueError("Refuse overwrite prior sync sample edition")
    report=validate(path)
    DEST.mkdir(parents=True)
    shutil.copyfile(path,DEST/"s01e01-sparse-asr-drift.json")
    lines=["# S01E01 five-window source video / subtitle drift review",
          "",
          "**Model-proposed start time differences only, not an AV-synced edition certificate.**",
          "",
          "| Source AVI interval | Original SRT cues | ASR speech candidates | Strong matching anchors | Median candidate start difference |",
          "|---|---:|---:|---:|---:|"]
    for w in report["windows"]:
        a,b=w["source_window_ms"]
        med=w.get("strong_lexical_start_delta_median_ms")
        val=f"{med} ms" if med is not None else "No strong match"
        lines.append(f'| {a/60000:.2f}–{b/60000:.2f} min | '
          f'{w["source_cues_in_window"]} | {len(w["asr_segments"])} | '
          f'{w["strong_lexical_anchor_count"]} | {val} |')
    spread=report["drift_hypothesis_summary"]["spread_between_window_median_start_differences_ms"]
    lines+=["",f"Spread between qualifying window medians: **{spread if spread is not None else 'not estimable'} ms**.",
         "",
         "A subtitle cue can cover multiple voices/utterances, and this method compares",
         "the beginning of a Whisper ASR segment with the start of the closest caption.",
         "This is not a calibrated global sync offset, and five sparse windows cannot",
         "establish that all dialogue/scene action is preserved across the source video.",
         "Human listening and/or constrained original-text alignment must resolve all",
         "suspicious or missing windows before promoting source words to script timecodes.",
         "",
         "The original caption, source video and all model weights remain outside the",
         "derived evidence artifact, with source SHA identity preserved.",
         ""]
    (DEST/"s01e01-sparse-asr-drift-review.md").write_text("\n".join(lines),"utf-8")
    print("Preserved five original-source pilot windows; drift remains model hypothesis, not verified")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("source",type=Path)
    write(p.parse_args().source)
