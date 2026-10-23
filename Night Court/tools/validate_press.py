#!/usr/bin/env python3
"""Validate source-specific contemporary press, fandom and archival conflicts."""
from pathlib import Path
from collections import Counter
from datetime import date
from urllib.parse import urlparse
import json

ROOT=Path(__file__).resolve().parents[1]
RESEARCH=ROOT/"research"

def jsonl(name):
    path=RESEARCH/name
    return [json.loads(s) for s in path.read_text("utf-8").splitlines() if s.strip()]

def main():
    sources=jsonl("contemporary-press-bibliography.jsonl")
    claims=jsonl("production-and-reception-claims.jsonl")
    conflicts=json.loads((RESEARCH/"source-conflicts.json").read_text("utf-8"))["discrepancies"]
    bibliography={s["id"]:s for s in sources}
    assert len(bibliography)==len(sources),"duplicate source IDs"
    for s in sources:
        assert s["id"] and s["title"] and s["outlet"] and s["summary_original"],s
        assert urlparse(s["url"]).scheme=="https",s["id"]
        assert s["rights"],s["id"]
        assert s["period"] in ("original_broadcast_era","archival_reference",
           "post_broadcast_reassessment","nostalgic_rewatch","modern_online_ratings",
           "mixed_era","secondary_reference"),s["id"]
        if s["published"]: date.fromisoformat(s["published"])
        assert s["kind"] and s["source_strength"],s["id"]
    ids=set()
    for c in claims:
        assert c["id"] not in ids,c["id"];ids.add(c["id"])
        assert c["supporting_sources"],c["id"]
        for sid in c["supporting_sources"]:
            assert sid in bibliography,(c["id"],sid)
        assert c["confidence"] in ("low","medium","high"),c["id"]
        assert c["claim_kind"] and c["caution"],c["id"]
        assert len(c["object"])>=25,c["id"]
    conflicts_ids=set()
    for c in conflicts:
        assert c["id"] not in conflicts_ids,c["id"];conflicts_ids.add(c["id"])
        assert len(c["observations"])>=2 and c["note"],c["id"]
        for ob in c["observations"]:
            assert urlparse(ob["url"]).scheme=="https",c["id"]
    assert len(sources)>=10 and len(claims)>=10 and len(conflicts)>=3
    print("PASS: press bibliography",len(sources),"attributed analytical claims",len(claims),
          "documented source conflicts",len(conflicts))
if __name__=="__main__":main()
