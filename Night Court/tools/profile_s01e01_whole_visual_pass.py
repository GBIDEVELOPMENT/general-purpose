#!/usr/bin/env python3
"""One verified original S01E01 AVI -> timed whole-episode low-res cut scan
and at most 240 ephemeral, source-PTS-audited frame samples.

Scores and evenly distributed motion PROBES are not evidence of actual cuts,
character speech, motion or script completeness. All original media stays
inside one ephemeral trusted owner workflow.
"""
from __future__ import annotations
import argparse
from decimal import Decimal,ROUND_HALF_UP
import ftplib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate,retrieve
from plan_fast_visual_pass import make_plan
from extract_fast_visual_plan import extract
from summarize_motion_triplets import summarize
from probe_s01e01_cadence_and_cost import video_properties, SHA, SIZE

ROOT=Path(__file__).resolve().parents[1]
ACTIVITY=ROOT/'seasons/S01/S01E01/derived/editorial-review-v1/acceptance-worklist.json'
THRESHOLD=Decimal('0.12')
MAX_CUTS=2500
MAX_SCAN_STDERR=5_000_000
AUTO_PROBES=26
FRAME_RE=re.compile(r'\bframe:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:\s*(-?\d+(?:\.\d+)?)')
SCORE_RE=re.compile(r'\blavfi\.scene_score=([0-9]+(?:\.[0-9]+)?)')


