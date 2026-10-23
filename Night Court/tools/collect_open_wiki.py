#!/usr/bin/env python3
"""Preserve specifically CC BY-SA-licensed Wikipedia wikitext with attribution."""
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
import json
import re
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"research"/"licensed-wiki"
API="https://en.wikipedia.org/w/api.php"
TITLES=("Night Court","List of Night Court episodes")
UA="NightCourtResearchIndexer/0.1 (open-license source preservation)"

def download(title):
    qs=urlencode({"action":"query","format":"json","formatversion":"2","prop":"revisions",
                  "rvprop":"ids|timestamp|content","rvslots":"main","titles":title})
    with urlopen(Request(API+"?"+qs,headers={"User-Agent":UA}),timeout=25) as r:
        data=json.load(r)
    pages=data.get("query",{}).get("pages",[])
    if len(pages)!=1 or pages[0].get("missing"):raise ValueError("Article missing")
    rev=pages[0]["revisions"][0]
    text=rev["slots"]["main"].get("content")
    if not isinstance(text,str) or len(text)<100:raise ValueError("Unexpected article content")
    return pages[0]["title"],rev["revid"],rev["timestamp"],text

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    saved=0
    for i,title in enumerate(TITLES):
        try: name,rid,stamp,raw=download(title)
        except Exception as e:
            print("Wiki source unavailable:",title,str(e))
            continue
        stem=re.sub("[^A-Za-z0-9_-]+","-",name).strip("-")
        article=OUT/(stem+".wikitext")
        provenance=OUT/(stem+".provenance.json")
        if not article.exists() or article.read_text("utf-8")!=raw:
            article.write_text(raw,"utf-8");saved+=1
        data={
            "source_title":name,"revision":rid,"source_timestamp":stamp,
            "permalink":"https://en.wikipedia.org/w/index.php?oldid="+str(rid),
            "author_attribution":"Wikipedia contributors, "+name+" rev. "+str(rid),
            "license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
            "retrieved_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "exclusions":"Not licensed television dialogue, caption tracks or embedded imagery"
        }
        if not provenance.exists() or json.loads(provenance.read_text("utf-8")).get("revision")!=rid:
            provenance.write_text(json.dumps(data,indent=2)+"\n","utf-8")
        if i==0:time.sleep(1)
    print("Saved/updated",saved,"openly licensed wiki articles")

if __name__=="__main__":main()
