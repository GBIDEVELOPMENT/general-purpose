#!/usr/bin/env python3
"""Permission-aware preservation of Night Court Fandom wiki article *text*.

Checks robots and the wiki's own declared article license before any scraping.
Never downloads images, videos, comment threads, or TV subtitles/scripts.
Unavailable sources are recorded as unavailable, not falsely held.
"""
from collections import Counter
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlencode,quote
from urllib.request import Request,urlopen
import hashlib,json,re,time

ROOT=Path(__file__).resolve().parents[1]
BASE="https://nightcourt.fandom.com"
API=BASE+"/api.php"
UA="NightCourtPrivateResearch/0.2 (CC licensed wiki, obey robots)"
OUT=ROOT/"research"/"fandom-wiki"
GENERAL=["Night_Court","List_of_Night_Court_episodes"]+[f"Season_{s}" for s in range(1,10)]+[
"Harry_T._Stone","Dan_Fielding","Bull_Shannon","Christine_Sullivan",
"Roz_Russell","Mac_Robinson","Selma_Hacker","Flo_Kleiner","Reinhold_Weege"]
SOURCE_KIND="Fandom Night Court Wiki"
MAX_PAGES=230
LIMIT=150_000

def get(params):
    url=API+"?"+urlencode(params)
    with urlopen(Request(url,headers={"User-Agent":UA,"Accept":"application/json"}),timeout=22) as r:
        return json.load(r)

def save(path,text):
    if not path.exists() or path.read_text("utf-8")!=text:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(text,"utf-8")
        return True
    return False

def manifest(status,**kw):
    OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/"collection-status.json",json.dumps({"status":status,**kw},indent=2,ensure_ascii=False)+"\n")

def main():
    robots=robotparser.RobotFileParser()
    robots.set_url(BASE+"/robots.txt")
    try:
        robots.read()
        test=API+"?action=query&meta=siteinfo&siprop=rights&format=json"
        if not robots.can_fetch(UA,test):
            manifest("blocked_by_robots",note="No article fetch attempted; site robots disallows API")
            return
        info=get({"action":"query","meta":"siteinfo","siprop":"rights","format":"json"})
        rights=info["query"]["rightsinfo"]
        rights_url=rights.get("url","")
        rights_name=rights.get("text","")
    except Exception as exc:
        manifest("not_accessible_or_license_unknown",error=str(exc)[:220])
        return
    if not rights_url.startswith("https://creativecommons.org/licenses/by-sa/") and not rights_url.startswith("http://creativecommons.org/licenses/by-sa/"):
        manifest("license_not_approved",rights=rights_name,rights_url=rights_url)
        return
    title_to_episode={}
    for f in sorted((ROOT/"seasons").glob("S*/S*/episode.json")):
        d=json.loads(f.read_text("utf-8"))
        key=d["title"].casefold().strip()
        title_to_episode.setdefault(key,[]).append(f)
    query=list(GENERAL)
    for name,files in title_to_episode.items():
        if len(files)==1:
            title=files[0].parent.name
            d=json.loads(files[0].read_text("utf-8"))
            query.append(d["title"].replace(" ","_"))
    query=list(dict.fromkeys(query))[:MAX_PAGES]
    held=0; episode_captured=0; misses=[]; skip=[]; edited=0
    for i in range(0,len(query),6):
        chunk=query[i:i+6]
        endpoint=API+"?"+urlencode({"action":"query","format":"json","prop":"revisions","rvprop":"ids|timestamp|content","rvslots":"main","titles":"|".join(chunk),"redirects":"1"})
        if not robots.can_fetch(UA,endpoint):
            skip.append({"chunk":i//6,"error":"blocked by robots"})
            continue
        try:
            response=get({"action":"query","format":"json","prop":"revisions","rvprop":"ids|timestamp|content",
                          "rvslots":"main","titles":"|".join(chunk),"redirects":"1"})
        except Exception as exc:
            skip.append({"chunk":i//6,"error":str(exc)[:180]})
            continue
        pages=response.get("query",{}).get("pages",{})
        if isinstance(pages,dict):pages=list(pages.values())
        for page in pages:
            if page.get("missing") or not page.get("revisions"):
                misses.append(page.get("title","unknown"))
                continue
            rev=page["revisions"][0]
            slot=rev.get("slots",{}).get("main",{})
            text=slot.get("content",slot.get("*",rev.get("*")))
            if not isinstance(text,str) or not 70<=len(text)<=LIMIT:
                misses.append(page.get("title","unknown")+" (unusable size)")
                continue
            name=page["title"]; stem=re.sub("[^A-Za-z0-9_-]+","-",name).strip("-")
            original_url=BASE+"/wiki/"+quote(name.replace(" ","_"))
            source={
             "publisher":"Night Court Wiki contributors (Fandom)",
             "title":name,"url":original_url,"revision_id":rev["revid"],"revision_date":rev["timestamp"],
             "attribution":"Night Court Wiki contributors; page "+name+" (revision "+str(rev["revid"])+")",
             "license":rights_name,"license_url":rights_url,
             "sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),
             "scope":"User-contributed wiki text only; externally inserted excerpts may have distinct rights; media not included."}
            local=OUT/(stem+".wikitext")
            edited+=save(local,text)
            edited+=save(OUT/(stem+".provenance.json"),json.dumps(source,indent=2,ensure_ascii=False)+"\n")
            held+=1
            matches=title_to_episode.get(name.casefold().strip(),[])
            if len(matches)==1:
                episode=matches[0]; d=json.loads(episode.read_text("utf-8"))
                epdir=episode.parent
                target=epdir/"authorized-text"/"fandom-article.wikitext"
                manifest_file=epdir/"sources"/"fandom-article.provenance.json"
                edited+=save(target,text)
                details={**source,"stored_file":"authorized-text/fandom-article.wikitext",
                    "episode_id":d["id"],"mapping_confidence":"exact_unique_title"}
                edited+=save(manifest_file,json.dumps(details,indent=2,ensure_ascii=False)+"\n")
                if not any(x.get("provider")==SOURCE_KIND and x.get("level")=="episode_page" for x in d["episode_sources"]):
                    d["episode_sources"].append({"kind":"fan_wiki","provider":SOURCE_KIND,
                        "url":original_url,"level":"episode_page","verified":True,
                        "license":rights_name,"content_imported":True})
                    edited+=save(episode,json.dumps(d,indent=2,ensure_ascii=False)+"\n")
                if not any(x.get("source")==SOURCE_KIND for x in d["holdings"]["wiki_exports"]):
                    d["holdings"]["wiki_exports"].append({"source":SOURCE_KIND,
                        "file":"authorized-text/fandom-article.wikitext",
                        "provenance_file":"sources/fandom-article.provenance.json",
                        "license":rights_name})
                    edited+=save(episode,json.dumps(d,indent=2,ensure_ascii=False)+"\n")
                episode_captured+=1
        time.sleep(.7)
    manifest("completed",license=rights_name,license_url=rights_url,requested=len(query),
             wiki_pages_captured=held,episode_pages_captured=episode_captured,
             unavailable_pages=misses,skipped_batches=skip)
    print("Fandom licensed wiki pages:",held,"episode-matched:",episode_captured,
          "missing:",len(misses),"skipped batches:",len(skip),"writes:",edited)

if __name__=="__main__":main()
