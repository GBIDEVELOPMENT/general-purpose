#!/usr/bin/env python3
"""Decode only planned, cut-aware source frames in one bounded FFmpeg process.

Must be called only on a locally present verified owner source and scratch
directory outside Git checkout. Emits compact PTS/hashes; never approves action
continuity, shot boundaries, voice identities or a production screenplay.
"""
from __future__ import annotations
import argparse
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import re
import subprocess

from plan_fast_visual_pass import frame_rate

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent.resolve()
MAX_IMAGES=240
MAX_TOTAL_IMAGE_BYTES=10_000_000
MAX_IMAGE_BYTES=120_000
MAX_TIME_DEVIATION_MS=125
SHOWINFO=re.compile(r'\[Parsed_showinfo_\d+[^\]]*\] n:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:\s*(-?\d+(?:\.\d+)?)')


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def inside_repo(path):
    x=path.resolve()
    return x==REPO or REPO in x.parents


def validate_plan(plan):
    if (plan.get('schema')!='night-court-fast-visual-sampling-plan/1'
        or plan.get('frame_time_basis')!='nominal_fps_seek_candidates_not_verified_decoded_original_frame_pts'
        or plan.get('frame_rate_provenance')!='verified_local_ffprobe'
        or plan.get('speaker_action_or_script_accepted') is not False
        or plan.get('candidate_cuts_are_independently_verified') is not False):
        raise ValueError('Plan not sourced from verified original ffprobe provenance')
    source=plan.get('source_video_sha256')
    if not isinstance(source,str) or not re.fullmatch('[0-9a-f]{64}',source):
        raise ValueError('Missing exact source AVI hash')
    fps=frame_rate(plan.get('nominal_avg_frame_rate'))
    frames=plan.get('frames')
    if not isinstance(frames,list) or not 1<=len(frames)<=MAX_IMAGES:
        raise ValueError('Frame count cap invalid')
    count=plan.get('counts',{}).get('frames')
    if type(count) is not int or count!=len(frames):
        raise ValueError('Reported source sample count mismatch')
    positions=[]
    for f in frames:
        idx=f.get('nominal_frame_index')
        ms=f.get('nominal_ms')
        if (type(idx) is not int or type(ms) is not int or idx<0
            or idx>1000000 or ms<0 or ms>7200000):
            raise ValueError('Bad video frame index or nominal time')
        if abs(round(idx*1000/fps)-ms)>1:
            raise ValueError('Proposed frame time inconsistent with frame rate')
        positions.append(idx)
    if positions!=sorted(set(positions)):
        raise ValueError('Frame requests must be unique and source-order increasing')
    return fps,frames


def extract(media:Path,plan:dict,output:Path,*,expected_media_bytes:int|None=None):
    fps,frames=validate_plan(plan)
    if (not media.is_file() or inside_repo(output) or output.exists()
        or expected_media_bytes is not None and media.stat().st_size!=expected_media_bytes):
        raise ValueError('Original media is missing, changed, or output is unsafe')
    if sha(media)!=plan['source_video_sha256']:
        raise ValueError('Original video content differs from planned source')
    output.mkdir(parents=True)
    sample_dir=output/'frames'
    sample_dir.mkdir()
    terms='+'.join(f'eq(n\\,{f["nominal_frame_index"]})' for f in frames)
    argv=['ffmpeg','-nostdin','-hide_banner','-loglevel','info',
          '-i',str(media),'-map','0:v:0','-an',
          '-vf',f"select='{terms}',scale=320:-2,showinfo",
          '-fps_mode','passthrough','-q:v','9','-frames:v',str(len(frames)),
          '-start_number','1',str(sample_dir/'frame-%03d.jpg')]
    run=subprocess.run(argv,capture_output=True,text=True,timeout=180,check=True)
    if len(run.stderr)>1_000_000:
        raise ValueError('Frame-source provenance log unexpectedly large')
    seen=[]
    for line in run.stderr.splitlines():
        m=SHOWINFO.search(line)
        if m:
            n=int(m[1]);ms=int((Decimal(m[3])*1000).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
            if n!=len(seen):
                raise ValueError('Non-sequential FFmpeg decoded frame sample index')
            seen.append({'ffmpeg_sample_ordinal':n,'actual_pts_ms':ms,'ffmpeg_pts':int(m[2])})
    found=sorted(sample_dir.glob('frame-*.jpg'))
    if len(seen)!=len(frames) or len(found)!=len(frames):
        raise ValueError('Missing actual source frames or decoded timestamps')
    results=[]
    total_bytes=0
    for index,(requested,detected,file) in enumerate(zip(frames,seen,found),start=1):
        if file.name!=f'frame-{index:03d}.jpg':
            raise ValueError('Frame extraction output sequence changed')
        size=file.stat().st_size
        total_bytes+=size
        if not 100<=size<=MAX_IMAGE_BYTES or total_bytes>MAX_TOTAL_IMAGE_BYTES:
            raise ValueError('Source frame byte budget exceeded')
        difference=detected['actual_pts_ms']-requested['nominal_ms']
        results.append({'source_frame_index_nominal':requested['nominal_frame_index'],
                        'source_frame_pts_ms_actual':detected['actual_pts_ms'],
                        'nominal_ms':requested['nominal_ms'],
                        'pts_minus_nominal_ms':difference,
                        'matched_within_125ms':abs(difference)<=MAX_TIME_DEVIATION_MS,
                        'role':requested['role'],
                        'candidate_shot_partition':requested['candidate_shot_partition'],
                        'event_id':requested.get('evidence_event_id'),
                        'frame_filename':file.name,'sha256':sha(file),'bytes':size})
    report={
      'schema':'night-court-budgeted-original-source-frame-execution/1',
      'original_video_sha256':plan['source_video_sha256'],
      'source_encoded_avg_frame_rate':str(fps),
      'original_picture_or_audio_committed_to_repo':False,
      'reported_actual_ffmpeg_frame_pts':True,
      'extraction_frame_count':len(results),
      'total_image_bytes':total_bytes,
      'images_located_only_outside_checkout':True,
      'all_samples_within_source_pts_tolerance':all(r['matched_within_125ms'] for r in results),
      'all_scene_and_action_verification_pending':True,
      'frames':results}
    (output/'index.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--media',type=Path,required=True)
    p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    plan=json.loads(args.plan.read_text('utf-8'))
    report=extract(args.media,plan,args.output)
    print(f"{report['extraction_frame_count']} source-frame stills, "
          f"{report['total_image_bytes']} bytes in private scratch, "
          f"source-PTS matches: {report['all_samples_within_source_pts_tolerance']}")


if __name__=='__main__':main()
