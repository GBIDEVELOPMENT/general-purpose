#!/usr/bin/env python3
"""Source-exact S09 P0 speaker handoff candidates C127/C146/C284.

A single originally UNTIMED subtitle paragraph can contain speech by two
characters; the C126→127 Harriet turn also crosses a paragraph boundary.
This tool never changes the original subtitle cue text or timing; it builds
a private and wholly reversible *provisional* source-role dialogue reader.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from build_pilot_fan_beat_cards import ROOT,load_witness

SCHEMA="night-court-original-s09-source-character-turns-v13/1"
LEDGER_SCHEMA="night-court-s09-original-dialogue-split-and-reunion-v13/1"
LEDGER=ROOT/"research/s09-explicit-address-speaker-turns-v13.json"
SOURCE_SHA="659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
OLD_ROWS="pilot-original-speaker-context-v12.jsonl"
OLD_MANIFEST="pilot-original-speaker-context-v12-manifest.json"
NEW_ROWS="pilot-source-dialogue-turns-v13.jsonl"
NEW_MANIFEST="pilot-source-dialogue-turns-v13-manifest.json"
STATUS="source_context_named_character_handoff_proposal_not_original_AV_verified"
EXPECTED={
 "C127.1":(["C126.1","C127.1"],"Well, thanks, Harriet.",
            ["HARRIET","MAC ROBINSON"]),
 "C146.1":(["C146.1"],"Yeah, thanks, Dan.",
            ["DAN FIELDING","HARRY STONE"]),
 "C284.1":(["C284.1"],"Out of here.",
            ["ALEX PATTERSON","ROZ RUSSELL"])
}
OLD_ROLE={"C126.1":"HARRIET","C127.1":None,
          "C146.1":None,"C284.1":None}

def digest(text:bytes)->str:return hashlib.sha256(text).hexdigest()

def check_ledger(data:dict)->list[dict]:
    if (data.get("schema")!=LEDGER_SCHEMA
        or data.get("original_source_sha256")!=SOURCE_SHA
        or data.get("working_source_reader_prior")!="v12"
        or data.get("prior_named_original_source_units")!=610
        or data.get("prior_unknown_original_source_units")!=141
        or data.get("original_s09_untimed_source_modified") is not False
        or data.get("original_speaker_turns_independently_soundtrack_verified") is not False
        or data.get("roles_original_actor_voice_verified") is not False):
        raise ValueError("Changed source S09 speaker split evidence would overstate original film proof")
    ops=data.get("proposals")
    if not isinstance(ops,list) or len(ops)!=3:
        raise ValueError("Expected three exact original 1992 scene voice handoff questions")
    seen=set()
    for op in ops:
        ref=op.get("split_source_ref")
        if ref in seen or ref not in EXPECTED:
            raise ValueError("Unrecognized or duplicate original two-voice source subtitle")
        seen.add(ref)
        refs,phrase,roles=EXPECTED[ref]
        if (op.get("previous_source_reading_refs")!=refs
            or op.get("split_before")!=phrase
            or not isinstance(op.get("reason"),str) or len(op["reason"])<55
            or not isinstance(op.get("split_role_groups"),list)
            or len(op["split_role_groups"])!=2
            or [r.get("provisional_role") for r in op["split_role_groups"]]!=roles):
            raise ValueError("Original source speaking roles/split boundary differ from scene evidence")
        wanted=( [[["C126.1","whole"],["C127.1",0]],[["C127.1",1]]]
                 if ref=="C127.1" else [[[ref,0]],[[ref,1]]] )
        if [r.get("source_parts") for r in op["split_role_groups"]]!=wanted:
            raise ValueError("Unsupported source-character spanning or partial cue"
                             " (does not conserve original 1992 dialogue)")
    if seen!=set(EXPECTED):
        raise ValueError("Original source split cue missing")
    return ops


def transform(rows:list[dict],ledger:dict,strict:bool=True)->tuple[list[dict],dict]:
    operations=check_ledger(ledger)
    index={}
    all_original_cue_refs={(r["episode_id"],ref) for r in rows
                           for ref in r["original_source_part_refs"]}
    for i,row in enumerate(rows):
        if row["episode_id"]=="S09E19" and row["source_reading_ref"] in OLD_ROLE:
            key=row["source_reading_ref"]
            if key in index:
                raise ValueError("Original source role duplicate before stage-turn transformation")
            if (row.get("candidate_role")!=OLD_ROLE[key]
                or row.get("original_source_part_refs")!=[key]
                or row.get("original_source_sha256")!=SOURCE_SHA
                or row.get("original_source_untimed") is not True
                or row.get("source_original_times_ms") is not None
                or row.get("speaker_turn_boundary_verified") is not False
                or row.get("actor_face_or_voice_independently_verified") is not False):
                raise ValueError("Original source role/untimed cue state drift")
            index[key]=(i,row)
    if set(index)!=set(OLD_ROLE):
        raise ValueError("Missing prior exact S09 source paragraphs to split")
    old=rows[:]
    for op in sorted(operations,key=lambda x:index[x["previous_source_reading_refs"][0]][0],
                     reverse=True):
        refs=op["previous_source_reading_refs"]
        start=index[refs[0]][0]
        if [index[ref][0] for ref in refs]!=list(range(start,start+len(refs))):
            raise ValueError("Original speaker turn source cues not consecutive")
        original={ref:index[ref][1] for ref in refs}
        cue=original[op["split_source_ref"]]["caption_text"]
        phrase=op["split_before"]
        if cue.count(phrase)!=1:
            raise ValueError("Actual original cue lacks unique claimed speaker handoff phrase")
        cut=cue.index(phrase)
        if not 0<cut<len(cue) or not cue[:cut].strip() or not cue[cut:].strip():
            raise ValueError("Original speaker boundary cannot be placed at claimed exact text")
        spans={ref:{ "whole":(0,len(original[ref]["caption_text"]))} for ref in refs}
        spans[op["split_source_ref"]][0]=(0,cut)
        spans[op["split_source_ref"]][1]=(cut,len(cue))
        new=[]
        consumed=defaultdict(list)
        for number,group in enumerate(op["split_role_groups"]):
            fragments=[]
            text_parts=[]
            for ref,kind in group["source_parts"]:
                a,b=spans[ref][kind]
                txt=original[ref]["caption_text"][a:b]
                if not txt.strip():raise ValueError("Original performer utterance cannot be empty")
                consumed[ref].append((a,b,txt))
                text_parts.append(txt.strip())
                fragments.append({
                    "original_source_ref":ref,
                    "start_char":a,"end_char":b,
                    "original_exact_text_sha256":digest(txt.encode("utf-8"))
                })
            role=group["provisional_role"]
            primary=original[group["source_parts"][0][0]]
            output=dict(primary)
            output.update({
                "reading_block_id":f"S09E19:source-speaker-turn-v13:{op['split_source_ref']}:{number+1}",
                "source_reading_ref":f"S09-{op['split_source_ref']}-TURN-{number+1}",
                "original_source_part_refs":list(dict.fromkeys(x["original_source_ref"] for x in fragments)),
                "caption_text":" ".join(text_parts),
                "candidate_role":role,
                "role_attribution_status":STATUS,
                "original_source_unicode_spans_v13":fragments,
                "previous_v12_original_reading_block_ids":[original[ref]["reading_block_id"] for ref in refs],
                "speaker_identity_provisional_from_context":True,
                "source_context_supporting_reason":op["reason"],
                "source_previous_roles_not_independently_av_confirmed":True,
                "source_original_untimed_cue_preserved":True,
                "source_original_times_ms":None,
                "original_source_untimed":True,
                "speaker_turn_boundary_verified":False,
                "actor_face_or_voice_independently_verified":False,
                "human_viewed_film_or_listened_to_actor":False,
                "original_soundtrack_speaker_id_accepted":False,
            })
            # Don't inherit an old whole-cue model confidence onto only
            # one subset of the newly split performed lines.
            for name in tuple(output):
                if (name.startswith("source_acoustic_") or
                    name.startswith("quarantined_acoustic_") or
                    name=="original_soundtrack_human_role_reviewed"):
                    output.pop(name,None)
            new.append(output)
        for ref,row in original.items():
            entries=sorted(consumed[ref],key=lambda x:x[0])
            if (not entries or entries[0][0]!=0
                or entries[-1][1]!=len(row["caption_text"])
                or any(a[1]!=b[0] for a,b in zip(entries,entries[1:]))
                or "".join(x[2] for x in entries)!=row["caption_text"]):
                raise ValueError("Original source paragraph omitted/duplicated a character")
        old[start:start+len(refs)]=new
    accounted=defaultdict(set)
    for r in old:
        for ref in r["original_source_part_refs"]:
            accounted[(r["episode_id"],ref)].add(r["candidate_role"])
    if set(accounted)!=all_original_cue_refs:
        raise ValueError("Original 751 caption part refs changed in source turn splitting")
    named=sum(None not in names for names in accounted.values())
    report={
        "schema":SCHEMA,
        "original_held_caption_units":len(accounted),
        "provisionally_named_original_caption_units":named,
        "unidentified_original_caption_units":len(accounted)-named,
        "previous_provisional_speaking_turns":len(rows),
        "new_provisional_speaking_turns":len(old),
        "original_s09_multi_voice_cues_split":["C127.1","C146.1","C284.1"],
        "original_s09_untimed_source_changed":False,
        "all_source_character_spans_reversible":True,
        "source_audio_actor_identities_or_true_turns_independently_verified":0,
        "provisional_role_naming_performed_from_original_scene_context_only":True,
    }
    if strict and (len(rows),len(old),len(accounted),named,len(accounted)-named)!=(
        716,718,751,613,138):
        raise ValueError("Private S09 original-source v13 named coverage/speaker-turn count drift")
    return old,report


def build(root:Path,v12:Path,ledger_path:Path,output:Path)->dict:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private original episode dialogue must stay outside repository")
    raw=(v12/OLD_ROWS).read_bytes()
    m=json.loads((v12/OLD_MANIFEST).read_text("utf-8"))
    if (digest(raw)!=m.get("v12_source_roles_sha256")
        or m.get("original_caption_source_units")!=751
        or m.get("current_provisional_character_named_original_units")!=610
        or m.get("still_unknown_original_source_units")!=141
        or m.get("current_original_speaker_reading_blocks")!=716
        or m.get("original_soundtrack_actor_identities_independently_reviewed_and_accepted")!=0):
        raise ValueError("Source v12 high-context actor reading prerequisite not validated")
    meta,cues=load_witness(root,"S09E19")
    if meta["sha256"]!=SOURCE_SHA or meta["timecoded"] is not False or len(cues)!=347:
        raise ValueError("Original 347 S09 paragraphs changed or fictional timestamp added")
    instructions=ledger_path.read_bytes()
    ledger=json.loads(instructions)
    for op in check_ledger(ledger):
        for ref in op["previous_source_reading_refs"]:
            n=int(ref[1:4])
            if cues[n-1]["start_ms"] is not None or cues[n-1]["end_ms"] is not None:
                raise ValueError("Original S09 source oddly gained exact subtitle timecodes")
        if op["split_before"] not in cues[int(op["split_source_ref"][1:4])-1]["text"]:
            raise ValueError("P0 source-bound speaker handoff phrase absent from held original")
    previous=[json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    result,report=transform(previous,ledger)
    output.mkdir(parents=True,exist_ok=True)
    encoded="".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in result)
    (output/NEW_ROWS).write_text(encoded,"utf-8")
    report["original_s09_turn_proposals_source_sha256"]=SOURCE_SHA
    report["v13_records_sha256"]=digest(encoded.encode("utf-8"))
    report["v12_source_records_sha256"]=digest(raw)
    report["source_turn_ledger_sha256"]=digest(instructions)
    report["private_manuscript_sha256_by_episode"]={}
    for episode in ("S01E01","S09E19"):
        w=load_witness(root,episode)[0]
        lines=[f"# {episode}: original Night Court source-first character-turns v13","",
               "Provisional character and speaking-turn interpretations, NOT"
               " verified performer identities.",
               "Frozen original subtitle text/cue part SHA and original clock status preserved.",
               f"Original episode caption SHA256: {w['sha256']}",""]
        for row in result:
            if row["episode_id"]!=episode:continue
            who=row["candidate_role"] or "UNIDENTIFIED SPEAKER"
            lines.extend([f"### {row['source_reading_ref']} ({', '.join(row['original_source_part_refs'])})",
                          who+" · "+row["role_attribution_status"],row["caption_text"],""])
        script="\n".join(lines).rstrip()+"\n"
        (output/f"{episode}-source-turns-v13.md").write_text(script,"utf-8")
        report["private_manuscript_sha256_by_episode"][episode]=digest(script.encode("utf-8"))
    (output/NEW_MANIFEST).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n","utf-8")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--v12",type=Path,required=True)
    p.add_argument("--ledger",type=Path,default=LEDGER)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    r=build(a.root,a.v12,a.ledger,a.output)
    print(f"{r['provisionally_named_original_caption_units']}/751 source cue units have provisional roles, "
          f"{r['unidentified_original_caption_units']} remain UNKNOWN; "
          "three exact-original intra-cue character handoffs reconstructed, 0 genuine performer reviews accepted")

if __name__=="__main__":
    main()
