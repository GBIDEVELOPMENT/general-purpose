#!/usr/bin/env python3
"""Triangulate original SRT + independent text-constrained CTC + tiny.en words.

This compares *proposals*, not independent human-reviewed acoustic truth.
CTC input windows came from tiny.en, so two timestamps are not independent
source verification. Output is a review packet, NEVER subtitle corrections.
"""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
import re
from statistics import median

ROOT=Path(__file__).resolve().parents[1]/"seasons"/"S01"/"S01E01"/"derived"
V1=ROOT/"scene-review-v1"
V3=ROOT/"scene-review-v3"
MEDIA_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SRT_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
CUTOFF_MS=300

def norm(x):
    return re.sub("[^A-Z]","",x.upper())

def evaluate():
    orig=json.loads((V1/"word-alignment-review.json").read_text())
    ctc=json.loads((V3/"ctc-source-word-candidates.json").read_text())
    if not (orig["media_sha256"]==ctc["source_media_sha256"]==MEDIA_SHA
            and orig["caption_sha256"]==ctc["source_caption_sha256"]==SRT_SHA
            and orig["source_window_ms"]==ctc["source_window_ms"]==[60000,90000]
            and not orig["verified_word_alignment"]
            and not ctc["model_predictions_are_verified_word_alignment"]):
        raise ValueError("Cross-model source identity or epistemic mismatch")
    before=[(x["cue"], t["source_turn_index"], t)
           for x in orig["cue_turn_packets"] for t in x["source_turns"]]
    after=ctc["source_turns"]
    if len(before)!=len(after) or len(after)!=11:
        raise ValueError("Expected exactly 11 unchanged source turns")
    allwords=[]
    for (cue,turnno,tiny),candidate in zip(before,after):
        if (candidate["cue"],candidate["source_turn_index"],candidate["text"]) != (cue,turnno,tiny["text"]):
            raise ValueError("Original subtitle turn modified between methods")
        clean_words=[norm(w) for w in re.findall(r"[A-Za-z]+(?:['\u2019][A-Za-z]+)*",tiny["text"])]
        ctc_words=candidate.get("proposed_words",[])
        if ctc_words and [x["word"] for x in ctc_words]!=clean_words:
            raise ValueError("CTC original source token order differs from tiny.en source")
        tiny_map={}
        for x in tiny["exact_word_time_candidates"]:
            index=x["source_caption_word_index"]
            if index in tiny_map:raise ValueError("Duplicate source word anchor")
            if index>=len(clean_words) or norm(x["source_word"])!=clean_words[index]:
                raise ValueError("ASR lexical source token mismatched")
            tiny_map[index]=x
        for idx,word in enumerate(clean_words):
            x=tiny_map.get(idx)
            y=ctc_words[idx] if ctc_words else None
            ctc_interval=y.get("time_candidate_ms") if y and y["status"]=="candidate_unreviewed" else None
            asr_interval=x.get("proposed_audio_interval_ms") if x else None
            delta=ctc_interval[0]-asr_interval[0] if ctc_interval and asr_interval else None
            if delta is not None:
                tier=("two_model_start_proximity_300ms_or_less" if abs(delta)<=CUTOFF_MS
                      else "two_model_start_disagreement_over_300ms")
                # Near-agreement is not a speech transcript verified by humans.
            elif ctc_interval:tier="CTC_only_model_word_candidate"
            elif asr_interval:tier="tiny_en_only_word_candidate"
            else:tier="no_usable_word_timing_candidate"
            allwords.append({
              "source_cue":cue,"source_turn_index":turnno,"source_word_index":idx,
              "original_normalized_word":word,
              "tiny_en_start_end_ms":asr_interval,
              "ctc_start_end_ms":ctc_interval,
              "start_delta_ctc_minus_tiny_ms":delta,
              "source_review_priority":tier,
              "manual_audio_confirmation":False,
              "speaker_verified":False,
              "original_caption_text_modified":False})
    totals=Counter(x["source_review_priority"] for x in allwords)
    both=[x["start_delta_ctc_minus_tiny_ms"] for x in allwords if x["start_delta_ctc_minus_tiny_ms"] is not None]
    out={
      "schema":"night-court-s01e01-cross-model-word-triage/1",
      "episode_id":"S01E01","source_media_sha256":MEDIA_SHA,
      "source_caption_sha256":SRT_SHA,
      "source_window_ms":[60000,90000],
      "tiny_en_source":"scene-review-v1/word-alignment-review.json",
      "CTC_source":"scene-review-v3/ctc-source-word-candidates.json",
      "CTC_model_revision":ctc["model_revision_sha"],
      "shared_words_with_both_time_candidates":len(both),
      "within_300ms_start_proposals":totals["two_model_start_proximity_300ms_or_less"],
      "over_300ms_start_disagreements":totals["two_model_start_disagreement_over_300ms"],
      "median_CTC_minus_tiny_start_ms":median(both) if both else None,
      "counts":dict(sorted(totals.items())),
      "source_words":len(allwords),
      "shared_window_dependence":"CTC windows derived from tiny.en speech segments; proximity is not independent timestamp validation",
      "per_source_word_review":allwords,
      "audiovisual_word_timing_verified":False,
      "original_caption_edition_completeness_verified":False,
      "character_voices_verified":False,
      "interpretive_performance_tags_verified":False,
    }
    return out

