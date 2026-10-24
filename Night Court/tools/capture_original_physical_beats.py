#!/usr/bin/env python3
"""Source-fingerprinted bounded original episode physical-business preview.

Uses 5fps sequences around four preselected potentially significant actions.
No source movie or soundtrack enters any artifact or repository; output is
private temporary action-review contact sheets and exact still digests.
"""
from __future__ import annotations
import argparse,ftplib,hashlib,json,os,subprocess,tempfile
from pathlib import Path
from ftp_research_intake import connect
from pilot_ftp_video_acoustics import candidate as s01_candidate,retrieve
from s09e19_untimed_video_anchor_pilot import exact_candidate as s09_candidate

SOURCES={
 "S01E01":("5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962",
            [(160,22,"court-office-open-window-action"),(1258,20,"court-bench-posture")]),
 "S09E19":("51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649",
            [(684,20,"brief-floor-spark"),(951,20,"restaurant-dance-business")])
}
FPS=5
MAX_FRAMES_PER_WINDOW=115


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def windows(ep):
    if ep not in SOURCES:raise ValueError("Only two pinned original episodes")
    seen=[]
    for start,duration,label in SOURCES[ep][1]:
        if (not 0<=start<1430 or duration<5 or duration>25 or
            start+duration>1448 or not label):raise ValueError("Unbounded source excerpt")
        if any(not (start+duration<=a or start>=a+b) for a,b,_ in seen):
            raise ValueError("Overlapping replay clips")
        seen.append((start,duration,label))
    return seen


def run(args,timeout=200):
    try:
        return subprocess.run(args,check=True,capture_output=True,text=True,timeout=timeout)
    except subprocess.CalledProcessError as error:
        # Only decoder diagnostics. No credentials or source audio/video.
        raise RuntimeError('Bounded original decoder: '+(error.stderr or 'no detail')[-1000:]) from error

def generate(media,out,ep):
    from PIL import Image,ImageDraw
    if digest(media)!=SOURCES[ep][0]:raise ValueError("Original AVI SHA mismatch")
    if out.exists():raise ValueError("Do not overwrite original samples")
    out.mkdir(parents=True)
    groups=[]
    for start,duration,label in windows(ep):
        folder=out/label
        folder.mkdir()
        run(['ffmpeg','-hide_banner','-nostdin','-loglevel','error','-threads','1','-filter_threads','1',
             '-ss',str(start),'-i',str(media),'-t',str(duration),'-an',
             '-vf','fps=5,scale=240:144:force_original_aspect_ratio=decrease,pad=240:144:(ow-iw)/2:(oh-ih)/2',
             '-q:v','7','-y',str(folder/'frame-%03d.jpg')],timeout=220)
        frames=sorted(folder.glob('frame-*.jpg'))
        if not (FPS*duration-2<=len(frames)<=FPS*duration+2 and
                len(frames)<=MAX_FRAMES_PER_WINDOW):
            raise ValueError("Missing or runaway original-source dense sample")
        refs=[]
        sheet_refs=[]
        for i,p in enumerate(frames):
            if p.stat().st_size>=65000 or p.stat().st_size<=100:
                raise ValueError("Invalid bounded source JPEG")
            refs.append({'frame':i+1,'nominal_original_video_time_ms':
                         start*1000+round(i*1000/FPS),
                         'source_thumbnail_sha256':digest(p),
                         'requested_offset_not_native_PTS_verified':True,
                         'original_audio_or_speaker_observed':False})
        for base in range(0,len(frames),50):
            sheet=Image.new('RGB',(2400,5*164),(11,12,15))
            draw=ImageDraw.Draw(sheet)
            for j,p in enumerate(frames[base:base+50]):
                with Image.open(p) as img:
                    if img.size!=(240,144):raise ValueError("Unexpected image geometry")
                    x=j%10*240;y=j//10*164
                    sheet.paste(img,(x,y))
                t=start+(base+j)/FPS
                caption=f'{ep}  {int(t//60):02}:{t%60:04.1f}  #{base+j+1:03}'
                draw.text((x+5,y+145),caption,fill=(245,245,245))
            image_name=f'{label}-sheet-{base//50+1:02}.jpg'
            image_path=out/image_name
            sheet.save(image_path,'JPEG',quality=82,optimize=True)
            if not 1000<image_path.stat().st_size<1600000:
                raise ValueError("Bounded source motion sheet unexpectedly large")
            sheet_refs.append({'file':image_name,'sha256':digest(image_path)})
        groups.append({
          'original_source_window_seconds':[start,start+duration],
          'review_focus_proposal':label,
          'nominal_sampling_fps':FPS,'original_video_sha256':SOURCES[ep][0],
          'source_frames_indexed':len(refs),'frames':refs,
          'review_contact_sheets':sheet_refs,
          'human_or_assistant_sampled_image_motion_review_completed':False,
          'full_continuous_action_or_laughter_verified':False,
          'named_speaker_verified':False
        })
    report={'schema':'night-court-original-dense-physical-beat-review/1',
      'episode_id':ep,'source_video_sha256':SOURCES[ep][0],
      'source_episodes_processed':1,'source_avi_stored_in_artifact':False,
      'original_audio_stored_in_artifact':False,
      'windows':groups,'complete_episode_stage_directions_verified':False,
      'frame_presentation_times_verified':False,
      'limits':'Nominal 5fps images only; use source audio/video for actual continuous-action and voice acceptance.'}
    (out/'sample-evidence.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(ep,"actual original bounded 5fps action preview",[(x['review_focus_proposal'],x['source_frames_indexed']) for x in groups])
    return report


def ftp_mode(ep,out):
    item=s01_candidate() if ep=='S01E01' else s09_candidate()
    pw=os.getenv('FTP_PASSWORD')
    if not pw:raise ValueError("Trusted source access only")
    with tempfile.TemporaryDirectory(prefix='night-court-original-motion-') as tmp:
        media=Path(tmp)/item['basename']
        ftp=connect(os.getenv('FTP_HOST','wood.seedhost.eu'),os.getenv('FTP_USER','ianseeds'),pw,'ftp')
        try:original_sha=retrieve(ftp,item,media)
        finally:
            try:ftp.quit()
            except ftplib.all_errors:ftp.close()
        if original_sha!=SOURCES[ep][0]:raise ValueError("Different original edition")
        return generate(media,out,ep)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--episode',choices=SOURCES.keys(),required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--ftp',action='store_true')
    a=p.parse_args()
    if not a.ftp:p.error('Trusted owner FTP mode only')
    ftp_mode(a.episode,a.output)
