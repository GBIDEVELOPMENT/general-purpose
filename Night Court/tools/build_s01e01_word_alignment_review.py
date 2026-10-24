#!/usr/bin/env python3
"""Build review-only original-caption-to-ASR word anchors from held evidence.

Never turn approximate model word times into certified source caption timings;
never infer scene speakers, pitch/emotion or missing original words.
"""
from __future__ import annotations
import argparse
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
from statistics import median

ROOT=Path(__file__).resolve().parents[1]
EP=ROOT/"seasons"/"S01"/"S01E01"
EDITION="s01-internal-dvdrip-xvid-sprinter-english--aa9f77600cd9f2b6"
SOURCE=EP/"dialogue"/"versions"/EDITION
OBS=EP/"derived"/"scene-review-v1"
ORIGINAL_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
MEDIA_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
TOKEN=re.compile(r"[^\W_]+(?:['\u2019][^\W_]+)*",re.UNICODE)

def tokens(s):
    return [m.group(0).replace("\u2019","'").lower() for m in TOKEN.finditer(s)]

def turns(text):
    """Split explicit two-speaker subtitle typography only; no speaker guesses."""
    lines=text.strip().splitlines()
    split_mode= len(lines)>1 and lines[0].lstrip().startswith("- ") and any(
        x.lstrip().startswith("- ") for x in lines[1:])
    if not split_mode:
        return [{"source_turn_index":0,"text":" ".join(x.strip() for x in lines),
                 "turn_split_evidence":"single_cue_or_continuation"}]
    result=[]
    for line in lines:
        val=line.strip()
        if val.startswith("- "):
            result.append({"source_turn_index":len(result),"text":val[2:].strip(),
                           "turn_split_evidence":"explicit_source_leading_hyphen"})
        elif result:
            result[-1]["text"]+=" "+val
        else:
            raise ValueError("Unattributed leading fragment")
    return result

def word_matches(cue_text,segment):
    cue_words=tokens(cue_text)
    model_words=segment["word_candidates"]
    asr_words=[tokens(w["word"]) for w in model_words]
    if any(len(w)!=1 for w in asr_words):
        # Rare malformed tokenization is an unresolved candidate, never collapsed.
        return [],cue_words
    asr_words=[w[0] for w in asr_words]
    matcher=SequenceMatcher(None,cue_words,asr_words,autojunk=False)
    anchors=[]
    matched=set()
    for block in matcher.get_matching_blocks():
        for offset in range(block.size):
            i,j=block.a+offset,block.b+offset
            word=model_words[j]
            if not isinstance(word.get("start_ms"),int) or not isinstance(word.get("end_ms"),int):
                continue
            if word["end_ms"]<=word["start_ms"]:continue
            if not 60000<=word["start_ms"]<90000 or word["end_ms"]>90000:
                continue
            anchors.append({
                "source_caption_word_index":i,"source_word":cue_words[i],
                "asr_word_index":j,"proposed_audio_interval_ms":[word["start_ms"],word["end_ms"]],
                "model_word_probability":word["model_probability"],
                "status":"text-exact-ASR-time-candidate_not_forced_alignment",
                "review_priority":"low_probability" if word["model_probability"]<0.65 else "standard"
            })
            matched.add(i)
    return anchors,[w for i,w in enumerate(cue_words) if i not in matched]

