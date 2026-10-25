#!/usr/bin/env python3
"""Validate an independent S09 public subtitle timing probe report, never overwrite original."""
import argparse,json
from pathlib import Path
from build_caption_first_working_drafts import SOURCE_SHA,witness
from probe_original_s09_public_srt_timing import URL
ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/"seasons/S09/S09E19/derived/public-timecoded-secondary-witness-v1/probe-report.json"

def verify(doc):
    _,meta,cues,units,_=witness("S09E19")
    if (len(cues)!=347 or meta["timecoded"] is not False or
        doc.get("schema")!="night-court-s09-secondary-externally-timed-original-text-probe/1"
        or doc.get("episode_id")!="S09E19"
        or doc.get("public_secondary_source_url")!=URL
        or doc.get("original_untimed_source_caption_sha256")!=SOURCE_SHA["S09E19"]
        or doc.get("held_source_original_paragraphs")!=347
        or doc.get("original_video_synchronization_verified") is not False
        or doc.get("original_episode_speaker_identity_verified") is not False
        or doc.get("original_witness_timestamps_edited") is not False
        or doc.get("original_av_cuts_verified") is not False):
        raise ValueError("Secondary data changed protected original source dialogue or AV certainty")
    allowed=("ABSTAIN_NETWORK_OR_SOURCE_UNAVAILABLE",
             "ABSTAIN_UNVERIFIED_SECONDARY_TIMING",
             "SECONDARY_CUE_TIMES_ALL_SOURCE_TEXT_EXACT")
    if doc.get("status") not in allowed:raise ValueError("Unsupported timing probe result")
    if doc["status"]!=allowed[2]:
        if doc.get("verified_secondary_timed_cues")!=0 or doc.get("secondary_candidate_cue_times"):
            raise ValueError("Unverified partial source time witness leaked as accepted")
        return
    rows=doc.get("secondary_candidate_cue_times")
    if (doc.get("verified_secondary_timed_cues")!=347
        or not isinstance(rows,list) or len(rows)!=347
        or doc.get("source_video_clock_sync_claimed") is not False):
        raise ValueError("Complete secondary candidate timing witness missing")
    for i,row in enumerate(rows,1):
        if (row.keys()!={"cue","candidate_start_ms","candidate_end_ms"} or
            row["cue"]!=i or
            type(row["candidate_start_ms"]) is not int or
            type(row["candidate_end_ms"]) is not int or
            not 0<=row["candidate_start_ms"]<row["candidate_end_ms"]<1_800_000):
            raise ValueError("External source cue or original time invalid")
    if any(b["candidate_start_ms"]<a["candidate_start_ms"] or
           b["candidate_end_ms"]<a["candidate_end_ms"]
           for a,b in zip(rows,rows[1:])):
        raise ValueError("Secondary witness timestamps out of order")
    if doc["probe_details"]["selected_extract_mode"] is None:
        raise ValueError("Untimed public source cannot be considered timed")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--report",type=Path,default=DEFAULT)
    args=p.parse_args()
    obj=json.loads(args.report.read_text("utf-8"))
    verify(obj)
    print("S09 secondary original source report validated:",obj["status"],
          obj["verified_secondary_timed_cues"],"candidates; no original video sync accepted")
if __name__=="__main__":main()
