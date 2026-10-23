#!/usr/bin/env python3
"""Audit 193-episode source and artifact coverage without assuming a link is held."""
from collections import Counter,defaultdict
from pathlib import Path
import csv
import io
import json

ROOT=Path(__file__).resolve().parents[1]
COUNTS=[13,22,22,22,22,22,24,24,22]

def write(path,content):
    if not path.exists() or path.read_text("utf-8")!=content:
        path.write_text(content,"utf-8")

def main():
    data=[]
    seasonal=defaultdict(Counter)
    for season,count in enumerate(COUNTS,1):
        for number in range(1,count+1):
            key=f"S{season:02d}E{number:02d}"
            directory=ROOT/"seasons"/f"S{season:02d}"/key
            episode=json.loads((directory/"episode.json").read_text("utf-8"))
            sources=episode["episode_sources"]
            stored=episode["holdings"]
            schema={
                "id":key,"season":season,"episode":number,"title":episode["title"],
                "licensed_wikipedia_capsule_held":int(any(x.get("source")=="Wikipedia" and
                    (directory/x["file"]).is_file() for x in stored["recaps"])),
                "fandom_wiki_article_held":int(any((directory/x["file"]).is_file()
                    for x in stored["wiki_exports"])),
                "full_transcripts_held":len(stored["full_transcripts"]),
                "caption_files_held":len(stored["caption_files"]),
                "review_texts_held":len(stored["reviews"]),
                "guestcast_api_embedded":int("guest_cast_source" in episode["credits"]),
                "guestcast_credited_roles":len(episode["credits"].get("guest_cast",[])),
                "forever_dreaming_indexed":int(any(x.get("provider")=="Forever Dreaming" and x["level"] in
                   ("episode_in_index","episode_page") for x in sources)),
                "springfield_inferred_url":int(any(x.get("provider")=="Springfield! Springfield!" and
                    x["level"]=="episode_url_derived_from_verified_index" for x in sources)),
                "subtitlecat_episode_page":int(any(x.get("provider")=="Subtitle Cat" and
                    x["level"]=="episode_page" for x in sources)),
                "subtitlecat_any_episode_page_located":int(any(x.get("provider")=="Subtitle Cat" and
                    x["level"] in ("episode_page","episode_in_index") for x in sources)),
                "subtitlecat_distinct_page_links":len({x["url"] for x in sources
                    if x.get("provider")=="Subtitle Cat" and x["level"] in ("episode_page","episode_in_index")}),
                "exact_episode_source_links":sum(x["level"]=="episode_page" for x in sources),
                "series_or_season_index_references":sum(x["level"]=="series_catalog" for x in sources),
                "source_pointers":len(sources)
            }
            for k,v in schema.items():
                if isinstance(v,int):seasonal[season][k]+=v
            data.append(schema)
    totals={key:sum(x[key] for x in data) for key in data[0] if isinstance(data[0][key],int)
            and key not in ("season","episode")}
    out={
     "series":"night-court-1984","episodes":len(data),
     "definition":"Held source files are tested for presence on disk; an index reference does not count as held material.",
     "totals":totals,
     "seasons":{f"S{k:02d}":dict(v) for k,v in sorted(seasonal.items())},
     "episodes":data,
     "warnings":[
      "Corpus has one encyclopedia synopsis per episode, frequently too brief for full narrative reconstruction.",
      "Guest cast includes credited roles, not necessarily every on-screen person or role.",
      "Forever Dreaming indexed episodes may be absent or inaccessible today.",
      "Springfield URL patterns are unverified episode URLs, never an actual download count.",
      "Fandom pages may be linked without being downloaded due to robots, license or connection limitations."
     ]}
    write(ROOT/"catalog"/"holdings-coverage.json",json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    buf=io.StringIO()
    w=csv.DictWriter(buf,fieldnames=list(data[0]))
    w.writeheader();w.writerows(data)
    write(ROOT/"catalog"/"holdings-coverage.csv",buf.getvalue())
    print("Audit:",len(data),"episodes;",totals["licensed_wikipedia_capsule_held"],
          "wiki capsules;",totals["guestcast_api_embedded"],"credited guestcast collections;",
          totals["caption_files_held"],"stored caption tracks")

if __name__=="__main__":main()
