#!/usr/bin/env python3
"""Lossless HTML-to-paragraph transcript extraction from *known* caption pages.

This extracts displayed plain text, NOT original SRT bytes, timestamps,
speaker attribution, or a verified-complete script. Never flatten unrelated
HTML, invent timestamps, or claim the page's reuse rights were verified.
"""
from html.parser import HTMLParser
from pathlib import Path
import argparse, hashlib, json
from tempfile import TemporaryDirectory

import import_dialogue as D

EXPECTED = {"S06E20", "S08E23"}

class OriginalParagraphs(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.in_paragraph = False
        self.current = []
        self.paragraphs = []
    def handle_starttag(self, tag, attrs):
        if tag == "div":
            if self.depth:
                self.depth += 1
            elif "orig-text" in dict(attrs).get("class", "").split():
                self.depth = 1
        if self.depth and tag == "p":
            if self.in_paragraph:
                raise ValueError("Nested source paragraphs")
            self.in_paragraph = True
            self.current = []
        if self.in_paragraph and tag == "br":
            self.current.append("\n")
    def handle_data(self, value):
        if self.in_paragraph:
            self.current.append(value)
    def handle_endtag(self, tag):
        if tag == "p" and self.in_paragraph:
            value = " ".join("".join(self.current).split())
            if value:
                self.paragraphs.append(value)
            self.current = []
            self.in_paragraph = False
        if tag == "div" and self.depth:
            self.depth -= 1

def extract(raw, ep):
    if ep.encode("ascii").lower() not in raw.lower():
        raise ValueError("The page does not identify the claimed episode")
    parser = OriginalParagraphs()
    parser.feed(raw.decode("utf-8", "replace"))
    paragraphs = parser.paragraphs
    if not 100 <= len(paragraphs) <= 2500:
        raise ValueError("Unconvincing original caption paragraph count")
    words = sum(len(v.split()) for v in paragraphs)
    if words < 1000:
        raise ValueError("Too little dialogue to use as a source witness")
    # Separate source paragraphs; do not synthesize cue numbering or time ranges.
    return "\n\n".join(paragraphs)+"\n", len(paragraphs), words

def selftest():
    fixture=b'<html>Outside<p>Not a source</p><div class="orig-text"><h3>Original subtitles</h3><p dir="auto">S06E20 Alice &amp; Bob</p><p>Second <b>sample</b> line.</p></div><p>Advertisement</p></html>'
    p = OriginalParagraphs()
    p.feed(fixture.decode())
    assert p.paragraphs == ["S06E20 Alice & Bob","Second sample line."]
    print("Original-page paragraph parser self-test passed")

def run(folder):
    report=json.loads((folder/"source-page-report.json").read_text("utf-8"))
    pages=report.get("pages", [])
    if report.get("series")!="night-court-1984" or len(pages)!=2 or {p["episode_id"] for p in pages}!=EXPECTED:
        raise ValueError("Wrong original-series source manifest")
    ready=[]
    with TemporaryDirectory(prefix="night-court-page-source-") as tmp:
        for row in pages:
            ep=row["episode_id"]
            file=folder/(ep+".source.html")
            raw=file.read_bytes()
            if len(raw)!=row["size_bytes"] or hashlib.sha256(raw).hexdigest()!=row["source_sha256"]:
                raise ValueError("Source HTML checksum mismatch: "+ep)
            source=row["source_url"]
            if not source.startswith("https://www.subtitlecat.com/subs/1121/"):
                raise ValueError("Unexpected source page")
            text, paragraphs, words=extract(raw,ep)
            path=Path(tmp)/(ep+".page-paragraphs.txt")
            path.write_text(text,encoding="utf-8")
            opts={
                "episode":ep, "edition":"Subtitle Cat source-page plain dialogue no timestamps",
                "language":"en","source_name":ep+" original caption display paragraphs",
                "source_url":source,"rights_basis":"user_provided",
                "confirmed":True, "complete":False,
                "notes":("Owner-directed private research. Derived from original displayed "
                         "HTML paragraphs, NOT a timed/original SRT or video-verified script. "
                         "Source HTML SHA-256: "+row["source_sha256"]+
                         "; source paragraphs: "+str(paragraphs))
            }
            # Validate every extract before mutating any source holdings.
            D.prepare(path,opts)
            ready.append((ep,path,opts,paragraphs,words))
        outcome=[]
        for ep,path,opts,paragraphs,words in ready:
            episode=json.loads((D.ROOT/"seasons"/ep[:3]/ep/"episode.json").read_text("utf-8"))
            if (episode["holdings"]["caption_files"] or episode["holdings"]["full_transcripts"]
                    or episode["holdings"]["other"]):
                outcome.append({"episode_id":ep,"status":"already_has_dialogue","paragraphs":paragraphs})
                continue
            D.import_one(path,opts)
            outcome.append({"episode_id":ep,"status":"page_derived_untimed_dialogue_imported",
                            "paragraphs":paragraphs,"words":words})
        D.rebuild_index()
        (D.ROOT/"research"/"two-original-page-dialogue-extraction.json").write_text(
            json.dumps({"source_run":40037923233,"source_artifact":12537977001,
                        "no_timing_preserved":True,"AV_verified":False,
                        "third_party_rights_not_adjudicated":True,"items":outcome},
                       indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps(outcome,ensure_ascii=False))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--source-folder",type=Path)
    args=ap.parse_args()
    if args.self_test:
        selftest()
    elif args.source_folder:
        run(args.source_folder)
    else:
        ap.error("Need --self-test or --source-folder")

if __name__=="__main__":
    main()
