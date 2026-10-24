#!/usr/bin/env python3
"""Conservative anonymous speaker-embedding similarity from S01E01 TV audio.

Embeddings exist only in ephemeral runner memory. No voiceprint, media, model
weights, character identity, diarization decision, or emotion is exported.
"""
from __future__ import annotations
from itertools import combinations
import argparse,ftplib,hashlib,json,math,os,subprocess,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"seasons"/"S01"/"S01E01"/"derived"/"scene-review-v1"/"asr-prosody-hypotheses.json"
MEDIA_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
CAPTION_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
MODEL="speechbrain/spkrec-ecapa-voxceleb"
MIN_LENGTH_MS=850

def sha(path):
    digest=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):digest.update(chunk)
    return digest.hexdigest()

def source_segments():
    j=json.loads(SOURCE.read_text("utf-8"))
    if (j["source_media_sha256"]!=MEDIA_SHA or
        j["dialogue_source_sha256"]!=CAPTION_SHA or
        j["source_window_ms"]!=[60000,90000] or
        j["asr_model"]!="tiny.en" or
        not j["asr_hypothesis_only"] or len(j["asr_segments"])!=10):
        raise ValueError("Changed media, source caption or independent ASR")
    segments=j["asr_segments"]
    for i,x in enumerate(segments):
        if (x["index"]!=i or
            not 60000<=x["start_ms"]<x["end_ms"]<=90000):
            raise ValueError("Invalid source ASR segment bounds")
    return segments

def cosines(vectors):
    """Return all pairwise normalized cosines, without voice IDs or clusters."""
    import numpy as np
    clean={}
    for index,v in vectors.items():
        if not isinstance(index,int) or index<0:
            raise ValueError("Invalid original source ASR index")
        z=np.asarray(v,dtype=np.float64).reshape(-1)
        if z.size<2 or not np.all(np.isfinite(z)):
            raise ValueError("Missing or invalid speaker embeddings")
        norm=float(np.linalg.norm(z))
        if norm<1e-8:raise ValueError("Zero embedding cannot identify vocal similarity")
        clean[index]=z/norm
    if len({x.shape[0] for x in clean.values()})>1:
        raise ValueError("Speaker feature dimension mismatch")
    return [{
      "asr_segment_a":i,"asr_segment_b":j,
      "anonymous_cosine_similarity_unreviewed":round(float(np.clip(clean[i]@clean[j],-1,1)),5),
      "same_speaker_conclusion":None,
      "model_probability_calibrated":False
    } for i,j in combinations(sorted(clean),2)]

