#!/usr/bin/env python3
"""Lossless, original-caption-anchored P0 *possible* internal voice-switch QA.

Do not automatically change the 751 original caption-derived units or give a
character name because a transcript appears to switch voice mid-paragraph.
Every cue is SHA-checked and split exactly at one short unique phrase, with
both halves conserved privately for targeted original-soundtrack reviewing.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from build_pilot_fan_beat_cards import ROOT, load_witness

SCHEMA="night-court-unresolved-internal-speaker-turn-review/1"
OUTPUT="night-court-private-p0-internal-voice-switches/1"
LEDGER=ROOT/"research/probable-internal-speaker-switches-v1.json"
SOURCES={
 "S01E01":"aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496",
 "S09E19":"659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
}


def validate(root:Path, seeds:dict, strict=True) -> tuple[list[dict],dict]:
    if (seeds.get("schema")!=SCHEMA
        or seeds.get("no_source_cue_automatically_changed") is not True
        or seeds.get("no_character_assigned") is not True
        or seeds.get("independently_original_audio_reviewed") is not False):
        raise ValueError("Untrusted P0 unknown-speaker switch report")
    source={}
    for ep in SOURCES:
        meta,cues=load_witness(root,ep)
        if meta["sha256"]!=SOURCES[ep]:
            raise ValueError("Changed held pilot original caption witness")
        source[ep]=(meta,cues)
    seen=set()
    packets=[]
    for seed in seeds.get("cues",[]):
        ep=seed.get("episode_id")
        n=seed.get("original_cue")
        fragment=seed.get("split_before")
        if (ep not in source or type(n) is not int
            or (ep,n) in seen
            or not isinstance(fragment,str) or not 3<=len(fragment)<=40
            or not seed.get("reason")):
            raise ValueError("Invalid, duplicative or unreasoned P0 source cue")
        seen.add((ep,n))
        meta,cues=source[ep]
        if not 1<=n<=len(cues):
            raise ValueError("Review requested cue outside original source")
        text=cues[n-1]["text"]
        if text.count(fragment)!=1:
            raise ValueError("Original caption source has no unique split phrase")
        pos=text.index(fragment)
        if pos==0 or pos>=len(text):
            raise ValueError("Boundary cannot split this source cue")
        a,b=text[:pos],text[pos:]
        if not a.strip() or not b.strip() or a+b!=text:
            raise ValueError("Proposed voice switch loses source text")
        packets.append({
            "schema":OUTPUT,
            "episode_id":ep,
            "original_cue":n,
            "held_original_caption_sha256":meta["sha256"],
            "original_cue_text_sha256":hashlib.sha256(text.encode()).hexdigest(),
            "source_original_timings_ms":(
                {"start_ms":cues[n-1]["start_ms"],"end_ms":cues[n-1]["end_ms"]}
                if meta["timecoded"] else None),
            "candidate_split_at_unicode_character_offset":pos,
            "original_complete_source_cue_text":text,
            "first_candidate_voice_text":a,
            "second_candidate_voice_text":b,
            "editorial_review_reason":seed["reason"],
            "source_original_cue_text_preserved_exactly":True,
            "source_switch_verified_by_original_soundtrack":False,
            "first_speaker_character_name":None,
            "second_speaker_character_name":None,
            "two_voices_actually_present_independently_verified":False,
        })
    if strict and (len(packets)!=12 or
                   sum(x["episode_id"]=="S01E01" for x in packets)!=1 or
                   sum(x["episode_id"]=="S09E19" for x in packets)!=11):
        raise ValueError("Original source-review P0 candidate coverage changed")
    summary={
        "schema":OUTPUT,
        "provisional_inside_original_cue_switch_questions":len(packets),
        "first_episode_timed_candidate_count":sum(x["episode_id"]=="S01E01" for x in packets),
        "last_episode_original_untimed_candidate_count":sum(x["episode_id"]=="S09E19" for x in packets),
        "original_caption_speaking_unit_denominator_unchanged":751,
        "actually_verified_new_speaker_switches":0,
        "new_original_soundtrack_accepted_speaker_names":0,
    }
    return packets,summary


def export(root:Path,ledger:Path,output:Path):
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Source-bearing private voice review packets must stay outside repo")
    seeds=json.loads(ledger.read_text("utf-8"))
    packets,summary=validate(root,seeds)
    output.mkdir(parents=True,exist_ok=True)
    (output/"potential-within-caption-voice-switches.jsonl").write_text(
        "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in packets),"utf-8"
    )
    (output/"potential-within-caption-summary.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)+"\n","utf-8"
    )
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--ledger",type=Path,default=LEDGER)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    r=export(a.root,a.ledger,a.output)
    print(f"{r['provisional_inside_original_cue_switch_questions']} exact-source "
          "potential internal voice switches queued for P0 original audio listening; "
          "no source dialogue printed and no new names accepted")


if __name__=="__main__":
    main()
