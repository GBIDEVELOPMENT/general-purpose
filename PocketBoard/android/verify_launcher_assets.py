#!/usr/bin/env python3
"""Structural smoke checks for the PocketBoard source-traced launcher assets.

Build-time checks cannot establish which icon mask a launcher ultimately uses.
The two-layer resource contract prevents accidental preclipped black tiles.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
DRAWABLE = BASE / "app/src/main/res/drawable"
MIPMAP = BASE / "app/src/main/res/mipmap-anydpi-v26"
ASSETS = ROOT / "assets/launcher"
ANDROID = "{http://schemas.android.com/apk/res/android}"

def parse(path: Path):
    assert path.is_file(), f"Missing {path}"
    return ET.parse(path).getroot()

def attr(element, name):
    return element.get(ANDROID + name)

fg = parse(DRAWABLE / "ic_launcher_foreground.xml")
bg = parse(DRAWABLE / "ic_launcher_background.xml")
assert fg.tag == "vector" and bg.tag == "vector"
assert len(fg.findall("group/path")) == 1
white = fg.find("group/path")
assert attr(white, "fillColor") == "#FFFFFFFF"
assert attr(white, "fillType") == "evenOdd"
# Frame outer + frame hole + ten keys + long space bar = thirteen contours.
assert attr(white, "pathData").count("M") == 13
assert fg.find(".//clip-path") is None
assert bg.find(".//clip-path") is None
stripes = bg.findall("path")
assert len(stripes) == 7
assert [attr(p, "fillColor").upper() for p in stripes] == [
    "#E92F61", "#FD791E", "#FDC405", "#03CE43",
    "#02B8B6", "#0E70F7", "#7D3CEE"
]  # The seven launcher bands are a subset of the canonical UI palette.
assert all(attr(p, "fillColor") != "#FF000000" for p in stripes)
for name in ("ic_launcher.xml", "ic_launcher_round.xml"):
    icon = parse(MIPMAP / name)
    assert icon.tag == "adaptive-icon", name
    assert attr(icon.find("foreground"), "drawable") == "@drawable/ic_launcher_foreground"
    assert attr(icon.find("background"), "drawable") == "@drawable/ic_launcher_background"
for name in ("keyboard-symbol.svg", "squircle-mask.svg", "circle-mask.svg",
             "rainbow-background.svg", "preview-circle.svg", "preview-squircle.svg"):
    assert parse(ASSETS / name).tag == "{http://www.w3.org/2000/svg}svg", name
header = parse(DRAWABLE / "pb_header_icon.xml")
assert len(header.findall(".//clip-path")) == 1
assert any(attr(p, "fillType") == "evenOdd" for p in header.findall("path"))
print("PocketBoard adaptive launcher: 7 stripes, 13 keyboard contours, and two-layer masks verified")
