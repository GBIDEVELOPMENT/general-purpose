#!/usr/bin/env python3
"""Gate S01E01 integrated v4 reading scene against exact original subtitle and AVI evidence.

No rewriting of the 1984 original source dialogue, and NO promotion from
sampled images/FFmpeg scene scores to accepted acting or character voice.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EP=ROOT/"seasons/S01/S01E01/derived"
SCENE=EP/"scene-review-v3/scene-evidence-map.json"
VISUAL=EP/"visual-review-v3/expanded-sampled-observations.json"
CUTS=EP/"shot-change-pts-v1/scene-candidates.json"
EDITION=EP/"scene-review-v4/research-scene-evidence-v4.json"
SCRIPT=EP/"scene-review-v4/research-scene-script-v4.md"
EXPECTED_AVI="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
EXPECTED_SRT="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
CLOCK_RE=re.compile(r"^(?:\*\[|\*\*\[)(\d{2}):(\d{2})\.(\d{3})(?:–| \|)")

def clock(ms):
    return f"{ms//60000:02d}:{ms//1000%60:02d}.{ms%1000:03d}"

def validate(version=None,script=None):
    meta=version if version is not None else json.loads(EDITION.read_text("utf-8"))
    text=script if script is not None else SCRIPT.read_text("utf-8")
    v3=json.loads(SCENE.read_text("utf-8"))
    images=json.loads(VISUAL.read_text("utf-8"))
    pts=json.loads(CUTS.read_text("utf-8"))
    if any(s!=EXPECTED_AVI for s in (
       meta.get("source_media_sha256"),v3.get("source_media_sha256"),
       images.get("source_original_video_sha256"),pts.get("source_original_video_sha256")):
       raise ValueError("Episode v4 source AVI fingerprint is inconsistent")
    if any(s!=EXPECTED_SRT for s in (
       meta.get("source_original_srt_sha256"),v3.get("original_subtitle_sha256"),
       images.get("source_original_caption_sha256"),pts.get("source_original_caption_sha256")):
       raise ValueError("Episode v4 original SRT source fingerprint is inconsistent")
    if (meta.get("schema")!="night-court-integrated-evidence-script/4"
       or meta.get("episode_id")!="S01E01"
       or meta.get("original_source_video_review_window_ms")!=[56912,93074]
       or meta.get("original_caption_cues")!=9
       or meta.get("original_source_speaking_turns")!=11
       or meta.get("earlier_static_source_observations")!=5
       or meta.get("earlier_sampled_sequence_observations")!=6
       or meta.get("expanded_sampled_source_observations")!=6
       or meta.get("machine_image_change_candidates")!=7
       or meta.get("total_timeline_events")!=28
       or meta.get("research_script_status")!="SOURCE_LINKED_EDITION_NOT_INDEPENDENT_AV_ACCEPTANCE"):
       raise ValueError("Unexpected v4 source-script structure or scope")
    gates=[
       "timeline_includes_source_turns_from_original_untimed_transcript",
       "source_AVI_video_to_SRT_synchronization_verified",
       "speaker_and_character_identity_verified","continuous_stage_action_verified",
       "spoken_delivery_verified","complete_episode_production_screenplay_verified",
       "video_and_audio_source_bytes_in_repo"
    ]
    if any(meta.get(g) is not False for g in gates):
       raise ValueError("Research screenplay cannot self-certify audiovisual completion")
    cues=[e for e in v3["events"] if e["source_kind"]=="caption_turn"]
    original_static=[e for e in v3["events"] if e["source_kind"]=="reviewed_static_frame"]
    old_action=[e for e in v3["events"] if e["source_kind"]=="reviewed_sampled_sequence"]
    if not (len(cues)==11 and len(original_static)==5 and len(old_action)==6
         and len(images["observations"])==6 and len(pts["candidate_shot_changes"])==7):
       raise ValueError("Missing preserved source dialogue or real AVI images")
    lines=text.splitlines()
    for e in cues:
        tag=f"**[{clock(e['start_ms'])} | C{e['cue']:04d} source turn {e['source_turn_index']+1} | UNATTRIBUTED VOICE, AUDIO UNVERIFIED]**"
        if lines.count(tag)!=1 or lines.count(e["text"])!=1:
            raise ValueError("Missing/duplicated/rewritten original source caption turn")
        loc=lines.index(tag)
        if loc+1>=len(lines) or lines[loc+1]!=e["text"]:
            raise ValueError("Original dialogue was separated from exact source cue label")
    for row in original_static+old_action:
        if sum(" | "+row["id"]+" | " in ln for ln in lines)!=1:
            raise ValueError("Legacy image/physical action evidence lost from new scene")
    for row in images["observations"]:
        if sum(" | "+row["observation_id"]+" | " in ln for ln in lines)!=1:
            raise ValueError("Newly inspected source AVI frame evidence lost from new scene")
    for row in pts["candidate_shot_changes"]:
        if f"| {clock(row['original_stream_pts_candidate_ms'])} | {row['ffmpeg_scene_score']:.6f} | Requires original continuous-video inspection |" not in lines:
            raise ValueError("FFmpeg source cut-time proposal mislabeled or omitted")
    marks=[]
    for ln in lines:
        found=CLOCK_RE.search(ln)
        if found:
            mins,seconds,msec=map(int,found.groups())
            marks.append((mins*60+seconds)*1000+msec)
    if len(marks)!=28 or marks!=sorted(marks):
        raise ValueError("Provisional scene timeline order or event count changed")
    if (f"Original AVI SHA-256: `{EXPECTED_AVI}`" not in text
        or f"Original English SRT SHA-256: `{EXPECTED_SRT}`" not in text
        or "UNATTRIBUTED VOICE, AUDIO UNVERIFIED" not in text
        or "0/193" not in text):
        raise ValueError("Missing essential source edition or uncertainty annotations")
    return {
        "schema":"night-court-scene-v4-source-reconciliation/1",
        "original_dialogue_turns_preserved":len(cues),
        "source_frame_and_action_observations":len(original_static)+len(old_action)+len(images["observations"]),
        "raw_image_difference_candidates":len(pts["candidate_shot_changes"]),
        "integrated_timeline_events":len(marks),
        "original_caption_wording_preserved":True,
        "speaker_and_stage_acceptance_performed":False,
        "complete_original_episode_script_verified":False
    }

if __name__=="__main__":
    print(json.dumps(validate(),indent=2))
