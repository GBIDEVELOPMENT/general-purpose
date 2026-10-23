#!/usr/bin/env python3
"""Index source-authored synopsis sentences as citation-addressable statements.

These are extracted encyclopedia claims, not verified events, verbatim
screenplay dialogue or generated plot conclusions. Sentence splits are
heuristic, with character offsets retained for reversibility.
"""
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
ABBREV=re.compile(r"(?:\bMr|\bMrs|\bMs|\bDr|\bSt|\bJr|\bSr|\be\.g|\bi\.e)\.$",re.I)

def spans(text):
    positions=[0]
    for m in re.finditer(r"(?<=[.!?])\s+(?=[\"'A-Z])",text):
        previous=text[positions[-1]:m.start()].rstrip()
        if ABBREV.search(previous[-12:]):continue
        positions.append(m.end())
    positions.append(len(text))
    for a,b in zip(positions,positions[1:]):
        raw=text[a:b]
        if not raw.strip():continue
        delta=len(raw)-len(raw.lstrip())
        stop=len(raw.rstrip())
        start=a+delta
        end=a+stop
        if end>start:yield (start,end,text[start:end])

def save(path,value):
    if not path.exists() or path.read_text("utf-8")!=value:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(value,"utf-8")

def main():
    source=ROOT/"catalog"/"episode-knowledge.jsonl"
    rows=[json.loads(x) for x in source.read_text("utf-8").splitlines() if x.strip()]
    assert len(rows)==193
    allstatements=[]
    for row in rows:
        episode=row["id"]
        statement_rows=[]
        for i,(start,end,statement) in enumerate(spans(row["plot_source_plaintext"]),1):
            named=[]
            for m in row["named_character_mentions"]:
                if any(start<=a and b<=end for a,b in m["text_offset_spans"]):
                    named.append(m["character_id"])
            statement_rows.append({
              "id":f"{episode}:WIKI-S{i:03d}",
              "episode_id":episode,
              "kind":"attributed_encyclopedia_source_statement_not_verified_event",
              "source_kind":"wikipedia_episode_capsule",
              "text":statement,
              "text_start":start,"text_end":end,
              "character_name_mentions":sorted(set(named)),
              "shared_capsule_for_composite_broadcast":False,
              "source_revision":row["source"]["revision"],
              "source_permalink":row["source"]["permalink"],
              "source_license":"CC BY-SA 4.0",
              "source_path":row["source"]["path"]})
        epjson=ROOT/"seasons"/episode[:3]/episode/"episode.json"
        obj=json.loads(epjson.read_text("utf-8"))
        for e in statement_rows:
            e["shared_capsule_for_composite_broadcast"]=bool(
                obj.get("wikipedia_production_metadata",{}).get("is_combined_broadcast_entry"))
        path=ROOT/"seasons"/episode[:3]/episode/"annotations"/"synopsis-statements.jsonl"
        save(path,"\n".join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in statement_rows)+"\n")
        allstatements.extend(statement_rows)
    dump="\n".join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in allstatements)+"\n"
    save(ROOT/"catalog"/"source-statements.jsonl",dump)
    report={"episodes":len(rows),"source_statements":len(allstatements),
       "sentence_splitting":"heuristic punctuation; with original plaintext byte-independent character offsets",
       "source_status":"third-party encyclopedia statements, not corroborated events, scenes, dialogue or jokes",
       "limitations":["Not an independent source per sentence",
                      "Source text for combined broadcasts may be repeated for two episode parts",
                      "Names inferred lexically; statements can be incomplete or misleading",
                      "No causal relation inferred from sentence order"]}
    save(ROOT/"catalog"/"source-statements-status.json",json.dumps(report,indent=2)+"\n")
    print("Indexed",len(allstatements),"source statements across",len(rows),"episodes")

if __name__=="__main__":main()
