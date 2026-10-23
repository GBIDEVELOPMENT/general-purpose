#!/usr/bin/env python3
"""Import verified staging artifact into original-series episode holdings."""
import json, csv, hashlib, sys
from pathlib import Path
from import_dialogue import import_one, rebuild_index, parse_timed, to_text

ROOT=Path(__file__).resolve().parents[1]
def main(folder):
    report=json.loads((folder/"retrieval-report.json").read_text())
    items=report["items"]
    expected={f"S{s:02d}E{e:02d}" for s in (3,4) for e in range(1,23)}
    if len(items)!=44 or {x["episode_id"] for x in items}!=expected:
        raise ValueError("Staging has incomplete episode manifest")
    summary=[]
    for x in items:
        ep=x["episode_id"]
        if x["status"]!="downloaded_unreviewed":
            raise ValueError("Unsuccessful staged retrieval for "+ep)
        f=folder/(ep+".en.srt")
        if not f.is_file() or f.stat().st_size>1_000_000:
            raise ValueError("Missing or oversized SRT "+ep)
        raw=f.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=x["sha256"]:
            raise ValueError("Staging source SHA mismatch "+ep)
        cues=parse_timed(to_text(raw)[0],"srt")
        if len(cues)!=x["cue_marker_count"]:
            raise ValueError("Cue count mismatch "+ep)
        # User identified sources for restricted private research; retention rights
        # remain expressly unadjudicated and completeness unverified.
        opts={"episode":ep,"edition":"Subtitle Cat 480p DVD English research witness",
              "language":"en","source_name":x["title"]+" / Subtitle Cat SRT",
              "source_url":x["source_url"],
              "rights_basis":"user_provided","confirmed":True,"complete":False,
              "notes":"User-directed acquisition for private research; third-party copyright/reuse status not independently established. Source SHA checked against retrieval artifact."}
        import_one(f,opts)
        summary.append({"episode_id":ep,"sha256":x["sha256"],"cues":len(cues),"bytes":len(raw),
                       "source_url":x["source_url"],"audiovisual_complete":False})
    rebuild_index()
    target=ROOT/"research"/"s03-s04-artifact-ingestion-report.json"
    target.write_text(json.dumps({"source_run":40035117368,"artifact_id":12535769451,
       "source_kind":"third_party_caption_witness","count":len(summary),"items":summary},
       indent=2,ensure_ascii=False)+"\n")
    print("Imported",len(summary),"S03/S04 original English subtitle witnesses")
if __name__=="__main__":
    main(Path(sys.argv[1]))
