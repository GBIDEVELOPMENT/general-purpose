#!/usr/bin/env python3
"""Compose source-complete S09 screenplay and unverified AV lookup as one editorial packet.

Never rewrite original dialogue, create paragraph timestamps, identify voices
from frames, or promote proposed lexical alignment to accepted stage direction.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from build_caption_first_working_drafts import ROOT,SOURCE_SHA
from render_in_scene_stage_directions_v6 import render as render_v6

EP="S09E19"
OUTPUT="caption-first-editor-review-v7"
COARSE="seasons/S09/S09E19/derived/source-coarse-picture-dialogue-review-v1"
def build(root=ROOT):
    draft,base,unknown=render_v6(EP,root)
    folder=root/COARSE
    jbytes=(folder/"review-map.json").read_bytes()
    table=(folder/"picture-to-dialogue-search.md").read_text("utf-8")
    lookup=json.loads(jbytes)
    counts=lookup["counts"]
    if (lookup.get("schema")!="night-court-unverified-coarse-original-picture-dialogue-location-map/1"
        or lookup.get("episode_id")!=EP
        or lookup.get("original_untimed_source_text_sha256")!=SOURCE_SHA[EP]
        or lookup.get("original_video_sha256")!="51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649"
        or lookup.get("source_paragraph_original_timestamps_created") is not False
        or lookup.get("original_picture_video_times_never_become_original_paragraph_times") is not True
        or lookup.get("independent_av_verified") is not False
        or counts.get("total_picture_editorial_review_events")!=18
        or counts.get("review_pointers_with_approximate_paragraph")!=15
        or counts.get("source_picture_events_deferred_without_interpolation")!=3
        or base["source_original_cues"]!=347
        or base["original_source_untimed_video_to_paragraph_alignment_invented"] is not False):
        raise ValueError("Coarse audiovisual appendix cannot be promoted to timed transcript")
    markers=["# S09E19 original audiovisual-to-untimed-transcript editor's review map",
             "ABSTAIN","UNVERIFIED","UNTIMED"]
    if not all(marker in table for marker in markers):raise ValueError("Cautionary evidence labels absent")
    prefix=(
        "\n\n## Appendix: S09E19 original picture-to-untimed-dialogue search guide\n\n"
        "**Editorial convenience only.** The transcript is still UNTIMED. "
        "The 15 suggested paragraph positions are unverified model-anchored "
        "search hints, not timestamps; three picture events intentionally "
        "abstain. Recheck the actual original soundtrack before putting a "
        "specific action beside a spoken line.\n\n"
    )
    combined=draft.rstrip()+prefix+table.rstrip()+"\n"
    proof={
      "schema":"night-court-untimed-screenplay-with-provisional-original-source-review-appendix/7",
      "episode_id":EP,
      "original_source_caption_sha256":SOURCE_SHA[EP],
      "original_source_untimed_paragraphs_preserved":347,
      "sourced_full_dialogue_original_fingerprints_preserved":base["all_v5_original_cue_text_and_fingerprints_preserved"],
      "source_v6_screenplay_sha256":hashlib.sha256(draft.encode()).hexdigest(),
      "existing_coarse_review_map_sha256":hashlib.sha256(jbytes).hexdigest(),
      "source_picture_review_suggestions":15,
      "source_picture_review_abstentions":3,
      "source_paragraph_original_times_invented":False,
      "original_audio_voices_verified":False,
      "source_video_motion_all_episode_verified":False,
      "editor_ready":False,
      "independently_av_certified":False
    }
    return combined,proof

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-root",type=Path,default=ROOT)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    text,proof=build()
    out=a.output_root/"seasons/S09/S09E19/derived"/OUTPUT
    files={"screenplay-and-review-guide.md":text,
           "editorial-manifest.json":json.dumps(proof,indent=2)+"\n"}
    if a.check:
        for name,value in files.items():
            if (out/name).read_text("utf-8")!=value:raise ValueError("Stale manuscript/guide: "+name)
    else:
        out.mkdir(parents=True,exist_ok=True)
        for name,value in files.items():(out/name).write_text(value,encoding="utf-8")
    print("S09E19: intact original dialogue, 15 unverified picture search hints, 3 abstentions.")
if __name__=="__main__":main()
