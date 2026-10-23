#!/usr/bin/env python3
"""Integrate sixteen verified Season 5/6 retrieval-artifact SRTs."""
import hashlib
import json
from pathlib import Path
import sys
from import_dialogue import import_one, rebuild_index, parse_timed, to_text
ROOT=Path(__file__).resolve().parents[1]
EPISODES={"S05E06","S05E07","S05E08","S05E09","S05E10","S05E11","S05E12","S05E13","S05E14","S05E16","S05E17","S05E18","S05E19","S05E20","S06E01","S06E02"}
def main(directory):
    report=json.loads((directory/"retrieval-report.json").read_text("utf-8"))
    items=report["items"]
    if len(items)!=16 or {r["episode_id"] for r in items}!=EPISODES:
        raise ValueError("Unexpected artifact episodes")
    imported=[]
    for row in items:
        episode=row["episode_id"]
        if row["status"]!="downloaded_unreviewed":raise ValueError("Unsuccessful source "+episode)
        source=directory/(episode+".en.srt")
        raw=source.read_bytes()
        if len(raw)>1_000_000 or hashlib.sha256(raw).hexdigest()!=row["sha256"]:
            raise ValueError("Artifact SHA mismatch "+episode)
        cues=parse_timed(to_text(raw)[0],"srt")
        opts={"episode":episode,"edition":"Subtitle Cat English late-season research witness",
            "language":"en","source_name":source.name,"source_url":row["source_url"],
            "rights_basis":"user_provided","confirmed":True,"complete":False,
            "notes":"Owner-directed private research acquisition; reuse status not adjudicated. Artifact run 40036236962."}
        import_one(source,opts)
        imported.append({"episode":episode,"source_sha256":row["sha256"],"cues":len(cues)})
    rebuild_index()
    target=ROOT/"research"/"s05-s06-sixteen-import-result.json"
    target.write_text(json.dumps({"source_run":40036236962,"artifact_id":12536369940,
        "source_count":len(imported),"items":imported,"audiovisual_completeness_verified":False},indent=2)+"\n")
if __name__=="__main__":main(Path(sys.argv[1]))
