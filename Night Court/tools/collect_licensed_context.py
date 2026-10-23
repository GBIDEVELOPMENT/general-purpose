#!/usr/bin/env python3
"""Archive a curated list of openly licensed context articles for Night Court.

Only Wikipedia CC BY-SA wikitext, revision-pinned; factual context about
principal performers, creators and the period. Not episode evidence or scripts.
"""
from __future__ import annotations
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode,quote
from urllib.request import Request,urlopen
import hashlib,json,re,time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"research"/"licensed-wiki"/"context"
API="https://en.wikipedia.org/w/api.php"
UA="NightCourtPrivateResearch/0.2 (CC BY-SA source archiving)"
TITLES={
 "principal-cast":[
  "Harry Anderson","John Larroquette","Richard Moll","Markie Post",
  "Charles Robinson (actor, born 1945)","Marsha Warfield","Karen Austin",
  "Selma Diamond","Florence Halop","Paula Kelly (actress)","Ellen Foley",
  "Gail Strickland","Denice Kumagai","John Astin"],
 "production":[
  "Reinhold Weege","James Burrows","Jeff Melman","Linwood Boomer"],
 "period-and-institution":[
  "New York City Criminal Court","1980s in American television","Sitcom"]
}
LICENSE="CC BY-SA 4.0"
LURL="https://creativecommons.org/licenses/by-sa/4.0/"

def fetch(titles):
    args=urlencode({"action":"query","format":"json","formatversion":"2",
                    "redirects":"1","prop":"revisions","rvprop":"ids|timestamp|content",
                    "rvslots":"main","titles":"|".join(titles)})
    with urlopen(Request(API+"?"+args,headers={"User-Agent":UA}),timeout=30) as r:
        data=json.load(r)
    return data.get("query",{}).get("pages",[])

def store(path,contents):
    if not path.exists() or path.read_text("utf-8")!=contents:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(contents,"utf-8")
        return 1
    return 0

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    captured={}
    failed=[]
    for category,titles in TITLES.items():
        for pos in range(0,len(titles),5):
            wanted=titles[pos:pos+5]
            try: pages=fetch(wanted)
            except Exception as exc:
                failed.extend({"requested":x,"error":str(exc)} for x in wanted)
                continue
            for page in pages:
                if page.get("missing") or not page.get("revisions"):
                    failed.append({"requested":page.get("title"),"error":"missing"})
                    continue
                rev=page["revisions"][0]
                body=rev.get("slots",{}).get("main",{}).get("content")
                if not isinstance(body,str) or len(body)<50 or len(body)>750_000:
                    failed.append({"requested":page.get("title"),"error":"empty or exceeds per-page size cap"})
                    continue
                name=page["title"]
                stem=re.sub(r"[^A-Za-z0-9_-]+","-",name).strip("-")
                wikitext=OUT/(stem+".wikitext")
                changed=store(wikitext,body)
                meta={
                 "title":name,"category":category,"source":"Wikipedia contributors",
                 "source_page":"https://en.wikipedia.org/wiki/"+quote(name.replace(" ","_")),
                 "revision_id":rev["revid"],"revision_timestamp":rev["timestamp"],
                 "permalink":"https://en.wikipedia.org/w/index.php?oldid="+str(rev["revid"]),
                 "license":LICENSE,"license_url":LURL,
                 "attribution":"Wikipedia contributors, "+name+" (revision "+str(rev["revid"])+")",
                 "sha256":hashlib.sha256(body.encode("utf-8")).hexdigest(),
                 "scope_note":"Supplementary contextual biography/history; not direct Night Court episode testimony.",
                 "media_excluded":True}
                mpath=OUT/(stem+".provenance.json")
                if not mpath.exists() or json.loads(mpath.read_text("utf-8")).get("revision_id")!=rev["revid"]:
                    store(mpath,json.dumps(meta,indent=2,ensure_ascii=False)+"\n")
                captured[name]={"category":category,"source_file":str(wikitext.relative_to(ROOT)),
                    "revision_id":rev["revid"],"sha256":meta["sha256"]}
            time.sleep(0.6)
    index={"source":"Wikipedia, CC BY-SA 4.0 with revision-level attribution",
       "requested_titles":sum(len(x) for x in TITLES.values()),
       "captured_count":len(captured),"captured":dict(sorted(captured.items())),
       "unavailable":failed,"no_episode_claims_inferred":True}
    store(OUT/"manifest.json",json.dumps(index,indent=2,ensure_ascii=False)+"\n")
    print("Saved",len(captured),"context pages; unavailable:",len(failed))

if __name__=="__main__":main()
