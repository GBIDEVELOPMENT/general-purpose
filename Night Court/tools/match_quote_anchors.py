#!/usr/bin/env python3
"""Source-traceable, conservative episode quote -> caption candidate anchors.

Input registry deliberately holds only brief licensed/limited quotation excerpts,
not downloaded pages. Candidate match does NOT verify identity or speech.
"""
from __future__ import annotations
import argparse
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import unicodedata

ROOT=Path(__file__).resolve().parents[1]
SCHEMA="night-court-quote-anchor-registry/1"
def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold()
    s=s.replace("’","'").replace("…"," ")
    return " ".join(re.findall(r"[a-z0-9]+",s))
def matches(cues,entry,min_ratio=.88):
    target=norm(entry["excerpt"])
    words=target.split()
    if len(words)<3: return []
    found=[]
    for start in range(len(cues)):
        for width in (1,2,3,4):
            if start+width>len(cues):break
            selected=cues[start:start+width]
            candidate=norm(" ".join(c["text"] for c in selected))
            ratio=SequenceMatcher(None,target,candidate,autojunk=False).ratio()
            # Text may be a subpart of a larger cue; only very distinctive
            # long phrases qualify for partial/substring matches.
            if len(words)>=7 and target in candidate:
                ratio=max(ratio,.91)
            if ratio>=min_ratio:
                found.append({"cue_ids":[c["cue"] for c in selected],
                              "similarity":round(ratio,4),
                              "candidate_text_exact":candidate==target})
    found.sort(key=lambda x:(-x["similarity"],len(x["cue_ids"]),x["cue_ids"]))
    return found

def align(registry,episode,index,segments):
    if registry["schema"]!=SCHEMA:raise ValueError("registry schema")
    if any(q["episode_id"]!=episode for q in registry["quotes"]):
        raise ValueError("cross-episode quote")
    results=[]
    for q in registry["quotes"]:
        if not q.get("source_url","").startswith("https://"):
            raise ValueError("citation URL required")
        if not q.get("source_character") or not q.get("excerpt"):raise ValueError("quote attribution absent")
        ranked=matches(segments,q)
        if len(ranked)==1 or (ranked and (len(ranked)==1 or ranked[0]["similarity"]>ranked[1]["similarity"]+.06)):
            best=ranked[0]
        else:best=None
        usable=bool(best and best["similarity"]>=.92 and
                    (best["candidate_text_exact"] or len(norm(q["excerpt"]).split())>=7))
        results.append({"quote_id":q["quote_id"],"source_url":q["source_url"],
                        "source_character":q["source_character"],
                        "source_kind":q.get("source_kind","third_party_attribution"),
                        "candidate_cue_ids":best["cue_ids"] if usable else [],
                        "top_candidates":ranked[:3],
                        "match_status":"unique_lexical_candidate_unverified" if usable else "ambiguous_or_unmatched",
                        "speaker_identity_accepted":False,
                        "caption_turn_boundary_accepted":False,
                        "source_original_av_reviewed":False})
    return {"schema":"night-court-quote-anchor-candidates/1",
            "episode_id":episode,"source_caption_sha256":index["sha256"],
            "source_caption_version_id":index["version_id"],
            "candidates":results,
            "counts":{"quotes":len(results),"unique_lexical_candidates":sum(bool(x["candidate_cue_ids"]) for x in results)},
            "independently_verified":False}

def run(episode,registry,root=ROOT):
    index=[json.loads(x) for x in (root/"catalog/dialogue-index.jsonl").read_text("utf-8").splitlines() if x.strip()]
    index=[x for x in index if x["episode_id"]==episode]
    if len(index)!=1:raise ValueError("missing or duplicate episode source")
    meta=json.loads((root/index[0]["manifest"]).read_text("utf-8"))
    if meta["sha256"]!=index[0]["sha256"]:raise ValueError("source fingerprint mismatch")
    segments=[json.loads(x) for x in (root/"seasons"/episode[:3]/episode/meta["segments_path"]).read_text("utf-8").splitlines() if x.strip()]
    if len(segments)!=index[0]["cue_count"]:raise ValueError("caption count mismatch")
    return align(registry,episode,index[0],segments)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--episode",required=True)
    p.add_argument("--registry",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result=run(a.episode,json.loads(a.registry.read_text("utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(result["counts"])
if __name__=="__main__":main()
