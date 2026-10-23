#!/usr/bin/env python3
"""Collect metadata-only individual transcript links from a verified episode index."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib import robotparser
from urllib.parse import urljoin,urlparse
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
URL="https://transcripts.foreverdreaming.org/viewforum.php?f=1485"
UA="NightCourtResearchIndexer/0.1 (episode URL inventory)"
CODE=re.compile(r"^(\d{2})x(\d{2})\s*[-–]", re.I)

class TopicParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href=None; self.bits=[]; self.links=[]
    def handle_starttag(self, tag, attrs):
        if tag=="a":
            href=dict(attrs).get("href","")
            if "viewtopic.php?" in href and "t=" in href: self.href=href;self.bits=[]
    def handle_data(self, data):
        if self.href is not None: self.bits.append(data)
    def handle_endtag(self,tag):
        if tag=="a" and self.href is not None:
            self.links.append(("".join(self.bits).strip(),self.href))
            self.href=None

def main():
    rp=robotparser.RobotFileParser("https://transcripts.foreverdreaming.org/robots.txt")
    try:
        rp.read()
        if not rp.can_fetch(UA,URL):
            print("Index disallowed by robots; no update")
            return
        with urlopen(Request(URL,headers={"User-Agent":UA}),timeout=25) as r:
            html=r.read(2500000).decode("utf-8","replace")
    except Exception as exc:
        print("Source temporarily inaccessible:",exc)
        return
    p=TopicParser(); p.feed(html)
    found={}
    for label,href in p.links:
        m=CODE.match(label)
        if m:
            key=f"S{int(m.group(1)):02d}E{int(m.group(2)):02d}"
            direct=urljoin(URL,href)
            if urlparse(direct).hostname=="transcripts.foreverdreaming.org":
                found.setdefault(key,direct)
    changed=0
    for key,direct in found.items():
        dest=ROOT/"seasons"/key[:3]/key/"episode.json"
        if not dest.exists():continue
        entry=json.loads(dest.read_text("utf-8"))
        source=next((s for s in entry["episode_sources"] if s["provider"]=="Forever Dreaming"),None)
        if source and source["url"]!=direct:
            source.update({"url":direct,"level":"episode_in_index","verified":True,
                           "source_index":URL,"content_imported":False})
            dest.write_text(json.dumps(entry,indent=2,ensure_ascii=False)+"\n","utf-8")
            changed+=1
    print("Resolved",len(found),"episode links; updated",changed,"records; zero dialogue copied")

if __name__=="__main__":main()
