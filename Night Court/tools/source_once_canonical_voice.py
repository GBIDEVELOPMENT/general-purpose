#!/usr/bin/env python3
"""One source transfer per pilot: compare ACTUAL soundtrack with latest canonical
provisional role reader, not an inherited v4-v19 editorial generator chain.

Machine voice proposals and anonymous boundary corroboration are NOT witnessed
actor identities, performed P0 turns or original picture/delivery acceptance.
Source AV, PCM, embedding vectors and credentials never enter Git or artifacts.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import ftplib
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import wave

from compare_original_speaker_embeddings import (
    centroid, cosine, holdout, infer, read_clip_pcm, sha256,
)
from episode_finish import VIDEO_SHA, verified_s09_candidate_locator
from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate as s01_candidate, retrieve
from s09e19_untimed_video_anchor_pilot import exact_candidate as s09_candidate
from compare_s09_original_speaker_embeddings import UNRESOLVED_INTERNAL_SWITCHES

ROOT=Path(__file__).resolve().parents[1]
CANON=ROOT/"saved-private/pilot-current"
AUDIO_S09=ROOT/"saved-private/episode-finish-current/S09E19-original-audio-locators.json"
ORIGINAL_SOURCE={
    "S01E01":"aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496",
    "S09E19":"659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2",
}
EXPECTED_BYTES={"S01E01":183386112,"S09E19":183377920}
SCHEMA="night-court-canonical-original-audio-p0-p1-evidence/1"
MIN_ANCHOR_MS=1900
MIN_QUERY_MS=1200
MAX_AUDIO_MS=12000
MAX_ANCHORS_PER_ROLE=12
MIN_ANCHORS_PER_ROLE=4
MIN_WORDS_IN_REFERENCE=4
MIN_GLOBAL_HOLDOUT=.80
MIN_ROLE_HOLDOUT=.75
MAX_REPORTED_ITEMS=375


def read_canonical(snapshot:Path=CANON)->tuple[dict,dict,dict]:
    manifest=json.loads((snapshot/"working-screenplay-layout-manifest.json").read_text("utf-8"))
    original=(snapshot/"pilot-current-editorial-reader.jsonl").read_bytes()
    if hashlib.sha256(original).hexdigest()!=manifest["current_editorial_reader_sha256"]:
        raise ValueError("Source reader SHA changed")
    rows=[json.loads(s) for s in original.decode("utf-8").splitlines() if s]
    groups={}
    by_episode={}
    for ep in ("S01E01","S09E19"):
        ep_rows=[r for r in rows if r["episode_id"]==ep]
        if len(ep_rows)!=manifest["episodes"][ep]["source_blocks"]:
            raise ValueError("Canonical reader block count drift")
        if any(r["original_source_sha256"]!=ORIGINAL_SOURCE[ep]
               or r["actor_face_or_voice_independently_verified"] is not False
               or r["speaker_turn_boundary_verified"] is not False
               for r in ep_rows):
            raise ValueError("Source-first actor status or immutable original witness changed")
        ids={r["reading_block_id"] for r in ep_rows}
        if len(ids)!=len(ep_rows):
            raise ValueError("Duplicated reader ID")
        prov=(snapshot/(ep+"-working-screenplay-provenance.jsonl")).read_text("utf-8")
        proofs=[json.loads(x) for x in prov.splitlines() if x]
        if len(proofs)!=len(ep_rows):
            raise ValueError("Source first and display provenance size differ")
        for a,b in zip(ep_rows,proofs):
            if (a["reading_block_id"]!=b["reading_block_id"]
                or a["candidate_role"]!=b["candidate_role"]
                or a["original_source_part_refs"]!=b["original_source_part_refs"]
                or hashlib.sha256(a["caption_text"].encode("utf-8")).hexdigest()
                   !=b["exact_rendered_caption_sha256"]):
                raise ValueError("Canonical source proof drift in soundtrack comparison")
        by_episode[ep]=ep_rows
        groups[ep]={p["reading_block_id"]:p["display_group_id"] for p in proofs}
    return manifest,by_episode,groups


def source_cue_n(ref):
    if not isinstance(ref,str) or len(ref)<6 or ref[0]!="C" or not ref[1:4].isdigit():
        raise ValueError("Missing original source cue")
    return int(ref[1:4])


def build_descriptors(ep,rows,locator=None):
    """Use only clean, unambiguously single-cue named seeds. No caption-clock invention."""
    if ep not in ORIGINAL_SOURCE:
        raise ValueError("Episode not permitted")
    appearances=Counter(source_cue_n(ref) for row in rows
                        for ref in row["original_source_part_refs"])
    source_audio={}
    if ep=="S09E19":
        if locator is None:
            raise ValueError("Real original film lexical locator required for UNTImED S09")
        verified_s09_candidate_locator(locator)
        report=json.loads(locator.read_text("utf-8"))
        for line in report["matches"]:
            if line["original_paragraph_id"] in source_audio:
                raise ValueError("Repeated S09 candidate audio locator")
            source_audio[line["original_paragraph_id"]]=line
    chosen=[]
    rejected=Counter()
    for row in rows:
        refs=row["original_source_part_refs"]
        if len(refs)!=1 or appearances[source_cue_n(refs[0])]!=1:
            rejected["multiple_people_or_split_caption"]+=1
            continue
        n=source_cue_n(refs[0])
        if ep=="S09E19":
            if n in UNRESOLVED_INTERNAL_SWITCHES:
                rejected["known_possible_intra_paragraph_voice_switch"]+=1;continue
            acoustic=source_audio.get(n)
            if acoustic is None:
                rejected["no_original_audio_lexical_locator"]+=1;continue
            window=acoustic.get("candidate_original_audio_window_ms")
            lexical=acoustic.get("global_audio_alignment_lexical_coverage")
            words=acoustic.get("exact_source_words_globally_matched")
            if (not isinstance(lexical,(int,float)) or
                lexical < .72 or type(words)!=int or words<3):
                rejected["weak_lexical_alignment"]+=1;continue
        else:
            times=row.get("source_original_times_ms")
            if not isinstance(times,list) or len(times)!=1:
                rejected["missing_or_ambiguous_original_cue_time"]+=1;continue
            window=[times[0]["start_ms"],times[0]["end_ms"]]
            words=len(row["caption_text"].split())
            lexical=1.0
        if (not isinstance(window,list) or len(window)!=2 or
            any(type(x)!=int for x in window) or
            not 0<=window[0]<window[1]<=1_800_000):
            raise ValueError("Out-of-bounds original source-audio candidate window")
        length=window[1]-window[0]
        if length<MIN_QUERY_MS or length>MAX_AUDIO_MS:
            rejected["bad_length_or_unusable_short_voice"]+=1;continue
        role=row["candidate_role"]
        chosen.append({"id":row["reading_block_id"],"source_ref":refs[0],
            "window_ms":window,"role":role,"reference_eligible":bool(
                role and length>=MIN_ANCHOR_MS and words>=MIN_WORDS_IN_REFERENCE),
            "time_is_original_caption":ep=="S01E01",
            "original_audio_lexical_window_unverified":ep=="S09E19",
            "audio_lexical_coverage":lexical})
    # Reference candidates must be spread chronologically across the whole film.
    refs=defaultdict(list)
    for x in chosen:
        if x["reference_eligible"]:
            refs[x["role"]].append(x)
    wanted=set()
    for role,seq in sorted(refs.items()):
        if len(seq)<MIN_ANCHORS_PER_ROLE:continue
        slots=([*range(len(seq))] if len(seq)<=MAX_ANCHORS_PER_ROLE else
               sorted({round(i*(len(seq)-1)/(MAX_ANCHORS_PER_ROLE-1))
                       for i in range(MAX_ANCHORS_PER_ROLE)}))
        wanted.update(seq[i]["id"] for i in slots)
    for row in chosen:
        row["anchor_selected"]=row["id"] in wanted
    return chosen,dict(rejected)


def source_original(ep: str, dest: Path):
    item=s01_candidate() if ep=="S01E01" else s09_candidate()
    if item["size_bytes"]!=EXPECTED_BYTES[ep]:
        raise ValueError("Original source size drift")
    password=os.environ.get("FTP_PASSWORD")
    if not password:
        raise ValueError("Missing original owner source credential")
    ftp=connect(os.environ.get("FTP_HOST","wood.seedhost.eu"),
                os.environ.get("FTP_USER","ianseeds"),password,"ftp")
    try:
        digest=retrieve(ftp,item,dest)
    finally:
        try:ftp.quit()
        except ftplib.all_errors:ftp.close()
    if digest!=VIDEO_SHA[ep]:
        raise ValueError("Original DVD-rip AVI hash changed")
    return digest


def audio_evidence(ep, movie:Path, descriptors, rejected, groups, meta, encoder):
    """All vectors transient. Export only source IDs and numeric model diagnostics."""
    if movie.stat().st_size!=EXPECTED_BYTES[ep] or sha256(movie)!=VIDEO_SHA[ep]:
        raise ValueError("Video source differs from pinned original")
    with tempfile.TemporaryDirectory(prefix="night-court-single-voice-pcm-") as scratch:
        wav=Path(scratch)/"audio.wav"
        subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
            "-i",str(movie),"-map","0:a:0","-vn","-ac","1","-ar","16000",
            "-c:a","pcm_s16le",str(wav)],check=True,capture_output=True,timeout=150)
        pcm_sha=sha256(wav)
        reference=defaultdict(list);vectors={};valid=0
        with wave.open(str(wav),"rb") as w:
            for item in descriptors:
                p=read_clip_pcm(w,*item["window_ms"])
                if p is None:
                    continue
                vec=encoder.embed_utterance(p)
                v=tuple(float(z) for z in vec)
                if not all(math.isfinite(z) for z in v):
                    continue
                vectors[item["id"]]=v
                valid+=1
                if item["anchor_selected"]:
                    reference[item["role"]].append((item["id"],v))
    quality=holdout({r:x for r,x in reference.items() if len(x)>=MIN_ANCHORS_PER_ROLE})
    counts=quality.get("provisional_role_holdout_counts",{})
    passed=bool(
        len(counts)>=3 and
        quality["evaluated_provisional_known_voice_samples"]>=20 and
        quality["raw_leave_one_out_role_accuracy"] is not None and
        quality["raw_leave_one_out_role_accuracy"]>=MIN_GLOBAL_HOLDOUT
    )
    names={r:centroid([vec for _,vec in entries]) for r,entries in reference.items()
           if len(entries)>=MIN_ANCHORS_PER_ROLE}
    by_id={x["id"]:x for x in descriptors}
    results=[]
    for item in descriptors:
        if item["role"] is not None or item["id"] not in vectors:
            continue
        m=infer(vectors[item["id"]],names,minimum=.71,margin=.10)
        role=m.get("role")
        class_quality=counts.get(role) if role else None
        role_pass=bool(class_quality and class_quality["evaluated"]>=4 and
                       class_quality["correct_held_out"]/class_quality["evaluated"]>=MIN_ROLE_HOLDOUT)
        results.append({"source_reading_block_id":item["id"],
            "source_ref":item["source_ref"],
            "source_original_timecode_ms":item["window_ms"] if ep=="S01E01" else None,
            "unverified_s09_original_audio_seek_hint_ms":item["window_ms"] if ep=="S09E19" else None,
            "acoustic_candidate":role if passed and role_pass else None,
            "uncertified_best_role":m.get("best_candidate_unaccepted"),
            "speaker_similarity":m.get("best_similarity"),
            "runner_up_similarity":m.get("runner_up_similarity"),
            "voice_model_margin":m.get("margin"),
            "global_and_role_holdout_pass":passed and role_pass,
            "actor_voice_original_soundtrack_independently_verified":False})
    joins=[]
    # Review performed boundaries (P0) as well as named role (P1), without
    # overwriting original caption joins or claiming a voice-match is truth.
    chronological=[x for x in descriptors if x["id"] in vectors]
    for a,b in zip(chronological,chronological[1:]):
        # Some dropped source reader blocks separate these; never skip them.
        ai=int(a["id"].rsplit(":",1)[-1]);bi=int(b["id"].rsplit(":",1)[-1])
        if bi!=ai+1:continue
        if not -1000<=b["window_ms"][0]-a["window_ms"][1]<=12_000:
            continue
        sim=cosine(vectors[a["id"]],vectors[b["id"]])
        joins.append({"source_left":a["id"],"source_right":b["id"],
            "provisional_display_join":groups[a["id"]]==groups[b["id"]],
            "machine_acoustic_voice_similarity":round(sim,4),
            "source_audio_p0_performed_boundary_independently_verified":False})
    if len(results)>MAX_REPORTED_ITEMS or len(joins)>MAX_REPORTED_ITEMS:
        raise ValueError("Unbounded source audio evidence report")
    return {"schema":SCHEMA,"episode_id":ep,
        "immutable_original_dialogue_sha256":ORIGINAL_SOURCE[ep],
        "original_video_sha256":VIDEO_SHA[ep],
        "canonical_manuscript_sha256":meta["manuscript_sha256"][ep],
        "source_pcm_sha256":pcm_sha,
        "original_caption_timed":ep=="S01E01",
        "unique_clean_sound_windows_considered":len(descriptors),
        "voice_embedding_windows_usable":valid,
        "source_window_rejection_counts":rejected,
        "acoustic_reference_roles_measured":{role:len(entries) for role,entries in reference.items()},
        "provisional_named_voice_holdout":quality,
        "provisional_role_holdout_threshold_passed":passed,
        "previously_unidentified_acoustic_windows_tested":len(results),
        "model_eligible_speaker_suggestions":sum(bool(x["acoustic_candidate"]) for x in results),
        "original_video_watched_by_human":False,
        "independent_original_actor_voice_accepted":0,
        "independent_performed_turns_accepted":0,
        "model_diary_not_film_truth":True,
        "media_audio_pcm_embedding_vectors_or_credentials_preserved":False,
        "unknown_original_soundtrack_proposals":results,
        "adjacent_P0_original_audio_voice_similarity":joins,
    }


def run(episode,out):
    if out.exists():raise ValueError("No silent overwrite of committed review evidence")
    meta,rows,groups=read_canonical()
    from resemblyzer import VoiceEncoder
    encoder=VoiceEncoder(device="cpu",verbose=False)
    selected=("S01E01","S09E19") if episode=="both" else (episode,)
    out.mkdir(parents=True)
    for ep in selected:
        descriptors,rejected=build_descriptors(ep,rows[ep],AUDIO_S09 if ep=="S09E19" else None)
        with tempfile.TemporaryDirectory(prefix="night-court-owner-original-") as tmp:
            movie=Path(tmp)/("original-"+ep+".avi")
            source_original(ep,movie)
            result=audio_evidence(ep,movie,descriptors,rejected,groups[ep],meta,encoder)
        dest=out/(ep+"-original-audio-p0p1-evidence.json")
        dest.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n","utf-8")
        print(ep,"original audio candidate windows",result["voice_embedding_windows_usable"],
            "unknowns",result["previously_unidentified_acoustic_windows_tested"],
            "UNCERTIFIED role hints",result["model_eligible_speaker_suggestions"],
            "P0 voice comparisons",len(result["adjacent_P0_original_audio_voice_similarity"]),
            "original AV certifications 0")


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--episode",choices=("S01E01","S09E19","both"),default="both")
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--offline-plan",action="store_true",
                    help="Read canonical source records only, never fetch the original media")
    a=ap.parse_args()
    if a.offline_plan:
        meta,rows,_=read_canonical()
        for ep in (("S01E01","S09E19") if a.episode=="both" else (a.episode,)):
            ds,rejected=build_descriptors(ep,rows[ep],AUDIO_S09 if ep=="S09E19" else None)
            print(ep,"pure source/SHA candidate windows",len(ds),"selected anchors",
                  sum(bool(x["anchor_selected"]) for x in ds),"rejected",rejected,
                  "NO video, audio, embeddings or voice acceptances")
        return
    if a.output.resolve().is_relative_to(ROOT.resolve()):
        ap.error("Raw machine output must be generated in an ephemeral runner, then vetted")
    run(a.episode,a.output)


if __name__=="__main__":
    main()
