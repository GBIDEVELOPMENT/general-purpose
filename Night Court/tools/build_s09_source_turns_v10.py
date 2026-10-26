#!/usr/bin/env python3
"""Reunite one strongly source-text-backed original S09 speaking turn, P0 first.

The original untimed paragraphs C266.1 and C267.1 are consecutive halves of
one complete sentence in the held original source. The second half carries a
provisional, real-original-audio-supported Roz voice candidate. This creates
one provisional joined reading turn with TWO preserved original source cue
parts, never edits the original 347 paragraphs, and never claims source audio
actor/true turn verification. All other v9 role entries stay byte-for-byte in
their JSON content apart from re-serializing with identical values.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from build_pilot_fan_beat_cards import ROOT,load_witness

SCHEMA="night-court-private-s09-source-provisional-same-turn-v10/1"
INPUT_ROWS="pilot-current-source-first-s09-audio-v9.jsonl"
INPUT_MANIFEST="pilot-current-speaker-s09-audio-v9-manifest.json"
OUTPUT_ROWS="pilot-current-source-turns-v10.jsonl"
OUTPUT_MANIFEST="pilot-current-source-turns-v10-manifest.json"
FROM="C266.1"
TO="C267.1"
JOINED="C266.1–C267.1"
STATUS="syntactic_and_source_voice_continuation_proposal_not_audio_verified"
EXPECTED_FIRST="You ever make a huge mistake you knew you were going to end up regretting"
EXPECTED_SECOND="every minute for the rest of your life?"
SHA="659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()


def merge_v9(rows:list[dict], strict:bool=True)->tuple[list[dict],dict]:
    hits={}
    for i,r in enumerate(rows):
        if r["episode_id"]=="S09E19" and r["source_reading_ref"] in (FROM,TO):
            key=r["source_reading_ref"]
            if key in hits:
                raise ValueError("More than one old source reading for S09 sentence")
            hits[key]=(i,r)
    if set(hits)!={FROM,TO}:
        raise ValueError("Exact original S09 continuation cues not found")
    ia,a=hits[FROM]
    ib,b=hits[TO]
    if (ia+1!=ib or a["original_source_part_refs"]!=[FROM]
        or b["original_source_part_refs"]!=[TO]
        or a["caption_text"]!=EXPECTED_FIRST
        or b["caption_text"]!=EXPECTED_SECOND
        or a["candidate_role"] is not None
        or a["role_attribution_status"]!="unidentified"
        or b["candidate_role"]!="ROZ RUSSELL"
        or b["role_attribution_status"]!="original_soundtrack_acoustic_context_proposal_not_independent_avi_id"
        or b.get("speaker_identity_provisional_from_model_and_context") is not True
        or a["original_source_sha256"]!=SHA or b["original_source_sha256"]!=SHA
        or a.get("source_original_times_ms") is not None
        or b.get("source_original_times_ms") is not None
        or a.get("original_source_untimed") is not True
        or b.get("original_source_untimed") is not True
        or a.get("speaker_turn_boundary_verified") is not False
        or b.get("speaker_turn_boundary_verified") is not False
        or a.get("actor_face_or_voice_independently_verified") is not False
        or b.get("actor_face_or_voice_independently_verified") is not False):
        raise ValueError("P0 same-speaker proposal no longer source-consistent, requires independent review")
    joined=dict(a)
    joined.update({
        "reading_block_id":a["reading_block_id"]+":source-turn-v10",
        "source_reading_ref":JOINED,
        "original_source_part_refs":[FROM,TO],
        "candidate_role":"ROZ RUSSELL",
        "role_attribution_status":STATUS,
        "caption_text":a["caption_text"]+" "+b["caption_text"],
        "original_reading_block_sha256":sha(
            (a["caption_text"]+" "+b["caption_text"]).encode("utf-8")),
        "merged_original_speaking_units_previously_unidentified":[FROM],
        "merged_provisional_previous_role_source_ref":TO,
        "original_source_part_original_text_sha256":[
            sha(a["caption_text"].encode("utf-8")),
            sha(b["caption_text"].encode("utf-8")),
        ],
        "previous_v9_reading_block_ids":[a["reading_block_id"],b["reading_block_id"]],
        "source_text_join_separator":" ",
        "source_original_times_ms":None,
        "original_source_untimed":True,
        "speaker_turn_boundary_verified":False,
        "actor_face_or_voice_independently_verified":False,
        "same_original_soundtrack_speaker_not_independently_verified":True,
        "independent_filmed_performance_turn_proven":False,
        "source_role_inherited_from_adjoining_acoustic_candidate":True,
        "source_original_audio_model_report_sha256":b.get("source_acoustic_numeric_report_sha256"),
        "source_S09_C189_C190_mixed_voices_still_unreviewed":True,
    })
    result=rows[:ia]+[joined]+rows[ib+1:]
    if len(result)!=len(rows)-1:
        raise ValueError("P0 source join lost/duplicated an unrelated speaking block")
    original_keys={(r["episode_id"],ref) for r in rows
                   for ref in r["original_source_part_refs"]}
    new_keys=defaultdict(set)
    for r in result:
        for ref in r["original_source_part_refs"]:
            new_keys[(r["episode_id"],ref)].add(r["candidate_role"])
    if set(new_keys)!=original_keys:
        raise ValueError("Lost or fabricated original caption unit")
    named=sum(None not in names for names in new_keys.values())
    summary={
        "schema":SCHEMA,
        "original_caption_immutable_source_units":len(new_keys),
        "current_provisional_character_named_original_units":named,
        "still_unknown_original_source_units":len(new_keys)-named,
        "reader_speaker_turn_blocks_before":len(rows),
        "reader_speaker_turn_blocks_after":len(result),
        "one_joined_source_turn_refs":[FROM,TO],
        "source_single_sentence_still_not_verified_performance_turn":True,
        "source_audio_human_actor_identity_confirmations_added":0,
        "original_S09_transcript_still_untimed":True,
        "other_cues_changed":False,
    }
    if strict and (len(rows),len(result),len(new_keys),named,len(new_keys)-named)!=(716,715,751,591,160):
        raise ValueError("Original source turn identity or current role totals drift")
    return result,summary


def build(root:Path,v9:Path,output:Path)->dict:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private full episode dialogue cannot enter Git")
    old=(v9/INPUT_ROWS).read_bytes()
    m=json.loads((v9/INPUT_MANIFEST).read_text("utf-8"))
    if (sha(old)!=m.get("current_source_roles_sha256")
        or m.get("original_source_caption_units")!=751
        or m.get("current_working_named_provisional_original_units")!=590
        or m.get("unidentified_original_cue_units")!=161
        or m.get("quarantined_suspicious_model_proposals")!=1
        or m.get("original_audio_human_identified_characters_added")!=0):
        raise ValueError("Private v9 original-source speaker bank not verified")
    metadata,_=load_witness(root,"S09E19")
    if metadata["sha256"]!=SHA or metadata["timecoded"] is not False:
        raise ValueError("Original S09 caption witness changed")
    rows=[json.loads(x) for x in old.decode("utf-8").splitlines() if x.strip()]
    result,summary=merge_v9(rows)
    output.mkdir(parents=True,exist_ok=True)
    serialized="".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in result)
    (output/OUTPUT_ROWS).write_text(serialized,"utf-8")
    summary["current_source_role_records_sha256"]=sha(serialized.encode("utf-8"))
    summary["input_v9_role_records_sha256"]=sha(old)
    summary["generated_reader_sha256_by_episode"]={}
    for ep in ("S01E01","S09E19"):
        episode_meta=load_witness(root,ep)[0]
        lines=[f"# {ep}: original Night Court source-first provisional speaking turns v10","",
            "Original caption/source units are exactly preserved. Same-speaker grouping",
            "and all character names are EDITORIAL proposals, not independently",
            "original-video/audio-confirmed performance turns.",
            f"Original episode caption SHA256: {episode_meta['sha256']}",""]
        for r in result:
            if r["episode_id"]!=ep:continue
            role=r["candidate_role"] or "UNIDENTIFIED SPEAKER"
            lines += [f"### {r['source_reading_ref']} ({', '.join(r['original_source_part_refs'])})",
                      role+" · "+r["role_attribution_status"],
                      r["caption_text"],""]
        text="\n".join(lines).rstrip()+"\n"
        (output/f"{ep}-source-turns-v10.md").write_text(text,"utf-8")
        summary["generated_reader_sha256_by_episode"][ep]=sha(text.encode("utf-8"))
    (output/OUTPUT_MANIFEST).write_text(
        json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n","utf-8")
    return summary


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--v9",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    r=build(args.root,args.v9,args.output)
    print("Original series source-led P0 provisional reading: "
          f"{r['current_provisional_character_named_original_units']}/751 named source-unit proposals, "
          f"{r['still_unknown_original_source_units']} UNKNOWN; "
          "one original S09 syntactic same-speaker continuation joined, 0 independent actor IDs certified")


if __name__=="__main__":
    main()
