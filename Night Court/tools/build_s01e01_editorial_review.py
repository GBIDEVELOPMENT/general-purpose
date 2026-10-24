#!/usr/bin/env python3
"""Compile the S01E01 audiovisual editorial acceptance worksheet.

This joins original caption turns, two acoustic word timing hypotheses, mixed
soundtrack metrics, and source-frame observations WITHOUT presenting these
as accepted transcriptions, speaker identities, emotions, or verified action.
"""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EP=ROOT/"seasons"/"S01"/"S01E01"
BASE=EP/"derived"
V1=BASE/"scene-review-v1"
V2=BASE/"scene-review-v2"
V3=BASE/"scene-review-v3"
OUT=BASE/"editorial-review-v1"
AVI="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SRT="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
VERSION="s01-internal-dvdrip-xvid-sprinter-english--aa9f77600cd9f2b6"

def load(path):
    return json.loads(path.read_text("utf-8"))

def validate_sources():
    scene=load(V3/"scene-evidence-map.json")
    words=load(V3/"word-timing-model-comparison.json")
    model=load(V3/"utterance-mix-prosody.json")
    motion=load(V2/"visual-motion-observations.json")
    frame_index=load(V2/"dense-frame-index.json")
    word_turns=load(V1/"word-alignment-review.json")
    meta=load(EP/"dialogue"/"versions"/VERSION/"manifest.json")
    if not (scene["source_media_sha256"]==words["source_media_sha256"]==
        model["source_media_sha256"]==motion["source_media_sha256"]==
        frame_index["source_media_sha256"]==word_turns["media_sha256"]==AVI):
        raise ValueError("Video source edition hash is inconsistent")
    if not (scene["original_subtitle_sha256"]==words["source_caption_sha256"]==
        model["source_caption_sha256"]==motion["source_caption_sha256"]==
        word_turns["caption_sha256"]==meta["sha256"]==SRT):
        raise ValueError("Original dialogue witness source hash inconsistent")
    if (words["source_window_ms"]!=[60000,90000] or
        word_turns["source_window_ms"]!=[60000,90000] or
        model["source_window_ms"]!=[60000,90000] or
        frame_index["source_time_window_ms"]!=[75000,90000] or
        scene["counts_and_gates"]["scene_audiovisual_complete"] or
        words["audiovisual_word_timing_verified"] or
        model["speaker_diarized_or_identified"] or motion["speaker_identities_verified"]):
        raise ValueError("Source window or accepted-claim invariant broken")
    cues=word_turns["cue_turn_packets"]
    if len(cues)!=9 or [x["cue"] for x in cues]!=list(range(19,28)):
        raise ValueError("Expected original nine caption cues C19 to C27")
    source_words=words["per_source_word_review"]
    if len(source_words)!=55 or len(model["utterance_prosody_hypotheses"])!=10:
        raise ValueError("Missing source word or audio evidence")
    if len(motion["time_scoped_observations"])!=6 or frame_index["frames_actual"]!=60:
        raise ValueError("Frame review mismatch")
    actual_cue_turns={(c["cue"],t["source_turn_index"]):t
            for c in cues for t in c["source_turns"]}
    if len(actual_cue_turns)!=11:
        raise ValueError("Expected eleven source voice-typography turns")
    for word in source_words:
        if (word["source_cue"],word["source_turn_index"]) not in actual_cue_turns:
            raise ValueError("Word references unknown original caption turn")
        if word["speaker_verified"] or word["manual_audio_confirmation"]:
            raise ValueError("Unreviewed model hypotheses promoted to verified speech")
    for obs in motion["time_scoped_observations"]:
        if not obs["supporting_frames"]:raise ValueError("Motion has no frame evidence")
        for ref in obs["supporting_frames"]:
            idx=ref["frame"]-1
            if not 0<=idx<60:raise ValueError("Unknown source frame index")
            orig=frame_index["frame_evidence"][idx]
            if (ref["sha256"]!=orig["sha256"] or
                ref["source_nominal_ms"]!=orig["approximate_video_time_ms"]):
                raise ValueError("Stale image checksum or source time")
    return scene,words,model,motion,frame_index,word_turns

