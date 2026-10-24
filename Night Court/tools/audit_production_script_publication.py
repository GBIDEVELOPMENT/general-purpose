#!/usr/bin/env python3
"""Enforce no false production-script promotion across the original 193 episodes.

This is a release gate, not a review performed by this script. Never treat
"source present", automatic captions, model confidence or frame extraction as
verified speakers, stage directions, episode edition or AV completeness.
"""
import json
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"catalog"/"av-script-reconstruction-queue.json"
SOURCES=ROOT/"catalog"/"source-script-scaffold-coverage.json"
OUT=ROOT/"catalog"/"production-script-publication-gates.json"
REQUIRED=[
 "video_edition_identification",
 "full_episode_subtitle_audio_alignment",
 "speaker_and_character_voice_identity",
 "observed_scene_boundaries_and_locations",
 "physical_stage_directions_and_reactions",
 "vocal_prosody_and_delivery",
 "full_episode_independent_av_QA"
]

def assess():
    board=json.loads(INPUT.read_text("utf-8"))
    scaffolds=json.loads(SOURCES.read_text("utf-8"))
    if board["original_episode_records"]!=193 or board["source_reading_scripts_ready"]!=193:
        raise ValueError("Expected all 193 original episode sources")
    if len(board["episodes"])!=193 or len(scaffolds["episodes"])!=193:
        raise ValueError("Unreconciled episode record counts")
    original={x["episode_id"]:x for x in scaffolds["episodes"]}
    if len(original)!=193:raise ValueError("Repeated source reading episode")
    entries=[]
    for item in board["episodes"]:
        ep=item["episode_id"]
        src=original.get(ep)
        if src is None:raise ValueError("No source reading witness for "+ep)
        md=item["source_metadata"]
        if src["source_sha256"]!=md["source_sha256"] or src["derived_path"]!=md["source_only_script"]:
            raise ValueError("Script/witness source hash or path mismatch: "+ep)
        if not (ROOT/src["derived_path"]).is_file():
            raise ValueError("Missing source reading script: "+ep)
        stage=item["stage_acceptance"]
        if set(stage)!=set(REQUIRED+["held_caption_witness","source_reading_script",
                                    "source_turns_and_roster","provisional_scene_participants"]):
            raise ValueError("Unexpected/missing stage acceptance gate: "+ep)
        if stage["held_caption_witness"]!="complete_source_present":
            raise ValueError("Archive source unexpectedly missing")
        if stage["source_reading_script"]!="complete_not_av_verified":
            raise ValueError("Scaffold improperly claimed production acceptance")
        if stage["full_episode_independent_av_QA"]!="not_verified":
            raise ValueError("Independent audiovisual sign-off changed without reviewed release evidence")
        # This audit can accept NO verified claims by inference. A future genuine
        # release requires a separate signed/independently-reviewed acceptance
        # manifest and a deliberate schema/policy revision.
        pending={field:stage[field] for field in REQUIRED}
        entries.append({
          "episode_id":ep,"source_sha256":src["source_sha256"],
          "reading_script":src["derived_path"],
          "source_cues":src["caption_cues"],
          "source_format":src["source_format"],
          "release_status":"BLOCKED_AWAITING_INDEPENDENT_AV_ACCEPTANCE",
          "required_review_gates":pending,
          "verified_production_script":False,
          "identity_or_emotion_inferred_from_model":False,
          "signed_independent_review":None
        })
    if len({x["episode_id"] for x in entries})!=193:
        raise ValueError("Duplicate episode publication gate")
    if board["episode_scripts_independently_av_verified"]!=0:
        raise ValueError("Top-level published state conflicts with per-episode unverified status")
    entries.sort(key=lambda x:x["episode_id"])
    return {
      "schema":"night-court-script-publication-gates/1",
      "scope":"original_1984_1992_only",
      "episodes_with_held_reading_scaffolds":193,
      "verified_full_episode_scripts":0,
      "blocked_full_episode_scripts":193,
      "blocked_reason":"no_independent_episode_complete_av_qa_signoff",
      "release_rule":"all gates require independent media-edition-matched evidence and reviewer decision; no model self-certification",
      "source_board_sha256":hashlib.sha256(INPUT.read_bytes()).hexdigest(),
      "source_scaffold_coverage_sha256":hashlib.sha256(SOURCES.read_bytes()).hexdigest(),
      "episodes":entries
    }

def main():
    payload=assess()
    data=json.dumps(payload,ensure_ascii=False,indent=2)+"\n"
    OUT.write_text(data,encoding="utf-8")
    print("Publication release gate:",len(payload["episodes"]),
          "reading scripts; zero independently accepted full-episode scripts")

if __name__=="__main__":main()
