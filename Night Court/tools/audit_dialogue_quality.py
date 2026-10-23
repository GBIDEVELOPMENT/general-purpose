#!/usr/bin/env python3
"""Evidence-oriented QC on Night Court dialogue witnesses, without claiming completeness.

Only local version manifests and normalized cues are read. No video access, no
third-party transcripts, no automatic canonical replacement. All warning
thresholds are heuristics, designed to triage human audiovisual review.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
from statistics import median
import csv
import hashlib
import io
import json
import re

ROOT=Path(__file__).resolve().parents[1]
LONG_GAP_MS=30000
SHORT_TRACK_END_MS=12*60*1000
LOW_WORD_COUNT=150

def write(path,value):
    value=(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+"\n") if not isinstance(value,str) else value
    if not path.exists() or path.read_text("utf-8")!=value:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(value,"utf-8")

def words(text):
    return re.findall(r"(?u)\b[\w']+\b",text)

def quality(meta,cues):
    if not cues:raise ValueError("Cannot assess empty dialogue witness")
    durations=[]
    overlap=0
    gaps=[]
    backwards=0
    last_start=None
    last_end=None
    caption_intervals=[]
    repeated=0
    prev_text=None
    for c in cues:
        text=" ".join(c["text"].casefold().split())
        if text==prev_text:repeated+=1
        prev_text=text
        if meta["timecoded"]:
            a,b=c["start_ms"],c["end_ms"]
            if a is None or b is None or a<0 or b<a:
                raise ValueError("Malformed cue timing in "+meta["version_id"])
            caption_intervals.append((a,b))
            durations.append(b-a)
            if last_start is not None and a<last_start:
                backwards+=1
            if last_end is not None:
                if a<last_end:overlap+=1
                elif a>last_end:gaps.append(a-last_end)
            last_start=a
            last_end=b if last_end is None else max(last_end,b)
    tokens=sum(len(words(c["text"])) for c in cues)
    text_length=sum(len(c["text"]) for c in cues)
    unique_texts=len({re.sub(r"\s+"," ",c["text"].strip()).casefold() for c in cues})
    first_start=min((a for a,b in caption_intervals),default=None)
    final_end=max((b for a,b in caption_intervals),default=None)
    # True union of caption intervals, not a claim of uninterrupted spoken dialogue.
    merged=[]
    for a,b in sorted(caption_intervals):
        if not merged or a>merged[-1][1]:
            merged.append([a,b])
        else:
            merged[-1][1]=max(merged[-1][1],b)
    caption_time_ms=sum(b-a for a,b in merged)
    flags=[]
    if meta["timecoded"]:
        if final_end is not None and final_end<SHORT_TRACK_END_MS:flags.append("suspiciously_short_caption_timeline")
        if backwards:flags.append("out_of_order_source_cues")
        if overlap:flags.append("overlapping_source_cues_review")
        if len([g for g in gaps if g>=LONG_GAP_MS])>=3:flags.append("several_long_caption_gaps_review")
    else:
        flags.append("untimed_source_requires_separate_completeness_check")
    if tokens<LOW_WORD_COUNT:flags.append("very_low_word_count_for_full_episode")
    if repeated>=3:flags.append("repeated_adjacent_captions_review")
    report={
      "episode_id":meta["episode_id"],"version_id":meta["version_id"],
      "source_sha256":meta["sha256"],"edition":meta["edition"],
      "format":meta["format"],"timecoded":meta["timecoded"],
      "source_declared_complete":bool(meta["declared_complete"]),
      "epistemic_status":"heuristic_automated_source_QA_not_audiovisual_completeness",
      "cue_count":len(cues),"word_count_rough":tokens,"text_characters":text_length,
      "unique_caption_texts":unique_texts,"adjacent_exact_repetitions":repeated,
      "earliest_cue_start_ms":first_start,"latest_cue_end_ms":final_end,
      "source_cue_out_of_order_count":backwards,"overlapping_cue_count":overlap,
      "median_cue_duration_ms":median(durations) if durations else None,
      "max_gap_between_source_cues_ms":max(gaps,default=None),
      "source_gaps_over_30_seconds":sum(g>=LONG_GAP_MS for g in gaps),
      "source_cue_union_duration_ms":caption_time_ms if meta["timecoded"] else None,
      "source_cue_union_fraction_of_final_time":round(caption_time_ms/final_end,4)
          if final_end and meta["timecoded"] else None,
      "flags":flags,
      "limits":[
        "An SRT's final timestamp does not prove every line was captured.",
        "Music, quiet scenes, titles, ads and cuts can legitimately create long caption gaps.",
        "Overlapping cues are often legitimate two-speaker or sound-effect captions.",
        "No source video was viewed; independently verified completeness remains unknown.",
        "Word counts are an English-oriented rough metric; this is not a semantic evaluation."
      ]}
    return report

def main():
    index=ROOT/"catalog"/"dialogue-index.jsonl"
    records=[json.loads(s) for s in index.read_text("utf-8").splitlines() if s.strip()] if index.exists() else []
    findings=[]
    for record in records:
        meta_path=ROOT/record["manifest"]
        meta=json.loads(meta_path.read_text("utf-8"))
        if record["sha256"]!=meta["sha256"]:raise ValueError("Index hash mismatch")
        episode_dir=ROOT/"seasons"/record["episode_id"][:3]/record["episode_id"]
        original=episode_dir/meta["original_path"]
        if hashlib.sha256(original.read_bytes()).hexdigest()!=meta["sha256"]:
            raise ValueError("Source changed since import: "+str(original))
        cues=[json.loads(s) for s in (episode_dir/meta["segments_path"]).read_text("utf-8").splitlines() if s.strip()]
        evaluation=quality(meta,cues)
        write(meta_path.parent/"quality.json",evaluation)
        findings.append(evaluation)
    overall={
      "series":"night-court-1984","source_witnesses":len(findings),
      "episodes_with_witnesses":len({x["episode_id"] for x in findings}),
      "witnesses_with_flags":sum(bool(x["flags"]) for x in findings),
      "flag_counts":dict(sorted(Counter(f for x in findings for f in x["flags"]).items())),
      "independently_verified_complete_episodes":0,
      "witness_quality":findings,
      "warning":"Heuristic triage. Unflagged tracks are not certified complete; flagged tracks may still be complete."
    }
    write(ROOT/"catalog"/"dialogue-quality.json",overall)
    csv_rows=[{"episode_id":r["episode_id"],"version_id":r["version_id"],"format":r["format"],
               "cue_count":r["cue_count"],"word_count_rough":r["word_count_rough"],
               "latest_cue_end_ms":r["latest_cue_end_ms"],
               "overlapping_cue_count":r["overlapping_cue_count"],
               "gaps_over_30s":r["source_gaps_over_30_seconds"],
               "flags":";".join(r["flags"])} for r in findings]
    columns=["episode_id","version_id","format","cue_count","word_count_rough","latest_cue_end_ms","overlapping_cue_count","gaps_over_30s","flags"]
    buffer=io.StringIO()
    writer=csv.DictWriter(buffer,fieldnames=columns)
    writer.writeheader();writer.writerows(csv_rows)
    write(ROOT/"catalog"/"dialogue-quality.csv",buffer.getvalue())
    print("Dialogue QA:",len(findings),"witnesses;",overall["witnesses_with_flags"],"flagged for review;",
          "0 audiovisual completeness attestations")

if __name__=="__main__":main()
