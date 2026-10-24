#!/usr/bin/env python3
"""Cheap pixel-change ranking for three PTS-checked original-source frames.

Works only on source-verified *ephemeral* extracted JPEGs, inside candidate
shot partitions. Differences can result from movement, camera work, changing
light, noise, or missed edits; no actions or scene boundaries are asserted.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re

from extract_fast_visual_plan import inside_repo

MAX_TRIADS = 32
GRID = (64, 48)
CHANGE_THRESHOLD = 24  # absolute 8-bit grey-level difference


def _pixels(path):
    # Import here: source-free module validation does not require Pillow.
    from PIL import Image
    with Image.open(path) as image:
        if image.width < 32 or image.height < 32:
            raise ValueError('Unusable source still dimensions')
        return tuple(image.convert('L').resize(GRID, Image.Resampling.BILINEAR).getdata())


def _delta(a, b):
    if len(a) != GRID[0] * GRID[1] or len(b) != len(a):
        raise ValueError('Unexpected pixel grid')
    diffs = [abs(x-y) for x,y in zip(a,b)]
    return {
        'mean_normalized_abs_delta': round(sum(diffs)/(255*len(diffs)),6),
        'changed_pixel_fraction_ge_24': round(sum(v>=CHANGE_THRESHOLD for v in diffs)/len(diffs),6)
    }


def summarize(plan, capture, frame_dir):
    """Return only bounded metadata. Never store pixel arrays or assert motion."""
    frame_dir=Path(frame_dir)
    if inside_repo(frame_dir) or not frame_dir.is_dir():
        raise ValueError('Frame pixels must remain in ephemeral scratch outside checkout')
    if (plan.get('schema') != 'night-court-fast-visual-sampling-plan/1'
        or capture.get('schema') != 'night-court-budgeted-original-source-frame-execution/1'
        or plan.get('source_video_sha256') != capture.get('original_video_sha256')
        or plan.get('frame_rate_provenance') != 'verified_local_ffprobe'
        or plan.get('candidate_cuts_are_independently_verified') is not False
        or capture.get('all_samples_within_source_pts_tolerance') is not True
        or capture.get('all_scene_and_action_verification_pending') is not True):
        raise ValueError('Missing verified-source and unverified-interpretation boundaries')
    events=plan.get('motion_bursts')
    pframes=plan.get('frames')
    frames=capture.get('frames')
    if (not isinstance(events,list) or len(events)>MAX_TRIADS
        or not isinstance(frames,list) or len(frames)>240
        or not isinstance(pframes,list) or len(pframes)!=len(frames)
        or len(frames)!=capture.get('extraction_frame_count')):
        raise ValueError('Unbounded or mismatched original-frame evidence')

    observed={}
    for proposed,actual in zip(pframes,frames):
        if (proposed.get('nominal_frame_index')!=actual.get('source_frame_index_nominal')
            or proposed.get('candidate_shot_partition')!=actual.get('candidate_shot_partition')
            or proposed.get('evidence_event_id')!=actual.get('event_id')
            or proposed.get('role')!=actual.get('role')
            or proposed.get('nominal_ms')!=actual.get('nominal_ms')
            or actual.get('matched_within_125ms') is not True):
            raise ValueError('Original frame identity or decoded PTS evidence changed')
        name=actual.get('frame_filename')
        if not isinstance(name,str) or not re.fullmatch(r'frame-[0-9]{3}\.jpg',name):
            raise ValueError('Unsafe image file reference')
        path=frame_dir/name
        if not path.is_file() or path.is_symlink() or path.stat().st_size!=actual.get('bytes'):
            raise ValueError('Missing source image or changed byte count')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=actual.get('sha256'):
            raise ValueError('Source image content SHA mismatch')
        if proposed['role']=='motion_burst':
            observed.setdefault(proposed.get('evidence_event_id'),[]).append((proposed,actual,path))
    outputs=[]
    for event in events:
        ident=event.get('event_id')
        group=observed.pop(ident,None)
        if (not isinstance(ident,str) or not group or len(group)!=3
            or event.get('frame_count')!=3
            or any(proposed['candidate_shot_partition']!=event.get('candidate_shot_partition')
                   for proposed,_,_ in group)
            or [p['nominal_ms'] for p,_,_ in group]!=event.get('nominal_frame_times_ms')):
            raise ValueError('Motion triple crossed candidate shot or lost one source still')
        timestamps=[a['source_frame_pts_ms_actual'] for _,a,_ in group]
        if any(type(t) is not int for t in timestamps):
            raise ValueError('Malformed actual PTS')
        # Duplicate/reversed actual decoded presentation timestamps make
        # a nominal-frame triple unsafe for time-ordered interpretation.
        if not timestamps[0]<timestamps[1]<timestamps[2]:
            outputs.append({'event_id':ident,'candidate_shot_partition':event['candidate_shot_partition'],
                'source_frame_pts_ms_actual':timestamps,
                'interpretation_status':'abstain_non_increasing_actual_source_pts'})
            continue
        three=[_pixels(path) for _,_,path in group]
        first=_delta(three[0],three[1])
        second=_delta(three[1],three[2])
        ranking=(first['mean_normalized_abs_delta']+second['mean_normalized_abs_delta'])/2
        outputs.append({
            'event_id':ident,'candidate_shot_partition':event['candidate_shot_partition'],
            'source_frame_pts_ms_actual':timestamps,
            'frame_sha256':[a['sha256'] for _,a,_ in group],
            'first_temporal_pixel_difference':first,
            'second_temporal_pixel_difference':second,
            'mean_temporal_pixel_change_score':round(ranking,6),
            'interpretation_status':'candidate_intra_partition_change_for_visual_review'
        })
    if observed:raise ValueError('Unexpected or duplicate original motion events')
    ranked=sorted((o for o in outputs if 'mean_temporal_pixel_change_score' in o),
                  key=lambda o:(-o['mean_temporal_pixel_change_score'],o['event_id']))
    return {
       'schema':'night-court-ephemeral-triad-pixel-change-metadata/1',
       'source_video_sha256':plan['source_video_sha256'],
       'triple_count':len(outputs),
       'pts_order_abstentions':len(outputs)-len(ranked),
       'analyzed_three_frame_groups':len(ranked),
       'analysis_grid_pixels':GRID[0]*GRID[1],
       'retained_source_image_pixels':False,
       'source_footage_or_audio_published':False,
       'true_cuts_or_character_actions_verified':False,
       'voice_identity_or_source_dialogue_verified':False,
       'production_script_accepted':False,
       'review_priority':ranked,
       'abstentions':[o for o in outputs if 'mean_temporal_pixel_change_score' not in o],
       'limitations':[
          'Pixel changes can reflect compression noise, lighting, camera changes or editorial cuts.',
          'Candidate partitions are unverified shot suggestions, not proven continuous takes.',
          'Triplets alone cannot establish movement direction, actor identity or stage directions.'
       ]
    }
