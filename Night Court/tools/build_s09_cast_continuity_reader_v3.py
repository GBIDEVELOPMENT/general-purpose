#!/usr/bin/env python3
"""Add auditable original episode cast+dialogue labels to S09E19 working screenplay.

Never conflate the credited Alex and separate 'The Guy', and NEVER map
the original untimed transcript to invented film frames or timestamps.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from build_cast_context_reading_screenplays import render as v2,ROOT
from build_caption_first_working_drafts import SOURCE_SHA

OUT="cast-continuity-reading-screenplay-v3"
LEDGER="seasons/S09/S09E19/derived/credited-continuity-speakers-v1/proposals.json"
EXPECTED=53

def render(root=ROOT):
    manuscript,old=v2("S09E19",root)
    raw=(root/LEDGER).read_bytes()
    evidence=json.loads(raw)
    if (evidence.get("schema")!="night-court-original-series-late-season-dialogue-role-continuation/1"
        or evidence.get("episode_id")!="S09E19"
        or evidence.get("source_caption_sha256")!=SOURCE_SHA["S09E19"]
        or evidence.get("original_source_is_untimed") is not True
        or evidence.get("proposed_source_speaking_blocks")!=EXPECTED
        or evidence.get("speaker_identification_original_soundtrack_verified") is not False
        or evidence.get("dialogue_roles_from_images") is not False
        or evidence.get("original_source_times_fabricated") is not False
        or not isinstance(evidence.get("proposals"),list)
        or len(evidence["proposals"])!=EXPECTED):
        raise ValueError("S09 original episode source or provisional identity gate")
    roster=json.loads((root/"research/pilot-episode-credited-cast-v1.json").read_text("utf-8"))
    members={x["character"] for x in roster["episodes"]["S09E19"]["people"]}
    if "ALEX" not in members or "THE GUY" not in members or "BARTENDER" not in members:
        raise ValueError("Distinct credited original S09 guest characters missing")
    index=[dict(x) for x in old["source_reading_index"]]
    by_ref={x["source_ref"]:i for i,x in enumerate(index)}
    lines=manuscript.splitlines()
    changed=[]
    for proposal in evidence["proposals"]:
        ref=proposal["source_ref"]
        if ref not in by_ref or proposal["proposed_role"] not in members:
            raise ValueError("Speaker context references uncredited identity")
        item=index[by_ref[ref]]
        lineno=item["reading_line"]+3
        if (item["speaker"]!=proposal["expected_original_reading_label"]
            or not item["speaker"].startswith("UNIDENTIFIED")
            or item["source_text_sha256"]!=proposal["original_dialogue_block_sha256"]
            or proposal.get("original_audio_voice_verified") is not False
            or proposal.get("character_or_actor_identified_in_photograph") is not False
            or lines[lineno]!=item["speaker"].upper()):
            raise ValueError("Original untimed dialogue changed or source identity falsely verified")
        new=proposal["proposed_role"]+" · PROVISIONAL EPISODE-CAST DIALOGUE"
        lines[lineno]=new
        item["speaker"]=new
        item["credited_role_evidence_tier"]=proposal["evidence_tier"]
        item["original_audio_voice_verified"]=False
        changed.append({"source_ref":ref,"proposed_role":proposal["proposed_role"],
                        "original_held_text_sha256":proposal["original_dialogue_block_sha256"],
                        "verified_original_soundtrack":False})
    oldlines=manuscript.splitlines()
    changed_lines={i for i,(a,b) in enumerate(zip(oldlines,lines)) if a!=b}
    legal={old["source_reading_index"][by_ref[p["source_ref"]]]["reading_line"]+3
           for p in evidence["proposals"]}
    if len(changed_lines)!=EXPECTED or changed_lines!=legal or len(oldlines)!=len(lines):
        raise ValueError("Editing scope crossed out of source-cited speaker labels")
    output="\n".join(lines).rstrip()+"\n"
    proof={
      "schema":"night-court-original-series-credited-S09-dialogue-reader/3",
      "episode_id":"S09E19",
      "original_caption_source_sha256":SOURCE_SHA["S09E19"],
      "base_v2_reader_sha256":hashlib.sha256(manuscript.encode()).hexdigest(),
      "credited_dialogue_ledger_sha256":hashlib.sha256(raw).hexdigest(),
      "source_original_untimed_paragraphs":347,
      "source_original_speaking_units":old["source_original_speaking_units"],
      "source_unit_text_hashes_in_order":old["source_original_unit_text_hashes"],
      "additional_provisional_guest_and_regular_voice_roles":EXPECTED,
      "previously_unknown_speaking_blocks_provisionally_named":EXPECTED,
      "distinct_alex_and_the_guy_credited_roles_preserved":True,
      "the_guy_actual_spoken_voice_verified":False,
      "source_original_paragraph_timestamps_created":False,
      "dialogue_or_observed_stage_directions_modified":False,
      "actors_identified_by_faces_or_pictures":False,
      "original_soundtrack_voice_identity_verified":False,
      "original_episode_scene_edit_ready":False,
      "whole_original_source_av_certified":False,
      "source_reading_index":index,
      "new_cast_credited_dialogue_proposals":changed
    }
    return output,proof

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root",type=Path,default=ROOT)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    manuscript,proof=render()
    out=args.output_root/"seasons/S09/S09E19/derived"/OUT
    outputs={"screenplay-cast-continuity.md":manuscript,
             "continuity-source-index.json":json.dumps(proof,indent=2,ensure_ascii=False)+"\n"}
    if args.check:
        for name,value in outputs.items():
            if (out/name).read_text("utf-8")!=value:
                raise ValueError("Stale source-complete original S09 cast manuscript "+name)
    else:
        out.mkdir(parents=True,exist_ok=True)
        for name,value in outputs.items():
            (out/name).write_text(value,encoding="utf-8")
    print("S09E19",proof["additional_provisional_guest_and_regular_voice_roles"],
         "new source-context speaking headings; 347 original untimed paragraphs unchanged")
if __name__=="__main__":
    main()
