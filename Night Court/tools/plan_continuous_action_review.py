#!/usr/bin/env python3
"""Bounded source-linked continuous-video review *requests*, not stage directions.

Produces short, cut-CANDIDATE-bounded review windows for editorial physical
comedy plus high- and low-pixel-change controls. No media decoding, scene
recognition, human listening, voice identity or performance claims are made.
"""
from __future__ import annotations
from bisect import bisect_right
import math

MAX_CUTS=2500
MAX_WINDOWS=12
MAX_PIXEL_EVENTS=32
HALO_MS=1200
CUT_MARGIN_MS=150
MIN_CLIP_MS=450


def _valid_int(x,low,high):
    return type(x) is int and low<=x<=high


def plan_continuous_review(source_plan, pixels, cut_candidates):
    if (source_plan.get('schema')!='night-court-fast-visual-sampling-plan/1'
        or pixels.get('schema')!='night-court-ephemeral-triad-pixel-change-metadata/1'
        or source_plan.get('source_video_sha256')!=pixels.get('source_video_sha256')
        or source_plan.get('frame_rate_provenance')!='verified_local_ffprobe'
        or source_plan.get('candidate_cuts_are_independently_verified') is not False
        or pixels.get('true_cuts_or_character_actions_verified') is not False
        or pixels.get('production_script_accepted') is not False):
        raise ValueError('Original-source plan and pixel evidence are incompatible')
    duration=source_plan.get('source_duration_ms')
    if not _valid_int(duration,1000,7200000):
        raise ValueError('Invalid source duration')
    if not isinstance(cut_candidates,list) or len(cut_candidates)>MAX_CUTS:
        raise ValueError('Unbounded original source shot-change suggestions')
    scored=[]
    for row in cut_candidates:
        if not isinstance(row,dict):
            raise ValueError('Bad source cut proposal')
        t=row.get('time_ms')
        score=row.get('image_change_score')
        if (not _valid_int(t,1,duration-1)
            or type(score) not in (int,float) or not math.isfinite(score)
            or not 0<=score<=1):
            raise ValueError('Invalid image-change time or score')
        scored.append(t)
    if scored!=sorted(set(scored)):
        raise ValueError('Source image-change cuts must be unique and chronological')
    if source_plan.get('counts',{}).get('cut_candidates')!=len(scored):
        raise ValueError('Review source cuts differ from planned shot partitioning')
    bounds=[0]+scored+[duration]
    bursts=source_plan.get('motion_bursts')
    ranked=pixels.get('review_priority')
    abstained=pixels.get('abstentions')
    if (not isinstance(bursts,list) or len(bursts)>MAX_PIXEL_EVENTS
        or not isinstance(ranked,list) or len(ranked)>MAX_PIXEL_EVENTS
        or not isinstance(abstained,list) or len(abstained)>MAX_PIXEL_EVENTS
        or len(ranked)+len(abstained)!=pixels.get('triple_count')
        or len(ranked)!=pixels.get('analyzed_three_frame_groups')):
        raise ValueError('Unbounded or misreported source triad measurements')
    bursts_by_id={e['event_id']:e for e in bursts}
    if len(bursts_by_id)!=len(bursts):
        raise ValueError('Duplicate original activity event ID')
    candidates={}
    cut_pts_deferred=[]
    for rank,row in enumerate(ranked):
        if not isinstance(row,dict):raise ValueError('Bad original source pixel record')
        name=row.get('event_id')
        event=bursts_by_id.get(name)
        pts=row.get('source_frame_pts_ms_actual')
        score=row.get('mean_temporal_pixel_change_score')
        partition=row.get('candidate_shot_partition')
        if (not event or name in candidates
            or not isinstance(pts,list) or len(pts)!=3
            or any(not _valid_int(t,0,duration) for t in pts)
            or not pts[0]<pts[1]<pts[2]<duration
            or not isinstance(score,(int,float)) or isinstance(score,bool)
            or not math.isfinite(score) or not 0<=score<=1
            or partition!=event.get('candidate_shot_partition')):
            raise ValueError('Unverified or malformed source triplet ranking')
        # Decoded PTS can depart nominal frame PTS; revisit shot boundary in
        # actual presentation-time space to avoid covert continuity claims.
        actual_partitions=[bisect_right(scored,t) for t in pts]
        if len(set(actual_partitions))!=1 or actual_partitions[0]!=partition:
            cut_pts_deferred.append({'event_id':name,
                'reason':'actual_source_pts_cross_candidate_cut',
                'source_frame_pts_ms_actual':pts})
            continue
        candidates[name]={'event_id':name,'actual_pts_ms':pts,'score':score,
                          'partition':partition,'pixel_rank':rank+1,
                          'editorial_priority':event.get('priority',0)}
    for row in abstained:
        if row.get('event_id') not in bursts_by_id or row['event_id'] in candidates:
            raise ValueError('Invalid or duplicate source PTS abstention')
    if len(candidates)+len(abstained)+len(cut_pts_deferred)!=len(bursts):
        raise ValueError('Missing source original motion sampling event')

    ordered=list(candidates.values())
    editorial=sorted((x for x in ordered if x['editorial_priority']>=4),
                    key=lambda x:(-x['editorial_priority'],x['pixel_rank']))[:6]
    selected=set(x['event_id'] for x in editorial)
    highest=[x for x in ordered if x['event_id'] not in selected][:4]
    selected.update(x['event_id'] for x in highest)
    controls=list(reversed([x for x in ordered if x['event_id'] not in selected]))[:2]
    selected.update(x['event_id'] for x in controls)
    # If there aren't six editorial tasks, fill spare slots with balanced
    # unselected probes; do not exceed 12 total windows.
    reserve=editorial+highest+controls
    for row in ordered:
        if len(reserve)>=MAX_WINDOWS:break
        if row['event_id'] not in selected:
            reserve.append(row)
            selected.add(row['event_id'])
    label={x['event_id']:'editorial_original_source_task' for x in editorial}
    label.update({x['event_id']:'high_pixel_change_review' for x in highest})
    label.update({x['event_id']:'low_pixel_change_control' for x in controls})
    result=[];deferred=list(cut_pts_deferred)
    for x in reserve:
        partition=x['partition']
        lo=bounds[partition]+CUT_MARGIN_MS
        hi=bounds[partition+1]-CUT_MARGIN_MS
        first,last=x['actual_pts_ms'][0],x['actual_pts_ms'][-1]
        a=max(lo,first-HALO_MS)
        z=min(hi,last+HALO_MS)
        if first<a or last>z or z-a<MIN_CLIP_MS:
            deferred.append({'event_id':x['event_id'],'reason':'insufficient_candidate_shot_continuity',
                             'source_frame_pts_ms_actual':x['actual_pts_ms']})
            continue
        result.append({
          'event_id':x['event_id'],'selection_reason':label.get(x['event_id'],'reserve_coverage_probe'),
          'time_window_ms_candidate_only':[a,z],
          'contains_three_verified_original_source_pts_ms':x['actual_pts_ms'],
          'pixel_change_review_priority_rank':x['pixel_rank'],
          'pixel_change_score_unverified_action':x['score'],
          'candidate_shot_partition_unverified':partition,
          'original_shot_and_action_human_verified':False,
          'speaking_identity_or_prosody_verified':False,
          'draft_stage_direction_accepted':False
        })
    return {
      'schema':'night-court-shot-bounded-original-continuity-review-plan/1',
      'source_video_sha256':source_plan['source_video_sha256'],
      'source_duration_ms':duration,
      'requested_video_excerpt_count':len(result),
      'requested_total_video_excerpt_ms':sum(x['time_window_ms_candidate_only'][1]-
                                          x['time_window_ms_candidate_only'][0] for x in result),
      'source_cut_candidates_not_confirmed_shots':len(scored),
      'source_triads_ranked':len(ranked),
      'source_triads_abstained_pts':len(abstained),
      'source_triads_deferred_actual_pts_cross_candidate_cut':len(cut_pts_deferred),
      'excerpt_media_decoded_or_retained':False,
      'human_continuous_video_review_done':False,
      'actor_gesture_voice_or_cut_verified':False,
      'scene_or_stage_directions_accepted':False,
      'full_original_episode_screenplay_accepted':False,
      'review_requests':result,
      'deferred_review_requests':deferred,
      'review_instructions':[
        'Check each excerpt against actual original continuous video and original audio.',
        'Candidate score cut boundaries can be false; verify edits, gesture continuity, participants and temporal context.',
        'Low-score controls are intentional: audit important low-motion comedy and sampling misses.',
        'Record physical actions and stage directions only after source-reviewed evidence, never from pixel score.'
      ]
    }
