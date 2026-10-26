#!/usr/bin/env python3
"""Reusable source-first original Night Court role amendment ledger.

Today this supports small, reversible UNKNOWN→character working-name changes
without writing another custom pilot reader for every batch. No genuine
actor/voice confirmation is inferred from lexical context, existing SRT
timings, physical comedy or model confidence.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from build_pilot_fan_beat_cards import ROOT,load_witness

SCHEMA="night-court-private-source-role-amendments/1"
LEDGER_SCHEMA="night-court-source-role-amendment-ledger/1"
LEDGER=ROOT/"research/source-role-amendments-v1.json"
BEFORE="pilot-source-dialogue-turns-v13.jsonl"
BEFORE_MANIFEST="pilot-source-dialogue-turns-v13-manifest.json"
AFTER="pilot-source-role-amendments.jsonl"
AFTER_MANIFEST="pilot-source-role-amendments-manifest.json"
STATUS="source_role_patch_context_only_not_original_voice_verified"
SOURCES={
 "S01E01":"aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496",
 "S09E19":"659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
}

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()


def validate_ledger(ledger:dict)->dict[tuple[str,str],dict]:
    if (ledger.get("schema")!=LEDGER_SCHEMA
        or not isinstance(ledger.get("id"),str) or len(ledger["id"])<8
        or ledger.get("input_role_reader")!="v13-original-source-speaker-turns"
        or ledger.get("sources")!=SOURCES
        or ledger.get("prior_source_caption_units")!=751
        or ledger.get("prior_working_named_source_units")!=613
        or ledger.get("prior_remaining_unknown_source_units")!=138
        or ledger.get("prior_private_reader_blocks")!=718
        or ledger.get("original_source_captions_modified") is not False
        or ledger.get("performed_turns_independently_verified") is not False
        or ledger.get("source_actor_identity_independently_verified") is not False):
        raise ValueError("Original speaker source amendment ledger violates frozen baseline")
    items=ledger.get("amendments")
    if not isinstance(items,list) or not 1<=len(items)<=138:
        raise ValueError("Source role amendment patch count not bounded by current UNKNOWN units")
    selected={}
    seen_units=set()
    for patch in items:
        ep=patch.get("episode_id")
        ref=patch.get("source_reading_ref")
        refs=patch.get("original_source_part_refs")
        name=patch.get("new_provisional_role")
        words=patch.get("source_text_must_contain")
        reason=patch.get("reason")
        if (set(patch)!={
            "operation","episode_id","source_reading_ref",
            "original_source_part_refs","original_source_witness_sha256",
            "prior_role","new_provisional_role","source_text_must_contain",
            "reason","original_actor_voice_recognition_confirmed",
            "original_performance_turn_verified"
        } or patch.get("operation")!="set_role"
            or ep not in SOURCES or not isinstance(ref,str) or not ref
            or not isinstance(refs,list) or not refs
            or len(refs)>8
            or not all(isinstance(x,str) and x.startswith("C")
                       and len(x)>=6 and x[1:4].isdigit() for x in refs)
            or patch.get("original_source_witness_sha256")!=SOURCES.get(ep)
            or patch.get("prior_role","missing") is not None
            or not isinstance(name,str) or not 3<=len(name)<=72
            or name.strip()!=name
            or name.upper()!=name or name=="UNIDENTIFIED SPEAKER"
            or not isinstance(words,str) or not 10<=len(words)<=130
            or not isinstance(reason,str) or len(reason)<65
            or patch.get("original_actor_voice_recognition_confirmed") is not False
            or patch.get("original_performance_turn_verified") is not False):
            raise ValueError("Source-scoped character name patch lacks reliable provenance")
        key=(ep,ref)
        if key in selected or any((ep,x) in seen_units for x in refs):
            raise ValueError("Duplicated source reader/paragraph patch in amendment list")
        selected[key]=patch
        seen_units.update((ep,x) for x in refs)
    return selected


def apply(rows:list[dict],ledger:dict,strict:bool=True)->tuple[list[dict],dict]:
    patches=validate_ledger(ledger)
    seen=set()
    updated=[dict(row) for row in rows]
    old_ids={(row["episode_id"],ref) for row in rows
             for ref in row["original_source_part_refs"]}
    before=defaultdict(set)
    for row in rows:
        for ref in row["original_source_part_refs"]:
            before[(row["episode_id"],ref)].add(row["candidate_role"])
    baseline_named=sum(None not in roles for roles in before.values())
    if strict and (len(rows),len(old_ids),baseline_named)!=(718,751,613):
        raise ValueError("Prior original source speaker role document changed unexpectedly")
    for row in updated:
        key=row["episode_id"],row["source_reading_ref"]
        if key not in patches:
            continue
        patch=patches[key]
        if (row.get("original_source_part_refs")!=patch["original_source_part_refs"]
            or row.get("original_source_sha256")!=SOURCES[row["episode_id"]]
            or row.get("candidate_role") is not None
            or row.get("role_attribution_status")!="unidentified"
            or row.get("speaker_turn_boundary_verified") is not False
            or row.get("actor_face_or_voice_independently_verified") is not False
            or patch["source_text_must_contain"] not in row.get("caption_text","")
            or (row["episode_id"]=="S09E19" and
                (row.get("source_original_times_ms") is not None
                 or row.get("original_source_untimed") is not True))):
            raise ValueError("Source character amendment would overwrite role, text, or AV-certification")
        seen.add(key)
        row.update({
            "candidate_role":patch["new_provisional_role"],
            "role_attribution_status":STATUS,
            "speaker_identity_provisional_from_source_context":True,
            "source_exact_context_role_patch_id":ledger["id"],
            "source_role_patch_reason":patch["reason"],
            "original_source_actor_voice_independently_verified":False,
            "original_source_turn_boundary_independently_verified":False,
            "source_original_witness_sha256":SOURCES[row["episode_id"]]
        })
    if seen!=set(patches):
        raise ValueError("Source role patch refers to missing/previously joined reading block")
    final=defaultdict(set)
    for row in updated:
        for ref in row["original_source_part_refs"]:
            final[(row["episode_id"],ref)].add(row["candidate_role"])
    if set(final)!=old_ids or len(updated)!=len(rows):
        raise ValueError("Source role amendment lost or created original cue/turn")
    named=sum(None not in roles for roles in final.values())
    changed_source_units=sum(len(p["original_source_part_refs"]) for p in patches.values())
    if (named!=baseline_named+changed_source_units or
        len(final)-named!=len(old_ids)-baseline_named-changed_source_units):
        raise ValueError("Source role patch reassignments did not resolve expected UNKNOWN cue parts")
    report={
        "schema":SCHEMA,
        "original_held_source_caption_units":len(final),
        "provisionally_named_source_units":named,
        "unknown_original_source_units":len(final)-named,
        "source_reading_blocks":len(updated),
        "reusable_ledger_amendment_count":len(patches),
        "previously_unidentified_original_source_parts_now_contextually_named":changed_source_units,
        "source_character_roles_independently_verified_via_AV":0,
        "source_s09_untimed_original_caption_status_preserved":True,
        "source_original_cue_text_and_part_membership_unchanged":True,
        "edits_are_provisional_context_roles_only":True,
        "source_role_amendment_id":ledger["id"]
    }
    return updated,report


def build(root:Path,v13:Path,ledger_path:Path,output:Path)->dict:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private episode dialogue and derived speaker readers cannot enter the repo")
    old=(v13/BEFORE).read_bytes()
    m=json.loads((v13/BEFORE_MANIFEST).read_text("utf-8"))
    if (sha(old)!=m.get("v13_records_sha256")
        or m.get("original_held_caption_units")!=751
        or m.get("provisionally_named_original_caption_units")!=613
        or m.get("unidentified_original_caption_units")!=138
        or m.get("new_provisional_speaking_turns")!=718
        or m.get("source_audio_actor_identities_or_true_turns_independently_verified")!=0):
        raise ValueError("Source-first baseline v13 original cue/role evidence is invalid")
    witnesses={}
    for ep,source_sha in SOURCES.items():
        meta,cues=load_witness(root,ep)
        if meta["sha256"]!=source_sha or (ep=="S09E19" and meta["timecoded"] is not False):
            raise ValueError("Original-source episode cue timestamp/SHA no longer frozen")
        witnesses[ep]=cues
    patch_bytes=ledger_path.read_bytes()
    changes=json.loads(patch_bytes)
    for (ep,ref),entry in validate_ledger(changes).items():
        exact=" ".join(witnesses[ep][int(x[1:4])-1]["text"] for x in entry["original_source_part_refs"])
        if entry["source_text_must_contain"] not in exact:
            raise ValueError("Source role patch anchor absent from canonical original caption text")
    rows=[json.loads(x) for x in old.decode("utf-8").splitlines() if x.strip()]
    result,report=apply(rows,changes)
    output.mkdir(parents=True,exist_ok=True)
    encoded="".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in result)
    (output/AFTER).write_text(encoded,"utf-8")
    report["source_patch_roles_sha256"]=sha(encoded.encode("utf-8"))
    report["source_patch_ledger_sha256"]=sha(patch_bytes)
    report["prior_original_source_v13_reader_sha256"]=sha(old)
    report["manuscripts_sha256_by_episode"]={}
    for ep in SOURCES:
        lines=[f"# {ep}: private original-series source-role amendments","",
               "All roles remain EDITORIAL working names, not verified original",
               "voice/face identifications. Actual film turn splits are not certified.",
               f"Original episode caption SHA256: {SOURCES[ep]}",""]
        for row in result:
            if row["episode_id"]!=ep:continue
            role=row["candidate_role"] or "UNIDENTIFIED SPEAKER"
            lines += [f"### {row['source_reading_ref']} ({', '.join(row['original_source_part_refs'])})",
                      role+" · "+row["role_attribution_status"],row["caption_text"],""]
        text="\n".join(lines).rstrip()+"\n"
        (output/f"{ep}-source-role-patches.md").write_text(text,"utf-8")
        report["manuscripts_sha256_by_episode"][ep]=sha(text.encode("utf-8"))
    (output/AFTER_MANIFEST).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n","utf-8")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--v13",type=Path,required=True)
    p.add_argument("--ledger",type=Path,default=LEDGER)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    m=build(a.root,a.v13,a.ledger,a.output)
    print(f"{m['provisionally_named_source_units']}/751 provisionally named source units, "
          f"{m['unknown_original_source_units']} UNKNOWN from "
          f"{m['reusable_ledger_amendment_count']} reusable source-pinned role amendments; "
          "0 independent original film actor identities accepted")


if __name__=="__main__":
    main()