def build():
    original=SOURCE/"original.srt"
    if hashlib.sha256(original.read_bytes()).hexdigest()!=ORIGINAL_SHA:
        raise ValueError("Original SRT mismatch")
    data=json.loads((OBS/"asr-prosody-hypotheses.json").read_text("utf-8"))
    if (data["source_media_sha256"]!=MEDIA_SHA or
        data["dialogue_source_sha256"]!=ORIGINAL_SHA or
        data["source_window_ms"]!=[60000,90000] or
        data["asr_model"]!="tiny.en" or not data["asr_hypothesis_only"]):
        raise ValueError("Unrecognized source ASR/edition; abort")
    rows=[json.loads(x) for x in (SOURCE/"segments.jsonl").read_text("utf-8").splitlines() if x.strip()]
    selected=[x for x in rows if x["end_ms"]>60000 and x["start_ms"]<90000]
    if len(selected)!=9 or {x["cue"] for x in selected}!=set(range(19,28)):
        raise ValueError("Expected nine source cue IDs")
    mapping={}
    segment_to_cue={}
    for x in data["alignment_candidates"]:
        idx=x["asr_segment_index"];cue=x["candidate_caption_cue"]
        if idx in segment_to_cue or idx<0 or idx>=len(data["asr_segments"]) or cue not in range(19,28):
            raise ValueError("Invalid ASR segment correspondence")
        segment_to_cue[idx]=cue
        mapping.setdefault(cue,[]).append(x)
    results=[]
    for row in selected:
        cue=row["cue"]
        proposed=mapping.get(cue,[])
        entries=turns(row["text"])
        candidates=[]
        for x in proposed:
            seg=data["asr_segments"][x["asr_segment_index"]]
            for turn in entries:
                v=SequenceMatcher(None,tokens(turn["text"]),tokens(seg["text"]),autojunk=False).ratio()
                candidates.append((v,x["asr_segment_index"],turn["source_turn_index"]))
        # Resolve per-turn/per-segment one-to-one assignment, highest lexical similarity first.
        used_segs=set();used_turns=set()
        for similarity,seg_i,turn_i in sorted(candidates,reverse=True):
            if similarity<0.45 or seg_i in used_segs or turn_i in used_turns:continue
            used_segs.add(seg_i);used_turns.add(turn_i)
            turn=entries[turn_i]
            seg=data["asr_segments"][seg_i]
            anchors,unmatched=word_matches(turn["text"],seg)
            turn.update({
                "speaker_identity":None,
                "asr_segment_index":seg_i,
                "lexical_similarity":round(similarity,4),
                "exact_word_time_candidates":anchors,
                "unanchored_caption_words":unmatched,
                "candidate_alignment_status":"partial_model_alignment_requires_listening",
                "asr_text_divergence_review":similarity<0.85,
            })
        for turn in entries:
            if "speaker_identity" not in turn:turn["speaker_identity"]=None
            if "asr_segment_index" not in turn:
                turn.update({"asr_segment_index":None,
                             "exact_word_time_candidates":[],
                             "unanchored_caption_words":tokens(turn["text"]),
                             "candidate_alignment_status":"no_reliable_ASR_turn_match"})
        results.append({
            "cue":cue,"original_caption_interval_ms":[row["start_ms"],row["end_ms"]],
            "source_cue_text":row["text"],"source_turns":entries,
            "unassigned_asr_segments":[x["asr_segment_index"] for x in proposed
                                       if x["asr_segment_index"] not in used_segs],
            "caption_boundary_status":"source_SRT_unverified_against_this_video",
            "first_utterance_may_precede_window":row["start_ms"]<60000,
            "last_utterance_may_follow_window":row["end_ms"]>90000
        })
    if len(data["asr_segments"])!=len(segment_to_cue):
        raise ValueError("Some model segments lack a source cue proposal")
    strong=[x["suggested_offset_ms"] for x in data["alignment_candidates"]
            if x["text_similarity_heuristic"]>=0.95 and x["asr_segment_index"]!=0]
    # Difference between model segment and caption START is not a validated sync offset.
    output={
        "schema":"night-court-source-caption-asr-word-review/1",
        "episode_id":"S01E01","media_sha256":MEDIA_SHA,
        "caption_sha256":ORIGINAL_SHA,"caption_edition":EDITION,
        "asr_model":"faster-whisper tiny.en","source_asr_evidence":"scene-review-v1/asr-prosody-hypotheses.json",
        "source_window_ms":[60000,90000],
        "source_caption_cues":len(results),"asr_segments":len(data["asr_segments"]),
        "cue_turn_packets":results,
        "strong_segment_start_difference_ms":{
            "count":len(strong),"median":median(strong) if strong else None,
            "meaning":"descriptive start-boundary differences only; NOT a global sync correction"
        },
        "review_notes":[
           "Cue C19 begins before the extracted 60-second audio; its first voice cannot be independently verified here.",
           "Cue C22 has two hyphen-separated speech turns, including a deliberately unusual word that tiny.en misrecognizes; retain source spelling and manually review.",
           "Cue C24's unusual vocabulary and potential grammar mismatch require listening, not automatic subtitle replacement.",
           "Cue C27 extends beyond 90 seconds; model speech is truncated at window boundary.",
           "Word starts/ends come from tiny.en hypotheses, not a forced aligner. Zero-length and out-of-range word estimates are discarded.",
           "Words not exactly recognized are explicitly unanchored; never interpolate them or infer performer/speaker identities."
        ],
        "verified_source_video_speech_alignment":False,
        "verified_word_alignment":False,
        "verified_speaker_identity":False,
        "verified_edition_complete":False,
        "raw_caption_modified":False
    }
    return output

def render(output):
    out=["# S01E01 01:00–01:30 | word-evidence review",
         "","**Candidate word timings only.** No source-cue offsets or speaker identities certified.",
         "","Source video SHA: \`"+MEDIA_SHA+"\`",
         "Original SRT SHA: \`"+ORIGINAL_SHA+"\`",""]
    for cue in output["cue_turn_packets"]:
        out.append(f'## Caption C{cue["cue"]:04d} ({cue["original_caption_interval_ms"][0]/1000:.3f}–{cue["original_caption_interval_ms"][1]/1000:.3f}s)')
        for turn in cue["source_turns"]:
            out.append(f'**Voice unknown, turn {turn["source_turn_index"]+1}:** {turn["text"]}')
            out.append(f'ASR link: {turn.get("asr_segment_index")}; candidate exact timed tokens: {len(turn["exact_word_time_candidates"])}; unresolved tokens: {", ".join(turn["unanchored_caption_words"]) or "none"}')
            out.append("")
    out.extend(["## Review gates",
      "Verify actual dialogue against audio, resolve which voice said each turn,",
      "listen to unusual vocabulary, and check earliest/latest boundary truncation.",
      "No physical action or emotion is inferred from this text-based alignment.",
      ""])
    return "\n".join(out)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,default=OBS)
    a=p.parse_args()
    if not a.output_dir.is_dir():raise ValueError("Output directory must already exist")
    doc=build()
    (a.output_dir/"word-alignment-review.json").write_text(
        json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (a.output_dir/"word-alignment-review.md").write_text(render(doc),encoding="utf-8")
    print("S01E01 source-grounded word anchors produced:",
        sum(len(t["exact_word_time_candidates"]) for c in doc["cue_turn_packets"] for t in c["source_turns"]),
        "review-only matches; all speaker/edition flags unresolved")

if __name__=="__main__":main()
