#!/usr/bin/env python3
"""Readable caption-first Night Court screenplay drafts with reversible soft-wrap repair.

Keeps held words and source-cue chronology; no independent spoken-word or
source-video certification is invented. New role labels are provisional.
S09 join groups repair obvious untimed transcript line wrapping without
inventing timecodes or resolving ambiguous mixed-speaker paragraphs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from build_caption_first_working_drafts import ROOT,SOURCE_SHA,witness
from render_caption_context_roles_v4 import render as render_v4
from render_caption_first_scene_edit_v2 import STORY_BEATS

OUTPUT="caption-first-readable-screenplay-v5"
LEDGER="dialogue-context-speakers-v5/editorial-additions.json"
EXPECTED_ADDITIONS={"S01E01":98,"S09E19":56}
NEW_NAMES={"HARRY STONE","ROZ RUSSELL","CHRISTINE SULLIVAN",
           "DAN FIELDING","MAC ROBINSON","ALEX PATTERSON"}
# These are single utterances wrapped by the untimed source text layout.
# No claim of voice-change detection is made.
S09_CONTINUATION_GROUPS=[
    [7,8],[10,11],[23,24],[28,29],[30,31],[63,64],
    [70,71],[75,76],[79,80],[82,83],[84,85,86],[89,90],
    [108,109],[131,132],[134,135],[147,148],[169,170],
    [175,176,177],[203,204],[207,208],[213,214],[216,217],
    [230,231],[245,246],[258,259],[273,274],[315,316],
    [318,319],[322,323,324],[326,327],[329,330],[336,337],[340,341]
]
SOURCE_ROLE=re.compile(
    r"(?m)^\*\*(?P<label>[^\n*]+)\*\*  \*\[C(?P<cue>\d{3})\.(?P<part>\d+) · "
    r"(?P<when>UNTIMED|\d{2}:\d{2}\.\d{3})\]\*$"
)


def get_additions(episode,cues,units,root=ROOT):
    ledger_path=root/"seasons"/episode[:3]/episode/"derived"/LEDGER
    binary=ledger_path.read_bytes()
    doc=json.loads(binary)
    rows=doc.get("proposals")
    if (doc.get("schema")!="night-court-v5-additional-subtitle-context-role-proposals/1"
        or doc.get("episode_id")!=episode
        or doc.get("source_caption_sha256")!=SOURCE_SHA[episode]
        or doc.get("additional_role_count")!=EXPECTED_ADDITIONS[episode]
        or doc.get("original_audio_spoken_identity_verified") is not False
        or doc.get("visual_character_identity_verified") is not False
        or doc.get("original_source_words_modified") is not False
        or not isinstance(rows,list) or len(rows)!=EXPECTED_ADDITIONS[episode]):
        raise ValueError("Unexpected original-subtitle editorial role witness")
    lookup={(u["cue"],u["part"]) for u in units}
    seen=set()
    result={}
    for row in rows:
        key=(row.get("cue"),row.get("part"))
        cue,part=key
        if (key in seen or key not in lookup or row.get("proposed_speaker_name") not in NEW_NAMES
            or row.get("status")!="PROVISIONAL_CONTEXT_NOT_AUDIO_VERIFIED"
            or not isinstance(row.get("original_source_text_excerpt"),str)
            or not cues[cue-1]["text"].startswith(row["original_source_text_excerpt"])
            or not isinstance(row.get("source_context_cue_ids"),list)
            or cue not in row["source_context_cue_ids"]
            or not all(type(x) is int and 1<=x<=len(cues)
                       for x in row["source_context_cue_ids"])):
            raise ValueError("Non-source-grounded or duplicate cue speaker proposal")
        seen.add(key)
        result[key]=row
    return result,hashlib.sha256(binary).hexdigest()


def v4_labels(episode,units,root=ROOT):
    text,prior=render_v4(episode,root=root)
    names={}
    for m in SOURCE_ROLE.finditer(text):
        key=(int(m.group("cue")),int(m.group("part")))
        if key in names:raise ValueError("Duplicate original source cue unit in v4")
        names[key]=m.group("label")
    if set(names)!={(u["cue"],u["part"]) for u in units}:
        raise ValueError("Original v4 speaking unit coverage is not complete")
    return names,text,prior


def join_groups(episode,cues):
    groups=S09_CONTINUATION_GROUPS if episode=="S09E19" else []
    by_start={}
    used=set()
    for group in groups:
        if (not isinstance(group,list) or len(group)<2
            or any(type(n) is not int or n<1 or n>len(cues) for n in group)
            or group!=list(range(group[0],group[-1]+1))
            or any(n in used for n in group)):
            raise ValueError("Invalid or overlapping untimed paragraph restoration")
        by_start[group[0]]=group
        used.update(group)
    return by_start,used


def render(episode,root=ROOT):
    if episode not in EXPECTED_ADDITIONS:raise ValueError("Only two approved originals")
    _item,meta,cues,units,packets=witness(episode,root=root)
    names,old,previous=v4_labels(episode,units,root)
    additions,add_sha=get_additions(episode,cues,units,root)
    overlap=set(additions)&{k for k,v in names.items()
                           if not v.startswith("VOICE · CHARACTER TO IDENTIFY")}
    if overlap:raise ValueError("Additional role proposals may not override existing names")
    for k,row in additions.items():
        names[k]=row["proposed_speaker_name"]+" · PROVISIONAL TEXT-CONTEXT ASSIGNMENT"
    if episode=="S09E19" and meta["timecoded"] is not False:
        raise ValueError("Original S09 text must stay untimed")
    if episode=="S01E01" and meta["timecoded"] is not True:
        raise ValueError("Original S01 SRT must remain timed")
    units_by_cue={}
    for unit in units:units_by_cue.setdefault(unit["cue"],[]).append(unit)
    starters,grouped=join_groups(episode,cues)
    scenes={cue:title for cue,title in STORY_BEATS.get(episode,[])}
    if episode=="S01E01":
        scenes={
          1:"INT. COURT OFFICE · sample-supported location, start time unverified",
          77:"EXT. CITY BRIDGE / INT. COURTROOM · picture transition near source 04:21–04:39; cut time unverified",
          154:"INT. BOOK-LINED COURT OFFICE · sample-supported around the ten-minute passage",
          183:"INT. COURTROOM · sample-supported return; cut time unverified"
        }
    # Preserve source picture chronology and bounded motion source text from
    # v4, separate from the episode script rather than asserting synchronized
    # dialogue for S09's untimed source paragraphs.
    first_header="## Working episode dialogue"
    if old.count(first_header)!=1:raise ValueError("Missing trusted original v4 dialogue")
    research=old.split(first_header,1)[0]
    research=research.replace("CAPTION-FIRST WORKING SCREENPLAY DRAFT  |  EDITORIAL PASS 1",
                             "SOURCE-VERIFIED VISUAL EVIDENCE APPENDIX / prior reading pass")
    body=[
      f"# {episode} · {('All You Need Is Love' if episode=='S01E01' else 'P.S. Do I Know You?')}",
      "",
      "## Readable original-caption screenplay · editorial draft 5",
      "",
      "Complete held-source dialogue, editorial character labels and visible",
      "picture-supported scene research, NOT a finalized production screenplay.",
      "Named voices are provisional unless independently authenticated;",
      "unidentified speakers remain explicitly unidentified. The S09 original",
      "transcript is UNTIMED. Scene headings from source text or widely spaced",
      "sampled frames are editorial reading aids, not verified shot boundaries.",
      "",
      f"Original subtitle/transcript SHA-256: `{SOURCE_SHA[episode]}`",
      f"Original source cues/paragraphs: {len(cues)}",
      "",
    ]
    original_cues_written=[]
    original_units_written=[]
    unknown=[]
    joined_count=0
    inferred_count=0
    source_word_source=[]
    i=1
    while i<=len(cues):
        if i in scenes:
            body.extend(["",f"### {scenes[i]}","",
                  "*Editorial grouping only; transitions and blocking require",
                  "continuous original source AV confirmation.*",""])
        if i in grouped and i not in starters:
            raise ValueError("Broken original continuation group pointer")
        join=starters.get(i,[i])
        if len(join)>1:
            # Every grouped record must contain just one speaking unit, since
            # source dash-typography or explicit voice splits remain distinct.
            if any(len(units_by_cue[c])!=1 for c in join):
                raise ValueError("Mixed-voice source caption cannot be combined automatically")
            # A titled story boundary is never swallowed by an utterance.
            if any(c in scenes for c in join[1:]):
                raise ValueError("Unreviewed source-story transition cannot be collapsed")
            chosen=[names[(c,1)] for c in join]
            actual={x for x in chosen if not x.startswith("VOICE · CHARACTER TO IDENTIFY")}
            if len(actual)>1:
                raise ValueError("Contradictory candidate speaker IDs in soft-wrap group")
            label=next(iter(actual),"UNIDENTIFIED SPEAKER · unresolved source voice")
            source_text=" ".join(units_by_cue[c][0]["source_text"].strip().replace("\r","")
                                 for c in join)
            # Cosmetic JOIN only: preserve exact complete original source
            # tokens/segments in a machine-checkable manifest.
            source_ids=[(c,1) for c in join]
            joined_count+=len(join)-1
            if actual:inferred_count+=len(join)-len(actual)
        else:
            if len(units_by_cue[i])>1:
                for unit in units_by_cue[i]:
                    label=names[(i,unit["part"])]
                    if label.startswith("VOICE · CHARACTER TO IDENTIFY"):
                        label="UNIDENTIFIED SPEAKER · unresolved source voice"
                    ref=f"C{i:03d}.{unit['part']}"
                    timing=(f" · {unit['start_ms']/1000:.3f}s original SRT"
                            if meta["timecoded"] else " · UNTIMED original paragraph")
                    body.extend([f"**{label}**",unit["source_text"].strip(),
                                 f"*Source: {ref}{timing}*",""])
                    original_units_written.append((i,unit["part"]))
                    if label.startswith("UNIDENTIFIED"):unknown.append(ref)
                    source_word_source.append(unit["source_text"].strip())
                original_cues_written.append(i)
                i+=1
                continue
            source_ids=[(i,1)]
            label=names[(i,1)]
            source_text=units_by_cue[i][0]["source_text"].strip()
            if label.startswith("VOICE · CHARACTER TO IDENTIFY"):
                label="UNIDENTIFIED SPEAKER · unresolved source voice"
        start,end=join[0],join[-1]
        citation=(f"C{start:03d}.1" if start==end
                  else f"C{start:03d}.1–C{end:03d}.1")
        when=(f"{cues[start-1]['start_ms']/1000:.3f}s original SRT"
              if meta["timecoded"] else "UNTIMED original source")
        body.extend([f"**{label}**",source_text,
                     f"*Source: {citation} · {when}*",""])
        if label.startswith("UNIDENTIFIED"):
            unknown.extend(f"C{c:03d}.1" for c in join)
        original_cues_written.extend(join)
        original_units_written.extend(source_ids)
        source_word_source.extend(units_by_cue[c][0]["source_text"].strip() for c in join)
        i=end+1
    if original_cues_written!=list(range(1,len(cues)+1)):
        raise ValueError("Original source paragraph order or coverage lost")
    expected_units=[(u["cue"],u["part"]) for u in units]
    if original_units_written!=expected_units:
        raise ValueError("Source dialogue unit omitted or duplicated")
    if len(source_word_source)!=len(units):
        raise ValueError("Split voice source lost")
    body.extend(["","## Source-picture motion and setting evidence", "",
      "The following observed frames and short original movie sequences",
      "are included as a separate source appendix. For S09, their video",
      "times must NOT be treated as timestamps of the transcript paragraphs.",
      ""])
    research=research.split("# "+episode+" ·",1)[-1]
    # Retain source observations and source motion provenance from v4.
    for required in ("## Directly observed original-video scene",
                     "## Actual source-picture physical business"):
        if required not in research:raise ValueError("Original video evidence missing")
    body.append(research.split("## Directly observed original-video scene",1)[1].split(
                "## Source-caption contextual speaker editing",1)[0].join(
                ["## Directly observed original-video scene",""]))
    body.extend(["","## Remaining source-editor review", "",
       f"Original source units: {len(units)}; dialogue paragraph wraps repaired: {joined_count}.",
       f"Additional named speaker proposals: {len(additions)}.",
       f"Source cue/part units still labeled unknown: {len(unknown)}.",
       "Unreviewed source words, actor identity, cut continuity, silent gags",
       "and every ambiguous caption collision remain editor tasks.",
       "All speaker proposals are EDITABLE and NOT independently AV-certified.",
       ""])
    output="\n".join(body).rstrip()+"\n"
    manifest={
      "schema":"night-court-readable-source-preserving-script/5",
      "episode_id":episode,"source_caption_sha256":SOURCE_SHA[episode],
      "source_original_cues":len(cues),"source_original_units":len(units),
      "rendered_source_cue_ids_in_order":original_cues_written,
      "rendered_source_cue_part_ids_in_order":[f"C{c:03d}.{p}" for c,p in original_units_written],
      "source_unit_text_sha256_in_order":[hashlib.sha256(s.encode("utf-8")).hexdigest() for s in source_word_source],
      "new_provisional_context_label_count":len(additions),
      "new_provisional_context_ledger_sha256":add_sha,
      "preexisting_context_label_count":previous["contextual_role_proposals_applied"],
      "paragraph_soft_wrapped_original_text_records_joined":joined_count,
      "original_source_untimed_paragraphs_still_untimed":episode=="S09E19",
      "source_dialogue_words_rewritten":False,
      "all_original_source_dialogue_units_preserved":True,
      "speakers_original_audio_verified":False,
      "original_video_actors_source_matched_to_speakers":False,
      "full_av_screenplay_accepted":False,
      "screenplay_editor_ready":False,
      "quality_state":"READABLE_FULL_HELD_SOURCE_DIALOGUE_PROVISIONAL_CAST_SCENE_ACTION_EDIT",
      "photo_motion_provenance_retained":True,
      "unknown_source_dialogue_unit_count":len(unknown)
    }
    review={"schema":"night-court-v5-remaining-speaker-review/1",
            "episode_id":episode,
            "source_caption_sha256":SOURCE_SHA[episode],
            "unknown_source_cue_part_ids":unknown,
            "source_audio_listened_for_these_roles":False,
            "explicit_scope":"Remaining labels unknown, not yet source voice authenticated"}
    return output,manifest,review


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--episode",choices=EXPECTED_ADDITIONS,required=True)
    ap.add_argument("--output-root",type=Path,default=ROOT)
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    script,manifest,review=render(args.episode)
    target=args.output_root/"seasons"/args.episode[:3]/args.episode/"derived"/OUTPUT
    exports={
      "screenplay-readable.md":script,
      "reader-manifest.json":json.dumps(manifest,indent=2)+"\n",
      "unidentified-dialogue-review.json":json.dumps(review,indent=2)+"\n"}
    if args.check:
        for name,text in exports.items():
            f=target/name
            if not f.exists() or f.read_text("utf-8")!=text:
                raise ValueError("Stale/missing exact-original source readable screenplay: "+str(f))
    else:
        target.mkdir(parents=True,exist_ok=True)
        for name,text in exports.items():(target/name).write_text(text,encoding="utf-8")
    print(args.episode,"readable scene/editor screenplay:",
          manifest["source_original_cues"],"original source cues,",
          manifest["new_provisional_context_label_count"],"new text-only character names,",
          manifest["paragraph_soft_wrapped_original_text_records_joined"],
          "broken source paragraph wraps fixed, no AV acceptance")


if __name__=="__main__":
    main()
