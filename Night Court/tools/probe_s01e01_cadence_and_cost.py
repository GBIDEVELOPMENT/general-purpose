#!/usr/bin/env python3
"""One SHA-pinned S01E01 source transfer: real cadence and stage timings only.

No frames, audio or video are exported. Source is temporary, credential isolation
is delegated to a trusted-base owner-only workflow.
"""
from __future__ import annotations
import argparse
import ftplib
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import tempfile
import time
from fractions import Fraction

from plan_fast_visual_pass import make_plan, frame_rate

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'research/s01e01-fast-visual-dryrun-input.json'
SHA='5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962'
SIZE=183386112


def ffprobe(media:Path, *args):
    p=subprocess.run(['ffprobe','-v','error',*args,'-of','json',str(media)],
                     check=True,capture_output=True,text=True,timeout=90)
    if len(p.stdout)>750000:
        raise ValueError('ffprobe report unbounded')
    return json.loads(p.stdout)


def video_properties(media:Path, *, require_episode_duration=True):
    response=ffprobe(media,'-select_streams','v:0','-show_entries',
                     'stream=codec_name,avg_frame_rate,r_frame_rate,time_base,start_pts,nb_frames,field_order,width,height:format=duration')
    v=response.get('streams',[])
    if len(v)!=1 or v[0].get('codec_name') not in ('mpeg4','h264','hevc','mpeg2video'):
        raise ValueError('Unrecognized unique source video stream')
    stream=v[0]
    avg=frame_rate(stream.get('avg_frame_rate'))
    nominal=frame_rate(stream.get('r_frame_rate'))
    timebase=Fraction(stream.get('time_base','0'))
    if not 0 < timebase < 1:
        raise ValueError('Invalid original stream time base')
    duration=float(response.get('format',{}).get('duration',0))
    if require_episode_duration and not 1200 <= duration <= 1800:
        raise ValueError('Original S01E01 runtime unexpectedly different')
    result={k:stream.get(k) for k in ('codec_name','avg_frame_rate','r_frame_rate','time_base','start_pts','nb_frames','field_order','width','height')}
    result['duration_seconds']=duration
    result['avg_fps_decimal']=round(float(avg),5)
    result['r_fps_decimal']=round(float(nominal),5)
    return result


def summarize_presentation_times(times, rate:Fraction):
    """Report actual frame PTS even when decoder/demux order includes B-frame reorder.

    A sorted unique list is used only to estimate the display-time cadence.
    Raw-order inversions and duplicate PTS remain explicit, not silently fixed.
    """
    if not 20 <= len(times) <= 150:
        raise ValueError('Unexpected number of PTS probe frames')
    inversions=sum(times[i]<=times[i-1] for i in range(1,len(times)))
    presented=sorted(set(times))
    duplicates=len(times)-len(presented)
    if len(presented)<20:
        raise ValueError('Insufficient unique presentation timestamps')
    deltas=[(presented[i]-presented[i-1])*1000 for i in range(1,len(presented))]
    med=statistics.median(deltas)
    target=Fraction(1000,1)/rate
    return {'pts_sample_count':len(times),
            'unique_pts_count':len(presented),
            'out_of_order_or_tied_adjacent_pts_count':inversions,
            'duplicate_pts_count':duplicates,
            'sampled_video_pts_start_ms':round(presented[0]*1000),
            'sampled_video_pts_end_ms':round(presented[-1]*1000),
            'median_sampled_frame_interval_ms':round(float(med),4),
            'nominal_interval_ms':round(float(target),4),
            'sample_interval_within_1pct_nominal':abs(med-target)/target<=Fraction(1,100),
            'decoded_frame_order_strictly_monotonic':inversions==0,
            'whole_episode_cadence_verified':False}


def sample_frame_cadence(media:Path, rate:Fraction, *, start_seconds=700):
    # The real AVI can expose display-order PTS out of decode/demux order.
    # Preserve that anomaly, then sort unique PTS for display cadence statistics.
    data=ffprobe(media,'-read_intervals',f'{start_seconds}%+3','-select_streams','v:0',
                 '-show_entries','frame=best_effort_timestamp_time')
    frames=data.get('frames',[])
    times=[Fraction(str(row['best_effort_timestamp_time'])) for row in frames
           if row.get('best_effort_timestamp_time') is not None]
    return summarize_presentation_times(times, rate)


