#!/usr/bin/env python3
"""Prioritize remaining original Night Court P0/P1 unknowns with real source leads.

Consumes private v8 speaker evidence, original S01 SRT times, the separately
original-UNTIMED S09 audio↔text locator, and known mixed-voice cue alerts.
Outputs a SHA-bound private **review queue**, never invented role names.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import re
from pathlib import Path

from build_pilot_fan_beat_cards import ROOT,load_witness

SCHEMA="night-court-private-original-speaker-review-next/1"
VIDEO_S09_SHA="51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649"
S09_ORIGINAL_SHA="659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
S09_LOCATOR_SHA="febac6aff2cb01ee36ac1c44b592317011d655628ede2eb83981b98201e3accc"
BASE_RECORD="pilot-original-acoustic-speaker-reads.jsonl"
BASE_MANIFEST="pilot-original-acoustic-speaker-manifest.json"
V8_SHA_FIELD="source_role_record_sha256"

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def load_private_v8(path:Path)->list[dict]:
    raw=(path/BASE_RECORD).read_bytes()
    manifest=json.loads((path/BASE_MANIFEST).read_text("utf-8"))
    if (sha(raw)!=manifest.get(V8_SHA_FIELD)
        or manifest.get("original_source_caption_units")!=751
        or manifest.get("source_units_with_provisional_names")!=587
        or manifest.get("original_units_still_unknown")!=164
        or manifest.get("source_speaker_identities_human_verified_by_pass")!=0):
        raise ValueError("Private v8 role source index missing or no longer true")
    rows=[json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    if len(rows)!=716:
        raise ValueError("Private v8 source speaking blocks have drifted")
    for row in rows:
        if row.get("speaker_turn_boundary_verified") is not False:
            raise ValueError("Unverified original episode turns must remain marked provisional")
    return rows

def load_s09_locator(path:Path)->dict[int,dict]:
    raw=path.read_bytes()
    if sha(raw)!=S09_LOCATOR_SHA:
        raise ValueError("Wrong S09 original-source audio locator report bytes")
    obj=json.loads(raw)
    if (obj.get("original_video_sha256")!=VIDEO_S09_SHA
        or obj.get("original_untimed_source_sha256")!=S09_ORIGINAL_SHA
        or obj.get("source_paragraphs")!=347
        or obj.get("candidate_source_paragraphs_given_audio_window")!=231
        or obj.get("exact_subtitle_timecode_recovered")!=0
        or obj.get("original_speaker_identities_verified")!=0):
        raise ValueError("Private S09 audio/source alignment never verified as input")
    lookup={}
    for item in obj.get("matches",[]):
        n=item.get("original_paragraph_id")
        a=item.get("candidate_original_audio_window_ms")
        if (type(n)!=int or n in lookup or not 1<=n<=347
            or not isinstance(a,list) or len(a)!=2
            or any(type(x)!=int for x in a) or not 0<=a[0]<a[1]<=1_800_000
            or item.get("original_paragraph_timecode_ms") is not None
            or item.get("original_film_audio_timing_independently_verified") is not False):
            raise ValueError("Untrusted S09 original audio time suggestion")
        lookup[n]=item
    if len(lookup)!=231:
        raise ValueError("Incomplete previously witnessed 231 audio locations")
    return lookup

def cue_parts(rows:list[dict])->dict[str,set[str]]:
    parts={}
    for row in rows:
        ep=row["episode_id"]
        for source in row["original_source_part_refs"]:
            key=ep+":"+source
            parts.setdefault(key,set()).add(row.get("candidate_role"))
    return parts

def make_queue(rows:list[dict],s09_times:dict[int,dict],
               internal:dict,strict:bool=True)->tuple[list[dict],dict]:
    roles=cue_parts(rows)
    unknown={k for k,names in roles.items() if None in names}
    marked={(r["episode_id"],r["original_cue"]) for r in internal["cues"]}
    review=[]
    for pos,row in enumerate(rows):
        if row["candidate_role"] is not None:
            continue
        ep=row["episode_id"]
        parts=row["original_source_part_refs"]
        unresolved=[ref for ref in parts if ep+":"+ref in unknown]
        if not unresolved:
            raise ValueError("Unidentified reader no longer has an unresolved source unit")
        if any(x["episode_id"]!=ep for x in rows[pos:pos+1]):
            raise ValueError("Episode partition drift")
        original_cue_ids=sorted({int(ref[1:4]) for ref in parts})
        flagged=any((ep,n) in marked for n in original_cue_ids)
        ref=row["source_reading_ref"]
        text=row["caption_text"]
        nwords=len(re.findall(r"\b[\w']+\b",text))
        window=None
        anchor=None
        if ep=="S01E01":
            times=row.get("source_original_times_ms")
            if isinstance(times,list) and times:
                start=min(x["start_ms"] for x in times)
                end=max(x["end_ms"] for x in times)
                if not 0<=start<end:
                    raise ValueError("Invalid original S01 timed caption")
                window=[max(0,start-1200),end+1200]
                anchor="held_s01_srt_approximate_not_verified_av_sync"
        elif ep=="S09E19":
            if row.get("source_original_times_ms") is not None or not row.get("original_source_untimed"):
                raise ValueError("Original S09 must remain untimed")
            matched=[s09_times.get(n) for n in original_cue_ids]
            if all(x is not None for x in matched):
                window=[min(x["candidate_original_audio_window_ms"][0] for x in matched),
                        max(x["candidate_original_audio_window_ms"][1] for x in matched)]
                anchor="unverified_original_audio_ASR_sequence_locator_not_caption_time"
        else:
            raise ValueError("Review includes unwanted original-series episode")
        risk=["speaker_unknown"]
        score=25
        if window is not None:
            score+=20
            risk.append("actual_original_source_audio_location_candidate")
        if flagged:
            score+=30
            risk.append("possible_internal_speaker_switch_p0_review_first")
        if len(parts)>1:
            score+=8
            risk.append("joined_source_paragraph_parts_check_p0")
        if nwords<=5:
            score+=7
            risk.append("short_or_one_word_voice_evidence_difficult")
        if text.startswith(("...","- ","— ")):
            score+=4
            risk.append("possible_continuation_or_intra_caption_split")
        neighbors=[]
        for ix in (pos-1,pos+1):
            if 0<=ix<len(rows) and rows[ix]["episode_id"]==ep:
                neighbors.append({
                    "source_reading_ref":rows[ix]["source_reading_ref"],
                    "provisional_role_not_speaker_proof":rows[ix]["candidate_role"],
                    "dialogue_for_private_context":rows[ix]["caption_text"]
                })
        review.append({
            "schema":SCHEMA,"episode_id":ep,
            "source_reading_ref":ref,
            "original_source_part_refs":parts,
            "original_caption_sha256":row["original_source_sha256"],
            "unidentified_original_unit_refs":unresolved,
            "original_dialogue_for_private_review":text,
            "adjacent_dialogue_editorial_context_only":neighbors,
            "rank":score,
            "reasons":risk,
            "actual_original_sound_candidate_window_ms":window,
            "window_provenance_not_accepted_source_timestamp":anchor,
            "all_original_S09_caption_times_remain_null":ep=="S09E19",
            "model_proposed_character":None,
            "actual_original_voice_actor_name_verified":False,
        })
    review.sort(key=lambda r:(-r["rank"],r["episode_id"],r["source_reading_ref"]))
    unresolved_units={r["episode_id"]+":"+ref for r in review for ref in r["unidentified_original_unit_refs"]}
    outcome={
        "schema":SCHEMA,
        "original_source_units":len(roles),
        "original_units_provisionally_named":len(roles)-len(unknown),
        "original_source_units_still_unknown":len(unknown),
        "unknown_source_unit_review_records":len(review),
        "actual_audio_window_leads":sum(r["actual_original_sound_candidate_window_ms"] is not None for r in review),
        "s09_actual_audio_window_leads":sum(r["episode_id"]=="S09E19" and r["actual_original_sound_candidate_window_ms"] is not None for r in review),
        "suspected_internal_switch_review_records":sum("possible_internal_speaker_switch_p0_review_first" in r["reasons"] for r in review),
        "new_speaker_names_automatically_assigned":0,
        "new_voices_human_accepted":0,
        "original_untimed_S09_captions_modified":False
    }
    if unknown!=unresolved_units:
        raise ValueError("Not every unresolved original unit is covered by review queue")
    if strict and (len(roles),len(unknown),outcome["original_units_provisionally_named"])!=(751,164,587):
        raise ValueError("Latest actual original source ledger changed")
    return review,outcome

def build(root:Path,role_root:Path,locator:Path,output:Path)->dict:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private source dialogue output must never enter repo")
    rows=load_private_v8(role_root)
    audio=load_s09_locator(locator)
    internal=json.loads((root/"research/probable-internal-speaker-switches-v1.json").read_text("utf-8"))
    for ep in ("S01E01","S09E19"):
        meta,_=load_witness(root,ep)
        for row in rows:
            if row["episode_id"]==ep and row["original_source_sha256"]!=meta["sha256"]:
                raise ValueError("Original source caption SHA mismatch in private v8 reader")
    selected,manifest=make_queue(rows,audio,internal)
    output.mkdir(parents=True,exist_ok=True)
    (output/"remaining-164-speaker-review.jsonl").write_text(
        "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in selected),"utf-8")
    (output/"remaining-164-speaker-review-summary.json").write_text(
        json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+"\n","utf-8")
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--speaker-v8-root",type=Path,required=True)
    p.add_argument("--s09-original-audio-locator",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=build(a.root,a.speaker_v8_root,a.s09_original_audio_locator,a.output)
    print(f"{result['original_source_units_still_unknown']} unresolved original-source "
          f"units organized for P0/P1 review; "
          f"{result['s09_actual_audio_window_leads']} S09 audio-search leads; "
          "no character guesses or source transcript text in logs")

if __name__=="__main__":
    main()
