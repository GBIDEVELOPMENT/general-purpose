#!/usr/bin/env python3
"""Source-neutral proposal map from original S09 AV lexical anchors to pictures.

Uses existing tiny 40-probe *unverified* independent-model review and
directly reviewed original-image manifests. Returns useful paragraph search
ranges for an editor without writing any source paragraph timecode, cut,
speaker or motion acceptance. Does NOT run ASR or download another AVI.
"""
from __future__ import annotations
import argparse
import bisect
import hashlib
import json
from pathlib import Path

from build_caption_first_working_drafts import ROOT,SOURCE_SHA,witness
from render_caption_first_scene_edit_v2 import VIDEO_SHA,source_visuals
from render_caption_first_motion_edit_v3 import evidence as motion_evidence

EP="S09E19"
REPORT="seasons/S09/S09E19/derived/continuous-review-original-v1/source-report.json"
OUTPUT="source-coarse-picture-dialogue-review-v1"
MAX_INTERANCHOR_GAP_MS=300000
EXPECTED_DISTINCT_PROBES=13


def read_original_anchors(root=ROOT):
    file=root/REPORT
    raw=file.read_bytes()
    src=json.loads(raw)
    if (src.get("schema")!="night-court-s09e19-whole-source-once-cross-episode-benchmark/1"
        or src.get("episode_id")!=EP
        or src.get("original_video_sha256")!=VIDEO_SHA[EP]
        or src.get("original_untimed_source_sha256")!=SOURCE_SHA[EP]
        or src.get("original_source_paragraphs")!=347
        or src.get("original_source_paragraphs_with_source_timecodes")!=0
        or src.get("source_untimed_paragraph_timestamps_created") is not False
        or src.get("human_original_audio_listened") is not False
        or src.get("episode_production_script_accepted") is not False):
        raise ValueError("Missing matching explicitly untimed original AV pilot")
    records=src["untimed_paragraph_lexical_candidates"]
    if len(records)!=40:raise ValueError("Original pilot lexical probes changed")
    anchors=[]
    for row in records:
        status=row["lexical_uniqueness_status"]
        if status!="distinct_high_lexical_match_UNVERIFIED":
            continue
        text=row["untimed_original_source_paragraph_candidate"]
        times=row["original_avi_audio_time_proposal_ms"]
        if (not isinstance(text,dict) or not isinstance(times,list)
            or len(times)!=2 or any(type(x) is not int for x in times)
            or not 0<=times[0]<times[1]<=1320144
            or not 1<=text["first"]<=text["last"]<=347
            or row["original_source_paragraph_time_ms"] is not None
            or row["word_identity_original_audio_human_verified"] is not False):
            raise ValueError("False original paragraph source time or word acceptance")
        anchors.append({
            "proposed_original_audio_midpoint_ms":(times[0]+times[1])//2,
            "source_text_paragraph_first":text["first"],
            "source_text_paragraph_last":text["last"],
            "source_text_paragraph_nominal_center":(text["first"]+text["last"])/2,
            "model_consensus_span_index":row["consensus_span_index"],
            "lexical_evidence_status":status,
            "source_audio_human_verified":False
        })
    if len(anchors)!=EXPECTED_DISTINCT_PROBES:
        raise ValueError("Original pilot anchor count changed")
    if any(x["proposed_original_audio_midpoint_ms"]>=y["proposed_original_audio_midpoint_ms"]
           or x["source_text_paragraph_last"]>=y["source_text_paragraph_first"]
           for x,y in zip(anchors,anchors[1:])):
        raise ValueError("Lexical anchor sequence is nonmonotone, cannot interpolate")
    return anchors,hashlib.sha256(raw).hexdigest()


