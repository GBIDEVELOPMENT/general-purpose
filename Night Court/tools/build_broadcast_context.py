#!/usr/bin/env python3
"""Derive original Night Court broadcast/reception metrics from held licensed wiki.

Ratings, shares, viewer counts and season ranks have different denominators and
are never pooled. Combined two-part listings can represent one measurement.
"""
from collections import defaultdict
from pathlib import Path
from statistics import median
import csv,io,json,re

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"catalog"/"episodes.jsonl"
WIKI=ROOT/"research"/"licensed-wiki"/"List-of-Night-Court-episodes.wikitext"
PROV=ROOT/"research"/"licensed-wiki"/"List-of-Night-Court-episodes.provenance.json"

def save(path,text):
    if not path.exists() or path.read_text("utf-8")!=text:path.write_text(text,"utf-8")

def overview(text,season):
    def f(key):
        m=re.search(r"(?m)^\s*\|\s*"+key+str(season)+r"\s*=\s*([\d.]+)",text)
        return float(m.group(1)) if m else None
    return {"season":season,"season_us_series_rank":int(f("infoA")) if f("infoA") is not None else None,
            "season_household_rating":f("infoB"),
            "rank_source":"Wikipedia episode-list season-overview table; independently verify underlying ratings references"}

def main():
    full=WIKI.read_text("utf-8")
    provenance=json.loads(PROV.read_text("utf-8"))
    source_url=provenance["permalink"]
    rows=[]
    byseason=defaultdict(list)
    for root in sorted((ROOT/"seasons").glob("S*/S*/episode.json")):
        ep=json.loads(root.read_text("utf-8"))
        src=ep.get("wikipedia_production_metadata",{})
        share=src.get("household_rating_and_share")
        hh_rating=hh_share=None
        if share:
            match=re.fullmatch(r"\s*([\d.]+)\s*/\s*([\d.]+)\s*",share)
            if not match:raise ValueError("Unexpected household rating/share string: "+str(share))
            hh_rating=float(match.group(1))
            hh_share=float(match.group(2))
        viewers=src.get("viewers_millions")
        if viewers is not None: viewers=float(viewers)
        row={"id":ep["id"],"season":ep["season"],"episode":ep["episode"],
             "title":ep["title"],"air_date":ep["original_air_date"],
             "household_rating_points":hh_rating,"household_share_percent":hh_share,
             "us_viewers_millions":viewers,"composite_source_row":bool(src.get("is_combined_broadcast_entry")),
             "measurement_from_source":"Wikipedia episode listing with original press citation, revision-pinned"}
        rows.append(row);byseason[ep["season"]].append(row)
    assert len(rows)==193
    seasons=[]
    for s in range(1,10):
        data=byseason[s]
        # Count a jointly aired two-part Wikipedia source entry as ONE audience observation.
        observed={}
        for o in data:
            key=(o["air_date"],o["household_rating_points"],o["household_share_percent"],o["us_viewers_millions"])
            if o["composite_source_row"]: observed.setdefault(key,o)
            else:observed[(o["id"],)]=o
        unique=list(observed.values())
        def calc(col):
            sample=[o[col] for o in unique if o[col] is not None]
            return {"measured_broadcasts":len(sample),
                    "median":median(sample) if sample else None,
                    "min":min(sample) if sample else None,
                    "max":max(sample) if sample else None}
        z=overview(full,s)
        z.update({
            "episode_parts":len(data),
            "uniquely_reported_broadcast_measurements":len(unique),
            "household_rating_points":calc("household_rating_points"),
            "household_share_percent":calc("household_share_percent"),
            "us_viewers_millions":calc("us_viewers_millions")})
        seasons.append(z)
    result={
        "series":"night-court-1984","source":source_url,
        "license":"CC BY-SA 4.0, Wikipedia contributors",
        "source_revision":provenance["revision"],
        "season_averages_meaning":"Season-wide U.S. TV-series ranking/rating as reported by the secondary Wikipedia season overview",
        "episode_measurements_meaning":"Per-episode measurements as attributed in wiki episode rows, either household rating/share or U.S. viewers in millions",
        "no_cross_unit_comparison":True,
        "composite_handling":"Combined two-part episodes share one audience metric in source; deduplicated for descriptive season stats.",
        "caveats":[
           "Household ratings and viewer millions are not interchangeable.",
           "A season-wide ranking is not the rank of each individual episode.",
           "Coverage and reporting methodologies vary by year; data should be checked against underlying cited contemporary reports.",
           "Correlation across seasons cannot establish that casts, scripts or network scheduling caused audience change.",
           "Numbers are from retrospective Wikipedia tables, not directly transcribed original Nielsen reports."],
        "seasons":seasons,
        "episode_measurements":rows}
    save(ROOT/"catalog"/"broadcast-context.json",json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    out=io.StringIO();w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    save(ROOT/"catalog"/"broadcast-context.csv",out.getvalue())
    lines=["# Original Night Court broadcast evidence (1984–1992)","",
       "Generated from licensed, revision-pinned Wikipedia season and episode tables.",
       "Source: "+source_url,
       "Attribution: Wikipedia contributors, CC BY-SA 4.0.",
       "",
       "Season ranks and season-wide household rating (when listed):","",
       "| Season | U.S. series rank | Season household rating | Episode parts | Per-broadcast viewer observations |",
       "|---|---:|---:|---:|---:|"]
    for s in seasons:
        lines.append("| {} | {} | {} | {} | {} |".format(
          s["season"],s["season_us_series_rank"],s["season_household_rating"],
          s["episode_parts"],s["us_viewers_millions"]["measured_broadcasts"]))
    lines+=["","The per-episode CSV/JSON preserves household rating/share and millions-of-viewers as distinct units;",
            "broadcasts spanning two episode parts are not double-counted in descriptive medians.",
            "Season rank does not establish episode-level popularity or the causal effect of creative changes.",""]
    save(ROOT/"research"/"broadcast-context.md","\n".join(lines))
    print("Broadcast metrics:",len(rows),"episode parts;",
          len(seasons),"season rows;",
          sum(s["household_rating_points"]["measured_broadcasts"] for s in seasons),"household-rated broadcasts;",
          sum(s["us_viewers_millions"]["measured_broadcasts"] for s in seasons),"viewer-count broadcasts")

if __name__=="__main__":main()
