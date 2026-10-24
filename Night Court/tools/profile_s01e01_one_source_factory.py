#!/usr/bin/env python3
"""Source-once initial Night Court audiovisual pass: actual combined wall time.

One SHA-pinned FTP AVI is held transiently while two independent free-decode
ASR models and capped full-video visual sampling run serially on the same
source. Export compact numerical/candidate statistics only; no movie, PCM,
JPEG, model weights, verified speakers or human-accepted performance claims.
"""
from __future__ import annotations
import argparse
import ftplib
import json
import os
from pathlib import Path
import tempfile
import time

from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate,retrieve
from probe_s01e01_full_dual_asr import build_report
from probe_s01e01_cadence_and_cost import SHA,SIZE
from profile_s01e01_whole_visual_pass import profile_local

MAX_REPORT_BYTES=100000


def compose_summary(audio,visual,transfer_s,combined_s):
    if (audio.get('schema')!='night-court-original-full-episode-dual-independent-asr-cost-and-agreement/1'
        or visual.get('schema')!='night-court-whole-source-visual-time-budget/1'
        or audio.get('original_video_sha256')!=SHA or visual.get('source_video_sha256')!=SHA
        or audio.get('original_video_bytes')!=SIZE or visual.get('original_video_bytes')!=SIZE
        or audio.get('source_audio_duration_ms')!=visual.get('source_video_duration_ms')
        or audio.get('model_original_srt_prompted') is not False
        or audio.get('original_audio_human_listened') is not False
        or visual.get('script_or_full_episode_accepted') is not False
        or not visual.get('all_image_frame_pts_match_verified')
        or visual.get('actual_extracted_frame_count',0)>240
        or visual.get('actual_JPEG_bytes',0)>10000000):
        raise ValueError('Unverifiable or media-unsafe joint original-source results')
    count=audio.get('comparison',{}).get('counts',{})
    models=audio.get('models',[])
    if (len(models)!=2
        or {m['architecture_family'] for m in models}!={'kaldi_hmm_wfst','whisper'}
        or not 0<=count.get('corroborated_words',-1)<=15000
        or not 0<=count.get('corroborated_spans',-1)<=5000):
        raise ValueError('Original model consensus and independent families not established')
    stage_a=dict(audio['measured_wall_time_seconds'])
    stage_a.pop('verified_source_ftp_transfer_seconds',None)
    stage_v=dict(visual['measured_stage_seconds'])
    if any(type(x) not in (int,float) or x<0 or x>1800
           for x in list(stage_a.values())+list(stage_v.values())):
        raise ValueError('Invalid source timing evidence')
    source_stage_sum=round(float(transfer_s)+sum(stage_a.values())+sum(stage_v.values()),3)
    if not 0<combined_s<=1800 or abs(source_stage_sum-combined_s)>20:
        raise ValueError('Combined monotonic clock differs unexpectedly from component timings')
    return {
        'schema':'night-court-original-one-source-integrated-first-pass/1',
        'episode_id':'S01E01','original_video_sha256':SHA,'original_video_bytes':SIZE,
        'decoded_audio_sha256':audio['decoded_audio_sha256'],
        'source_audio_video_duration_ms':audio['source_audio_duration_ms'],
        'fps_source_encoded':visual['original_stream_avg_frame_rate'],
        'model_independent_families':sorted(m['architecture_family'] for m in models),
        'asr_measured_seconds_excluding_ftp':stage_a,
        'visual_measured_seconds_excluding_ftp':stage_v,
        'ftp_verify_original_once_seconds':round(float(transfer_s),3),
        'sum_measured_individual_stages_seconds':source_stage_sum,
        'actual_source_to_final_metadata_wall_seconds':round(float(combined_s),3),
        'word_candidate_summary':count,
        'model_diagnostic_summary':[{'model_id':m['model_id'],
             'rejected_word_timestamps':m.get('rejected_word_timestamps'),
             'rejected_word_reasons':m.get('rejected_word_reasons',{})}
             for m in models],
        'unverified_image_change_candidates':visual['image_change_candidates_not_verified_cuts'],
        'selected_JPEG_frames':visual['actual_extracted_frame_count'],
        'selected_ephemeral_JPEG_bytes':visual['actual_JPEG_bytes'],
        'all_source_frame_pts_checked':visual['all_image_frame_pts_match_verified'],
        'original_source_video_download_count':1,
        'original_audio_pcm_decode_count':1,
        'independent_original_video_cuts_verified':False,
        'original_cues_independently_audio_reviewed':False,
        'speakers_identified_by_audio_and_mouth':False,
        'screen_performance_reviewed':False,
        'visual_language_model_applied':False,
        'complete_production_screenplay_accepted':False,
        'confidence_note':(
          'Separate independent model architectures provide positive corroborated dialogue candidates; '
          'not statistically independent recognizer errors or human source acceptance.'
        ),
        'limitations':[
          'This is the actual CPU source processing and evidence planning/export workflow on one episode, not measured fleet p95.',
          'No original media, separated voice embeddings, screenshots or model weights retained.',
          '212 FFmpeg cut/motion scores are hypotheses, not edited scene truth or continuous action verification.',
          'No visual-language model, named speaker or performance annotations included; these are downstream costs.'
        ]
    }


def run_source(out:Path):
    if out.exists():raise ValueError('Refuse to overwrite trusted source benchmark')
    item=candidate()
    if item['size_bytes']!=SIZE or not os.environ.get('FTP_PASSWORD'):
        raise ValueError('Missing immutable S01E01 file size/source credential')
    with tempfile.TemporaryDirectory(prefix='night-court-one-source-episode-') as tmp:
        scratch=Path(tmp)
        source=scratch/item['basename']
        total_start=time.monotonic()
        transfer_start=time.monotonic()
        ftp=connect(os.getenv('FTP_HOST','wood.seedhost.eu'),
                    os.getenv('FTP_USER','ianseeds'),os.environ['FTP_PASSWORD'],'ftp')
        try:received=retrieve(ftp,item,source)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        transfer=time.monotonic()-transfer_start
        if received!=SHA:
            raise ValueError('Original AVI bytes differ from approved edition SHA')
        audio=build_report(source,scratch,transfer)
        visual=profile_local(source,scratch/'source-visual-numeric.json')
        combined=time.monotonic()-total_start
        summary=compose_summary(audio,visual,transfer,combined)
        encoded=(json.dumps(summary,indent=2,ensure_ascii=False)+'\n').encode()
        if len(encoded)>MAX_REPORT_BYTES:
            raise ValueError('Integrated metadata report too large')
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_bytes(encoded)
    print(f"One original S01E01 AVI source, two independent ASR models, full cut scan, "
          f"{summary['selected_JPEG_frames']} ephemeral PTS-verified frames; "
          f"{summary['actual_source_to_final_metadata_wall_seconds']}s measured end-to-end, "
          "all acceptance gates still pending.")


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ftp',action='store_true')
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    if not args.ftp:ap.error('Trusted original-source owner workflow only')
    run_source(args.output)


if __name__=='__main__':
    main()
