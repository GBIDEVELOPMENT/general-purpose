#!/usr/bin/env python3
"""Align privately acquired 1984–92 production-script text to held caption parts.

No acquisition, upload, AI guessing or automatic speaker promotion. A production
script is *not* a complete broadcast-performance witness: revised, improvised,
cut and additional lines can differ. Only well-localized high-agreement lexical
candidate matches are offered, with ambiguity and role-conflict abstentions.
"""
from __future__ import annotations

import argparse
from difflib import SequenceMatcher
import hashlib
import json
import re
from pathlib import Path

from build_caption_turns import parse_caption
from build_pilot_fan_beat_cards import ROOT, load_witness
from build_pilot_character_evidence import records_for_episode

SCHEMA="night-court-private-production-script-speaker-alignment/1"
ALIASES={
 "HARRY":"HARRY STONE","HARRY STONE":"HARRY STONE",
 "JUDGE STONE":"HARRY STONE","DAN":"DAN FIELDING",
 "DAN FIELDING":"DAN FIELDING","LANA":"LANA WAGNER",
 "LANA WAGNER":"LANA WAGNER","SHEILA":"SHEILA GARDINER",
 "SHEILA GARDINER":"SHEILA GARDINER","BULL":"BULL SHANNON",
 "BULL SHANNON":"BULL SHANNON","SELMA":"SELMA HACKER",
 "SELMA HACKER":"SELMA HACKER","ROZ":"ROZ RUSSELL",
 "ROZ RUSSELL":"ROZ RUSSELL","CHRISTINE":"CHRISTINE SULLIVAN",
 "CHRISTINE SULLIVAN":"CHRISTINE SULLIVAN","MAC":"MAC ROBINSON",
 "MAC ROBINSON":"MAC ROBINSON","PHIL":"PHIL KERR",
 "PHIL KERR":"PHIL KERR","LOUISE":"LOUISE KERR",
 "LOUISE KERR":"LOUISE KERR","CARLA":"CARLA BOUVIER",
 "CARLA BOUVIER":"CARLA BOUVIER","HACKSAW":"HACKSAW HAMMOND",
 "HACKSAW HAMMOND":"HACKSAW HAMMOND","PAINTER":"PAINTER",
 "COURIER":"COURIER","FINGERS":"FINGERS KIRBY",
 "FINGERS KIRBY":"FINGERS KIRBY","LISETTE":"LISETTE HOCHEISER",
 "LISETTE HOCHEISER":"LISETTE HOCHEISER","ALEX":"ALEX",
 "ALEX PATTERSON":"ALEX","THE GUY":"THE GUY",
 "THE GUY (PLAYING ALEX)":"THE GUY",
 "BARTENDER":"BARTENDER","CASHIER":"CASHIER"
}
STAGE=re.compile(r"^(?:INT\.|EXT\.|ACT\s|SCENE\s|FADE\s|CUT TO|OMITTED|END OF|TEASER\b)",re.I)
HEADER=re.compile(r"^\s*([A-Z][A-Z .'\-()]{1,48}?)(?:\s+\((?:CONT'D|O\.S\.|V\.O\.)\))?\s*$")


