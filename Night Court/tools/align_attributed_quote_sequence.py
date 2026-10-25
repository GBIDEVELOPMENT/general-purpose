#!/usr/bin/env python3
"""Compare source-attributed ordered quote snippets with caption parts.

Produces *unverified* local speaker/boundary proposals. Does not alter source
captions or promote online quotations into audiovisual truth.
"""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
from match_quote_anchors import norm,ROOT
from build_caption_turns import parse_caption

def sequence_proposals(metadata,cues,sequence):
    if sequence["episode_id"]!=metadata["episode_id"]:raise ValueError("episode mismatch")
    if sequence["source_caption_sha256"]!=metadata["sha256"]:raise ValueError("source SHA mismatch")
    expected=sequence["anchors"]
    if any(x["cue"]<1 or x["cue"]>len(cues) or x["part"]<1 for x in expected):
        raise ValueError("invalid source cue pointer")
    results=[];previous=None
    for x in expected:
        source=parse_caption(cues[x["cue"]-1],metadata)
        if x["part"]>len(source):raise ValueError("missing cue part")
        unit=source[x["part"]-1]
        cue_norm=norm(unit["source_text"])
        excerpt_norm=norm(x["distinctive_fragment"])
        matched=bool(excerpt_norm and excerpt_norm in cue_norm)
        key=(x["cue"],x["part"])
        if previous is not None and key<=previous:raise ValueError("sequence out of order")
        previous=key
        results.append({"cue":x["cue"],"part":x["part"],"unit_id":unit["unit_id"],
          "source_character_claim":x["character"],"fragment_lexically_supported":matched,
          "segment_sha256":hashlib.sha256(unit["source_text"].encode("utf-8")).hexdigest(),
          "speaker_identity_accepted":False,"original_av_verified":False})
    edges=[]
    for a,b in zip(results,results[1:]):
        edges.append({"left_unit_id":a["unit_id"],"right_unit_id":b["unit_id"],
          "proposed_relationship":"same_speaker" if a["source_character_claim"]==b["source_character_claim"] else "speaker_change",
          "both_fragments_supported":a["fragment_lexically_supported"] and b["fragment_lexically_supported"],
          "source_attribution_verified_by_original_audio":False})
    return {"schema":"night-court-online-quote-sequence-proposals/1","episode_id":metadata["episode_id"],
      "source_caption_sha256":metadata["sha256"],"source_url":sequence["source_url"],
      "source_dependency_group":sequence.get("source_dependency_group","unresolved"),
      "anchors":results,"adjacent_anchor_edges":edges,
      "lexically_supported":sum(a["fragment_lexically_supported"] for a in results),
      "independently_verified":False}
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument("--registry",type=Path,required=True)
 p.add_argument("--output",type=Path,required=True)
 a=p.parse_args();sequence=json.loads(a.registry.read_text("utf-8"))
 episode=sequence["episode_id"]
 index=[json.loads(line) for line in (ROOT/"catalog/dialogue-index.jsonl").read_text("utf-8").splitlines() if line.strip()]
 source=next(x for x in index if x["episode_id"]==episode)
 meta=json.loads((ROOT/source["manifest"]).read_text("utf-8"))
 cues=[json.loads(line) for line in (ROOT/"seasons"/episode[:3]/episode/meta["segments_path"]).read_text("utf-8").splitlines() if line.strip()]
 if len(cues)!=source["cue_count"] or meta["sha256"]!=source["sha256"]:raise ValueError("source changed")
 result=sequence_proposals(meta,cues,sequence)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print({"anchors":len(result["anchors"]),"lexically_supported":result["lexically_supported"],"edges":len(result["adjacent_anchor_edges"])})
if __name__=="__main__":main()
