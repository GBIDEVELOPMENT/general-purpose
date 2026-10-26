#!/usr/bin/env python3
"""Add *actual original-audio-backed but UNVERIFIED* S01 role proposals to v7.

The source voice embedding model produced six source-verified AVI/caption-role
comparisons, FOUR new unknown cue role candidates and two agreements with
existing editorial suggestions. Never claim identity certified by actual
watching/listening or reference-seed-independent evaluation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from build_pilot_fan_beat_cards import ROOT, load_witness

SCHEMA="night-court-private-original-source-acoustic-speaker-reader/1"
LEDGER_SCHEMA="night-court-actual-s01-source-voice-embedding-proposals/1"
INPUT_ROLE_SCHEMA="night-court-private-character-dialogue-evidence/1"
REPORT_SHA="9729ed2882df04fcdc3706a491875e836873d334f5121be8d65809833e4a25e1"
V8_STATUS="original_soundtrack_embedding_support_not_audio_verified"
EXPECTED_NEW={"C074.1","C095.1","C161.1","C179.1"}
EXPECTED_SUPPORT={"C097.1","C172.1"}
INPUT_FILE="pilot-provisional-context-character-reads.jsonl"
INPUT_REPORT="pilot-contextual-speaker-manifest.json"
OUTPUT_FILE="pilot-original-acoustic-speaker-reads.jsonl"
OUTPUT_REPORT="pilot-original-acoustic-speaker-manifest.json"


def digest(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def validated_source_ledger(ledger:dict, original_sha:str):
    if (ledger.get("schema")!=LEDGER_SCHEMA
        or ledger.get("original_caption_sha256")!=original_sha
        or ledger.get("original_movie_sha256")!="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
        or ledger.get("full_original_numeric_report_sha256")!=REPORT_SHA
        or ledger.get("source_original_unknown_audio_samples_compared")!=42
        or ledger.get("voice_model_role_suggestions_that_passed_threshold")!=6
        or ledger.get("voice_model_abstentions")!=36
        or ledger.get("crossvalidation",{}).get("held_out_samples")!=75
        or ledger.get("crossvalidation",{}).get("correct_predicted_provisional_roles")!=56
        or ledger.get("crossvalidation",{}).get("independent_human_actor_identity_acceptances")!=0
        or ledger.get("cannot_automatically_confirm_actor_id") is not True
        or ledger.get("model")!="resemblyzer-0.1.4"):
        raise ValueError("Unrecognized or false original soundtrack provenance")
    rows=ledger.get("proposals")
    if not isinstance(rows,list) or len(rows)!=6:
        raise ValueError("Expected exactly six source-acoustic numeric findings")
    collected={}
    for item in rows:
        ref=item.get("source_ref")
        if (not isinstance(ref,str) or not re.fullmatch(r"C\d{3}\.1",ref)
            or ref in collected
            or item.get("voice_model_proposed_role") not in
                ("DAN FIELDING","HARRY STONE","LANA WAGNER")
            or item.get("original_soundtrack_was_processed") is not True
            or item.get("actor_id_independently_verified") is not False
            or type(item.get("cosine_similarity")) not in (float,int)
            or type(item.get("next_best_margin")) not in (float,int)
            or not .68<=item["cosine_similarity"]<=1
            or not .09<=item["next_best_margin"]<=1):
            raise ValueError("Unsafe unverified voice model role proposal")
        collected[ref]=item
    if set(collected)!=(EXPECTED_NEW|EXPECTED_SUPPORT):
        raise ValueError("Acoustic original cue identities have drifted")
    return collected


def apply(old:list[dict], ledger:dict, original_sha:str,
          require_full:bool=True)->tuple[list[dict],dict]:
    voice=validated_source_ledger(ledger,original_sha)
    rows=[dict(x) for x in old]
    refs={}
    for i,row in enumerate(rows):
        if row.get("episode_id")=="S01E01":
            key=row.get("source_reading_ref")
            refs.setdefault(key,[]).append(i)
    new=[]
    agrees=[]
    for ref,item in voice.items():
        indices=refs.get(ref,[])
        if len(indices)!=1:
            raise ValueError("Source voice result missing or ambiguous in prior speaker reader")
        original=rows[indices[0]]
        if (original.get("schema")!=INPUT_ROLE_SCHEMA
            or original.get("original_source_sha256")!=original_sha
            or original.get("original_source_part_refs")!=[ref]
            or original.get("speaker_turn_boundary_verified") is not False
            or original.get("actor_face_or_voice_independently_verified") is not False):
            raise ValueError("Improper original cue source identity for acoustic candidate")
        previously=original.get("candidate_role")
        name=item["voice_model_proposed_role"]
        if previously is None:
            if ref not in EXPECTED_NEW or original.get("role_attribution_status")!="unidentified":
                raise ValueError("Source-acoustic result attempts unsupported role overwrite")
            original["candidate_role"]=name
            original["role_attribution_status"]=V8_STATUS
            new.append(ref)
        else:
            if ref not in EXPECTED_SUPPORT or previously!=name:
                raise ValueError("Original soundtrack disagrees with earlier character role")
            agrees.append(ref)
        original.update({
            "original_soundtrack_acoustic_similarity_proposal_only":True,
            "source_acoustic_model":"resemblyzer-0.1.4",
            "source_acoustic_cosine_similarity":item["cosine_similarity"],
            "source_acoustic_runner_up_margin":item["next_best_margin"],
            "source_acoustic_numeric_report_sha256":REPORT_SHA,
            "source_acoustic_role_source_conditioned_on_previous_provisional_labels":True,
            "original_soundtrack_human_speaker_identity_verified":False,
            "speaker_turn_boundary_verified":False,
            "actor_face_or_voice_independently_verified":False,
        })
    units={}
    for row in rows:
        for ref in row["original_source_part_refs"]:
            key=(row["episode_id"],ref)
            units.setdefault(key,set()).add(row.get("candidate_role"))
    named=sum(None not in vals for vals in units.values())
    summary={
        "schema":SCHEMA,
        "original_source_caption_units":len(units),
        "source_units_with_provisional_names":named,
        "original_units_still_unknown":len(units)-named,
        "new_original_audio_model_supported_provisional_role_units":len(new),
        "provisional_previous_speaker_roles_corrob_by_acoustics":len(agrees),
        "new_role_source_refs":sorted(new),
        "corroboration_refs":sorted(agrees),
        "original_audio_model_candidates":len(voice),
        "source_speaker_identities_human_verified_by_pass":0,
        "source_video_sha256":ledger["original_movie_sha256"],
        "original_audio_embedding_quality_holdout":"56/75 provisional labels",
        "original_cue_to_source_role_association_remains_unverified":True
    }
    if require_full and (len(rows),len(units),named,len(units)-named,len(new),len(agrees)) != (716,751,587,164,4,2):
        raise ValueError("V8 pilot original-source speaker-name ledger drift")
    return rows,summary


def build(root:Path, v7_root:Path, ledger_path:Path, output:Path)->dict:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private screenplay/role text may not be written into repository")
    _,cue_meta=load_witness(root,"S01E01")
    # load_witness actually returns metadata, cues; explicitly checked below
    meta=_
    if meta["sha256"]!="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496":
        raise ValueError("Wrong original S01 source caption")
    v7_raw=(v7_root/INPUT_FILE).read_bytes()
    v7_meta=json.loads((v7_root/INPUT_REPORT).read_text("utf-8"))
    if (digest(v7_raw)!=v7_meta.get("reading_record_sha256")
        or v7_meta.get("source_units_provisionally_named")!=583
        or v7_meta.get("source_units_unknown")!=168
        or v7_meta.get("audio_confirmed_by_this_pass")!=0):
        raise ValueError("Wrong original provisional baseline")
    original=[json.loads(x) for x in v7_raw.decode("utf-8").splitlines() if x.strip()]
    raw_evidence=ledger_path.read_bytes()
    ledger=json.loads(raw_evidence)
    updated,summary=apply(original,ledger,meta["sha256"])
    summary["acoustic_ledger_sha256"]=digest(raw_evidence)
    summary["previous_private_reader_sha256"]=digest(v7_raw)
    output.mkdir(parents=True,exist_ok=True)
    encoded="".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in updated)
    (output/OUTPUT_FILE).write_text(encoded,"utf-8")
    summary["source_role_record_sha256"]=digest(encoded.encode("utf-8"))
    summary["source_reader_sha256_by_episode"]={}
    for ep in ("S01E01","S09E19"):
        lines=[f"# {ep}: speaker-first original caption private reader (v8)","",
              "Original source speech unit evidence. All identity labels are provisional;",
              "four S01 new names are supported by unverified local voice embedding similarity;",
              "no actor or true performance-turn segmentation independently reviewed.",
              f"Original source SHA256: {load_witness(root,ep)[0]['sha256']}",""]
        for row in updated:
            if row["episode_id"]!=ep:
                continue
            role=row["candidate_role"] or "UNIDENTIFIED SPEAKER"
            lines += [
                f"### {row['source_reading_ref']} ({', '.join(row['original_source_part_refs'])})",
                f"{role} · {row['role_attribution_status']}",
                row["caption_text"],"",
            ]
        body="\n".join(lines).rstrip()+"\n"
        filename=f"{ep}-source-speaker-v8.md"
        (output/filename).write_text(body,"utf-8")
        summary["source_reader_sha256_by_episode"][ep]=digest(body.encode("utf-8"))
    (output/OUTPUT_REPORT).write_text(
        json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2)+"\n","utf-8")
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--v7",type=Path,required=True)
    p.add_argument("--ledger",type=Path,default=ROOT/"research/s01e01-source-voice-acoustic-proposals-v1.json")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=build(a.root,a.v7,a.ledger,a.output)
    print(f"{result['source_units_with_provisional_names']}/{result['original_source_caption_units']} "
          "original units now have provisional source-grounded role candidates; "
          f"{result['original_units_still_unknown']} still unknown; "
          "zero new independently actor-ID verified")


if __name__=="__main__":
    main()
