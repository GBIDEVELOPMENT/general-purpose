#!/usr/bin/env python3
"""Prioritize remaining original Night Court P0/P1 unknowns with real source leads.

Consumes private v8 speaker evidence, original S01 SRT times, the separately
original-UNTIMED S09 audio↔text locator, and known mixed-voice cue alerts.
Outputs a SHA-bound private **review queue**, never invented role names.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import re
from pathlib import Path

from build_pilot_fan_beat_cards import ROOT,load_witness

SCHEMA="night-court-private-original-speaker-review-next/1"
VIDEO_S09_SHA="51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649"
S09_ORIGINAL_SHA="659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
S09_LOCATOR_SHA="febac6aff2cb01ee36ac1c44b592317011d655628ede2eb83981b98201e3accc"
BASE_RECORD="pilot-original-acoustic-speaker-reads.jsonl"
BASE_MANIFEST="pilot-original-acoustic-speaker-manifest.json"
V8_SHA_FIELD="source_role_record_sha256"

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def load_private_v8(path:Path)->list[dict]:
    raw=(path/BASE_RECORD).read_bytes()
    manifest=json.loads((path/BASE_MANIFEST).read_text("utf-8"))
    if (sha(raw)!=manifest.get(V8_SHA_FIELD)
        or manifest.get("original_source_caption_units")!=751
        or manifest.get("source_units_with_provisional_names")!=587
        or manifest.get("original_units_still_unknown")!=164
        or manifest.get("source_speaker_identities_human_verified_by_pass")!=0):
        raise ValueError("Private v8 role source index missing or no longer true")
    rows=[json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    if len(rows)!=716:
        raise ValueError("Private v8 source speaking blocks have drifted")
    for row in rows:
        if row.get("speaker_turn_boundary_verified") is not False:
            raise ValueError("Unverified original episode turns must remain marked provisional")
    return rows

def load_private_v9(path:Path)->list[dict]:
    raw=(path/"pilot-current-source-first-s09-audio-v9.jsonl").read_bytes()
    m=json.loads((path/"pilot-current-speaker-s09-audio-v9-manifest.json").read_text("utf-8"))
    if (sha(raw)!=m.get("current_source_roles_sha256")
        or m.get("original_source_caption_units")!=751
        or m.get("current_working_named_provisional_original_units")!=590
        or m.get("unidentified_original_cue_units")!=161
        or m.get("quarantined_suspicious_model_proposals")!=1
        or m.get("original_audio_human_identified_characters_added")!=0):
        raise ValueError("Latest private v9 source-role ledger is missing/modified")
    records=[json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    if len(records)!=716:
        raise ValueError("Original v9 cue-reader block count differs")
    disputed=[row for row in records if row["episode_id"]=="S09E19"
              and row["source_reading_ref"]=="C129.1"]
    if (len(disputed)!=1 or disputed[0].get("candidate_role") is not None
        or disputed[0].get("quarantined_acoustic_alternative_only")!="CHRISTINE SULLIVAN"):
        raise ValueError("Do not silently promote questioned original S09 C129 actor")
    if any(row.get("actor_face_or_voice_independently_verified") is not False
           for row in records):
        raise ValueError("Provisional candidate status suddenly became real AV proof")
    return records

def load_private_v10(path:Path)->list[dict]:
    """Load the latest reversible v10 source-turn reader, including two cue refs per joined turn."""
    raw=(path/"pilot-current-source-turns-v10.jsonl").read_bytes()
    m=json.loads((path/"pilot-current-source-turns-v10-manifest.json").read_text("utf-8"))
    if (sha(raw)!=m.get("current_source_role_records_sha256")
        or m.get("original_caption_immutable_source_units")!=751
        or m.get("current_provisional_character_named_original_units")!=591
        or m.get("still_unknown_original_source_units")!=160
        or m.get("reader_speaker_turn_blocks_after")!=715
        or m.get("one_joined_source_turn_refs")!=["C266.1","C267.1"]
        or m.get("source_audio_human_actor_identity_confirmations_added")!=0
        or m.get("original_S09_transcript_still_untimed") is not True):
        raise ValueError("Source-v10 original 160-UNKNOWN turn provenance failed")
    rows=[json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    if len(rows)!=715 or any(r.get("actor_face_or_voice_independently_verified") is not False for r in rows):
        raise ValueError("Source v10 invented human-accepted voice or changed turn count")
    joins=[r for r in rows if r["episode_id"]=="S09E19"
           and r["source_reading_ref"]=="C266.1–C267.1"]
    if (len(joins)!=1 or joins[0]["original_source_part_refs"]!=["C266.1","C267.1"]
        or joins[0]["candidate_role"]!="ROZ RUSSELL"
        or joins[0].get("independent_filmed_performance_turn_proven") is not False):
        raise ValueError("Provisional C266-C267 turn reunion missing")
    disputed=[r for r in rows if r["episode_id"]=="S09E19" and r["source_reading_ref"]=="C129.1"]
    if len(disputed)!=1 or disputed[0]["candidate_role"] is not None:
        raise ValueError("S09 suspicious C129 speaker cannot become accepted")
    return rows

def load_private_v11(path:Path)->list[dict]:
    raw=(path/"pilot-current-multi-voice-turns-v11.jsonl").read_bytes()
    m=json.loads((path/"pilot-current-multi-voice-turns-v11-manifest.json").read_text("utf-8"))
    if (sha(raw)!=m.get("current_provisional_turn_records_sha256")
        or m.get("original_caption_units")!=751
        or m.get("provisional_named_original_units")!=595
        or m.get("original_units_remaining_unknown")!=156
        or m.get("private_provisional_reading_turn_blocks_after")!=716
        or m.get("actual_audio_review_performed") is not False
        or m.get("potential_character_voice_and_turn_verifications_from_actual_original_av")!=0
        or m.get("original_source_fully_reconstructable_via_unicode_spans") is not True):
        raise ValueError("Source-v11 original-role 156-UNKNOWN ledger provenance failed")
    rows=[json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    if len(rows)!=716 or any(r.get("actor_face_or_voice_independently_verified") is not False for r in rows):
        raise ValueError("Source v11 source actor evidence falsely AV-certified")
    changed=[r for r in rows if r.get("role_attribution_status")==
             "scene_context_mixed_speaker_turn_proposal_not_audio_verified"]
    if (len(changed)!=6 or any(r["episode_id"]!="S09E19" or
          r.get("speaker_turn_boundary_verified") is not False or
          r.get("original_two_performer_scene_not_actually_verified") is not True
          for r in changed)):
        raise ValueError("S09 multi-voice scene turn proposals replaced with unsupported evidence")
    disputed=[r for r in rows if r["episode_id"]=="S09E19" and r["source_reading_ref"]=="C129.1"]
    if len(disputed)!=1 or disputed[0]["candidate_role"] is not None:
        raise ValueError("Original S09 C129 acoustic out-of-bank role must stay UNKNOWN")
    return rows

def load_private_v13(path:Path)->list[dict]:
    """Latest explicit split source speaking turns, without claiming verified AV roles."""
    raw=(path/"pilot-source-dialogue-turns-v13.jsonl").read_bytes()
    m=json.loads((path/"pilot-source-dialogue-turns-v13-manifest.json").read_text("utf-8"))
    if (sha(raw)!=m.get("v13_records_sha256")
        or m.get("original_held_caption_units")!=751
        or m.get("provisionally_named_original_caption_units")!=613
        or m.get("unidentified_original_caption_units")!=138
        or m.get("new_provisional_speaking_turns")!=718
        or m.get("source_audio_actor_identities_or_true_turns_independently_verified")!=0
        or m.get("all_source_character_spans_reversible") is not True
        or m.get("original_s09_untimed_source_changed") is not False):
        raise ValueError("Latest source-v13 private original speaker role SHA/count mismatch")
    rows=[json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    split=[x for x in rows
           if x.get("role_attribution_status")==
             "source_context_named_character_handoff_proposal_not_original_AV_verified"]
    if (len(rows)!=718 or len(split)!=6 or
        any(x.get("actor_face_or_voice_independently_verified") is not False
            for x in rows) or
        any(x.get("speaker_turn_boundary_verified") is not False for x in split)):
        raise ValueError("Original source P0 contextual voice turns were falsely verified")
    disputed=[x for x in rows if x["episode_id"]=="S09E19"
              and x["source_reading_ref"]=="C129.1"]
    if len(disputed)!=1 or disputed[0].get("candidate_role") is not None:
        raise ValueError("Acoustic original source speaker C129 must remain UNKNOWN")
    return rows

def load_private_source_patches(path:Path)->list[dict]:
    """Latest source-bound, append-only PAUL guest character proposals."""
    raw=(path/"pilot-source-role-amendments.jsonl").read_bytes()
    meta=json.loads((path/"pilot-source-role-amendments-manifest.json").read_text("utf-8"))
    if (sha(raw)!=meta.get("source_patch_roles_sha256")
        or meta.get("original_held_source_caption_units")!=751
        or meta.get("provisionally_named_source_units")!=619
        or meta.get("unknown_original_source_units")!=132
        or meta.get("source_reading_blocks")!=718
        or meta.get("reusable_ledger_amendment_count")!=6
        or meta.get("source_character_roles_independently_verified_via_AV")!=0
        or meta.get("source_original_cue_text_and_part_membership_unchanged") is not True):
        raise ValueError("Current 132-UNKNOWN source patch evidence or reader bytes mismatched")
    rows=[json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    if len(rows)!=718 or any(row.get("actor_face_or_voice_independently_verified") is not False
                             for row in rows):
        raise ValueError("Original actor source labels improperly treated as independently AV-verified")
    props=[r for r in rows if r.get("role_attribution_status")==
           "source_role_patch_context_only_not_original_voice_verified"]
    if (len(props)!=6 or any(r["episode_id"]!="S09E19" or r["candidate_role"]!="PAUL"
                             or r.get("source_original_times_ms") is not None for r in props)):
        raise ValueError("Source guest Paul speaker proposals lost original provenance")
    disputed=[r for r in rows if r["episode_id"]=="S09E19" and r["source_reading_ref"]=="C129.1"]
    if len(disputed)!=1 or disputed[0]["candidate_role"] is not None:
        raise ValueError("Disputed original C129 actor label must remain UNKNOWN")
    return rows

def load_private_source_turn_patches(path:Path)->list[dict]:
    """Read source-character-conserving latest 621/130 script turn ledger."""
    raw=(path/"pilot-source-turn-amendments.jsonl").read_bytes()
    m=json.loads((path/"pilot-source-turn-amendments-manifest.json").read_text("utf-8"))
    if (sha(raw)!=m.get("source_turn_records_sha256")
        or m.get("original_caption_source_units")!=751
        or m.get("named_original_source_units")!=621
        or m.get("unknown_original_source_units")!=130
        or m.get("new_provisional_reader_turn_blocks")!=721
        or m.get("original_source_exact_text_preserved") is not True
        or m.get("source_new_performer_identifications_AV_certified")!=0
        or m.get("source_new_turn_boundaries_AV_verified")!=0):
        raise ValueError("Latest 130-UNKNOWN source turn patch ledger SHA/actor evidence drift")
    rows=[json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    if len(rows)!=721 or any(r.get("actor_face_or_voice_independently_verified") is not False
                             for r in rows):
        raise ValueError("Original S09 source turn proof misrepresented")
    turns=[r for r in rows if r.get("role_attribution_status")==
           "original_dialogue_text_turn_split_context_proposal_not_original_AV_verified"]
    if (len(turns)!=5 or [r["candidate_role"] for r in turns[:3]]!=
        ["DAN FIELDING","HARRY STONE","DAN FIELDING"] or
        any(r.get("speaker_turn_boundary_verified") is not False for r in turns)):
        raise ValueError("Original speaker C102 C103 proposed turn split missing")
    disputed=[r for r in rows if r["episode_id"]=="S09E19" and r["source_reading_ref"]=="C129.1"]
    if len(disputed)!=1 or disputed[0]["candidate_role"] is not None:
        raise ValueError("Original source C129 false-positive actor label remains UNKNOWN")
    return rows

def load_s09_locator(path:Path)->dict[int,dict]:
    raw=path.read_bytes()
    if sha(raw)!=S09_LOCATOR_SHA:
        raise ValueError("Wrong S09 original-source audio locator report bytes")
    obj=json.loads(raw)
    if (obj.get("original_video_sha256")!=VIDEO_S09_SHA
        or obj.get("original_untimed_source_sha256")!=S09_ORIGINAL_SHA
        or obj.get("source_paragraphs")!=347
        or obj.get("candidate_source_paragraphs_given_audio_window")!=231
        or obj.get("exact_subtitle_timecode_recovered")!=0
        or obj.get("original_speaker_identities_verified")!=0):
        raise ValueError("Private S09 audio/source alignment never verified as input")
    lookup={}
    for item in obj.get("matches",[]):
        n=item.get("original_paragraph_id")
        a=item.get("candidate_original_audio_window_ms")
        if (type(n)!=int or n in lookup or not 1<=n<=347
            or not isinstance(a,list) or len(a)!=2
            or any(type(x)!=int for x in a) or not 0<=a[0]<a[1]<=1_800_000
            or item.get("original_paragraph_timecode_ms") is not None
            or item.get("original_film_audio_timing_independently_verified") is not False):
            raise ValueError("Untrusted S09 original audio time suggestion")
        lookup[n]=item
    if len(lookup)!=231:
        raise ValueError("Incomplete previously witnessed 231 audio locations")
    return lookup

def cue_parts(rows:list[dict])->dict[str,set[str]]:
    parts={}
    for row in rows:
        ep=row["episode_id"]
        for source in row["original_source_part_refs"]:
            key=ep+":"+source
            parts.setdefault(key,set()).add(row.get("candidate_role"))
    return parts

def make_queue(rows:list[dict],s09_times:dict[int,dict],
               internal:dict,strict:bool=True,
               expected_named:int=621,expected_unknown:int=130)->tuple[list[dict],dict]:
    roles=cue_parts(rows)
    unknown={k for k,names in roles.items() if None in names}
    marked={(r["episode_id"],r["original_cue"]) for r in internal["cues"]}
    review=[]
    for pos,row in enumerate(rows):
        if row["candidate_role"] is not None:
            continue
        ep=row["episode_id"]
        parts=row["original_source_part_refs"]
        unresolved=[ref for ref in parts if ep+":"+ref in unknown]
        if not unresolved:
            raise ValueError("Unidentified reader no longer has an unresolved source unit")
        if any(x["episode_id"]!=ep for x in rows[pos:pos+1]):
            raise ValueError("Episode partition drift")
        original_cue_ids=sorted({int(ref[1:4]) for ref in parts})
        flagged=any((ep,n) in marked for n in original_cue_ids)
        ref=row["source_reading_ref"]
        text=row["caption_text"]
        nwords=len(re.findall(r"\b[\w']+\b",text))
        window=None
        anchor=None
        if ep=="S01E01":
            times=row.get("source_original_times_ms")
            if isinstance(times,list) and times:
                start=min(x["start_ms"] for x in times)
                end=max(x["end_ms"] for x in times)
                if not 0<=start<end:
                    raise ValueError("Invalid original S01 timed caption")
                window=[max(0,start-1200),end+1200]
                anchor="held_s01_srt_approximate_not_verified_av_sync"
        elif ep=="S09E19":
            if row.get("source_original_times_ms") is not None or not row.get("original_source_untimed"):
                raise ValueError("Original S09 must remain untimed")
            matched=[s09_times.get(n) for n in original_cue_ids]
            if all(x is not None for x in matched):
                window=[min(x["candidate_original_audio_window_ms"][0] for x in matched),
                        max(x["candidate_original_audio_window_ms"][1] for x in matched)]
                anchor="unverified_original_audio_ASR_sequence_locator_not_caption_time"
        else:
            raise ValueError("Review includes unwanted original-series episode")
        possible_continuation=None
        if pos+1<len(rows):
            following=rows[pos+1]
            if (following["episode_id"]==ep
                and following.get("candidate_role") is not None
                and len(parts)==1
                and len(following["original_source_part_refs"])==1
                and int(following["original_source_part_refs"][0][1:4]) ==
                    int(parts[0][1:4])+1
                and re.match(r"^[a-z]", following["caption_text"].lstrip())
                and not re.search(r"[.!?:][\s\"']*$",text)):
                possible_continuation={
                    "next_source_ref":following["source_reading_ref"],
                    "next_provisional_role_not_verified":following["candidate_role"],
                    "reason":"original_source_sentence_continuation_candidate_P0",
                    "actual_original_audio_review_done":False
                }
        risk=["speaker_unknown"]
        score=25
        if window is not None:
            score+=20
            risk.append("actual_original_source_audio_location_candidate")
        if flagged:
            score+=30
            risk.append("possible_internal_speaker_switch_p0_review_first")
        if possible_continuation is not None:
            score+=27
            risk.append("possible_same_voice_sentence_continuation_to_next_named_cue_P0")
        if len(parts)>1:
            score+=8
            risk.append("joined_source_paragraph_parts_check_p0")
        if nwords<=5:
            score+=7
            risk.append("short_or_one_word_voice_evidence_difficult")
        if text.startswith(("...","- ","— ")):
            score+=4
            risk.append("possible_continuation_or_intra_caption_split")
        neighbors=[]
        for ix in (pos-1,pos+1):
            if 0<=ix<len(rows) and rows[ix]["episode_id"]==ep:
                neighbors.append({
                    "source_reading_ref":rows[ix]["source_reading_ref"],
                    "provisional_role_not_speaker_proof":rows[ix]["candidate_role"],
                    "dialogue_for_private_context":rows[ix]["caption_text"]
                })
        review.append({
            "schema":SCHEMA,"episode_id":ep,
            "source_reading_ref":ref,
            "original_source_part_refs":parts,
            "original_caption_sha256":row["original_source_sha256"],
            "unidentified_original_unit_refs":unresolved,
            "original_dialogue_for_private_review":text,
            "adjacent_dialogue_editorial_context_only":neighbors,
            "rank":score,
            "reasons":risk,
            "adjacent_source_sentence_continuation_candidate_not_auto_attributed":
                possible_continuation,
            "actual_original_sound_candidate_window_ms":window,
            "window_provenance_not_accepted_source_timestamp":anchor,
            "all_original_S09_caption_times_remain_null":ep=="S09E19",
            "model_proposed_character":None,
            "actual_original_voice_actor_name_verified":False,
        })
    review.sort(key=lambda r:(-r["rank"],r["episode_id"],r["source_reading_ref"]))
    unresolved_units={r["episode_id"]+":"+ref for r in review for ref in r["unidentified_original_unit_refs"]}
    outcome={
        "schema":SCHEMA,
        "original_source_units":len(roles),
        "original_units_provisionally_named":len(roles)-len(unknown),
        "original_source_units_still_unknown":len(unknown),
        "unknown_source_unit_review_records":len(review),
        "actual_audio_window_leads":sum(r["actual_original_sound_candidate_window_ms"] is not None for r in review),
        "s09_actual_audio_window_leads":sum(r["episode_id"]=="S09E19" and r["actual_original_sound_candidate_window_ms"] is not None for r in review),
        "suspected_internal_switch_review_records":sum("possible_internal_speaker_switch_p0_review_first" in r["reasons"] for r in review),
        "possible_unknown_to_named_same_sentence_continuation_reviews":sum(
            x["adjacent_source_sentence_continuation_candidate_not_auto_attributed"] is not None
            for x in review),
        "new_speaker_names_automatically_assigned":0,
        "new_voices_human_accepted":0,
        "original_untimed_S09_captions_modified":False
    }
    if unknown!=unresolved_units:
        raise ValueError("Not every unresolved original unit is covered by review queue")
    if strict and (len(roles),len(unknown),outcome["original_units_provisionally_named"])!=(
        751,expected_unknown,expected_named):
        raise ValueError("Latest actual original source ledger changed")
    return review,outcome

def build(root:Path,role_root:Path,locator:Path,output:Path,
          revision:str="v9")->dict:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private source dialogue output must never enter repo")
    if revision not in ("v8","v9","v10","v11","v13","source-patches","source-turn-patches"):
        raise ValueError("Unsupported private original speaker source version")
    rows=(load_private_source_turn_patches(role_root) if revision=="source-turn-patches" else
          load_private_source_patches(role_root) if revision=="source-patches" else
          load_private_v13(role_root) if revision=="v13" else
          load_private_v11(role_root) if revision=="v11" else
          load_private_v10(role_root) if revision=="v10" else
          load_private_v9(role_root) if revision=="v9" else load_private_v8(role_root))
    audio=load_s09_locator(locator)
    internal=json.loads((root/"research/probable-internal-speaker-switches-v1.json").read_text("utf-8"))
    for ep in ("S01E01","S09E19"):
        meta,_=load_witness(root,ep)
        for row in rows:
            if row["episode_id"]==ep and row["original_source_sha256"]!=meta["sha256"]:
                raise ValueError("Original source caption SHA mismatch in private v8 reader")
    named,unknown=((621,130) if revision=="source-turn-patches" else
                   (619,132) if revision=="source-patches" else
                   (613,138) if revision=="v13" else
                   (595,156) if revision=="v11" else
                   (591,160) if revision=="v10" else
                   (590,161) if revision=="v9" else (587,164))
    selected,manifest=make_queue(rows,audio,internal,
                                 expected_named=named,expected_unknown=unknown)
    output.mkdir(parents=True,exist_ok=True)
    (output/f"remaining-{unknown}-speaker-review.jsonl").write_text(
        "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in selected),"utf-8")
    (output/f"remaining-{unknown}-speaker-review-summary.json").write_text(
        json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+"\n","utf-8")
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    options=p.add_mutually_exclusive_group(required=True)
    options.add_argument("--speaker-v8-root",type=Path)
    options.add_argument("--speaker-v9-root",type=Path)
    options.add_argument("--speaker-v10-root",type=Path)
    options.add_argument("--speaker-v11-root",type=Path)
    options.add_argument("--speaker-v13-root",type=Path)
    options.add_argument("--speaker-patch-root",type=Path)
    options.add_argument("--speaker-turn-patch-root",type=Path)
    p.add_argument("--s09-original-audio-locator",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    role_root=(a.speaker_turn_patch_root or a.speaker_patch_root or
               a.speaker_v13_root or a.speaker_v11_root or
               a.speaker_v10_root or a.speaker_v9_root or a.speaker_v8_root)
    version=("source-turn-patches" if a.speaker_turn_patch_root is not None else
             "source-patches" if a.speaker_patch_root is not None else
             "v13" if a.speaker_v13_root is not None else
             "v11" if a.speaker_v11_root is not None else
             "v10" if a.speaker_v10_root is not None else
             "v9" if a.speaker_v9_root is not None else "v8")
    result=build(a.root,role_root,a.s09_original_audio_locator,a.output,
                 revision=version)
    print(f"{result['original_source_units_still_unknown']} unresolved original-source "
          f"units organized for P0/P1 review; "
          f"{result['s09_actual_audio_window_leads']} S09 audio-search leads; "
          "no character guesses or source transcript text in logs")

if __name__=="__main__":
    main()
