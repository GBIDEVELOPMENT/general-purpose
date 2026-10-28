#!/usr/bin/env python3
"""Publish one stable reviewer-attested Night Court AV screenplay per pilot.

Never substitutes model scores for original film review, never overwrites the
immutable caption witness or provisional pilot-current corpus, and never
publishes partial reviewing as completed. Runs in the existing one-pass CI.
A separate independent editor is required before declaring final acceptance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from episode_finish import (
    EPISODES, make_packet, render_reviewed_screenplay, verify_decisions,
)

ROOT=Path(__file__).resolve().parents[1]
REVIEW_ROOT=ROOT/"saved-private/episode-finish-current"
SNAPSHOT=ROOT/"saved-private/pilot-current"
SCHEMA="night-court-original-av-stable-reviewed-screenplay-publication/1"
INDEPENDENT_SCHEMA="night-court-original-av-independent-editor-sample/1"


def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def independent_sample(packet:dict, ledger:dict, screenplay:bytes, file:Path|None):
    """Optional second-editor spotcheck. Never manufacture an approval."""
    if file is None or not file.is_file():
        return {"status":"pending_independent_editorial_spotcheck"}
    report=json.loads(file.read_text("utf-8"))
    sample=report.get("sampled_original_reading_block_ids")
    source_ids={x["id"] for b in packet["sequential_one_pass_batches"] for x in b["reader_blocks"]}
    sampled={x for x in sample} if isinstance(sample,list) and all(isinstance(x,str) for x in sample) else set()
    if (report.get("schema")!=INDEPENDENT_SCHEMA
        or report.get("episode_id")!=packet["episode_id"]
        or report.get("source_video_sha256")!=packet["original_video_sha256_expected"]
        or report.get("source_packet_sha256")!=packet["packet_sha256"]
        or report.get("decision_ledger_sha256")!=sha(json.dumps(
            ledger,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode("utf-8"))
        or report.get("source_exact_rendered_screenplay_sha256")!=sha(screenplay)
        or not isinstance(report.get("independent_editor"),str)
        or not report["independent_editor"].strip()
        or report["independent_editor"].strip().casefold()==ledger["reviewer"].strip().casefold()
        or report.get("original_audio_and_picture_spotchecked") is not True
        or report.get("P0_P1_contradictions_remaining")!=0
        or report.get("accepted") is not True
        or not 9<=len(sampled)<=100
        or len(sampled)!=len(sample)
        or not sampled.issubset(source_ids)):
        raise ValueError("Independent acceptance report is stale, invalid, or not independent")
    return {
        "status":"independent_editor_spotcheck_attested",
        "independent_editor":report["independent_editor"].strip(),
        "sampled_original_reading_blocks":len(sampled),
        "spotcheck_ledger_sha256":sha(file.read_bytes()),
        "independent_human_observation_cannot_be_software_proven":True,
    }


def process(episode:str,snapshot:Path,review:Path,destination:Path,write:bool):
    if episode not in EPISODES:
        raise ValueError("Unknown original-series episode")
    ledger_path=review/(episode+"-original-av-decisions.json")
    if not ledger_path.is_file():
        return {"episode":episode,"status":"no_original_av_decisions","published":False}
    ledger_bytes=ledger_path.read_bytes()
    decisions=json.loads(ledger_bytes)
    if decisions.get("episode_id")!=episode:
        raise ValueError("Wrong original source episode in signed AV ledger")
    if decisions.get("original_source_full_episode_complete") is not True:
        # Partial reviews are encouraged as backups, never promoted or marked
        # failed merely because a source reviewer paused during the episode.
        return {"episode":episode,"status":"partial_unaccepted_review","published":False}
    locator=review/"S09E19-original-audio-locators.json"
    packet=make_packet(snapshot,episode,locator if episode=="S09E19" and locator.is_file() else None)
    verdict=verify_decisions(packet,decisions)
    if verdict.get("editorial_decisions_complete") is not True:
        raise ValueError("Original film or speaking turns not entirely verified")
    script=render_reviewed_screenplay(packet,decisions).encode("utf-8")
    if packet["source_original_dialogue_sha256"].encode() not in script:
        raise ValueError("Original caption source hash missing from reviewed script")
    independent=independent_sample(
        packet,decisions,script,
        review/(episode+"-independent-original-av-acceptance.json")
    )
    manifest={
        "schema":SCHEMA,
        "episode_id":episode,
        "original_film_sha256":packet["original_video_sha256_expected"],
        "immutable_original_dialogue_sha256":packet["source_original_dialogue_sha256"],
        "canonical_input_manuscript_sha256":packet["canonical_manuscript_sha256"],
        "original_av_source_packet_sha256":packet["packet_sha256"],
        "reviewed_manuscript_sha256":sha(script),
        "actual_editorial_ledger_sha256":sha(ledger_bytes),
        "original_source_reader_blocks":packet["source_reader_blocks"],
        "original_source_part_refs":packet["original_source_speaking_part_refs"],
        "original_audio_video_review_attested_by":decisions["reviewer"].strip(),
        "independent_sample_review":independent,
        "evidence_tier":("reviewer_and_independent_spotcheck_attested"
            if independent["status"]=="independent_editor_spotcheck_attested"
            else "original_av_reviewer_attested_pending_independent_editor"),
        "software_does_not_prove_human_attention":True,
        "caption_witness_remains_immutable":True,
        "canonical_provisional_pilot_current_not_overwritten":True,
        "original_film_timeline_observation":verdict["original_film_playback_coverage"],
        "remaining_unknown_voice_labels_are_explicit_abstentions":True,
    }
    if write:
        destination.mkdir(parents=True,exist_ok=True)
        (destination/(episode+"-original-av-reviewed-screenplay.md")).write_bytes(script)
        (destination/(episode+"-original-av-reviewed-manifest.json")).write_text(
            json.dumps(manifest,indent=2,sort_keys=True,ensure_ascii=False)+"\n","utf-8")
    return {"episode":episode,"status":manifest["evidence_tier"],
            "published":write,"reviewed_sha256":sha(script),
            "independent_sample":independent["status"]}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--snapshot",type=Path,default=SNAPSHOT)
    ap.add_argument("--review-root",type=Path,default=REVIEW_ROOT)
    ap.add_argument("--output",type=Path,default=REVIEW_ROOT)
    ap.add_argument("--episode",choices=(*EPISODES,"both"),default="both")
    ap.add_argument("--write",action="store_true")
    args=ap.parse_args()
    if args.write and args.output.resolve()!=REVIEW_ROOT.resolve():
        ap.error("Committed accepted screenplay must use stable private episode-finish-current directory")
    status=[]
    for ep in EPISODES if args.episode=="both" else (args.episode,):
        status.append(process(ep,args.snapshot,args.review_root,args.output,args.write))
    print(json.dumps(status,sort_keys=True,ensure_ascii=False))


if __name__=="__main__":
    main()
