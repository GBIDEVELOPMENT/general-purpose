#!/usr/bin/env python3
"""Original S09 soundtrack: conservative acoustic role proposals for untimed cues.

Input is a SHA-verified, privately retained original-film Whisper alignment
artifact with 231 *proposed* paragraph-to-audio windows, not authentic SRT
timestamps. Reference character labels are provisional original-script
readings. Each audio interval is checked for lexical coverage, duration,
single-source-part membership, possible mid-paragraph speaker switches and
holdout quality. No actor identity is independently verified and no voice
print/video/original PCM survives the trusted runner.
"""
from __future__ import annotations

import argparse
import ftplib
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import wave

from build_pilot_character_evidence import ROOT, records_for_episode
from build_pilot_fan_beat_cards import load_witness
from compare_original_speaker_embeddings import centroid, holdout, infer, read_clip_pcm
from ftp_research_intake import connect
from pilot_ftp_video_acoustics import retrieve
from s09e19_untimed_video_anchor_pilot import exact_candidate

SCHEMA="night-court-original-s09-source-speaker-embedding-proposals/1"
ALIGNMENT_SCHEMA="night-court-s09-original-film-untimed-paragraph-audio-locator/1"
VIDEO_SHA="51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649"
SOURCE_SHA="659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
PCM_SHA="7f3e3634c99469214360d59faf69c7838301e6ee94d5f08968382a74607b6711"
ALIGNMENT_REPORT_SHA="febac6aff2cb01ee36ac1c44b592317011d655628ede2eb83981b98201e3accc"
MEDIA_BYTES=183377920
MAX_MODEL_ROLE_LABELS=18
MIN_ANCHORS=4
MAX_ANCHORS_PER_ROLE=14
MIN_ANCHOR_MS=1900
MIN_QUERY_MS=1500
MIN_ALIGN_COVERAGE=.72
MIN_ANCHOR_WORD_MATCH=4
MIN_QUERY_WORD_MATCH=3
MIN_HOLDOUT_ACC=.65
MIN_HOLDOUT_EVAL=20
MIN_SIMILARITY=.69
MIN_MARGIN=.1
MAX_REPORT_BYTES=180_000
# Source paragraph contains or probably contains multiple speakers.
# Do not use these as speaker voice embedding *seeds* or query examples.
UNRESOLVED_INTERNAL_SWITCHES={
  34,102,121,127,146,188,189,190,191,206,209,211,220,225,
  240,271,277,284,290,291
}


def digest(path:Path)->str:
    with path.open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()


def read_alignment(path:Path)->dict:
    if digest(path)!=ALIGNMENT_REPORT_SHA:
        raise ValueError("Private original S09 soundtrack paragraph report SHA mismatch")
    report=json.loads(path.read_text("utf-8"))
    if (report.get("schema")!=ALIGNMENT_SCHEMA
        or report.get("original_video_sha256")!=VIDEO_SHA
        or report.get("original_untimed_source_sha256")!=SOURCE_SHA
        or report.get("original_audio_pcm_sha256")!=PCM_SHA
        or report.get("candidate_source_paragraphs_given_audio_window")!=231
        or report.get("source_paragraphs")!=347
        or report.get("source_exact_sequence_word_matches")!=1803
        or report.get("exact_subtitle_timecode_recovered")!=0
        or report.get("original_speaker_identities_verified")!=0):
        raise ValueError("Unrecognized or falsely approved S09 original sound alignment")
    rows=report.get("matches")
    if not isinstance(rows,list) or len(rows)!=231:
        raise ValueError("Expected 231 original audio paragraph proposals")
    seen=set()
    last_start=-1
    for m in rows:
        n=m.get("original_paragraph_id")
        t=m.get("candidate_original_audio_window_ms")
        if (type(n)!=int or not 1<=n<=347 or n in seen
            or not isinstance(t,list) or len(t)!=2
            or any(type(x)!=int for x in t)
            or not 0<=t[0]<t[1]<=1_800_000
            or t[0]<last_start
            or m.get("original_paragraph_timecode_ms") is not None
            or m.get("original_film_audio_timing_independently_verified") is not False
            or m.get("spoken_character_identity_verified") is not False):
            raise ValueError("Unverified S09 paragraph audio window is malformed")
        seen.add(n)
        last_start=t[0]
    return report


