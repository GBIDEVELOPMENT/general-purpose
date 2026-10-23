#!/usr/bin/env python3
"""Discover original 1984 Night Court subtitle *page URLs*, never subtitle text.

Source-specific versions, rights, index provenance, and uncertain coverage stay
distinct. The public upload index is consulted only when robots policy permits.
"""
from __future__ import annotations
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlencode,urljoin,urlparse
from urllib.request import Request,urlopen
import json
import re
import time

ROOT=Path(__file__).resolve().parents[1]
BASE="https://www.subtitlecat.com"
UA="NightCourtPrivateResearch/0.3 (episode subtitle URL index only)"
INDEX=BASE+"/list_page.php"
SEARCH=BASE+"/index.php"
MAX_HTML=2_500_000
CODE=re.compile(r"\bS(\d{2})E(\d{2})\b",re.I)
SHOW=re.compile(r"\bnight[\s._-]*court\b",re.I)

# Manually verified English-caption display pages, independently inspected.
# These are not SRT files and are not copied. The 2023 reboot is excluded.
SEED={
 "S01E05":"https://www.subtitlecat.com/subs/1079/Night%20Court%20%281984%29%20-%20S01E05%20-%20The%20Eye%20of%20the%20Beholder%20%28480p%20DVD%20x265%20Panda%29.eng.html",
 "S02E01":"https://www.subtitlecat.com/subs/1080/Night%20Court%20%281984%29%20-%20S02E01%20-%20The%20Nun%20%28480p%20DVD%20x265%20Panda%29.eng.html",
 "S02E03":"https://www.subtitlecat.com/subs/1080/Night%20Court%20%281984%29%20-%20S02E03%20-%20Billie%20and%20the%20Cat%20%28480p%20DVD%20x265%20Panda%29.eng.html",
 "S02E05":"https://www.subtitlecat.com/subs/1080/Night%20Court%20%281984%29%20-%20S02E05%20-%20The%20Computer%20Kid%20%28480p%20DVD%20x265%20Panda%29.eng.html",
 "S02E11":"https://www.subtitlecat.com/subs/1080/Night%20Court%20%281984%29%20-%20S02E11%20-%20Take%20My%20Wife%2C%20Please%20%28480p%20DVD%20x265%20Panda%29.eng.html",
 "S02E15":"https://www.subtitlecat.com/subs/1080/Night%20Court%20%281984%29%20-%20S02E15%20-%20An%20Old%20Flame%20%28480p%20DVD%20x265%20Panda%29.eng.html",
 "S02E16":"https://www.subtitlecat.com/subs/1080/Night%20Court%20%281984%29%20-%20S02E16%20-%20The%20Gypsy%20%28480p%20DVD%20x265%20Panda%29.eng.html",
 "S02E20":"https://www.subtitlecat.com/subs/1080/Night%20Court%20%281984%29%20-%20S02E20%20-%20Mac%20and%20Quon%20Le%20Together%20Again%20%28480p%20DVD%20x265%20Panda%29.eng.html",
 "S03E04":"https://www.subtitlecat.com/subs/1081/Night%20Court%20%281984%29%20-%20S03E04%20-%20Mac%20and%20Quon%20Le%20No%20Reservations%20%28480p%20DVD%20x265%20Panda%29.eng.html",
 "S03E13":"https://www.subtitlecat.com/subs/1081/Night%20Court%20%281984%29%20-%20S03E13%20-%20The%20Night%20Off%20%28480p%20DVD%20x265%20Panda%29.eng.html",
 "S03E15":"https://www.subtitlecat.com/subs/1081/Night%20Court%20%281984%29%20-%20S03E15%20-%20The%20Apartment%20%28480p%20DVD%20x265%20Panda%29.eng.html",
 "S04E01":"https://www.subtitlecat.com/subs/1120/night_court_s04e01_the_next_voice_you_hear.html",
 "S09E22":"https://www.subtitlecat.com/subs/1592/S09E22%20-%20The%201992%20Boat%20Show.html"
}

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__(); self.href=None;self.bits=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            self.href=dict(attrs).get("href");self.bits=[]
    def handle_data(self,s):
        if self.href is not None:self.bits.append(s)
    def handle_endtag(self,tag):
        if tag=="a" and self.href is not None:
            self.links.append((unescape("".join(self.bits)).strip(),self.href))
            self.href=None