def main():
    out=evaluate()
    js=V3/"word-timing-model-comparison.json"
    md=V3/"word-timing-model-comparison.md"
    if js.exists() or md.exists():raise ValueError("Refusing to overwrite model comparison edition")
    js.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n","utf-8")
    lines=[
      "# S01E01 01:00–01:30 | model word-time comparison",
      "",
      "**Research QA only.** Two model clocks agreeing does not prove the",
      "original source dialogue has been heard or identify any character.",
      "Wav2Vec2/CTC used approximate tiny.en speech segments as analysis windows.",
      "",
      f'Both models produced candidates for **{out["shared_words_with_both_time_candidates"]}** original source words.',
      f'**{out["within_300ms_start_proposals"]}** start times agree within 300ms; '
      f'**{out["over_300ms_start_disagreements"]}** differ by more than 300ms.',
      f'Median signed CTC minus tiny.en start delta: **{out["median_CTC_minus_tiny_start_ms"]} ms**.',
      "",
      "| Review category | Source word count |",
      "|---|---:|"]
    for k,v in out["counts"].items():lines.append(f"| {k.replace('_',' ')} | {v} |")
    lines+=["","## High-priority source-word checks","",
      "The entries below lack a two-model start-time candidate within 300ms.",
      "They require listening and/or an independent forced alignment; they",
      "must not be automatically overwritten in the original captions.",""]
    for w in out["per_source_word_review"]:
        if w["source_review_priority"]!="two_model_start_proximity_300ms_or_less":
            lines.append(f'- C{w["source_cue"]:04d} T{w["source_turn_index"]+1} word {w["source_word_index"]+1} '
                         f'(\u0060{w["original_normalized_word"]}\u0060): '
                         f'{w["source_review_priority"].replace("_"," ")}')
    lines+=["","## Acceptance limits","",
      "Most shared candidates land near one another because the original",
      "caption sequence is plausible and the models use related source-audio",
      "windows, **not** because timing was independently human verified.",
      "Never infer speaker identity, emotional tone, a confirmed word correction",
      "or transcript completeness from these statistics.",
      ""]
    md.write_text("\n".join(lines),"utf-8")
    print(f"Original-source triage: {out['source_words']} tokens, {len(out['per_source_word_review'])} reviewed for priority; {out['within_300ms_start_proposals']}/{len([x for x in out['per_source_word_review'] if x['start_delta_ctc_minus_tiny_ms'] is not None])} shared starts close")

if __name__=="__main__":main()
