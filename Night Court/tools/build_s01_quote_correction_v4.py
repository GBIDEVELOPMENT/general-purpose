#!/usr/bin/env python3
"""Reconcile a demonstrated false pilot speaker role against attributed quotations.

The old attribution and original captions remain in source/provenance; an
explicitly reviewed corrective layer edits only the final reading heading.
This is not original-audio listening, facial identification or AV acceptance.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from build_credited_courtroom_guest_reader_v3 import build as build_v3,ROOT
from build_caption_first_working_drafts import SOURCE_SHA

OUT="pilot-quote-corrected-screenplay-v4"
LEDGER="seasons/S01/S01E01/derived/editor-reviewed-speaker-corrections-v1/decisions.json"
REF="C285.1"
CORRECTED="BULL SHANNON · EXTERNALLY QUOTE-CORROBORATED; AUDIO UNVERIFIED"


def render(root=ROOT):
    source,index=build_v3(root)
    raw=(root/LEDGER).read_bytes()
    decision=json.loads(raw)
    items=index["source_reading_index"]
    matches=[x for x in items if x["source_ref"]==REF]
    if len(matches)!=1:raise ValueError("Original C285 provenance duplicate or missing")
    previous=matches[0]
    if (decision.get("schema")!="night-court-external-dialogue-quote-reconciliation/1"
        or decision.get("episode_id")!="S01E01"
        or decision.get("source_original_caption_sha256")!=SOURCE_SHA["S01E01"]
        or decision.get("source_ref")!=REF
        or decision.get("corrected_role")!="BULL SHANNON"
        or decision.get("previous_reading_label")!=previous["speaker"]
        or decision.get("original_source_unit_sha256")!=previous["source_text_sha256"]
        or decision.get("original_witness_short_line")!="Oh, yeah?"
        or decision.get("original_audio_listened") is not False
        or decision.get("actor_identified_from_original_frame") is not False
        or decision.get("original_source_words_modified") is not False
        or len(decision.get("original_episode_character_dialogue_sources",[]))<2):
        raise ValueError("Missing two-source verified character quote correction")
    before=source.splitlines()
    after=list(before)
    line=previous["reading_line"]+3
    if (before[line]!=previous["speaker"].upper()
        or before[line+1]!="Oh, yeah?"):
        raise ValueError("Changing a source dialogue text outside a proven heading")
    after[line]=CORRECTED
    if len(after)!=len(before) or [
      n for n,(old,new) in enumerate(zip(before,after)) if old!=new]!=[line]:
        raise ValueError("Only one speaker heading may be corrected")
    source_index=[dict(x) for x in items]
    at=next(i for i,x in enumerate(source_index) if x["source_ref"]==REF)
    source_index[at]["speaker"]=CORRECTED
    source_index[at]["speaker_identity_original_audio_verified"]=False
    source_index[at]["previous_incorrect_provisional_label"]=previous["speaker"]
    source_index[at]["provenance_basis"]="two_independent_character_attributed_episode_dialogue_sources"
    result="\n".join(after).rstrip()+"\n"
    manifest={
      "schema":"night-court-pilot-external-source-speaker-correction/4",
      "episode_id":"S01E01",
      "source_original_caption_sha256":SOURCE_SHA["S01E01"],
      "original_held_source_cues":336,
      "original_held_source_speaking_units":404,
      "source_original_unit_word_hashes":index["source_all_speaking_word_hashes"],
      "previous_uncorrected_reader_sha256":hashlib.sha256(source.encode()).hexdigest(),
      "correction_ledger_sha256":hashlib.sha256(raw).hexdigest(),
      "corrected_prior_wrong_speaker_labels":1,
      "new_provisional_characters_from_correction":0,
      "source_dialogue_word_or_caption_time_modified":False,
      "original_film_or_actor_photo_used_to_identify_role":False,
      "original_audio_speaker_match_verified":False,
      "whole_episode_editor_ready":False,
      "independently_full_original_AV_certified":False,
      "reversible_dialogue_source_index":source_index
    }
    return result,manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-root",type=Path,default=ROOT)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    text,proof=render()
    target=a.output_root/"seasons/S01/S01E01/derived"/OUT
    outputs={"screenplay-quote-corrected.md":text,
             "quote-correction-source-index.json":json.dumps(proof,indent=2,ensure_ascii=False)+"\n"}
    if a.check:
        for name,body in outputs.items():
            if (target/name).read_text("utf-8")!=body:
                raise ValueError("Stale externally episode-verified screenplay "+name)
    else:
        target.mkdir(parents=True,exist_ok=True)
        for name,body in outputs.items():(target/name).write_text(body,encoding="utf-8")
    print("Pilot corrected Bull/Selma original quotation, all 336 cue source lines unchanged")


if __name__=="__main__":
    main()
