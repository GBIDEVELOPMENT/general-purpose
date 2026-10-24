#!/usr/bin/env python3
"""Render first original S09E19 evidence-linked but unaccepted scene passage.

Preserves original 347 untimed source paragraphs. Proposed positions come
from independent 25s ASR lexical matching, NOT the source caption itself.
Stage observations come from sampled source frames, not inferred dialogue.
"""
from __future__ import annotations
import json
from pathlib import Path
from s09e19_untimed_video_anchor_pilot import sources,TXT_SHA

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"seasons"/"S09"/"S09E19"/"derived"
OUT=BASE/"scene-review-v1"
AVI_SHA="51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649"
SOURCE=BASE/"source-timing-review-v1"/"sparse-source-paragraph-candidates.json"
VISUAL=BASE/"visual-review-v1"/"visual-source-review.json"
FRAME_INDEX=BASE/"visual-review-v1"/"frame-source-index.json"

def clock(ms):
    return f"{ms//60000:02}:{(ms%60000)/1000:06.3f}"

def build():
    full=json.loads(SOURCE.read_text("utf-8"))
    visual=json.loads(VISUAL.read_text("utf-8"))
    frames=json.loads(FRAME_INDEX.read_text("utf-8"))
    paragraphs=sources()
    if not (full["schema"]=="night-court-s09e19-untimed-source-av-anchor/1"
        and full["source_video_sha256"]==visual["source_media_sha256"]==
             frames["source_original_avi_sha256"]==AVI_SHA
        and full["original_untimed_transcript_sha256"]==
             visual["original_untimed_text_sha256"]==
             frames["original_untimed_text_sha256"]==TXT_SHA
        and full["original_paragraphs"]==347
        and full["distinct_high_lexical_match_candidates_total"]==15
        and visual["frames_hash_verified"]==100
        and frames["sample_count"]==100
        and len(visual["scene_observations"])==6
        and not full["original_source_cue_times_introduced"]
        and not visual["voice_and_character_identities_verified"]
        and not visual["actual_source_utterance_timecodes_verified"]):
        raise ValueError("S09E19 source/AV provenance, evidence count or unknown-speaker status changed")
    selected=[w for w in full["windows"] if w["source_window_ms"]==[900000,925000]]
    if len(selected)!=1 or selected[0]["distinct_high_lexical_match_candidates"]!=5:
        raise ValueError("The selected visual 25s excerpt lacks five known source candidates")
    events=[]
    for m in selected[0]["text_alignment_candidates"]:
        span=m["source_paragraph_candidate"]
        if not span:continue
        start,end=span["first"],span["last"]
        if not 1<=start<=end<=347:raise ValueError("Invalid original paragraph locator")
        original=[paragraphs[i-1] for i in range(start,end+1)]
        if any(x["start_ms"] is not None or x["end_ms"] is not None for x in original):
            raise ValueError("Original untimed dialogue was given fake timestamps")
        interval=m["source_audio_interval_ms"]
        if not 900000<=interval[0]<interval[1]<=925000:
            raise ValueError("ASR-time candidate outside actual source sound sample")
        if m["decision"]!="distinct_high_lexical_match_UNVERIFIED":
            raise ValueError("Non-unique model lexical candidates promoted")
        events.append({
           "source_kind":"original_untimed_source_paragraph_candidate",
           "video_candidate_interval_ms":interval,
           "source_first_paragraph":start,"source_last_paragraph":end,
           "original_source_text":" ".join(x["text"] for x in original),
           "asr_segment_index":m["asr_segment_index"],
           "model_similarity_heuristic":m["best_lexical_similarity"],
           "model_runner_up_similarity":m["runner_up_similarity_nonoverlapping"],
           "candidate_speaking_character":None,
           "original_source_paragraph_has_no_timecodes":True,
           "human_audio_dialogue_verified":False,
           "human_video_lip_synced":False
        })
    for item in visual["scene_observations"]:
        refs=item["source_frame_evidence"]
        if len(refs)!=len(item["frame_numbers"]):
            raise ValueError("Broken frame evidence locator")
        for x in refs:
            idx=x["frame_number"]-1
            frame=frames["frames"][idx]
            if (x["sha256"]!=frame["sha256"] or
                x["approx_source_time_ms"]!=frame["approx_source_time_ms"]):
                raise ValueError("Referenced frame SHA/time mismatch")
        events.append({
           "source_kind":"sampled_original_video_observation",
           "video_candidate_interval_ms":item["interval_ms"],
           "visual_id":item["id"],"description":item["description"],
           "frame_evidence":[{"sha256":x["sha256"],"file":x["file"],
                   "nominal_time_ms":x["approx_source_time_ms"]} for x in refs],
           "observation_class":item["evidence_kind"],
           "scene_action_continuous_video_verified":False,
           "character_identity":None,"speaker_identity":None
        })
    events.sort(key=lambda e:(e["video_candidate_interval_ms"][0],
           0 if e["source_kind"]=="sampled_original_video_observation" else 1))
    dialogue=[x for x in events if x["source_kind"]=="original_untimed_source_paragraph_candidate"]
    visual_rows=[x for x in events if x["source_kind"]=="sampled_original_video_observation"]
    if len(dialogue)!=5 or len(visual_rows)!=6:
        raise ValueError("Expected five candidate source paragraphs and six visual observations")
    doc={
       "schema":"night-court-s09e19-source-evidence-scene/1",
       "episode_id":"S09E19","source_media_sha256":AVI_SHA,
       "source_original_untimed_text_sha256":TXT_SHA,
       "observed_video_excerpt_ms":[900000,925000],
       "setting_heading":"INT. SHARED INTERIOR WITH COUNTER AND TABLES – ACTUAL VENUE UNVERIFIED",
       "source_paragraph_count":347,"source_paragraph_dialogue_candidates":5,
       "reviewed_sampled_video_observations":6,
       "source_audio_model":"faster-whisper tiny.en",
       "events":events,
       "original_source_paragraphs_still_untimed":True,
       "independent_audio_word_verification":False,
       "independent_speaker_character_attribution":False,
       "continuous_video_performance_actions_verified":False,
       "actual_full_scene_boundaries_verified":False,
       "original_episode_audiovisual_complete":False,
       "publication_status":"source_linked_private_research_excerpt_not_accepted_screenplay"
    }
    lines=[
      "# S09E19 | first integrated dialogue-and-stage-evidence excerpt",
      "",
      "## INT. INTERIOR WITH COUNTER AND TABLES – LOCATION AND TIME OF DAY UNVERIFIED",
      "",
      "**Source-video interval 15:00–15:25. Private research draft only.**",
      "",
      "This sequence shows people at a counter and two seated individuals in later",
      "sampled camera views. It has no independently verified named characters,",
      "voice performances, physical-joke intentions or original script dialogue timings.",
      "",
      "> The original source text consists of UNTIMED HTML-derived paragraphs.",
      "> Audio-time markers below are independent ASR matching PROPOSALS,",
      "> not original SRT timestamps. Image notes describe sampled states.",
      ""
    ]
    for e in events:
        first,last=e["video_candidate_interval_ms"]
        if e["source_kind"]=="sampled_original_video_observation":
            files=", ".join(x["file"].rsplit("/",1)[-1] for x in e["frame_evidence"])
            lines+= [
               f"*[{clock(first)}–{clock(last)} | {e['visual_id']} | sampled visual state]*",
               "*"+e["description"]+"*",
               f"Frame evidence: {files}.",""
            ]
        else:
            lines+= [
              f"**[{clock(first)}–{clock(last)} ASR PROPOSAL | ORIGINAL P{e['source_first_paragraph']:03d}–P{e['source_last_paragraph']:03d} | SPEAKER UNVERIFIED]**",
              e["original_source_text"],
              f"*Lexical proposal similarity {e['model_similarity_heuristic']:.3f}; not listened to or synchronized to a visible speaker.*",
              ""
            ]
    lines+= [
      "## Outstanding production acceptance",
      "",
      "This research excerpt has not established its actual screen scene boundaries.",
      "A 4fps sample does not prove the precise onset of physical action, nor",
      "that a person shown near a subtitle's proposed time spoke that phrase.",
      "Independent listening, character/voice corroboration, visual review of",
      "continuous video and complete episode cut verification are still required.",
      "No changes have been made to the original 347 untimed source paragraphs.",
      "",
      "Original AVI SHA-256: "+AVI_SHA,
      "Original untimed text SHA-256: "+TXT_SHA,""
    ]
    return doc,"\n".join(lines)

def main():
    if OUT.exists():raise ValueError("Refuse to overwrite earlier script research edition")
    doc,script=build()
    OUT.mkdir(parents=True)
    (OUT/"source-linked-scene.json").write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n","utf-8")
    (OUT/"source-linked-scene.md").write_text(script,"utf-8")
    print("S09E19 v1 scene: 5 tentative original text paragraphs, 6 reviewed sampled states, zero invented source timing/speaker identities")

if __name__=="__main__":main()
