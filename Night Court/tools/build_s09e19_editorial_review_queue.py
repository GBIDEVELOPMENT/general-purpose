#!/usr/bin/env python3
"""Editorial worklist for the unique S09E19 UNTIMED text and source video.

Original source paragraphs have NO timecodes. All selected video intervals
below are audio-model hypotheses, never source caption timing. Frame states
are sampled images, not independently reviewed continuous physical action.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from s09e19_untimed_video_anchor_pilot import sources, TXT_SHA

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "seasons/S09/S09E19/derived"
SCENE = BASE / "scene-review-v1/source-linked-scene.json"
FRAMES = BASE / "visual-review-v1/frame-source-index.json"
OUT = BASE / "editorial-review-v1/untimed-scene-review-queue.json"
AVI_SHA = "51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649"


def build(scene=None, frames=None, paragraphs=None):
    s = scene if scene is not None else json.loads(SCENE.read_text("utf-8"))
    f = frames if frames is not None else json.loads(FRAMES.read_text("utf-8"))
    p = paragraphs if paragraphs is not None else sources()
    if (s.get("schema") != "night-court-s09e19-source-evidence-scene/1"
        or s.get("episode_id") != "S09E19"
        or s.get("source_media_sha256") != AVI_SHA
        or s.get("source_original_untimed_text_sha256") != TXT_SHA
        or s.get("observed_video_excerpt_ms") != [900000, 925000]
        or s.get("source_paragraph_count") != 347
        or s.get("source_paragraph_dialogue_candidates") != 5
        or s.get("reviewed_sampled_video_observations") != 6
        or s.get("original_source_paragraphs_still_untimed") is not True
        or any(s.get(key) is not False for key in (
          "independent_audio_word_verification",
          "independent_speaker_character_attribution",
          "continuous_video_performance_actions_verified",
          "actual_full_scene_boundaries_verified",
          "original_episode_audiovisual_complete"))):
        raise ValueError("Source-linked S09E19 scene provenance or acceptance changed")
    if (f.get("source_original_avi_sha256") != AVI_SHA
        or f.get("original_untimed_text_sha256") != TXT_SHA
        or f.get("source_window_ms") != [900000, 925000]
        or f.get("sample_count") != 100 or len(f.get("frames",[])) != 100
        or len(p) != 347):
        raise ValueError("Original S09E19 untimed paragraphs or sampled frames missing")
    tasks=[]
    for event in s["events"]:
        a,b=event["video_candidate_interval_ms"]
        if any(type(n) is not int for n in (a,b)) or not 900000<=a<b<=925000:
            raise ValueError("Model/video candidate time invalid")
        if event["source_kind"] == "original_untimed_source_paragraph_candidate":
            first,last=event["source_first_paragraph"],event["source_last_paragraph"]
            if not 1<=first<=last<=347:
                raise ValueError("Original untimed paragraph IDs invalid")
            src=[p[i-1] for i in range(first,last+1)]
            if (any(x["start_ms"] is not None or x["end_ms"] is not None for x in src)
                or event["original_source_text"] != " ".join(x["text"] for x in src)
                or event["original_source_paragraph_has_no_timecodes"] is not True
                or event["human_audio_dialogue_verified"] is not False
                or event["human_video_lip_synced"] is not False
                or event["candidate_speaking_character"] is not None):
                raise ValueError("Untimed source text modified, timed, or falsely accepted")
            tasks.append({
                "task_id":f"S09E19:P{first:03d}:ASR{event['asr_segment_index']}",
                "kind":"proposed_dialogue_match",
                "original_untimed_paragraphs":[first,last],
                "original_source_text":event["original_source_text"],
                "source_paragraph_timestamp_ms":None,
                "model_proposed_video_time_interval_ms":[a,b],
                "model_similarity_heuristic":event["model_similarity_heuristic"],
                "review_evidence_status":"pending_source_audio_listening",
                "accepted_speaking_character":None,
                "accepted_vocal_delivery":None,
                "source_audio_segment_independently_verified":False,
                "mouth_voice_synchronization_verified":False
            })
        elif event["source_kind"] == "sampled_original_video_observation":
            refs=event["frame_evidence"]
            if len(refs)<2 or event["scene_action_continuous_video_verified"] is not False:
                raise ValueError("Incomplete or falsely accepted sampled visual event")
            for x in refs:
                name=x["file"]
                n=int(name.rsplit("-",1)[-1].removesuffix(".jpg"))
                if not 1<=n<=100:
                    raise ValueError("Invalid source frame index")
                true=f["frames"][n-1]
                if (true["file"] != name or true["sha256"] != x["sha256"]
                    or true["approx_source_time_ms"] != x["nominal_time_ms"]):
                    raise ValueError("Actual original AVI frame SHA/time mismatch")
            if event["speaker_identity"] is not None or event["character_identity"] is not None:
                raise ValueError("Visual source cannot establish cast speaker")
            tasks.append({
                "task_id":"S09E19:"+event["visual_id"],
                "kind":"sampled_visual_stage_claim",
                "sampled_video_interval_ms":[a,b],
                "description":event["description"],
                "supporting_frame_sha256":[x["sha256"] for x in refs],
                "original_frame_presentation_times_verified":False,
                "continuous_video_action_verified":False,
                "source_audio_speaker_identity":None,
                "review_evidence_status":"pending_continuous_video",
            })
        else:
            raise ValueError("Unknown source scene evidence kind")
    if (len(tasks)!=11 or len({x["task_id"] for x in tasks})!=11
        or sum(t["kind"]=="proposed_dialogue_match" for t in tasks)!=5
        or sum(t["kind"]=="sampled_visual_stage_claim" for t in tasks)!=6):
        raise ValueError("Expected five tentative paragraph matches and six visual events")
    return {
      "schema":"night-court-s09e19-untimed-editorial-review-queue/1",
      "episode_id":"S09E19",
      "original_video_sha256":AVI_SHA,
      "original_untimed_source_sha256":TXT_SHA,
      "original_paragraph_count":347,
      "original_source_paragraphs_with_actual_timecodes":0,
      "video_excerpt_ms":[900000,925000],
      "source_asr_candidate_count":5,
      "sampled_video_event_count":6,
      "individual_review_tasks":11,
      "independently_accepted_dialogue_matches":0,
      "independently_accepted_physical_actions":0,
      "speaker_identity_verified":False,
      "vocal_delivery_verified":False,
      "complete_scene_audiovisual_accepted":False,
      "tasks":tasks,
      "acceptance_order":"Listen to exact original AVI; confirm each proposed spoken line and untimed paragraph; separately inspect continuous video for real action and mouth-voice identity; document reviewer provenance; only then consider timecoded derived *edition*, never modify original untimed source.",
      "rights_note":"Private audiovisual research only; source rights and episode completeness unverified."
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--write",action="store_true")
    opts=ap.parse_args()
    result=build()
    if opts.write:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n","utf-8")
        print("Created 11 PENDING S09E19 original-source reviewer tasks; no invented source timecodes")
    else:
        print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
