#!/usr/bin/env python3
"""Apply manual, source-pinned editorial speaker proposals to private v15 pilots.

Neither context nor a speaker display label constitutes independently heard AV
evidence. Original 1984-1992 captions and source-first v15 reader remain intact.
This stage writes private v16 manuscripts and per-row provenance, never original
episode dialogue into Git.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from build_pilot_fan_beat_cards import ROOT,load_witness
from render_current_pilot_screenplays import (
    SOURCE, INPUT, INPUT_MANIFEST, sha, check_source, render, time_envelope,
)

LEDGER=ROOT/"research/manual-context-editorial-speaker-review-v16.json"
LEDGER_SCHEMA="night-court-private-manual-context-role-review/1"
SCHEMA="night-court-private-manual-editorial-pilots-v16/1"
LAYOUT_SCHEMA="night-court-private-pilot-screenplay-layout/2"
STATUS="manual_editorial_context_role_candidate_not_original_AV_verified"

def validate_ledger(ledger:dict)->tuple[list[dict],dict]:
    if (ledger.get("schema")!=LEDGER_SCHEMA
        or ledger.get("original_source_shas")!={ep:x[0] for ep,x in SOURCE.items()}
        or ledger.get("source_reader_input")!=INPUT
        or (ledger.get("prior_source_units"),ledger.get("prior_named_source_units"),
            ledger.get("prior_unidentified_source_units"),ledger.get("prior_reading_blocks"))
           !=(751,621,130,726)
        or ledger.get("context_not_original_av_verified") is not True):
        raise ValueError("Manual context evidence is not based on exact current v15 source")
    edits=ledger.get("role_amendments")
    splits=ledger.get("original_source_split_proposals")
    if not isinstance(edits,list) or len(edits)!=34 or not isinstance(splits,list) or len(splits)!=1:
        raise ValueError("Manual source editorial amendments not at checked count")
    keys=set()
    for item in edits:
        if set(item)!={"episode_id","source_reading_ref","original_source_part_refs",
                      "prior_role","new_provisional_role","source_text_must_contain",
                      "rationale","source_witness_sha256","original_audio_verified",
                      "performed_turn_verified"}:
            raise ValueError("Unsafe fields in original source attribution proposal")
        ep,ref=item["episode_id"],item["source_reading_ref"]
        refs=item["original_source_part_refs"]
        if (ep not in SOURCE or not isinstance(ref,str) or not ref
            or (ep,ref) in keys
            or not isinstance(refs,list) or not refs
            or any(not isinstance(x,str) or not x.startswith("C") for x in refs)
            or item["source_witness_sha256"]!=SOURCE[ep][0]
            or item["prior_role"] is not None and
               (not isinstance(item["prior_role"],str) or not item["prior_role"])
            or not isinstance(item["new_provisional_role"],str)
            or item["new_provisional_role"].upper()!=item["new_provisional_role"]
            or not 3<=len(item["new_provisional_role"])<=72
            or not isinstance(item["source_text_must_contain"],str)
            or len(item["source_text_must_contain"])<3
            or not isinstance(item["rationale"],str) or len(item["rationale"])<75
            or item["original_audio_verified"] is not False
            or item["performed_turn_verified"] is not False):
            raise ValueError("Unanchored, duplicate or falsely AV-certified manual role attribution")
        keys.add((ep,ref))
    if (sum(x["prior_role"] is None for x in edits)!=32
        or {(x["episode_id"],x["source_reading_ref"]) for x in edits if x["prior_role"]}!=
           {("S09E19","C305.1"),("S09E19","C306.1")}):
        raise ValueError("Unexpected named-speaker correction or contextual attribution")
    split=splits[0]
    if (set(split)!={"episode_id","original_source_ref","source_reading_ref",
                    "prior_role","source_witness_sha256","source_text_must_equal",
                    "split_before","roles","rationale","original_audio_verified"}
        or split["episode_id"]!="S09E19"
        or split["source_reading_ref"]!="C277.1"
        or split["original_source_ref"]!="C277.1"
        or split["prior_role"] is not None
        or split["source_witness_sha256"]!=SOURCE["S09E19"][0]
        or split["roles"]!=[None,None]
        or split["original_audio_verified"] is not False
        or split["source_text_must_equal"]!=
           "And the snacks are free. Yeah, but they're not fresh."
        or split["split_before"]!="Yeah, but they're not fresh."
        or not isinstance(split["rationale"],str) or len(split["rationale"])<75):
        raise ValueError("S09 C277 exact-original source P0 handoff drift")
    if ("S09E19","C277.1") in keys:
        raise ValueError("Do not overwrite the unresolved original two-voice cue")
    return edits,split

def counts(rows:list[dict])->dict:
    groups=defaultdict(set)
    for row in rows:
        for ref in row["original_source_part_refs"]:
            groups[row["episode_id"],ref].add(row["candidate_role"])
    return {
        "source_units":len(groups),
        "fully_provisionally_named_source_units":sum(None not in xs for xs in groups.values()),
        "source_units_with_any_unknown_voice":sum(None in xs for xs in groups.values()),
        "unknown_source_units_by_episode":{
            ep:sum(k[0]==ep and None in v for k,v in groups.items()) for ep in SOURCE
        },
    }

def apply(rows:list[dict],ledger:dict,strict:bool=True)->tuple[list[dict],dict]:
    edits,split=validate_ledger(ledger)
    if strict and (len(rows),counts(rows)) != (726,{
        "source_units":751,
        "fully_provisionally_named_source_units":621,
        "source_units_with_any_unknown_voice":130,
        "unknown_source_units_by_episode":{"S01E01":34,"S09E19":96}
    }):
        raise ValueError("Private v15 reader baseline changed")
    before=counts(rows)
    index={(row["episode_id"],row["source_reading_ref"]):i for i,row in enumerate(rows)}
    if len(index)!=len(rows):
        raise ValueError("Duplicate original reading block ref")
    updated=[dict(row) for row in rows]
    for p in edits:
        key=p["episode_id"],p["source_reading_ref"]
        if key not in index:
            raise ValueError("Missing exact original reading reference for manual role review")
        row=updated[index[key]]
        if (row["original_source_part_refs"]!=p["original_source_part_refs"]
            or row["original_source_sha256"]!=p["source_witness_sha256"]
            or row["candidate_role"]!=p["prior_role"]
            or row.get("speaker_turn_boundary_verified") is not False
            or row.get("actor_face_or_voice_independently_verified") is not False
            or p["source_text_must_contain"] not in row["caption_text"]
            or (p["episode_id"]=="S09E19" and
                (row.get("source_original_times_ms") is not None
                 or row.get("original_source_untimed") is not True))):
            raise ValueError("Manual speaker correction conflicts with immutable source, role or AV status")
        row["candidate_role"]=p["new_provisional_role"]
        row["role_attribution_status"]=STATUS
        row["contextual_editorial_review_ledger"]=ledger["id"]
        row["contextual_editorial_role_rationale"]=p["rationale"]
        row["original_soundtrack_role_independently_reviewed"]=False
    key=split["episode_id"],split["source_reading_ref"]
    if key not in index:
        raise ValueError("Missing unsplit S09 C277 source paragraph")
    n=index[key]
    row=updated[n]
    cue=split["source_text_must_equal"]
    phrase=split["split_before"]
    if (row["candidate_role"] is not None
        or row["original_source_part_refs"]!=[split["original_source_ref"]]
        or row["original_source_sha256"]!=SOURCE["S09E19"][0]
        or row["caption_text"]!=cue or cue.count(phrase)!=1
        or row["source_original_times_ms"] is not None
        or row.get("original_source_untimed") is not True
        or row["speaker_turn_boundary_verified"] is not False
        or row["actor_face_or_voice_independently_verified"] is not False):
        raise ValueError("Original S09 snack cue or prior speaker structure changed")
    cut=cue.index(phrase)
    if cut<=0 or not cue[:cut].strip() or not cue[cut:].strip():
        raise ValueError("No two complete exact-original snack speech fragments")
    fragments=[]
    for i,(a,b) in enumerate(((0,cut),(cut,len(cue))),1):
        fragment=dict(row)
        fragment.update({
          "reading_block_id":f"S09E19:manual-P0-C277:unknown-{i}",
          "source_reading_ref":f"S09E19-C277-MANUAL-SOURCE-TURN-{i}",
          "original_source_part_refs":["C277.1"],
          "caption_text":cue[a:b],
          "candidate_role":None,
          "role_attribution_status":"manual_editorial_source_speaker_split_unknown_unverified",
          "source_exact_character_span":{
              "original_source_ref":"C277.1","start_char":a,"end_char":b,
              "exact_text_sha256":sha(cue[a:b].encode("utf-8"))
          },
          "source_original_times_ms":None,
          "original_source_untimed":True,
          "speaker_turn_boundary_verified":False,
          "actor_face_or_voice_independently_verified":False,
          "human_viewed_film_or_listened_to_actor":False,
          "contextual_editorial_review_ledger":ledger["id"],
          "contextual_editorial_role_rationale":split["rationale"],
        })
        fragments.append(fragment)
    if fragments[0]["caption_text"]+fragments[1]["caption_text"]!=cue:
        raise ValueError("Original speaker split omitted or changed a source character")
    updated[n:n+1]=fragments
    after=counts(updated)
    changed_roles=sum(p["prior_role"]!=p["new_provisional_role"] for p in edits)
    old_keys={(r["episode_id"],ref) for r in rows for ref in r["original_source_part_refs"]}
    new_keys={(r["episode_id"],ref) for r in updated for ref in r["original_source_part_refs"]}
    if (old_keys!=new_keys or len(updated)!=len(rows)+1
        or after["source_units"]!=before["source_units"]
        or after["fully_provisionally_named_source_units"]!=
           before["fully_provisionally_named_source_units"]+30
        or after["source_units_with_any_unknown_voice"]!=
           before["source_units_with_any_unknown_voice"]-30):
        raise ValueError("Manually proposed roles/turns changed original source conservation or count")
    report={
        "schema":SCHEMA,
        "new_contextual_role_assignments_in_reader_blocks":32,
        "corrected_previously_named_reader_blocks":2,
        "new_contextually_named_complete_source_units":30,
        "role_changes_in_reading_blocks":changed_roles,
        "source_text_p0_split_unverified":"S09E19:C277.1",
        "original_caption_dialogue_changed":False,
        "performed_turns_independently_AV_verified":0,
        "actor_role_identifications_independently_original_audio_verified":0,
        "previous_reader_blocks":len(rows),"current_reader_blocks":len(updated),
        "source_coverage":after,"previous_source_coverage":before,
    }
    return updated,report

def build(root:Path,source_v15:Path,output:Path,ledger_path:Path=LEDGER)->dict:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Never write full source-derived manuscripts into Night Court repo")
    binary=(source_v15/INPUT).read_bytes()
    prior_manifest=json.loads((source_v15/INPUT_MANIFEST).read_text("utf-8"))
    witnesses={ep:load_witness(root,ep) for ep in SOURCE}
    rows=[json.loads(x) for x in binary.decode("utf-8").splitlines() if x.strip()]
    check_source(rows,prior_manifest,binary,witnesses)
    ledger_bytes=ledger_path.read_bytes()
    ledger=json.loads(ledger_bytes)
    # Patch anchors must exist in the exact original held witness, not only a
    # mutable manuscript, except for split-specific substrings within the cue.
    for p in ledger["role_amendments"]:
        anchor=p["source_text_must_contain"]
        if len(p["original_source_part_refs"])==1:
            n=int(p["original_source_part_refs"][0][1:4])
            original=witnesses[p["episode_id"]][1][n-1]["text"]
            if anchor not in original:
                raise ValueError("Editorial role text anchor missing from immutable original cue")
    split=ledger["original_source_split_proposals"][0]
    if witnesses["S09E19"][1][276]["text"]!=split["source_text_must_equal"]:
        raise ValueError("Original snack cue source text changed")
    updated,report=apply(rows,ledger)
    manuscripts,sidecars,summary=render(updated)
    output.mkdir(parents=True,exist_ok=True)
    payload="".join(json.dumps(row,sort_keys=True,ensure_ascii=False)+"\n" for row in updated)
    (output/"pilot-manual-context-speaker-v16.jsonl").write_text(payload,"utf-8")
    report.update({
       "source_v15_reader_sha256":sha(binary),
       "editorial_patch_ledger_sha256":sha(ledger_bytes),
       "current_v16_reader_sha256":sha(payload.encode("utf-8")),
       "reading_block_ids_preserved_except_exact_C277_source_split":True
    })
    (output/"pilot-manual-context-speaker-v16-manifest.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n","utf-8")
    layout_report={
      "schema":LAYOUT_SCHEMA,
      "source_v15_reader_sha256":sha(binary),
      "source_manual_v16_reader_sha256":sha(payload.encode("utf-8")),
      "source_manual_v16_patch_sha256":sha(ledger_bytes),
      "source_unit_counts":{
         "original_source_units":751,"named_provisional":651,"unknown":100
      },
      "episodes":summary,
      "new_independently_verified_actor_voices":0,
      "new_independently_verified_performed_turns":0,
      "scene_review_complete":False,
      "provisional_contextual_roles_only":True,
      "manuscript_sha256":{},
    }
    for ep,script in manuscripts.items():
        name=f"{ep}-working-screenplay.md"
        (output/name).write_text(script,"utf-8")
        layout_report["manuscript_sha256"][ep]=sha(script.encode("utf-8"))
        (output/f"{ep}-working-screenplay-provenance.jsonl").write_text(
            "".join(json.dumps(item,sort_keys=True,ensure_ascii=False)+"\n"
                    for item in sidecars[ep]),"utf-8")
    (output/"working-screenplay-layout-manifest.json").write_text(
        json.dumps(layout_report,indent=2,sort_keys=True)+"\n","utf-8")
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--v15-root",type=Path,required=True)
    p.add_argument("--ledger",type=Path,default=LEDGER)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=build(a.root,a.v15_root,a.output,a.ledger)
    print(result["current_reader_blocks"],"provisional screenplay reading blocks;",
          result["source_coverage"]["fully_provisionally_named_source_units"],
          "fully provisionally named original source units;",
          result["source_coverage"]["source_units_with_any_unknown_voice"],
          "still have UNKNOWN voices; zero original AV accepted")

if __name__=="__main__":
    main()
