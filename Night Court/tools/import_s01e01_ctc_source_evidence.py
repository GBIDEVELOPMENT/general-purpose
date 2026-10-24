#!/usr/bin/env python3
"""Ingest only compact SHA-checked forced-alignment hypotheses from trusted CI.

Candidates are not certified times. Original SRT and all visual claims untouched.
"""
from __future__ import annotations
import argparse,json, re, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCENE=ROOT/"seasons"/"S01"/"S01E01"/"derived"
DEST=SCENE/"scene-review-v3"
SRT_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
MEDIA_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"

def validate(candidate_file):
    if not candidate_file.is_file() or candidate_file.stat().st_size>180_000:
        raise ValueError("No bounded CTC JSON artifact")
    j=json.loads(candidate_file.read_text("utf-8"))
    if (j.get("schema")!="night-court-ctc-source-constrained-words/1" or
        j.get("episode_id")!="S01E01" or j.get("source_media_sha256")!=MEDIA_SHA or
        j.get("source_caption_sha256")!=SRT_SHA or
        j.get("source_window_ms")!=[60000,90000] or
        j.get("ctc_model")!="facebook/wav2vec2-base-960h" or
        not re.fullmatch(r"[0-9a-f]{40,64}",str(j.get("model_revision_sha"))) or
        j.get("raw_episode_media_or_audio_in_artifact") is not False or
        j.get("model_audio_window_complete") is not False or
        j.get("model_predictions_are_verified_word_alignment") is not False or
        j.get("source_caption_offset_and_drift_verified") is not False or
        j.get("actor_identity_verified") is not False or
        j.get("acting_emotion_verified") is not False or
        j.get("finished_screenplay_verified") is not False):
        raise ValueError("Source, licensing or no-overclaim gate violated")
    existing=json.loads((SCENE/"scene-review-v1"/"word-alignment-review.json").read_text("utf-8"))
    ref=[(cue["cue"],t["source_turn_index"],t["text"])
         for cue in existing["cue_turn_packets"] for t in cue["source_turns"]]
    turns=j.get("source_turns")
    if not isinstance(turns,list) or len(turns)!=11 or len(set((x["cue"],x["source_turn_index"]) for x in turns))!=11:
        raise ValueError("Missing/extra/duplicate original caption turns")
    if [(x["cue"],x["source_turn_index"],x["text"]) for x in turns]!=ref:
        raise ValueError("CTC source word text diverges from immutable SRT review")
    candidates=0; abstentions=0
    for x in turns:
        status=x["status"]
        if status.startswith("candidate_"):
            if x.get("asr_segment_index") is None or not isinstance(x.get("proposed_words"),list):
                raise ValueError("Candidate lacks ASR or word provenance")
            if not len(x["proposed_words"]):
                raise ValueError("Candidate lacks any aligned word")
            if not 60000<=x["ctc_processing_window_ms"][0]<x["ctc_processing_window_ms"][1]<=90000:
                raise ValueError("CTC processed an unapproved audio interval")
            previous=0
            for token in x["proposed_words"]:
                if token["status"]=="candidate_unreviewed":
                    t=token.get("time_candidate_ms")
                    if t is None or not x["ctc_processing_window_ms"][0]<=t[0]<t[1]<=x["ctc_processing_window_ms"][1]:
                        raise ValueError("Source token time outside approved audio")
                    if t[0]<previous:raise ValueError("Non-monotonic source token sequence")
                    previous=t[0];candidates+=1
                elif not token["status"].startswith("abstain_"):
                    raise ValueError("Unrecognized forced-alignment confidence state")
                else:abstentions+=1
        elif status.startswith("abstain_"):
            if x.get("proposed_words"):raise ValueError("Abstained source was assigned words")
        else:raise ValueError("Unrecognized alignment source status")
    if not candidates:
        raise ValueError("No usable CTC candidates: do not promote an empty result")
    return j,candidates,abstentions

def write(source):
    if (DEST/"ctc-source-word-candidates.json").exists():
        raise ValueError("Would overwrite existing acoustic edition")
    j,candidates,abstentions=validate(source)
    shutil.copyfile(source,DEST/"ctc-source-word-candidates.json")
    lines=["# S01E01 independent CTC original-text word timing candidates",
           "",
           "**No CTC output is a certified dialogue timestamp or speaker label.**",
           f"Source AVI SHA-256: \u0060{MEDIA_SHA}\u0060",
           f"Original SRT SHA-256: \u0060{SRT_SHA}\u0060",
           f"Acoustic model: \u0060{j['ctc_model']}\u0060, revision \u0060{j['model_revision_sha']}\u0060",
           f"CTC word candidates: {candidates}; word-level abstentions: {abstentions}.",
           "",
           "| Original caption turn | Acoustic support | Candidate words | Abstentions |",
           "|---|---|---:|---:|"]
    for turn in j["source_turns"]:
        wc=sum(x["status"]=="candidate_unreviewed" for x in turn.get("proposed_words",[]))
        ab=sum(x["status"]!="candidate_unreviewed" for x in turn.get("proposed_words",[]))
        lines.append(f'| C{turn["cue"]:04d} turn {turn["source_turn_index"]+1} | {turn["status"]} | {wc} | {ab} |')
    lines.extend(["","The CTC model is *forced* to find a monotonic path matching source text.",
       "A path with plausible time ranges does not mean every word was spoken,",
       "especially unusual vocabulary, laughter-covered sections or an incomplete cut.",
       "This evidence must be independently auditioned and compared with the original",
       "caption timing and tiny.en hypotheses before any production-script promotion.",
       "No characters, speaker voiceprints or emotional inflection are identified.",
       ""])
    (DEST/"ctc-source-word-review.md").write_text("\n".join(lines),"utf-8")
    print(f"Preserved source-constrained CTC: {candidates} tentative words, {abstentions} low-support abstentions")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("source",type=Path)
    write(p.parse_args().source)
