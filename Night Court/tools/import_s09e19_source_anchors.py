#!/usr/bin/env python3
"""Import source-faithful S09E19 video/untimed-text review candidates only.

The exact original 347 paragraphs must remain unaltered and untimed. Source
matches merely prioritize listening and further review.
"""
from __future__ import annotations
import hashlib,json,re,shutil,sys
from pathlib import Path
from match_s09e19_untimed_paragraphs import score_windows
from s09e19_untimed_video_anchor_pilot import WINDOWS,TXT_SHA,sources,SCHEMA

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"seasons"/"S09"/"S09E19"/"derived"/"source-timing-review-v1"
EXPECTED_BYTES=183377920
MAX_BYTES=400_000
HEX=re.compile(r"^[0-9a-f]{64}$")

def validate(path):
    if not path.is_file() or not 100<path.stat().st_size<=MAX_BYTES:
        raise ValueError("Missing or unbounded original source evidence JSON")
    j=json.loads(path.read_text("utf-8"))
    if not (j.get("schema")==SCHEMA and j.get("episode_id")=="S09E19"
        and j.get("source_video_size_bytes")==EXPECTED_BYTES
        and isinstance(j.get("source_duration_seconds"),(int,float))
        and 1320<=j["source_duration_seconds"]<=1800
        and HEX.fullmatch(str(j.get("source_video_sha256","")))
        and j.get("original_untimed_transcript_sha256")==TXT_SHA
        and j.get("original_paragraphs")==347
        and j.get("model")=="faster-whisper tiny.en"
        and j.get("original_source_cue_times_introduced") is False
        and j.get("original_transcript_modified") is False
        and j.get("all_347_paragraphs_time_aligned") is False
        and j.get("source_edition_audiovisually_verified") is False
        and j.get("words_speaker_and_emotion_verified") is False
        and j.get("all_audio_or_video_complete") is False
        and j.get("raw_source_media_wav_or_model_weights_retained_in_artifact") is False):
        raise ValueError("Cannot accept an unpinned or overclaiming S09E19 source review")
    windows=j.get("windows",[])
    if len(windows)!=len(WINDOWS):raise ValueError("Five original sparse samples missing")
    paragraphs=sources()
    for w,(a,b) in zip(windows,WINDOWS):
        if w.get("source_window_ms")!=[a*1000,b*1000]:
            raise ValueError("Source sample time differs from plan")
        if not HEX.fullmatch(str(w.get("source_audio_sha256",""))):
            raise ValueError("Audio SHA missing")
        segments=w.get("asr_segments",[])
        for i,s in enumerate(segments):
            if (s["index"]!=i or
                not a*1000<=s["start_ms"]<s["end_ms"]<=b*1000 or
                len(s["text"])>1200 or not isinstance(s["text"],str)
                or not isinstance(s["segment_boundary_clipped"],bool)):
                raise ValueError("Unbounded, reordered or malformed acoustic proposals")
    # Recompute all paragraph/word matches from the current immutable source.
    raw=[{"source_window_ms":w["source_window_ms"],
          "source_audio_sha256":w["source_audio_sha256"],
          "asr_segments":w["asr_segments"]} for w in windows]
    confirmed=score_windows(raw,paragraphs)
    if confirmed!=windows:
        raise ValueError("ASR text/paragraph alignment changed since trusted source processing")
    total=sum(w["distinct_high_lexical_match_candidates"] for w in windows)
    segs=sum(len(w["asr_segments"]) for w in windows)
    ids=[m["source_paragraph_candidate"]["first"] for w in windows
         for m in w["text_alignment_candidates"] if m["source_paragraph_candidate"]]
    monotonic=all(x<y for x,y in zip(ids,ids[1:]))
    if (j.get("distinct_high_lexical_match_candidates_total")!=total
        or j.get("segments_reviewed")!=segs
        or j.get("candidate_paragraphs_monotonic_across_windows")!=monotonic):
        raise ValueError("Source paragraph counts/order reconciliation failed")
    if any(x["start_ms"] is not None or x["end_ms"] is not None for x in paragraphs):
        raise ValueError("Original source timecodes were fabricated")
    return j

def write(source):
    if DEST.exists():raise ValueError("Refuse overwrite of previous S09E19 evidence")
    result=validate(source)
    DEST.mkdir(parents=True)
    shutil.copy2(source,DEST/"sparse-source-paragraph-candidates.json")
    lines=[
      "# S09E19 original untimed dialogue: first source-video timing review",
      "",
      "**Candidate anchors, not a subtitle SRT, dialogue correction, speaker map, or certified episode.**",
      f"Original AVI bytes: {result['source_video_size_bytes']}",
      f"Original video SHA-256: \u0060{result['source_video_sha256']}\u0060",
      f"Source duration: {result['source_duration_seconds']:.3f} seconds.",
      f"Immutable untimed source text SHA-256: \u0060{TXT_SHA}\u0060",
      f"Original displayed source paragraphs: {result['original_paragraphs']}; none given timecodes.",
      f"Independent {result['model']} ASR segments considered: {result['segments_reviewed']}.",
      f"Distinctive text-to-paragraph candidate matches: {result['distinct_high_lexical_match_candidates_total']}.",
      f"Proposed source-paragraph order monotonic: {result['candidate_paragraphs_monotonic_across_windows']} (not validation).",
      "",
      "| Video source excerpt | ASR segments | High lexical uniqueness candidates | Paragraph IDs proposed |",
      "|---|---:|---:|---|"
    ]
    for w in result["windows"]:
        a,b=w["source_window_ms"]
        pids=[f'{m["source_paragraph_candidate"]["first"]}–{m["source_paragraph_candidate"]["last"]}'
              for m in w["text_alignment_candidates"] if m["source_paragraph_candidate"]]
        lines.append(f'| {a/1000:.0f}–{b/1000:.0f}s | {len(w["asr_segments"])} | '
                     f'{w["distinct_high_lexical_match_candidates"]} | {", ".join(pids) or "none"} |')
    lines+=["",
      "## What remains unknown","",
      "Source AVI content and the original text are **not independently verified as episode complete**.",
      "Five sparse audio excerpts cannot establish full episode scene coverage, named speakers,",
      "vocal delivery, dialogue omissions, or paragraph-level original timestamps.",
      "The source text remains legally and technically distinct from verified timed captions.",
      "",
      "## Next acceptance",
      "",
      "Audition at least two distinct high-lexical candidates in the real AVI,",
      "confirm words/cut identity and refine source time anchors while preserving",
      "original untimed paragraphs. If no candidates exist, review the filename",
      "edition or speech model rather than inventing timings.",
      ""]
    (DEST/"sparse-source-paragraph-review.md").write_text("\n".join(lines),"utf-8")
    print("S09E19: source SHA validated",result["segments_reviewed"],
          "ASR segments,",result["distinct_high_lexical_match_candidates_total"],
          "candidate paragraph references; zero verified source timecodes")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: import_s09e19_source_anchors.py ARTIFACT_JSON")
    write(Path(sys.argv[1]))
