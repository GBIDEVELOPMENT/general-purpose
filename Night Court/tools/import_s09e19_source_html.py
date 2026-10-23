#!/usr/bin/env python3
"""Import original 1984 Night Court S09E19 source-page dialogue as untimed text.

The preserved HTML source contains original displayed dialogue, not an English
SRT file or verifiable AV timing. Its attribution remains unadjudicated.
"""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import import_dialogue as D
from import_original_caption_page_text import extract

ROOT = Path(__file__).resolve().parents[1]
EP="S09E19"
EXPECTED_URL="https://www.subtitlecat.com/subs/1592/S09E19%20-%20PS%20Do%20i%20know%20you.html"

def main(folder):
    report=json.loads((folder/"source-page-report.json").read_text("utf-8"))
    entries=report.get("pages")
    if report.get("series")!="night-court-1984" or not isinstance(entries,list) or len(entries)!=1:
        raise ValueError("Expected exactly one original-series source")
    witness=entries[0]
    if witness.get("episode_id")!=EP or witness.get("source_url")!=EXPECTED_URL:
        raise ValueError("Wrong source episode, identity, or URL")
    raw=(folder/(EP+".source.html")).read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if len(raw)!=witness["size_bytes"] or sha!=witness["source_sha256"]:
        raise ValueError("Original source page integrity mismatch")
    txt, paragraph_count, word_count=extract(raw,EP)
    ep_path=ROOT/"seasons"/"S09"/EP/"episode.json"
    ep=json.loads(ep_path.read_text("utf-8"))
    existing=sum(len(ep["holdings"][name]) for name in ("caption_files","full_transcripts"))
    existing+=sum(bool(h.get("version_id") and h.get("manifest_file")) for h in ep["holdings"]["other"])
    if existing:
        raise ValueError("S09E19 already has dialogue: do not duplicate an existing witness")
    with TemporaryDirectory(prefix="night-court-s09e19-original-") as tmp:
        file=Path(tmp)/(EP+".page-source.txt")
        file.write_text(txt,encoding="utf-8")
        opts={
            "episode":EP,
            "edition":"Subtitle Cat S09E19 original caption page untimed",
            "language":"en",
            "source_name":"S09E19 original-subtitle display paragraphs",
            "source_url":EXPECTED_URL,
            "rights_basis":"user_provided",
            "confirmed":True,
            "complete":False,
            "notes":("Owner-directed private research retention; third-party rights not independently "
                     "assessed. The source is HTML displayed paragraphs, not an original SRT. "
                     "No timecodes or original cue numbering retained. "
                     "Original HTML SHA-256 "+sha),
        }
        # Check every source before creating immutable episode assets.
        D.prepare(file,opts)
        D.import_one(file,opts)
        records=D.rebuild_index()
    summary={
        "series":"night-court-1984","episode_id":EP,
        "source_run":40038491460,"source_artifact_id":12538106920,
        "html_sha256":sha,"plain_text_paragraphs":paragraph_count,"words":word_count,
        "new_dialogue_witnesses":1,"indexed_witnesses":len(records),
        "format":"untimed_text_from_source_html",
        "timing_verified":False,"audiovisual_completeness_verified":False,
        "rights_independently_established":False,
        "source_url":EXPECTED_URL
    }
    (ROOT/"research"/"s09e19-final-dialogue-acquisition.json").write_text(
       json.dumps(summary,indent=2,ensure_ascii=False)+"\n","utf-8")
    print("S09E19: imported",paragraph_count,"untimed original-caption paragraphs;",
          len(records),"total held dialogue witnesses")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: import_s09e19_source_html.py FOLDER")
    main(Path(sys.argv[1]))
