#!/usr/bin/env python3
"""Render source-photo enriched pilot editorial drafts from real original AVI stills.

Keeps all held caption dialogue, adds directly inspected, frame-SHA-bound
scene-setting notes and distinct source-text story beats. Untimed paragraphs
are NEVER assigned original movie timestamps. No performer is identified from
a still and no 18-second sparse sample certifies a moving gag.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from build_caption_first_working_drafts import ROOT, SOURCE_SHA, witness, render_episode

OUTPUT="caption-first-scene-edit-v2"
ATLAS="source-photo-scene-overview-v1/observations.json"
VIDEO_SHA={
    "S01E01":"5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962",
    "S09E19":"51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649"
}
SHEETS={"S01E01":(80,17),"S09E19":(73,16)}
STORY_BEATS={
  "S09E19":[
    (1,"Campaign preparations and correspondence"),
    (59,"Courtroom case and courtroom duties"),
    (96,"Investigation around an old office safe"),
    (126,"Campaign commercial complications"),
    (152,"An anticipated meeting and other court business"),
    (216,"The restaurant meeting"),
    (282,"Questioned identity at the meeting"),
    (314,"Campaign commercial discovery and closing exchanges")
  ]
}
SPEAKING_SELF_LABELS={
  "S01E01":{
    (57,2):("HARRY STONE","responds to a direct spoken identification as Judge Harold T. Stone; dialogue-context attribution"),
    (72,1):("LANA WAGNER","explicitly states 'I'm Lana Wagner' in this source caption")
  },
  "S09E19":{
    (283,1):("VOICE SELF-INTRODUCING AS ALEX PATTERSON","claimed identity only, not independent character identification")
  }
}


def position(ms):
    return f"{ms//60000:02d}:{(ms%60000)/1000:06.3f}"


def source_visuals(ep,root=ROOT):
    p=root/"seasons"/ep[:3]/ep/"derived"/ATLAS
    raw=p.read_bytes()
    data=json.loads(raw)
    n,count=SHEETS[ep]
    items=data.get("visual_observations")
    if (data.get("schema")!="night-court-real-original-image-scene-observations/1"
        or data.get("episode_id")!=ep
        or data.get("source_caption_sha256")!=SOURCE_SHA[ep]
        or data.get("original_video_sha256")!=VIDEO_SHA[ep]
        or data.get("whole_episode_uniform_frames_captured")!=n
        or not isinstance(items,list) or len(items)!=count
        or data.get("speaker_identity_from_picture_asserted") is not False
        or data.get("continuous_scene_boundaries_verified") is not False
        or data.get("physical_motion_source_verified") is not False
        or data.get("episode_editor_ready") is not False):
        raise ValueError("Visual report edition, direct observations or non-acceptance status invalid")
    seen=set()
    for obs in items:
        fid=obs.get("frame_id")
        sha=obs.get("source_thumbnail_sha256")
        if (type(fid) is not int or not 1<=fid<=n or fid in seen
            or obs.get("source_requested_ms")!=9000+(fid-1)*18000
            or not isinstance(sha,str) or not re.fullmatch("[a-f0-9]{64}",sha)
            or obs.get("evidence_basis")!="single_original_source_video_thumbnail"
            or obs.get("speaking_identity_verified") is not False
            or obs.get("continuous_action_or_precise_cut_verified") is not False):
            raise ValueError("Wrong original frame, forged PTS, speech or action acceptance")
        seen.add(fid)
    return items,hashlib.sha256(raw).hexdigest(),data


def best_cue_at_or_after(cues,when):
    for cue in cues:
        if cue["start_ms"]>=when:return cue["cue"]
    return cues[-1]["cue"]


def edit(episode,root=ROOT):
    if episode not in SHEETS:raise ValueError("Two pinned pilots only")
    before,original_manifest,review=render_episode(episode,root=root)
    _item,metadata,cues,units,packets=witness(episode,root)
    visual,visual_sha,source=source_visuals(episode,root)
    cue_groups=[f"C{x['cue']:03d}.1" for x in cues]
    for cue_id in cue_groups:
        if before.count(cue_id)!=1:
            raise ValueError("Complete existing original cue draft required")
    # The entire original dialogue remains, verbatim and in order, including
    # the previously produced caption-first script's existing sample notes.
    script=before
    heading="## Working episode dialogue"
    if script.count(heading)!=1:raise ValueError("Unexpected draft structure")
    overview=[
        "## Directly observed original-video scene and setting chronology","",
        "These notes come from the original SHA-verified movie contact sheets.",
        "Each is an *individual frame* at a requested decode offset, not a",
        "motion recording or independently confirmed edit boundary. Dialogue",
        "has not been moved or replaced. Names of persons pictured are not",
        "inferred. The exact source frames remain a private short-lived artifact.",
        ""
    ]
    for entry in visual:
        overview.extend([
          f"**{position(entry['source_requested_ms'])} · frame {entry['frame_id']:03d} · {entry['provisional_location']}**",
          entry["visually_observed_static_description"],
          f"*Original frame SHA-256: \`{entry['source_thumbnail_sha256']}\`*",
          ""
        ])
    script=script.replace(heading,"\n".join(overview)+heading)
    inline=0
    if metadata["timecoded"]:
        # Source-cue timeline is useful for rough notes, but an 18-second
        # frame gap is not a new scene cut. Insert only setting observations,
        # separate from any speaking-turn or cast attribution.
        for entry in visual:
            cue_id=best_cue_at_or_after(cues,entry["source_requested_ms"])
            anchor=f"C{cue_id:03d}.1"
            find=re.search(r"(?m)^\*\*[^\n]*\[C"+re.escape(f"{cue_id:03d}")+r"\.1\s+·\s+[^\n]*\*\*$",script)
            if not find:raise ValueError("Original caption anchor lost for photo note")
            note=(f"*PICTURE [{position(entry['source_requested_ms'])}, original still "
                  f"{entry['frame_id']:03d}]: {entry['visually_observed_static_description']} "
                  f"(Observed static state only, not timed dialogue attribution.)*\n\n")
            script=script[:find.start()]+note+script[find.start():]
            inline+=1
    else:
        # Original page has zero authentic timestamps. Introductory textual
        # beats improve reading without claiming S09 paragraph/AV alignment.
        for cue_id,title in reversed(STORY_BEATS[episode]):
            find=re.search(r"(?m)^\*\*[^\n]*\[C"+f"{cue_id:03d}"+r"\.1\s+·\s+UNTIMED\]\*$",script)
            if not find:raise ValueError("Untimed dialogue chapter anchor lost")
            note=(f"### Editorial story beat · {title}\n\n"
                  "*Heading inferred from source transcript context, NOT a source video cut or original timestamp.*\n\n")
            script=script[:find.start()]+note+script[find.start():]
    # Three narrow *spoken self-introductions* can be tentatively labeled from
    # source dialogue alone, never by recognizing a pictured performer.
    for (cue,part),(label,explanation) in SPEAKING_SELF_LABELS[episode].items():
        patt=re.compile(r"(?m)^\*\*VOICE · CHARACTER TO IDENTIFY\*\*(?=\s+\*\[C"+f"{cue:03d}"+
                        r"\."+str(part)+r"\s+·)")
        script,n=patt.subn("**"+label+" · DIALOGUE-INFERRED, UNCONFIRMED**",script,count=1)
        if n!=1:raise ValueError(f"Self-identifying cue C{cue}.{part} missing")
    caution=(
      "\n## Source-photo and dramatic editing limits\n\n"
      "- Episode-wide source image overview is sampled every eighteen seconds, "
      "not continuous-action surveillance. Fast silent physical gags may be missed.\n"
      "- Speaker names beyond direct spoken self-identification are still unresolved.\n"
      "- The listed source photo locations are visually observed; exact scene "
      "cut times and actor dialogue-to-picture alignment remain provisional.\n"
      "- No source paragraph timecodes have been invented for S09E19.\n"
      "- Full editor-ready screenplay requires substantially more verified "
      "physical comedy, cast dialogue attribution and dialogue-to-scene continuity.\n"
    )
    script=script.rstrip()+caution
    report={
        "schema":"night-court-caption-first-source-photo-scene-edit/2",
        "episode_id":episode,"original_caption_sha256":SOURCE_SHA[episode],
        "original_video_sha256":VIDEO_SHA[episode],
        "original_rendered_caption_cues":len(cues),
        "original_dialogue_text_changed":False,
        "original_source_caption_timestamps_invented":False,
        "original_source_photo_ledger_sha256":visual_sha,
        "whole_episode_original_photo_samples":source["whole_episode_uniform_frames_captured"],
        "directly_inspected_source_photo_observations":len(visual),
        "inserted_original_timed_picture_notes":inline,
        "source_transcript_story_beats":len(STORY_BEATS.get(episode,[])),
        "source_dialogue_self_identification_proposals":len(SPEAKING_SELF_LABELS[episode]),
        "named_speakers_independently_audio_or_video_verified":0,
        "whole_episode_continuous_video_actions_verified":False,
        "complete_live_episode_scene_edges_verified":False,
        "full_episode_editor_ready":False,
        "independent_archival_AV_acceptance":False,
        "draft_status":"SOURCE_DIALOGUE_COMPLETE_VISUAL_SETTING_OUTLINE_REAL_ACTIONS_AND_SPEAKERS_IN_PROGRESS",
        "private_visual_evidence_artifact_id":source["private_thumbnail_artifact_id"]
    }
    return script+"\n",report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--episode",choices=SHEETS.keys(),required=True)
    p.add_argument("--output-root",type=Path,default=ROOT)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    script,report=edit(a.episode)
    dest=a.output_root/"seasons"/a.episode[:3]/a.episode/"derived"/OUTPUT
    outputs={"screenplay-scene-edit.md":script,
             "scene-edit-manifest.json":json.dumps(report,indent=2)+"\n"}
    if a.check:
        for name,content in outputs.items():
            if (dest/name).read_text("utf-8")!=content:
                raise ValueError("Missing/stale original photo-enriched script")
    else:
        dest.mkdir(parents=True,exist_ok=True)
        for name,content in outputs.items():(dest/name).write_text(content,"utf-8")
    print(f"{a.episode}: {report['directly_inspected_source_photo_observations']} "
          "real sampled picture observations; source complete; "
          "speakers/actions and episode publication still unverified")


if __name__=="__main__":
    main()
