#!/usr/bin/env python3
"""Add directly reviewed original-picture motion notes to two caption-first pilots.

Preserves every original caption-derived dialogue turn in the v2 screenplay.
Source samples are frames at 5fps; speaker identity, sound, native PTS
and complete physical-comedy coverage remain explicitly unverified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from render_caption_first_scene_edit_v2 import ROOT, edit as edit_v2, witness, VIDEO_SHA
from build_caption_first_working_drafts import SOURCE_SHA

OUTPUT="caption-first-physical-business-v3"
SOURCE="physical-motion-original-v1/observations.json"
WINDOWS={
    "S01E01":{"court-office-open-window-action":(160,182,110,3),
              "court-bench-posture":(1258,1278,100,2)},
    "S09E19":{"brief-floor-spark":(684,704,100,2),
              "restaurant-dance-business":(951,971,100,2)}
}


def timestamp(seconds):
    minutes,secs=divmod(seconds,60)
    return f"{minutes:02}:{secs:02}"


def evidence(episode, root=ROOT):
    if episode not in WINDOWS:
        raise ValueError("Only pinned 1984-series original pilots")
    path=root/"seasons"/episode[:3]/episode/"derived"/SOURCE
    binary=path.read_bytes()
    record=json.loads(binary)
    rows=record.get("sequences")
    if (record.get("schema")!="night-court-original-5fps-source-picture-physical-beat-annotations/1"
        or record.get("episode_id")!=episode
        or record.get("original_source_video_sha256")!=VIDEO_SHA[episode]
        or record.get("original_source_caption_sha256")!=SOURCE_SHA[episode]
        or record.get("original_motion_coverage_run_id")!=40139082891
        or record.get("nominal_sampling_fps")!=5
        or record.get("sequence_count")!=2
        or not isinstance(rows,list) or len(rows)!=2
        or record.get("source_original_audio_listened_during_picture_annotation") is not False
        or record.get("named_actors_or_voices_identified") is not False
        or record.get("full_motion_or_scene_completeness_claimed") is not False
        or record.get("local_visual_inspection_of_sampled_original_motion_sheet") is not True):
        raise ValueError("Wrong or deceptively accepted motion source evidence")
    seen=set()
    for row in rows:
        name=row.get("window_label")
        if name not in WINDOWS[episode] or name in seen:
            raise ValueError("Unknown or duplicate original physical-business window")
        seen.add(name)
        start,stop,count,sheets=WINDOWS[episode][name]
        sheet_list=row.get("sheets")
        if (row.get("source_window_s")!=[start,stop]
            or row.get("sampled_frames")!=count
            or row.get("original_source_timing_kind")!="requested_source_position_no_native_frame_PTS_verification"
            or row.get("source_video_sha256")!=VIDEO_SHA[episode]
            or row.get("source_picture_observation_status")!="reviewed_bounded_still_sequence_not_audio_verified"
            or row.get("source_drama_beat_text_is_an_editorial_paraphrase") is not True
            or not isinstance(sheet_list,list) or len(sheet_list)!=sheets
            or any(not re.fullmatch(r"[a-f0-9]{64}",x.get("sha256",""))
                   or not x.get("file","").endswith(".jpg") for x in sheet_list)
            or not isinstance(row.get("stage_direction"),str)
            or len(row["stage_direction"])>1200):
            raise ValueError("Modified original source window or ungrounded stage direction")
    return rows, hashlib.sha256(binary).hexdigest(),record


def closest_original_cue(cues,second):
    assert cues[0]["start_ms"] is not None
    for cue in cues:
        if cue["start_ms"]>=second*1000:
            return cue["cue"]
    return cues[-1]["cue"]


def render(episode,root=ROOT):
    old,prior=edit_v2(episode,root=root)
    _i,meta,cues,units,_packs=witness(episode,root=root)
    rows,sha,record=evidence(episode,root=root)
    total=len(cues)
    for cue in cues:
        key=f"C{cue['cue']:03d}.1"
        # Original cue is present once in *caption dialogue*; existing
        # picture evidence can mention other C IDs, hence exact bracket regex.
        if not re.search(r"\[C"+f"{cue['cue']:03d}"+r"\.1 · (?:UNTIMED|\d{2}:\d{2}\.\d{3})\]",old):
            raise ValueError("Original complete-caption dialogue cue vanished")
    header="## Working episode dialogue"
    if old.count(header)!=1:raise ValueError("Unexpected original draft headings")
    lines=[
      "## Actual source-picture physical business · 5fps scene review","",
      "The following stage-direction proposals are based on directly inspected",
      "short ORIGINAL AVI image sequences, not subtitle deductions.",
      "Source timestamps describe requested video decode positions, not",
      "verified native PTS or synchronized original dialogue.",
      "Facial/voice identity, sound, emotion and full-runtime action",
      "completeness remain **pending**.",
      ""
    ]
    for row in rows:
        start,stop=row["source_window_s"]
        lines.extend([
            f"### {timestamp(start)}–{timestamp(stop)} · {row['setting']}",
            "",
            f"*{row['stage_direction']}*",
            "",
            f"*Picture-only limitation: {row['notes']}*",
            f"*Evidence: original video SHA \`{VIDEO_SHA[episode]}\`, "
            f"window \`{row['window_label']}\`, 5fps, "
            f"{row['sampled_frames']} frames, "
            f"{len(row['sheets'])} private contact sheets.*",
            ""
        ])
    result=old.replace(header,"\n".join(lines)+header)
    inline_count=0
    if meta["timecoded"]:
        for row in rows:
            start,_stop=row["source_window_s"]
            cue=closest_original_cue(cues,start)
            patt=(r"(?m)^\*\*[^\n]*\*\*\s+\*\[C"+
                  f"{cue:03d}"+r"\.1 · \d{2}:\d{2}\.\d{3}\]\*$")
            match=re.search(patt,result)
            if not match:raise ValueError("Original SRT source cue anchor not found")
            note=(f"*PHYSICAL ACTION SAMPLE [{timestamp(start)}, "
                  f"original picture]: {row['stage_direction']} "
                  f"(Video frames reviewed at 5fps; speaker/sound not verified.)*\n\n")
            result=result[:match.start()]+note+result[match.start():]
            inline_count+=1
    # For original UNTImed text, NEVER align an AV time to a paragraph
    # or insert a stage direction beside a specific source dialogue line.
    foot=(
      "\n## Additional original-video physical-business review boundary\n\n"
      "These four story moments have been independently inspected as *sampled"
      " original picture sequences*, not as synchronized source audio+video. "
      "No whole-episode physical-action, named speaker, dramatic causality,"
      " accurate cut position or independently certified script is claimed.\n"
    )
    result=result.rstrip()+"\n"+foot
    report={
      "schema":"night-court-caption-first-original-video-physical-business-draft/3",
      "episode_id":episode,
      "original_source_caption_sha256":SOURCE_SHA[episode],
      "original_source_video_sha256":VIDEO_SHA[episode],
      "complete_original_held_caption_cues":total,
      "all_original_dialogue_preserved_from_v2":True,
      "original_motion_picture_review_ledger_sha256":sha,
      "source_motion_artifact_zip_sha256":record["private_original_artifact_zip_sha256"],
      "source_motion_private_artifact_id":record["original_private_image_artifact_id"],
      "reviewed_picture_windows":len(rows),
      "source_motion_frames_reviewed_in_bounded_sequences":sum(r["sampled_frames"] for r in rows),
      "source_picture_window_seconds":sum(r["source_window_s"][1]-r["source_window_s"][0] for r in rows),
      "script_inline_original_timed_action_notes":inline_count,
      "untimed_paragraph_source_timecode_fabricated":False,
      "speaker_name_from_original_picture_guessed":False,
      "source_original_audio_listened_for_four_sequences":False,
      "full_episode_setting_scene_spatial_coverage_verified":False,
      "full_episode_important_physical_comedy_coverage_verified":False,
      "editor_ready":False,
      "independent_AV_certified":False,
      "status":"SOURCE_DIALOGUE_COMPLETE_ORIGINAL_PICTURE_ACTION_EXCERPTS_EDITORIAL_REVIEW_PENDING"
    }
    return result.rstrip()+"\n",report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--episode",choices=sorted(WINDOWS),required=True)
    ap.add_argument("--output-root",type=Path,default=ROOT)
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    text,metadata=render(args.episode)
    out=args.output_root/"seasons"/args.episode[:3]/args.episode/"derived"/OUTPUT
    expected={"screenplay-motion-edit.md":text,
              "motion-edit-manifest.json":json.dumps(metadata,ensure_ascii=False,indent=2)+"\n"}
    if args.check:
        for name,content in expected.items():
            file=out/name
            if not file.is_file() or file.read_text("utf-8")!=content:
                raise ValueError(f"Missing/stale original-source physical-business draft {name}")
    else:
        out.mkdir(parents=True,exist_ok=True)
        for name,content in expected.items():
            (out/name).write_text(content,encoding="utf-8")
    print(args.episode,metadata["complete_original_held_caption_cues"],
          "complete held source cues;",
          metadata["reviewed_picture_windows"],"reviewed physical picture windows,",
          "still no comprehensive motion/speaking AV approval.")


if __name__=="__main__":
    main()
