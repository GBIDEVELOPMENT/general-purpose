#!/usr/bin/env python3
"""Validate exact original S09 source-turn split proposals without naming actors."""
import hashlib
import json
from pathlib import Path
from build_pilot_fan_beat_cards import ROOT, load_witness

LEDGER = ROOT / "research/pending-s09-p0-source-splits-v1.json"
SHA = "659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
EXPECT = {"C121.1":"Yeah, probably.","C206.1":"No, this whole thing",
          "C271.1":"No, really.","C290.1":"Was she?","C291.1":"He was me."}

def validate(root=ROOT, ledger_path=LEDGER):
    meta, cues = load_witness(Path(root), "S09E19")
    doc = json.loads(Path(ledger_path).read_text("utf-8"))
    if (meta["sha256"] != SHA or meta["timecoded"] is not False or
        doc.get("schema") != "night-court-p0-pending-source-exact-split-specs/1" or
        doc.get("original_witness_sha256") != SHA or
        doc.get("episode") != "S09E19" or
        doc.get("independently_original_av_verified") is not False or
        doc.get("original_untimed") is not True or
        doc.get("named_actor_roles_introduced") != 0):
        raise ValueError("Original S09 cue source or review status changed")
    rows=doc.get("source_cues")
    if not isinstance(rows,list) or len(rows)!=5 or {r.get("source_ref") for r in rows}!=set(EXPECT):
        raise ValueError("All five unresolved S09 original cue split proposals required")
    packets=[]
    for row in rows:
        ref=row["source_ref"]
        if (row.get("split_before")!=EXPECT[ref] or row.get("proposed_roles")!=[None,None]
            or row.get("source_soundtrack_verification") is not False
            or not isinstance(row.get("reason"),str) or len(row["reason"])<80):
            raise ValueError("Unsourced or overconfident actor turn attribution")
        text=cues[int(ref[1:4])-1]["text"]
        phrase=row["split_before"]
        if text.count(phrase)!=1:
            raise ValueError("Original cue does not contain one exact unique split anchor")
        pos=text.index(phrase)
        left,right=text[:pos],text[pos:]
        if not left.strip() or not right.strip() or left+right!=text:
            raise ValueError("Original speaker cue lost characters")
        packets.append({"source_ref":ref,"original_cue_sha256":hashlib.sha256(text.encode()).hexdigest(),
                        "candidate_char_offset":pos,"first_proposed_role":None,
                        "second_proposed_role":None,"original_av_verified":False})
    return packets

if __name__=="__main__":
    p=validate()
    print(f"{len(p)} source-exact candidate speaker splits; original 347 S09 cues intact; 0 actor IDs inferred")
