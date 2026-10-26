#!/usr/bin/env python3
"""Reversible original S09 C291 source turn: preserve partial Alex hypothesis.

The previously held S09 C291 line has a *whole-cue* provisional ALEX PATTERSON
attribution. Its pronoun exchange plausibly has two speakers, so it must not
be split by a tool accepting only UNKNOWN sources; nor should Alex's name be
copied to both voices. The first very short fragment stays UNKNOWN, the
second inherits the old tentative actor hypothesis. No actual original
movie voice/face/turn has been independently accepted by this operation.
"""
from __future__ import annotations
from collections import defaultdict
import argparse
import hashlib
import json
from pathlib import Path
from build_pilot_fan_beat_cards import ROOT,load_witness

SCHEMA="night-court-private-s09-role-preserving-c291-source-turn-v16/1"
BEFORE="pilot-source-episode-turns-v15.jsonl"
BEFORE_MANIFEST="pilot-source-episode-turns-v15-manifest.json"
AFTER="pilot-source-role-aware-turns-v16.jsonl"
AFTER_MANIFEST="pilot-source-role-aware-turns-v16-manifest.json"
SHA="659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
SOURCE_REF="C291.1"
SOURCE_TEXT="He. He was me."
SECOND="He was me."
ALEX="ALEX PATTERSON"
PRIOR_STATUS="narrative_context_candidate_not_voice_verified"
PROPOSED_STATUS="prior_original_source_context_partial_role_not_AV_verified"

