#!/usr/bin/env python3
"""Render first integrated S01E01 60–90s evidence-linked scene, no new claims.

Takes source cues from immutable SRT-derived review, AI-reviewed sampled
visual observations and model word candidates as distinctly labeled evidence.
"""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]/"seasons"/"S01"/"S01E01"
V1=ROOT/"derived"/"scene-review-v1"
V2=ROOT/"derived"/"scene-review-v2"
DEST=ROOT/"derived"/"scene-review-v3"
MEDIA_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SRT_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"

def load():
    first=json.loads((V1/"visual-observations.json").read_text("utf-8"))
    recent=json.loads((V2/"visual-motion-observations.json").read_text("utf-8"))
    words=json.loads((V1/"word-alignment-review.json").read_text("utf-8"))
    index=json.loads((V2/"dense-frame-index.json").read_text("utf-8"))
    if (first["source_media_sha256"]!=MEDIA_SHA or
        recent["source_media_sha256"]!=MEDIA_SHA or words["media_sha256"]!=MEDIA_SHA or
        first["subtitle_witness_sha256"]!=SRT_SHA or
        recent["source_caption_sha256"]!=SRT_SHA or words["caption_sha256"]!=SRT_SHA or
        index["frames_actual"]!=60):
        raise ValueError("Cross-modal source SHA or sample size mismatch")
    if len(first["time_bounded_observations"])!=5 or len(recent["time_scoped_observations"])!=6:
        raise ValueError("Expected source-observed evidence counts changed")
    cues=words["cue_turn_packets"]
    if len(cues)!=9 or [x["cue"] for x in cues]!=list(range(19,28)):
        raise ValueError("Missing/duplicated source captions")
    if any(x.get("speaker_identity") is not None for c in cues for x in c["source_turns"]):
        raise ValueError("Unverified speaker identity entered word review")
    if recent["speaker_identities_verified"] or words["verified_word_alignment"]:
        raise ValueError("An explicit new review mode is required for promoted source claims")
    for o in recent["time_scoped_observations"]:
        for ref in o["supporting_frames"]:
            original=index["frame_evidence"][ref["frame"]-1]
            if ref["sha256"]!=original["sha256"] or ref["file"]!=original["file"]:
                raise ValueError("Visual motion observation orphaned from source frame hash")
    return first,recent,words,index

def clock(ms):
    total=ms/1000
    return f"{int(total//60):02d}:{total%60:06.3f}"

