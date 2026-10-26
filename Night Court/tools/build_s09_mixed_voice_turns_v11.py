#!/usr/bin/env python3
"""Reversible source-exact candidate P0 role turns for S09 C188-C192.

This mixed exchange has rapid back-and-forth overlapping held subtitle
paragraphs. The NEW turns are *context-derived, NOT observed/verified*; each
source caption is represented as one or more Unicode exact text spans that
reconstruct its original line character by character. The original untimed
347 paragraph held source and all source SHAs remain intact. This adds
provisional working stage-dialogue to help an LLM understand the exchange,
not evidence that two performers were independently recognized by audio.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from build_pilot_fan_beat_cards import ROOT,load_witness

SCHEMA="night-court-original-s09-multi-voice-role-turns-v11/1"
OLD_ROWS="pilot-current-source-turns-v10.jsonl"
OLD_META="pilot-current-source-turns-v10-manifest.json"
NEW_ROWS="pilot-current-multi-voice-turns-v11.jsonl"
NEW_META="pilot-current-multi-voice-turns-v11-manifest.json"
SOURCE_SHA="659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
STATUS="scene_context_mixed_speaker_turn_proposal_not_audio_verified"
TARGETS=["C188.1","C189.1","C190.1","C191.1","C192.1"]
# Exact unique lexical split anchors. THESE ARE PROVISIONAL SPEAKER TURN
# BOUNDARIES requiring actual moving-source audio/video review.
DELIMITERS={
    "C188.1":["oh roz"],
    "C189.1":["i can't face him"],
    "C190.1":["i think you're missing","yeah i"],
    "C191.1":["there's only one way"],
    "C192.1":[]
}
OLD_ROLES={
    "C188.1":None,"C189.1":None,
    "C190.1":"CHRISTINE SULLIVAN",
    "C191.1":None,"C192.1":None
}
# A turn may span partial source-caption parts and adjacent original
# paragraphs. Group boundaries are scene-dialogue hypotheses only.
GROUPS=[
 ("ROZ RUSSELL",[("C188.1",0)]),
 ("CHRISTINE SULLIVAN",[("C188.1",1),("C189.1",0)]),
 ("ROZ RUSSELL",[("C189.1",1),("C190.1",0)]),
 ("CHRISTINE SULLIVAN",[("C190.1",1)]),
 ("ROZ RUSSELL",[("C190.1",2),("C191.1",0)]),
 ("CHRISTINE SULLIVAN",[("C191.1",1),("C192.1",0)]),
]

def digest(payload:bytes)->str:
    return hashlib.sha256(payload).hexdigest()

def splits(text:str, phrases:list[str])->list[tuple[int,int,str]]:
    starts=[0]
    for phrase in phrases:
        if text.count(phrase)!=1:
            raise ValueError("Source-original exact in-cue voice switch phrase missing or duplicated")
        start=text.index(phrase)
        if start<=starts[-1] or start>=len(text):
            raise ValueError("Impossible nonmonotone original source cue speaker split")
        starts.append(start)
    starts.append(len(text))
    pieces=[(a,b,text[a:b]) for a,b in zip(starts,starts[1:])]
    if not all(x[2].strip() for x in pieces):
        raise ValueError("Original episode cannot carry an empty performed speech segment")
    if "".join(x[2] for x in pieces)!=text:
        raise ValueError("Exact held source paragraph text was lost")
    return pieces

def transform(old:list[dict],full:bool=True)->tuple[list[dict],dict]:
    located={}
    for i,row in enumerate(old):
        if row["episode_id"]=="S09E19" and row["source_reading_ref"] in TARGETS:
            if row["source_reading_ref"] in located:
                raise ValueError("Original source cue has duplicate prior reading blocks")
            located[row["source_reading_ref"]]=(i,row)
    if set(located)!=set(TARGETS):
        raise ValueError("One original S09 mixed-speaker paragraph was absent")
    first=located[TARGETS[0]][0]
    if [located[ref][0] for ref in TARGETS]!=list(range(first,first+5)):
        raise ValueError("Original S09 mixed-voice source paragraphs not adjacent")
    cue_parts={}
    index=[]
    for ref in TARGETS:
        prior=located[ref][1]
        if (prior.get("original_source_sha256")!=SOURCE_SHA
            or prior.get("original_source_part_refs")!=[ref]
            or prior.get("candidate_role")!=OLD_ROLES[ref]
            or prior.get("original_source_untimed") is not True
            or prior.get("source_original_times_ms") is not None
            or prior.get("speaker_turn_boundary_verified") is not False
            or prior.get("actor_face_or_voice_independently_verified") is not False
            or not isinstance(prior.get("caption_text"),str)
            or not prior["caption_text"]):
            raise ValueError("Original mixed-speaker source cue or v10 provisional role drift")
        cue_parts[ref]=splits(prior["caption_text"],DELIMITERS[ref])
        index.append((ref,prior["reading_block_id"]))
    used=defaultdict(list)
    new=[]
    for number,(role,members) in enumerate(GROUPS,1):
        selected=[]
        for ref,partid in members:
            if ref not in cue_parts or not 0<=partid<len(cue_parts[ref]):
                raise ValueError("A voice turn references nonexistent original source text")
            a,b,piece=cue_parts[ref][partid]
            used[ref].append(partid)
            selected.append((ref,a,b,piece))
        joined=" ".join(piece.strip() for _,_,_,piece in selected)
        if not joined:
            raise ValueError("Empty provisional character dialogue")
        source_refs=list(dict.fromkeys(ref for ref,_,_,_ in selected))
        original=located[members[0][0]][1]
        row=dict(original)
        row.update({
          "reading_block_id":f"S09E19:mixed-source-turn-v11:{number:02d}",
          "source_reading_ref":f"S09-C188-C192-T{number:02d}",
          "original_source_part_refs":source_refs,
          "original_source_sha256":SOURCE_SHA,
          "caption_text":joined,
          "candidate_role":role,
          "role_attribution_status":STATUS,
          "source_original_untimed":True,
          "source_original_times_ms":None,
          "source_original_unicode_spans":[
              {"source_ref":ref,"start_char":a,"end_char":b,
               "exact_text_sha256":digest(piece.encode("utf-8"))}
              for ref,a,b,piece in selected
          ],
          "original_source_sentence_segments_exact_original":True,
          "original_two_performer_scene_not_actually_verified":True,
          "actor_face_or_voice_independently_verified":False,
          "speaker_turn_boundary_verified":False,
          "speaker_identity_provisional_from_unverified_scene_context":True,
          "superseded_original_v10_reading_block_ids":[key for _,key in index],
          "source_T188_T192_prior_entire_cue_character_roles_not_treated_as_verified":True,
        })
        # Don't retain old, whole-cue source-v10 voice evidence that applies
        # to a different substring/character after the split.
        for field in tuple(row):
            if field.startswith("source_acoustic_") or field in (
                "original_soundtrack_human_role_reviewed",
                "speaker_identity_provisional_from_model_and_context",
                "quarantined_acoustic_alternative_only",
                "original_source_part_original_text_sha256",
                "merged_original_speaking_units_previously_unidentified",
                "merged_provisional_previous_role_source_ref",
            ):
                row.pop(field,None)
        new.append(row)
    for ref,pieces in cue_parts.items():
        if sorted(used[ref])!=list(range(len(pieces))):
            raise ValueError("Original source speech span duplicated or missing")
        # Strict source-character conservation, including whitespace
        prior=located[ref][1]
        extracted={}
        for row in new:
            for x in row["source_original_unicode_spans"]:
                if x["source_ref"]==ref:
                    a,b=x["start_char"],x["end_char"]
                    if a in extracted:
                        raise ValueError("Duplicated source paragraph character span")
                    piece=prior["caption_text"][a:b]
                    if digest(piece.encode())!=x["exact_text_sha256"]:
                        raise ValueError("Private review source text SHA no longer matches")
                    extracted[a]=(b,piece)
        a=0
        recovered=[]
        for start,(end,piece) in sorted(extracted.items()):
            if start!=a:
                raise ValueError("Gap in original source paragraph reconstructed speech")
            recovered.append(piece)
            a=end
        if a!=len(prior["caption_text"]) or "".join(recovered)!=prior["caption_text"]:
            raise ValueError("Full original S09 paragraph text was altered")
    output=old[:first]+new+old[first+5:]
    if len(output)!=len(old)+1:
        raise ValueError("Wrong number of provisional performance turns")
    before={(r["episode_id"],ref) for r in old for ref in r["original_source_part_refs"]}
    after=defaultdict(set)
    for row in output:
        for ref in row["original_source_part_refs"]:
            after[(row["episode_id"],ref)].add(row["candidate_role"])
    if set(after)!=before:
        raise ValueError("Changed original S09 cue coverage")
    named=sum(None not in labels for labels in after.values())
    result={
       "schema":SCHEMA,
       "original_caption_units":len(after),
       "provisional_named_original_units":named,
       "original_units_remaining_unknown":len(after)-named,
       "private_provisional_reading_turn_blocks_before":len(old),
       "private_provisional_reading_turn_blocks_after":len(output),
       "mixed_source_paragraphs_reviewed_for_candidate_p0_turns":TARGETS,
       "candidate_scene_turns_inserted":len(new),
       "role_attribution_status":STATUS,
       "potential_character_voice_and_turn_verifications_from_actual_original_av":0,
       "original_untimed_S09_source_preserved":True,
       "actual_audio_review_performed":False,
       "original_source_fully_reconstructable_via_unicode_spans":True,
       "all_original_text_sha256_by_source_ref":{
           ref:digest(located[ref][1]["caption_text"].encode("utf-8")) for ref in TARGETS
       },
    }
    if full and (len(old),len(output),len(after),named,len(after)-named)!=(715,716,751,595,156):
        raise ValueError("New scene P0 proposal shifted unexpected original unit accounting")
    return output,result

def build(root:Path,v10:Path,out:Path)->dict:
    if out.resolve().is_relative_to(root.resolve()):
        raise ValueError("Original private source text cannot enter the repo")
    raw=(v10/OLD_ROWS).read_bytes()
    m=json.loads((v10/OLD_META).read_text("utf-8"))
    if (digest(raw)!=m.get("current_source_role_records_sha256")
        or m.get("original_caption_immutable_source_units")!=751
        or m.get("current_provisional_character_named_original_units")!=591
        or m.get("still_unknown_original_source_units")!=160
        or m.get("reader_speaker_turn_blocks_after")!=715
        or m.get("source_audio_human_actor_identity_confirmations_added")!=0):
        raise ValueError("Old private S09 v10 source-role prerequisite not validated")
    meta,_=load_witness(root,"S09E19")
    if meta["sha256"]!=SOURCE_SHA or meta["timecoded"] is not False:
        raise ValueError("Frozen original S09 paragraph source changed or invented timestamp")
    prior=[json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    result,summary=transform(prior)
    out.mkdir(parents=True,exist_ok=True)
    encoded="".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in result)
    (out/NEW_ROWS).write_text(encoded,"utf-8")
    summary["current_provisional_turn_records_sha256"]=digest(encoded.encode("utf-8"))
    summary["old_v10_source_role_records_sha256"]=digest(raw)
    summary["private_manuscripts_sha256_by_episode"]={}
    for ep in ("S01E01","S09E19"):
        witness=load_witness(root,ep)[0]
        lines=[f"# {ep}: current source-first provisional speaker turns v11","",
               "This private manuscript preserves all ORIGINAL source words and cue IDs.",
               "Role, actor identity and internal speaker boundaries are EDITORIAL",
               "proposals. They have NOT been verified from moving-source AV.",
               f"Frozen original caption SHA256: {witness['sha256']}",""]
        for row in result:
            if row["episode_id"]!=ep:continue
            role=row["candidate_role"] or "UNIDENTIFIED SPEAKER"
            lines += [f"### {row['source_reading_ref']} ({', '.join(row['original_source_part_refs'])})",
                      role+" · "+row["role_attribution_status"],row["caption_text"],""]
        text="\n".join(lines).rstrip()+"\n"
        (out/f"{ep}-source-turns-v11.md").write_text(text,"utf-8")
        summary["private_manuscripts_sha256_by_episode"][ep]=digest(text.encode("utf-8"))
    (out/NEW_META).write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n","utf-8")
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--v10",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    r=build(a.root,a.v10,a.output)
    print(f"{r['provisional_named_original_units']}/{r['original_caption_units']} original units now have UNVERIFIED role proposals; "
          f"{r['original_units_remaining_unknown']} remain UNKNOWN; "
          "rapid Roz/Christine mixed-caption scene divided into source-reconstructable candidate speaking turns, zero independent AV identity approvals")

if __name__=="__main__":
    main()
