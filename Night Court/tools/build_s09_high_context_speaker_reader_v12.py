#!/usr/bin/env python3
"""Create private source-first S09 character reader v12 from careful source context.

Source dialogue, the 347 originally UNTIMED source cue IDs and all already
provisionally named characters stay unchanged. Only twelve source-anchored
previously UNKNOWN reader blocks gain explicit *editorial* role hypotheses.
No new audio, visual or actor recognition is claimed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from build_pilot_fan_beat_cards import ROOT,load_witness

SCHEMA="night-court-private-original-s09-context-reader-v12/1"
LEDGER_SCHEMA="night-court-original-s09-contextual-speaker-reading-v12/1"
LEDGER=ROOT/"research/s09-high-context-speaker-proposals-v12.json"
OLD_ROWS="pilot-current-multi-voice-turns-v11.jsonl"
OLD_MANIFEST="pilot-current-multi-voice-turns-v11-manifest.json"
ROWS="pilot-original-speaker-context-v12.jsonl"
MANIFEST="pilot-original-speaker-context-v12-manifest.json"
SOURCE_SHA="659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
STATUS="source_scene_character_dialogue_proposal_not_original_av_verified"
EXPECTED_BLOCKS=12
EXPECTED_SOURCE_UNITS=15


def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()


def verify_ledger(ledger:dict)->dict[str,dict]:
    if (ledger.get("schema")!=LEDGER_SCHEMA
        or ledger.get("episode_id")!="S09E19"
        or ledger.get("original_caption_sha256")!=SOURCE_SHA
        or ledger.get("prior_reader_version")!="v11"
        or ledger.get("original_caption_source_units")!=751
        or ledger.get("prior_named_proposals")!=595
        or ledger.get("prior_unknown_units")!=156
        or ledger.get("contextual_name_proposals_are_independently_original_audio_verified") is not False
        or ledger.get("original_dialogue_and_source_timestamps_change") is not False
        or ledger.get("original_p0_speaker_boundaries_independently_av_verified") is not False
        or ledger.get("source_subtitle_witness_is_originally_untimed") is not True):
        raise ValueError("Latest original S09 source contextual speaker ledger not admissible")
    candidates=ledger.get("candidates")
    if not isinstance(candidates,list) or len(candidates)!=EXPECTED_BLOCKS:
        raise ValueError("Exactly 12 contextual character hypotheses expected")
    byref={}
    seen_source_units=set()
    for row in candidates:
        key=row.get("source_reading_ref")
        refs=row.get("original_source_part_refs")
        role=row.get("proposed_role")
        phrase=row.get("source_text_must_contain")
        reason=row.get("reason")
        if (not isinstance(key,str) or not isinstance(refs,list) or not refs
            or not all(isinstance(ref,str) and len(ref)==6 and ref.startswith("C")
                       and ref[1:4].isdigit() and ref[4:]==".1" for ref in refs)
            or key in byref or not isinstance(role,str) or len(role)<3
            or not isinstance(phrase,str) or len(phrase)<8
            or not isinstance(reason,str) or len(reason)<35
            or row.get("source_actor_or_performer_independently_audio_verified") is not False):
            raise ValueError("Contextual role lacks exact source cue or provisional evidence")
        if len(refs)==1 and key!=refs[0]:
            raise ValueError("Single-cue source speaker record ID differs")
        if len(refs)>1 and key!="–".join(refs):
            raise ValueError("Original multi-cue reader grouping drift")
        if any(ref in seen_source_units for ref in refs):
            raise ValueError("Duplicate original caption part in S09 role overlay")
        seen_source_units.update(refs)
        byref[key]=row
    if len(seen_source_units)!=EXPECTED_SOURCE_UNITS:
        raise ValueError("Original 15 UNKNOWN cue part count differs")
    return byref


def apply_context(rows:list[dict],ledger:dict,strict:bool=True)->tuple[list[dict],dict]:
    proposed=verify_ledger(ledger)
    updated=[dict(row) for row in rows]
    found=set()
    prior_source_refs={(row["episode_id"],ref) for row in rows
                       for ref in row["original_source_part_refs"]}
    for row in updated:
        if row["episode_id"]!="S09E19" or row["source_reading_ref"] not in proposed:
            continue
        ref=row["source_reading_ref"]
        if ref in found:
            raise ValueError("Duplicated source reader block must not get repeated named role")
        evidence=proposed[ref]
        if (row.get("original_source_sha256")!=SOURCE_SHA
            or row.get("original_source_part_refs")!=evidence["original_source_part_refs"]
            or row.get("candidate_role") is not None
            or row.get("role_attribution_status")!="unidentified"
            or row.get("source_original_times_ms") is not None
            or row.get("original_source_untimed") is not True
            or row.get("speaker_turn_boundary_verified") is not False
            or row.get("actor_face_or_voice_independently_verified") is not False
            or evidence["source_text_must_contain"] not in row.get("caption_text","")):
            raise ValueError("Named source contextual hypothesis conflicts with original actor/cue")
        found.add(ref)
        row.update({
            "candidate_role":evidence["proposed_role"],
            "role_attribution_status":STATUS,
            "speaker_identity_provisional_from_context":True,
            "source_context_supporting_reason":evidence["reason"],
            "original_source_actor_voice_independently_identified":False,
            "original_untimed_s09_caption_remains_untimed":True,
            "source_exact_caption_references_used_for_character_proposal":
                list(evidence["original_source_part_refs"]),
        })
    if found!=set(proposed):
        raise ValueError("Contextual source cue targets not all present in prior original reader")
    if len(updated)!=len(rows):
        raise ValueError("Changed source speaking block count without explicit P0 proposal")
    remaining={(r["episode_id"],ref) for r in updated for ref in r["original_source_part_refs"]}
    if remaining!=prior_source_refs:
        raise ValueError("Source cue part lost or inserted by episode role guesses")
    speakers={}
    for row in updated:
        for ref in row["original_source_part_refs"]:
            speakers.setdefault((row["episode_id"],ref),set()).add(row["candidate_role"])
    named=sum(None not in xs for xs in speakers.values())
    result={
       "schema":SCHEMA,
       "original_caption_source_units":len(speakers),
       "current_provisional_character_named_original_units":named,
       "still_unknown_original_source_units":len(speakers)-named,
       "current_original_speaker_reading_blocks":len(updated),
       "previously_unidentified_reader_blocks_now_contextually_named":len(proposed),
       "new_original_caption_parts_with_working_names":EXPECTED_SOURCE_UNITS,
       "original_soundtrack_actor_identities_independently_reviewed_and_accepted":0,
       "original_S09_source_still_untimed":True,
       "source_p0_speaker_turn_divisions_auto_verified":False,
       "new_contextual_role_source_refs":sorted(proposed),
    }
    if strict and (len(rows),len(updated),len(speakers),named,len(speakers)-named)!=(
        716,716,751,610,141):
        raise ValueError("Current frozen original S09 source-led names/counts drift")
    return updated,result


def build(root:Path,prior:Path,ledger_path:Path,output:Path)->dict:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private full original source transcripts cannot be written into Git")
    raw=(prior/OLD_ROWS).read_bytes()
    old_meta=json.loads((prior/OLD_MANIFEST).read_text("utf-8"))
    if (sha(raw)!=old_meta.get("current_provisional_turn_records_sha256")
        or old_meta.get("original_caption_units")!=751
        or old_meta.get("provisional_named_original_units")!=595
        or old_meta.get("original_units_remaining_unknown")!=156
        or old_meta.get("private_provisional_reading_turn_blocks_after")!=716
        or old_meta.get("actual_audio_review_performed") is not False
        or old_meta.get("potential_character_voice_and_turn_verifications_from_actual_original_av")!=0):
        raise ValueError("Untrusted old v11 original-S09 source speaking blocks")
    meta,cues=load_witness(root,"S09E19")
    if meta["sha256"]!=SOURCE_SHA or meta["timecoded"] is not False or len(cues)!=347:
        raise ValueError("Source S09 held 347 originally untimed paragraphs changed")
    ledger_bytes=ledger_path.read_bytes()
    ledger=json.loads(ledger_bytes)
    targets=verify_ledger(ledger)
    for key,data in targets.items():
        expected=" ".join(cues[int(ref[1:4])-1]["text"] for ref in data["original_source_part_refs"])
        if data["source_text_must_contain"] not in expected:
            raise ValueError("Claimed contextual cue text does not match held S09 witness")
    original=[json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    records,report=apply_context(original,ledger)
    # A source reader may join adjacent subtitle paragraphs with inserted
    # spaces, but each original paragraph's actual bytes remain in its witness.
    output.mkdir(parents=True,exist_ok=True)
    new_raw="".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in records)
    (output/ROWS).write_text(new_raw,"utf-8")
    report["v12_source_roles_sha256"]=sha(new_raw.encode("utf-8"))
    report["input_v11_roles_sha256"]=sha(raw)
    report["source_contextual_ledger_sha256"]=sha(ledger_bytes)
    report["manuscripts_sha256_by_episode"]={}
    for ep in ("S01E01","S09E19"):
        witness=load_witness(root,ep)[0]
        lines=[f"# {ep}: private original Night Court current P0/P1 source-first reader v12","",
               "Working character names and true performance turn splits are EDITORIAL PROPOSALS",
               "until the original episode soundtrack and on-screen actor are independently checked.",
               "The original source caption wording, SHA and original lack/presence of timecodes",
               "are preserved. Scene-dialogue context is not original speaker voice evidence.",
               f"Original source SHA256: {witness['sha256']}",""]
        for row in records:
            if row["episode_id"]!=ep:continue
            role=row["candidate_role"] or "UNIDENTIFIED SPEAKER"
            lines += [f"### {row['source_reading_ref']} ({', '.join(row['original_source_part_refs'])})",
                      role+" · "+row["role_attribution_status"],row["caption_text"],""]
        manuscript="\n".join(lines).rstrip()+"\n"
        (output/f"{ep}-source-roles-v12.md").write_text(manuscript,"utf-8")
        report["manuscripts_sha256_by_episode"][ep]=sha(manuscript.encode("utf-8"))
    (output/MANIFEST).write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n","utf-8")
    return report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--v11",type=Path,required=True)
    ap.add_argument("--ledger",type=Path,default=LEDGER)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    result=build(args.root,args.v11,args.ledger,args.output)
    print(f"{result['current_provisional_character_named_original_units']} original cue parts now have provisional name roles; "
          f"{result['still_unknown_original_source_units']} UNKNOWN, "
          f"{result['new_original_caption_parts_with_working_names']} source-context-only assignments; "
          "no original audio/video speaker identification accepted")


if __name__=="__main__":
    main()
