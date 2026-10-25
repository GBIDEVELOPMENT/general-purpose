#!/usr/bin/env python3
"""Show two independent impostor roles in the S09 original-dialogue reader.

Only unknown speaker heading labels may change. The public episode synopsis
and credited roles support *editorial* characterization, not person identity
in any image, lip/soundtrack identification, or source-time alignment.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from build_s09_cast_continuity_reader_v3 import render as prior,ROOT
from build_caption_first_working_drafts import SOURCE_SHA

OUT="impostor-scene-reading-screenplay-v4"
LEDGER="seasons/S09/S09E19/derived/credited-impostor-scene-v1/proposals.json"
COUNT=18


def render(root=ROOT):
    source,previous=prior(root)
    original=(root/LEDGER).read_bytes()
    evidence=json.loads(original)
    if (evidence.get("schema")!="night-court-original-s09-explicit-two-impostor-plot-roles/1"
        or evidence.get("episode_id")!="S09E19"
        or evidence.get("original_caption_sha256")!=SOURCE_SHA["S09E19"]
        or evidence.get("original_source_is_untimed") is not True
        or evidence.get("provisional_role_count")!=COUNT
        or evidence.get("no_actor_identity_asserted_from_images") is not True
        or evidence.get("original_audio_not_listened_to_validate_turns") is not True
        or evidence.get("original_source_word_or_time_mutation") is not False
        or not isinstance(evidence.get("proposals"),list)
        or len(evidence["proposals"])!=COUNT):
        raise ValueError("Two-stand-in episode plot/cast witness not source safe")
    credited=json.loads((root/"research/pilot-episode-credited-cast-v1.json").read_text("utf-8"))
    names={x["character"] for x in credited["episodes"]["S09E19"]["people"]}
    if not {"ALEX","THE GUY","ROZ RUSSELL","LISETTE HOCHEISER"}<=names:
        raise ValueError("Could not independently confirm two distinct credited impostors")
    text=source.splitlines()
    old_index=previous["source_reading_index"]
    new_index=[dict(x) for x in old_index]
    by_ref={x["source_ref"]:i for i,x in enumerate(old_index)}
    changes=[]
    for item in evidence["proposals"]:
        ref=item.get("source_ref")
        role=item.get("impostor_story_role")
        if ref not in by_ref or role not in (
            "LISETTE HOCHEISER (PLAYING ROZ)",
            "THE GUY (PLAYING ALEX)"):
            raise ValueError("Source cue was not part of reviewed episode impersonation")
        old=old_index[by_ref[ref]]
        line=old["reading_line"]+3
        if (old["speaker"]!=item["previous_unidentified_speaker_label"]
            or not old["speaker"].startswith("UNIDENTIFIED")
            or old["source_text_sha256"]!=item["original_source_dialogue_sha256"]
            or text[line]!=old["speaker"].upper()
            or item.get("original_audio_speaker_identified") is not False
            or item.get("cast_from_original_source_photograph_identified") is not False):
            raise ValueError("Cannot change original dialogue, already resolved label or image-based identity")
        new_role=role+" · PROVISIONAL EPISODE-ROLE CONTEXT"
        text[line]=new_role
        new_index[by_ref[ref]]["speaker"]=new_role
        new_index[by_ref[ref]]["source_episodic_impostor_plot_supported"]=True
        new_index[by_ref[ref]]["original_audio_voice_verified"]=False
        changes.append({"source_ref":ref,"role":role,
                        "original_dialogue_sha256":old["source_text_sha256"],
                        "speaker_identity_original_audio_verified":False})
    old_lines=source.splitlines()
    diffs=[i for i,(a,b) in enumerate(zip(old_lines,text)) if a!=b]
    legal={old_index[by_ref[p["source_ref"]]]["reading_line"]+3 for p in evidence["proposals"]}
    if len(text)!=len(old_lines) or len(diffs)!=COUNT or set(diffs)!=legal:
        raise ValueError("Attempted to rewrite original speech, action, or already named voice")
    output="\n".join(text).rstrip()+"\n"
    report={
       "schema":"night-court-two-source-impostor-roles-original-dialogue-reader/4",
       "episode_id":"S09E19",
       "source_original_caption_sha256":SOURCE_SHA["S09E19"],
       "source_original_untimed_paragraphs":347,
       "source_original_spoken_units":347,
       "previous_cast_continuity_reader_sha256":hashlib.sha256(source.encode()).hexdigest(),
       "impostor_evidence_ledger_sha256":hashlib.sha256(original).hexdigest(),
       "held_original_source_unit_word_hashes":previous["source_unit_text_hashes_in_order"],
       "new_provisional_speaker_role_blocks":COUNT,
       "previously_unidentified_dialogue_blocks_provisionally_labeled":COUNT,
       "original_source_words_or_paragraph_times_changed":False,
       "public_reference_images_used_to_identify_people":False,
       "lips_or_voice_verified_on_original_video":False,
       "full_original_video_stage_action_complete":False,
       "whole_episode_script_editor_ready":False,
       "independent_original_av_certification":False,
       "original_two_impostor_credit_distinction_preserved":True,
       "source_reading_index":new_index,
       "new_cast_and_plot_role_hypotheses":changes
    }
    return output,report


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-root",type=Path,default=ROOT)
    ap.add_argument("--check",action="store_true")
    a=ap.parse_args()
    text,report=render()
    dest=a.output_root/"seasons/S09/S09E19/derived"/OUT
    outputs={"screenplay-impostors.md":text,
             "impostor-role-source-index.json":json.dumps(report,indent=2,ensure_ascii=False)+"\n"}
    if a.check:
        for name,body in outputs.items():
            if (dest/name).read_text("utf-8")!=body:
                raise ValueError("Stale source-exact S09 two-standin manuscript "+name)
    else:
        dest.mkdir(parents=True,exist_ok=True)
        for name,body in outputs.items():(dest/name).write_text(body,encoding="utf-8")
    print("S09E19: 18 source-cited provisional stand-in dialogue roles, no original subtitle time invented")


if __name__=="__main__":main()
