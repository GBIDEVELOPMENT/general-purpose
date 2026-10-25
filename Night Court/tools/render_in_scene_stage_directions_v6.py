#!/usr/bin/env python3
"""Source-timed S01 theatrical reading draft with genuinely observed picture cues.

A stage direction is inserted beside SRT dialogue only for a source JPEG or
bounded original motion sample that has already been individually reviewed.
A cue's original SRT start is a nearby reading locator, NOT verified speech-to-
image causality or an exact cut time. S09 source paragraphs stay UNTIMED.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from render_readable_caption_screenplay_v5 import render as v5,ROOT,OUTPUT as V5_OUTPUT
from render_caption_first_scene_edit_v2 import source_visuals
from render_caption_first_motion_edit_v3 import evidence as motion_evidence
from build_caption_first_working_drafts import witness, SOURCE_SHA

OUTPUT="caption-first-source-stage-in-scene-v6"


def first_cue_at_or_after(cues,ms):
    if not isinstance(ms,int) or ms<0:raise ValueError("Invalid observed source-video window")
    for cue in cues:
        if cue["start_ms"]>=ms:return cue["cue"]
    return cues[-1]["cue"]


def insert_before_speaker_for_cue(script,cue,text):
    marker=f"*Source: C{cue:03d}.1 · "
    index=script.find(marker)
    if index<0 or script.find(marker,index+1)!=-1:
        raise ValueError("Missing/duplicate original source dialogue cue anchor: "+marker)
    lead=script.rfind("\n**",0,index)
    if lead<0:raise ValueError("Could not locate reading-script speaker block")
    # The nearest preceding speaker block must be the one whose source
    # citation is this cue. Don't silently insert the note elsewhere.
    nearby=script[lead:index]
    if "\n*Source:" in nearby or len(nearby)>2000:
        raise ValueError("Stage-note cue map crossed another dialogue segment")
    return script[:lead+1]+text+"\n\n"+script[lead+1:]


def render(episode,root=ROOT):
    original,old_manifest,old_review=v5(episode,root)
    _,meta,cues,units,_=witness(episode,root)
    if episode not in ("S01E01","S09E19"):raise ValueError("Only original-series pilots")
    text=original
    inserts=[]
    if episode=="S01E01":
        if not meta["timecoded"]:raise ValueError("The source SRT timing vanished")
        photos,ledger_sha,source=source_visuals(episode,root)
        motion,motion_sha,motion_report=motion_evidence(episode,root)
        candidates=[]
        for entry in photos:
            candidates.append({
               "kind":"directly_inspected_source_still",
               "time_ms":entry["source_requested_ms"],
               "source_sha256":entry["source_thumbnail_sha256"],
               "evidence_key":f"original-source-photo-frame-{entry['frame_id']:03d}",
               "text":entry["visually_observed_static_description"],
               "scope":"Individual original AVI still only; not a verified gesture or speaking identity"
            })
        for seq in motion:
            start,end=seq["source_window_s"]
            candidates.append({
              "kind":"directly_inspected_bounded_5fps_motion",
              "time_ms":start*1000,
              "source_sha256":motion_report["private_original_artifact_zip_sha256"],
              "evidence_key":seq["window_label"],
              "text":seq["stage_direction"],
              "scope":f"Sampled 5fps original picture passage {start}–{end}s; sound, character names and exact cut not verified"
            })
        candidates.sort(key=lambda x:x["time_ms"])
        for event in candidates:
            when=event["time_ms"]
            cue=first_cue_at_or_after(cues,when)
            quote=(f"*SOURCE-PICTURE STAGE DIRECTION "
                   f"[requested source {when/1000:.3f}s, {event['kind']}]: "
                   f"{event['text']}*\n"
                   f"*{event['scope']}. Evidence key: `{event['evidence_key']}`; "
                   f"SHA-256: `{event['source_sha256']}`. The following "
                   "subtitle cue is a **nearby timing locator**, not an "
                   "audio-synchronized cause.*")
            text=insert_before_speaker_for_cue(text,cue,quote)
            inserts.append({"closest_caption_cue":cue,
                "source_requested_original_video_ms":when,
                "evidence_kind":event["kind"],
                "evidence_key":event["evidence_key"],
                "original_evidence_sha256":event["source_sha256"],
                "speaker_or_original_audio_verified":False,
                "native_frame_pts_accepted":False})
        if sum(x["kind"]=="directly_inspected_source_still" for x in candidates)!=17:
            raise ValueError("Original photographic scene ledger lost")
        if sum(x["kind"]=="directly_inspected_bounded_5fps_motion" for x in candidates)!=2:
            raise ValueError("Original physical stage samples lost")
    else:
        # S09 has an original untimed *transcript*. No source movie time can
        # honestly be mapped to a paragraph yet, regardless of lexical match.
        if meta["timecoded"] is not False:
            raise ValueError("Untimed source incorrectly given timing")
        ledger_sha=None;motion_sha=None
    if [f"C{x:03d}.1" for x in old_manifest["rendered_source_cue_ids_in_order"]]!=[
           f"C{x:03d}.1" for x in range(1,len(cues)+1)]:
        raise ValueError("A held source dialogue cue vanished")
    if old_manifest["source_original_cues"]!=len(cues):
        raise ValueError("Source dialogue version drift")
    text=text.replace("\\`","`").rstrip()+"\n"
    manifest={
      "schema":"night-court-sourced-stage-directions-in-readable-screenplay/6",
      "episode_id":episode,
      "source_caption_sha256":SOURCE_SHA[episode],
      "source_original_cues":len(cues),
      "source_original_speaking_units":len(units),
      "all_v5_original_cue_text_and_fingerprints_preserved":True,
      "v5_original_unit_text_sha256_in_order":old_manifest["source_unit_text_sha256_in_order"],
      "original_srt_nearby_in_scene_still_notes":sum(x["evidence_kind"]=="directly_inspected_source_still" for x in inserts),
      "original_srt_nearby_in_scene_motion_notes":sum(x["evidence_kind"]=="directly_inspected_bounded_5fps_motion" for x in inserts),
      "original_source_untimed_video_to_paragraph_alignment_invented":False,
      "source_picture_ledger_sha256":ledger_sha,
      "source_motion_ledger_sha256":motion_sha,
      "source_timed_caption_evidence_insertions":inserts,
      "original_audio_lip_voices_matched":False,
      "scene_transition_and_significant_gags_complete":False,
      "screenplay_editor_ready":False,
      "independently_whole_episode_av_certified":False,
      "source_provisional_speaker_labels_preserved":True,
      "original_photo_motion_in_repo":False,
      "status":"READABLE_DIALOGUE_COMPLETE_SOURCE_TIMED_PICTURE_INSERTS_ORIGINAL_AV_EDITORIAL_PENDING"
    }
    return text,manifest,old_review


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode",choices=["S01E01","S09E19"],required=True)
    parser.add_argument("--output-root",type=Path,default=ROOT)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    script,manifest,review=render(args.episode)
    out=args.output_root/"seasons"/args.episode[:3]/args.episode/"derived"/OUTPUT
    values={"screenplay-with-stage-directions.md":script,
       "stage-direction-manifest.json":json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",
       "pending-voice-review.json":json.dumps(review,indent=2,ensure_ascii=False)+"\n"}
    if args.check:
        for name,value in values.items():
            path=out/name
            if not path.is_file() or path.read_text("utf-8")!=value:
                raise ValueError("Stale or missing original stage-direction editorial artifact: "+str(path))
    else:
        out.mkdir(parents=True,exist_ok=True)
        for name,value in values.items():
            (out/name).write_text(value,encoding="utf-8")
    print(args.episode,manifest["source_original_cues"],"complete source cues,",
        manifest["original_srt_nearby_in_scene_still_notes"],"new inline photos,",
        manifest["original_srt_nearby_in_scene_motion_notes"],"source moving-image notes;",
        "not AV-certified or all-speaker/editor-ready")


if __name__=="__main__":
    main()
