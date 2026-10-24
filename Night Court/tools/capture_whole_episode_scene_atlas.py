#!/usr/bin/env python3
"""Private bounded whole-episode photographic scene overview for Night Court pilots.

Source-verified AVI is held only in temporary runner scratch; compact timestamp-
labeled contact sheets and source-hashed frame catalogue stay in a seven-day
private Actions artifact, never a Git commit. Original source PTS labels are
sampling targets, NOT assertions of scene cuts, named cast or motion.
"""
from __future__ import annotations
import argparse
import ftplib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate as s01_candidate,retrieve
from s09e19_untimed_video_anchor_pilot import exact_candidate as s09_candidate

SOURCE_SHA={
    'S01E01':'5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962',
    'S09E19':'51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649'
}
INTERVAL_MS=18000
MAX_FRAMES=84
MAX_JPEG_BYTES=110000
MAX_ARTIFACT_BYTES=15000000
MAX_WALL_SECONDS=1450


def sha_file(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):
            h.update(block)
    return h.hexdigest()


def sample_targets(duration_ms,interval_ms=INTERVAL_MS):
    if type(duration_ms) is not int or not 1200000<=duration_ms<=MAX_WALL_SECONDS*1000:
        raise ValueError('Original source episode duration outside accepted bounds')
    if type(interval_ms) is not int or not 12000<=interval_ms<=30000:
        raise ValueError('Unsafe still interval')
    times=list(range(interval_ms//2,duration_ms,interval_ms))
    if not 1<=len(times)<=MAX_FRAMES:raise ValueError('Episode still cap exceeded')
    return times


def manifest(episode,video_sha,duration_ms,frames,sheets):
    if episode not in SOURCE_SHA or video_sha!=SOURCE_SHA[episode]:
        raise ValueError('Wrong original source edition')
    expected=sample_targets(duration_ms)
    if (len(frames)!=len(expected) or
        [f['requested_original_source_time_ms'] for f in frames]!=expected or
        any(f['original_video_sha256']!=video_sha or
            len(f['jpg_sha256'])!=64 for f in frames)):
        raise ValueError('Incomplete/mismatched source-wide capture')
    return {
        'schema':'night-court-whole-episode-private-scene-overview/1',
        'episode_id':episode,'original_source_video_sha256':video_sha,
        'original_source_duration_ms':duration_ms,
        'sample_spacing_ms':INTERVAL_MS,'frame_count':len(frames),
        'sheets':sheets,'frame_index':frames,
        'actual_frames_inspected_for_settings':False,
        'continuous_original_video_action_reviewed':False,
        'source_shot_boundaries_verified':False,
        'named_speaker_or_character_verified':False,
        'screenplay_or_episode_accepted':False,
        'source_avi_or_audio_in_artifact':False,
        'limitations':[
            'Sampling every 18s exposes room/location overview only; cuts and brief physical comedy can occur between samples.',
            'Frame labels are requested source times rather than decoded original-frame PTS.',
            'No automatic role or stage-direction claims are made by this capture.',
            'Original movie and audio are deleted with the trusted runner scratch.'
        ]
    }


def run_cmd(args,timeout=90):
    return subprocess.run(args,capture_output=True,text=True,check=True,timeout=timeout)


def make_scene_atlas(media,out,episode):
    from PIL import Image,ImageDraw,ImageFont
    if episode not in SOURCE_SHA or sha_file(media)!=SOURCE_SHA[episode]:
        raise ValueError('Source AVI SHA-256 mismatch')
    if out.exists():raise ValueError('Refuse overwrite of capture')
    meta=json.loads(run_cmd(['ffprobe','-v','error','-show_format','-of','json',str(media)]).stdout)
    duration_ms=round(float(meta['format']['duration'])*1000)
    times=sample_targets(duration_ms)
    out.mkdir(parents=True)
    frames_dir=out/'frames'
    frames_dir.mkdir()
    recorded=[]
    for i,when in enumerate(times):
        destination=frames_dir/f'frame-{i+1:03d}.jpg'
        run_cmd(['ffmpeg','-hide_banner','-nostdin','-loglevel','error',
                 '-ss',f'{when/1000:.3f}','-i',str(media),'-an',
                 '-frames:v','1','-vf','scale=320:-2','-q:v','6',
                 '-y',str(destination)],timeout=50)
        n=destination.stat().st_size
        if not 100<n<MAX_JPEG_BYTES:raise ValueError('Oversized or empty original source thumbnail')
        recorded.append({'frame_id':i+1,
            'requested_original_source_time_ms':when,
            'time_was_exactly_checked_against_decoded_frame_pts':False,
            'jpg_sha256':sha_file(destination),
            'original_video_sha256':SOURCE_SHA[episode],
            'file':f'frames/{destination.name}',
            'scene_boundary_or_action_verified':False})
    # The sheet groups contiguous time windows so reviewers can spot new
    # locations, cut density and actor entrances cheaply, not infer action.
    sheets=[]
    for group_start in range(0,len(recorded),20):
        block=recorded[group_start:group_start+20]
        tile_w,tile_h=320,204
        contact=Image.new('RGB',(tile_w*5,tile_h*4),(12,13,15))
        draw=ImageDraw.Draw(contact)
        for offset,f in enumerate(block):
            p=frames_dir/Path(f['file']).name
            with Image.open(p) as img:
                if img.size[0]!=320 or img.size[1]>184:
                    raise ValueError('Unexpected original source video thumbnail dimensions')
                x=(offset%5)*tile_w
                y=(offset//5)*tile_h
                contact.paste(img,(x,y))
            t=f['requested_original_source_time_ms']//1000
            caption=f'{episode}  {t//60:02}:{t%60:02}  #{f["frame_id"]:03}'
            draw.rectangle([x,y+181,x+tile_w,y+204],fill=(12,13,15))
            draw.text((x+7,y+186),caption,fill=(247,247,247))
        sheet=out/f'scene-overview-{group_start//20+1:02}.jpg'
        contact.save(sheet,format='JPEG',quality=80,optimize=True)
        if not 1000<sheet.stat().st_size<2500000:raise ValueError('Invalid contact sheet')
        sheets.append({'file':sheet.name,'first_frame_id':block[0]['frame_id'],
                       'last_frame_id':block[-1]['frame_id'],'sha256':sha_file(sheet)})
    document=manifest(episode,SOURCE_SHA[episode],duration_ms,recorded,sheets)
    (out/'frame-source-catalogue.json').write_text(json.dumps(document,indent=2)+'\n','utf-8')
    total=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
    if total>MAX_ARTIFACT_BYTES:raise ValueError('Private photo-only evidence cap exceeded')
    print(f'{episode}: source SHA verified, {len(recorded)} frames across entire '
          f'{duration_ms/1000:.1f}s original, {len(sheets)} review sheets; '
          'no accepted scenes, actions or named speakers')
    return document


def ftp_capture(episode,out):
    item=s01_candidate() if episode=='S01E01' else s09_candidate()
    password=os.getenv('FTP_PASSWORD')
    if not password:raise ValueError('Trusted source access required')
    with tempfile.TemporaryDirectory(prefix='night-court-private-atlas-') as temp:
        movie=Path(temp)/item['basename']
        f=connect(os.getenv('FTP_HOST','wood.seedhost.eu'),
                  os.getenv('FTP_USER','ianseeds'),password,'ftp')
        try:received=retrieve(f,item,movie)
        finally:
            try:f.quit()
            except ftplib.all_errors:f.close()
        if received!=SOURCE_SHA[episode]:raise ValueError('Source transfer SHA changed')
        document=make_scene_atlas(movie,out,episode)
    return document


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--episode',choices=sorted(SOURCE_SHA),required=True)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--ftp',action='store_true')
    a=p.parse_args()
    if not a.ftp:p.error('Trusted owner original-source FTP mode only')
    ftp_capture(a.episode,a.output)


if __name__=='__main__':main()
