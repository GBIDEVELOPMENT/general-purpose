#!/usr/bin/env python3
"""Import prior trusted five-window S01E01 ASR drift evidence conservatively.

Do not fit a global offset to duplicate caption matches or hallucinated
30-second ASR segments. Retain raw evidence and derivative quality gates.
"""
from collections import Counter
import hashlib,json,re,shutil,sys
from pathlib import Path
from statistics import median

ROOT=Path(__file__).resolve().parents[1]
EP=ROOT/"seasons"/"S01"/"S01E01"
SOURCE=EP/"dialogue"/"versions"/"s01-internal-dvdrip-xvid-sprinter-english--aa9f77600cd9f2b6"
OUT=EP/"derived"/"source-sync-review-v1"
AVI="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SRT="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
RUN=40050642750
WINSTARTS=[300000,600000,900000,1200000,1350000]
THRESHOLD=2500

def load_original():
    manifest=json.loads((SOURCE/"manifest.json").read_text("utf-8"))
    srt=SOURCE/"original.srt"
    if manifest["sha256"]!=SRT or hashlib.sha256(srt.read_bytes()).hexdigest()!=SRT:
        raise ValueError("Original immutable DVD subtitle witness changed")
    return [json.loads(x) for x in (SOURCE/"segments.jsonl").read_text("utf-8").splitlines() if x.strip()]

def validate(path):
    if not path.is_file() or path.stat().st_size>180000:
        raise ValueError("Only bounded source-ASR evidence JSON may be imported")
    j=json.loads(path.read_text("utf-8"))
    if (j.get("schema")!="night-court-s01e01-multisite-asr-drift/1" or
        j.get("episode_id")!="S01E01" or
        j.get("original_media_sha256")!=AVI or
        j.get("original_caption_sha256")!=SRT or
        j.get("source_video_duration_ms")!=1448256 or
        j.get("ASR_model")!="faster-whisper tiny.en" or
        j.get("original_caption_times_independently_verified") is not False or
        j.get("source_edition_audio_sync_verified") is not False or
        j.get("audiovisual_episode_completeness_verified") is not False or
        j.get("identifiable_speakers_or_expressive_emotions_claimed") is not False or
        j.get("media_wav_and_model_weights_retained") is not False):
        raise ValueError("Source hash, actor or certification claim altered")
    if not isinstance(j.get("windows"),list) or len(j["windows"])!=5:
        raise ValueError("Must contain exactly five pre-authorized sample windows")
    cues=load_original()
    bycue={x["cue"]:x for x in cues}
    reports=[]
    for start,w in zip(WINSTARTS,j["windows"]):
        if w["source_window_ms"]!=[start,start+30000]:
            raise ValueError("Changed audio sample window")
        if not re.fullmatch("[0-9a-f]{64}",str(w["source_audio_sha256"])):
            raise ValueError("Bad sample source audio fingerprint")
        expected=[c["cue"] for c in cues if c["end_ms"]>start and c["start_ms"]<start+30000]
        if sorted(w["expected_source_caption_cues"])!=expected:
            raise ValueError("Source cue coverage differs from unmodified DVD subtitles")
        if w["source_cues_in_window"]!=len(expected):
            raise ValueError("Reported cue coverage mismatch")
        segments=w["asr_segments"];matches=w["alignment_candidates"]
        for seg in segments:
            if not start<=seg["start_ms"]<seg["end_ms"]<=start+30000:
                raise ValueError("ASR segment outside bounded media source")
            if seg["segment_boundary_clipped"] and seg["end_ms"]!=start+30000:
                raise ValueError("Clipped audio segment not at sample edge")
        if len(matches)!=len(segments):raise ValueError("Every model segment must retain a candidate or abstention")
        cue_matches=Counter()
        raw_anchors=[]
        for match in matches:
            n=match["asr_segment_index"]
            if not isinstance(n,int) or n<0 or n>=len(segments):
                raise ValueError("ASR alignment points to missing model segment")
            cue=match["source_caption_cue"]
            if cue is not None:
                if cue not in bycue:
                    raise ValueError("Candidate is not an original source cue")
                if match["source_cue_interval_ms"]!=[bycue[cue]["start_ms"],bycue[cue]["end_ms"]]:
                    raise ValueError("Model candidate disagrees with preserved source")
                cue_matches[cue]+=1
            delta=match["candidate_start_offset_ms"]
            if (delta is not None and not isinstance(delta,(int,float))):
                raise ValueError("Source delta not numeric")
            if (cue is not None and cue in expected and delta is not None and
                match["cue_fully_inside_window"] and
                match["lexical_similarity"]>=0.85 and abs(delta)<=THRESHOLD and
                not segments[n]["segment_boundary_clipped"] and
                segments[n]["end_ms"]-segments[n]["start_ms"]<=5000):
                raw_anchors.append({
                    "cue":cue,"asr_segment_index":n,
                    "candidate_start_difference_ms":delta,
                    "lexical_similarity":match["lexical_similarity"],
                    "status":"strict_candidate_for_manual_listening_only"})
        candidates=[x for x in raw_anchors if cue_matches[x["cue"]]==1]
        warnings=[]
        if any(n>1 for n in cue_matches.values()):
            warnings.append("repeat_caption_match_possible_ASR_hallucination_or_repeated_line")
        if any(seg["segment_boundary_clipped"] for seg in segments):
            warnings.append("end_boundary_model_proposal_clipped")
        if any((seg["end_ms"]-seg["start_ms"])>10000 for seg in segments):
            warnings.append("suspicious_long_model_segment")
        if len({x["cue"] for x in candidates})<2:
            warnings.append("insufficient_two_distinct_source_cue_anchors")
        if not candidates:warnings.append("no_strict_anchor_candidates")
        reports.append({
            "source_window_ms":w["source_window_ms"],
            "original_subtitle_cues":expected,
            "ASR_segments":len(segments),
            "heuristic_match_count":len(matches),
            "strict_candidate_anchors":candidates,
            "unique_strict_anchor_source_cues":len({x["cue"] for x in candidates}),
            "candidate_median_ms_for_listening":median(x["candidate_start_difference_ms"] for x in candidates)
                if len({x["cue"] for x in candidates})>=2 else None,
            "warnings":warnings,
            "global_drift_support":"none_without_independent_listening_and_cut_consistency"
        })
    return j,reports

