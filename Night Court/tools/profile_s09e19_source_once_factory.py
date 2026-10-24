#!/usr/bin/env python3
"""Second, genuinely different original-series source-once speed pilot: S09E19.

Reuses proved S01E01 inference, scan, bounded JPEG and consensus primitives.
Does not invent original timestamps for any of 347 untimed source paragraphs.
The original AVI, PCM, model weights and JPEGs are ephemeral.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
import ftplib
import json
import os
from pathlib import Path
import tempfile
import time

from compare_independent_asr import compare
from rejected_asr_word_diagnostics import add_independent_context
from extract_fast_visual_plan import extract, sha
from summarize_motion_triplets import summarize
from plan_continuous_action_review import plan_continuous_review
from ftp_research_intake import connect
from match_s09e19_untimed_paragraphs import assess, candidates
from pilot_ftp_video_acoustics import retrieve
from plan_fast_visual_pass import make_plan
from probe_s01e01_full_dual_asr import (decode_audio, download_pinned_model,
    unpack_pinned_model, vosk_free_decode, whisper_free_decode, VOSK_ZIP_SHA256)
from probe_s01e01_cadence_and_cost import video_properties
from profile_s01e01_whole_visual_pass import scan_video
from s09e19_untimed_video_anchor_pilot import (exact_candidate, sources,
    BYTES, TXT_SHA)

SHA='51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649'
MAX_BYTES=180000
MAX_ASR_PARAGRAPH_PROBES=40
MAX_CUT_CANDIDATES=2500


def original_events(cuts, duration, packet):
    if (packet.get('episode_id')!='S09E19' or
        packet.get('original_video_sha256')!=SHA or
        packet.get('original_untimed_source_sha256')!=TXT_SHA or
        packet.get('original_paragraph_count')!=347):
        raise ValueError('S09E19 source-unmatched visual/editorial packet')
    events=[]
    for row in packet['tasks']:
        if row.get('kind')!='sampled_visual_stage_claim':
            continue
        a,b=row['sampled_video_interval_ms']
        if not 0<=a<b<=duration:
            raise ValueError('Original sampled task does not fit source video')
        events.append({'event_id':row['task_id'].split(':')[-1],
                       'time_ms':(a+b)//2, 'priority':4,'mode':'gesture'})
    if len(events)!=6:
        raise ValueError('Missing six original source visual tasks')
    boundaries=[0]+[c['time_ms'] for c in cuts]+[duration]
    import bisect
    for i in range(26):
        target=round((i+.5)*duration/26)
        ix=bisect.bisect_right(boundaries,target)-1
        left,right=boundaries[ix],boundaries[ix+1]
        if right-left<1200:continue
        center=min(max(target,left+600),right-600)
        if left+500<=center<=right-500:
            events.append({'event_id':f'coverage-probe-{i:02d}',
                           'time_ms':center,'priority':1,'mode':'gesture'})
    return events


def review_untimed_paragraphs(spans, paragraphs):
    """Bounded evenly spread exploratory lexical paragraph hints, NEVER source SRT."""
    bank=candidates(paragraphs)
    if not spans:return []
    picks=sorted({round(i*(len(spans)-1)/max(1,MAX_ASR_PARAGRAPH_PROBES-1))
                  for i in range(min(MAX_ASR_PARAGRAPH_PROBES,len(spans)))})
    report=[]
    for index in picks:
        span=spans[index]
        text=span['model_a_verbatim_candidate']
        matched=assess({'index':index,'text':text},bank)
        report.append({
          'consensus_span_index':index,
          'original_avi_audio_time_proposal_ms':span['time_interval_ms'],
          'independent_model_agreed_text_hypothesis':text,
          'untimed_original_source_paragraph_candidate':matched['source_paragraph_candidate'],
          'lexical_uniqueness_status':matched['decision'],
          'original_source_paragraph_time_ms':None,
          'word_identity_original_audio_human_verified':False
        })
    return report


def profile(media:Path, scratch:Path, transfer:float, *, execution_mode='serial'):
    if media.stat().st_size!=BYTES or sha(media)!=SHA:
        raise ValueError('Original S09E19 full AVI SHA and byte size mismatch')
    paragraphs=sources()
    if len(paragraphs)!=347:
        raise ValueError('Original untimed source must be exactly 347 paragraphs')
    packet_path=(Path(__file__).resolve().parents[1]/
          'seasons/S09/S09E19/derived/editorial-review-v1/untimed-scene-review-queue.json')
    packet=json.loads(packet_path.read_text('utf-8'))
    if execution_mode not in ('serial','parallel'):
        raise ValueError('Unexpected source AV execution mode')
    timings={'single_original_ftp_transfer_and_sha_seconds':round(transfer,3)}
    total_start=time.monotonic()
    t=time.monotonic()
    stream=video_properties(media,require_episode_duration=False)
    duration=round(stream['duration_seconds']*1000)
    if not 1200000<=duration<=1800000:
        raise ValueError('Wrong original 1984-series episode duration')
    timings['ffprobe_source_metadata_seconds']=round(time.monotonic()-t,3)
    def timed_scan():
        started=time.monotonic()
        result=scan_video(media,duration_ms=duration)
        return result,time.monotonic()-started
    # Launch read-only video decode while the separately decoded soundtrack
    # and architecturally distinct model passes work against the same AVI.
    # Controlled serial mode remains the reference and safe fallback.
    with (ThreadPoolExecutor(max_workers=1,thread_name_prefix='nc-video-scan')
          if execution_mode=='parallel' else nullcontext()) as scan_pool:
        scan_future=(scan_pool.submit(timed_scan) if scan_pool else None)
        t=time.monotonic()
        wav=scratch/'shared-16khz-mono-original.wav'
        audio_duration,audio_sha=decode_audio(media,wav)
        if abs(audio_duration-duration)>1500:
            raise ValueError('Source episode sound/video duration drift')
        timings['one_source_pcm_decode_seconds']=round(time.monotonic()-t,3)
        t=time.monotonic()
        model_archive=scratch/'weights.zip'
        weight_bytes=download_pinned_model(model_archive)
        model_dir=unpack_pinned_model(model_archive,scratch/'vosk-root')
        timings['pinned_vosk_download_unpack_seconds']=round(time.monotonic()-t,3)
        t=time.monotonic()
        vosk_words,vosk_rejected,vosk_reasons=vosk_free_decode(wav,model_dir,audio_duration)
        timings['kaldi_wfst_full_episode_inference_seconds']=round(time.monotonic()-t,3)
        t=time.monotonic()
        rejected_details=[]
        whisper_words,whisper_rejected,whisper_segments,whisper_reasons=whisper_free_decode(
            wav,scratch/'whisper-cache',audio_duration,rejected_details=rejected_details)
        add_independent_context(rejected_details,vosk_words,audio_duration)
        timings['whisper_tiny_full_episode_inference_seconds']=round(time.monotonic()-t,3)
        t=time.monotonic()
        comparison=compare({'schema':'night-court-two-independent-asr-words/1',
           'episode_id':'S09E19','source_video_sha256':SHA,
           'decoded_audio_sha256':audio_sha,
           'source_window_ms':[0,audio_duration],
           'models':[
            {'model_id':'faster-whisper tiny.en beam1 cpu','architecture_family':'whisper',
             'free_decoding':True,'srt_or_other_model_prompt_used':False,'words':whisper_words},
            {'model_id':'vosk-model-small-en-us-0.15 Kaldi WFST',
             'architecture_family':'kaldi_hmm_wfst','free_decoding':True,
             'srt_or_other_model_prompt_used':False,'words':vosk_words}]})
        timings['independent_model_word_reconciliation_seconds']=round(time.monotonic()-t,3)
        if scan_future is None:
            (scored,trace),scan_seconds=timed_scan()
        else:
            (scored,trace),scan_seconds=scan_future.result()
        if len(scored)>MAX_CUT_CANDIDATES:raise ValueError('Unbounded original image-change candidates')
        timings['full_source_low_res_cut_scan_seconds']=round(scan_seconds,3)
    t=time.monotonic()
    events=original_events(scored,duration,packet)
    plan=make_plan({'schema':'night-court-fast-visual-input/1',
       'episode_id':'S09E19','source_video_sha256':SHA,
       'duration_ms':duration,'window_ms':[0,duration],
       'avg_frame_rate':stream['avg_frame_rate'],
       'frame_rate_provenance':'verified_local_ffprobe',
       'cut_candidates':scored,'activity_events':events})
    timings['bounded_visual_plan_seconds']=round(time.monotonic()-t,3)
    t=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='nc-s09e19-private-jpegs-') as image_tmp:
        location=Path(image_tmp)/'source-frames'
        image_report=extract(media,plan,location,expected_media_bytes=BYTES)
        timings['one_pass_source_frame_jpeg_extraction_seconds']=round(time.monotonic()-t,3)
        t=time.monotonic()
        pixel_review=summarize(plan,image_report,location/'frames')
        timings['ephemeral_three_frame_pixel_difference_seconds']=round(time.monotonic()-t,3)
    t=time.monotonic()
    continuous_review=plan_continuous_review(plan,pixel_review,scored)
    timings['shot_candidate_bounded_review_planning_seconds']=round(time.monotonic()-t,3)
    if not image_report['all_samples_within_source_pts_tolerance']:
        raise ValueError('Image source PTS drift; no source screenshot labels accepted')
    t=time.monotonic()
    paragraph_matches=review_untimed_paragraphs(comparison['corroborated_spans'],paragraphs)
    timings['untimed_source_paragraph_lexical_probe_seconds']=round(time.monotonic()-t,3)
    full_wall=round(time.monotonic()-total_start+transfer,3)
    measured_overlap=max(0.0,round(sum(timings.values())-full_wall,3))
    if execution_mode=='serial' and measured_overlap>20:
        raise ValueError('Unexpected serial source stage timing overlap')
    return {
       'schema':'night-court-s09e19-whole-source-once-cross-episode-benchmark/1',
       'episode_id':'S09E19','original_series':'night-court-1984',
       'original_video_sha256':SHA,'source_video_bytes':BYTES,
       'original_untimed_source_sha256':TXT_SHA,'original_source_paragraphs':347,
       'original_source_paragraphs_with_source_timecodes':0,
       'decoded_original_pcm_sha256':audio_sha,
       'original_video_duration_ms':duration,'original_audio_duration_ms':audio_duration,
       'video_encoded_avg_fps':stream['avg_frame_rate'],
       'original_audio_decoded_once':True,'original_video_download_count':1,
       'model_families':['whisper','kaldi_hmm_wfst'],
       'model_was_primed_by_original_text':False,
       'model_word_counts':{'whisper':len(whisper_words),'vosk':len(vosk_words)},
       'model_invalid_word_time_counts':{'whisper':whisper_rejected,'vosk':vosk_rejected},
       'model_rejection_reasons':{'whisper':whisper_reasons,'vosk':vosk_reasons},
       'whisper_rejected_word_time_review':{
          'total_invalid_word_intervals':whisper_rejected,
          'retained_bounded_invalid_time_proposals':len(rejected_details),
          'unretained_diagnostics_over_cap':max(0,whisper_rejected-len(rejected_details)),
          'rejection_details_no_source_time_promotion':rejected_details,
          'original_soundtrack_listened':False,
          'separate_model_context_human_verified':False},
       'source_consensus_word_counts':comparison['counts'],
       'reviewed_untimed_source_lexical_probe_count':len(paragraph_matches),
       'untimed_paragraph_lexical_candidates':paragraph_matches,
       'source_video_cut_change_candidates_unverified':len(scored),
       'source_video_pts_trace_anomalies':trace,
       'source_sample_plan_counts':plan['counts'],
       'actual_source_frames_selected':image_report['extraction_frame_count'],
       'actual_source_jpegs_bytes_ephemeral':image_report['total_image_bytes'],
       'source_triads_with_pixel_change_features':pixel_review['analyzed_three_frame_groups'],
       'source_triads_abstaining_for_pts_order':pixel_review['pts_order_abstentions'],
       'pixel_change_candidate_reviews':pixel_review['review_priority'][:12],
       'pixel_change_is_verified_physical_action':False,
       'shot_bounded_selective_original_video_review':continuous_review,
       'sampled_frames_original_pts_checked':image_report['all_samples_within_source_pts_tolerance'],
       'component_measured_seconds':timings,
       'source_av_execution_mode':execution_mode,
       'individual_stages_sum_seconds':round(sum(timings.values()),3),
       'source_stage_clock_overlap_seconds':measured_overlap,
       'parallel_execution_verified_faster_than_serial':False,
       'source_processing_wall_seconds_excluding_job_startup_and_dependency_install':full_wall,
       'all_original_source_media_deleted_after_job':True,
       'human_original_audio_listened':False,
       'independently_verified_real_cuts_and_physical_action':False,
       'source_untimed_paragraph_timestamps_created':False,
       'speaker_identity_or_emotion_verified':False,
       'episode_production_script_accepted':False,
       'fleet_p95_episode_speed_verified':False,
       'limitations':[
         'The 347 source paragraphs have no source timecodes, and model lexical matches are proposals only.',
         'Video cuts are FFmpeg frame-change hypotheses; uniform triads are not recognized motion.',
         'Both recognizers decode independently but their errors may correlate.',
         'No vision-language understanding or human hearing/continuous-video review is measured.',
         'This second episode helps evaluate throughput generalization but does not establish p95 across 193 episodes.'
       ]
    }


def run_ftp(destination:Path,*,execution_mode='serial'):
    if destination.exists():raise ValueError('Do not overwrite source evidence')
    item=exact_candidate()
    if item['size_bytes']!=BYTES or not os.getenv('FTP_PASSWORD'):
        raise ValueError('Exact S09E19 FTP original source/credential not available')
    with tempfile.TemporaryDirectory(prefix='night-court-s09e19-source-once-') as root:
        root=Path(root)
        video=root/item['basename']
        t=time.monotonic()
        ftp=connect(os.getenv('FTP_HOST','wood.seedhost.eu'),
            os.getenv('FTP_USER','ianseeds'),os.getenv('FTP_PASSWORD'),'ftp')
        try:received=retrieve(ftp,item,video)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        if received!=SHA:raise ValueError('Actual original AVI S09E19 fingerprint differs')
        report=profile(video,root,time.monotonic()-t,execution_mode=execution_mode)
        encoded=(json.dumps(report,indent=2,ensure_ascii=False)+'\n').encode()
        if len(encoded)>MAX_BYTES:
            raise ValueError('Numeric/candidate source output exceeds tiny report cap')
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(encoded)
    print('Original S09E19 source-once full episode: '
          f"{report['source_processing_wall_seconds_excluding_job_startup_and_dependency_install']}s, "
          f"{report['source_consensus_word_counts']['corroborated_spans']} agreement spans, "
          f"{report['actual_source_frames_selected']} source JPEG samples; "
          'all original text remains untimed and all AV acceptance pending')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--ftp',action='store_true')
    p.add_argument('--execution-mode',choices=('serial','parallel'),default='serial')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if not args.ftp:p.error('Authorized trusted owner original-source Actions job only')
    run_ftp(args.output,execution_mode=args.execution_mode)


if __name__=='__main__':
    main()
