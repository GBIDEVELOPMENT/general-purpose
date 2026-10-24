#!/usr/bin/env python3
"""Original-caption-constrained CTC acoustic timing candidates for S01E01.

Input video is the sole owner-approved SHA-verified source AVI. The processor
must abstain for incomplete/crossing turns. Character identity and source-cut
sync are never certified by a model's forced alignment.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from ctc_source_aligner import align_words, normalize_words
from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate, retrieve

ROOT=Path(__file__).resolve().parents[1]
OBS=ROOT/"seasons"/"S01"/"S01E01"/"derived"/"scene-review-v1"
MEDIA_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
CAPTION_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
MODEL="facebook/wav2vec2-base-960h"
START=60000
END=90000

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def source_turns():
    review=json.loads((OBS/"word-alignment-review.json").read_text("utf-8"))
    asr=json.loads((OBS/"asr-prosody-hypotheses.json").read_text("utf-8"))
    if (review["media_sha256"]!=MEDIA_SHA or
        review["caption_sha256"]!=CAPTION_SHA or
        asr["source_media_sha256"]!=MEDIA_SHA or
        asr["dialogue_source_sha256"]!=CAPTION_SHA or
        review["source_window_ms"]!=[START,END]):
        raise ValueError("Unrecognized source media, subtitle or ASR evidence")
    segments=asr["asr_segments"]
    chosen=[]
    for cue in review["cue_turn_packets"]:
        for turn in cue["source_turns"]:
            ix=turn.get("asr_segment_index")
            if ix is None:
                chosen.append({"cue":cue["cue"],"source_turn_index":turn["source_turn_index"],
                    "text":turn["text"],"status":"abstain_no_source_ASR_turn",
                    "proposed_words":[]})
                continue
            if not 0<=ix<len(segments):raise ValueError("Invalid original ASR interval index")
            seg=segments[ix]
            if seg["start_ms"]<START or seg["end_ms"]>END or seg["end_ms"]-seg["start_ms"]<400:
                chosen.append({"cue":cue["cue"],"source_turn_index":turn["source_turn_index"],
                    "text":turn["text"],"asr_segment_index":ix,
                    "status":"abstain_excerpt_boundary_or_too_short",
                    "proposed_words":[]})
                continue
            # Source cue C27 runs past the 90s excerpt, and the independent
            # tiny.en ASR is itself truncated: no false full-utterance alignment.
            if cue["original_caption_interval_ms"][1]>END:
                chosen.append({"cue":cue["cue"],"source_turn_index":turn["source_turn_index"],
                    "text":turn["text"],"asr_segment_index":ix,
                    "status":"abstain_source_caption_outside_audio_window",
                    "proposed_words":[]})
                continue
            chosen.append({"cue":cue["cue"],"source_turn_index":turn["source_turn_index"],
                "text":turn["text"],"asr_segment_index":ix,
                "segment_ms":[seg["start_ms"],seg["end_ms"]],
                "status":"pending_constrained_model"})
    return chosen

def calculate(video,output):
    if output.exists():raise ValueError("Refuse evidence overwrite")
    if digest(video)!=MEDIA_SHA:raise ValueError("Only existing immutable S01E01 AVI is permitted")
    # Model dependencies are heavy; import only after source is validated.
    import torch
    import soundfile as sf
    import numpy as np
    import transformers
    from transformers import AutoProcessor,AutoModelForCTC
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY","1")
    torch.set_num_threads(2)
    processor=AutoProcessor.from_pretrained(MODEL,trust_remote_code=False)
    model=AutoModelForCTC.from_pretrained(MODEL,use_safetensors=True,trust_remote_code=False)
    model.eval()
    vocabulary=processor.tokenizer.get_vocab()
    blank=processor.tokenizer.pad_token_id
    if blank is None or "|" not in vocabulary or any(chr(k) not in vocabulary for k in range(65,91)):
        raise ValueError("Unexpected English uppercase CTC model tokenizer")
    revision=getattr(model.config,"_commit_hash",None)
    if not revision:
        raise ValueError("Model weight revision could not be recorded")
    with tempfile.TemporaryDirectory(prefix="nc-ctc-mono-") as tmp:
        wav=Path(tmp)/"wav.wav"
        subprocess.run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error",
           "-ss","60","-i",str(video),"-t","30","-map","0:a:0",
           "-vn","-ac","1","-ar","16000","-c:a","pcm_s16le",
           "-y",str(wav)],check=True,capture_output=True,timeout=90)
        samples,sr=sf.read(str(wav),dtype="float32")
        if sr!=16000 or not 29.9<=len(samples)/sr<=30.05:
            raise ValueError("Unexpected source decoded PCM duration")
        wavsha=digest(wav)
        results=[]
        for turn in source_turns():
            if turn["status"]!="pending_constrained_model":
                results.append(turn)
                continue
            a,b=turn["segment_ms"]
            chunk_start=max(START,a-350)
            chunk_end=min(END,b+350)
            chunk=samples[round((chunk_start-START)*sr/1000):
                          round((chunk_end-START)*sr/1000)]
            if not 0.5<=len(chunk)/sr<=5:
                turn["status"]="abstain_audio_window_invalid"
                results.append(turn)
                continue
            inputs=processor(chunk,sampling_rate=sr,return_tensors="pt")
            with torch.inference_mode():
                emission=model(inputs.input_values).logits.log_softmax(-1)[0].cpu().numpy()
            frame_ms=(len(chunk)/sr*1000)/emission.shape[0]
            turn["ctc_processing_window_ms"]=[chunk_start,chunk_end]
            try:
                match=align_words(emission,turn["text"],vocabulary,blank,
                                   absolute_start_ms=chunk_start,frame_step_ms=frame_ms,
                                   min_confidence=0.30)
                turn["status"]="candidate_ctc_forced_alignment_not_audio_verified"
                turn["proposed_words"]=match["words"]
                turn["candidate_ctc_mean_log_probability"]=match["ctc_path_average_log_probability"]
                turn["candidate_alignment_abstentions"]=match["abstentions"]
                turn["lexical_transcript"]=[str(x) for x in normalize_words(turn["text"])]
            except ValueError as exc:
                turn["status"]="abstain_alignment_infeasible"
                turn["abstention_reason"]=str(exc)
                turn["proposed_words"]=[]
            results.append(turn)
    out={
      "schema":"night-court-ctc-source-constrained-words/1",
      "episode_id":"S01E01","source_media_sha256":MEDIA_SHA,
      "source_caption_sha256":CAPTION_SHA,"source_pcm_sha256":wavsha,
      "source_window_ms":[START,END],
      "ctc_model":MODEL,"model_revision_sha":revision,
      "tools":{"torch":torch.__version__,"transformers":transformers.__version__,
               "numpy":np.__version__,"soundfile":sf.__version__},
      "source_turns":results,
      "aligner":"original_source_text_constrained_CTC_Viterbi_with_abstention",
      "model_audio_window_complete":False,
      "model_predictions_are_verified_word_alignment":False,
      "source_caption_offset_and_drift_verified":False,
      "actor_identity_verified":False,
      "acting_emotion_verified":False,
      "finished_screenplay_verified":False,
      "raw_episode_media_or_audio_in_artifact":False,
      "limitations":["CTC_alignment_can_force_incorrect_text_onto_acoustic_frames",
                     "sitcom_music_and_laughter_are_present_in_mix",
                     "rare_comic_vocabulary_and_unmatched_cues_require_manual_review",
                     "model_segment_boundaries_are_tiny_en_hypotheses",
                     "only_60_to_90s_original_episode_excerpt_was_processed"]
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("CTC generated",sum(t["status"].startswith("candidate_") for t in results),
          "cautious source text turn-alignment candidates; all speech/voice verification remains open")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--media",type=Path)
    parser.add_argument("--ftp",action="store_true")
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    if a.ftp==bool(a.media):parser.error("Choose exactly one of --ftp or --media")
    if a.ftp:
        item=candidate()
        pwd=os.getenv("FTP_PASSWORD")
        if not pwd:raise ValueError("Existing FTP_PASSWORD is required")
        import ftplib
        with tempfile.TemporaryDirectory(prefix="nc-source-ctc-") as tmp:
            media=Path(tmp)/item["basename"]
            ftp=connect(os.getenv("FTP_HOST","wood.seedhost.eu"),
                        os.getenv("FTP_USER","ianseeds"),pwd,"ftp")
            try:downloadsha=retrieve(ftp,item,media)
            finally:
                try:ftp.quit()
                except ftplib.all_errors:ftp.close()
            if downloadsha!=MEDIA_SHA:raise ValueError("Source FTP content drifted")
            calculate(media,a.output)
    else:
        calculate(a.media,a.output)

if __name__=="__main__":main()