def build():
    scene,words,model,motion,frames,original=validate_sources()
    by_word={}
    for row in words["per_source_word_review"]:
        by_word.setdefault((row["source_cue"],row["source_turn_index"]),[]).append(row)
    speech={i["asr_segment_index"]:i for i in model["utterance_prosody_hypotheses"]}
    voice_tasks=[]
    counts=Counter()
    for cue in original["cue_turn_packets"]:
        for turn in cue["source_turns"]:
            key=(cue["cue"],turn["source_turn_index"])
            word_rows=sorted(by_word.get(key,[]),key=lambda x:x["source_word_index"])
            if not word_rows:raise ValueError("Original speaking turn lost its words")
            if [x["source_word_index"] for x in word_rows]!=list(range(len(word_rows))):
                raise ValueError("Source word indexes not sequential")
            tally=Counter(row["source_review_priority"] for row in word_rows)
            counts.update(tally)
            seg=turn.get("asr_segment_index")
            acoustic=speech.get(seg) if seg is not None else None
            if acoustic and acoustic["caption_cue_hint"]!=cue["cue"]:
                raise ValueError("Prosody segment points to different caption")
            if acoustic and acoustic["speaker_isolated"]:
                raise ValueError("Audio mix falsely represented as actor-specific")
            flags=[]
            if cue["original_caption_interval_ms"][0]<60000:
                flags.append("caption_starts_before_audio_sample")
            if cue["original_caption_interval_ms"][1]>90000:
                flags.append("caption_continues_after_audio_sample")
            if seg is None:
                flags.append("no_source_asr_speaker_turn")
            if tally["no_usable_word_timing_candidate"]:
                flags.append("words_without_model_time")
            if tally["two_model_start_disagreement_over_300ms"]:
                flags.append("model_timing_disagreement")
            if any(w["original_normalized_word"] in {"MINIMIFIDIAN","EXTRAVASATE"}
                   for w in word_rows):
                flags.append("unusual_comic_vocabulary_requires_listening")
            if acoustic and ("too_short" in acoustic["acoustics"]["pitch_reliability"]):
                flags.append("voice_span_too_short_for_stable_pitch")
            # Important: a frame near an utterance is NOT evidence of its speaker.
            nearby=[{"observation_id":ob["id"],"source_interval_ms":ob["interval_ms"],
                     "sampled_frame_sha256":[ref["sha256"] for ref in ob["supporting_frames"]]}
                  for ob in motion["time_scoped_observations"]
                  if ob["interval_ms"][0]<=cue["original_caption_interval_ms"][1]+1000
                    and ob["interval_ms"][1]>=cue["original_caption_interval_ms"][0]-1000]
            priority=(10*len(flags)+8*tally["no_usable_word_timing_candidate"]+
                      6*tally["two_model_start_disagreement_over_300ms"]+
                      4*tally["CTC_only_model_word_candidate"]+
                      4*tally["tiny_en_only_word_candidate"])
            voice_tasks.append({
                "task_id":f'S01E01:C{cue["cue"]:05d}.{turn["source_turn_index"]+1}',
                "episode_id":"S01E01","source_caption_sha256":SRT,
                "source_cue":cue["cue"],"source_turn_index":turn["source_turn_index"],
                "source_caption_interval_ms":cue["original_caption_interval_ms"],
                "original_dialogue":turn["text"],
                "source_words":word_rows,
                "word_timing_category_counts":dict(sorted(tally.items())),
                "asr_speech_candidate_interval_ms":
                  acoustic["asr_source_audio_interval_ms"] if acoustic else None,
                "mixed_audio_metrics":acoustic["acoustics"] if acoustic else None,
                "nearby_sampled_visual_events_not_speaker_evidence":nearby,
                "review_flags":flags,"priority_score_for_editor_only":priority,
                "speaker_identity":None,
                "audio_text_confirmation":"not_reviewed",
                "audio_word_timing_confirmation":"not_reviewed",
                "audio_delivery_review":"not_reviewed",
                "video_mouth_to_voice_confirmation":"not_reviewed",
                "visual_context_alone_proves_speaker":False,
                "independent_human_acceptance":False
            })
    visual_tasks=[]
    for ob in motion["time_scoped_observations"]:
        visual_tasks.append({
          "task_id":"S01E01:"+ob["id"],
          "source_media_sha256":AVI,"source_interval_ms":ob["interval_ms"],
          "observation":ob["description"],
          "observation_class":ob["observation_class"],
          "supporting_source_frames":[{"path":x["file"],"sha256":x["sha256"],
              "time_ms":x["source_nominal_ms"]} for x in ob["supporting_frames"]],
          "continuous_video_observation_verified":False,
          "exact_action_onset_verified":False,
          "character_identity_from_visual_evidence":None,
          "spoken_voice_from_visual_evidence":None,
          "review_status":"AI_sampled_frames_needs_independent_video_acceptance"
        })
    tasks_sorted=sorted(voice_tasks,key=lambda x:(-x["priority_score_for_editor_only"],
                                      x["source_cue"],x["source_turn_index"]))
    packet={
      "schema":"night-court-s01e01-editorial-qa-packet/1",
      "episode_id":"S01E01",
      "source_video_sha256":AVI,"source_caption_sha256":SRT,
      "review_scope_ms":[60000,90000],
      "inputs":{
         "script":"scene-review-v3/scene-evidence-map.json",
         "word_comparison":"scene-review-v3/word-timing-model-comparison.json",
         "audio":"scene-review-v3/utterance-mix-prosody.json",
         "visual":"scene-review-v2/visual-motion-observations.json",
         "source_dialogue":"scene-review-v1/word-alignment-review.json"
      },
      "counts":{
          "source_caption_cues":9,"source_speaking_turns":len(voice_tasks),
          "source_words":sum(len(t["source_words"]) for t in voice_tasks),
          "visual_motion_observations":len(visual_tasks),
          "source_model_comparison_categories":dict(sorted(counts.items())),
          "voice_turns_human_accepted":0,
          "visual_events_continuous_video_accepted":0
      },
      "voice_review_tasks":tasks_sorted,
      "visual_review_tasks":visual_tasks,
      "independent_audio_reviewed":False,
      "source_cut_verified":False,
      "speaker_identity_verified":False,
      "acting_emotion_verified":False,
      "episode_audiovisual_complete":False,
      "review_note":"Tasks are compiled from prior evidence, not additional listening or video viewing"
    }
    if packet["counts"]["source_speaking_turns"]!=11 or packet["counts"]["source_words"]!=55:
        raise ValueError("Incomplete voice task packet")
    return packet

