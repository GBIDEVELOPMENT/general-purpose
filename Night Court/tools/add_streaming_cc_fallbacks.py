#!/usr/bin/env python3
"""Attach streaming CC *availability* metadata to the remaining 3 episodes.

No subtitles or episode video downloaded. A provider's episode listing with
closed captions does not expose independent SRT/VTT bytes or reuse rights.
"""
from pathlib import Path
from urllib.parse import urlparse
import json

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"research"/"three-remaining-cc-streaming-options.json"
EXPECTED={"S09E08","S09E17","S09E19"}

def write(path,value):
    raw=json.dumps(value,indent=2,ensure_ascii=False)+"\n"
    if not path.exists() or path.read_text("utf-8")!=raw:
        path.write_text(raw,"utf-8")
        return True
    return False

def main():
    manifest=json.loads(INPUT.read_text("utf-8"))
    if manifest.get("series")!="night-court-1984" or {r["episode_id"] for r in manifest["items"]}!=EXPECTED:
        raise ValueError("Caption provider mapping must cover only missing original-series S09 IDs")
    if len(manifest["items"])!=3:
        raise ValueError("Duplicate or missing episode entries")
    imported=0
    for r in manifest["items"]:
        eid=r["episode_id"]
        parsed=urlparse(r["url"])
        if parsed.scheme!="https" or parsed.hostname!="tv.apple.com" or not parsed.path.startswith("/"+r["region"].lower()+"/episode/"):
            raise ValueError("Unverified provider URL identity: "+eid)
        if r["cc_language"]!="en-US":
            raise ValueError("Expected English US closed caption availability")
        episode_file=ROOT/"seasons"/eid[:3]/eid/"episode.json"
        ep=json.loads(episode_file.read_text("utf-8"))
        if ep["id"]!=eid or ep["title"]!=r["title"]:
            raise ValueError("Catalog title mapping mismatch at "+eid)
        refs=ep["episode_sources"]
        previous=next((v for v in refs if v.get("provider")=="Apple TV" and v.get("url")==r["url"]),None)
        if previous:continue
        refs.append({
            "kind":"streaming_closed_caption_availability",
            "provider":"Apple TV","url":r["url"],
            "level":"episode_streaming_catalog",
            "verified":True,"content_imported":False,
            "language":r["cc_language"],"region":r["region"],
            "reported_runtime_minutes":r["runtime_minutes"],
            "rights_status":"not_license_to_download_or_redistribute",
            "verification":"publisher_episode_listing_explicitly_advertises_en_US_CC",
            "note":"Publisher's episode page advertises English CC. Requires supported access/region; no external subtitle display page or held caption track established."
        })
        imported+=int(write(episode_file,ep))
    # Maintain separate viewing-source report. Its non-copyable availability
    # must not upgrade existing 'no episode-specific transcript locator' tiers.
    output={
      "series":"night-court-1984",
      "provider":"Apple TV",
      "supported_surface":"individual streaming episode pages with English US CC",
      "episode_pages":len(manifest["items"]),
      "subtitle_files_obtained":0,
      "copyrighted_dialogue_copied":False,
      "source_type":"provider_closed_caption_viewing_availability_not_downloadable_transcript",
      "episode_ids":sorted(EXPECTED),
      "sources":manifest["items"],
      "warning":"Streaming playback may require payment and be unavailable by region. It does not provide an exported SRT or prove full dialogue capture."
    }
    write(ROOT/"catalog"/"streaming-cc-fallbacks.json",output)
    print("Streaming CC availability mapped for",len(EXPECTED),"episodes;",imported,
          "episode metadata files changed; no caption files downloaded")
if __name__=="__main__":main()
