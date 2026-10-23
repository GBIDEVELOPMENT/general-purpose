#!/usr/bin/env python3
"""Consistency and provenance audit for Night Court's 193 episode files."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
counts=[13,22,22,22,22,22,24,24,22]
episodes=[]
for s,total in enumerate(counts,1):
    for ep in range(1,total+1):
        key=f"S{s:02d}E{ep:02d}"
        file=root/"seasons"/f"S{s:02d}"/key/"episode.json"
        assert file.exists(), f"missing {key}"
        obj=json.loads(file.read_text(encoding="utf8"))
        assert (obj["id"],obj["season"],obj["episode"])==(key,s,ep)
        for src in obj["episode_sources"]:
            assert src["url"].startswith("https://")
            assert src["level"] in ("series_catalog","episode_in_index","episode_page","episode_url_derived_from_verified_index")
            if src.get("level")=="episode_url_derived_from_verified_index":
                assert src.get("verified") is False
        episodes.append(obj)
assert len(episodes)==193
print("VALID 193 episode records; titled:",sum(bool(x["title"]) for x in episodes),
      "; provenance links:",sum(len(x["episode_sources"]) for x in episodes),
      "; stored full transcripts:",sum(len(x["holdings"]["full_transcripts"]) for x in episodes))