def parse_full_avi_scores(stderr, *, duration_ms):
    if not 1200000 <= duration_ms <= 1800000:
        raise ValueError('Expected one original-sized episode duration')
    raw=[]
    pending=None
    for line in stderr.splitlines():
        if 'Parsed_metadata_' not in line: continue
        m=FRAME_RE.search(line)
        if m:
            if pending is not None:raise ValueError('Missing score between source frame observations')
            pending=(int(m[1]),Decimal(m[3]))
        s=SCORE_RE.search(line)
        if s:
            if pending is None:raise ValueError('Unpaired original source score')
            score=Decimal(s[1])
            if not THRESHOLD < score <= 1:
                raise ValueError('Invalid candidate frame-score value')
            when=int((pending[1]*1000).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
            if 0 < when < duration_ms:
                raw.append((when,float(score)))
            if len(raw)>MAX_CUTS:
                raise ValueError('Excessive full-episode image-change candidates')
            pending=None
    if pending is not None:raise ValueError('Dangling source frame without image score')
    duplicates=0
    score_by_time={}
    for t,score in raw:
        if t in score_by_time:
            duplicates+=1
            score_by_time[t]=max(score_by_time[t],score)
        else:
            score_by_time[t]=score
    rows=[{'time_ms':t,'image_change_score':score_by_time[t]}
          for t in sorted(score_by_time)]
    return rows,{'emitted_rows':len(raw),'duplicate_timestamp_rows':duplicates,
                 'ordered_or_tied_timestamp_steps':sum(raw[i][0]<=raw[i-1][0]
                 for i in range(1,len(raw)))}


def scan_video(original:Path, *, duration_ms:int):
    # First scale to 160 wide, then score decoded adjacent frames. This
    # should be faster than high-resolution visual model classification.
    filt=f"scale=160:-2,select='gt(scene,{THRESHOLD})',metadata=print:key=lavfi.scene_score"
    argv=['ffmpeg','-nostdin','-hide_banner','-loglevel','info',
          '-i',str(original),'-map','0:v:0','-an','-vf',filt,
          '-fps_mode','vfr','-f','null','-']
    p=subprocess.run(argv,capture_output=True,text=True,check=True,timeout=360)
    if len(p.stderr)>MAX_SCAN_STDERR:
        raise ValueError('Full-video score console output too large')
    return parse_full_avi_scores(p.stderr,duration_ms=duration_ms)


def source_activity_events(cuts:list, duration_ms:int):
    # Existing six events are genuine *ordered 4fps sampled observations*.
    # Proposed extra 'coverage-probe' events are NOT detected body motion.
    packet=json.loads(ACTIVITY.read_text('utf-8'))
    if packet.get('source_video_sha256')!=SHA:
        raise ValueError('Editorial observation source fingerprint changed')
    visuals=packet.get('visual_review_tasks')
    if not isinstance(visuals,list) or len(visuals)!=6:
        raise ValueError('Expected six original sampled physical/shot observations')
    events=[]
    for v in visuals:
        a,b=v['source_interval_ms']
        if not 0<=a<b<=duration_ms:
            raise ValueError('Original observation timestamp out of source range')
        events.append({'event_id':v['task_id'].split(':')[-1],
                       'time_ms':(a+b)//2,'priority':5 if v.get('observation_class')=='motion_inferred_from_ordered_sampled_positions' else 3,
                       'mode':'gesture'})
    boundaries=[0]+[x['time_ms'] for x in cuts]+[duration_ms]
    # Use uniform time buckets first, but place each coverage triad at a safe
    # midpoint of a plausible shot, not around the detected cut boundary.
    extra=0
    import bisect
    for i in range(AUTO_PROBES):
        target=round((i+0.5)*duration_ms/AUTO_PROBES)
        shot=bisect.bisect_right(boundaries,target)-1
        left,right=boundaries[shot],boundaries[shot+1]
        if right-left<1200:
            continue
        center=min(max(target,left+600),right-600)
        if not left+500<=center<=right-500:
            continue
        events.append({'event_id':f'coverage-probe-{i:02d}',
                       'time_ms':center,'priority':1,'mode':'gesture'})
        extra+=1
    return events,extra


def profile_local(original:Path,private_output:Path):
    if private_output.exists():
        raise ValueError('Never overwrite original source cost evidence')
    if not original.is_file() or original.stat().st_size!=SIZE:
        raise ValueError('Unexpected original AVI byte count')
    from extract_fast_visual_plan import sha
    if sha(original)!=SHA:
        raise ValueError('Wrong original source SHA')
    timings={}
    t=time.monotonic()
    stream=video_properties(original)
    timings['ffprobe_metadata_seconds']=round(time.monotonic()-t,3)
    duration_ms=round(stream['duration_seconds']*1000)
    t=time.monotonic()
    scored,trace=scan_video(original,duration_ms=duration_ms)
    timings['full_episode_lowres_cut_proposal_scan_seconds']=round(time.monotonic()-t,3)
    t=time.monotonic()
    events,coverage_count=source_activity_events(scored,duration_ms)
    plan=make_plan({'schema':'night-court-fast-visual-input/1',
        'episode_id':'S01E01','source_video_sha256':SHA,
        'duration_ms':duration_ms,'window_ms':[0,duration_ms],
        'avg_frame_rate':stream['avg_frame_rate'],
        'frame_rate_provenance':'verified_local_ffprobe',
        'cut_candidates':scored,'activity_events':events})
    timings['source_plan_seconds']=round(time.monotonic()-t,3)
    if plan['counts']['frames']>240:
        raise ValueError('Unbounded visual source plan')
    t=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='night-court-private-jpegs-') as tmp:
        location=Path(tmp)/'extracted'
        captured=extract(original,plan,location,expected_media_bytes=SIZE)
        timings['one_pass_ffmpeg_source_frame_extraction_seconds']=round(time.monotonic()-t,3)
        t=time.monotonic()
        pixel_review=summarize(plan,captured,location/'frames')
        timings['ephemeral_three_frame_pixel_difference_seconds']=round(time.monotonic()-t,3)
    if not captured['all_samples_within_source_pts_tolerance']:
        raise ValueError('Actual selected AVI PTS do not match planned times; do not publish image evidence')
    report={
      'schema':'night-court-whole-source-visual-time-budget/1',
      'episode_id':'S01E01','source_video_sha256':SHA,'original_video_bytes':SIZE,
      'source_video_duration_ms':duration_ms,
      'original_stream_avg_frame_rate':stream['avg_frame_rate'],
      'original_stream_r_frame_rate':stream['r_frame_rate'],
      'score_threshold':float(THRESHOLD),
      'image_change_candidates_not_verified_cuts':len(scored),
      'score_trace_anomalies':trace,
      'full_avi_cut_proposals':[x['time_ms'] for x in scored],
      'editorial_sampled_events':6,'uniform_coverage_probe_events':coverage_count,
      'source_plan_counts':plan['counts'],
      'source_plan_event_deferrals':plan['deferred_events'],
      'measured_stage_seconds':timings,
      'source_JPEGs_in_ephemeral_scratch_only':True,
      'actual_extracted_frame_count':captured['extraction_frame_count'],
      'actual_JPEG_bytes':captured['total_image_bytes'],
      'source_triads_with_pixel_change_features':pixel_review['analyzed_three_frame_groups'],
      'source_triads_abstaining_for_pts_order':pixel_review['pts_order_abstentions'],
      'pixel_change_candidate_reviews':pixel_review['review_priority'][:12],
      'pixel_change_is_verified_physical_action':False,
      'all_image_frame_pts_match_verified':captured['all_samples_within_source_pts_tolerance'],
      'visual_models_executed':False,
      'visual_content_independently_reviewed':False,
      'shot_boundaries_or_real_scenes_independently_verified':False,
      'speaking_characters_or_actions_accepted':False,
      'script_or_full_episode_accepted':False,
      'notes':[
       'Full video frame-to-frame FFmpeg image changes are hypotheses, not confirmed shot or scene cuts.',
       'Coverage triads are uniformly seeded for observation, not independently detected movements.',
       'Source JPEG images and movie remain temporary; benchmark stores numbers and source timing only.',
       'Timings omit runner startup and FFmpeg installation. Video-model inference not yet measured.'
      ]}
    private_output.parent.mkdir(parents=True,exist_ok=True)
    private_output.write_text(json.dumps(report,indent=2)+'\n','utf-8')
    return report


