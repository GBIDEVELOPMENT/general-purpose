#!/usr/bin/env python3
"""First true-original-S09 soundtrack ASR↔UNTIMED paragraph locator candidate pass.

Uses the exact original 1992 AVI and untimed 347 source paragraphs. Both remain
separately SHA-bound and immutable. Whisper word times are machine hypotheses;
the source paragraphs get candidate *audio* intervals, NOT source timestamps,
speaker names, original video-sync certification or actor identifications.
No source video/audio/model weights/transcript words in retained JSON.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from difflib import SequenceMatcher
import ftplib
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile

from build_pilot_fan_beat_cards import ROOT, load_witness
from ftp_research_intake import connect
from pilot_ftp_video_acoustics import retrieve
from probe_s01e01_full_dual_asr import decode_audio, whisper_free_decode
from s09e19_untimed_video_anchor_pilot import exact_candidate

SCHEMA="night-court-s09-original-film-untimed-paragraph-audio-locator/1"
VIDEO_SHA="51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649"
SOURCE_SHA="659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
VIDEO_BYTES=183377920
REGEX=re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")
MIN_MATCHED_WORDS=3
MIN_COVERAGE=.46
MAX_ALIGNED_SPAN_MS=18_000
MAX_REPORT_BYTES=125_000


def tokens(text:str)->list[str]:
    return REGEX.findall(text.casefold().replace("’","'"))


def original_source(root:Path=ROOT)->list[dict]:
    meta,cues=load_witness(root,"S09E19")
    if (meta["sha256"]!=SOURCE_SHA or meta["timecoded"] is not False
        or len(cues)!=347 or any(row["cue"]!=i for i,row in enumerate(cues,1))
        or any(row["start_ms"] is not None or row["end_ms"] is not None for row in cues)):
        raise ValueError("Untimed original S09 source edition changed or falsely timed")
    return cues


def align(paragraphs:list[dict],asr_words:list[dict],
          minimum_words:int=MIN_MATCHED_WORDS,
          minimum_coverage:float=MIN_COVERAGE)->dict:
    if minimum_words<3 or not .3<=minimum_coverage<=1:
        raise ValueError("Unsafe original soundtrack lexical threshold")
    if not paragraphs or not asr_words:
        raise ValueError("Missing source or independent soundtrack words")
    if any(p["cue"]!=i for i,p in enumerate(paragraphs,1)):
        raise ValueError("Original untimed paragraph IDs not sequential")
    src=[]
    owners=[]
    for p in paragraphs:
        for t in tokens(p["text"]):
            src.append(t)
            owners.append(p["cue"])
    audio=[]
    audio_refs=[]
    prev_end=-1
    for i,row in enumerate(asr_words):
        start,end=row.get("start_ms"),row.get("end_ms")
        if (type(start)!=int or type(end)!=int or not 0<=start<end<=1_800_000
            or start<prev_end-1000):
            raise ValueError("Incorrect original-source ASR word timestamps")
        prev_end=max(prev_end,end)
        for token in tokens(row["text"]):
            audio.append(token)
            audio_refs.append((i,start,end))
    if not src or not audio:
        raise ValueError("No lexical words to align")
    # Monotone text-sequence matching only. Repeated short interjections are
    # not independently identifiable from transcription, so only 3+ exact
    # consecutive matching words can serve as source/time lexical anchors.
    blocks=SequenceMatcher(None,src,audio,autojunk=False).get_matching_blocks()
    mapping=defaultdict(list)
    matched_source_positions=set()
    for match in blocks:
        if match.size<minimum_words:
            continue
        for delta in range(match.size):
            srcpos=match.a+delta
            audpos=match.b+delta
            cue=owners[srcpos]
            index,start,end=audio_refs[audpos]
            mapping[cue].append((srcpos,audpos,start,end))
            matched_source_positions.add(srcpos)
    counts=defaultdict(int)
    for cue in owners:
        counts[cue]+=1
    out=[]
    deferred=0
    for row in paragraphs:
        n=row["cue"]
        evidence=mapping.get(n,[])
        if not evidence:
            deferred+=1
            continue
        matchcount=len({e[0] for e in evidence})
        coverage=matchcount/counts[n]
        first=min(e[2] for e in evidence)
        last=max(e[3] for e in evidence)
        duration=last-first
        if (matchcount<minimum_words or coverage<minimum_coverage
            or duration<=0 or duration>MAX_ALIGNED_SPAN_MS):
            deferred+=1
            continue
        # The proposed interval is an alignment hint to actual AVI audio,
        # not a modification of the held untimed subtitle source paragraph.
        out.append({
            "original_paragraph_id":n,
            "original_paragraph_timecode_ms":None,
            "candidate_original_audio_window_ms":[first,last],
            "exact_source_words_globally_matched":matchcount,
            "total_original_paragraph_words":counts[n],
            "global_audio_alignment_lexical_coverage":round(coverage,4),
            "original_caption_source_timed":False,
            "original_film_audio_timing_independently_verified":False,
            "spoken_character_identity_verified":False,
        })
    if any(b["candidate_original_audio_window_ms"][0]<
           a["candidate_original_audio_window_ms"][0]
           for a,b in zip(out,out[1:])):
        raise ValueError("Aligned original audio passage order not monotonic")
    return {
        "schema":SCHEMA,
        "source_paragraphs":len(paragraphs),
        "source_token_count":len(src),
        "asr_hypothesis_token_count":len(audio),
        "source_exact_sequence_word_matches":len(matched_source_positions),
        "candidate_source_paragraphs_given_audio_window":len(out),
        "unlocated_original_source_paragraphs":deferred,
        "exact_subtitle_timecode_recovered":0,
        "audio_sync_human_certified":False,
        "voice_names_independently_verified":0,
        "matches":out,
    }


def run(original_video:Path, output:Path,root:Path=ROOT)->dict:
    if original_video.stat().st_size!=VIDEO_BYTES:
        raise ValueError("Original film S09 size mismatch")
    def sha(p):
        with p.open("rb") as f:
            return hashlib.file_digest(f,"sha256").hexdigest()
    if sha(original_video)!=VIDEO_SHA:
        raise ValueError("Wrong original S09 video edition SHA")
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private original audio timing evidence must stay outside repo")
    if output.exists():
        raise FileExistsError("Don't overwrite an original audio evidence locator")
    paragraphs=original_source(root)
    with tempfile.TemporaryDirectory(prefix="night-court-original-s09-paragraphs-") as temp:
        tempdir=Path(temp)
        wav=tempdir/"source-original-16k-mono.wav"
        duration_ms, pcm_sha=decode_audio(original_video,wav)
        words,invalid,segments,reasons=whisper_free_decode(
            wav,tempdir/"whisper-weights",duration_ms)
        outcome=align(paragraphs,words)
        outcome.update({
            "episode_id":"S09E19",
            "original_video_sha256":VIDEO_SHA,
            "original_video_bytes":VIDEO_BYTES,
            "original_untimed_source_sha256":SOURCE_SHA,
            "original_source_untimed_paragraph_count":347,
            "original_audio_pcm_sha256":pcm_sha,
            "recognizer":"faster-whisper tiny.en, beam1, unprompted",
            "source_dialogue_prompted_into_asr":False,
            "asr_original_word_hypotheses":len(words),
            "asr_invalid_word_time_candidates":invalid,
            "asr_word_timestamp_rejection_reasons":reasons,
            "original_soundtrack_processed":True,
            "original_speaker_identities_verified":0,
            "source_original_movie_or_pcm_retained":False,
        })
        blob=json.dumps(outcome,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
        if len(blob.encode("utf-8"))>MAX_REPORT_BYTES:
            raise ValueError("Too many retained original-source paragraph candidate timestamps")
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(blob,"utf-8")
    return outcome


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--offline-plan-only",action="store_true")
    ap.add_argument("--ftp",action="store_true")
    a=ap.parse_args()
    if a.offline_plan_only:
        src=original_source()
        print(f"{len(src)} original S09 untimed paragraphs source-verified; no audio requested")
        return
    if not a.ftp or not os.environ.get("FTP_PASSWORD"):
        raise ValueError("Must use trusted owner source job with repository secret")
    item=exact_candidate()
    if item["size_bytes"]!=VIDEO_BYTES:
        raise ValueError("Original owner S09 source selection disagrees with verified size")
    with tempfile.TemporaryDirectory(prefix="night-court-original-S09-") as temp:
        path=Path(temp)/item["basename"]
        ftp=connect(os.environ.get("FTP_HOST","wood.seedhost.eu"),
                    os.environ.get("FTP_USER","ianseeds"),os.environ["FTP_PASSWORD"],"ftp")
        try:
            downloaded=retrieve(ftp,item,path)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        if downloaded!=VIDEO_SHA:
            raise ValueError("Original S09 source downloaded file SHA mismatch")
        report=run(path,a.output)
    print(f"S09 verified original film soundtrack: "
          f"{report['candidate_source_paragraphs_given_audio_window']} /347 "
          "source paragraphs given UNVERIFIED acoustic text-position hints; "
          "original source remains untimed, no actor identification or private soundtrack printed")


if __name__=="__main__":
    main()
