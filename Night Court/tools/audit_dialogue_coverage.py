#!/usr/bin/env python3
"""Produce an accurate, 193-row inventory of *held* Night Court dialogue versions.

"Declared complete" records the submitter's metadata. "Verified complete"
remains false until independent edition-aligned audiovisual acceptance.
"""
from collections import Counter
from pathlib import Path
import csv
import io
import json

ROOT=Path(__file__).resolve().parents[1]
SEASONS=[13,22,22,22,22,22,24,24,22]

def main():
    index=ROOT/"catalog"/"dialogue-index.jsonl"
    versions=[json.loads(line) for line in index.read_text("utf-8").splitlines()
              if line.strip()] if index.exists() else []
    by_ep={}
    for row in versions:
        by_ep.setdefault(row["episode_id"],[]).append(row)
    table=[]
    for season,count in enumerate(SEASONS,1):
        for number in range(1,count+1):
            id=f"S{season:02d}E{number:02d}"
            e=json.loads((ROOT/"seasons"/f"S{season:02d}"/id/"episode.json").read_text("utf-8"))
            tracks=by_ep.get(id,[])
            timed=[v for v in tracks if v["format"] in ("srt","vtt")]
            plain=[v for v in tracks if v["format"]=="txt"]
            declared=[v for v in tracks if v["declared_complete"]]
            table.append({
                "id":id,"season":season,"episode":number,"title":e["title"],
                "held_dialogue_versions":len(tracks),
                "held_timed_caption_tracks":len(timed),
                "held_plain_transcripts":len(plain),
                "submitter_declared_complete_versions":len(declared),
                "independently_video_verified_complete":0,
                "status":"source_supplied_completeness_unverified" if declared else
                  ("partially_held_or_unknown_completeness" if tracks else "no_held_dialogue"),
                "version_ids":";".join(sorted(v["version_id"] for v in tracks))
            })
    assert len(table)==193
    counts=Counter(r["status"] for r in table)
    result={
        "series":"night-court-1984",
        "total_episodes":193,
        "held_dialogue_versions":len(versions),
        "episodes_with_held_dialogue":sum(r["held_dialogue_versions"]>0 for r in table),
        "episodes_with_any_claimed_complete_source":sum(r["submitter_declared_complete_versions"]>0 for r in table),
        "independently_verified_complete_episodes":0,
        "status_counts":dict(sorted(counts.items())),
        "quality_rule":"Source-file presence and submitter's stated completeness are never audiovisual completeness validation.",
        "rows":table
    }
    out=ROOT/"catalog"/"dialogue-coverage.json"
    new=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
    if not out.exists() or out.read_text("utf-8")!=new:out.write_text(new,"utf-8")
    csv_path=ROOT/"catalog"/"dialogue-coverage.csv"
    temp=io.StringIO()
    writer=csv.DictWriter(temp,fieldnames=table[0].keys())
    writer.writeheader()
    writer.writerows(table)
    if not csv_path.exists() or csv_path.read_text("utf-8")!=temp.getvalue():
        csv_path.write_text(temp.getvalue(),"utf-8")
    print("DIALOGUE COVERAGE:",result["episodes_with_held_dialogue"],"/193 episodes with bytes;",
          result["episodes_with_any_claimed_complete_source"],"source-claimed complete;",
          result["independently_verified_complete_episodes"],"AV-verified complete")

if __name__=="__main__":
    main()
