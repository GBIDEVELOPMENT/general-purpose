#!/usr/bin/env python3
"""Pure-metadata batch plan for later original-video semantic review.

Groups already selected source windows into bounded batches; never performs
inference, never reads original episode media, never accepts theatrical claims.
"""
import argparse
import hashlib
import json
from pathlib import Path

MAX_WINDOWS_PER_BATCH=4
MAX_DURATION_PER_BATCH_MS=12000


def batches(packet):
    if packet.get("schema")!="night-court-multigoal-original-AV-review/1":
        raise ValueError("Source multi-goal review packet required")
    sha=packet.get("original_video_sha256")
    rows=packet.get("requests")
    if (not isinstance(sha,str) or len(sha)!=64 or
        packet.get("script_or_claim_independently_accepted") is not False or
        not isinstance(rows,list) or not 1<=len(rows)<=12):
        raise ValueError("Unsafe original-review metadata")
    # Temporal order minimizes source seek work and preserves scene context;
    # do not cross candidate cuts by merging windows into a larger clip.
    rows=sorted(rows,key=lambda row:row["source_window_ms"][0])
    groups=[]
    current=[]
    duration=0
    seen=set()
    for row in rows:
        window=row.get("source_window_ms")
        if (row.get("original_video_sha256")!=sha or
            row.get("independently_accepted") is not False or
            not isinstance(row.get("goals"),dict) or
            any(v!="PENDING_ORIGINAL_AV_REVIEW" for v in row["goals"].values()) or
            not isinstance(window,list) or len(window)!=2 or
            any(type(t) is not int for t in window) or
            not 0<=window[0]<window[1]<=packet["original_duration_ms"] or
            row.get("id") in seen):
            raise ValueError("Forged review claim, identity or source time")
        seen.add(row["id"])
        cost=window[1]-window[0]
        if cost>MAX_DURATION_PER_BATCH_MS:raise ValueError("Overlong AV request")
        if current and (len(current)>=MAX_WINDOWS_PER_BATCH or
                        duration+cost>MAX_DURATION_PER_BATCH_MS):
            groups.append(current)
            current=[]
            duration=0
        current.append(row)
        duration+=cost
    if current:groups.append(current)
    result=[]
    for i,group in enumerate(groups):
        result.append({
          "batch_id":f'{packet["episode_id"]}-pending-AV-batch-{i+1:02d}',
          "original_video_sha256":sha,
          "separate_original_source_windows":[r["source_window_ms"] for r in group],
          "review_request_ids":[r["id"] for r in group],
          "requested_window_ms":sum(r["source_window_ms"][1]-r["source_window_ms"][0]
                                    for r in group),
          "batch_model_inference_executed":False,
          "speaker_action_scene_or_script_accepted":False
        })
    return {
       "schema":"night-court-model-ready-original-AV-microbatches/1",
       "episode_id":packet["episode_id"],
       "original_video_sha256":sha,
       "model_provider_and_hardware_selected":False,
       "batches":result,
       "original_source_window_count":len(rows),
       "semantic_video_inference_executed":False,
       "original_episodes_or_scenes_accepted":False
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--review-packet",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():p.error("Refusing to overwrite")
    original=a.review_packet.read_bytes()
    result=batches(json.loads(original))
    result["review_packet_sha256"]=hashlib.sha256(original).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(len(result["batches"]),"bounded proposed semantic-model microbatches, no inference")


if __name__=="__main__":
    main()