def summary(packet):
    text=["# S01E01 original audiovisual script editorial worklist",
          "",
          "This is an **unaccepted review dossier** for the original episode",
          "01:00–01:30, not an endorsed screenplay or a replacement subtitle track.",
          "The source spans 11 typographic turns and 55 source words; video frames",
          "capture six action observations but do not prove speaking identities.",
          "",
          "## Voice and dialogue listening queue",
          "",
          "| Source turn | Priority | Words | ASR window | Evidence flags |",
          "|---|---:|---:|---|---|"]
    for task in packet["voice_review_tasks"]:
        span=task["asr_speech_candidate_interval_ms"]
        moment="not linked" if span is None else f'{span[0]/1000:.3f}–{span[1]/1000:.3f}s'
        text.append(f'| {task["task_id"]} | {task["priority_score_for_editor_only"]} | '
                    f'{len(task["source_words"])} | {moment} | '
                    f'{", ".join(task["review_flags"]) or "sample source speech"} |')
    text += ["","### Required audible acceptance","",
       "For each entry, independently listen to the referenced original AVI excerpt.",
       "Check every original caption word, omitted/overlapping words, segment timing",
       "and whether the isolated spoken voice can actually be identified.",
       "Compare CTC and tiny.en hypotheses; no accepted word/voice result yet.",
       "",
       "## Stage directions and motion acceptance queue",""]
    for t in packet["visual_review_tasks"]:
        times=t["source_interval_ms"]
        refs=", ".join(x["path"].split("/")[-1] for x in t["supporting_source_frames"])
        text.append(f'- **{t["task_id"]}** ({times[0]/1000:.2f}–{times[1]/1000:.2f}s): '
                    f'{t["observation"]} Evidence: {refs}. '
                    "**Needs continuous-video independent review.**")
    text += ["","## Publication gate","",
      "Production-script labels for scene boundaries, named characters, delivery",
      "and physical comedy must link to individually reviewed audio/video evidence.",
      "A sampled still or model pitch contour cannot alone establish speaker,",
      "acting emotion, word truth, or episode completeness.",
      "",
      f"AVI SHA-256: {AVI}",
      f"Original English SRT SHA-256: {SRT}",
      ""]
    return "\n".join(text)

def main():
    if OUT.exists():raise ValueError("Refusing to overwrite another editorial packet")
    packet=build()
    OUT.mkdir(parents=True)
    (OUT/"acceptance-worklist.json").write_text(json.dumps(packet,indent=2,ensure_ascii=False)+"\n","utf-8")
    (OUT/"acceptance-worklist.md").write_text(summary(packet),"utf-8")
    print("Generated",packet["counts"]["source_speaking_turns"],
          "unverified source voice tasks and",
          packet["counts"]["visual_motion_observations"],"reviewable video actions; zero accepted claims")

if __name__=="__main__":main()