def get(url,robots):
    if not robots.can_fetch(UA,url):
        raise PermissionError("robots policy disallows "+url)
    with urlopen(Request(url,headers={"User-Agent":UA}),timeout=25) as r:
        return r.read(MAX_HTML).decode("utf-8","replace")

def parse_list(text,index_url,found):
    links=Anchors();links.feed(text)
    for label,href in links.links:
        match=CODE.search(label)
        if not match or not SHOW.search(label):continue
        season=int(match.group(1));episode=int(match.group(2))
        # Reject unqualified S01-S03 sources that may belong to the 2023 revival.
        if season<4 and "1984" not in label:continue
        if not 1<=season<=9:continue
        key=f"S{season:02d}E{episode:02d}"
        target=urljoin(index_url,href)
        if urlparse(target).hostname not in ("www.subtitlecat.com","subtitlecat.com"):
            continue
        if "/subs/" not in urlparse(target).path:
            continue
        found.setdefault(key,{})[target]={
            "provider":"Subtitle Cat","episode_id":key,"source_page":target,
            "index_page":index_url,"display_label":label,
            "source_locator_status":"listed_in_upload_index",
            "full_caption_file_imported":False}

def save(path,obj):
    new=json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+"\n"
    if not path.exists() or path.read_text("utf-8")!=new:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(new,"utf-8");return True
    return False

def main():
    found={}
    for key,url in SEED.items():
        found.setdefault(key,{})[url]={"provider":"Subtitle Cat","episode_id":key,
            "source_page":url,"index_page":None,"display_label":key,
            "source_locator_status":"individually_verified_public_caption_display",
            "full_caption_file_imported":False}
    scanned=[];failures=[]
    robots=robotparser.RobotFileParser(BASE+"/robots.txt")
    try:robots.read()
    except Exception as exc:
        failures.append({"source":"robots.txt","error":str(exc)[:160]})
    else:
        q=SEARCH+"?"+urlencode({"search":"Night Court (1984)","show":"1000"})
        try:
            parse_list(get(q,robots),q,found)
            scanned.append(q)
        except Exception as exc:failures.append({"source":"search","error":str(exc)[:180]})
        # Dated May 2025 DVD caption upload cluster. Only index rows; no captions.
        for start in range(1666200,1666951,50):
            url=INDEX+"?from="+str(start)
            try:
                parse_list(get(url,robots),url,found)
                scanned.append(url)
            except PermissionError as exc:
                failures.append({"source":"upload_index","error":str(exc)[:180]})
                break
            except Exception as exc:
                failures.append({"source":url,"error":str(exc)[:180]})
            time.sleep(0.5)
    changed=0
    for key,versions in found.items():
        target=ROOT/"seasons"/key[:3]/key/"episode.json"
        if not target.exists():continue
        entry=json.loads(target.read_text("utf-8"))
        rows=entry["episode_sources"]
        for url,details in versions.items():
            if any(r.get("url")==url for r in rows):continue
            rows.append({"kind":"subtitle_index","provider":"Subtitle Cat",
              "url":url,"level":"episode_in_index","verified":True,"content_imported":False,
              "source_index":details.get("index_page"),
              "verification":details["source_locator_status"],
              "note":"External caption display page; subtitle bytes not held; version unconfirmed"})
        changed+=save(target,entry)
    report={
     "series":"night-court-1984","source":"Subtitle Cat",
     "rights_note":"Only URL/filename metadata indexed; no transcript or SRT copied.",
     "manually_verified_page_count":len(SEED),
     "scanned_index_urls":scanned,"scanning_errors":failures,
     "episodes_with_indexed_pages":len(found),
     "page_versions_indexed":sum(len(v) for v in found.values()),
     "episodic_page_versions":{key:list(versions.values()) for key,versions in sorted(found.items())}}
    save(ROOT/"catalog"/"subtitlecat-discovery.json",report)
    print("Episode pages discovered:",report["episodes_with_indexed_pages"],
          "versions:",report["page_versions_indexed"],"index URLs scanned:",len(scanned),
          "source records updated:",changed,"errors:",len(failures))

if __name__=="__main__":main()
