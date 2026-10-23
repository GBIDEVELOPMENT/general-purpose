#!/usr/bin/env python3
"""Integrate nine verified late-season retrieval-artifact SRTs."""
import hashlib
import json
from pathlib import Path
import sys
from import_dialogue import import_one, rebuild_index, parse_timed, to_text
ROOT=Path(__file__).resolve().parents[1]
EPISODES={"S05E01","S07E03","S07E04","S07E23","S08E06","S09E06","S09E20","S09E21","S09E22"}
def main(directory):
    report=json.loads((directory/"retrieval-report.json").read_text("utf-8"))
    items=report["items"]
    if len(items)!=9 or {r["episode_id"] for r in items}!=EPISODES:
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
            "notes":"Owner-directed private research acquisition; reuse status not adjudicated. Artifact run 40035810168."}
        import_one(source,opts)
        imported.append({"episode":episode,"source_sha256":row["sha256"],"cues":len(cues)})
    rebuild_index()
    target=ROOT/"research"/"s05-s09-import-result.json"
    target.write_text(json.dumps({"source_run":40035810168,"artifact_id":12537211693,
        "source_count":len(imported),"items":imported,"audiovisual_completeness_verified":False},indent=2)+"\n")
if __name__=="__main__":main(Path(sys.argv[1]))
