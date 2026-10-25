#!/usr/bin/env python3
"""Enrich original pilot courtroom dialogue with credited guest-role context.

The only mutation is the heading of an as-yet unknown original speaking block.
Preserves every source dialogue and action/stage direction byte, records exact
source block hashes, and refuses to claim face or voice identity verification.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from build_cast_context_reading_screenplays import render as cast_v2,ROOT
from build_caption_first_working_drafts import SOURCE_SHA

OUT="cast-courtroom-reading-screenplay-v3"
WITNESS="seasons/S01/S01E01/derived/credited-case-speakers-v1/proposals.json"
COUNT=106

def build(root=ROOT):
    script,prior=cast_v2("S01E01",root)
    raw=(root/WITNESS).read_bytes()
    witness=json.loads(raw)
    if (witness.get("schema")!="night-court-pilot-credited-guest-and-courtroom-turns/1"
        or witness.get("episode_id")!="S01E01"
        or witness.get("original_caption_sha256")!=SOURCE_SHA["S01E01"]
        or witness.get("new_provisional_turn_labels")!=COUNT
        or witness.get("cast_list_never_proves_actor_in_a_still") is not True
        or witness.get("source_soundtrack_speaker_identity_verified") is not False
        or not isinstance(witness.get("proposals"),list)
        or len(witness["proposals"])!=COUNT):
        raise ValueError("Courtroom original source / identity integrity gate")
    roster=json.loads((root/"research/pilot-episode-credited-cast-v1.json").read_text("utf-8"))
    credited={x["character"] for x in roster["episodes"]["S01E01"]["people"]}
    index=prior["source_reading_index"]
    by_ref={x["source_ref"]:i for i,x in enumerate(index)}
    updated=[dict(x) for x in index]
    lines=script.splitlines()
    edits=[]
    seen=set()
    for p in witness["proposals"]:
        ref=p.get("source_ref")
        if ref in seen or ref not in by_ref:raise ValueError("Missing/duplicate cue reference")
        seen.add(ref)
        old=index[by_ref[ref]]
        if (p.get("proposed_role") not in credited
            or p.get("previous_source_reading_label")!=old["speaker"]
            or p.get("original_dialogue_sha256")!=old["source_text_sha256"]
            or not old["speaker"].startswith("UNIDENTIFIED")
            or p.get("visual_identity_not_inferred") is not True
            or p.get("speaker_original_soundtrack_not_listened") is not True
            or p.get("source_original_caption_times_unmodified") is not True):
            raise ValueError("Source cue conflict, false cast identity or source word rewrite")
        lineno=old["reading_line"]+3
        if lines[lineno]!=old["speaker"].upper():
            raise ValueError("Speaker line no longer linked to original dialogue block")
        character=p["proposed_role"]
        new=character+" · PROVISIONAL CREDITED-EPISODE DIALOGUE CONTEXT"
        lines[lineno]=new
        updated[by_ref[ref]]["speaker"]=new
        updated[by_ref[ref]]["evidence_kind"]=p["evidence_tier"]
        updated[by_ref[ref]]["audio_speaker_identity_verified"]=False
        edits.append({"source_ref":ref,"proposed_character":character,
            "original_source_reading_dialogue_sha256":old["source_text_sha256"],
            "status":"UNVERIFIED_EDITORIAL_HYPOTHESIS"})
    actual=[i for i,(a,b) in enumerate(zip(script.splitlines(),lines)) if a!=b]
    expected={index[by_ref[p["source_ref"]]]["reading_line"]+3 for p in witness["proposals"]}
    if len(actual)!=COUNT or set(actual)!=expected:
        raise ValueError("A non-speaker script line was modified")
    answer="\n".join(lines).rstrip()+"\n"
    proof={
       "schema":"night-court-credited-pilot-guest-case-speaker-reader/3",
       "episode_id":"S01E01",
       "original_caption_sha256":SOURCE_SHA["S01E01"],
       "original_held_caption_cues":prior["source_original_cues"],
       "original_speaking_units":prior["source_original_speaking_units"],
       "prior_reader_sha256":hashlib.sha256(script.encode("utf-8")).hexdigest(),
       "courtroom_guest_role_evidence_sha256":hashlib.sha256(raw).hexdigest(),
       "source_all_speaking_word_hashes":prior["source_original_unit_text_hashes"],
       "additional_contextual_turns_proposed":COUNT,
       "previously_unknown_source_blocks_assigned_provisionally":COUNT,
       "source_words_or_original_times_modified":False,
       "old_cast_context_roles_preserved":True,
       "credited_cast_does_not_identify_people_in_photos":True,
       "source_lip_or_audio_voice_identity_verified":False,
       "full_original_video_action_coverage_complete":False,
       "editor_ready":False,
       "independently_av_certified":False,
       "source_reading_index":updated,
       "new_contextual_guest_role_proposals":edits
    }
    return answer,proof

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-root",type=Path,default=ROOT)
    ap.add_argument("--check",action="store_true")
    a=ap.parse_args()
    script,proof=build()
    dest=a.output_root/"seasons/S01/S01E01/derived"/OUT
    outputs={"screenplay-courtroom-cast.md":script,
             "courtroom-source-index.json":json.dumps(proof,indent=2,ensure_ascii=False)+"\n"}
    if a.check:
        for file,content in outputs.items():
            if (dest/file).read_text("utf-8")!=content:
                raise ValueError("Stale source-backed courtroom screenplay "+file)
    else:
        dest.mkdir(parents=True,exist_ok=True)
        for file,content in outputs.items():
            (dest/file).write_text(content,encoding="utf-8")
    print("S01E01",proof["additional_contextual_turns_proposed"],
          "more provisional original episode court-case voices; complete original dialogue preserved")

if __name__=="__main__":main()
