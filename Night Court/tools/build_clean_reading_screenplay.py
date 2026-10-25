#!/usr/bin/env python3
"""Make the existing full-caption scripts read like screenplays.

Remove provenance clutter from the reading copy, not from the archive.
Every dialogue source marker is saved in an index and original word SHA list.
Names remain provisional. No source AV or extra recognizer is needed.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from render_in_scene_stage_directions_v6 import render as render_v6
from build_caption_first_working_drafts import ROOT,SOURCE_SHA

OUT="clean-reading-screenplay-v1"
SOURCE_LINE=re.compile(r"^\*Source: (?P<ref>C\d{3}\.\d+(?:–C\d{3}\.\d+)?) · (?P<when>.+)\*$")
SPEAKER_LINE=re.compile(r"^\*\*(?P<name>.+)\*\*$")

def build(ep,root=ROOT):
    if ep not in ("S01E01","S09E19"):raise ValueError("Unknown pilot")
    source,prior,review=render_v6(ep,root)
    head,sep,rest=source.partition("## Source-picture motion and setting evidence")
    if not sep:raise ValueError("No separate picture archive evidence")
    first=head.find("## Readable original-caption screenplay")
    if first<0:raise ValueError("Unexpected source screenplay")
    clean=head[first:]
    # Pre-dialogue headings are retained but verbose evidence belongs in its
    # own linked archive; source-matched stage directions stay in the reading.
    clean=clean.replace(
      "*Editorial grouping only; transitions and blocking require\ncontinuous original source AV confirmation.*\n","")
    lines=clean.splitlines()
    rendered=[];index=[];pending=None
    for line in lines:
        match=SOURCE_LINE.fullmatch(line)
        if match:
            if pending is None:raise ValueError("Orphan source reference")
            item={"number":len(index)+1,"reading_line":pending["reading_line"],
                  "speaker":pending["speaker"],"source_ref":match["ref"],
                  "source_time_kind":match["when"],
                  "source_text_sha256":pending["text_sha256"]}
            index.append(item);pending=None
            continue
        if line.startswith("**") and line.endswith("**"):
            m=SPEAKER_LINE.fullmatch(line)
            if m:
                if pending is not None:raise ValueError("Missing previous source reference")
                pending={"speaker":m["name"],"reading_line":len(rendered)+1,"text_sha256":None}
                line=m["name"].upper()
        if pending is not None and pending["text_sha256"] is None and line!=pending["speaker"].upper() and line.strip():
            pending["text_sha256"]=hashlib.sha256(line.encode()).hexdigest()
        # Do not replace the source-provenance identifiers embedded in existing
        # observed stage directions; they are necessary to evaluate real acts.
        rendered.append(line)
    if pending is not None:raise ValueError("Unclosed original dialogue reference")
    original_speech=prior["source_original_speaking_units"]
    if len(index)>original_speech or len(index)<original_speech-40:
        raise ValueError("Whole dialogue speaking units lost in reading edition")
    if any(x["source_text_sha256"] is None for x in index):
        raise ValueError("Missing source speech text")
    output="\n".join(rendered).rstrip()+"\n"
    # Include a lightweight up-front reader notice, not hundreds of inline
    # provenance footnotes; separately ship per-line exact source index.
    output=("**Working screenplay · editorial reading copy.** "
            "Character labels are provisional; observed video passages may "
            "not be synchronized with dialogue. Original source wording and "
            "cue references are retained in the adjacent reading index.\n\n"+output)
    result={
      "schema":"night-court-clean-readable-script-source-index/1",
      "episode_id":ep,"original_caption_sha256":SOURCE_SHA[ep],
      "source_original_cues":prior["source_original_cues"],
      "source_original_speaking_units":original_speech,
      "indexed_reading_dialogue_blocks":len(index),
      "original_source_cue_unit_hashes_in_order":prior["v5_original_unit_text_sha256_in_order"],
      "original_dialogue_and_cue_timing_unchanged":True,
      "original_timing_generated_for_untimed_source":False,
      "source_speakers_verified":False,
      "full_episode_editor_ready":False,
      "independent_av_certification":False,
      "dialogue_index":index
    }
    return output,result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--episode",choices=["S01E01","S09E19"],required=True)
    p.add_argument("--output-root",type=Path,default=ROOT)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    s,m=build(a.episode)
    out=a.output_root/"seasons"/a.episode[:3]/a.episode/"derived"/OUT
    outputs={"screenplay-clean.md":s,"source-reading-index.json":json.dumps(m,indent=2,ensure_ascii=False)+"\n"}
    if a.check:
        for n,c in outputs.items():
            if (out/n).read_text("utf-8")!=c:raise ValueError("Stale reading edition "+n)
    else:
        out.mkdir(parents=True,exist_ok=True)
        for n,c in outputs.items():(out/n).write_text(c,encoding="utf-8")
    print(a.episode,m["indexed_reading_dialogue_blocks"],"readable dialogue blocks")
if __name__=="__main__":main()
