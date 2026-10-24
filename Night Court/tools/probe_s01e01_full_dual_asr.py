#!/usr/bin/env python3
"""One original episode / one PCM / two *free-decoding* independent ASR families.

Owner-only trusted-main runner. The original AVI, WAV and model weights are
ephemeral; the private output contains only small candidate text and timings.
No SRT is ever read by a decoder, and no dialogue or speaker is source-certified.
"""
from __future__ import annotations

import argparse
import ftplib
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import time
import urllib.request
import wave
import zipfile

from compare_independent_asr import compare
from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate, retrieve
from probe_s01e01_cadence_and_cost import SIZE, SHA

VOSK_ZIP_URL='https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip'
VOSK_ZIP_SHA256='30f26242c4eb449f948e42cb302dd7a686cb29a3423a8367f99ff41780942498'
VOSK_ROOT='vosk-model-small-en-us-0.15'
MAX_VOSK_ZIP=52_000_000
MAX_VOSK_UNPACKED=200_000_000
MAX_ASR_WORDS=15000
MAX_JSON_BYTES=5_000_000
MIN_EPISODE_MS=1_200_000
MAX_EPISODE_MS=1_800_000


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle,'sha256').hexdigest()


def download_pinned_model(destination:Path):
    if destination.exists():
        raise ValueError('Existing potentially untrusted model archive')
    size=0
    digest=hashlib.sha256()
    with urllib.request.urlopen(VOSK_ZIP_URL,timeout=50) as response, destination.open('xb') as output:
        while True:
            chunk=response.read(1024*1024)
            if not chunk:break
            size+=len(chunk)
            if size>MAX_VOSK_ZIP:
                raise ValueError('Vosk source model exceeds archive cap')
            digest.update(chunk)
            output.write(chunk)
    if digest.hexdigest()!=VOSK_ZIP_SHA256:
        raise ValueError('Official downloaded Vosk model SHA mismatch; do not use unpinned weights')
    return size


def unpack_pinned_model(archive:Path, out:Path):
    with zipfile.ZipFile(archive) as z:
        names=z.infolist()
        if len(names)>250 or sum(i.file_size for i in names)>MAX_VOSK_UNPACKED:
            raise ValueError('Oversized Vosk zip tree')
        for item in names:
            p=PurePosixPath(item.filename)
            unix_mode=(item.external_attr >> 16) & 0o170000
            if (p.is_absolute() or '..' in p.parts or not p.parts
                or p.parts[0]!=VOSK_ROOT or '\\' in item.filename
                or unix_mode==0o120000):
                raise ValueError('Unsafe Vosk ZIP path/symlink')
        out.mkdir()
        z.extractall(out)
    if not (out/VOSK_ROOT/'am').is_dir():
        raise ValueError('Wrong Vosk model root')
    return out/VOSK_ROOT


def decode_audio(video:Path,wav:Path):
    job=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error',
                        '-i',str(video),'-map','0:a:0','-vn','-ac','1',
                        '-ar','16000','-c:a','pcm_s16le',str(wav)],
                       capture_output=True,text=True,check=True,timeout=180)
    with wave.open(str(wav),'rb') as f:
        if f.getnchannels()!=1 or f.getframerate()!=16000 or f.getsampwidth()!=2:
            raise ValueError('Unexpected original source mono PCM encoding')
        duration_ms=round(f.getnframes()*1000/16000)
    if not MIN_EPISODE_MS<=duration_ms<=MAX_EPISODE_MS or wav.stat().st_size>60_000_000:
        raise ValueError('Whole-episode audio exceeds source-approved runtime/size')
    return duration_ms,sha(wav)


def preserve_word(text,a,b,duration_ms):
    if not isinstance(text,str) or not text.strip() or len(text)>80:
        return None
    a=round(a*1000)
    b=round(b*1000)
    if not 0<=a<b<=duration_ms:
        return None
    return {'text':text.strip(),'start_ms':a,'end_ms':b}


def vosk_free_decode(wav:Path,model_path:Path,duration_ms:int):
    import vosk
    vosk.SetLogLevel(-1)
    model=vosk.Model(str(model_path))
    engine=vosk.KaldiRecognizer(model,16000)
    engine.SetWords(True)
    words=[]
    rejected=0

    def add(response):
        nonlocal rejected
        for row in json.loads(response).get('result',[]):
            w=preserve_word(row.get('word'),row.get('start'),row.get('end'),duration_ms)
            if w is None:
                rejected+=1
                continue
            words.append(w)
            if len(words)>MAX_ASR_WORDS:
                raise ValueError('Vosk whole episode word count cap reached')

    with wave.open(str(wav),'rb') as inp:
        while True:
            frames=inp.readframes(8000)
            if not frames:break
            if engine.AcceptWaveform(frames):
                add(engine.Result())
        add(engine.FinalResult())
    return words,rejected


def whisper_free_decode(wav:Path,cache:Path,duration_ms:int):
    from faster_whisper import WhisperModel
    model=WhisperModel('tiny.en',device='cpu',compute_type='int8',
                       download_root=str(cache),cpu_threads=2,num_workers=1)
    iterator,info=model.transcribe(str(wav),language='en',beam_size=1,
                   word_timestamps=True,vad_filter=False,
                   condition_on_previous_text=False,temperature=0.0,
                   initial_prompt=None)
    words=[]
    rejected=0
    segments=0
    for seg in iterator:
        segments+=1
        if segments>1200:
            raise ValueError('Excessive original-episode model segments')
        for row in seg.words or ():
            w=preserve_word(row.word,row.start,row.end,duration_ms)
            if w is None:
                rejected+=1
                continue
            words.append(w)
            if len(words)>MAX_ASR_WORDS:
                raise ValueError('Whisper word count cap reached')
    return words,rejected,segments


