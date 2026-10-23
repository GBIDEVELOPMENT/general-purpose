#!/usr/bin/env python3
"""Bounded evidence-preserving fetch of last original-series dialogue display page."""
import hashlib, json, re, sys
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

SOURCES = {
    "S09E19": "https://www.subtitlecat.com/subs/1592/S09E19%20-%20PS%20Do%20i%20know%20you.html",
}
def main(directory):
    directory.mkdir(parents=True,exist_ok=True)
    report=[]
    for ep,url in SOURCES.items():
        p=urlsplit(url)
        if p.hostname!="www.subtitlecat.com" or p.scheme!="https":
            raise ValueError("Source outside allowlist")
        with urlopen(Request(url,headers={"User-Agent":"NightCourtEpisodeSourceAudit/1.0"}), timeout=25) as resp:
            if urlsplit(resp.url).hostname!="www.subtitlecat.com":raise ValueError("Redirected outside allowlist")
            raw=resp.read(1_000_001)
        if len(raw)>1_000_000:raise ValueError("Oversized HTML")
        if ep.lower().encode() not in raw.lower():raise ValueError("Wrong episode")
        file=directory/(ep+".source.html")
        file.write_bytes(raw)
        record={"episode_id":ep,"source_url":url,"source_sha256":hashlib.sha256(raw).hexdigest(),
                "size_bytes":len(raw),"html_timecode_mentions":len(re.findall(rb"\d\d:\d\d:\d\d",raw)),
                "status":"source_html_preserved_as_private_actions_artifact_not_dialogue_import"}
        report.append(record)
        print(ep,"bytes",len(raw),"timecode mentions",record["html_timecode_mentions"])
    (directory/"source-page-report.json").write_text(json.dumps({"series":"night-court-1984","pages":report},indent=2)+"\n")
if __name__=="__main__":main(Path(sys.argv[1]))
