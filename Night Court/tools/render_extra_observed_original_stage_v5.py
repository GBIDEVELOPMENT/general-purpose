#!/usr/bin/env python3
"""Add newly *inspected* original AVI 5fps stage-picture business to two scripts.

Only S01 source SRT has authentic cue times for nearby insertion. S09 has
347 UNTIMED transcript paragraphs: its source-film observations stay in a
separate chronology, especially two review targets proven wrong by pictures.
Never conflate faces, voices, source cue times, or verified continuous shots.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from build_s01_quote_correction_v4 import render as s01
from build_s09_impostor_speaking_reader_v4 import render as s09
from build_caption_first_working_drafts import ROOT,SOURCE_SHA,witness

OUTPUT="additional-original-film-staged-reader-v5"
MOVIE_SHA={
"S01E01":"5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962",
"S09E19":"51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649"
}
REPORT_SHA={
"S01E01":"cafd8cc45292f26f72683a0140dfc3c538421219bfbfea53e1e41efa33aede09",
"S09E19":"f229ff8aa8b376426384569d973c5868563efe6fb043040c98fb80887f9b3f86"
}
EXPECTED={"S01E01":404,"S09E19":347}


def observed(ep,root=ROOT):
    path=root/"seasons"/ep[:3]/ep/"derived/additional-original-motion-observations-v2/observations.json"
    binary=path.read_bytes()
    doc=json.loads(binary)
    rows=doc.get("observations")
    if (doc.get("schema")!="night-court-extra-5fps-actually-reviewed-original-physical-observations/1"
        or doc.get("episode_id")!=ep
        or doc.get("source_video_sha256")!=MOVIE_SHA[ep]
        or doc.get("original_caption_sha256")!=SOURCE_SHA[ep]
        or doc.get("source_private_gha_run_id")!=40161079027
        or doc.get("source_private_sample_evidence_report_sha256")!=REPORT_SHA[ep]
        or doc.get("nominal_original_source_fps")!=5
        or doc.get("images_inspected_total")!=300
        or doc.get("actors_identified_from_images") is not False
        or doc.get("original_synchronized_audio_listened") is not False
        or doc.get("native_original_video_pts_verified") is not False
        or doc.get("continuous_full_episode_action_verified") is not False
        or doc.get("original_source_text_or_cue_timing_changed") is not False
        or not isinstance(rows,list) or len(rows)!=3):
        raise ValueError("Original video image observations source/provenance drift")
    for row in rows:
        a,b=row["window"]
        if (type(a) is not int or type(b) is not int
            or b-a!=20 or row["frame_count"]!=100
            or row["source_video_sha256"]!=MOVIE_SHA[ep]
            or row["screenplay_action_status"]!="PICTURE_OBSERVATION_ONLY_UNCERTIFIED"
            or row["source_frame_time_kind"]!="requested_ffmpeg_source_offset_5fps_not_native_pts_or_spoken_caption_sync"
            or len(row["contact_sheet_sha"])!=2
            or any(not re.fullmatch("[a-f0-9]{64}",s) for s in row["contact_sheet_sha"])
            or not row["physical_action"] or not row["observed_location"]
            or type(row["hypothesis_supported"]) is not bool):
            raise ValueError("Invalid sampled original physical stage passage")
    if ep=="S09E19" and [x["hypothesis_supported"] for x in rows]!=[False,False,False]:
        raise ValueError("Do not report observed safe or arrival that is not in source pictures")
    return rows,hashlib.sha256(binary).hexdigest()


def speaker_index(ep,doc):
    if ep=="S01E01":return doc["reversible_dialogue_source_index"]
    return doc["source_reading_index"]


def source_counts(ep,idx,root=ROOT):
    _,meta,cues,units,_=witness(ep,root)
    if meta["timecoded"] is not (ep=="S01E01"):
        raise ValueError("Source cue date/time status altered")
    seen=[]
    unit_hashes=[]
    for row in idx:
        ref=row["source_ref"]
        match=re.fullmatch(r"C(\d{3})\.(\d+)(?:–C(\d{3})\.(\d+))?",ref)
        if match is None:raise ValueError("Invalid source cue part provenance: "+ref)
        a,part,b,last=match.groups()
        if part!="1" and b is not None:raise ValueError("Ambiguous multi-part source range")
        items=[(int(a),int(part))] if b is None else [
            (i,1) for i in range(int(a),int(b)+1)]
        seen.extend(items)
    if seen!=[(u["cue"],u["part"]) for u in units]:
        raise ValueError("Reading edition loses or duplicates original source speaking units")
    named=sum((not row["speaker"].startswith("UNIDENTIFIED"))*
              (int(row["source_ref"].split("–C")[1].split(".")[0])-
               int(row["source_ref"][1:].split(".")[0])+1
               if "–C" in row["source_ref"] else 1) for row in idx)
    if named+sum(row["speaker"].startswith("UNIDENTIFIED")*
              (int(row["source_ref"].split("–C")[1].split(".")[0])-
               int(row["source_ref"][1:].split(".")[0])+1
               if "–C" in row["source_ref"] else 1) for row in idx)!=len(units):
        raise ValueError("Incomplete source reading attr count")
    return len(cues),len(units),named,len(units)-named


def wrap_event(item,ep):
    t0,t1=item["window"]
    picture=item["physical_action"].strip()
    return (
      f"**Source-video observed stage business ({t0//60:02d}:{t0%60:02d}–"
      f"{t1//60:02d}:{t1%60:02d}; 5fps sampled picture, not sound):** "
      +picture+"\n\n"
      +f"*Original AVI SHA: `{MOVIE_SHA[ep]}`; evidence target: "
      +f"`{item['label']}`; source focus matched: "
      +("yes" if item["hypothesis_supported"] else "NO")
      +". This is a picture-only observation, not an exact native frame PTS, "
      +"character identification, verified cut or subtitle synchronization.*"
    )


def render(ep,root=ROOT):
    if ep not in EXPECTED:raise ValueError("Only original pilots")
    body,index=(s01(root) if ep=="S01E01" else s09(root))
    readings=speaker_index(ep,index)
    cues,units,named,unknown=source_counts(ep,readings,root)
    if units!=EXPECTED[ep]:raise ValueError("Original source dialogue count changed")
    observations,evidence_sha=observed(ep,root)
    generated=body
    inserts=[]
    if ep=="S01E01":
        # Align picture observations only to NEARBY ORIGINAL SRT cues,
        # without asserting that pictured gestures caused that dialogue.
        __,___,source_cues,____,_____=witness(ep,root)
        for item in reversed(observations):
            at=item["window"][0]*1000
            candidate=next((cue for cue in source_cues if cue["start_ms"]>=at),
                           source_cues[-1])
            row=next((x for x in readings if x["source_ref"].startswith(
                f"C{candidate['cue']:03d}.")),None)
            if row is None:raise ValueError("Missing SRT source locator")
            # Preserve exact existing source dialogue, inserting only one
            # explicitly picture-only paragraph at existing speaker heading.
            lines=generated.splitlines()
            old_header=row["speaker"].upper()
            # Reverse chronological insertion keeps all earlier SRT
            # reading-line offsets unchanged, even with repeated speakers.
            base_line=row["reading_line"]+3
            original_lines=body.splitlines()
            if base_line>=len(original_lines) or original_lines[base_line]!=old_header:
                raise ValueError("Original source SRT dialogue reading index drift")
            line_index=base_line
            if line_index>=len(lines) or lines[line_index]!=old_header:
                raise ValueError("Source picture insertion offset drift")
            passage=wrap_event(item,ep)
            lines[line_index:line_index]=["",passage,
                "*Nearby SRT reading locator only. The sampled original picture "
                "has not been aligned to a specific spoken word or character.*",""]
            generated="\n".join(lines)+"\n"
            inserts.append({"window_label":item["label"],
                "original_source_srt_cue":candidate["cue"],
                "picture_time_ms_requested":at,
                "original_srt_source_start_ms":candidate["start_ms"],
                "visual_hypothesis_observed":item["hypothesis_supported"],
                "original_source_cue_time_replaced":False,
                "spoken_source_alignment_verified":False})
    else:
        generated+="\n## Additional original film picture-only scene chronology\n\n"
        generated+=(
            "The original 347 dialogue paragraphs are UNTIMED. These reviewed "
            "original video positions are **not paragraph timecodes**. The "
            "two targeted safe events were NOT visible at the selected "
            "positions; preserve these failures rather than inventing action.\n\n")
        for item in observations:
            generated+=wrap_event(item,ep)+"\n\n"
            for limit in item["limitations"]:
                generated+="*Evidence limitation: "+limit+"*\n\n"
            inserts.append({"window_label":item["label"],
                "picture_time_ms_requested":item["window"][0]*1000,
                "visual_hypothesis_observed":item["hypothesis_supported"],
                "original_text_paragraph_time_ms":None,
                "spoken_source_alignment_verified":False})
    generated=generated.rstrip()+"\n"
    report={"schema":"night-court-actual-source-video-stage-reader/5",
       "episode_id":ep,"original_caption_sha256":SOURCE_SHA[ep],
       "original_source_video_sha256":MOVIE_SHA[ep],
       "input_original_reading_script_sha256":hashlib.sha256(body.encode()).hexdigest(),
       "new_source_observation_ledger_sha256":evidence_sha,
       "source_original_cues":cues,"source_original_speaking_units":units,
       "original_reading_blocks":len(readings),
       "source_speaking_units_attributed_provisionally":named,
       "source_speaking_units_unidentified":unknown,
       "directly_inspected_new_5fps_frames":300,
       "new_original_picture_stage_windows":len(observations),
       "source_movie_frame_windows_proving_original_target":sum(x["hypothesis_supported"] for x in observations),
       "source_movie_frame_windows_rejecting_review_target":sum(not x["hypothesis_supported"] for x in observations),
       "source_picture_insertions_or_chronology_entries":inserts,
       "speaker_and_actor_identity_from_photographs_claimed":False,
       "original_dialogue_words_edited":False,
       "source_untimed_captions_given_timecodes":False,
       "original_synchronized_audio_listened":False,
       "continuous_whole_episode_video_reviewed":False,
       "full_episode_editor_ready":False,"independently_av_certified":False}
    return generated,report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--episode",choices=sorted(EXPECTED),required=True)
    p.add_argument("--output-root",type=Path,default=ROOT)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    screenplay,index=render(args.episode)
    folder=args.output_root/"seasons"/args.episode[:3]/args.episode/"derived"/OUTPUT
    values={"screenplay-extra-observed-business.md":screenplay,
            "source-picture-stage-index.json":json.dumps(index,indent=2,ensure_ascii=False)+"\n"}
    if args.check:
        for name,value in values.items():
            if (folder/name).read_text("utf-8")!=value:
                raise ValueError("Source stage screenplay output changed: "+name)
    else:
        folder.mkdir(parents=True,exist_ok=True)
        for name,value in values.items():
            (folder/name).write_text(value,encoding="utf-8")
    print(args.episode,"new source picture stage windows",
          index["new_original_picture_stage_windows"],
          "provisionally named source units",index["source_speaking_units_attributed_provisionally"],
          "unresolved source units",index["source_speaking_units_unidentified"],
          "no original source timecodes invented")


if __name__=="__main__":
    main()
