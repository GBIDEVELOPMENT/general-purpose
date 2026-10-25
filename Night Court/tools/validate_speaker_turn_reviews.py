#!/usr/bin/env python3
"""Validate human-reviewed P0 boundary decisions without changing original captions.

A reviewed decision does not assert independent AV certification; this utility
only validates structure, source hash consistency and complete pair coverage.
"""
from __future__ import annotations
import json
from pathlib import Path

DECISIONS={"same_speaker","speaker_change","overlap","unresolved"}

def validate(proposals, reviews):
    if proposals.get("schema")!="night-court-p0-turn-boundaries/1":
        raise ValueError("Unknown P0 proposal schema")
    if reviews.get("schema")!="night-court-p0-reviewed-boundaries/1":
        raise ValueError("Unknown P0 review schema")
    for key in ("episode_id","source_sha256"):
        if not proposals.get(key) or reviews.get(key)!=proposals[key]:
            raise ValueError("Episode or original source mismatch: "+key)
    pairs=proposals["boundary_decisions"]
    expected={(p["left_unit_id"],p["right_unit_id"]) for p in pairs}
    if len(expected)!=len(pairs):raise ValueError("Duplicate proposed boundary")
    actual=set()
    for row in reviews.get("decisions",[]):
        pair=(row.get("left_unit_id"),row.get("right_unit_id"))
        if pair not in expected or pair in actual:
            raise ValueError("Foreign or duplicate review boundary")
        actual.add(pair)
        if row.get("decision") not in DECISIONS:
            raise ValueError("Unsupported boundary decision")
        accepted=row["decision"]!="unresolved"
        if accepted and (row.get("evidence_kind") not in ("original_audio","original_audiovisual") or
                         row.get("reviewed_source_sha256")!=proposals["source_sha256"] or
                         not row.get("reviewer_attested_original_source") or
                         not isinstance(row.get("evidence_location"),str) or
                         not row["evidence_location"].strip()):
            raise ValueError("Decision requires specific attested original-source evidence")
    if actual!=expected:raise ValueError("Incomplete boundary review; preserve unresolved rows")
    return {"episode_id":proposals["episode_id"],"source_sha256":proposals["source_sha256"],
            "reviewed":len(actual),"resolved":sum(r["decision"]!="unresolved" for r in reviews["decisions"]),
            "unresolved":sum(r["decision"]=="unresolved" for r in reviews["decisions"]),
            "all_boundaries_resolved":all(r["decision"]!="unresolved" for r in reviews["decisions"]),
            "independent_whole_episode_audiovisual_certification":False}

def review_template(proposals):
    return {"schema":"night-court-p0-reviewed-boundaries/1",
            "episode_id":proposals["episode_id"],"source_sha256":proposals["source_sha256"],
            "decisions":[{"left_unit_id":p["left_unit_id"],"right_unit_id":p["right_unit_id"],
                          "decision":"unresolved","evidence_kind":None,"evidence_location":None,
                          "reviewed_source_sha256":None,"reviewer_attested_original_source":False}
                         for p in proposals["boundary_decisions"]]}

def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--proposals",required=True,type=Path)
    p.add_argument("--reviews",type=Path)
    p.add_argument("--output-template",type=Path)
    a=p.parse_args()
    proposals=json.loads(a.proposals.read_text("utf-8"))
    if a.output_template:
        if a.output_template.exists():raise ValueError("Refusing to overwrite review file")
        a.output_template.parent.mkdir(parents=True,exist_ok=True)
        a.output_template.write_text(json.dumps(review_template(proposals),indent=2)+"\n",encoding="utf-8")
    if a.reviews:
        summary=validate(proposals,json.loads(a.reviews.read_text("utf-8")))
        print(json.dumps(summary,sort_keys=True))

if __name__=="__main__":main()