def process(media,output):
    if output.exists():raise ValueError("Do not overwrite evidence edition")
    if sha(media)!=MEDIA_SHA:raise ValueError("Wrong original source AVI fingerprint")
    segments=source_segments()
    import numpy as np
    import soundfile as sf
    import torch
    import speechbrain
    from huggingface_hub import HfApi,snapshot_download
    from speechbrain.inference.speaker import EncoderClassifier

    torch.set_num_threads(2)
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY","1")
    # Resolve and freeze a model revision for this single, owner-authorized run.
    revision=HfApi().model_info(MODEL).sha
    if not isinstance(revision,str) or len(revision)!=40:
        raise ValueError("Cannot pin model commit for provenance")
    with tempfile.TemporaryDirectory(prefix="nc-voice-embedding-") as tmp:
        model_folder=snapshot_download(repo_id=MODEL,revision=revision,
                 cache_dir=str(Path(tmp)/"model-cache"))
        classifier=EncoderClassifier.from_hparams(
            source=model_folder,
            savedir=str(Path(tmp)/"speechbrain-run"),
            run_opts={"device":"cpu"})
        wav=Path(tmp)/"audio.wav"
        subprocess.run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error",
           "-ss","60","-i",str(media),"-t","30","-map","0:a:0",
           "-vn","-ac","1","-ar","16000","-c:a","pcm_s16le",
           "-y",str(wav)],check=True,capture_output=True,timeout=90)
        audio,rate=sf.read(str(wav),dtype="float32")
        if rate!=16000 or not 29.9<=len(audio)/rate<=30.05:
            raise ValueError("Unexpected original 30-second audio excerpt")
        pcm_sha=sha(wav)
        vectors={}
        dispositions=[]
        with torch.inference_mode():
            for seg in segments:
                idx=seg["index"]
                duration=seg["end_ms"]-seg["start_ms"]
                note={"asr_segment_index":idx,
                      "source_interval_ms":[seg["start_ms"],seg["end_ms"]],
                      "source_voice_identity":None,
                      "embedding_retained":False,
                      "speaker_isolation_verified":False}
                if duration<MIN_LENGTH_MS:
                    note["status"]="abstain_short_ASR_segment"
                else:
                    start=round((seg["start_ms"]-60000)*rate/1000)
                    end=round((seg["end_ms"]-60000)*rate/1000)
                    chunk=audio[start:end]
                    rms=float(np.sqrt(np.mean(chunk**2)))
                    if rms<0.008:
                        note["status"]="abstain_near_silence"
                    else:
                        embedding=classifier.encode_batch(
                            torch.tensor(chunk,dtype=torch.float32).unsqueeze(0))
                        vectors[idx]=embedding.cpu().numpy().reshape(-1)
                        note["status"]="anonymous_embedding_computed_not_speech_or_speaker_verified"
                        note["mixed_audio_rms_dbfs"]=round(20*math.log10(rms),2)
                dispositions.append(note)
        sims=cosines(vectors)
    out={
       "schema":"night-court-s01e01-anonymous-voice-similarity/1",
       "episode_id":"S01E01","source_media_sha256":MEDIA_SHA,
       "source_caption_sha256":CAPTION_SHA,
       "source_pcm_sha256":pcm_sha,"source_audio_window_ms":[60000,90000],
       "candidate_ASR_speech_segments":len(segments),
       "model":MODEL,"model_revision_sha":revision,
       "model_license":"Apache-2.0 per publisher model card",
       "software_versions":{"torch":torch.__version__,
                            "speechbrain":speechbrain.__version__,
                            "soundfile":sf.__version__},
       "source_voice_intervals":dispositions,
       "anonymous_pairs":sims,
       "raw_voice_embeddings_retained":False,
       "speaker_clusters_assigned":False,
       "speaker_identities_assigned":False,
       "same_speaker_pairs_verified":False,
       "voice_biometrics_or_source_media_in_artifact":False,
       "emotion_and_delivery_inferred":False,
       "limitations":["source_ASR_intervals_not_verified_speaker_turns",
                       "audience_laughter_music_and_overlaps_can_dominate_utterance_embedding",
                       "ECAPA_score_not_calibrated_for_original_sitcom_mix",
                       "no_name_or_visual_identity_from_embedding",
                       "short_source_ASR_intervals_abstain_without_padded_voice_guess"],
       "review_status":"anonymous_acoustic_similarity_hypotheses_only"
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(out,indent=2)+"\n","utf-8")
    print("Anonymous original voice-similarity evidence:",len(vectors),
          "candidate segments,",len(sims),"unreviewed pairs; no model embedding/audio retained")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--media",type=Path)
    p.add_argument("--ftp",action="store_true")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.ftp==bool(a.media):p.error("Choose exactly one of --ftp or --media")
    if a.ftp:
        from ftp_research_intake import connect
        from pilot_ftp_video_acoustics import candidate,retrieve
        item=candidate()
        password=os.getenv("FTP_PASSWORD")
        if not password:raise ValueError("Existing FTP_PASSWORD required")
        with tempfile.TemporaryDirectory(prefix="nc-anonymous-voice-") as t:
            media=Path(t)/item["basename"]
            ftp=connect(os.getenv("FTP_HOST","wood.seedhost.eu"),
              os.getenv("FTP_USER","ianseeds"),password,"ftp")
            try:verified_sha=retrieve(ftp,item,media)
            finally:
                try:ftp.quit()
                except ftplib.all_errors:ftp.close()
            if verified_sha!=MEDIA_SHA:raise ValueError("Source FTP bytes changed")
            process(media,a.output)
    else:process(a.media,a.output)

if __name__=="__main__":main()
