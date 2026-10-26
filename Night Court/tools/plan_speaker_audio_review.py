#!/usr/bin/env python3
"""Plan short original-soundtrack listening clips for Night Court speaker P0/P1.

S01E01 has real original caption SRT timing (NOT verified audio/film sync).
S09E19 held transcript is UNTImED; it is explicitly deferred until aligned.
No video/audio samples are stored in GitHub, CI logs or outputs without a
private local movie file whose original-source SHA256 has been verified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S01_MOVIE_SHA = "5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
PLAN_SCHEMA = "night-court-private-pilot-speaker-audio-listening-plan/1"
QUEUE_SCHEMA = "night-court-private-speaker-identity-first-review/1"
MAX_CLIP_LENGTH_MS = 18000


def validate_queue(rows: list[dict]) -> None:
    if not rows or any(row.get("schema") != QUEUE_SCHEMA for row in rows):
        raise ValueError("Wrong or empty source speaker review queue")
    unique = [(x["episode_id"],x["source_ref"],x["editorial_acceptance"]) for x in rows]
    if len(set(unique)) != len(unique):
        raise ValueError("Repeated original cue review item")
    for row in rows:
        if row.get("proposed_character") is not None or row.get("original_soundtrack_reviewed") is not False:
            raise ValueError("Review proposal falsely certified audio or inserted a character")
        ep = row.get("episode_id")
        if ep == "S09E19":
            if row.get("review_srt_window") is not None:
                raise ValueError("An original untimed S09 paragraph was given invented SRT timing")
        elif ep == "S01E01":
            window = row.get("review_srt_window")
            # A named-role conflict review item need not carry timing: it must
            # be located by its original SRT cue rather than invented time.
            if window is not None and (
                type(window.get("srt_approx_start_ms")) is not int or
                type(window.get("srt_approx_end_ms")) is not int or
                window["srt_approx_start_ms"] < 0 or
                window["srt_approx_start_ms"] >= window["srt_approx_end_ms"] or
                window.get("is_verified_audio_alignment") is not False
            ):
                raise ValueError("Invalid original SRT window")
        else:
            raise ValueError("Unexpected pilot identity")


def build_plan(rows: list[dict], max_clips: int = 12, context_ms: int = 2000) -> dict:
    validate_queue(rows)
    if not 1 <= max_clips <= 32 or not 0 <= context_ms <= 6000:
        raise ValueError("Clip or context budget outside bounded listening contract")
    clips = []
    skipped = []
    for row in sorted(rows, key=lambda r: (-r["priority_score"], r["episode_id"], r["source_ref"])):
        w = row.get("review_srt_window")
        if row["episode_id"] != "S01E01" or w is None:
            skipped.append({
                "episode_id":row["episode_id"],"source_ref":row["source_ref"],
                "reason":"source_untimed_or_named_conflict_without_source_srt_window"
            })
            continue
        a = max(0,w["srt_approx_start_ms"]-context_ms)
        b = w["srt_approx_end_ms"]+context_ms
        if b-a > MAX_CLIP_LENGTH_MS:
            # Do not silently trim a source speech paragraph; defer it
            # for a larger explicitly scoped source review.
            skipped.append({"episode_id":row["episode_id"],"source_ref":row["source_ref"],
                            "reason":"unabridged_source_context_exceeds_18_second_cap"})
            continue
        merge = None
        for clip in clips:
            combined_start=min(a,clip["start_ms"])
            combined_end=max(b,clip["end_ms"])
            if (a <= clip["end_ms"] + 500 and b >= clip["start_ms"] - 500
                and combined_end-combined_start <= MAX_CLIP_LENGTH_MS):
                merge=clip
                break
        if merge is not None:
            merge["start_ms"]=min(a,merge["start_ms"])
            merge["end_ms"]=max(b,merge["end_ms"])
            merge["priority_score_max"]=max(merge["priority_score_max"],row["priority_score"])
            merge["source_refs"].append(row["source_ref"])
            continue
        if len(clips)>=max_clips:
            skipped.append({"episode_id":row["episode_id"],"source_ref":row["source_ref"],
                            "reason":"bounded_private_audio_clip_budget"})
            continue
        clips.append({
            "id":f"S01E01:listen:{len(clips)+1:03d}",
            "episode_id":"S01E01",
            "start_ms":a,"end_ms":b,
            "priority_score_max":row["priority_score"],
            "source_refs":[row["source_ref"]],
            "speaker_identity_audio_verified":False,
            "subtitle_audio_sync_verified":False
        })
    for clip in clips:
        clip["source_refs"]=sorted(set(clip["source_refs"]))
        clip["duration_ms"]=clip["end_ms"]-clip["start_ms"]
        if clip["duration_ms"]>MAX_CLIP_LENGTH_MS:
            raise AssertionError("Overlong source listening clip")
    return {
        "schema":PLAN_SCHEMA,
        "original_film_episode":"S01E01",
        "original_movie_sha256_required":S01_MOVIE_SHA,
        "source_audio_alignment_verified":False,
        "queued_unknowns_considered":len(rows),
        "selected_clip_count":len(clips),
        "source_review_items_selected":sum(len(x["source_refs"]) for x in clips),
        "skipped_review_items":len(skipped),
        "deferred_untimed_s09_items":sum(x["episode_id"]=="S09E19" for x in skipped),
        "source_video_audio_processed":False,
        "clip_list":clips,
        "deferred":skipped,
        "audio_privacy":"private_local_only_no_ci_artifact_or_public_repo_commit"
    }


def sha256_stream(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for piece in iter(lambda:fh.read(4*1024*1024),b""):
            h.update(piece)
    return h.hexdigest()


def extract_private_audio(plan: dict, movie: Path, destination: Path,
                          expected_sha: str = S01_MOVIE_SHA) -> int:
    if plan.get("schema")!=PLAN_SCHEMA or expected_sha!=plan.get("original_movie_sha256_required"):
        raise ValueError("Wrong original AVI expected identity")
    if destination.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("Cannot write source soundtrack excerpts into repository")
    if not movie.is_file() or sha256_stream(movie)!=expected_sha:
        raise ValueError("Original source AVI bytes do not match trusted SHA-256")
    destination.mkdir(parents=True,exist_ok=True)
    for i,clip in enumerate(plan["clip_list"],1):
        if not re.fullmatch(r"S01E01:listen:\d{3}",clip["id"]):
            raise ValueError("Unexpected clip ID")
        output=destination/f"s01e01-speaker-listen-{i:03d}.wav"
        if output.exists():
            raise FileExistsError("Will not overwrite previously prepared soundtrack review")
        args=[
            "ffmpeg","-nostdin","-hide_banner","-loglevel","error",
            "-ss",f"{clip['start_ms']/1000:.3f}",
            "-i",str(movie),
            "-t",f"{clip['duration_ms']/1000:.3f}",
            "-map","0:a:0","-vn","-ac","1","-ar","16000",
            "-c:a","pcm_s16le",str(output)
        ]
        subprocess.run(args,check=True,capture_output=True,timeout=90)
        if not output.is_file() or output.stat().st_size < 44:
            raise ValueError("FFmpeg produced no useful source audio")
    return len(plan["clip_list"])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--max-clips",type=int,default=12)
    parser.add_argument("--context-ms",type=int,default=2000)
    parser.add_argument("--original-avi",type=Path,default=None,
                        help="Optional local SHA-verified S01 original film; extracts private WAV")
    parser.add_argument("--audio-output",type=Path,default=None)
    a=parser.parse_args()
    if a.output.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("Private review metadata must stay outside the repository")
    data=[json.loads(line) for line in a.queue.read_text("utf-8").splitlines() if line.strip()]
    plan=build_plan(data,max_clips=a.max_clips,context_ms=a.context_ms)
    if (a.original_avi is None) != (a.audio_output is None):
        raise ValueError("Specify original film and private audio destination together")
    if a.original_avi is not None:
        count=extract_private_audio(plan,a.original_avi,a.audio_output)
        plan["source_video_audio_processed"]=True
        plan["private_wav_clips_written"]=count
        # Still NOT a human listening, source audio identity verification
        # or exact subtitle synchronization.
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(plan,indent=2,ensure_ascii=False,sort_keys=True)+"\n","utf-8")
    print(f"{plan['selected_clip_count']} bounded source listening windows planned; "
          f"{plan['deferred_untimed_s09_items']} S09 untimed cases deferred; "
          "no transcript or source audio printed")


if __name__=="__main__":
    main()
