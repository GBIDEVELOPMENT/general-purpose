#!/usr/bin/env python3
"""Try bounded, episode-specific source-page candidates for 89 not-yet-held episodes.

Only 1984-series S05-S09 IDs in the fixed canonical CSV are accepted.
An *inferred page candidate* is never called a verified lead until its actual
page has been opened, the episode ID matched, and an English SRT validated.
Do not scrape site indexes, brute-force numeric /subs/ IDs, or bypass 429/403.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
from html.parser import HTMLParser
from http.client import IncompleteRead
import json
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
HOST = "www.subtitlecat.com"
MAX_BYTES = 1_000_000
TIMEOUT = 20
SRT_CUES = re.compile(rb"(?:\d{1,2}:)?\d{2}:\d{2}[,.]\d{3}\s*-->")
EXPECTED = {f"S{s:02d}E{e:02d}" for s, n in ((5, 22), (6, 22), (7, 24), (8, 24), (9, 22))
            for e in range(1, n + 1)}

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.active = None
        self.label = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.active = dict(attrs).get("href")
            self.label = []
    def handle_data(self, data):
        if self.active is not None:
            self.label.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self.active is not None:
            self.result.append((self.active, " ".join(self.label).strip()))
            self.active = None

def slug(title, keep_apostrophe_sep=True):
    text = re.sub(r"\(\s*(?:part|pt\.?)\s*(\d+)\s*\)", r"\1", title, flags=re.I)
    text = text.lower().replace("’", "'").replace("&", "and")
    if not keep_apostrophe_sep:
        text = text.replace("'", "")
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")

def candidates(entry):
    ep = entry["episode_id"].lower()
    title = entry["title"]
    prefix = "https://www.subtitlecat.com/subs/1121/"
    urls = []
    if entry["verified_page"]:
        urls.append((entry["verified_page"], "externally_verified_specific_page"))
    urls.extend([
        (prefix + "night_court_" + ep + "_" + slug(title) + ".html", "generated_snake_case"),
        (prefix + "night_court_" + ep + "_" + slug(title, False) + ".html", "generated_compact_apostrophe"),
        (prefix + quote("Night Court " + ep + " " +
                        re.sub(r"\(\s*(?:part|pt\.?)\s*(\d+)\s*\)", r"\1", title, flags=re.I),
                        safe="()-._~") + ".html", "generated_display_title")
    ])
    seen = set()
    for url, kind in urls:
        if url not in seen:
            seen.add(url)
            yield url, kind

def safe_url(url, expected_suffix):
    parts = urlsplit(url)
    if (parts.scheme != "https" or parts.hostname != HOST or parts.port or
            parts.username or parts.password or parts.query or parts.fragment):
        raise ValueError("non-allowlisted URL")
    if expected_suffix == ".html" and not parts.path.startswith("/subs/1121/"):
        raise ValueError("candidate page is outside the mapped caption-page family")
    if expected_suffix == ".srt" and not re.match(r"^/subs/[0-9]+/", parts.path):
        raise ValueError("download is outside the source download directories")
    if not parts.path.lower().endswith(expected_suffix):
        raise ValueError("unexpected source extension")
    return urlunsplit((parts.scheme, parts.netloc,
                      quote(unquote(parts.path), safe="/%-._~()'!,"), "", ""))

class StopForSiteRestriction(Exception):
    pass

def fetch(url, suffix, delay):
    url = safe_url(url, suffix)
    request = Request(url, headers={"User-Agent": "NightCourtEpisodeSourceAudit/1.0",
                                    "Accept": "text/html, text/plain, application/x-subrip, */*"})
    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            if urlsplit(response.url).hostname != HOST:
                raise ValueError("unexpected redirect")
            raw = response.read(MAX_BYTES + 1)
            ctype = response.headers.get("Content-Type", "")
        if len(raw) > MAX_BYTES:
            raise ValueError("oversized response")
        return raw, ctype
    except HTTPError as exc:
        if exc.code in (403, 429):
            raise StopForSiteRestriction("site denied access: HTTP " + str(exc.code)) from exc
        raise
    finally:
        time.sleep(delay)

def extract_english_srt(page_url, raw):
    html = raw.decode("utf-8", "replace")
    links = Links()
    links.feed(html)
    choices = []
    for href, label in links.result:
        if label.casefold() != "download":
            continue
        candidate = urljoin(page_url, href)
        suffix = urlsplit(candidate).path.lower()
        if suffix.endswith("-en.srt") or suffix.endswith(".eng-en.srt"):
            try:
                candidate = safe_url(candidate, ".srt")
                choices.append(candidate)
            except ValueError:
                continue
    choices = list(dict.fromkeys(choices))
    if len(choices) != 1:
        raise ValueError(f"expected exactly one English SRT link; found {len(choices)}")
    return choices[0]

def process(entry, output, delay):
    ep = entry["episode_id"]
    record = {"episode_id": ep, "title": entry["title"],
              "provenance": "owner-directed private research; third-party reuse not independently established",
              "source_candidates": [], "status": "unavailable"}
    for page, evidence in candidates(entry):
        attempt = {"url": page, "evidence": evidence}
        record["source_candidates"].append(attempt)
        try:
            raw, ctype = fetch(page, ".html", delay)
            if "text/html" not in ctype.lower() and b"<html" not in raw.lower()[:400]:
                raise ValueError("not an HTML caption display page")
            # Do not permit an unrelated episode or 2023-revival page to enter the archive.
            if ep.lower().encode("ascii") not in raw.lower():
                raise ValueError("page does not identify expected original-series episode")
            if b"subtitle" not in raw.lower():
                raise ValueError("not a subtitle display page")
            download_url = extract_english_srt(page, raw)
            srt, srt_ctype = fetch(download_url, ".srt", delay)
            if "text/html" in srt_ctype.lower() or len(SRT_CUES.findall(srt)) < 30:
                raise ValueError("English source has insufficient valid timed cues")
            path = output / f"{ep}.en.srt"
            path.write_bytes(srt)
            attempt["status"] = "downloaded_and_checked"
            record.update(status="downloaded_unreviewed", verified_page_url=page,
                          direct_download_url=download_url, source_page_evidence=evidence,
                          sha256=hashlib.sha256(srt).hexdigest(), size_bytes=len(srt),
                          cue_marker_count=len(SRT_CUES.findall(srt)), file=path.name)
            break
        except StopForSiteRestriction:
            raise
        except (HTTPError, URLError, TimeoutError, ValueError, IncompleteRead, OSError) as exc:
            attempt["status"] = "rejected"
            attempt["reason"] = str(exc)[:150]
    return record

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT/"research"/"unheld-original-series-caption-page-candidates.csv")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--delay", type=float, default=0.8)
    args = parser.parse_args()
    entries = list(csv.DictReader(args.manifest.open(encoding="utf-8", newline="")))
    if len(entries) != 89 or len({e["episode_id"] for e in entries}) != 89:
        raise ValueError("Expected exactly 89 distinct still-unheld episodes from baseline")
    if not all(e["episode_id"] in EXPECTED for e in entries):
        raise ValueError("Manifest contains an out-of-scope episode")
    if not 0.8 <= args.delay <= 10:
        raise ValueError("Delay must be >= 0.8 seconds")
    args.output.mkdir(parents=True, exist_ok=True)
    output = []
    restriction = None
    for entry in entries:
        try:
            if args.download:
                item = process(entry, args.output, args.delay)
            else:
                item = {"episode_id": entry["episode_id"], "status": "candidate_only",
                        "page_candidates": len(list(candidates(entry)))}
        except StopForSiteRestriction as exc:
            restriction = str(exc)
            item = {"episode_id": entry["episode_id"], "status": "site_access_restricted",
                    "reason": restriction}
        output.append(item)
        print(item["episode_id"], item["status"], flush=True)
        if restriction:
            break
    successes = sum(x["status"] == "downloaded_unreviewed" for x in output)
    report = {"series": "night-court-1984", "baseline_held_episodes": 104,
              "targeted_missing_episode_count": len(entries), "attempted_episodes": len(output),
              "downloaded": successes, "site_access_restriction": restriction,
              "new_sources_not_yet_in_repository": True, "items": output}
    (args.output/"retrieval-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(f"SUMMARY: downloaded={successes}, attempted={len(output)}; restriction={restriction}", flush=True)
    return 1 if restriction or (args.download and not successes) else 0

if __name__ == "__main__":
    sys.exit(main())
