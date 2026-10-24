#!/usr/bin/env python3
"""S01E01 timeline: original captions, sampled actions, and scored edits.

This is an editorial review agenda, not reviewed screenplay acceptance.
Source evidence is SHA reconciled; model scores and mixed soundtrack energy
must never become voice, emotion, shot-cut or word-time truth automatically.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"seasons/S01/S01E01/derived"
WORK=BASE/"editorial-review-v1/acceptance-worklist.json"
CUT=BASE/"editorial-review-v1/review-cut-manifest.json"
ENERGY=BASE/"audio-energy-v1/energy-envelope.json"
SHOTS=BASE/"shot-change-pts-v1/scene-candidates.json"
VISUAL=BASE/"visual-review-v3/expanded-sampled-observations.json"
OUTPUT=BASE/"editorial-review-v2/source-playback-agenda.json"
AVI="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SRT="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
WINDOW=[56912,93074]

def load(path):
    return json.loads(path.read_text("utf-8"))

def build():
    work,cut,energy,shots,visual=map(load,(WORK,CUT,ENERGY,SHOTS,VISUAL))
    if (work["source_video_sha256"]!=AVI
        or work["source_caption_sha256"]!=SRT
        or cut["source_video_sha256"]!=AVI
        or cut["source_caption_sha256"]!=SRT
        or energy["original_video_sha256"]!=AVI
        or energy["original_source_srt_sha256"]!=SRT
        or shots["source_original_video_sha256"]!=AVI
        or shots["source_original_caption_sha256"]!=SRT
        or visual["source_original_video_sha256"]!=AVI
        or visual["source_original_caption_sha256"]!=SRT):
        raise ValueError("Original AVI/SRT source fingerprint conflict")
    if (len(work["voice_review_tasks"])!=11 or len(work["visual_review_tasks"])!=6
        or len(cut["tasks"])!=17
        or cut["continuous_review_windows"][0]["start_ms"]!=WINDOW[0]
        or cut["continuous_review_windows"][0]["end_ms"]!=WINDOW[1]
        or energy["source_review_window_ms"]!=WINDOW
        or len(energy["caption_turn_mixed_audio"])!=11
        or len(energy["level_bins"])!=362
        or shots["source_window_ms"]!=WINDOW
        or len(shots["candidate_shot_changes"])!=7
        or len(visual["observations"])!=6):
        raise ValueError("Source review evidence layer unexpectedly incomplete")
    for field in ("human_listened_original_audio","original_audio_to_caption_alignment_verified",
                  "speaker_identity_verified","vocal_delivery_or_emotion_verified",
                  "episode_screenplay_complete"):
        if energy.get(field) is not False:
            raise ValueError("Mixed soundtrack data is not independently accepted audio truth")
    if shots["scene_boundaries_verified"] is not False:
        raise ValueError("Machine scene-score candidates are not verified cuts")
    if visual["independent_continuous_video_acceptances"]!=0:
        raise ValueError("Sampled frames cannot certify full-motion video review")
    source_review_ids={x["task_id"] for x in cut["tasks"]}
    levels={x["source_task_id"]:x for x in energy["caption_turn_mixed_audio"]}
    points=shots["candidate_shot_changes"]
    rows=[]
    for category,items,timefield in (
        ("caption_turn",work["voice_review_tasks"],"source_caption_interval_ms"),
        ("sampled_visual_action",work["visual_review_tasks"],"source_interval_ms")
    ):
        for item in items:
            key=item["task_id"]
            if key not in source_review_ids:raise ValueError("Missing original source task")
            a,b=item[timefield]
            if not WINDOW[0]<=a<b<=WINDOW[1]:raise ValueError("Original cue/action outside source review window")
            related=[
              {"original_stream_pts_candidate_ms":p["original_stream_pts_candidate_ms"],
               "ffmpeg_scene_score":p["ffmpeg_scene_score"],
               "interpretation":"image_difference_only_not_verified_camera_cut"}
              for p in points
              if a-1000<=p["original_stream_pts_candidate_ms"]<=b+1000
            ]
            row={
              "task_id":key,"kind":category,
              "source_interval_ms":[a,b],
              "suggested_original_video_playback_ms":[max(WINDOW[0],a-1000),min(WINDOW[1],b+1000)],
              "adjacent_machine_image_change_candidates":related,
              "independent_original_audio_or_video_review_conducted":False,
              "review_state":"pending",
              "named_character_or_expressive_delivery_verified":False
            }
            if category=="caption_turn":
                loudness=levels.get(key)
                if not loudness or loudness["original_source_caption_interval_ms"]!=[a,b]:
                    raise ValueError("Original source cue and mixed soundtrack summary disagree")
                row.update({
                  "source_caption_text_untouched":item["original_dialogue"],
                  "review_priority":item["priority_score_for_editor_only"],
                  "caption_review_flags":item["review_flags"],
                  "mixed_soundtrack_level_only":{
                    "rms_median_dbfs":loudness["mixed_soundtrack_rms_median_dbfs"],
                    "peak_max_dbfs":loudness["mixed_soundtrack_peak_max_dbfs"],
                    "speech_presence_cannot_be_inferred":True
                  },
                  "review_goal":"Original soundtrack listening: source text, overlap, word timing, source AVI edition, and actual performed voice; never infer from mixture level"
                })
            else:
                row.update({
                  "original_sampled_action_note":item["observation"],
                  "source_frame_digests":[f["sha256"] for f in item["supporting_source_frames"]],
                  "review_goal":"Original continuous-video viewing: identify actual edit, physical action, timing and reactions without assigning speech from still frames"
                })
            rows.append(row)
    if len(rows)!=17 or len({t["task_id"] for t in rows})!=17:
        raise ValueError("Duplicate or missing original source editorial task")
    for ix,p in enumerate(points,1):
        ms=p["original_stream_pts_candidate_ms"]
        if not WINDOW[0]<ms<WINDOW[1]:raise ValueError("Image candidate outside original cut")
        rows.append({
            "task_id":f"S01E01:VIDEO-PTS-{ix:02d}",
            "kind":"unverified_machine_image_change",
            "source_interval_ms":[ms,ms],
            "suggested_original_video_playback_ms":[max(WINDOW[0],ms-1000),min(WINDOW[1],ms+1000)],
            "ffmpeg_scene_score":p["ffmpeg_scene_score"],
            "review_goal":"Watch original continuous AVI around this frame; decide edit vs gesture/flash/dissolve; reject score as cut probability",
            "independent_original_audio_or_video_review_conducted":False,
            "review_state":"pending",
            "named_character_or_expressive_delivery_verified":False
        })
    rows.sort(key=lambda x:(x["source_interval_ms"][0],
                            0 if x["kind"]=="unverified_machine_image_change" else
                            1 if x["kind"]=="sampled_visual_action" else 2,x["task_id"]))
    return {
      "schema":"night-court-s01e01-editorial-playback-agenda/1",
      "episode_id":"S01E01",
      "source_video_sha256":AVI,
      "original_timed_SRT_sha256":SRT,
      "original_avi_window_ms":WINDOW,
      "original_caption_turn_review_tasks":11,
      "original_visual_stage_review_tasks":6,
      "extra_machine_transition_review_prompts":7,
      "total_chronological_review_entries":24,
      "all_original_editorial_tasks_still_unaccepted":True,
      "total_full_episode_screenplays_verified":0,
      "epistemic_limits":"The original TV mix RMS is not an isolated voice. FFmpeg scores and sampled frames are not accepted edits or continuous actions. This is a review navigation agenda, not a verified script.",
      "chronological_review_entries":rows
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--write",action="store_true")
    a=parser.parse_args()
    result=build()
    if a.write:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True)
        OUTPUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n","utf-8")
        print("S01E01: 24 agenda events, 17 actual pending review tasks, zero accepted source media interpretations")
    else:
        print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
