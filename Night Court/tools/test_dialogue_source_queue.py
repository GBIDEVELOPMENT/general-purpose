#!/usr/bin/env python3
"""Validate the truthful original-series dialogue source lead inventory."""
from collections import Counter
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
def main():
    report=json.loads((ROOT/"catalog"/"dialogue-source-queue.json").read_text("utf-8"))
    episodes=report["episodes"]
    assert len(episodes)==report["episodes_count"]==193
    ids={r["episode_id"] for r in episodes}
    assert len(ids)==193
    assert sum(report["source_status_counts"].values())==193
    for item in episodes:
        key=item["episode_id"]
        e=json.loads((ROOT/"seasons"/key[:3]/key/"episode.json").read_text("utf-8"))
        assert item["title"]==e["title"],key
        assert item["held_dialogue_versions"]==(len(e["holdings"]["caption_files"])+len(e["holdings"]["full_transcripts"])),key
        direct=[x for x in item["source_locations"] if x["status"].startswith("verified_direct_")]
        assert len(direct)==item["direct_episode_page_locators"],key
        for x in direct:
            assert x["verified"] and x["url"].startswith("https://"),key
            assert x["content_imported"] is False or x["rights_status"]=="not_established",key
    for key in ("S01E03","S04E15"):
        entry=next(e for e in episodes if e["episode_id"]==key)
        assert any(x["provider"]=="Subtitle Cat" and x["status"]=="verified_direct_caption_display_page"
                   for x in entry["source_locations"]),key
    # An individually named row in a shared upload index is evidence of
    # indexing, not a confirmed direct subtitle page or held caption.
    for key in ("S05E02","S06E04","S07E01","S08E01","S09E01"):
        entry=next(e for e in episodes if e["episode_id"]==key)
        assert any(x["provider"]=="Subtitle Cat" and
            x["status"]=="verified_caption_index_listing" for x in entry["source_locations"]),key
    for item in episodes:
        for loc in item["source_locations"]:
            if loc["status"]=="verified_caption_index_listing":
                assert "/list_page.php?" in loc["url"] and not loc["content_imported"], item["episode_id"]
    status=json.loads((ROOT/"catalog"/"archive-status.json").read_text("utf-8"))
    audit=json.loads((ROOT/"catalog"/"holdings-coverage.json").read_text("utf-8"))
    assert status["source_pointer_count_including_repeated_series_indexes"]==audit["totals"]["source_pointers"]
    assert status["sources"]["subtitle_cat_direct_pages_verified"]==audit["totals"]["subtitlecat_any_episode_page_located"]
    rejected_file=ROOT/"catalog"/"rejected-dialogue-source-matches.json"
    if rejected_file.exists():
        rejected=json.loads(rejected_file.read_text("utf-8"))
        urls={s["url"] for e in episodes for s in e["source_locations"]}
        for bad in rejected["rejected"]:
            assert bad["url"] not in urls,("Revival/mislabeled subtitle pollutes original corpus",bad["url"])
    print("VALID: 193 provenance-ranked episode source inventories, status and direct caption locators")
if __name__=="__main__":main()