def digest(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def transform(rows:list[dict],strict:bool=True)->tuple[list[dict],dict]:
    matches=[(i,row) for i,row in enumerate(rows)
             if row["episode_id"]=="S09E19" and row["source_reading_ref"]==SOURCE_REF]
    if len(matches)!=1:
        raise ValueError("Original S09 C291 one existing source reading not found")
    position,old=matches[0]
    if (old.get("original_source_sha256")!=SHA
        or old.get("original_source_part_refs")!=[SOURCE_REF]
        or old.get("caption_text")!=SOURCE_TEXT
        or old.get("candidate_role")!=ALEX
        or old.get("role_attribution_status")!=PRIOR_STATUS
        or old.get("actor_face_or_voice_independently_verified") is not False
        or old.get("speaker_turn_boundary_verified") is not False
        or old.get("original_source_untimed") is not True
        or old.get("source_original_times_ms") is not None):
        raise ValueError("Existing original C291 Alex context cannot be safely partially inherited")
    if SOURCE_TEXT.count(SECOND)!=1:
        raise ValueError("C291 exact original dialogue split not uniquely defined")
    cut=SOURCE_TEXT.index(SECOND)
    if cut<=0 or cut>=len(SOURCE_TEXT):
        raise ValueError("S09 C291 source turn speech split must be internal")
    pieces=[(0,cut,SOURCE_TEXT[:cut]),(cut,len(SOURCE_TEXT),SOURCE_TEXT[cut:])]
    if "".join(x[2] for x in pieces)!=SOURCE_TEXT or not all(x[2].strip() for x in pieces):
        raise ValueError("S09 C291 source characters lost or duplicate speaker text")
    outputs=[]
    for i,(start,end,words) in enumerate(pieces):
        row=dict(old)
        row.update({
            "reading_block_id":f"S09E19:role-aware-source-turn-C291:{i+1}",
            "source_reading_ref":f"S09E19-C291-PARTIAL-TURN-{i+1}",
            "original_source_part_refs":[SOURCE_REF],
            "caption_text":words,
            "candidate_role":None if i==0 else ALEX,
            "role_attribution_status":"unidentified" if i==0 else PROPOSED_STATUS,
            "speaker_turn_boundary_verified":False,
            "actor_face_or_voice_independently_verified":False,
            "original_source_untimed":True,
            "source_original_times_ms":None,
            "previous_legacy_whole_cue_role_not_independent_actor_evidence":ALEX,
            "source_partial_role_from_preexisting_context_not_new_voice_recognition":i==1,
            "original_audio_speaker_identity_verified":False,
            "source_exact_character_span":{
                "source_ref":SOURCE_REF,
                "start_char":start,"end_char":end,
                "original_source_substring_sha256":digest(words.encode("utf-8"))
            },
        })
        outputs.append(row)
    updated=rows[:position]+outputs+rows[position+1:]
    keys=defaultdict(set)
    previous_keys={(r["episode_id"],ref) for r in rows
                   for ref in r["original_source_part_refs"]}
    for row in updated:
        for ref in row["original_source_part_refs"]:
            keys[(row["episode_id"],ref)].add(row["candidate_role"])
    if set(keys)!=previous_keys:
        raise ValueError("Source S09 caption cue unit ID lost through partial role attribution")
    named=sum(None not in roles for roles in keys.values())
    report={
        "schema":SCHEMA,
        "original_caption_source_units":len(keys),
        "provisional_named_original_caption_units":named,
        "unknown_original_source_units":len(keys)-named,
        "private_provisional_speaking_blocks_before":len(rows),
        "private_provisional_speaking_blocks_after":len(updated),
        "previous_single_cue_role_was_provisional":ALEX,
        "partial_legacy_source_role_retained_only_on_second_fragment":True,
        "source_c291_originally_untimed_and_unchanged":True,
        "source_words_and_unicode_offsets_fully_reconstructable":True,
        "new_original_AV_certified_voice_or_actor_turns":0,
        "source_c291_opening_fragment_role":"UNIDENTIFIED SPEAKER",
        "source_c291_second_fragment_role_provisional":ALEX,
    }
    if strict and (len(rows),len(updated),len(keys),named,len(keys)-named)!=(
        726,727,751,620,131):
        raise ValueError("Original C291 mixed-voice proposal source-unit/role counts drift")
    return updated,report


def build(root:Path,old_dir:Path,out:Path)->dict:
    if out.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private source-original episode dialogue must stay outside Git")
    raw=(old_dir/BEFORE).read_bytes()
    m=json.loads((old_dir/BEFORE_MANIFEST).read_text("utf-8"))
    if (digest(raw)!=m.get("source_role_record_sha256")
        or m.get("original_caption_source_units")!=751
        or m.get("provisional_named_original_source_units")!=621
        or m.get("original_source_units_still_UNKNOWN")!=130
        or m.get("current_provisional_speaking_blocks")!=726
        or m.get("new_original_actor_identities_certified")!=0):
        raise ValueError("Current v15 source reader prerequisite failed SHA/role reconciliation")
    witness,cues=load_witness(root,"S09E19")
    if (witness["sha256"]!=SHA or witness["timecoded"] is not False
        or cues[290]["cue"]!=291 or cues[290]["text"]!=SOURCE_TEXT):
        raise ValueError("Original untimed S09 C291 source paragraph changed")
    before=[json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    after,report=transform(before)
    out.mkdir(parents=True,exist_ok=True)
    data="".join(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n" for row in after)
    (out/AFTER).write_text(data,"utf-8")
    report["new_source_role_record_sha256"]=digest(data.encode("utf-8"))
    report["prior_source_role_record_sha256"]=digest(raw)
    report["private_manuscript_sha256_by_episode"]={}
    for ep in ("S01E01","S09E19"):
        caption=load_witness(root,ep)[0]
        lines=[f"# {ep}: private original source-first role-aware candidate turns v16","",
               "No moving-film/audio performance turn or character is independently verified.",
               "Editorial original-source context roles can apply to only part of a cue.",
               "Original source dialogue and source cue-time status preserved unchanged.",
               f"Original caption SHA256: {caption['sha256']}",""]
        for row in after:
            if row["episode_id"]!=ep:continue
            role=row["candidate_role"] or "UNIDENTIFIED SPEAKER"
            lines.extend([f"### {row['source_reading_ref']} ({', '.join(row['original_source_part_refs'])})",
                          role+" · "+row["role_attribution_status"],row["caption_text"],""])
        text="\n".join(lines).rstrip()+"\n"
        (out/f"{ep}-source-partial-roles-v16.md").write_text(text,"utf-8")
        report["private_manuscript_sha256_by_episode"][ep]=digest(text.encode("utf-8"))
    (out/AFTER_MANIFEST).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n","utf-8")
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--v15",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    report=build(a.root,a.v15,a.output)
    print(f"{report['private_provisional_speaking_blocks_after']} provisional character-turn blocks, "
          f"{report['provisional_named_original_caption_units']}/751 fully provisionally named original cue units, "
          f"{report['unknown_original_source_units']} source units still have unidentified speech, "
          "no original film actor identity verified")
if __name__=="__main__":
    main()
