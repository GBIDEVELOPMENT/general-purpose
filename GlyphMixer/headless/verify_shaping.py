#!/usr/bin/env python3
"""Independently verify Glyph Mixer GSUB behavior with HarfBuzz shaping."""
import argparse
import json
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont


def shape(raw: bytes, text: str, features=None):
    face = hb.Face(raw)
    font = hb.Font(face)
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer, features or {})
    return [item.codepoint for item in buffer.glyph_infos]


def check(font_path: Path, report_path: Path):
    raw=font_path.read_bytes()
    tt=TTFont(font_path)
    glyph_order=tt.getGlyphOrder()
    cmap=tt.getBestCmap()
    report=json.loads(report_path.read_text())
    features=set(report.get("features", []))
    alternate_pairs=[(cp,glyph_order.index(name+".alt01"))
                     for cp,name in cmap.items() if name+".alt01" in glyph_order]
    checks=[]
    for cp,alt_id in alternate_pairs:
        character=chr(cp)
        if "ss01" in features:
            shaped=shape(raw,character,{"ss01":True,"salt":False,"calt":False})
            if shaped!=[alt_id]:
                raise AssertionError(f"ss01 shaping failed for U+{cp:04X}: {shaped} != {alt_id}")
            checks.append("ss01 U+%04X" % cp)
        if "calt" in features:
            normal=shape(raw,character*2,{"calt":False,"salt":False,"ss01":False})
            context=shape(raw,character*2,{"calt":True,"salt":False,"ss01":False})
            expected=[cmap and glyph_order.index(cmap[cp]),alt_id]
            if normal!=[expected[0],expected[0]]:
                raise AssertionError(f"calt off baseline failure for U+{cp:04X}: {normal}")
            if context!=expected:
                raise AssertionError(f"calt adjacent-repeat failure for U+{cp:04X}: {context} != {expected}")
            checks.append("calt repeated U+%04X" % cp)
    if ("calt" in features or "ss01" in features) and not checks:
        raise AssertionError("GSUB features requested but no matching alternate pairs found")
    return {
        "font":str(font_path),
        "checked_alternate_characters":len(alternate_pairs),
        "shaping_assertions":len(checks),
        "sample_checks":checks[:12],
        "engine":"HarfBuzz via uharfbuzz"
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--report",required=True)
    args=parser.parse_args()
    report_path=Path(args.report)
    metadata=json.loads(report_path.read_text())
    output=Path(metadata["output"])
    print(json.dumps(check(output,report_path),indent=2))
if __name__=="__main__":
    main()
