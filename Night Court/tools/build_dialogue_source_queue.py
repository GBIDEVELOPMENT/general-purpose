#!/usr/bin/env python3
"""Offline episode dialogue-location inventory. Links are not held transcripts."""
from collections import Counter,defaultdict
from pathlib import Path
import csv,io,json

ROOT=Path(__file__).resolve().parents[1]
COUNTS=[13,22,22,22,22,22,24,24,22]
ORDER=["no_episode_dialogue_specific_locator","inferred_link_only",
       "index_coverage_only","direct_episode_page_found_not_held",
       "held_dialogue_needs_quality_review"]

def locator(source):
    provider=source.get("provider","")
    url=source.get("url","")
    verified=bool(source.get("verified"))
    if provider=="Forever Dreaming":
        status=("verified_direct_transcript_topic" if verified and "viewtopic.php?" in url
                else "verified_transcript_index_listing")
    elif provider=="Springfield! Springfield!":
        status="verified_direct_script_page" if verified else "inferred_script_url_unchecked"
    elif provider=="Subtitle Cat":
        if verified and "/subs/" in url:
            status="verified_direct_caption_display_page"
        elif verified and "/list_page.php" in url:
            status="verified_caption_index_listing"
        else:
            status="caption_listing_unverified"
    else:return None
    return {"provider":provider,"url":url,"status":status,"verified":verified,
            "content_imported":bool(source.get("content_imported")),
            "source_kind":source.get("kind"),
            "rights_status":"not_established"}
def classify(held,links):
    values={e["status"] for e in links}
    if held:return ORDER[4]
    if any(k.startswith("verified_direct_") for k in values):return ORDER[3]
    if "verified_transcript_index_listing" in values or "verified_caption_index_listing" in values:return ORDER[2]
    if "inferred_script_url_unchecked" in values:return ORDER[1]
    return ORDER[0]
def save(path,value):
    if not path.exists() or path.read_text("utf-8")!=value:
        path.write_text(value,"utf-8")

def main():
    entries=[]; seasons=defaultdict(Counter)
    for s,count in enumerate(COUNTS,1):
        for e in range(1,count+1):
            id=f"S{s:02d}E{e:02d}"
            source=json.loads((ROOT/"seasons"/f"S{s:02d}"/id/"episode.json").read_text("utf-8"))
            links=[]; seen=set()
            for item in source["episode_sources"]:
                c=locator(item)
                if c and (c["provider"],c["url"]) not in seen:
                    links.append(c)
                    seen.add((c["provider"],c["url"]))
            held=(len(source["holdings"]["caption_files"])+len(source["holdings"]["full_transcripts"])
                  +sum(bool(item.get("version_id") and item.get("manifest_file"))
                       for item in source["holdings"].get("other",[])))
            level=classify(held,links)
            direct=[x for x in links if x["status"].startswith("verified_direct_")]
            row={
              "episode_id":id,"season":s,"episode":e,"title":source["title"],
              "held_dialogue_versions":held,
              "direct_episode_page_locators":len(direct),
              "index_only_transcript_refs":sum(x["status"] in ("verified_transcript_index_listing","verified_caption_index_listing") for x in links),
              "unverified_pattern_urls":sum(x["status"]=="inferred_script_url_unchecked" for x in links),
              "acquisition_status":level,"source_locations":links}
            entries.append(row);seasons[s][level]+=1
    assert len(entries)==193
    counts=dict(sorted(Counter(x["acquisition_status"] for x in entries).items()))
    ranked=sorted(entries,key=lambda e:(ORDER.index(e["acquisition_status"]),-e["season"],e["episode"]))
    output={
      "series_id":"night-court-1984","episodes_count":193,
      "ranking_policy":"Least episode-specific source evidence first; within tier, later seasons first.",
      "source_caveat":"A discovered link is not a held transcript and does not establish reuse permission.",
      "source_status_counts":counts,
      "by_season":{f"S{k:02d}":dict(v) for k,v in sorted(seasons.items())},
      "ranked_missing_episode_ids":[x["episode_id"] for x in ranked if not x["held_dialogue_versions"]],
      "episodes":entries}
    save(ROOT/"catalog"/"dialogue-source-queue.json",json.dumps(output,indent=2,ensure_ascii=False)+"\n")
    flat=[]
    for e in entries:
        flat.append({
         "episode_id":e["episode_id"],"title":e["title"],"season":e["season"],
         "status":e["acquisition_status"],"held_versions":e["held_dialogue_versions"],
         "verified_direct_pages":e["direct_episode_page_locators"],
         "transcript_index_only":e["index_only_transcript_refs"],
         "inferred_urls":e["unverified_pattern_urls"],
         "direct_urls":"; ".join(x["url"] for x in e["source_locations"] if x["status"].startswith("verified_direct_"))})
    buf=io.StringIO()
    writer=csv.DictWriter(buf,fieldnames=list(flat[0]))
    writer.writeheader();writer.writerows(flat)
    save(ROOT/"catalog"/"dialogue-source-queue.csv",buf.getvalue())
    md=["# Original Night Court: dialogue-source acquisition queue","",
        "Links are external research leads, not held dialogue or approved copying.",
        "","| Source evidence status | Episodes |","|---|---:|"]
    for k in ORDER:md.append(f"| {k.replace('_',' ')} | {counts.get(k,0)} |")
    md+=["","## Verified episode-level external pages",""]
    for e in entries:
        links=[x for x in e["source_locations"] if x["status"].startswith("verified_direct_")]
        if links:
            md.append("- **{} {}:** {}".format(e["episode_id"],e["title"],
                ", ".join(f"[{x['provider']}]({x['url']})" for x in links)))
    md+=["","Consult dialogue-source-queue.csv for all 193 episodes and sortable gaps.",
          "Always confirm the 1984 original series, not the 2023 revival.",
          "No full third-party dialogue has been mirrored by this operation.",""]
    save(ROOT/"catalog"/"dialogue-source-queue.md","\n".join(md))
    statusfile=ROOT/"catalog"/"archive-status.json"
    auditfile=ROOT/"catalog"/"holdings-coverage.json"
    if statusfile.exists() and auditfile.exists():
        status=json.loads(statusfile.read_text("utf-8"))
        audits=json.loads(auditfile.read_text("utf-8"))
        totals=audits["totals"]
        status["sources"]["subtitle_cat_direct_pages_verified"]=totals["subtitlecat_any_episode_page_located"]
        status["source_pointer_count_including_repeated_series_indexes"]=totals["source_pointers"]
        status["source_locator_queue"]="catalog/dialogue-source-queue.json"
        status["distinct_sources_warning"]=(
          f'{totals["source_pointers"]} references may repeat a series catalog; '
          "the 193 episode records contain no automatically acquired full television dialogue.")
        save(statusfile,json.dumps(status,indent=2,ensure_ascii=False)+"\\n".replace("\\n","\n"))
    print("Dialogue source queue:",len(entries),"episodes;",counts)
if __name__=="__main__":main()