def research_probe(media:Path):
    from probe_s01e01_source_avi_shot_changes import contract, ffmpeg_candidates, WINDOW
    m=contract()
    if (not media.is_file() or media.stat().st_size!=SIZE
        or m['source_video_sha256']!=SHA or m['source_video_size_bytes_candidate']!=SIZE):
        raise ValueError('Original source media fingerprint/size contract mismatch')
    with media.open('rb') as f:
        digest=hashlib.file_digest(f,'sha256').hexdigest()
    if digest!=SHA:
        raise ValueError('Original source AVI SHA mismatch')
    elapsed={}
    t=time.monotonic();info=video_properties(media);elapsed['ffprobe_stream_metadata_seconds']=round(time.monotonic()-t,3)
    t=time.monotonic();cadence=sample_frame_cadence(media,frame_rate(info['avg_frame_rate']));elapsed['ffprobe_sample_pts_seconds']=round(time.monotonic()-t,3)
    t=time.monotonic();cuts=ffmpeg_candidates(media,*WINDOW);elapsed['original_shot_score_window_seconds']=round(time.monotonic()-t,3)
    original=json.loads(FIXTURE.read_text('utf-8'))
    if original['source_video_sha256']!=SHA or original['window_ms']!=list(WINDOW):
        raise ValueError('Original source dryrun fixture changed')
    prior_cut_times=[x['time_ms'] for x in original['cut_candidates']]
    new_cut_times=[x['original_stream_pts_candidate_ms'] for x in cuts]
    original['cut_candidates']=[{'time_ms':x['original_stream_pts_candidate_ms'],
                                 'image_change_score':x['ffmpeg_scene_score']} for x in cuts]
    original['avg_frame_rate']=info['avg_frame_rate']
    original['frame_rate_provenance']='verified_local_ffprobe'
    plan=make_plan(original)
    return {'schema':'night-court-s01e01-original-cadence-and-cost/1',
            'episode_id':'S01E01','original_video_sha256':SHA,'original_video_bytes':SIZE,
            'cadence':info,'sampled_pts':cadence,'wall_clock_stage_seconds':elapsed,
            'shot_proposal_count':len(cuts),
            'prior_shot_times_equal_current_run':prior_cut_times==new_cut_times,
            'verified_rate_visual_plan_counts':plan['counts'],
            'visual_plan_input_rate_provenance':plan['frame_rate_provenance'],
            'original_picture_audio_frames_exported':False,
            'source_video_ephemeral':True,
            'full_episode_dual_asr_benchmarked':False,
            'full_episode_visual_models_benchmarked':False,
            'episode_initial_pass_under_30_minutes_verified':False,
            'limitations':['PTS interval sampled in one short mid-episode seek, not a full frame cadence audit.',
                           'FFmpeg scene scores are original video *candidate changes*, not certified cuts.',
                           'Shot scoring only this 36s review window, not full-episode throughput.',
                           'No media content retained, no word recognition or character identity established.']}


def run_ftp(output:Path):
    from ftp_research_intake import connect
    from pilot_ftp_video_acoustics import candidate, retrieve
    if output.exists():raise ValueError('Refuse to overwrite prior cost evidence')
    item=candidate()
    if (item['size_bytes']!=SIZE or not os.environ.get('FTP_PASSWORD')):
        raise ValueError('Original FTP candidate changed or trusted secret missing')
    with tempfile.TemporaryDirectory(prefix='night-court-cadence-') as tmp:
        media=Path(tmp)/item['basename']
        t=time.monotonic()
        ftp=connect(os.getenv('FTP_HOST','wood.seedhost.eu'),os.getenv('FTP_USER','ianseeds'),os.environ['FTP_PASSWORD'],'ftp')
        try:receipt=retrieve(ftp,item,media)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        transfer=round(time.monotonic()-t,3)
        if receipt!=SHA:raise ValueError('FTP original source hash changed')
        result=research_probe(media)
        result['wall_clock_stage_seconds']['source_ftp_transfer_sha_verify_seconds']=transfer
        result['wall_clock_measured_stages_seconds']=round(sum(result['wall_clock_stage_seconds'].values()),3)
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print('S01E01 verified original AVI cadence and bounded shot-cost metadata captured; media wiped')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ftp',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args()
    if not a.ftp:parser.error('Source media transfer only allowed via trusted owner workflow')
    run_ftp(a.output)


if __name__=='__main__':main()
