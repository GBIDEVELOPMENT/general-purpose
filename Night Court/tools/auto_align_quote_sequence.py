#!/usr/bin/env python3
"""Automatic, order-constrained external quote alignment to caption-derived parts.

Unique lexical *proposals*, never authenticated speaker identities. No media,
third-party text downloading or caption mutation.
"""
from __future__ import annotations
import argparse
from difflib import SequenceMatcher
import json
from pathlib import Path
from build_caption_turns import parse_caption
from match_quote_anchors import norm, ROOT

def propose(meta, cues, sequence, threshold=.84):
    if sequence["episode_id"] != meta["episode_id"] or sequence["source_caption_sha256"] != meta["sha256"]:
        raise ValueError("Wrong episode or source SHA")
    units=[u for c in cues for u in parse_caption(c,meta)]
    quotes=sequence["anchors"]
    candidates=[]
    for q in quotes:
        words=norm(q["distinctive_fragment"]).split()
        if not words:
            raise ValueError("Empty quote")
        ranking=[]
        for j,u in enumerate(units):
            target=norm(u["source_text"])
            snippet=" ".join(words)
            score=SequenceMatcher(None,snippet,target,autojunk=False).ratio()
            if len(words)>=3 and snippet in target:
                score=max(score,.96)
            if score>=threshold:
                ranking.append((j,round(score,4)))
        candidates.append(ranking)
    # Dynamic program across *all* anchors. Strictly monotonic and unique
    # unit positions, with optional nonmatches rather than forced attributions.
    # A missing anchor cannot magically become a reliable speaker claim.
    states={-1:(0.0,[])}
    for ranking in candidates:
        new={}
        for prev,(value,path) in states.items():
            # abstain, with a modest penalty to prefer supported matches
            option=(value-.1,path+[None])
            if prev not in new or option[0]>new[prev][0]:new[prev]=option
            for idx,score in ranking:
                if idx<=prev:continue
                option=(value+score,path+[idx])
                if idx not in new or option[0]>new[idx][0]:new[idx]=option
        states=new
    best=max(states.values(),key=lambda x:x[0])[1] if states else []
    result=[]
    for q,idx,ranking in zip(quotes,best,candidates):
        # Do not promote duplicated near-equal lexical matches, even
        # when surrounding order would select one.
        ordered=sorted(ranking,key=lambda r:-r[1])
        ambiguous=(len(ordered)>1 and ordered[0][1]-ordered[1][1]<.06)
        accepted_idx=idx if idx is not None and not ambiguous else None
        u=units[accepted_idx] if accepted_idx is not None else None
        result.append({"source_character_claim":q["character"],
          "quote_fragment_word_count":len(norm(q["distinctive_fragment"]).split()),
          "cue":u["cue"] if u else None,"part":u["part"] if u else None,
          "unit_id":u["unit_id"] if u else None,
          "matched":u is not None,"ambiguous_lexical_match":ambiguous,
          "speaker_identity_accepted":False,"original_audio_reviewed":False})
    edges=[]
    for a,b in zip(result,result[1:]):
        if a["matched"] and b["matched"]:
            edges.append({"left_unit_id":a["unit_id"],"right_unit_id":b["unit_id"],
              "proposed_relationship":"same_speaker" if a["source_character_claim"]==b["source_character_claim"] else "speaker_change",
              "original_audio_reviewed":False})
    return {"schema":"night-court-automatic-quote-sequence/1",
      "episode_id":meta["episode_id"],"source_caption_sha256":meta["sha256"],
      "source_url":sequence["source_url"],"anchors":result,"edges":edges,
      "matched_count":sum(x["matched"] for x in result),
      "independently_verified":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--registry",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    seq=json.loads(a.registry.read_text("utf-8"))
    index=[json.loads(x) for x in (ROOT/"catalog/dialogue-index.jsonl").read_text("utf-8").splitlines() if x.strip()]
    hits=[x for x in index if x["episode_id"]==seq["episode_id"]]
    if len(hits)!=1:raise ValueError("Missing unique source edition")
    meta=json.loads((ROOT/hits[0]["manifest"]).read_text("utf-8"))
    if meta["sha256"]!=hits[0]["sha256"]:raise ValueError("Source manifest mismatch")
    cues=[json.loads(x) for x in (ROOT/"seasons"/seq["episode_id"][:3]/seq["episode_id"]/meta["segments_path"]).read_text("utf-8").splitlines() if x.strip()]
    if len(cues)!=hits[0]["cue_count"]:raise ValueError("Source cues changed")
    report=propose(meta,cues,seq)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print({"matched":report["matched_count"],"total":len(report["anchors"])})
if __name__=="__main__":main()
