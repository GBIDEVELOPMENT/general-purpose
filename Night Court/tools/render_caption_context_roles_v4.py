#!/usr/bin/env python3
"""Improve pilot readability with conservative explicitly provisional role names.

Existing complete original caption text, timed/untimed status, original-picture
action evidence, and the original draft remain untouched. Contextual roles are
editorial hypotheses sourced to nearby actual captions, NOT verified voices.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from render_caption_first_motion_edit_v3 import ROOT,render as render_v3
from build_caption_first_working_drafts import witness,SOURCE_SHA

OUTPUT="caption-first-speaker-context-v4"
LEDGER="dialogue-context-speakers-v1/proposals.json"
NAMES={"HARRY STONE","DAN FIELDING","SHEILA GARDINER",
       "ROZ RUSSELL","MAC ROBINSON"}
EXPECTED={"S01E01":18,"S09E19":20}


def context_proposals(episode,root=ROOT):
    if episode not in EXPECTED:
        raise ValueError("Two source-complete original pilot scripts only")
    path=root/"seasons"/episode[:3]/episode/"derived"/LEDGER
    raw=path.read_bytes()
    ledger=json.loads(raw)
    if (ledger.get("schema")!="night-court-explicit-and-nearby-dialogue-context-speaker-proposals/1"
        or ledger.get("episode_id")!=episode
        or ledger.get("source_caption_sha256")!=SOURCE_SHA[episode]
        or ledger.get("named_character_speaking_original_audio_verified") is not False
        or ledger.get("speaker_identified_from_images") is not False
        or ledger.get("character_attributions_are_editable_unverified_hypotheses") is not True
        or not isinstance(ledger.get("proposals"),list)
        or len(ledger["proposals"])!=EXPECTED[episode]):
        raise ValueError("Speaker proposal edition, counts or acceptance flags invalid")
    _,meta,cues,units,packages=witness(episode,root)
    by_cue={r["cue"]:r for r in cues}
    unit_ids={(x["cue"],x["part"]) for x in units}
    seen=set()
    for proposal in ledger["proposals"]:
        key=(proposal.get("cue"),proposal.get("part"))
        if (key in seen or key not in unit_ids
            or proposal.get("proposed_speaker_name") not in NAMES
            or proposal.get("independently_verified") is not False
            or proposal.get("contextual_label_only") is not True):
            raise ValueError("Unknown, duplicate or falsely verified named speaker")
        seen.add(key)
        phrase=proposal.get("source_cue_contains_text")
        if (not isinstance(phrase,str) or len(phrase)<3 or
            phrase.casefold() not in by_cue[key[0]]["text"].casefold()):
            raise ValueError("Quoted original subtitle source phrase does not exist")
        refs=proposal.get("source_context_cue_ids")
        if (not isinstance(refs,list) or key[0] not in refs
            or not all(type(n) is int and 1<=n<=len(cues) for n in refs)
            or len(refs)>7 or not isinstance(proposal.get("reason"),str)
            or len(proposal["reason"])>600):
            raise ValueError("Out-of-bounds unsupported contextual role reasoning")
    return ledger["proposals"],hashlib.sha256(raw).hexdigest()


def render(episode,root=ROOT):
    old,prev=render_v3(episode,root=root)
    proposals,ledger_sha=context_proposals(episode,root)
    output=old
    marked=[]
    for row in proposals:
        cue,part,name=row["cue"],row["part"],row["proposed_speaker_name"]
        ref=f"C{cue:03d}.{part}"
        original=(r"(?m)^\*\*VOICE · CHARACTER TO IDENTIFY\*\*  "
                  r"\*\["+re.escape(ref)+r" · (?:UNTIMED|\d{2}:\d{2}\.\d{3})\]\*$")
        matches=list(re.finditer(original,output))
        if len(matches)!=1:
            raise ValueError("Candidate speaker target not uniquely unresolved: "+ref)
        replacement=(f"**{name} · PROVISIONAL TEXT-CONTEXT ASSIGNMENT**  "
                     +matches[0].group(0).split("**  ",1)[1])
        output=output[:matches[0].start()]+replacement+output[matches[0].end():]
        marked.append({"cue":cue,"part":part,"speaker_name":name,
                       "source_context_cue_ids":row["source_context_cue_ids"],
                       "original_audio_verified":False})
    lead=(
      "## Source-caption contextual speaker editing\n\n"
      f"{len(proposals)} formerly anonymous dialogue units have received "
      "provisional names on the basis of direct self-identification, adjacent "
      "spoken address or explicit courtroom-role context. Each name is a "
      "TEXTUAL EDITING HYPOTHESIS, not voice-recognized, source-listened or "
      "visually identified. The original caption wording is unchanged and "
      "remaining unknown voices remain unnamed. Detailed cue-based reasons "
      f"are in `{LEDGER}`.\n\n"
    )
    marker="## Working episode dialogue"
    if output.count(marker)!=1:
        raise ValueError("Missing unique original dialogue section")
    output=output.replace(marker,lead+marker)
    metadata={
        "schema":"night-court-practical-caption-speaker-role-draft/4",
        "episode_id":episode,
        "original_caption_sha256":SOURCE_SHA[episode],
        "original_video_sha256":prev["original_source_video_sha256"],
        "all_original_dialogue_preserved_from_v3":True,
        "source_original_cue_count":prev["complete_original_held_caption_cues"],
        "source_picture_action_windows_preserved":prev["reviewed_picture_windows"],
        "contextual_role_proposals_applied":len(marked),
        "contextual_role_ledger_sha256":ledger_sha,
        "original_audio_speaker_identity_verified":False,
        "visual_face_character_identity_asserted":False,
        "speaker_candidate_status":"EDITABLE_UNVERIFIED_CAPTION_TEXT_CONTEXT_ONLY",
        "source_untimed_paragraph_timecodes_fabricated":False,
        "substantial_all_episode_speaker_attribution_complete":False,
        "all_video_actions_and_scene_transitions_verified":False,
        "editor_ready":False,
        "independently_av_certified":False,
        "proposed_speaker_turns":marked
    }
    return output.rstrip()+"\n",metadata


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode",choices=sorted(EXPECTED),required=True)
    parser.add_argument("--output-root",type=Path,default=ROOT)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    text,report=render(args.episode)
    dest=args.output_root/"seasons"/args.episode[:3]/args.episode/"derived"/OUTPUT
    files={
       "screenplay-dialogue-context-edit.md":text,
       "speaker-context-manifest.json":json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    }
    if args.check:
        for name,data in files.items():
            if not (dest/name).exists() or (dest/name).read_text("utf-8")!=data:
                raise ValueError("Unreconciled source-cited original speaker editorial script")
    else:
        dest.mkdir(parents=True,exist_ok=True)
        for name,data in files.items():
            (dest/name).write_text(data,encoding="utf-8")
    print(args.episode,report["source_original_cue_count"],"source cues preserved;",
          report["contextual_role_proposals_applied"],"source-caption based",
          "UNVERIFIED role labels; episode remains not editor-ready")


if __name__=="__main__":
    main()