def propose(when_ms,anchors):
    if type(when_ms) is not int or not 0<=when_ms<=1320144:
        raise ValueError("Source video position missing or illegal")
    times=[x["proposed_original_audio_midpoint_ms"] for x in anchors]
    idx=bisect.bisect_left(times,when_ms)
    if idx==0 or idx==len(times):
        return {"status":"ABSTAIN_OUTSIDE_SOURCE_LEXICAL_ANCHORS",
                "paragraph_original_timecode_ms":None,
                "candidate_approx_source_paragraph":None,
                "possible_paragraph_bracket":None}
    left,right=anchors[idx-1],anchors[idx]
    gap=right["proposed_original_audio_midpoint_ms"]-left["proposed_original_audio_midpoint_ms"]
    if gap>MAX_INTERANCHOR_GAP_MS:
        status="ABSTAIN_LEXICAL_GAP_TOO_WIDE"
        guess=None
    else:
        status=("BROAD_UNVERIFIED_REVIEW_POINTER" if gap>120000
                else "SHORT_SPAN_UNVERIFIED_REVIEW_POINTER")
        t=(when_ms-left["proposed_original_audio_midpoint_ms"])/gap
        guess=round(left["source_text_paragraph_nominal_center"]
                    +t*(right["source_text_paragraph_nominal_center"]
                        -left["source_text_paragraph_nominal_center"]))
        guess=max(left["source_text_paragraph_first"],
                  min(right["source_text_paragraph_last"],guess))
    return {
        "status":status,
        "original_picture_time_requested_ms":when_ms,
        "candidate_approx_source_paragraph":guess,
        "possible_paragraph_bracket":[left["source_text_paragraph_first"],
                                      right["source_text_paragraph_last"]],
        "original_paragraph_has_source_timecode":False,
        "paragraph_original_timecode_ms":None,
        "bracketing_lexical_model_audio_midpoints_ms":[
          left["proposed_original_audio_midpoint_ms"],
          right["proposed_original_audio_midpoint_ms"]],
        "bracketing_lexical_source_span_ids":[
          left["model_consensus_span_index"],
          right["model_consensus_span_index"]],
        "interanchor_audio_span_ms":gap,
        "original_audio_soundtrack_listened_to_validate":False,
        "speaker_and_scene_crossmodal_verified":False
    }