def prepare_eligible(record:dict, role_by_original_paragraph:dict[int,list[dict]],
                     minimum_coverage:float=MIN_ALIGN_COVERAGE)->dict:
    """Source-bound single-voice *candidates* only; no accepted role claims."""
    if not .48<=minimum_coverage<=1:
        raise ValueError("Source lexical coverage must meet a positive evidence floor")
    sources={}
    declined=[]
    for sample in record["matches"]:
        n=sample["original_paragraph_id"]
        time_window=sample["candidate_original_audio_window_ms"]
        duration=time_window[1]-time_window[0]
        coverage=sample["global_audio_alignment_lexical_coverage"]
        matched=sample["exact_source_words_globally_matched"]
        if (n in UNRESOLVED_INTERNAL_SWITCHES
            or duration<MIN_QUERY_MS or duration>15_000
            or coverage<minimum_coverage or matched<MIN_QUERY_WORD_MATCH):
            declined.append(n)
            continue
        candidates=role_by_original_paragraph.get(n,[])
        if len(candidates)!=1:
            declined.append(n)
            continue
        row=candidates[0]
        if (row.get("original_source_part_refs")!=[f"C{n:03d}.1"]
            or row.get("speaker_turn_boundary_verified") is not False
            or row.get("actor_face_or_voice_independently_verified") is not False):
            declined.append(n)
            continue
        role=row["candidate_role"]
        obj={
            "original_source_paragraph":n,
            "original_source_reading_ref":row["source_reading_ref"],
            "original_audio_window_proposal_ms":time_window,
            "original_source_paragraph_timecode_ms":None,
            "asr_lexical_coverage":coverage,
            "asr_exact_word_matches":matched,
            "candidate_role":role,
            "original_soundtrack_human_identified_voice":False,
        }
        sources[n]=obj
    anchors={}
    queries=[]
    for x in sources.values():
        duration=x["original_audio_window_proposal_ms"][1]-x["original_audio_window_proposal_ms"][0]
        if x["candidate_role"] is None:
            queries.append(x)
        elif duration>=MIN_ANCHOR_MS and x["asr_exact_word_matches"]>=MIN_ANCHOR_WORD_MATCH:
            anchors.setdefault(x["candidate_role"],[]).append(x)
    chosen={}
    for name,items in sorted(anchors.items()):
        if len(items)<MIN_ANCHORS:
            continue
        idx=(range(len(items)) if len(items)<=MAX_ANCHORS_PER_ROLE else
             sorted({round(i*(len(items)-1)/(MAX_ANCHORS_PER_ROLE-1))
                     for i in range(MAX_ANCHORS_PER_ROLE)}))
        chosen[name]=[items[i] for i in idx]
    return {
        "schema":SCHEMA,
        "original_video_sha256_required":VIDEO_SHA,
        "original_paragraph_source_sha256":SOURCE_SHA,
        "input_audio_alignment_report_sha256":ALIGNMENT_REPORT_SHA,
        "original_source_paragraphs_total":347,
        "original_audio_paragraphs_with_candidate_windows":len(record["matches"]),
        "source_aligned_audio_windows_eligible_for_single_voice_comparison":len(sources),
        "minimum_source_lexical_coverage_for_voice_reference":minimum_coverage,
        "potentially_multivoice_or_weak_alignment_rejected_count":len(declined),
        "candidate_reference_role_counts":{k:len(v) for k,v in chosen.items()},
        "reference_audio_windows":chosen,
        "previously_unidentified_audio_windows":queries,
        "original_paragraphs_remain_untimed":True,
        "original_speech_identity_human_verified":False,
    }


