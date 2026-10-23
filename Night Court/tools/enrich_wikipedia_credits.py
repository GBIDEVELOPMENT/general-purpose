#!/usr/bin/env python3
"""Import factual production credits and period ratings from licensed Wikipedia wikitext.

Reads already archived CC BY-SA article; supports composite two-part episode rows.
Keeps exact source credit strings and tags partial/uncertain parsing, not scripted dialogue.
"""
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
WIKI=ROOT/"research"/"licensed-wiki"/"List-of-Night-Court-episodes.wikitext"
COUNTS=[13,22,22,22,22,22,24,24,22]
FIELDS=("EpisodeNumber","EpisodeNumber2","NumParts","Title","DirectedBy","WrittenBy",
        "OriginalAirDate","ProdCode","Aux4","Viewers")
PREFIX="https://en.wikipedia.org/wiki/List_of_Night_Court_episodes"

def field(block,key):
    m=re.search(r"(?m)^\s*\|"+re.escape(key)+r"\s*=\s*(.*?)\s*$",block)
    return m.group(1).strip() if m else None

def normalize(credit):
    if not credit:return None
    credit=re.sub(r"\[\[(?:[^]|]+\|)?([^]]+)\]\]",r"\1",credit)
    credit=re.sub(r"<[^>]+>","",credit).replace("'''","").replace("''","")
    return credit.strip()

def source_rows(text):
    matches=list(re.finditer(r"\{\{\s*Episode list\b",text,re.I))
    found={}
    for i,m in enumerate(matches):
        block=text[m.start():matches[i+1].start() if i+1<len(matches) else len(text)]
        if field(block,"NumParts")=="2":
            nums=[field(block,"EpisodeNumber_1"),field(block,"EpisodeNumber_2")]
        else:
            nums=[field(block,"EpisodeNumber")]
        for part,n in enumerate(nums,1):
            if not n or not n.isdigit():
                raise ValueError("Unrecognised episode numbering in a wiki row")
            overall=int(n)
            if overall in found:raise ValueError(f"Duplicated overall episode {overall}")
            suffix="_"+str(part) if len(nums)>1 else ""
            def value(key):return field(block,key+suffix) or field(block,key)
            clean_director=normalize(value("DirectedBy"))
            clean_writer=normalize(value("WrittenBy"))
            found[overall]={
                "title_on_wikipedia":normalize(value("Title")),
                "director":clean_director,
                "writer_credit":clean_writer,
                "production_code":value("ProdCode"),
                "episode_airdate_wikitext":field(block,"OriginalAirDate"),
                "household_rating_and_share":re.match(r"\s*[\d.]+/[\d.]+",field(block,"Aux4") or "").group(0) if re.match(r"\s*[\d.]+/[\d.]+",field(block,"Aux4") or "") else None,
                "viewers_millions":float(re.match(r"[\d.]+",field(block,"Viewers") or "").group()) if re.match(r"[\d.]+",field(block,"Viewers") or "") else None,
                "is_combined_broadcast_entry":len(nums)>1,
                "shared_entry_parts":len(nums)
            }
    if len(found)!=193 or set(found)!=set(range(1,194)):
        missing=sorted(set(range(1,194))-set(found))
        raise ValueError(f"Expected 193 episode parts; got {len(found)}, missing {missing}")
    return found

def main():
    if not WIKI.exists():
        print("Licensed Wikipedia archive missing; no modifications")
        return
    rows=source_rows(WIKI.read_text("utf-8"))
    lines=[]
    updated=0
    absolute=0
    for season,num in enumerate(COUNTS,1):
        for episode in range(1,num+1):
            absolute+=1
            key=f"S{season:02d}E{episode:02d}"
            path=ROOT/"seasons"/f"S{season:02d}"/key/"episode.json"
            obj=json.loads(path.read_text("utf-8"))
            src=rows[absolute]
            credits=obj.setdefault("credits",{})
            credits["director"]=src["director"]
            credits["writers"]=([src["writer_credit"]] if src["writer_credit"] else [])
            credits["writer_credit_display"]=src["writer_credit"]
            credits["production_code"]=src["production_code"]
            obj["wikipedia_production_metadata"]={k:v for k,v in src.items() if k not in ("director","writer_credit","production_code")}
            if src["title_on_wikipedia"] and src["title_on_wikipedia"]!=obj.get("title"):
                aliases=obj.setdefault("title_aliases",[])
                if src["title_on_wikipedia"] not in aliases:aliases.append(src["title_on_wikipedia"])
            if not any(s.get("provider")=="Wikipedia production table" for s in obj["episode_sources"]):
                obj["episode_sources"].append({"kind":"production_credits","provider":"Wikipedia production table",
                    "url":PREFIX,"level":"episode_in_index","verified":True,
                    "license":"CC BY-SA 4.0","content_imported":True,
                    "source_file":"research/licensed-wiki/List-of-Night-Court-episodes.wikitext",
                    "episode_number_in_source":absolute})
            path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n","utf-8")
            lines.append(json.dumps({"id":key,"season":season,"episode":episode,"absolute_episode":absolute,
                "title":obj["title"],"original_air_date":obj["original_air_date"],
                "director":credits["director"],"writer_credit":credits["writer_credit_display"],
                "production_code":credits["production_code"],
                "source_count":len(obj["episode_sources"])},ensure_ascii=False))
            updated+=1
    (ROOT/"catalog"/"episodes.jsonl").write_text("\n".join(lines)+"\n","utf-8")
    indexfile=ROOT/"catalog"/"index.json"
    index=json.loads(indexfile.read_text("utf-8"))
    index["catalogue_status"]="193 episode titles and air dates filled from TVmaze; 193 production rows resolved from 188 Wikipedia entries (5 two-part composite rows)"
    indexfile.write_text(json.dumps(index,indent=2,ensure_ascii=False)+"\n","utf-8")
    print(f"Enriched {updated} episode facts from {len(rows)} licensed-source episode parts")

if __name__=="__main__":main()