def build():
    first,recent,words,index=load()
    events=[]
    for item in words["cue_turn_packets"]:
        for sub in item["source_turns"]:
            events.append({"start_ms":item["original_caption_interval_ms"][0],
                           "end_ms":item["original_caption_interval_ms"][1],
                           "source_kind":"caption_turn","cue":item["cue"],
                           "source_turn_index":sub["source_turn_index"],
                           "text":sub["text"],
                           "exact_model_word_time_candidates":len(sub["exact_word_time_candidates"]),
                           "review_status":"unattributed_source_dialogue_candidate_audio_timing"})
    for num,o in enumerate(first["time_bounded_observations"],1):
        events.append({"start_ms":o["time_ms"],"end_ms":o["time_ms"],
                       "source_kind":"reviewed_static_frame","id":f"STATIC-{num:02d}",
                       "text":o["description"],"evidence":o["evidence"],
                       "review_status":"AI_still_image_observation_not_motion"})
    for o in recent["time_scoped_observations"]:
        events.append({"start_ms":o["interval_ms"][0],"end_ms":o["interval_ms"][1],
                       "source_kind":"reviewed_sampled_sequence","id":o["id"],
                       "text":o["description"],
                       "evidence":[ref["file"] for ref in o["supporting_frames"]],
                       "review_status":"AI_ordered_4fps_frames_not_continuous_video_review"})
    events.sort(key=lambda x:(x["start_ms"],0 if x["source_kind"]!="caption_turn" else 1,
                               x.get("cue",0),x.get("source_turn_index",0)))
    if sum(e["source_kind"]=="caption_turn" for e in events)!=11:
        raise ValueError("Expected 11 explicit source-dialogue turns across nine cues")
    counts={
       "source_caption_cues":9,"explicit_subtitle_typographic_voice_turns":11,
       "reviewed_static_observations":5,"reviewed_dense_motion_observations":6,
       "exact_text_ASR_word_time_candidates":sum(
           len(t["exact_word_time_candidates"])
           for c in words["cue_turn_packets"] for t in c["source_turns"]),
       "source_window_ms":[60000,90000],
       "all_known_speakers_unverified":True,
       "caption_audio_edition_synchronization_verified":False,
       "scene_continuous_video_verified":False,
       "scene_audiovisual_complete":False
    }
    if counts["exact_text_ASR_word_time_candidates"]!=45:
        raise ValueError("Expected 45 distinct model candidate token anchors")
    data={
      "schema":"night-court-integrated-evidence-script/3",
      "episode_id":"S01E01","source_media_sha256":MEDIA_SHA,
      "original_subtitle_sha256":SRT_SHA,
      "scene_heading":"INT. BOOK-LINED COURT OFFICE – TIME OF DAY UNVERIFIED",
      "scope":"bounded_source_video_time_60_to_90_seconds_only",
      "first_visual_source":"scene-review-v1/visual-observations.json",
      "dense_visual_source":"scene-review-v2/visual-motion-observations.json",
      "word_evidence_source":"scene-review-v1/word-alignment-review.json",
      "reviewed_by":"AI from sampled source stills; independent full-motion, audio and cast acceptance pending",
      "counts_and_gates":counts,"events":events
    }
    out=[
      "# S01E01 | Integrated evidence-linked scene v3",
      "",
      "## INT. BOOK-LINED COURT OFFICE – TIME OF DAY UNVERIFIED",
      "",
      "**EXCERPT 01:00–01:30.** Working script, not independently AV-certified.",
      "The scene shows rows of books, wood trim and an office desk with papers,",
      "folders and a black telephone. An adult in lavender is beside the desk;",
      "an adult in a dark uniform is opposite.",
      "",
      "> Caption lines retain the exact source witness text, including unusual",
      "> vocabulary. The words and 45 model-derived word-time anchors have not",
      "> been independently verified against the soundtrack. Speaker labels are",
      "> intentionally unassigned. Motion notes describe ordered frame evidence.",
      ""
    ]
    for event in events:
        when=clock(event["start_ms"])
        if event["source_kind"]=="caption_turn":
            before=event["start_ms"]<60000
            after=event["end_ms"]>90000
            note=(" [starts outside sample]" if before else "")+(" [continues beyond sample]" if after else "")
            out += [f'**{when} | C{event["cue"]:04d} | UNIDENTIFIED VOICE · source turn {event["source_turn_index"]+1}{note}**',
                    event["text"],""]
        else:
            interval=(f"{when}–{clock(event['end_ms'])}" if event["end_ms"]!=event["start_ms"]
                      else when)
            evidence=", ".join(event["evidence"])
            qualifier=("sampled sequence" if event["source_kind"]=="reviewed_sampled_sequence"
                       else "single still")
            out += [f'*[{interval} | {event["id"]} | {qualifier}]*',
                    f'*{event["text"]}*',
                    f'Frame evidence: {evidence}',""]
    out += [
       "### Editorial and provenance limits","",
       "Source images, candidate acoustic timing and subtitle typography are separate",
       "witnesses; no visual cue assigns a real performer to a spoken turn.",
       "Unusual comic vocabulary, overlapping voices, audience laughter, and",
       "the 01:00/01:30 excerpt boundaries require independent audio review.",
       "Four-hertz visual sampling may miss fast gestures and reactions.",
       "",
       f"Source AVI SHA-256: "+MEDIA_SHA,
       f"Source English SRT SHA-256: "+SRT_SHA,
       "No original source subtitle, AVI, audio or raw unreviewed model prediction was modified.",
       ""
    ]
    return data,"\n".join(out)

def main():
    if DEST.exists():raise ValueError("Refuse overwrite of derived source-script revision")
    doc,script=build()
    DEST.mkdir(parents=True)
    (DEST/"scene-evidence-map.json").write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n","utf-8")
    (DEST/"scene-script-v3.md").write_text(script,"utf-8")
    print("Integrated reviewed first-scene excerpt: 9 captions, 11 source turns, 11 visual observations, 45 text-exact model anchors")

if __name__=="__main__":main()
