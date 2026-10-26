#!/usr/bin/env python3
"""Create speaker-first private v9 pilot readers, with genuine original S09 sound.

Three original S09 UNKNOWN source units gain **provisional acoustic and
context-backed** character proposals. A fourth model prediction is quarantined
rather than mislabeling a possible absent speaker. All original cue texts,
source-unit coverage, private text export and independent AV uncertainty stay
unchanged. No real actor identity was certified by this pass.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from build_pilot_fan_beat_cards import ROOT,load_witness

SCHEMA="night-court-private-original-s09-acoustic-speaker-reader-v9/1"
LEDGER_SCHEMA="night-court-original-s09-acoustic-role-review/1"
ORIGINAL_SHA="659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
FILM_SHA="51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649"
PCM_SHA="7f3e3634c99469214360d59faf69c7838301e6ee94d5f08968382a74607b6711"
MODEL_NUMERIC_SHA="656ee523b6a2996c3be9a8adf9bdf59a1086226e613d7b3000f38b30bb5657f8"
ALIGNMENT_SHA="febac6aff2cb01ee36ac1c44b592317011d655628ede2eb83981b98201e3accc"
OLD_READER="pilot-original-acoustic-speaker-reads.jsonl"
OLD_MANIFEST="pilot-original-acoustic-speaker-manifest.json"
NEW_READER="pilot-current-source-first-s09-audio-v9.jsonl"
NEW_MANIFEST="pilot-current-speaker-s09-audio-v9-manifest.json"
NEW_STATUS="original_soundtrack_acoustic_context_proposal_not_independent_avi_id"
EXPECTED_ACCEPT={"C046.1":"CHRISTINE SULLIVAN","C057.1":"CHRISTINE SULLIVAN","C267.1":"ROZ RUSSELL"}
EXPECTED_REJECT={"C129.1":"CHRISTINE SULLIVAN"}

def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def validate_model_ledger(ledger:dict)->dict:
    if (ledger.get("schema")!=LEDGER_SCHEMA
        or ledger.get("episode_id")!="S09E19"
        or ledger.get("original_video_sha256")!=FILM_SHA
        or ledger.get("original_caption_sha256")!=ORIGINAL_SHA
        or ledger.get("original_pcm_sha256")!=PCM_SHA
        or ledger.get("full_numeric_original_voice_report_sha256")!=MODEL_NUMERIC_SHA
        or ledger.get("source_asr_paragraph_alignment_report_sha256")!=ALIGNMENT_SHA
        or ledger.get("model")!="resemblyzer-0.1.4"
        or ledger.get("role_holdout_correct")!=18
        or ledger.get("role_holdout_total")!=26
        or ledger.get("source_unknown_original_paragraphs_compared")!=28
        or ledger.get("acoustic_similarity_threshold_proposals")!=4
        or ledger.get("working_character_proposals_to_add")!=3
        or ledger.get("quarantined_speaker_suspicions")!=1
        or ledger.get("source_soundtrack_human_actor_voice_identifications_accepted")!=0
        or ledger.get("original_untimed_cue_timestamps_introduced")!=0
        or ledger.get("known_reference_roles_count")!={"CHRISTINE SULLIVAN":10,"DAN FIELDING":5,"MAC ROBINSON":4,"ROZ RUSSELL":7}):
        raise ValueError("Actual source S09 numeric actor-role model identity or certainty differs")
    details=ledger.get("candidates")
    if not isinstance(details,list) or len(details)!=4:
        raise ValueError("Four original source acoustic candidates missing")
    seen={}
    for row in details:
        key=row.get("source_ref")
        if (not isinstance(key,str) or key in seen
            or not isinstance(row.get("similarity"),(int,float))
            or not isinstance(row.get("margin"),(int,float))
            or row["similarity"]<.69 or row["margin"]<.1
            or not isinstance(row.get("reason"),str) or len(row["reason"])<20):
            raise ValueError("Unverifiable individual source-audio role candidate")
        seen[key]=row
        role=row.get("proposed_role")
        disposition=row.get("disposition")
        if key in EXPECTED_ACCEPT and (role!=EXPECTED_ACCEPT[key]
            or disposition!="provisional_speaker_working_reader_only"):
            raise ValueError("Unexpected validated provisional role evidence")
        if key in EXPECTED_REJECT and (role!=EXPECTED_REJECT[key]
            or disposition!="quarantine_plausible_out_of_bank_speaker"):
            raise ValueError("Do not promote an out-of-bank suspicious role proposal")
    if set(seen)!=(set(EXPECTED_ACCEPT)|set(EXPECTED_REJECT)):
        raise ValueError("Wrong original S09 cue identities in source audio evidence")
    return seen


def merge(old:list[dict], ledger:dict, strict:bool=True)->tuple[list[dict],dict]:
    voice=validate_model_ledger(ledger)
    result=[dict(row) for row in old]
    map_refs=defaultdict(list)
    for i,row in enumerate(result):
        map_refs[(row["episode_id"],row["source_reading_ref"])].append(i)
    named_before=set()
    for row in old:
        for ref in row["original_source_part_refs"]:
            named_before.add((row["episode_id"],ref,row["candidate_role"]))
    for ref,proposal in voice.items():
        matched=map_refs.get(("S09E19",ref),[])
        if len(matched)!=1:
            raise ValueError("S09 original source candidate was joined or split")
        row=result[matched[0]]
        if (row.get("original_source_sha256")!=ORIGINAL_SHA
            or row.get("original_source_untimed") is not True
            or row.get("source_original_times_ms") is not None
            or row.get("original_source_part_refs")!=[ref]
            or row.get("candidate_role") is not None
            or row.get("role_attribution_status")!="unidentified"
            or row.get("speaker_turn_boundary_verified") is not False
            or row.get("actor_face_or_voice_independently_verified") is not False):
            raise ValueError("Source S09 cue identity no longer UNKNOWN or wrongly timed")
        row["source_acoustic_original_episode_role_similarity"]=proposal["similarity"]
        row["source_acoustic_competing_role_margin"]=proposal["margin"]
        row["source_acoustic_numeric_report_sha256"]=MODEL_NUMERIC_SHA
        row["source_acoustic_role_reference_candidates_not_all_cast"]=True
        row["original_soundtrack_human_role_reviewed"]=False
        if ref in EXPECTED_ACCEPT:
            row["candidate_role"]=proposal["proposed_role"]
            row["role_attribution_status"]=NEW_STATUS
            row["speaker_identity_provisional_from_model_and_context"]=True
        else:
            # Alternative diagnosis recorded, but speaker label remains
            # unknown: the model's four-reference cast bank lacked other
            # plausible actors in this scene.
            row["quarantined_acoustic_alternative_only"]=proposal["proposed_role"]
            row["candidate_role"]=None
            row["role_attribution_status"]="unidentified"
    group=defaultdict(set)
    for row in result:
        for ref in row["original_source_part_refs"]:
            group[(row["episode_id"],ref)].add(row["candidate_role"])
    named=sum(None not in xs for xs in group.values())
    old_keys={(ep,ref) for ep,ref,_ in named_before}
    if set(group)!=old_keys:
        raise ValueError("Original 751 cue part names have been added/lost")
    manifest={
        "schema":SCHEMA,
        "original_source_caption_units":len(group),
        "current_working_named_provisional_original_units":named,
        "unidentified_original_cue_units":len(group)-named,
        "original_s09_soundtrack_supported_new_named_proposals":len(EXPECTED_ACCEPT),
        "quarantined_suspicious_model_proposals":len(EXPECTED_REJECT),
        "original_audio_human_identified_characters_added":0,
        "correct_original_s09_episode_movie_sha256":FILM_SHA,
        "original_s09_script_still_untimed":True,
        "source_S09_speaker_candidate_reference_holdout":"18/26",
        "source_role_model_artifact_SHA256":MODEL_NUMERIC_SHA,
        "newly_proposed_ref_ids":sorted(EXPECTED_ACCEPT),
        "quarantined_source_refs":sorted(EXPECTED_REJECT),
    }
    if strict and (len(result),len(group),named,len(group)-named)!=(716,751,590,161):
        raise ValueError("V9 original caption provenance or provisional count drift")
    return result,manifest


def build(root:Path, source_v8:Path, ledger_file:Path, output:Path)->dict:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private full copyrighted episode dialogue must stay outside repository")
    base_raw=(source_v8/OLD_READER).read_bytes()
    base_report=json.loads((source_v8/OLD_MANIFEST).read_text("utf-8"))
    if (sha(base_raw)!=base_report.get("source_role_record_sha256")
        or base_report.get("original_source_caption_units")!=751
        or base_report.get("source_units_with_provisional_names")!=587
        or base_report.get("original_units_still_unknown")!=164
        or base_report.get("source_speaker_identities_human_verified_by_pass")!=0):
        raise ValueError("Cannot import S09 voice evidence without current original v8 speaker baseline")
    original=[json.loads(x) for x in base_raw.decode("utf-8").splitlines() if x.strip()]
    meta,_=load_witness(root,"S09E19")
    if meta["sha256"]!=ORIGINAL_SHA or meta["timecoded"] is not False:
        raise ValueError("Original 1992 S09 source SHA or original untimed status changed")
    ledger_bytes=ledger_file.read_bytes()
    rows,manifest=merge(original,json.loads(ledger_bytes))
    manifest["input_current_source_reader_sha256"]=sha(base_raw)
    manifest["source_audio_evidence_ledger_sha256"]=sha(ledger_bytes)
    encoded="".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows)
    manifest["current_source_roles_sha256"]=sha(encoded.encode("utf-8"))
    output.mkdir(parents=True,exist_ok=True)
    (output/NEW_READER).write_text(encoded,"utf-8")
    manifest["working_manuscript_sha256_by_episode"]={}
    for ep in ("S01E01","S09E19"):
        source_sha=load_witness(root,ep)[0]["sha256"]
        lines=[f"# {ep}: private true-source original-series speaker-first v9","",
            "All character labels are EDITORIAL PROVISIONAL, not independently",
            "identified actors. Sources are frozen exact original captions;",
            "S09 original paragraph timecodes remain absent.",
            f"Original source caption SHA256: {source_sha}",""]
        for row in rows:
            if row["episode_id"]!=ep:
                continue
            label=row["candidate_role"] or "UNIDENTIFIED SPEAKER"
            lines += [
                f"### {row['source_reading_ref']} ({', '.join(row['original_source_part_refs'])})",
                label+" · "+row["role_attribution_status"],
                row["caption_text"],""
            ]
        manuscript="\n".join(lines).rstrip()+"\n"
        (output/f"{ep}-source-speaker-v9.md").write_text(manuscript,"utf-8")
        manifest["working_manuscript_sha256_by_episode"][ep]=sha(manuscript.encode("utf-8"))
    (output/NEW_MANIFEST).write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n","utf-8")
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--current-v8",type=Path,required=True)
    p.add_argument("--ledger",type=Path,default=ROOT/"research/s09-original-source-acoustic-speaker-proposals-v1.json")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    report=build(args.root,args.current_v8,args.ledger,args.output)
    print(f"{report['current_working_named_provisional_original_units']}/751 original source units "
          "now have UNVERIFIED working character names; "
          f"{report['unidentified_original_cue_units']} still unknown, "
          "1 conflicting model candidate quarantined; 0 independently soundtrack actor IDs accepted")


if __name__=="__main__":
    main()
