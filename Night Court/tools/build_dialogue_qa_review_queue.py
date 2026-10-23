#!/usr/bin/env python3
"""Deterministic 193-episode subtitle QA triage, not a media verification tool."""
from pathlib import Path
from collections import Counter
import csv, io, json

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = {
    "untimed_source_requires_separate_completeness_check": 100,
    "several_long_caption_gaps_review": 40,
    "repeated_adjacent_captions_review": 25,
    "overlapping_source_cues_review": 20,
}
def main():
    c=json.loads((ROOT/"catalog/dialogue-coverage.json").read_text("utf-8"))
    q=json.loads((ROOT/"catalog/dialogue-quality.json").read_text("utf-8"))
    byid={x["episode_id"]:x for x in q["witness_quality"]}
    if len(byid)!=193 or len(c["rows"])!=193 or set(byid)!={x["id"] for x in c["rows"]}:
        raise ValueError("Triage cannot silently omit any original-series episode")
    items=[]
    for episode in c["rows"]:
        ep=episode["id"];audit=byid[ep]
        flags=audit.get("flags",[])
        unknown=set(flags)-set(WEIGHTS)
        if unknown:raise ValueError("New QA flag requires explicit triage: "+str(unknown))
        score=1+sum(WEIGHTS[f] for f in flags)
        if audit.get("source_gaps_over_30_seconds",0)>=5:score+=10
        if audit.get("overlapping_cue_count",0)>=100 and "overlapping_source_cues_review" in flags:score+=10
        actions=[]
        if "untimed_source_requires_separate_completeness_check" in flags:
            actions.append("source_audio_alignment_needed_for_timecodes")
        if "several_long_caption_gaps_review" in flags:
            actions.append("inspect_silent_spans_and_possible_missing_captions")
        if "repeated_adjacent_captions_review" in flags:
            actions.append("listen_for_duplicate_or_repeated_spoken_lines")
        if "overlapping_source_cues_review" in flags:
            actions.append("compare_simultaneous_spoken_dialogue_and_cue_overlay")
        if not actions:actions.append("sample_video_edition_alignment_and_full_runtime")
        items.append({
            "episode_id":ep,"season":episode["season"],"title":episode["title"],
            "score_for_triage_only":score, "flags":flags,
            "format":audit["format"],"source_sha256":audit["source_sha256"],
            "cue_count":audit["cue_count"],"words_rough":audit["word_count_rough"],
            "overlapping_cues":audit["overlapping_cue_count"],
            "gaps_over_30_seconds":audit["source_gaps_over_30_seconds"],
            "largest_cue_gap_ms":audit["max_gap_between_source_cues_ms"],
            "last_source_cue_end_ms":audit["latest_cue_end_ms"],
            "suggested_manual_checks":actions,
            "review_status":"needs_edition_aligned_av_review",
            "audiovisual_completeness_verified":False
        })
    items.sort(key=lambda x:(-x["score_for_triage_only"],x["episode_id"]))
    out={
        "series":"night-court-1984","episodes":len(items),
        "source_witnesses":q["source_witnesses"],
        "witnesses_with_flags":q["witnesses_with_flags"],
        "source_quality_flags":q["flag_counts"],
        "no_source_video_was_reviewed":True,
        "priority_limit":"Heuristic ordering for human review efficiency, NOT source error probability or completeness assessment.",
        "all_episodes_require_av_verification":True,
        "items":items
    }
    path=ROOT/"catalog/dialogue-qa-review-queue.json"
    txt=json.dumps(out,indent=2,ensure_ascii=False)+"\n"
    if not path.exists() or path.read_text("utf-8")!=txt:path.write_text(txt,encoding="utf-8")
    buf=io.StringIO()
    columns=["episode_id","season","title","score_for_triage_only","format",
             "cue_count","words_rough","overlapping_cues","gaps_over_30_seconds",
             "largest_cue_gap_ms","last_source_cue_end_ms","flags","suggested_manual_checks",
             "review_status","source_sha256"]
    writer=csv.DictWriter(buf,fieldnames=columns)
    writer.writeheader()
    for item in items:
        row={key:item[key] for key in columns}
        for key in ("flags","suggested_manual_checks"):row[key]=";".join(row[key])
        writer.writerow(row)
    outcsv=ROOT/"catalog/dialogue-qa-review-queue.csv"
    if not outcsv.exists() or outcsv.read_text("utf-8")!=buf.getvalue():
        outcsv.write_text(buf.getvalue(),encoding="utf-8")
    print(f"QA TRIAGE: {len(items)} episodes; {q['witnesses_with_flags']} flagged source witnesses; all remain AV-unverified")
if __name__=="__main__":
    main()