def run_source(output:Path):
    if output.exists():raise ValueError('Source experiment output exists')
    item=candidate()
    if item.get('size_bytes')!=SIZE or not os.environ.get('FTP_PASSWORD'):
        raise ValueError('Original owner source metadata/secret missing')
    with tempfile.TemporaryDirectory(prefix='night-court-original-visual-full-') as tmp:
        scratch=Path(tmp)
        original=scratch/item['basename']
        t=time.monotonic()
        ftp=connect(os.getenv('FTP_HOST','wood.seedhost.eu'),
                    os.getenv('FTP_USER','ianseeds'),os.environ['FTP_PASSWORD'],'ftp')
        try:received=retrieve(ftp,item,original)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        if received!=SHA:raise ValueError('Original FTP AVI content hash changed')
        transfer=round(time.monotonic()-t,3)
        internal=scratch/'numeric-report.json'
        report=profile_local(original,internal)
        report['measured_stage_seconds']['ftp_source_transfer_sha256_seconds']=transfer
        report['measured_source_wall_stage_seconds']=round(sum(report['measured_stage_seconds'].values()),3)
        result=json.dumps(report,indent=2)+'\n'
        if len(result.encode('utf-8'))>250000:
            raise ValueError('Numerical source performance report unexpectedly large')
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(result,'utf-8')
    print(f"Original episode: {report['image_change_candidates_not_verified_cuts']} scored frame candidates; "
          f"{report['actual_extracted_frame_count']} bounded source images; "
          f"{report['measured_source_wall_stage_seconds']}s source stages; no media retained.")


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--ftp',action='store_true')
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    if not a.ftp:p.error('Only owner trusted-base FTP experiment is enabled')
    run_source(a.output)


if __name__=='__main__':
    main()