def render(root=ROOT):
    _,meta,cues,units,_=witness(EP,root)
    if meta["timecoded"] is not False or len(cues)!=347:
        raise ValueError("Source paragraph boundaries or timing mutated")
    anchors,source_sha=read_original_anchors(root)
    stills,photo_sha,_=source_visuals(EP,root)
    motion,motion_sha,_=motion_evidence(EP,root)
    items=[]
    for row in stills:
        event_id=f"original_source_frame_{row['frame_id']:03d}"
        items.append({
           "kind":"reviewed_single_original_picture",
           "event_id":event_id,
           "source_video_requested_ms":row["source_requested_ms"],
           "picture_review_note":row["visually_observed_static_description"],
           "picture_source_sha256":row["source_thumbnail_sha256"],
           "paragraph_search":propose(row["source_requested_ms"],anchors)
        })
    for row in motion:
        a,b=row["source_window_s"]
        items.append({
          "kind":"reviewed_original_5fps_picture_sequence",
          "event_id":row["window_label"],
          "source_video_requested_ms":((a+b)*1000)//2,
          "picture_review_note":row["stage_direction"],
          "picture_source_sha256":VIDEO_SHA[EP],
          "paragraph_search":propose(((a+b)*1000)//2,anchors)
        })
    items.sort(key=lambda x:x["source_video_requested_ms"])
    counts={
      "original_reviewed_still_notes":len(stills),
      "original_reviewed_motion_sequences":len(motion),
      "original_distinct_text_lexical_anchors":len(anchors),
      "total_picture_editorial_review_events":len(items),
      "review_pointers_with_approximate_paragraph":sum(
           x["paragraph_search"]["candidate_approx_source_paragraph"] is not None for x in items),
      "source_picture_events_deferred_without_interpolation":sum(
           x["paragraph_search"]["candidate_approx_source_paragraph"] is None for x in items)
    }
    report={
        "schema":"night-court-unverified-coarse-original-picture-dialogue-location-map/1",
        "episode_id":EP,
        "original_video_sha256":VIDEO_SHA[EP],
        "original_untimed_source_text_sha256":SOURCE_SHA[EP],
        "original_source_report_sha256":source_sha,
        "source_photo_reviewer_ledger_sha256":photo_sha,
        "source_motion_reviewer_ledger_sha256":motion_sha,
        "source_original_untimed_paragraph_count":347,
        "source_paragraph_original_timestamps_created":False,
        "ASR_consensus_is_not_original_audio_listening_verification":True,
        "original_video_scene_and_character_labels_not_accepted":True,
        "original_picture_video_times_never_become_original_paragraph_times":True,
        "accuracy_note":"Interpolated nominal source paragraph search index only, bracketed by two UNVERIFIED distinct ASR lexical proposals, not a synchronized caption or source timecode.",
        "counts":counts,
        "lexical_source_anchors":anchors,
        "original_picture_search_proposals":items,
        "screenplay_editor_ready":False,
        "independent_av_verified":False
    }
    lines=[
      "# S09E19 original audiovisual-to-untimed-transcript editor's review map","",
      "**Search aid, not paragraph timing, scene boundary or speaking-voice evidence.**",
      "",
      "Original written text has 347 UNTIMED paragraphs. Thirteen unverified",
      "distinct lexical ASR hypotheses provide broad chronological anchor",
      "brackets; within those brackets, interpolation suggests only where an",
      "editor might SEARCH the transcript while reviewing the original video.",
      "Never publish these estimates as caption timestamps or named speakers.",
      "",
      f"Original source AVI SHA: `{VIDEO_SHA[EP]}`",
      f"Original untimed transcript SHA: `{SOURCE_SHA[EP]}`",
      "",
      "## Original scene photographs and short motion passages","",
      "| Original video position | Observed subject | Candidate untimed paragraph | Status / range |",
      "| --- | --- | --- | --- |"
    ]
    for x in items:
        s=x["paragraph_search"]
        when=x["source_video_requested_ms"]
        t=f"{when//60000:02d}:{when%60000/1000:06.3f}"
        estimate=s["candidate_approx_source_paragraph"]
        bracket=s["possible_paragraph_bracket"]
        subject=x["picture_review_note"].split(".")[0][:76].replace("|","/")
        span=(f"C{bracket[0]:03d}–C{bracket[1]:03d}"
              if bracket else "no two-sided anchor")
        lines.append(f"| {t} | {subject} | "+(
          f"C{estimate:03d} (UNVERIFIED)" if estimate is not None else "ABSTAIN")+
          f" | {s['status']}; {span} |")
    lines.extend(["",
      "All candidate paragraph positions are approximate review pointers;",
      "model lexical agreement is not independent original source listening.",
      "Source original paragraph timestamps remain NULL. A pending editor",
      "must inspect real video and soundtrack before relocating or naming",
      "a stage direction inside a specific transcript exchange.",""])
    return report,"\n".join(lines).rstrip()+"\n"


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-root",type=Path,default=ROOT)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    data,text=render()
    out=a.output_root/"seasons/S09/S09E19/derived"/OUTPUT
    outputs={"review-map.json":json.dumps(data,indent=2)+"\n",
             "picture-to-dialogue-search.md":text}
    if a.check:
        for name,body in outputs.items():
            if not (out/name).exists() or (out/name).read_text("utf-8")!=body:
                raise ValueError("Stale original untimed paragraph reviewer mapping "+name)
    else:
        out.mkdir(parents=True,exist_ok=True)
        for name,body in outputs.items():(out/name).write_text(body,encoding="utf-8")
    print("S09E19",data["counts"]["review_pointers_with_approximate_paragraph"],
          "provisional locations,",data["counts"]["source_picture_events_deferred_without_interpolation"],
          "abstentions, ZERO original paragraph timecodes")


if __name__=="__main__":
    main()
