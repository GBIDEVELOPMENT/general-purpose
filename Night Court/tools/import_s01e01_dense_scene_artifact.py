#!/usr/bin/env python3
"""Preserve audited S01E01 dense visual source frames and time-scoped observations.

Input is already downloaded from owner-authorized GitHub Actions artifact
#12542300327 (run #40047395721). No FTP access, no model run, no new video.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"seasons"/"S01"/"S01E01"/"derived"/"scene-review-v2"
SOURCE_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
CAPTION_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
ASR_SHA="234eae34fc5d9ec3a2366a7c26676be1ba4dbb0d5abd97942ba9e93fd0b6409b"
SOURCE_RUN=40047395721
ARTIFACT_ID=12542300327

OBSERVATIONS=[
 {"id":"OBS-V2-01","interval_ms":[76250,76500],
  "description":"The view shifts from the lavender-clad person in front of book shelves to a closer view of the uniformed person.",
  "frame_indices":[6,7],"observation_class":"change_between_adjacent_sampled_shots","confidence":"high"},
 {"id":"OBS-V2-02","interval_ms":[80750,81000],
  "description":"The view changes from the uniformed person's face to the lavender-clad person beside the desk.",
  "frame_indices":[24,25],"observation_class":"change_between_adjacent_sampled_shots","confidence":"high"},
 {"id":"OBS-V2-03","interval_ms":[82500,83750],
  "description":"At the desk, the uniformed person reaches toward the black telephone and raises its handset to the ear.",
  "frame_indices":[31,32,34,36],
  "observation_class":"motion_inferred_from_ordered_sampled_positions","confidence":"high"},
 {"id":"OBS-V2-04","interval_ms":[83750,87250],
  "description":"The uniformed person holds the black telephone receiver against the ear while the lavender-clad person remains on the other side of the desk.",
  "frame_indices":[36,40,44,50],
  "observation_class":"repeated_visible_state_across_frames","confidence":"high"},
 {"id":"OBS-V2-05","interval_ms":[87500,88500],
  "description":"The uniformed person lowers the receiver from the ear toward the telephone on the desktop.",
  "frame_indices":[51,52,54,55],
  "observation_class":"motion_inferred_from_ordered_sampled_positions","confidence":"high"},
 {"id":"OBS-V2-06","interval_ms":[88500,89750],
  "description":"The receiver is down at the desk; the uniformed person straightens while the lavender-clad person remains nearby.",
  "frame_indices":[55,56,59,60],
  "observation_class":"repeated_visible_state_across_frames","confidence":"moderate"}
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check_and_import(source):
    if TARGET.exists():raise ValueError("Derived v2 must not be overwritten")
    report_path=source/"dense-frame-index.json"
    report=json.loads(report_path.read_text("utf-8"))
    if (report["schema"]!="night-court-s01e01-dense-visual-sampling/1" or
        report["source_media_sha256"]!=SOURCE_SHA or
        report["source_time_window_ms"]!=[75000,90000] or
        report["frames_expected"]!=60 or report["frames_actual"]!=60 or
        report["sampling_frames_per_second"]!=4 or
        report["source_video_audio_bytes_in_artifact"] or
        report["audiovisual_episode_completeness_verified"]):
        raise ValueError("Unexpected source packet, edition or claims")
    frames=report["frame_evidence"]
    if len(frames)!=60 or len({x["file"] for x in frames})!=60:
        raise ValueError("Missing or duplicate frames")
    allowed={"dense-frame-index.json","contact-sheet.jpg"} | {x["file"] for x in frames}
    actual={str(p.relative_to(source)) for p in source.rglob("*") if p.is_file()}
    if actual!=allowed:raise ValueError("Unknown additional source files")
    for i,frame in enumerate(frames):
        target=f"sampled-frames/frame-{i+1:03d}.jpg"
        if frame["file"]!=target or frame["frame"]!=i+1:
            raise ValueError("Unexpected frame order/path")
        if frame["approximate_video_time_ms"]!=75000+i*250:
            raise ValueError("Unexpected source sampling time")
        f=source/target
        if f.stat().st_size>150_000 or sha(f)!=frame["sha256"]:
            raise ValueError("Frame SHA/size mismatch")
        if frame["observation_status"]!="not_reviewed" or frame["continuous_motion_proven"]:
            raise ValueError("Source packet overclaims visual review")
    if sha(source/"contact-sheet.jpg")!=report["contact_sheet_sha256"]:
        raise ValueError("Contact montage checksum mismatch")
    if sum(p.stat().st_size for p in source.rglob("*") if p.is_file())>5_000_000:
        raise ValueError("Oversized private frame package")
    asr=json.loads((ROOT/"seasons"/"S01"/"S01E01"/"derived"/"scene-review-v1"/"asr-prosody-hypotheses.json").read_text())
    words=json.loads((ROOT/"seasons"/"S01"/"S01E01"/"derived"/"scene-review-v1"/"word-alignment-review.json").read_text())
    if asr["source_media_sha256"]!=SOURCE_SHA or asr["audio_wav_sha256"]!=ASR_SHA or words["caption_sha256"]!=CAPTION_SHA:
        raise ValueError("Cross-modal audio or source caption provenance mismatch")
    for obs in OBSERVATIONS:
        if not all(1<=f<=60 for f in obs["frame_indices"]):
            raise ValueError("Observation refers to nonexistent frame")
        supported=[frames[n-1]["approximate_video_time_ms"] for n in obs["frame_indices"]]
        if min(supported)<obs["interval_ms"][0] or max(supported)>obs["interval_ms"][1]:
            raise ValueError("Observation's evidence lies outside claimed interval")
    TARGET.mkdir(parents=True)
    shutil.copy2(report_path,TARGET/"dense-frame-index.json")
    shutil.copy2(source/"contact-sheet.jpg",TARGET/"contact-sheet.jpg")
    shutil.copytree(source/"sampled-frames",TARGET/"sampled-frames")
    review={
      "schema":"night-court-visual-motion-review/2",
      "episode_id":"S01E01","source_media_sha256":SOURCE_SHA,
      "source_caption_sha256":CAPTION_SHA,
      "source_workflow_run":SOURCE_RUN,"source_artifact_id":ARTIFACT_ID,
      "review_status":"ai_visual_review_of_sampled_sequence_not_independent_continuous_video_acceptance",
      "review_method":"visual_review_of_4fps_15s_contact_sheet_and_individual_source_frames",
      "speaker_identities_verified":False,"spoken_line_to_mouth_verified":False,
      "scene_heading_status":"provisional_office_setting_from_prior_source_frames",
      "sampling_limitation":"4fps snapshots may omit rapid action and are not exact source PTS measurements",
      "time_scoped_observations":[{
          **x,"supporting_frames":[{"frame":k,"file":frames[k-1]["file"],"source_nominal_ms":frames[k-1]["approximate_video_time_ms"],"sha256":frames[k-1]["sha256"]} for k in x["frame_indices"]]
      } for x in OBSERVATIONS],
      "stage_direction_status":"bounded_visual_motion_observations_only_not_finished_screenplay",
      "edition_match_verified":False,"audiovisual_complete":False
    }
    (TARGET/"visual-motion-observations.json").write_text(json.dumps(review,indent=2,ensure_ascii=False)+"\n","utf-8")
    cues={x["cue"]:x for x in words["cue_turn_packets"]}
    # Do not infer the speaker of a caption line from the nearby body pose.
    eventlist=[]
    for n in range(23,28):
        cue=cues[n]
        eventlist.append((cue["original_caption_interval_ms"][0],
                          {"type":"caption","cue":n,"text":cue["source_cue_text"]}))
    for item in OBSERVATIONS:
        eventlist.append((item["interval_ms"][0],{"type":"visual","item":item}))
    eventlist.sort(key=lambda x:(x[0],0 if x[1]["type"]=="visual" else 1))
    lines=[
      "# S01E01 | early courtroom office scene | dense-motion draft v2",
      "",
      "**INT. BOOK-LINED COURT OFFICE – TIME OF DAY UNVERIFIED**",
      "",
      "> SOURCE-LINKED EXCERPT ONLY. The visual stage directions below describe",
      "> changes observed at 4fps, not certified continuous-motion or speaker attribution.",
      "> Source SRT times are not independently aligned to the source cut.",
      "",
      "A desk holds papers, folders, and a black telephone. An adult in lavender",
      "stands near the desk opposite a uniformed adult.",
      "",
      "### Timeline, ~01:15–01:30", ""
    ]
    for ms,event in eventlist:
        if event["type"]=="caption":
            n=event["cue"]
            lines += [f'**{ms/1000:.3f}s | C{n:04d} | SPEAKER UNVERIFIED:**',
                     event["text"],""]
        else:
            ob=event["item"]
            fnums=", ".join("F"+str(n).zfill(3) for n in ob["frame_indices"])
            lines += [f'*[{ms/1000:.3f}–{ob["interval_ms"][1]/1000:.3f}s, {ob["id"]}; {fnums}]*',
                     "*"+ob["description"]+"*",""]
    lines+=["### Why this is not a finished script","",
      "The visual action is limited to the sampled interval. Stage directions are",
      "source-frame supported but not independently reviewed against continuous video.",
      "Neither face/mouth movement nor costume establishes which character spoke.",
      "Cue words and model timestamps remain separate, uncertain witnesses.",
      "The full episode and its source edition are not certified AV-complete.",
      "",
      f"Media SHA-256: \u0060{SOURCE_SHA}\u0060",
      f"Subtitle SHA-256: \u0060{CAPTION_SHA}\u0060",
      f"Acquisition: GitHub Actions run #{SOURCE_RUN}, artifact #{ARTIFACT_ID}.",""]
    (TARGET/"scene-source-motion-v2.md").write_text("\n".join(lines),"utf-8")
    print("Integrated 60 SHA-verified stills, one montage, six time-scoped visual observations and one limited script excerpt")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: import_s01e01_dense_scene_artifact.py DIRECTORY")
    check_and_import(Path(sys.argv[1]))
