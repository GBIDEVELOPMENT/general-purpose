#!/usr/bin/env python3
"""Preserve checked S05-S09 caption witnesses discovered by the bounded worker."""
import hashlib
import json
from pathlib import Path
import re
import sys
from import_dialogue import import_one, rebuild_index, prepare

ROOT = Path(__file__).resolve().parents[1]
def main(folder):
    result = json.loads((folder/"retrieval-report.json").read_text("utf-8"))
    if result["series"]!="night-court-1984" or result["targeted_missing_episode_count"]!=89:
        raise ValueError("Incompatible Night Court report")
    eligible = [x for x in result["items"] if x["status"]=="downloaded_unreviewed"]
    if result["downloaded"]!=len(eligible) or len({x["episode_id"] for x in eligible})!=len(eligible):
        raise ValueError("Duplicate or inconsistent accession report")
    prepared = []
    rejected = []
    for x in eligible:
        ep = x["episode_id"]
        if not re.fullmatch(r"S0[5-9]E\d{2}",ep):
            raise ValueError("Out-of-scope episode: "+ep)
        file = folder/(ep+".en.srt")
        data = file.read_bytes()
        if len(data)!=x["size_bytes"] or hashlib.sha256(data).hexdigest()!=x["sha256"]:
            raise ValueError("Source integrity failure: "+ep)
        # Don't imply review/licensing or that actual audiovisual dialogue is complete.
        metadata={"episode":ep,"edition":"Subtitle Cat English online caption research witness",
                  "language":"en","source_url":x["direct_download_url"],
                  "source_name":ep+" English source SRT",
                  "rights_basis":"user_provided","confirmed":True,"complete":False,
                  "notes":("Owner-directed source preservation in private research repository; "
                           "third-party source rights not independently assessed. "
                           "Web source page: "+x["verified_page_url"])}
        # Preflight *all* inputs before mutating canonical episode files.
        try:
            prepare(file, metadata)
        except (ValueError, OSError, KeyError) as exc:
            rejected.append({"episode_id":ep,"error":str(exc)[:240]})
            continue
        prepared.append((file, metadata))
    for file, metadata in prepared:
        import_one(file, metadata)
    index = rebuild_index()
    accession = {
        "source_workflow": "night-court-unheld-caption-candidates.yml",
        "source_baseline":104, "new_sources":len(prepared),
        "held_witnesses_after_import":len(index),
        "retrieved_but_invalid_for_import":rejected,
        "original_series_only":True,
        "third_party_retention_rights_unverified":True,
        "audiovisual_completeness_verified":False,
        "acquired_episode_ids":[item[1]["episode"] for item in prepared],
        "not_acquired":[x["episode_id"] for x in result["items"]
                        if x["status"]!="downloaded_unreviewed"] + [x["episode_id"] for x in rejected]
    }
    (ROOT/"research"/"unheld-caption-acquisition-summary.json").write_text(
        json.dumps(accession,indent=2,ensure_ascii=False)+"\n","utf-8")
    print("Imported",len(prepared),"S05–S09 caption sources; indexed",len(index),"held dialogue versions",flush=True)

if __name__ == "__main__":
    main(Path(sys.argv[1]))
