#!/usr/bin/env python3
"""Reversible P0 original S01E01 C219 dash-separated speaking-turn proposal.

This operates on the private current source-first reader, not on the frozen
SRT. The SRT provides one 879532–882330ms *cue* window with two apparent
voices, but cannot time those separate performances or identify their actors.
Consequently both candidate speaker labels stay UNKNOWN.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from build_pilot_fan_beat_cards import ROOT, load_witness

SCHEMA="night-court-private-s01-c219-two-unknown-turns/1"
BEFORE="pilot-source-turn-amendments.jsonl"
BEFORE_MANIFEST="pilot-source-turn-amendments-manifest.json"
AFTER="pilot-source-episode-turns-v15.jsonl"
AFTER_MANIFEST="pilot-source-episode-turns-v15-manifest.json"
SOURCE_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
SOURCE_REF="C219.1"
SPLIT_BEFORE="- Yeah."
EXPECTED_START=879532
EXPECTED_END=882330
EXPECTED_STATUS="unidentified"

def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def split(rows:list[dict],source_text:str,strict:bool=True)->tuple[list[dict],dict]:
    candidates=[(n,row) for n,row in enumerate(rows)
                if row["episode_id"]=="S01E01" and row["source_reading_ref"]==SOURCE_REF]
    if len(candidates)!=1:
        raise ValueError("Expected exactly one original S01 C219 reading block")
    pos,original=candidates[0]
    if (original.get("original_source_sha256")!=SOURCE_SHA
        or original.get("original_source_part_refs")!=[SOURCE_REF]
        or original.get("candidate_role") is not None
        or original.get("role_attribution_status")!=EXPECTED_STATUS
        or original.get("actor_face_or_voice_independently_verified") is not False
        or original.get("speaker_turn_boundary_verified") is not False
        or original.get("caption_text")!=source_text
        or source_text.count(SPLIT_BEFORE)!=1):
        raise ValueError("Original S01 caption C219 or prior speaker identity changed")
    at=source_text.index(SPLIT_BEFORE)
    if not 0<at<len(source_text):
        raise ValueError("Original S01 speaker handoff at invalid position")
    chunks=[(0,at,source_text[:at]),(at,len(source_text),source_text[at:])]
    if not all(part.strip() for _,_,part in chunks):
        raise ValueError("Empty original source speech candidate")
    if "".join(part for _,_,part in chunks)!=source_text:
        raise ValueError("Original S01 source words were altered")
    output=[]
    for i,(a,b,txt) in enumerate(chunks,1):
        row=dict(original)
        row.update({
            "reading_block_id":f"S01E01:source-P0-C219:unverified-turn-{i}",
            "source_reading_ref":f"S01E01-C219-SOURCE-TURN-{i}",
            "original_source_part_refs":[SOURCE_REF],
            "caption_text":txt,
            "candidate_role":None,
            "role_attribution_status":"unidentified",
            "speaker_turn_boundary_verified":False,
            "actor_face_or_voice_independently_verified":False,
            "independent_original_audio_voice_identification":False,
            "original_source_cue_start_ms":EXPECTED_START,
            "original_source_cue_end_ms":EXPECTED_END,
            "source_original_cue_bounds_not_subturn_alignment":True,
            "source_exact_character_span":{
                "original_source_ref":SOURCE_REF,"start_char":a,"end_char":b,
                "exact_text_sha256":sha(txt.encode("utf-8"))
            },
            "original_two_actor_turns_not_independently_AV_verified":True
        })
        output.append(row)
    changed=rows[:pos]+output+rows[pos+1:]
    keys=defaultdict(set)
    original_keys={(row["episode_id"],ref) for row in rows
                   for ref in row["original_source_part_refs"]}
    for row in changed:
        for ref in row["original_source_part_refs"]:
            keys[(row["episode_id"],ref)].add(row["candidate_role"])
    if set(keys)!=original_keys:
        raise ValueError("An original source speaking unit disappeared")
    named=sum(None not in roles for roles in keys.values())
    report={
       "schema":SCHEMA,
       "original_caption_source_units":len(keys),
       "provisional_named_original_source_units":named,
       "original_source_units_still_UNKNOWN":len(keys)-named,
       "previous_provisional_speaking_blocks":len(rows),
       "current_provisional_speaking_blocks":len(changed),
       "split_original_source_ref":SOURCE_REF,
       "original_source_cue_start_ms":EXPECTED_START,
       "original_source_cue_end_ms":EXPECTED_END,
       "source_cue_timing_is_not_performer_turn_timing":True,
       "original_source_caption_text_and_times_changed":False,
       "new_performer_turns_independently_audio_verified":0,
       "new_original_actor_identities_certified":0,
       "all_original_source_characters_preserved_exactly":True,
    }
    if strict and (len(rows),len(changed),len(keys),named,len(keys)-named)!=(725,726,751,621,130):
        raise ValueError("New source-exact original S01 turn status drift")
    return changed,report

def build(root:Path,previous:Path,out:Path)->dict:
    if out.resolve().is_relative_to(root.resolve()):
        raise ValueError("Full private original copyrighted source cannot enter repo")
    old=(previous/BEFORE).read_bytes()
    m=json.loads((previous/BEFORE_MANIFEST).read_text("utf-8"))
    if (sha(old)!=m.get("source_turn_records_sha256")
        or m.get("original_caption_source_units")!=751
        or m.get("named_original_source_units")!=621
        or m.get("unknown_original_source_units")!=130
        or m.get("new_provisional_reader_turn_blocks")!=725
        or m.get("source_new_performer_identifications_AV_certified")!=0):
        raise ValueError("Original source-first S09 P0 role reader prerequisite invalid")
    metadata,cues=load_witness(root,"S01E01")
    if (metadata["sha256"]!=SOURCE_SHA or metadata["timecoded"] is not True
        or cues[218]["cue"]!=219
        or cues[218]["start_ms"]!=EXPECTED_START
        or cues[218]["end_ms"]!=EXPECTED_END):
        raise ValueError("Original S01 SRT cue C219 timing/source SHA changed")
    rows=[json.loads(x) for x in old.decode("utf-8").splitlines() if x.strip()]
    updated,report=split(rows,cues[218]["text"])
    out.mkdir(parents=True,exist_ok=True)
    encoded="".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in updated)
    (out/AFTER).write_text(encoded,"utf-8")
    report["source_role_record_sha256"]=sha(encoded.encode("utf-8"))
    report["prior_private_source_role_sha256"]=sha(old)
    report["private_source_manuscripts_sha256"]={}
    for ep in ("S01E01","S09E19"):
        witness=load_witness(root,ep)[0]
        lines=[f"# {ep}: original source-first speaking-turns v15","",
               "All role and turn labels provisional. Original cue timestamps are",
               "bounding context, never separately measured character turn times.",
               "No original moving-video/audio actor identification was accepted.",
               f"Original caption SHA256: {witness['sha256']}",""]
        for row in updated:
            if row["episode_id"]!=ep:continue
            role=row["candidate_role"] or "UNIDENTIFIED SPEAKER"
            lines.extend([f"### {row['source_reading_ref']} ({', '.join(row['original_source_part_refs'])})",
                          role+" · "+row["role_attribution_status"],row["caption_text"],""])
        text="\n".join(lines).rstrip()+"\n"
        (out/f"{ep}-source-turns-v15.md").write_text(text,"utf-8")
        report["private_source_manuscripts_sha256"][ep]=sha(text.encode("utf-8"))
    (out/AFTER_MANIFEST).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n","utf-8")
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--source-turn-patches",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    x=build(a.root,a.source_turn_patches,a.output)
    print(f"{x['current_provisional_speaking_blocks']} original source-turn reader blocks; "
          "S01 C219 dash reply split without voice identity/timing inventing; "
          f"{x['provisional_named_original_source_units']}/751 source units provisionally named")
if __name__=="__main__":
    main()
