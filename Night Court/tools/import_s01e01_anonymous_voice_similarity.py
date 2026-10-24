#!/usr/bin/env python3
"""Preserve only source-verified anonymous pairwise voice similarity metadata."""
from __future__ import annotations
from itertools import combinations
import json,math,re,shutil,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"seasons"/"S01"/"S01E01"/"derived"/"scene-review-v3"
SOURCE=ROOT/"seasons"/"S01"/"S01E01"/"derived"/"scene-review-v1"/"asr-prosody-hypotheses.json"
AVI="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SRT="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"

def validate(path):
    if not path.is_file() or path.stat().st_size>80000:
        raise ValueError("Unbounded or absent anonymous vocal metadata")
    j=json.loads(path.read_text("utf-8"))
    if (j.get("schema")!="night-court-s01e01-anonymous-voice-similarity/1"
        or j.get("episode_id")!="S01E01"
        or j.get("source_media_sha256")!=AVI
        or j.get("source_caption_sha256")!=SRT
        or j.get("source_audio_window_ms")!=[60000,90000]
        or j.get("candidate_ASR_speech_segments")!=10
        or j.get("model")!="speechbrain/spkrec-ecapa-voxceleb"
        or not re.fullmatch(r"[0-9a-f]{40}",str(j.get("model_revision_sha")))
        or j.get("raw_voice_embeddings_retained") is not False
        or j.get("speaker_clusters_assigned") is not False
        or j.get("speaker_identities_assigned") is not False
        or j.get("same_speaker_pairs_verified") is not False
        or j.get("voice_biometrics_or_source_media_in_artifact") is not False
        or j.get("emotion_and_delivery_inferred") is not False):
        raise ValueError("Model provenance, private data or certainty boundary violated")
    src=json.loads(SOURCE.read_text("utf-8"))
    if src["source_media_sha256"]!=AVI or src["dialogue_source_sha256"]!=SRT:
        raise ValueError("ASR candidate source fingerprint mismatch")
    dispositions=j.get("source_voice_intervals")
    if not isinstance(dispositions,list) or len(dispositions)!=10:
        raise ValueError("Expected ten original S01E01 source candidate intervals")
    retained=[]
    for i,(d,s) in enumerate(zip(dispositions,src["asr_segments"])):
        if (d.get("asr_segment_index")!=i or
            d.get("source_interval_ms")!=[s["start_ms"],s["end_ms"]] or
            d.get("source_voice_identity") is not None or
            d.get("embedding_retained") is not False or
            d.get("speaker_isolation_verified") is not False):
            raise ValueError("Voiceprint or identity leak, or time-source change")
        status=d.get("status")
        if status not in {"abstain_short_ASR_segment","abstain_near_silence",
                          "anonymous_embedding_computed_not_speech_or_speaker_verified"}:
            raise ValueError("Unrecognized anonymous speaker status")
        if status.startswith("anonymous_embedding"):
            retained.append(i)
        elif s["end_ms"]-s["start_ms"]>=850 and status=="abstain_short_ASR_segment":
            raise ValueError("Incorrect short-utterance abstention")
    pairs=j.get("anonymous_pairs")
    if not isinstance(pairs,list):raise ValueError("Missing voice-similarity pair list")
    expected=list(combinations(retained,2))
    actual=[(x.get("asr_segment_a"),x.get("asr_segment_b")) for x in pairs]
    if actual!=expected:raise ValueError("Pairwise similarity missing/duplicate/unlisted source intervals")
    for row in pairs:
        v=row.get("anonymous_cosine_similarity_unreviewed")
        if not isinstance(v,(int,float)) or not math.isfinite(v) or not -1<=v<=1:
            raise ValueError("Invalid anonymous acoustic cosine")
        if row.get("same_speaker_conclusion") is not None or row.get("model_probability_calibrated") is not False:
            raise ValueError("Model score misrepresented as speaker probability or verified decision")
    # No high-dimensional embedding array may be serialized under any name.
    for field in ("embeddings","voiceprints","raw_audio","speaker_clusters","character_names","person_ids"):
        if field in j:raise ValueError("Unnecessary biometric/identifying artifact field")
    return j,retained

def run(path):
    if (DIR/"anonymous-voice-similarity.json").exists():
        raise ValueError("Refusing to overwrite an accepted research edition")
    j,ids=validate(path)
    shutil.copyfile(path,DIR/"anonymous-voice-similarity.json")
    lines=["# S01E01 anonymous voice similarity review",
           "",
           "**Model-only acoustic resemblance, not identity or speaker diarization.**",
           f"Model: \u0060{j['model']}\u0060 (revision \u0060{j['model_revision_sha']}\u0060)",
           f"Eligible ASR speech windows: {len(ids)} / 10.",
           f"Anonymous pairwise similarities: {len(j['anonymous_pairs'])}.",
           "",
           "ECAPA input came from mixed original television sound with laughter, music",
           "and possible overlapping character voices; scores are uncalibrated.",
           "The model was deliberately run in a process with **no FTP password**.",
           "Original WAV, AVI, model weights and per-turn voiceprints are not saved.",
           "",
           "| Model ASR spans | Anonymous cosine | Speaker decision |",
           "|---|---:|---|"]
    for pair in sorted(j["anonymous_pairs"],key=lambda x:-x["anonymous_cosine_similarity_unreviewed"]):
        lines.append(f'| {pair["asr_segment_a"]} / {pair["asr_segment_b"]} | '
                     f'{pair["anonymous_cosine_similarity_unreviewed"]:.5f} | NOT VERIFIED |')
    lines += ["","Never promote these scores to character names, voice identity,",
              "acting emotion or a full-scene synchronization certificate.",
              "Use them only to prioritize original audio listening and independent",
              "visual mouth/voice verification from the editorial task packet.",""]
    (DIR/"anonymous-voice-similarity.md").write_text("\n".join(lines),"utf-8")
    print("Preserved",len(ids),"unverified acoustic embeddings as ONLY",
          len(j["anonymous_pairs"]),"pairwise non-biometric cosine values; no raw voiceprint retained")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: import_s01e01_anonymous_voice_similarity.py ARTIFACT_JSON")
    run(Path(sys.argv[1]))