def norm(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9']+",text.casefold().replace("’","'")))


def parse_private_plaintext(text: str, ep: str) -> list[dict]:
    """Only recognize character headings in the known episode's role pool."""
    allowed = (
        {"HARRY STONE","DAN FIELDING","LANA WAGNER","SHEILA GARDINER",
         "BULL SHANNON","SELMA HACKER","PHIL KERR","LOUISE KERR",
         "CARLA BOUVIER","HACKSAW HAMMOND","PAINTER","COURIER"}
        if ep=="S01E01" else
        {"HARRY STONE","DAN FIELDING","BULL SHANNON","MAC ROBINSON",
         "CHRISTINE SULLIVAN","ROZ RUSSELL","LISETTE HOCHEISER",
         "ALEX","THE GUY","FINGERS KIRBY","BARTENDER","CASHIER"}
    )
    output=[]
    current=None
    body=[]
    firstline=0
    def flush():
        if current and body:
            words=norm(" ".join(body)).split()
            if len(words)>=4:
                output.append({"character":current,
                    "dialogue":" ".join(body),"script_start_line":firstline})
    for i,line in enumerate(text.splitlines(),1):
        stripped=line.strip()
        m=HEADER.fullmatch(line)
        recognized=ALIASES.get(m.group(1).strip(),None) if m else None
        if recognized in allowed:
            flush()
            current=recognized
            body=[]
            firstline=i
            continue
        if not stripped:
            flush()
            current=None
            body=[]
            continue
        if STAGE.match(stripped) or stripped.startswith("(") and stripped.endswith(")"):
            # Stage directions are not dialogue or independent voice evidence.
            if STAGE.match(stripped):
                flush()
                current=None
                body=[]
            continue
        if current is not None:
            body.append(stripped)
    flush()
    return output


def source_units(root: Path, episode: str) -> tuple[list[dict],str]:
    meta,cues=load_witness(root,episode)
    units=[u for cue in cues for u in parse_caption(cue,meta)]
    if (episode=="S01E01" and len(units)!=404 or
        episode=="S09E19" and len(units)!=347):
        raise ValueError("Original caption speaking-unit ledger drift")
    return units,meta["sha256"]


def scored_windows(units: list[dict], spoken: str, threshold: float=.88,
                   max_span: int=6) -> list[tuple[float,int,int]]:
    if not 0.78<=threshold<=1 or not 1<=max_span<=10:
        raise ValueError("Unsafe fuzzy matching parameters")
    wanted=norm(spoken)
    if len(wanted.split())<4:
        return []
    candidates=[]
    for i in range(len(units)):
        bundle=[]
        for j in range(i,min(i+max_span,len(units))):
            bundle.append(norm(units[j]["source_text"]))
            candidate=" ".join(bundle)
            nwords=len(candidate.split())
            wanted_len=len(wanted.split())
            if nwords>max(wanted_len*2+6,60):
                break
            if nwords<max(3,int(wanted_len*.45)):
                continue
            ratio=SequenceMatcher(None,wanted,candidate,autojunk=False).ratio()
            # Exact source substring is still one dependent lexical witness,
            # not independent source sound authentication.
            if wanted in candidate and wanted_len>=6:
                ratio=max(ratio,0.94)
            if ratio>=threshold:
                candidates.append((round(ratio,5),i,j))
    candidates.sort(key=lambda t:(-t[0],t[1],t[2]))
    return candidates[:12]


def align(units: list[dict], transcript: list[dict], source_sha: str,
          threshold: float=.88) -> dict:
    accepted=[]
    ambiguous=[]
    missed=0
    prev_end=-1
    for block in transcript:
        ranked=[r for r in scored_windows(units,block["dialogue"],threshold)
                if r[1]>prev_end]
        if not ranked:
            missed+=1
            continue
        best=ranked[0]
        # Different boundaries for the very same source exchange can vary
        # without a competing speaker. Compare only distinct start positions.
        rivals=[r for r in ranked[1:] if r[1]!=best[1]]
        if rivals and best[0]-rivals[0][0]<.055:
            ambiguous.append({
                "script_line":block["script_start_line"],
                "character_claim":block["character"],
                "best_score":best[0],"rival_score":rivals[0][0],
                "accepted":False
            })
            continue
        matched=units[best[1]:best[2]+1]
        data={
            "character_claim":block["character"],
            "script_start_line":block["script_start_line"],
            "source_ref_first":f"C{matched[0]['cue']:03d}.{matched[0]['part']}",
            "source_ref_last":f"C{matched[-1]['cue']:03d}.{matched[-1]['part']}",
            "source_unit_ids":[f"C{u['cue']:03d}.{u['part']}" for u in matched],
            "source_sha256":source_sha,
            "lexical_match_score":best[0],
            "source_script_revision_not_broadcast_verified":True,
            "original_speech_identity_verified":False,
            "speaker_attribution_status":"production_script_lexical_match_proposal",
        }
        accepted.append(data)
        prev_end=best[2]
    return {"schema":SCHEMA,"matched_claims":accepted,
            "ambiguous_claims":ambiguous,"unmatched_script_blocks":missed,
            "source_audio_identity_verified":False}


def create(root: Path, episode: str, private_script: Path,
           output: Path, threshold: float=.88) -> dict:
    if episode not in ("S01E01","S09E19"):
        raise ValueError("Only the two original-series pilots are in scope")
    if output.resolve().is_relative_to(root.resolve()) or private_script.resolve().is_relative_to(root.resolve()):
        raise ValueError("Original screenplay text and private alignment output must stay outside repository")
    binary=private_script.read_bytes()
    if len(binary)>2_000_000:
        raise ValueError("Unexpectedly huge plaintext screenplay; extract a bounded source")
    blocks=parse_private_plaintext(binary.decode("utf-8-sig"),episode)
    if not blocks:
        raise ValueError("No recognizable episode character headings/dialogue: verify supplied edition, not 2023 revival")
    units,sha=source_units(root,episode)
    result=align(units,blocks,sha,threshold=threshold)
    old=records_for_episode(root,episode)
    unit_role={}
    for r in old:
        for ref in r["original_source_part_refs"]:
            unit_role[ref]=r["candidate_role"]
    for hit in result["matched_claims"]:
        found={unit_role[x] for x in hit["source_unit_ids"]}
        hit["existing_role_candidates"]=sorted(x for x in found if x)
        hit["conflicts_with_existing_named_role"]=any(
            x and x!=hit["character_claim"] for x in found)
        hit["contains_previously_unknown_source_unit"]=None in found
    result.update({
        "episode_id":episode,
        "original_caption_sha256":sha,
        "input_private_screenplay_sha256":hashlib.sha256(binary).hexdigest(),
        "recognized_script_role_blocks":len(blocks),
        "source_caption_units":len(units),
        "proposed_matches":len(result["matched_claims"]),
        "accepted_as_verified_original_speakers":0,
        "production_revision_match_does_not_prove_final_episode_identity":True,
    })
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n","utf-8")
    print(f"{len(result['matched_claims'])} script/caption lexical matches proposed; "
          "no production script text uploaded or output to stdout; no speaker identifications accepted")
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--episode",required=True,choices=["S01E01","S09E19"])
    p.add_argument("--script-text",type=Path,required=True,
                   help="Owner-provided private TXT extract from correct original-series production script")
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--threshold",type=float,default=.88)
    args=p.parse_args()
    create(ROOT,args.episode,args.script_text,args.output,args.threshold)


if __name__=="__main__":
    main()