def build_report(media:Path,scratch:Path,transfer_seconds:float):
    if media.stat().st_size!=SIZE or sha(media)!=SHA:
        raise ValueError('Immutable original-source AVI SHA/size incorrect')
    times={'verified_source_ftp_transfer_seconds':round(transfer_seconds,3)}
    wav=scratch/'mono16k.wav'
    t=time.monotonic()
    duration_ms,audio_sha=decode_audio(media,wav)
    times['one_episode_pcm_decode_seconds']=round(time.monotonic()-t,3)
    # Each model processes the *same* original decoded source WAV, without
    # captions, the other's text, vocabulary hints or speaker labels.
    t=time.monotonic()
    archive=scratch/'vosk.zip'
    bytes_downloaded=download_pinned_model(archive)
    model_dir=unpack_pinned_model(archive,scratch/'vosk-model')
    times['vosk_weight_download_unpack_seconds']=round(time.monotonic()-t,3)
    t=time.monotonic()
    vosk_words,vosk_rejected=vosk_free_decode(wav,model_dir,duration_ms)
    times['kaldi_wfst_vosk_full_episode_inference_seconds']=round(time.monotonic()-t,3)
    t=time.monotonic()
    whisper_words,whisper_rejected,whisper_segments=whisper_free_decode(wav,scratch/'whisper-cache',duration_ms)
    times['whisper_tiny_en_full_episode_inference_seconds']=round(time.monotonic()-t,3)
    source_spec={
        'schema':'night-court-two-independent-asr-words/1',
        'episode_id':'S01E01','source_video_sha256':SHA,
        'decoded_audio_sha256':audio_sha,
        'source_window_ms':[0,duration_ms],
        'models':[
          {'model_id':'faster-whisper tiny.en beam1 int8 cpu',
           'architecture_family':'whisper','free_decoding':True,
           'srt_or_other_model_prompt_used':False,'words':whisper_words},
          {'model_id':'vosk-model-small-en-us-0.15 Kaldi WFST',
           'architecture_family':'kaldi_hmm_wfst','free_decoding':True,
           'srt_or_other_model_prompt_used':False,'words':vosk_words}
        ]}
    t=time.monotonic()
    result=compare(source_spec)
    times['two_model_text_reconciliation_seconds']=round(time.monotonic()-t,3)
    output={
      'schema':'night-court-original-full-episode-dual-independent-asr-cost-and-agreement/1',
      'episode_id':'S01E01','original_video_sha256':SHA,'original_video_bytes':SIZE,
      'decoded_audio_sha256':audio_sha,'source_audio_duration_ms':duration_ms,
      'model_original_srt_prompted':False,'original_audio_human_listened':False,
      'models':[{'model_id':'vosk-model-small-en-us-0.15 Kaldi WFST',
                 'architecture_family':'kaldi_hmm_wfst',
                 'weight_zip_sha256':VOSK_ZIP_SHA256,'weight_zip_bytes':bytes_downloaded,
                 'vosk_package_version':importlib.metadata.version('vosk'),
                 'rejected_word_timestamps':vosk_rejected,'word_count':len(vosk_words)},
                {'model_id':'faster-whisper tiny.en beam1 int8 cpu',
                 'architecture_family':'whisper',
                 'faster_whisper_version':importlib.metadata.version('faster-whisper'),
                 'rejected_word_timestamps':whisper_rejected,
                 'segment_count':whisper_segments,'word_count':len(whisper_words)}],
      'measured_wall_time_seconds':times,
      'measured_source_processing_seconds_excludes_install':round(sum(times.values()),3),
      'comparison':result,
      'original_video_audio_or_model_weights_exported':False,
      'episode_dialogue_human_verified':False,'speaker_identities_verified':False,
      'episode_script_complete':False,
      'limitations':[
         'All timing and dialogue text are two free-decoding independent model hypotheses, not direct listening.',
         'Kaldi and Whisper models have distinct architectures but can make correlated recognition errors.',
         'Whitespace-normalized agreement uses 3+ word runs; short genuine phrases may remain unresolved.',
         'Model weight download and inference cost measured; workflow OS/pip install/startup not included.',
         'One episode is insufficient to prove population p95 throughput or original subtitle equivalence.',
         'No source subtitle supplied to either model; SRT agreement and human joint-error calibration still pending.'
       ]}
    return output


def run_ftp(output:Path):
    if output.exists():raise ValueError('Refuse original source-ASR artifact overwrite')
    item=candidate()
    if item['size_bytes']!=SIZE or not os.getenv('FTP_PASSWORD'):
        raise ValueError('Exact original source FTP candidate/secret missing')
    with tempfile.TemporaryDirectory(prefix='night-court-whole-dual-asr-') as tmp:
        scratch=Path(tmp)
        original=scratch/item['basename']
        t=time.monotonic()
        ftp=connect(os.getenv('FTP_HOST','wood.seedhost.eu'),
                    os.getenv('FTP_USER','ianseeds'),os.environ['FTP_PASSWORD'],'ftp')
        try:receipt=retrieve(ftp,item,original)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        if receipt!=SHA:raise ValueError('Unexpected source AVI fingerprint')
        report=build_report(original,scratch,time.monotonic()-t)
        encoded=(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode()
        if len(encoded)>MAX_JSON_BYTES:raise ValueError('Private ASR report exceeded text budget')
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_bytes(encoded)
    print('Finished two independent full-episode source ASR families and text alignment: '
          +str(report['comparison']['counts'])+', '
          +str(report['measured_source_processing_seconds_excludes_install'])+'s excluding runner setup')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ftp',action='store_true')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if not a.ftp:p.error('Authenticated source inference only through reviewed trusted owner workflow')
    run_ftp(a.output)


if __name__=='__main__':
    main()
