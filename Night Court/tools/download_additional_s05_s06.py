#!/usr/bin/env python3
"""Acquire explicitly mapped late-season captions from their individual pages.

No bulk index enumeration; only URLs curated against canonical episodes.
Downloads are staging evidence, not a completeness or reuse-rights decision.
"""
import csv
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import time
from urllib.parse import urljoin, urlsplit, quote, urlunsplit
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
LIMIT=1_000_000

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.href=None
        self.title=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            self.href=dict(attrs).get("href")
            self.title=[]
    def handle_data(self,data):
        if self.href is not None:self.title.append(data)
    def handle_endtag(self,tag):
        if tag=="a" and self.href is not None:
            self.links.append((self.href," ".join(self.title).strip()))
            self.href=None

def fetch(url):
    p=urlsplit(url)
    if p.scheme!="https" or p.hostname!="www.subtitlecat.com" or p.port or p.username:
        raise ValueError("unexpected destination")
    with urlopen(Request(url,headers={"User-Agent":"NightCourtResearchIntake/1.0"}),timeout=30) as response:
        q=urlsplit(response.url)
        if q.scheme!="https" or q.hostname!="www.subtitlecat.com":
            raise ValueError("unexpected redirect")
        data=response.read(LIMIT+1)
    if len(data)>LIMIT:raise ValueError("file exceeds 1MB")
    return data

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--download",action="store_true")
    args=p.parse_args()
    source=ROOT/"research"/"s05-s06-additional-caption-pages.csv"
    rows=list(csv.DictReader(source.open(encoding="utf-8")))
    if len(rows)!=16 or len({r["episode_id"] for r in rows})!=16:
        raise ValueError("expected sixteen distinct original-series entries")
    args.output.mkdir(parents=True,exist_ok=True)
    result=[]
    for row in rows:
        ep=row["episode_id"]; page=row["source_page_url"]
        rec={"episode_id":ep,"source_page":page}
        try:
            if not re.fullmatch(r"S0[5-9]E\d{2}",ep):raise ValueError("invalid episode")
            if not args.download:
                rec["status"]="dry_run"
            else:
                markup=fetch(page).decode("utf-8","replace")
                a=Anchors();a.feed(markup)
                candidates=[urljoin(page,href) for href,label in a.links
                            if label.casefold()=="download" and href.lower().split("?")[0].endswith(".srt")]
                candidates=[x for x in candidates if x.lower().endswith("-en.srt") or x.lower().endswith(".eng-en.srt")]
                if len(set(candidates))!=1:
                    raise ValueError(f"expected one English SRT endpoint, found {len(set(candidates))}")
                target=candidates[0]
                parts=urlsplit(target)
                target=urlunsplit((parts.scheme, parts.netloc, quote(parts.path, safe="/%()-._~"), parts.query, ""))
                raw=fetch(target)
                if not re.search(rb"\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->",raw):
                    raise ValueError("not an SRT")
                dst=args.output/(ep+".en.srt");dst.write_bytes(raw)
                rec.update(status="downloaded_unreviewed",source_url=target,
                           sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
        except Exception as exc:
            rec.update(status="failed",error=str(exc)[:200])
        result.append(rec)
        print(ep,rec["status"],flush=True)
        if args.download:time.sleep(1.5)
    (args.output/"retrieval-report.json").write_text(json.dumps({"series":"night-court-1984",
        "attempted":len(result),"successful":sum(x["status"]=="downloaded_unreviewed" for x in result),
        "items":result,"audiovisual_complete":False},indent=2)+"\n")
    return int(any(x["status"]=="failed" for x in result))

if __name__=="__main__":sys.exit(main())
