#!/usr/bin/env python3
"""Guard exact original-AVI S01E01 visual edit proposals from false screenplay claims."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"seasons/S01/S01E01/derived"
RESULT=BASE/"shot-change-pts-v1/scene-candidates.json"
MANIFEST=BASE/"editorial-review-v1/review-cut-manifest.json"
OBSERVED_PTS=[59026,60928,68268,74107,76777,80948,82382]
OBSERVED_SCORES=[.306012,.143181,.138734,.277865,.261383,.140563,.140819]
SOURCE_AVI_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SOURCE_SRT_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"

def validate(data=None,manifest=None):
    r=data if data is not None else json.loads(RESULT.read_text("utf-8"))
    m=manifest if manifest is not None else json.loads(MANIFEST.read_text("utf-8"))
    if (r.get("schema")!="night-court-s01e01-avi-shot-change-candidates/1"
        or r.get("episode_id")!="S01E01"
        or r.get("source_original_video_sha256")!=SOURCE_AVI_SHA
        or r.get("source_original_caption_sha256")!=SOURCE_SRT_SHA
        or r.get("source_original_video_sha256")!=m.get("source_video_sha256")
        or r.get("source_original_caption_sha256")!=m.get("source_caption_sha256")
        or r.get("source_video_expected_size_bytes")!=m.get("source_video_size_bytes_candidate")
        or r.get("source_window_ms")!=[56912,93074]
        or [m["continuous_review_windows"][0]["start_ms"],
            m["continuous_review_windows"][0]["end_ms"]] != [56912,93074]):
        raise ValueError("Corrupted canonical S01E01 source/probe provenance")
    if (r.get("detector_threshold")!=.12
        or r.get("original_srt_source_turns_in_scope")!=11
        or r.get("sampled_visual_action_tasks_in_scope")!=6
        or r.get("candidate_count")!=7):
        raise ValueError("Unexpected scoped original AVI frame-rate detection run")
    rows=r.get("candidate_shot_changes")
    if not isinstance(rows,list) or len(rows)!=7:
        raise ValueError("Seven original decoded-frame candidates must be retained")
    for i,c in enumerate(rows):
        if (set(c)!={"selected_frame_index","original_stream_pts_candidate_ms",
                      "ffmpeg_scene_score","source_time_status"}
            or c["selected_frame_index"]!=i
            or c["original_stream_pts_candidate_ms"]!=OBSERVED_PTS[i]
            or c["ffmpeg_scene_score"]!=OBSERVED_SCORES[i]
            or c["source_time_status"]!="decoded_avi_presentation_timestamp_candidate_not_independently_verified_cut"):
            raise ValueError("Source-PST candidate bytes/time/score changed")
    for name in (
        "original_video_audio_or_frames_exported",
        "independent_human_video_review",
        "speaker_or_character_identity_verified",
        "continuous_stage_action_verified",
        "scene_boundaries_verified",
        "original_video_to_subtitle_alignment_verified",
        "production_script_accepted"
    ):
        if r.get(name) is not False:
            raise ValueError("Image difference heuristic cannot accept script, actor or sync")
    return {
        "source_video_sha_consistent":True,
        "source_SRT_sha_consistent":True,
        "original_frame_rate_candidate_count":len(rows),
        "absolute_candidate_PTS_ms":OBSERVED_PTS,
        "verified_edits_or_source_speakers":0,
        "production_script_verified":False
    }

if __name__=="__main__":
    print(json.dumps(validate(),indent=2))
