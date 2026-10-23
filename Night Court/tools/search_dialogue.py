#!/usr/bin/env python3
"""Search locally HELD Night Court dialogue alongside the licensed synopsis index.

No network calls, imports or downloads. Results link to source cues, timestamps,
individual versions, exact article revisions and provenance. A synopsis match is
never represented as spoken dialogue or a verified scene.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]

def load_jsonl(file):
    if not file.exists():return []
    return [json.loads(line) for line in file.read_text("utf-8").splitlines() if line.strip()]

def explicit_speaker(text):
    a=re.match(r"^\s*<v\s+([^>]+)>",text)
    if a:return {"label":a.group(1).strip(),"basis":"explicit_webvtt_voice_tag"}
    b=re.match(r"^\s*([A-Z][A-Z0-9 .'-]{1,30}):(?:\s|$)",text)
    if b:return {"label":b.group(1).strip(),"basis":"explicit_caption_text_prefix"}
    return None

def text_matches(text,term):
    return bool(re.search(re.escape(term),text,flags=re.I))

def clip(text,term,limit=180):
    # Use original text offsets, not casefold offsets (which may change length).
    m=re.search(re.escape(term),text,flags=re.I)
    single=" ".join(text.split())
    if not m:return single[:limit]
    start=max(0,m.start()-60);end=min(len(text),m.end()+100)
    snippet=" ".join(text[start:end].split())
    return ("…" if start else "")+snippet[:limit]+("…" if end<len(text) or len(snippet)>limit else "")

def records(needle,domain,episode=None,season=None,edition=None,language=None,timecoded=False):
    results=[]
    if domain in ("dialogue","both"):
        index=load_jsonl(ROOT/"catalog"/"dialogue-index.jsonl")
        for entry in index:
            ep=entry["episode_id"]
            if episode and ep!=episode:continue
            if season and int(ep[1:3])!=season:continue
            if edition and edition.lower() not in entry["edition"].lower():continue
            if language and language.lower()!=entry["language"].lower():continue
            if timecoded and entry["format"] not in ("srt","vtt"):continue
            manifest=ROOT/entry["manifest"]
            if not manifest.exists():
                raise ValueError("Indexed dialogue witness missing: "+str(manifest))
            meta=json.loads(manifest.read_text("utf-8"))
            source=ROOT/"seasons"/ep[:3]/ep/meta["segments_path"]
            for cue in load_jsonl(source):
                if not text_matches(cue["text"],needle):continue
                results.append({
                    "episode_id":ep,"kind":"held_caption" if meta["timecoded"] else "held_plain_transcript",
                    "match_text_preview":clip(cue["text"],needle),
                    "cue":cue["cue"],"start_ms":cue["start_ms"],"end_ms":cue["end_ms"],
                    "speaker_explicit":explicit_speaker(cue["text"]),
                    "edition":meta["edition"],"language":meta["language"],"format":meta["format"],
                    "version_id":meta["version_id"],
                    "source_sha256":meta["sha256"],"manifest_path":entry["manifest"],
                    "evidence_locator":{"segments_file":meta["segments_path"],
                                        "cue_ordinal":cue["cue"]},
                    "completeness_status":meta["completeness_status"],
                    "note":"Source witness: speaker inferred only when explicitly labeled in the cue."
                })
    if domain in ("capsules","both"):
        entries=load_jsonl(ROOT/"catalog"/"episode-knowledge.jsonl")
        for ep in entries:
            if episode and ep["id"]!=episode:continue
            if season and ep["season"]!=season:continue
            # Edition and language constraints exclude synopsis-only results.
            if edition or language or timecoded:continue
            text=ep["plot_source_plaintext"]
            if not text_matches(text,needle):continue
            results.append({
               "episode_id":ep["id"],"title":ep["title"],"kind":"licensed_synopsis_not_dialogue",
               "match_text_preview":clip(text,needle),
               "source_url":ep["source"]["permalink"],
               "source_path":ep["source"]["path"],"source_revision":ep["source"]["revision"],
               "license":ep["source"]["license"],
               "note":"Encyclopedia synopsis, not a quote from the episode or a timed cue."
            })
    priority={"held_caption":0,"held_plain_transcript":1,"licensed_synopsis_not_dialogue":2}
    return sorted(results,key=lambda x:(x["episode_id"],priority.get(x["kind"],9),
                                      x.get("start_ms") or 0,x.get("cue") or 0))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phrase",help="literal phrase to search (case insensitive)")
    parser.add_argument("--source",choices=["both","dialogue","capsules"],default="both")
    parser.add_argument("--episode",help="exact SxxEyy")
    parser.add_argument("--season",type=int,choices=range(1,10))
    parser.add_argument("--edition",help="edition label substring")
    parser.add_argument("--language",help="only this dialogue language")
    parser.add_argument("--timecoded",action="store_true")
    parser.add_argument("--limit",type=int,default=30)
    parser.add_argument("--json",action="store_true",help="emit citation-ready JSON")
    args=parser.parse_args()
    if args.limit<1 or args.limit>2000:parser.error("--limit must be in 1..2000")
    if args.episode and not re.fullmatch(r"S(?:0[1-9])E(?:0[1-9]|[12][0-9])",args.episode):
        parser.error("--episode must use SxxEyy")
    all_matches=records(args.phrase,args.source,args.episode,args.season,
                        args.edition,args.language,args.timecoded)
    payload={"phrase":args.phrase,"matches":len(all_matches),"shown":min(len(all_matches),args.limit),
             "source_distinction":"Held dialogue witnesses vs separate CC BY-SA synopses",
             "results":all_matches[:args.limit]}
    if args.json:
        print(json.dumps(payload,indent=2,ensure_ascii=False))
    else:
        print(f"{len(all_matches)} matches ({payload['shown']} shown); held dialogue and synopsis evidence kept separate.")
        for x in payload["results"]:
            when=(f" [{x['start_ms']/1000:.3f}s]" if x.get("start_ms") is not None else "")
            suffix=(f" ({x['edition']}; cue {x['cue']})" if x.get("version_id") else " (licensed synopsis)")
            print(f"{x['episode_id']}{when}{suffix}\n  {x['match_text_preview']}")
        if not all_matches:
            print("No matching held dialogue or licensed synopsis. This is not evidence that the episode lacks the phrase.")

if __name__=="__main__":main()
