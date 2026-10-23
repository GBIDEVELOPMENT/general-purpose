#!/usr/bin/env python3
"""Offline invariants for the original 193-episode Night Court archive."""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
counts=[13,22,22,22,22,22,24,24,22]
episodes=[]
capsules=0
for season,total in enumerate(counts,1):
    for ep in range(1,total+1):
        key=f"S{season:02d}E{ep:02d}"
        directory=root/"seasons"/f"S{season:02d}"/key
        file=directory/"episode.json"
        assert file.exists(),f"Missing {key}"
        obj=json.loads(file.read_text("utf-8"))
        assert (obj["id"],obj["season"],obj["episode"])==(key,season,ep),key
        assert obj.get("title"),f"Missing title {key}"
        assert obj.get("original_air_date"),f"Missing air date {key}"
        assert obj.get("credits",{}).get("director"),f"Missing director {key}"
        assert obj.get("credits",{}).get("writers"),f"Missing writers {key}"
        assert obj.get("credits",{}).get("production_code"),f"Missing production code {key}"
        for source in obj.get("episode_sources",[]):
            assert source["url"].startswith("https://"),key
            assert source["level"] in (
                "series_catalog","episode_in_index","episode_page",
                "episode_url_derived_from_verified_index","episode_streaming_catalog"),key
            if source["level"]=="episode_url_derived_from_verified_index":
                assert source.get("verified") is False,key
            if source["level"]=="episode_streaming_catalog":
                assert source.get("kind")=="streaming_closed_caption_availability",key
                assert source.get("content_imported") is False,key
        for holding in obj.get("holdings",{}).get("recaps",[]):
            file=directory/holding["file"]
            provenance=directory/holding["provenance_file"]
            assert file.exists() and file.stat().st_size>0,(key,file)
            assert provenance.exists(),(key,provenance)
            meta=json.loads(provenance.read_text("utf-8"))
            assert meta["episode_id"]==key,(key,"bad episode provenance")
            assert meta["license"]==holding["license"]=="CC BY-SA 4.0",(key,"bad license")
            assert meta["source_revision"],(key,"source revision missing")
            capsules+=1
        episodes.append(obj)
assert len(episodes)==193
index=json.loads((root/"catalog"/"index.json").read_text("utf-8"))
assert index["episode_count"]==193
assert len(index["episode_paths"])==193
print("VALID episode records:",len(episodes),"; licensed episode capsules:",capsules,
      "; source pointers:",sum(len(x["episode_sources"]) for x in episodes),
      "; held full transcripts:",sum(len(x["holdings"]["full_transcripts"]) for x in episodes))