def import_source(path):
    if OUT.exists():raise ValueError("Refuse prior source-sync version overwrite")
    data,reports=validate(path)
    OUT.mkdir(parents=True)
    shutil.copyfile(path,OUT/"sparse-asr-original-source.json")
    result={
       "schema":"night-court-s01e01-sparse-source-drift-triage/1",
       "episode_id":"S01E01",
       "source_media_sha256":AVI,"source_caption_sha256":SRT,
       "source_run":RUN,
       "sampled_audio_total_ms":150000,
       "original_episode_runtime_ms":1448256,
       "source_windows":reports,
       "global_source_to_subtitle_offset_ms":None,
       "drift_ms_per_minute":None,
       "reliable_global_drift_fitted":False,
       "all_source_dialogue_verified":False,
       "character_voices_verified":False,
       "video_scenes_verified":False,
       "quality_note":"ASR model times can be guessed/repeated and subtitle cue starts need not equal word onset"
    }
    (OUT/"drift-acceptance-triage.json").write_text(json.dumps(result,indent=2)+"\n","utf-8")
    text=["# S01E01 five-window original source-to-SRT drift review",
          "",
          "**No global offset or source timing drift is accepted.** A direct",
          "tiny.en-to-subtitle start difference is not equivalent to a real cut",
          "offset and can be grossly misleading with repeated or long ASR segments.",
          "",
          f"Source real-media run: [#{RUN}](https://github.com/gamesbyian/general-purpose/actions/runs/{RUN})",
          "",
          "| Source window | Candidate anchors | Proposed offset for listening only | Quality cautions |",
          "|---|---:|---:|---|"]
    for w in reports:
        a,b=w["source_window_ms"]
        offset=("Not estimated" if w["candidate_median_ms_for_listening"] is None
               else str(w["candidate_median_ms_for_listening"])+"ms, unverified")
        text.append(f'| {a/1000:.0f}–{b/1000:.0f}s | {w["unique_strict_anchor_source_cues"]} | {offset} | '
                    f'{", ".join(w["warnings"]) or "manual audio review required"} |')
    text.extend(["","## Specific source review requirements","",
        "The 05:00–05:30 sample contains repeated matching ASR text,",
        "including an implausible 27-second cue-start discrepancy. Do **not**",
        "incorporate those proposals into a linear drift model.",
        "Other windows include laughter/effects, model word hallucinations,",
        "duplicated captions and imperfect utterance boundaries.",
        "Independent listening must verify multiple unique original caption",
        "anchors per window and at least one cross-window endpoint before",
        "a drift slope or revised source subtitle timestamp can be accepted.",
        "No actor/scene/emotion/episode completeness claim is established.",""])
    (OUT/"drift-acceptance-triage.md").write_text("\n".join(text),"utf-8")
    print("Preserved real sparse ASR evidence and",len(reports),
          "strict review windows; zero accepted global drift models")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: import_s01e01_drift_qa.py JSON_FROM_PRIOR_TRUSTED_RUN")
    import_source(Path(sys.argv[1]))
