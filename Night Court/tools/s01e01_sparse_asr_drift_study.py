#!/usr/bin/env python3
"""Source-edition drift sampling across S01E01, never full transcript certification.

Five disjoint 30s windows are independently transcribed with tiny.en.
Matching to the existing SRT only yields candidates for human verification.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, tempfile
from difflib import SequenceMatcher
from pathlib import Path
from statistics import median
from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate,retrieve

ROOT=Path(__file__).resolve().parents[1]
SRT_DIR=ROOT/"seasons"/"S01"/"S01E01"/"dialogue"/"versions"/"s01-internal-dvdrip-xvid-sprinter-english--aa9f77600cd9f2b6"
VIDEO_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
SRT_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
WINDOWS=((300,330),(600,630),(900,930),(1200,1230),(1350,1380))
CUT_DURATION_MS=1448256

def norm(s):
    return re.sub(r"\s+"," ",re.sub("[^a-z0-9 ]"," ",s.casefold())).strip()

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def caption_candidates(cues,start,end):
    a,b=start*1000,end*1000
    return [x for x in cues if x["end_ms"]>a and x["start_ms"]<b]

def match(asr_source,cues,start,end):
    if not cues:return None
    text=norm(asr_source["text"])
    if len(text)<2:return None
    score,cue=max(((SequenceMatcher(None,text,norm(x["text"]),autojunk=False).ratio(),x)
                   for x in cues),key=lambda pair:pair[0])
    contained=start*1000<=cue["start_ms"]<cue["end_ms"]<=end*1000
    return {
      "asr_segment_index":asr_source["index"],
      "source_caption_cue":cue["cue"] if score>=.35 else None,
      "source_cue_interval_ms":[cue["start_ms"],cue["end_ms"]],
      "lexical_similarity":round(score,4),
      "candidate_start_offset_ms":asr_source["start_ms"]-cue["start_ms"] if score>=.55 else None,
      "cue_fully_inside_window":contained,
      "usable_for_global_drift_review":bool(score>=.85 and contained
         and not asr_source.get("segment_boundary_clipped",False)
         and asr_source["end_ms"]>asr_source["start_ms"]+400),
      "review_state":"heuristic_text_match_not_verified_audio",
      "caution":"Caption cue and model segment boundaries can refer to different sub-utterances."
    }

def compare_windows(windows):
    medians=[]
    for w in windows:
        offsets=[x["candidate_start_offset_ms"] for x in w["alignment_candidates"]
                 if x and x["usable_for_global_drift_review"] and x["candidate_start_offset_ms"] is not None]
        w["strong_lexical_anchor_count"]=len(offsets)
        w["strong_lexical_start_delta_median_ms"]=median(offsets) if offsets else None
        if len(offsets)>=2:
            medians.append((w["source_window_ms"][0],median(offsets)))
    span=(max(x[1] for x in medians)-min(x[1] for x in medians)) if len(medians)>=2 else None
    return {
       "qualified_windows_with_2plus_lexical_anchors":len(medians),
       "spread_between_window_median_start_differences_ms":span,
       "interpretation":"qualifying source-cue vs tiny.en segment START difference only, not exact offset/drift",
       "global_video_to_subtitle_offset_verified":False,
       "global_drift_verified":False}

def sources():
    if sha(SRT_DIR/"original.srt")!=SRT_SHA:
        raise ValueError("Original owner SRT witness changed")
    cues=[json.loads(s) for s in (SRT_DIR/"segments.jsonl").read_text("utf-8").splitlines() if s.strip()]
    if len(cues)!=336 or [x["cue"] for x in cues]!=list(range(1,337)):
        raise ValueError("Unknown original caption source or missing cues")
    return cues

def run(media,destination):
    if destination.exists():raise ValueError("Refuse output overwrite")
    if sha(media)!=VIDEO_SHA:raise ValueError("Only the prior SHA-accepted S01E01 AVI is allowed")
    cues=sources()
    import importlib.metadata
    from faster_whisper import WhisperModel
    records=[]
    with tempfile.TemporaryDirectory(prefix="night-court-drift-pilot-") as tmp:
        model=WhisperModel("tiny.en",device="cpu",compute_type="int8",
            download_root=str(Path(tmp)/"model-cache"))
        for index,(start,end) in enumerate(WINDOWS):
            if end-start!=30 or end*1000>=CUT_DURATION_MS:
                raise ValueError("Invalid original S01E01 sampling schedule")
            wav=Path(tmp)/f"source-{start}-{end}.wav"
            subprocess.run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error",
              "-ss",str(start),"-i",str(media),"-t","30","-map","0:a:0",
              "-vn","-ac","1","-ar","16000","-c:a","pcm_s16le","-y",str(wav)],
              check=True,timeout=90,capture_output=True)
            import wave
            with wave.open(str(wav),"rb") as aud:
                dur=aud.getnframes()/aud.getframerate()
            if not 29.90<=dur<=30.05:
                raise ValueError("Invalid source sample duration")
            audio_sha=sha(wav)
            found,info=model.transcribe(str(wav),language="en",beam_size=3,
              vad_filter=False,word_timestamps=False,
              condition_on_previous_text=False)
            texts=[]
            for ix,x in enumerate(found):
                raw_start=round(start*1000+x.start*1000)
                raw_end=round(start*1000+x.end*1000)
                abs_start=max(start*1000,raw_start)
                abs_end=min(end*1000,raw_end)
                # Whisper may estimate speech beyond an excerpt even though no
                # such samples were decoded. Preserve a bounded candidate and
                # disqualify it from drift statistics rather than inventing audio.
                if raw_end<=raw_start or abs_start>=abs_end:
                    continue
                clipped=(raw_start<start*1000 or raw_end>end*1000)
                texts.append({
                   "index":len(texts),"start_ms":abs_start,"end_ms":abs_end,
                   "segment_boundary_clipped":clipped,
                   "model_proposed_end_ms_before_clamping":raw_end,
                   "text":x.text.strip(),"model_average_log_probability":round(float(x.avg_logprob),4),
                   "model_no_speech_probability":round(float(x.no_speech_prob),4)
                })
            wav.unlink()
            visible=caption_candidates(cues,start,end)
            align=[match(a,visible,start,end) for a in texts]
            records.append({
               "source_window_ms":[start*1000,end*1000],
               "source_audio_sha256":audio_sha,
               "expected_source_caption_cues":[x["cue"] for x in visible],
               "source_cues_in_window":len(visible),"asr_segments":texts,
               "alignment_candidates":align,
               "source_caption_alignment_status":"unverified_candidate_only",
               "scene_and_speaker_identity_verified":False
            })
    statistical=compare_windows(records)
    out={
       "schema":"night-court-s01e01-multisite-asr-drift/1",
       "episode_id":"S01E01","original_media_sha256":VIDEO_SHA,
       "original_caption_sha256":SRT_SHA,
       "source_video_duration_ms":CUT_DURATION_MS,
       "windows":records,"drift_hypothesis_summary":statistical,
       "ASR_model":"faster-whisper tiny.en",
       "faster_whisper_version":importlib.metadata.version("faster-whisper"),
       "ASR_is_independent_transcription_not_source_truth":True,
       "original_caption_times_independently_verified":False,
       "source_edition_audio_sync_verified":False,
       "audiovisual_episode_completeness_verified":False,
       "identifiable_speakers_or_expressive_emotions_claimed":False,
       "media_wav_and_model_weights_retained":False,
       "quality_limits":[
          "Sparse five-by-thirty-second sampling does not measure all intervening episode minutes",
          "Cue-start vs utterance-start differences are not a calibrated offset",
          "Simultaneous dialog and multi-line captions affect lexical match and apparent timing",
          "Unmatched windows must be reviewed, not removed from the source corpus",
          "A source cut can be temporally well aligned yet incomplete or incorrectly identified"]
    }
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n","utf-8")
    print("S01E01 drift samples finished: 5 fixed windows, "+
          str(sum(len(x["asr_segments"]) for x in records))+
          " independent ASR segments; zero globally verified offsets")

def ftp_source(destination):
    import ftplib
    with tempfile.TemporaryDirectory(prefix="nc-s01e01-sync-") as tmp:
        item=candidate()
        media=Path(tmp)/item["basename"]
        pwd=os.getenv("FTP_PASSWORD")
        if not pwd:raise ValueError("Existing owner FTP_PASSWORD missing")
        ftp=connect(os.getenv("FTP_HOST","wood.seedhost.eu"),
           os.getenv("FTP_USER","ianseeds"),pwd,"ftp")
        try:received=retrieve(ftp,item,media)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        if received!=VIDEO_SHA:raise ValueError("AVI no longer matches known source hash")
        run(media,destination)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ftp",action="store_true")
    ap.add_argument("--media",type=Path)
    ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args()
    if a.ftp==bool(a.media):ap.error("Choose --ftp or --media, not both")
    if a.ftp:ftp_source(a.output)
    else:run(a.media,a.output)
if __name__=="__main__":main()
