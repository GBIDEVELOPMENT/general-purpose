#!/usr/bin/env python3
"""Private original-video S01E01 voice embedding pilot, source-cue anchored.

One SHA-pinned owner original AVI; WAV and 256-d Resemblyzer embeddings stay
ephemeral. Nothing maps actor identities from audio alone: named references
come from already *provisionally* named original caption units. Results are
UNVERIFIED acoustic-similarity proposals, with holdout validation and refusals.
No voice biometrics, episode media or caption dialogue in the report.
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
import time
import wave

from build_pilot_character_evidence import ROOT, records_for_episode
from build_pilot_fan_beat_cards import load_witness
from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate, retrieve

SCHEMA="night-court-original-s01-source-speaker-embedding-proposals/1"
VIDEO_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
CANON_SOURCE_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
# Evaluation controls are explicit and are not guaranteed to pass:
MIN_SEED_CLIP_MS=1700
MIN_QUERY_CLIP_MS=1100
MAX_ANCHORS_PER_ROLE=16
MIN_ANCHORS_PER_ROLE=4
MAX_QUERIES=97
MAX_REPORTED_PROPOSALS=97
MIN_HOLDOUT_ACCURACY=0.60
MIN_SIMILARITY=0.68
MIN_MARGIN=0.09

def sha256(path:Path)->str:
    with path.open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()


def cosine(a, b)->float:
    if len(a)!=len(b) or not a:
        raise ValueError("Embedding dimensions mismatch")
    dot=sum(float(x)*float(y) for x,y in zip(a,b))
    aa=sum(float(x)**2 for x in a)
    bb=sum(float(y)**2 for y in b)
    if not aa or not bb:
        raise ValueError("Empty/zero voice embedding")
    return dot/math.sqrt(aa*bb)


def centroid(vectors):
    if not vectors:
        raise ValueError("No embeddings to average")
    n=len(vectors[0])
    if any(len(v)!=n for v in vectors):
        raise ValueError("Incompatible speaker embedding dimensions")
    out=[sum(float(vec[i]) for vec in vectors)/len(vectors) for i in range(n)]
    magnitude=math.sqrt(sum(v*v for v in out))
    if magnitude<1e-8:
        raise ValueError("Unreliable canceling speaker centroid")
    return [x/magnitude for x in out]


def infer(embedding, reference:dict, minimum=MIN_SIMILARITY, margin=MIN_MARGIN):
    """A *proposed* role from acoustic fingerprints, never an accepted label."""
    if not 0<=minimum<=1 or not 0<=margin<=1:
        raise ValueError("Invalid calibration thresholds")
    if not reference:
        return {"status":"no_reference_voices","role":None}
    ranks=sorted(
        [(role,cosine(embedding,vec)) for role,vec in reference.items()],
        key=lambda x:(-x[1],x[0])
    )
    role,score=ranks[0]
    alternative=ranks[1][1] if len(ranks)>1 else -1.0
    distance=score-alternative
    reliable=(len(ranks)>1 and score>=minimum and distance>=margin)
    return {
        "status":("candidate_passed_uncalibrated_threshold" if reliable
                  else "ambiguous_or_low_similarity_abstain"),
        "role":role if reliable else None,
        "best_candidate_unaccepted":role,
        "best_similarity":round(score,5),
        "runner_up_similarity":round(alternative,5),
        "margin":round(distance,5),
        "thresholds_not_calibrated_to_original_episode":True,
    }


def holdout(examples:dict) ->dict:
    trials=0
    wins=0
    by_role={}
    for true_role, items in sorted(examples.items()):
        good=0
        evaluated=0
        for i,(ref,embedded) in enumerate(items):
            others={}
            for r, rows in examples.items():
                remaining=[v for j,(_,v) in enumerate(rows)
                           if r!=true_role or i!=j]
                if len(remaining)<2:
                    continue
                others[r]=centroid(remaining)
            guess=infer(embedded,others,minimum=0.0,margin=0.0)
            if guess.get("best_candidate_unaccepted") is not None:
                trials+=1
                evaluated+=1
                if guess["best_candidate_unaccepted"]==true_role:
                    wins+=1
                    good+=1
        by_role[true_role]={"correct_held_out":good,"evaluated":evaluated}
    return {
        "evaluated_provisional_known_voice_samples":trials,
        "correctly_recovered_held_out_provisional_roles":wins,
        "raw_leave_one_out_role_accuracy":round(wins/trials,4) if trials else None,
        "provisional_role_holdout_counts":by_role,
        "threshold_calibration_complete":False,
        "source_av_voice_confirmation_completed":False,
    }


def source_plan(root=ROOT)->dict:
    meta,cues=load_witness(root,"S01E01")
    if meta["sha256"]!=CANON_SOURCE_SHA or not meta["timecoded"]:
        raise ValueError("Original timed S01E01 source edition does not match")
    cue_map={c["cue"]:c for c in cues}
    reading=records_for_episode(root,"S01E01")
    part_counts={}
    for row in reading:
        for ref in row["original_source_part_refs"]:
            n=int(ref[1:4])
            part_counts[n]=part_counts.get(n,0)+1
    anchors={}
    unknown=[]
    skipped_split=0
    for row in reading:
        refs=row["original_source_part_refs"]
        # A merged reader from multiple cues is not a known single acoustic
        # turn, and the original SRT does not time internal multi-voice cues.
        if len(refs)!=1:
            continue
        ref=refs[0]
        n=int(ref[1:4])
        cue=cue_map[n]
        if part_counts.get(n)!=1 or not ref.endswith(".1"):
            skipped_split+=1
            continue
        start,end=cue["start_ms"],cue["end_ms"]
        if type(start)!=int or type(end)!=int or not 0<=start<end<=1_800_000:
            raise ValueError("Invalid timestamp in SHA-bound source caption")
        role=row["candidate_role"]
        descriptor={"ref":ref,"start_ms":start,"end_ms":end,
                    "duration_ms":end-start}
        if role is None:
            if end-start>=MIN_QUERY_CLIP_MS:
                unknown.append(descriptor)
        elif row["role_attribution_status"]=="provisional_not_original_audio_verified":
            if end-start>=MIN_SEED_CLIP_MS:
                anchors.setdefault(role,[]).append(descriptor)
    chosen={}
    for role,clips in sorted(anchors.items()):
        if len(clips)<MIN_ANCHORS_PER_ROLE:
            continue
        # Spread anchor voices across the episode to make held-out accuracy
        # more meaningful, rather than using a single adjacent dialogue scene.
        positions=(list(range(len(clips))) if len(clips)<=MAX_ANCHORS_PER_ROLE else
                   sorted({round(j*(len(clips)-1)/(MAX_ANCHORS_PER_ROLE-1))
                          for j in range(MAX_ANCHORS_PER_ROLE)}))
        selected=[clips[i] for i in positions]
        chosen[role]=selected
    if len(unknown)>MAX_QUERIES:
        unknown=unknown[:MAX_QUERIES]
    return {
        "schema":SCHEMA,
        "episode_id":"S01E01",
        "original_caption_sha256":meta["sha256"],
        "original_movie_sha256_required":VIDEO_SHA,
        "selected_reference_voice_roles":{x:len(y) for x,y in chosen.items()},
        "source_unidentified_candidates_timeable":len(unknown),
        "skipped_multi_speaker_or_untimed_source_blocks":skipped_split,
        "reference_cues":chosen,
        "unidentified_cues":unknown,
        "source_audio_reviewed":False,
        "source_identity_acceptances":0,
    }


def read_clip_pcm(wav:wave.Wave_read, start_ms:int, end_ms:int):
    import numpy as np
    if wav.getframerate()!=16000 or wav.getnchannels()!=1 or wav.getsampwidth()!=2:
        raise ValueError("Unexpected original PCM format")
    start=max(0,start_ms+100)
    end=max(start,end_ms-100)
    frames=wav.getnframes()
    a=min(frames,start*16)
    b=min(frames,end*16)
    if b-a<MIN_QUERY_CLIP_MS*16:
        return None
    wav.setpos(a)
    piece=wav.readframes(b-a)
    audio=np.frombuffer(piece,dtype="<i2").astype("float32") / 32768.0
    # Reject source silence and damaged/non-speech windows before embedding.
    rms=float(np.sqrt(np.mean(audio**2))) if len(audio) else 0
    if not math.isfinite(rms) or rms<0.006:
        return None
    return audio


def compute(source:Path,plan:dict,out:Path, model_name:str="resemblyzer-0.1.4") ->dict:
    import numpy as np
    from resemblyzer import VoiceEncoder
    if source.stat().st_size!=183_386_112 or sha256(source)!=VIDEO_SHA:
        raise ValueError("Source AVI is not the recorded original episode bytes")
    if out.exists():
        raise FileExistsError("Original evidence report must not be overwritten")
    with tempfile.TemporaryDirectory(prefix="night-court-s01e01-acoustic-pilot-") as temp:
        wav_path=Path(temp)/"original-soundtrack-mono16k.wav"
        subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
                       "-i",str(source),"-map","0:a:0","-vn",
                       "-ac","1","-ar","16000","-c:a","pcm_s16le",
                       str(wav_path)],capture_output=True,check=True,timeout=180)
        audio_sha=sha256(wav_path)
        encoder=VoiceEncoder(device="cpu",verbose=False)
        trained={}
        probes={}
        with wave.open(str(wav_path),"rb") as wav:
            def embed(descriptor):
                pcm=read_clip_pcm(wav,descriptor["start_ms"],descriptor["end_ms"])
                if pcm is None:
                    return None
                arr=encoder.embed_utterance(pcm)
                vec=[float(x) for x in arr.tolist()]
                if not all(math.isfinite(v) for v in vec):
                    return None
                return vec
            for role,items in plan["reference_cues"].items():
                values=[]
                for row in items:
                    value=embed(row)
                    if value is not None:
                        values.append((row["ref"],value))
                if len(values)>=MIN_ANCHORS_PER_ROLE:
                    trained[role]=values
            for row in plan["unidentified_cues"]:
                value=embed(row)
                if value is not None:
                    probes[row["ref"]]=(row,value)
        diag=holdout(trained)
        usable=(len(trained)>=3 and
                diag["evaluated_provisional_known_voice_samples"]>=16 and
                diag["raw_leave_one_out_role_accuracy"] is not None and
                diag["raw_leave_one_out_role_accuracy"]>=MIN_HOLDOUT_ACCURACY)
        refs={role:centroid([v for _,v in rows]) for role,rows in trained.items()}
        predictions=[]
        for ref,(row,embedding) in sorted(probes.items()):
            result=infer(embedding,refs)
            predictions.append({
                "source_ref":ref,
                "start_ms":row["start_ms"],
                "end_ms":row["end_ms"],
                "acoustic_comparison":result,
                "proposed_character_for_editor_review":(
                    result["role"] if usable else None
                ),
                "acoustic_model_eligible_to_make_proposals":usable,
                "original_audio_voice_acting_identity_verified":False,
            })
        report={
            "schema":SCHEMA,
            "episode_id":"S01E01",
            "source_video_sha256":VIDEO_SHA,
            "source_video_size_bytes":source.stat().st_size,
            "caption_source_sha256":CANON_SOURCE_SHA,
            "decoded_pcm_sha256":audio_sha,
            "embedding_model_runtime":model_name,
            "model_weights_audio_or_voice_embeddings_retained":False,
            "model_used_as_relative_speaker_recognition_not_actor_identity_proof":True,
            "speaker_reference_origins":"old_v4_provisional_non_split_long_original_subtitle_lines",
            "reference_roles_with_minimum_four_acoustic_samples":{k:len(v) for k,v in trained.items()},
            "holdout":diag,
            "minimum_proposal_eligibility_criteria_met":usable,
            "unknown_caption_units_with_usable_original_pcm":len(predictions),
            "provisional_acoustic_identity_proposals":sum(
                x["proposed_character_for_editor_review"] is not None for x in predictions),
            "source_soundtrack_processed_for_audio_embeddings":True,
            "actor_character_identities_independently_confirmed":0,
            "screen_action_performance_original_film_accepted":False,
            "predictions":predictions[:MAX_REPORTED_PROPOSALS]
        }
        encoded=json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
        if len(encoded)>180_000:
            raise ValueError("Source model numeric evidence output unbounded")
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(encoded,"utf-8")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ftp",action="store_true",
                   help="Source credentials must exist in trusted owner base checkout")
    p.add_argument("--plan-only",action="store_true",
                   help="No source video, PCM, models or secrets accessed")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if not a.ftp and not a.plan_only:
        p.error("One trusted original owner movie or source-free plan only")
    if a.output.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("Original speaker analysis output must stay outside repository")
    plan=source_plan()
    if a.plan_only:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(plan,indent=2,sort_keys=True)+"\n","utf-8")
        print(f"Speaker acoustic review plan: {len(plan['reference_cues'])} known-role "
              f"reference candidates, {plan['source_unidentified_candidates_timeable']} unknown cues")
        return
    if not os.getenv("FTP_PASSWORD"):
        raise ValueError("Owner secret missing")
    item=candidate()
    with tempfile.TemporaryDirectory(prefix="night-court-true-original-speaker-") as temp:
        path=Path(temp)/item["basename"]
        ftp=connect(os.environ.get("FTP_HOST","wood.seedhost.eu"),
                    os.environ.get("FTP_USER","ianseeds"),os.environ["FTP_PASSWORD"],"ftp")
        try:
            fetched_sha=retrieve(ftp,item,path)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        if fetched_sha!=VIDEO_SHA:
            raise ValueError("Owner original source media SHA mismatch")
        result=compute(path,plan,a.output)
    print(f"SHA-bound original episode audio analysis: "
          f"{result['unknown_caption_units_with_usable_original_pcm']} unknown-source "
          "acoustic comparisons; "
          f"{result['provisional_acoustic_identity_proposals']} UNVERIFIED proposals; "
          "no WAV, voice embedding, movie or transcript in logs/artifacts")


if __name__=="__main__":
    main()
