#!/usr/bin/env python3
"""Integrate episode-credited cast + held-dialogue evidence into clean reader scripts.

This is NOT facial identification, lip reading, voice biometrics or original
audio verification. Names are provisional with exact original source evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from build_clean_reading_screenplay import build as build_clean,ROOT
from build_caption_first_working_drafts import SOURCE_SHA

OUT="cast-context-reading-screenplay-v2"
ROSTER="research/pilot-episode-credited-cast-v1.json"
EXPECTED={"S01E01":82,"S09E19":18}


def inputs(ep,root=ROOT):
    if ep not in EXPECTED:
        raise ValueError("Original pilots only")
    cast=json.loads((root/ROSTER).read_text("utf-8"))
    if (cast.get("schema")!="night-court-original-series-pilot-episode-cast-metadata-v1"
        or cast.get("image_identity_matching_used") is not False):
        raise ValueError("Missing source-grounded original-series episode roles")
    row=cast["episodes"][ep]
    names=[x["character"] for x in row["people"]]
    if len(set(names))!=len(names) or not row["primary_source_urls"]:
        raise ValueError("Duplicate or unsupported credited character")
    source_path=root/"seasons"/ep[:3]/ep/"derived/cast-grounded-speaker-context-v1/proposals.json"
    raw=source_path.read_bytes()
    proposals=json.loads(raw)
    if (proposals.get("schema")!="night-court-cast-and-dialogue-speaker-editorial-proposals/1"
        or proposals.get("episode_id")!=ep
        or proposals.get("original_source_caption_sha256")!=SOURCE_SHA[ep]
        or proposals.get("additional_speaker_role_proposals")!=EXPECTED[ep]
        or proposals.get("proposal_identity_status")!="UNVERIFIED_SOURCE_CONTEXT_ONLY"
        or proposals.get("no_actor_or_character_identity_claimed_from_images") is not True
        or proposals.get("not_whole_episode_av_certified") is not True
        or len(proposals.get("proposals",[]))!=EXPECTED[ep]):
        raise ValueError("Incorrect original dialogue / external cast provenance status")
    seen=set()
    for p in proposals["proposals"]:
        ref=p.get("source_ref")
        if (ref in seen or p.get("role") not in names
            or p.get("original_audio_voice_independently_verified") is not False
            or p.get("image_identity_claimed") is not False
            or not isinstance(p.get("original_dialogue_block_sha256"),str)
            or len(p["original_dialogue_block_sha256"])!=64
            or p.get("basis") not in (
                "original_dialogue_self_identification_and_distinct_credited_role",
                "character_attributed_external_episodic_dialogue",
                "source_role_reply_context_plus_episode_credits")):
            raise ValueError("Improper speaker assignment or image identity promotion")
        seen.add(ref)
    return row,proposals["proposals"],hashlib.sha256(raw).hexdigest()


def render(ep,root=ROOT):
    original,manifest=build_clean(ep,root)
    cast,proposals,ledger_sha=inputs(ep,root)
    lines=original.splitlines()
    index=manifest["dialogue_index"]
    by_ref={x["source_ref"]:x for x in index}
    if len(by_ref)!=len(index):
        raise ValueError("Repeated original source reading ref")
    new_index=[dict(x) for x in index]
    pos_by_ref={x["source_ref"]:i for i,x in enumerate(index)}
    changed=[]
    new_names=0
    for p in proposals:
        ref=p["source_ref"]
        old=by_ref.get(ref)
        if old is None:
            raise ValueError("Original source dialogue block absent: "+ref)
        if (p["original_dialogue_block_sha256"]!=old["source_text_sha256"]
            or p["expected_original_reading_label"]!=old["speaker"]):
            raise ValueError("Original speaker/text provenance drift: "+ref)
        line=old["reading_line"]+3  # 4 reader heading lines, zero-index offset
        if lines[line]!=old["speaker"].upper():
            raise ValueError("Reading line moved from original dialogue: "+ref)
        if (old["speaker"].startswith("UNIDENTIFIED SPEAKER")):
            new_names+=1
        elif not (ep=="S09E19" and ref=="C283.1" and
                  "SELF-INTRODUCING AS ALEX PATTERSON" in old["speaker"]):
            raise ValueError("Cannot silently overwrite known character voice: "+ref)
        proposed=p["role"]+" · PROVISIONAL EPISODE-CAST AND DIALOGUE"
        lines[line]=proposed
        new_index[pos_by_ref[ref]]["speaker"]=proposed
        new_index[pos_by_ref[ref]]["source_actor_credibility"]="episode_cast_exists_not_identified_by_image"
        new_index[pos_by_ref[ref]]["speaker_identity_original_audio_verified"]=False
        new_index[pos_by_ref[ref]]["evidence_tier"]=p["basis"]
        changed.append({"source_ref":ref,"proposed_character":p["role"],
            "original_reading_block_sha256":old["source_text_sha256"],
            "original_text_role_basis":p["basis"],
            "independent_voice_or_face_identification":False})
    # Strict text change scope: only original speaker heading lines are
    # modified. All source dialogue/action and line count stays unchanged.
    expected=original.splitlines()
    diffs=[i for i,(x,y) in enumerate(zip(expected,lines)) if x!=y]
    if len(expected)!=len(lines) or len(diffs)!=EXPECTED[ep]:
        raise ValueError("Unexpected dialogue text, stage directions or line-count edit")
    index_by_ref={x["source_ref"]:x for x in index}
    if any(i not in [index_by_ref[p["source_ref"]]["reading_line"]+3 for p in proposals]
           for i in diffs):
        raise ValueError("Provenance citation or dialogue word changed")
    script="\n".join(lines).rstrip()+"\n"
    no_identity=bool(ep=="S09E19" and "THE GUY" in [c["character"] for c in cast["people"]])
    derived={
        "schema":"night-court-original-episode-cast-contextual-reading-manuscript/2",
        "episode_id":ep,
        "original_source_caption_sha256":SOURCE_SHA[ep],
        "base_clean_reader_sha256":hashlib.sha256(original.encode("utf-8")).hexdigest(),
        "episode_role_ledger_sha256":ledger_sha,
        "source_original_cues":manifest["source_original_cues"],
        "source_original_speaking_units":manifest["source_original_speaking_units"],
        "source_original_unit_text_hashes":manifest["original_source_cue_unit_hashes_in_order"],
        "original_source_words_changed":False,
        "newly_named_previously_unknown_dialogue_blocks":new_names,
        "provisional_cast_attribution_edits":len(diffs),
        "original_episode_cast_credits_not_spoken_turn_proof":True,
        "known_distinct_guest_characters_alex_and_the_guy":no_identity,
        "identities_identified_from_images":False,
        "original_audio_or_lips_verified":False,
        "whole_episode_speaker_complete":False,
        "whole_episode_editor_ready":False,
        "independently_av_certified":False,
        "character_appearance_and_dialogue_confidence":"PROVISIONAL",
        "additional_cast_dialogue_assessments":changed,
        "source_reading_index":new_index
    }
    return script,derived


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--episode",choices=EXPECTED,required=True)
    p.add_argument("--output-root",type=Path,default=ROOT)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    screenplay,manifest=render(a.episode)
    out=a.output_root/"seasons"/a.episode[:3]/a.episode/"derived"/OUT
    files={
        "screenplay-cast-aware.md":screenplay,
        "cast-attribution-source-index.json":json.dumps(manifest,indent=2,ensure_ascii=False)+"\n"
    }
    if a.check:
        for name,body in files.items():
            if (out/name).read_text("utf-8")!=body:
                raise ValueError("Stale original-source cast-aware screenplay "+name)
    else:
        out.mkdir(parents=True,exist_ok=True)
        for name,body in files.items():
            (out/name).write_text(body,encoding="utf-8")
    print(a.episode,manifest["provisional_cast_attribution_edits"],
          "original-caption cast-supported role changes;",
          manifest["newly_named_previously_unknown_dialogue_blocks"],
          "formerly unknown, 0 original source AV certified")


if __name__=="__main__":
    main()
