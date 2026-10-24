#!/usr/bin/env python3
"""One independently traceable, acceptance-gated AV production queue per episode.

Merge QA, source scripts, character/scene evidence preparation and FTP filename
candidates. Rank only existing source-review urgency; never promote inferred
scene candidates or subtitle presence to audiovisual acceptance.
"""
from __future__ import annotations
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/"catalog"
DEST=CAT/"av-script-reconstruction-queue.json"

def read(name):
    return json.loads((CAT/name).read_text("utf-8"))

def unique(rows,key):
    result={}
    for row in rows:
        identifier=row[key]
        if identifier in result:raise ValueError("Duplicate "+identifier)
        result[identifier]=row
    return result

def build():
    script=read("source-script-scaffold-coverage.json")
    qa=read("dialogue-qa-review-queue.json")
    scene=read("scene-participation-evidence.json")
    speakers=read("speaker-attribution-preparation.json")
    video=read("ftp-video-inventory-2026-10-23.json")
    if any(x!=193 for x in (script["episodes_with_source_scaffold"],qa["episodes"],scene["episodes"],
                             speakers["episodes_with_packets"],len(video["files"]))):
        raise ValueError("Incomplete original-series input index")
    byscript=unique(script["episodes"],"episode_id")
    byqa=unique(qa["items"],"episode_id")
    byscene=unique(scene["versions_index"],"episode_id")
    byspeaker=unique(speakers["versions"],"episode_id")
    byvideo=unique(video["files"],"episode_id_from_filename")
    universe=set(byscript)
    if not all(set(x)==universe for x in (byqa,byscene,byspeaker,byvideo)):
        raise ValueError("A source index omits or invents original-series episode IDs")
    tasks=[]
    for episode_id in sorted(universe):
        s=byscript[episode_id];q=byqa[episode_id];c=byscene[episode_id]
        p=byspeaker[episode_id];v=byvideo[episode_id]
        if (s["source_sha256"]!=q["source_sha256"] or
           s["source_sha256"]!=p["source_sha256"] or
           s["source_sha256"]!=c["source_sha256"] or
           v["identity_status"]!="filename_candidate_not_video_verified"):
            raise ValueError("Cross-index source/fingerprint mismatch "+episode_id)
        if s["caption_cues"]!=q["cue_count"] or s["caption_cues"]!=p["source_cues"]:
            raise ValueError("Cross-index original subtitle cue count mismatch "+episode_id)
        if s["source_format"]!=q["format"]:
            raise ValueError("Audio/source edition type disagreement "+episode_id)
        first_sample=episode_id=="S01E01"
        stages={
           "held_caption_witness":"complete_source_present",
           "source_reading_script":"complete_not_av_verified",
           "source_turns_and_roster":"prepared_unknown_speakers",
           "provisional_scene_participants":"source_only_no_confirmed_scene",
           "video_edition_identification":"bounded_sample_pilot_not_whole_episode_verified" if first_sample else "filename_candidate_only",
           "full_episode_subtitle_audio_alignment":"not_verified",
           "speaker_and_character_voice_identity":"not_verified",
           "observed_scene_boundaries_and_locations":"not_verified",
           "physical_stage_directions_and_reactions":"bounded_source_sample_only" if first_sample else "not_started",
           "vocal_prosody_and_delivery":"unreviewed_pilot_mix_features_only" if first_sample else "not_started",
           "full_episode_independent_av_QA":"not_verified",
        }
        required=[
          "Identify correct source-video release and decode/verify duration",
          "Listen for completeness, caption omissions and source-to-video offsets/drift",
          "Confirm source words, diarize/identify voices from verified evidence",
          "Observe video cuts, scene locations, facial/physical action and props",
          "Review audio prosody/emphasis/laughter separately from emotion guesses",
          "Generate source-linked proper scene script and independently accept episode"
        ]
        if not s["timed"]: required.insert(1,"Derive AV-validated original-source word times from untimed S09E19 paragraphs")
        if q["flags"]:required.insert(2,"Review source QA warnings: "+", ".join(q["flags"]))
        tasks.append({
           "episode_id":episode_id,"title":s["title"],
           "priority_score_existing_quality_only":q["score_for_triage_only"],
           "source_metadata":{
              "source_sha256":s["source_sha256"],"source_version_id":s["version_id"],
              "format":s["source_format"],"timed":s["timed"],
              "caption_cues":s["caption_cues"],
              "source_only_script":s["derived_path"],
              "speaker_preparation_folder":p["derived_path"],
              "provisional_participation_source":c["file"],
              "video_filename_candidate":v["basename"],"video_size_bytes_candidate":v["size_bytes"],
              "video_filename_identity_only":True,
           },
           "text_preparation":{
              "caption_units":s["unattributed_caption_units"],
              "caption_gap_dialogue_blocks":s["candidate_conversation_blocks"],
              "speaker_preparation_units":p["turns"],
              "agent_packets":p["packets"],
              "provisional_scene_clusters":c["scene_count"],
              "unverified_source_quality_flags":q["flags"]
           },
           "stage_acceptance":stages,
           "next_tasks":required,
           "status":"S01E01_bounded_AV_experiment_only" if first_sample else "source_ready_AV_pending",
           "speaker_verified":False,
           "full_episode_screenplay_verified":False,
        })
    tasks.sort(key=lambda row:(row["episode_id"]!="S01E01",
                                -row["priority_score_existing_quality_only"],row["episode_id"]))
    return {
      "schema":"night-court-1984-av-script-evidence-production-queue/1",
      "source_scope":"original_1984_to_1992_only_not_2023_reboot",
      "original_episode_records":len(tasks),
      "source_reading_scripts_ready":script["episodes_with_source_scaffold"],
      "source_voice_packets_ready":speakers["episodes_with_packets"],
      "source_participation_packets_ready":scene["episodes"],
      "filename_only_video_candidates":len(video["files"]),
      "original_caption_cues":script["source_cues"],
      "source_only_dialogue_units":script["caption_units"],
      "source_only_voice_attribution_units":speakers["attribution_units"],
      "provisional_scene_gap_clusters":scene["provisional_scenes"],
      "episode_scripts_independently_av_verified":0,
      "current_active_pilot":"S01E01",
      "ranking_basis":"S01E01 continuation first; other episodes use existing caption-QA heuristic review priority; not a measure of true AV accuracy",
      "file_identity_note":"FTP filenames and sizes do not prove video episode identity, content, or edition match",
      "rights_note":"Private owner research, no legal rights determination for external subtitles and production media",
      "episodes":tasks,
    }

def main():
    data=build()
    text=json.dumps(data,indent=2,ensure_ascii=False)+"\n"
    if not DEST.exists() or DEST.read_text("utf-8")!=text:
        DEST.write_text(text,encoding="utf-8")
    print("AV script work queue: 193 source-ready, one bounded S01E01 pilot, zero independent full-episode video verifications")

if __name__=="__main__":main()
