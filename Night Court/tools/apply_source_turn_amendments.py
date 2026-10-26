#!/usr/bin/env python3
"""Reusable, exact-character original transcript speaking-turn amendments.

An amendment is a proposed source-text segmentation and provisional role
assignment, not audiovisual confirmation of a TV performance. Private reader
transforms retain 100% of exact original Unicode characters and source refs.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from build_pilot_fan_beat_cards import ROOT, load_witness

SCHEMA="night-court-private-original-speaker-turn-amendments/1"
LEDGER_SCHEMA="night-court-original-speaker-turn-amendments/1"
LEDGER=ROOT/"research/source-turn-amendments-v1.json"
SOURCE_SHA="659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
OLD_ROWS="pilot-source-role-amendments.jsonl"
OLD_MANIFEST="pilot-source-role-amendments-manifest.json"
NEW_ROWS="pilot-source-turn-amendments.jsonl"
NEW_MANIFEST="pilot-source-turn-amendments-manifest.json"
STATUS="original_dialogue_text_turn_split_context_proposal_not_original_AV_verified"

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def validate_ledger(ledger:dict)->list[dict]:
    if (ledger.get("schema")!=LEDGER_SCHEMA
        or ledger.get("source_episode_id")!="S09E19"
        or ledger.get("source_witness_sha256")!=SOURCE_SHA
        or ledger.get("prior_source_role_ledger")!="night-court-source-role-amendment-ledger/1"
        or ledger.get("prior_named_original_source_units")!=619
        or ledger.get("prior_remaining_UNKNOWN")!=132
        or ledger.get("prior_original_source_units")!=751
        or ledger.get("prior_reading_blocks")!=718
        or ledger.get("source_original_untimed") is not True
        or ledger.get("source_audio_actor_identifications_independently_accepted")!=0
        or ledger.get("source_performance_turns_independently_verified")!=0):
        raise ValueError("Original source-turn patch ledger not based on live character/role evidence")
    ops=ledger.get("p0_amendments")
    if not isinstance(ops,list) or not 1<=len(ops)<=30:
        raise ValueError("Original transcript source-turn patch count out of bounds")
    seen=set()
    for op in ops:
        ref=op.get("source_refs")
        if (set(op)!={"id","source_refs","prior_roles","split_before","new_turns",
                     "reason","original_video_audio_confirmed"}
            or not isinstance(op["id"],str) or not 8<=len(op["id"])<=110
            or not isinstance(ref,list) or not 1<=len(ref)<=12
            or any(not isinstance(x,str) or len(x)!=6 or x[0]!="C"
                   or not x[1:4].isdigit() or x[4:]!=".1" for x in ref)
            or not all(int(b[1:4])==int(a[1:4])+1 for a,b in zip(ref,ref[1:]))
            or not isinstance(op.get("prior_roles"),list)
            or len(op["prior_roles"])!=len(ref)
            or any(role is not None for role in op["prior_roles"])
            or not isinstance(op.get("reason"),str) or len(op["reason"])<90
            or op.get("original_video_audio_confirmed") is not False
            or any(r in seen for r in ref)):
            raise ValueError("Original speaking-turn patch improperly verified, duplicate or malformed")
        seen.update(ref)
        cuts=op.get("split_before")
        if not isinstance(cuts,dict) or set(cuts)!=set(ref):
            raise ValueError("Each source paragraph requires explicit split positions, even if none")
        fragment_keys=set()
        for cue,phrases in cuts.items():
            if not isinstance(phrases,list) or len(phrases)>10 or any(
                not isinstance(p,str) or not p.strip() for p in phrases
            ):
                raise ValueError("Invalid original-source lexical turn boundary")
            for index in range(len(phrases)+1):
                fragment_keys.add((cue,index))
        used=[]
        turns=op.get("new_turns")
        if not isinstance(turns,list) or not 2<=len(turns)<=24:
            raise ValueError("Source speaking-turn amendments must visibly change speaker turns")
        for turn in turns:
            if set(turn)!={"role","source_fragments"}:
                raise ValueError("Unexpected unreviewed original actor detail in turn proposal")
            role=turn["role"]
            if role is not None and (not isinstance(role,str) or not 3<=len(role)<=96
                                     or role.upper()!=role):
                raise ValueError("Unverified actor role label malformed")
            fragments=turn["source_fragments"]
            if not isinstance(fragments,list) or not fragments:
                raise ValueError("New performing turn has no original speech")
            for part in fragments:
                if (not isinstance(part,list) or len(part)!=2
                    or not isinstance(part[0],str) or type(part[1])!=int
                    or (part[0],part[1]) not in fragment_keys):
                    raise ValueError("Provisional voice turn refers to nonexistent source substring")
                used.append((part[0],part[1]))
        if len(used)!=len(fragment_keys) or set(used)!=fragment_keys:
            raise ValueError("Source speech fragment used zero times or twice")
        expected=sorted(fragment_keys,key=lambda x:(int(x[0][1:4]),x[1]))
        if used!=expected:
            raise ValueError("Source fragment speaking turns must respect episode dialogue order")
    return ops


def apply(rows:list[dict],ledger:dict,strict:bool=True)->tuple[list[dict],dict]:
    ops=validate_ledger(ledger)
    working=[dict(x) for x in rows]
    old_refs={(r["episode_id"],ref) for r in rows
              for ref in r["original_source_part_refs"]}
    old_voices=defaultdict(set)
    for r in rows:
        for ref in r["original_source_part_refs"]:
            old_voices[(r["episode_id"],ref)].add(r["candidate_role"])
    old_named=sum(None not in roles for roles in old_voices.values())
    if strict and (len(rows),len(old_refs),old_named)!=(718,751,619):
        raise ValueError("Old original role-ledger source speaker state changed")
    for op in sorted(ops,key=lambda x:int(x["source_refs"][0][1:4]),reverse=True):
        byref={r["source_reading_ref"]:(i,r) for i,r in enumerate(working)
               if r["episode_id"]=="S09E19" and
               r["source_reading_ref"] in op["source_refs"]}
        refs=op["source_refs"]
        if len(byref)!=len(refs):
            raise ValueError("Original source paragraphs to split absent or already combined")
        positions=[byref[ref][0] for ref in refs]
        if positions!=list(range(positions[0],positions[0]+len(refs))):
            raise ValueError("Source paragraph speaking units not adjacent as planned")
        originals={}
        parts={}
        for ref,prior_role in zip(refs,op["prior_roles"]):
            prior=byref[ref][1]
            if (prior.get("original_source_sha256")!=SOURCE_SHA
                or prior.get("original_source_part_refs")!=[ref]
                or prior.get("candidate_role")!=prior_role
                or prior.get("role_attribution_status")!="unidentified"
                or prior.get("actor_face_or_voice_independently_verified") is not False
                or prior.get("speaker_turn_boundary_verified") is not False
                or prior.get("source_original_times_ms") is not None
                or prior.get("original_source_untimed") is not True):
                raise ValueError("An original unidentified S09 source cue or AV role changed")
            text=prior["caption_text"]
            starts=[0]
            for phrase in op["split_before"][ref]:
                if text.count(phrase)!=1:
                    raise ValueError("An expected exact original lexical turn boundary was altered")
                pos=text.index(phrase)
                if pos<=starts[-1] or pos>=len(text):
                    raise ValueError("Source speaker turn split is empty or out of order")
                starts.append(pos)
            starts.append(len(text))
            pieces=[(a,b,text[a:b]) for a,b in zip(starts,starts[1:])]
            if any(not frag.strip() for _,_,frag in pieces) or "".join(x[2] for x in pieces)!=text:
                raise ValueError("Original source dialogue characters not completely preserved")
            originals[ref]=prior
            parts[ref]=pieces
        result=[]
        for i,turn in enumerate(op["new_turns"],1):
            spans=[]
            fragments=[]
            for ref,n in turn["source_fragments"]:
                a,b,frag=parts[ref][n]
                spans.append({"original_source_ref":ref,"start_char":a,"end_char":b,
                              "original_text_sha256":sha(frag.encode("utf-8"))})
                fragments.append(frag.strip())
            base=originals[turn["source_fragments"][0][0]]
            out=dict(base)
            for name in tuple(out):
                if name.startswith("source_acoustic_") or name.startswith("quarantined_acoustic_"):
                    del out[name]
            out.update({
                "reading_block_id":f"S09E19:source-turn-amendment:{op['id']}:{i:02d}",
                "source_reading_ref":f"S09-{op['id']}-T{i:02d}",
                "original_source_part_refs":list(dict.fromkeys(x["original_source_ref"] for x in spans)),
                "candidate_role":turn["role"],
                "role_attribution_status":STATUS if turn["role"] is not None else "unidentified",
                "caption_text":" ".join(fragments),
                "source_exact_character_spans":spans,
                "source_prior_speaking_block_ids":[originals[ref]["reading_block_id"] for ref in refs],
                "source_actor_and_turn_contextual_hypothesis_only":True,
                "original_soundtrack_actor_identity_independently_verified":False,
                "actor_face_or_voice_independently_verified":False,
                "speaker_turn_boundary_verified":False,
                "source_original_times_ms":None,
                "original_source_untimed":True
            })
            result.append(out)
        for ref in refs:
            recovered=[]
            for r in result:
                for span in r["source_exact_character_spans"]:
                    if span["original_source_ref"]==ref:
                        a,b=span["start_char"],span["end_char"]
                        piece=originals[ref]["caption_text"][a:b]
                        if sha(piece.encode("utf-8"))!=span["original_text_sha256"]:
                            raise ValueError("Source exact substring digest changed")
                        recovered.append((a,b,piece))
            recovered.sort()
            if (not recovered or recovered[0][0]!=0
                or recovered[-1][1]!=len(originals[ref]["caption_text"])
                or any(a[1]!=b[0] for a,b in zip(recovered,recovered[1:]))
                or "".join(x[2] for x in recovered)!=originals[ref]["caption_text"]):
                raise ValueError("One original source character was lost or duplicated")
        working[positions[0]:positions[-1]+1]=result
    names=defaultdict(set)
    for r in working:
        for ref in r["original_source_part_refs"]:
            names[(r["episode_id"],ref)].add(r["candidate_role"])
    if set(names)!=old_refs:
        raise ValueError("Original cue refs did not survive speaking-turn reconstruction")
    # A cue with even one unassigned fragment remains UNKNOWN, rather than
    # inflating named coverage simply because another speaker had a name.
    named=sum(None not in roles for roles in names.values())
    new_source_named=sum(1 for key,roles in names.items()
                         if old_voices[key]=={None} and None not in roles)
    if named!=old_named+new_source_named:
        raise ValueError("Original named source parts wrongly counted")
    report={
        "schema":SCHEMA,
        "original_caption_source_units":len(names),
        "named_original_source_units":named,
        "unknown_original_source_units":len(names)-named,
        "original_previous_reader_turn_blocks":len(rows),
        "new_provisional_reader_turn_blocks":len(working),
        "source_episode_originally_untimed":True,
        "original_source_exact_text_preserved":True,
        "newly_named_original_source_units":new_source_named,
        "source_new_performer_identifications_AV_certified":0,
        "source_new_turn_boundaries_AV_verified":0,
        "source_p0_amendment_count":len(ops),
        "source_turn_amendment_ids":[op["id"] for op in ops]
    }
    return working,report


def build(root:Path,source_roles:Path,ledger_path:Path,out:Path)->dict:
    if out.resolve().is_relative_to(root.resolve()):
        raise ValueError("Original Night Court source dialogue must remain private")
    old=(source_roles/OLD_ROWS).read_bytes()
    meta=json.loads((source_roles/OLD_MANIFEST).read_text("utf-8"))
    if (sha(old)!=meta.get("source_patch_roles_sha256")
        or meta.get("original_held_source_caption_units")!=751
        or meta.get("provisionally_named_source_units")!=619
        or meta.get("unknown_original_source_units")!=132
        or meta.get("source_reading_blocks")!=718
        or meta.get("source_character_roles_independently_verified_via_AV")!=0):
        raise ValueError("Prior source-role amend ledger or receipt no longer verifiable")
    witness,cues=load_witness(root,"S09E19")
    if witness["sha256"]!=SOURCE_SHA or witness["timecoded"] is not False or len(cues)!=347:
        raise ValueError("Original episode 347 untimed paragraph witness no longer source-exact")
    instruction=ledger_path.read_bytes()
    ledger=json.loads(instruction)
    for op in validate_ledger(ledger):
        for ref in op["source_refs"]:
            original=cues[int(ref[1:4])-1]
            if original["start_ms"] is not None or original["end_ms"] is not None:
                raise ValueError("Original subtitle timestamps incorrectly invented")
            for phrase in op["split_before"][ref]:
                if phrase not in original["text"]:
                    raise ValueError("Patch lexical split anchor not present in held original caption")
    rows=[json.loads(x) for x in old.decode("utf-8").splitlines() if x.strip()]
    result,summary=apply(rows,ledger)
    out.mkdir(parents=True,exist_ok=True)
    raw="".join(json.dumps(x,sort_keys=True,ensure_ascii=False)+"\n" for x in result)
    (out/NEW_ROWS).write_text(raw,"utf-8")
    summary["source_turn_records_sha256"]=sha(raw.encode("utf-8"))
    summary["prior_source_role_records_sha256"]=sha(old)
    summary["source_turn_amendment_ledger_sha256"]=sha(instruction)
    summary["private_reader_sha256_by_episode"]={}
    for ep in ("S01E01","S09E19"):
        witness=load_witness(root,ep)[0]
        words=[f"# {ep}: source-preserving original Night Court speaker turn amendments","",
               "Character labels and performer turn boundaries remain EDITORIAL working",
               "hypotheses. Neither actor voice nor original moving-picture performance",
               "was independently verified by this source-text operation.",
               f"Original source caption SHA256: {witness['sha256']}",""]
        for r in result:
            if r["episode_id"]!=ep:continue
            words += [f"### {r['source_reading_ref']} ({', '.join(r['original_source_part_refs'])})",
                      (r["candidate_role"] or "UNIDENTIFIED SPEAKER")+" · "+r["role_attribution_status"],
                      r["caption_text"],""]
        text="\n".join(words).rstrip()+"\n"
        (out/f"{ep}-source-turn-amendments.md").write_text(text,"utf-8")
        summary["private_reader_sha256_by_episode"][ep]=sha(text.encode("utf-8"))
    (out/NEW_MANIFEST).write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n","utf-8")
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--source-role-patches",type=Path,required=True)
    p.add_argument("--ledger",type=Path,default=LEDGER)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    m=build(a.root,a.source_role_patches,a.ledger,a.output)
    print(f"{m['named_original_source_units']}/751 proposed named source cues, "
          f"{m['unknown_original_source_units']} UNKNOWN; {m['new_provisional_reader_turn_blocks']} "
          "provisional source reading turns; no new cast actor voices independently authenticated")


if __name__=="__main__":
    main()