def read_current_v8_speaker_roles(root:Path, private_v8:Path)->list[dict]:
    """The current source-cue SHA-bound v8 provisional role bank.

    Do not reinterpret context guesses as certified actors. Only use the
    newer editorial names as acoustically testable candidate seed labels.
    """
    from build_original_audio_speaker_reader_v8 import OUTPUT_FILE, OUTPUT_REPORT
    raw=(private_v8 / OUTPUT_FILE).read_bytes()
    manifest=json.loads((private_v8 / OUTPUT_REPORT).read_text("utf-8"))
    if (hashlib.sha256(raw).hexdigest()!=manifest.get("source_role_record_sha256")
        or manifest.get("original_source_caption_units")!=751
        or manifest.get("source_units_with_provisional_names")!=587
        or manifest.get("original_units_still_unknown")!=164
        or manifest.get("source_speaker_identities_human_verified_by_pass")!=0):
        raise ValueError("Private v8 source characters not securely derived from held original caption")
    rows=[json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    source_rows=[r for r in rows if r["episode_id"]=="S09E19"]
    _,cues=load_witness(root,"S09E19")
    if len(cues)!=347:
        raise ValueError("Original S09 source has missing paragraphs")
    accounted=set()
    for row in source_rows:
        if row["original_source_sha256"]!=SOURCE_SHA:
            raise ValueError("New character evidence conflicts with original S09 source")
        if (row.get("actor_face_or_voice_independently_verified") is not False
            or row.get("speaker_turn_boundary_verified") is not False):
            raise ValueError("Reference role improperly declares AV actor ID certified")
        for ref in row["original_source_part_refs"]:
            if ref in accounted and ref!="C034.1":
                raise ValueError("New provisional speaker source overlaps unsupported original cue")
            accounted.add(ref)
    if accounted!={f"C{i:03d}.1" for i in range(1,348)}:
        raise ValueError("Original source S09 paragraph cue missing from expanded voice bank")
    return source_rows


def source_plan(root:Path, alignment:Path,
                private_v8:Path|None=None,
                minimum_coverage:float=MIN_ALIGN_COVERAGE)->dict:
    meta,cues=load_witness(root,"S09E19")
    if meta["sha256"]!=SOURCE_SHA or meta["timecoded"] is not False or len(cues)!=347:
        raise ValueError("Original source S09 text or time status drift")
    rows=(read_current_v8_speaker_roles(root,private_v8)
          if private_v8 is not None else records_for_episode(root,"S09E19"))
    source_map={}
    for item in rows:
        for ref in item["original_source_part_refs"]:
            n=int(ref[1:4])
            source_map.setdefault(n,[]).append(item)
    plan=prepare_eligible(read_alignment(alignment),source_map,
                          minimum_coverage=minimum_coverage)
    plan["voice_reference_source"]=("latest_587_named_v8_provisional_originals"
                                    if private_v8 is not None else "older_v4_pilot_editorial_roles")
    return plan


def embed_original_source(media:Path, plan:dict, output:Path)->dict:
    import numpy as np
    from resemblyzer import VoiceEncoder
    if media.stat().st_size!=MEDIA_BYTES or digest(media)!=VIDEO_SHA:
        raise ValueError("Actual original 1992 S09 soundtrack source does not match")
    if output.exists():
        raise FileExistsError("Do not overwrite original-media acoustic findings")
    if plan.get("input_audio_alignment_report_sha256")!=ALIGNMENT_REPORT_SHA:
        raise ValueError("Wrong acoustic source alignment seed")
    with tempfile.TemporaryDirectory(prefix="night-court-s09-private-voice-") as temp:
        wavpath=Path(temp)/"original-1992-night-court-mono16.wav"
        subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
                        "-i",str(media),"-map","0:a:0","-vn","-ac","1","-ar","16000",
                        "-c:a","pcm_s16le",str(wavpath)],
                       check=True,capture_output=True,timeout=180)
        pcm_digest=digest(wavpath)
        if pcm_digest!=PCM_SHA:
            raise ValueError("S09 original PCM digest disagrees with previous verified soundtrack run")
        encoder=VoiceEncoder(device="cpu",verbose=False)
        refs={}
        queries={}
        with wave.open(str(wavpath),"rb") as wav:
            def encode(item):
                a,b=item["original_audio_window_proposal_ms"]
                audio=read_clip_pcm(wav,a,b)
                if audio is None:
                    return None
                # Does not correct for overlapping voices or laughs.
                v=encoder.embed_utterance(audio)
                arr=[float(x) for x in v.tolist()]
                if not all(math.isfinite(x) for x in arr):
                    return None
                return arr
            for role,items in plan["reference_audio_windows"].items():
                values=[]
                for row in items:
                    v=encode(row)
                    if v is not None:
                        values.append((f"C{row['original_source_paragraph']:03d}.1",v))
                if len(values)>=MIN_ANCHORS:
                    refs[role]=values
            for row in plan["previously_unidentified_audio_windows"]:
                v=encode(row)
                if v is not None:
                    queries[row["original_source_paragraph"]]=(row,v)
        quality=holdout(refs)
        good=(len(refs)>=3
              and quality["evaluated_provisional_known_voice_samples"]>=MIN_HOLDOUT_EVAL
              and quality["raw_leave_one_out_role_accuracy"] is not None
              and quality["raw_leave_one_out_role_accuracy"]>=MIN_HOLDOUT_ACC)
        vectors={role:centroid([x[1] for x in rows]) for role,rows in refs.items()}
        candidates=[]
        for n,(row,v) in sorted(queries.items()):
            match=infer(v,vectors,minimum=MIN_SIMILARITY,margin=MIN_MARGIN)
            candidates.append({
                "source_paragraph":n,
                "original_paragraph_time_ms":None,
                "original_audio_window_proposal_ms":row["original_audio_window_proposal_ms"],
                "model_prediction":match,
                "proposed_role_for_independent_editor_review":match["role"] if good else None,
                "voice_holdout_model_eligibility_passed":good,
                "speaker_identity_original_audio_human_verified":False,
                "audio_window_temporal_alignment_is_unverified":True,
            })
        report={
            "schema":SCHEMA,
            "episode_id":"S09E19",
            "source_film_sha256":VIDEO_SHA,
            "source_paragraph_sha256":SOURCE_SHA,
            "decoded_pcm_sha256":pcm_digest,
            "source_numeric_alignment_sha256":ALIGNMENT_REPORT_SHA,
            "source_paragraphs_originally_untimed":347,
            "source_paragraphs_with_asr_audio_location_candidates":231,
            "source_original_subtitle_timestamps_verified":0,
            "usable_provisional_speaker_reference_role_counts":{k:len(v) for k,v in refs.items()},
            "known_role_holdout_metrics":quality,
            "crossvalidated_acoustic_model_eligible_to_propose":good,
            "usable_unknown_source_audio_windows":len(queries),
            "unverified_acoustic_role_suggestions":sum(
                x["proposed_role_for_independent_editor_review"] is not None for x in candidates),
            "original_actor_identity_independently_verified":0,
            "source_original_soundtrack_voice_embeddings_retained":False,
            "speaker_reference_roles_originally_provisional":True,
            "voice_reference_source":plan.get("voice_reference_source"),
            "minimum_source_lexical_coverage_for_voice_reference":
                plan.get("minimum_source_lexical_coverage_for_voice_reference"),
            "model":"resemblyzer-0.1.4",
            "candidates":candidates,
        }
        body=json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
        if len(body.encode("utf-8"))>MAX_REPORT_BYTES:
            raise ValueError("Unbounded original soundtrack speaker numeric report")
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(body,"utf-8")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-alignment",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--v8-source-roles",type=Path,default=None,
                   help="Current private source-checked 587-named character evidence root")
    p.add_argument("--minimum-coverage",type=float,default=MIN_ALIGN_COVERAGE,
                   help="Source–original-audio ASR lexical word coverage; 0.48 to 1.0")
    p.add_argument("--plan-only",action="store_true")
    p.add_argument("--ftp",action="store_true")
    a=p.parse_args()
    if a.output.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("Original source audio evidence cannot be written into repository")
    plan=source_plan(ROOT,a.source_alignment,private_v8=a.v8_source_roles,
                     minimum_coverage=a.minimum_coverage)
    if a.plan_only:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n","utf-8")
        print(f"Source S09 provisional role reference groups={len(plan['reference_audio_windows'])}, "
              f"source UNKNOWN candidate windows={len(plan['previously_unidentified_audio_windows'])}; "
              "no soundtrack decoded or new speaker name accepted")
        return
    if not a.ftp or not os.getenv("FTP_PASSWORD"):
        raise ValueError("Owner-privileged SHA-pinned original AVI source required")
    candidate=exact_candidate()
    if candidate["size_bytes"]!=MEDIA_BYTES:
        raise ValueError("Original owner S09 source file size drift")
    with tempfile.TemporaryDirectory(prefix="night-court-s09-role-soundtrack-") as temp:
        movie=Path(temp)/candidate["basename"]
        ftp=connect(os.getenv("FTP_HOST","wood.seedhost.eu"),
                    os.getenv("FTP_USER","ianseeds"),os.environ["FTP_PASSWORD"],"ftp")
        try:
            downloaded=retrieve(ftp,candidate,movie)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        if downloaded!=VIDEO_SHA:
            raise ValueError("Downloaded original S09 AVI SHA changed")
        result=embed_original_source(movie,plan,a.output)
    print(f"Exact-original S09 voice source: "
          f"{result['usable_unknown_source_audio_windows']} eligible UNKNOWN paragraphs, "
          f"{result['unverified_acoustic_role_suggestions']} purely machine role suggestions; "
          f"holdout success {result['known_role_holdout_metrics']['correctly_recovered_held_out_provisional_roles']} / "
          f"{result['known_role_holdout_metrics']['evaluated_provisional_known_voice_samples']}, "
          "zero actual actor identifications accepted")


if __name__=="__main__":
    main()
