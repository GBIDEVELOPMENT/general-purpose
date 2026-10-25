#!/usr/bin/env python3
"""Current source-UNIT speaker coverage, never collapsed reading-block coverage.

S09's 347 ORIGINAL untimed paragraphs are combined into 311 rendered
reading blocks. Miscounting these as equivalent falsely changed project
completion percentages. Expand every provenance-linked source ref and
validate exact original subtitle word SHA per speaking unit.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from build_caption_first_working_drafts import ROOT,SOURCE_SHA,witness
from render_extra_observed_original_stage_v5 import render as stage_v5
from build_s01_quote_correction_v4 import render as s01_v4
from build_s09_impostor_speaking_reader_v4 import render as s09_v4

OUTPUT="catalog/current-night-court-original-speaking-unit-coverage.json"
EXPECTED={"S01E01":(336,404,306,98,404),"S09E19":(347,347,181,166,311)}
RANGE=re.compile(r"C(?P<first>\d{3})\.(?P<part>\d+)(?:–C(?P<last>\d{3})\.(?P<lastpart>\d+))?")


def expand(ref):
    m=RANGE.fullmatch(ref)
    if not m:raise ValueError("Broken source speaking unit ref: "+ref)
    a=int(m["first"]);part=int(m["part"]);b=m["last"];last=m["lastpart"]
    if b is None:return [(a,part)]
    if part!=1 or last!="1" or int(b)<a:
        raise ValueError("Ambiguous/inverted source multi-caption reading wrap")
    return [(i,1) for i in range(a,int(b)+1)]


def per_episode(ep,root=ROOT):
    _,source_meta,cues,units,_=witness(ep,root)
    _staged,current=stage_v5(ep,root)
    base,report=s01_v4(root) if ep=="S01E01" else s09_v4(root)
    index=(report["reversible_dialogue_source_index"] if ep=="S01E01"
           else report["source_reading_index"])
    if current["original_reading_blocks"]!=len(index):
        raise ValueError("Original staged script and reading block index disagree")
    expected_ids=[(u["cue"],u["part"]) for u in units]
    expected_hashes=[hashlib.sha256(u["source_text"].strip().encode("utf-8")).hexdigest()
                     for u in units]
    original_hashes=(report["source_original_unit_word_hashes"] if ep=="S01E01"
                     else report["held_original_source_unit_word_hashes"])
    if original_hashes!=expected_hashes:
        raise ValueError("Current character text differs from original source witness")
    flattened=[]
    unknown=[]
    reading_unknown=0
    last_speaker=None
    next_by_idx={}
    for n,entry in enumerate(index):
        refs=expand(entry["source_ref"])
        flattened.extend(refs)
        unidentified=entry["speaker"].startswith("UNIDENTIFIED")
        if unidentified:
            reading_unknown+=1
            previous=index[n-1]["speaker"] if n>0 else None
            next_speaker=index[n+1]["speaker"] if n+1<len(index) else None
            for cue,part in refs:
                unit=next((x for x in units if x["cue"]==cue and x["part"]==part),None)
                if unit is None:raise ValueError("Missing unknown original-speaking source unit")
                unknown.append({
                 "original_speaking_ref":f"C{cue:03d}.{part}",
                 "reading_block_ref":entry["source_ref"],
                 "original_caption_start_ms":unit["start_ms"],
                 "original_caption_end_ms":unit["end_ms"],
                 "source_unit_dialogue_sha256":hashlib.sha256(unit["source_text"].strip().encode()).hexdigest(),
                 "adjacent_previous_reading_speaker":previous,
                 "adjacent_next_reading_speaker":next_speaker,
                 "original_soundtrack_listened_to_resolve":False
                })
    if flattened!=expected_ids:
        raise ValueError("Original speaking cue/part dropped, duplicated or reordered")
    named=len(units)-len(unknown)
    result={
       "episode_id":ep,
       "original_caption_sha256":SOURCE_SHA[ep],
       "original_source_caption_cues_or_paragraphs":len(cues),
       "original_speaking_units":len(units),
       "original_subtitle_source_has_authentic_timecodes":source_meta["timecoded"],
       "current_reading_blocks":len(index),
       "current_reading_blocks_provisionally_named":len(index)-reading_unknown,
       "current_reading_blocks_unidentified":reading_unknown,
       "original_speaking_units_provisionally_named":named,
       "original_speaking_units_unidentified":len(unknown),
       "source_unit_attribution_fraction_percent":round(named*100/len(units),1),
       "original_speaking_units_soundtrack_identity_verified":0,
       "all_original_caption_words_and_order_preserved":True,
       "unknown_original_speaking_unit_review_queue":unknown
    }
    if (len(cues),len(units),named,len(unknown),len(index))!=EXPECTED[ep]:
        raise ValueError("Unexpected new coverage: audit source truth before revising metrics")
    if (named!=current["source_speaking_units_attributed_provisionally"] or
        len(unknown)!=current["source_speaking_units_unidentified"]):
        raise ValueError("Current screenplay staged manifest speaker count drift")
    return result


def build(root=ROOT):
    entries=[per_episode(x,root) for x in EXPECTED]
    total=sum(x["original_speaking_units"] for x in entries)
    named=sum(x["original_speaking_units_provisionally_named"] for x in entries)
    unknown=sum(x["original_speaking_units_unidentified"] for x in entries)
    if (total,named,unknown)!=(751,487,264):
        raise ValueError("Project original speaking units no longer reconcile")
    report={
      "schema":"night-court-authoritative-immutable-original-speaking-unit-attribution/1",
      "series":"Night Court (1984–1992)",
      "episode_count_with_complete_held_dialogue_manuscripts":2,
      "original_held_source_episodes_scaffolded":193,
      "source_speaking_units_total":total,
      "original_speaking_units_provisionally_attributed":named,
      "original_speaking_units_unidentified":unknown,
      "original_source_unit_attribution_percentage":round(100*named/total,1),
      "all_original_audio_identifications_independently_verified":False,
      "full_original_episode_editor_ready":0,
      "original_entire_av_episodes_certified":0,
      "measurement_unit":"original source cue.part, NOT grouped rendered reading blocks",
      "timecode_provenance":"S01 SRT authentic, S09 347 original paragraphs UNTIMED",
      "cautions":["All named roles editorial and provisional, no original soundtrack independently listened to accept them.",
                  "S09 36 layout continuation joins collapse original paragraphs into 311 reading blocks. Reading-block named fractions must not be used as original speech-unit coverage.",
                  "Source video image contact sheets cannot prove any actor/voice identity."],
      "pilots":entries}
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-root",type=Path,default=ROOT)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    report=build()
    text=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    target=a.output_root/OUTPUT
    if a.check:
        if target.read_text("utf-8")!=text:raise ValueError("Stale real source speaking-unit counts")
    else:
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(text,encoding="utf-8")
    print("Night Court source-unit exact pilot speaker tally:",
          report["original_speaking_units_provisionally_attributed"],"/",
          report["source_speaking_units_total"],"provisional;",
          report["original_speaking_units_unidentified"],"unknown; no AV acceptance.")


if __name__=="__main__":
    main()
