#!/usr/bin/env python3
"""Query the original Night Court evidence corpus without inventing events.

Examples:
  python "Night Court/tools/query_corpus.py" --text blizzard
  python "Night Court/tools/query_corpus.py" --character dan-fielding --season 2
  python "Night Court/tools/query_corpus.py" --actor "Rita Taggart"
  python "Night Court/tools/query_corpus.py" --theme romantic-relationships
"""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(path):
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def main():
    p=argparse.ArgumentParser(description=__doc__,
       formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--text",help="case-insensitive phrase in source-derived synopsis or title")
    p.add_argument("--character",help="canonical character mention ID, e.g. dan-fielding")
    p.add_argument("--theme",help="lexical theme key, e.g. romantic-relationships")
    p.add_argument("--actor",help="actor display-name substring in TVmaze episode guest credits")
    p.add_argument("--director",help="director credit substring")
    p.add_argument("--writer",help="writer credit-line substring")
    p.add_argument("--season",type=int,choices=range(1,10))
    p.add_argument("--limit",type=int,default=20)
    args=p.parse_args()
    if args.limit<1 or args.limit>193:p.error("--limit must be 1..193")
    docs=load(ROOT/"catalog"/"episode-knowledge.jsonl")
    guest_ids=None
    if args.actor:
        graphfile=ROOT/"catalog"/"cast-relationship-graph.json"
        if not graphfile.exists():
            p.error("Actor guest-credit graph missing; build_cast_graph.py must run first")
        graph=json.loads(graphfile.read_text("utf-8"))
        people_ids={k for k,v in graph["persons"].items()
                    if args.actor.casefold() in (v["display_name"] or "").casefold()}
        # Episode presence is NOT inferred from show-level main cast membership.
        guest_ids={e["episode_id"] for e in graph["credits"]
                   if e.get("credit_scope")=="episode_guest_cast"
                   and e.get("person_id") in people_ids}
    selected=[]
    for d in docs:
        if args.season and d["season"]!=args.season:continue
        if args.text and args.text.casefold() not in (d["title"]+" "+d["plot_source_plaintext"]).casefold():continue
        if args.character and not any(args.character.casefold()==m["character_id"].casefold()
             for m in d["named_character_mentions"]):continue
        if args.theme and not any(args.theme.casefold()==x["topic"].casefold()
             for x in d["theme_lexical_cues"]):continue
        if args.director and args.director.casefold() not in (d["production"]["director"] or "").casefold():continue
        if args.writer and args.writer.casefold() not in (d["production"]["writer_credit"] or "").casefold():continue
        if guest_ids is not None and d["id"] not in guest_ids:continue
        selected.append({"id":d["id"],"title":d["title"],"airdate":d["broadcast_date"],
            "director":d["production"]["director"],
            "mentioned_characters":[m["character_id"] for m in d["named_character_mentions"]],
            "lexical_topics":[x["topic"] for x in d["theme_lexical_cues"]],
            "source":d["source"]["permalink"],
            "dossier":"seasons/S%02d/%s/derived/evidence-dossier.json"%(d["season"],d["id"])})
    print(json.dumps({"matches":len(selected),"shown":min(len(selected),args.limit),
         "warning":"Mentions are capsule text occurrences, guest roles are TVmaze credits, and topics are lexical cues, not proven appearances, events, moods or jokes.",
         "results":selected[:args.limit]},indent=2,ensure_ascii=False))

if __name__=="__main__":main()
