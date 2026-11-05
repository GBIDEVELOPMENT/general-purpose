#!/usr/bin/env python3
"""Fail CI if active PocketBoard colours or traced vector assets drift.

The list below is the approved palette manifest. To approve a new colour,
change this explicit manifest, PocketBoardPalette.kt and the design reference
together. Archived historical artwork is deliberately excluded.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "android/app/src/main/java/dev/pocketkeyboard"
DRAWABLE = ROOT / "android/app/src/main/res/drawable"
NS = "{http://schemas.android.com/apk/res/android}"
APPROVED = {
    "CHARCOAL": "FF171923", "DISCONNECTED": "FF283040",
    "CREAM": "FFFCF4E9", "MUTED_CREAM": "FFE6DDD0",
    "HINT_CREAM": "FFD0C9BE", "PRESS_RIPPLE": "33FCF4E9",
    "BLUE": "FF0E70F7", "TEAL": "FF02B8B6", "PINK": "FFFA398F",
    "PURPLE": "FF7D3CEE", "ORANGE": "FFFD791E", "YELLOW": "FFFDC405",
    "GREEN": "FF03CE43", "RED_PINK": "FFE92F61", "SKY_BLUE": "FF22A3FF",
    "VIOLET": "FFA857FF", "CORAL": "FFFF5A3C",
    "MAGENTA": "FFD94BDE", "LIME": "FF76DE1A", "INDIGO": "FF4D62FF",
}
BUTTON_ORDER = ("BLUE", "TEAL", "PINK", "PURPLE", "ORANGE", "YELLOW",
                "GREEN", "RED_PINK", "SKY_BLUE", "VIOLET", "CORAL",
                "MAGENTA", "LIME", "INDIGO")
RAINBOW = ("RED_PINK", "ORANGE", "YELLOW", "GREEN", "TEAL", "BLUE", "PURPLE")
SYMBOLS = {
    "connected-check": "pb_connected_check", "search": "pb_discover",
    "clear": "pb_clear", "microphone": "pb_mic",
    "volume-down": "pb_volume_down", "volume-up": "pb_volume_up",
    "mute": "pb_volume_mute", "previous-track": "pb_media_prev",
    "play": "pb_media_play", "pause": "pb_media_pause",
    "next-track": "pb_media_next", "apps-grid": "pb_apps",
    "overlapping-windows": "pb_copy", "windows-check": "pb_all_copy",
    "windows-plus": "pb_paste", "escape": "pb_escape",
    "tab": "pb_tab", "enter": "pb_enter",
}
SHAPES = (
    "search", "clear", "microphone", "volume-down", "volume-up", "mute",
    "previous-track", "pause", "next-track", "apps-grid",
    "overlapping-windows", "windows-check", "windows-plus",
    "escape", "tab", "enter", "connected-pill"
)

def norm(path):
    return " ".join(path.split())

def xml(path):
    assert path.is_file(), f"Missing asset: {path}"
    return ET.parse(path).getroot()

def argb(s):
    if s.startswith("#") and len(s) == 7:
        return "FF" + s[1:].upper()
    if s.startswith("#") and len(s) == 9:
        return s[1:].upper()
    raise AssertionError(f"Noncanonical literal: {s!r}")

palette_source = (JAVA / "PocketBoardPalette.kt").read_text()
actual = dict(re.findall(r"\bval\s+([A-Z_]+)\s*=\s*0x([A-Fa-f0-9]{8})", palette_source))
assert {k: v.upper() for k, v in actual.items()} == APPROVED, "Palette changed without approval"
actual_button_list = re.search(r"val BUTTON_COLORS:[^=]+=\s*listOf\((.*?)\)", palette_source, re.S)
assert actual_button_list, "No canonical action-button order"
assert tuple(re.findall(r"\b[A-Z][A-Z_]+\b", actual_button_list.group(1))) == BUTTON_ORDER

main = (JAVA / "MainActivity.kt").read_text()
assert not re.search(r"\b0x[0-9a-fA-F]{6,8}\b|Color\.(?:WHITE|BLACK|rgb)\b", main), "Literal runtime colour"
assert "statusShape(if (ready) PocketBoardPalette.GREEN" in main
assert "R.drawable.pb_shape_connected" in main
assert "R.drawable.pb_connected_check" in main
assert "R.drawable.pb_shape_pause" in main
assert "R.drawable.pb_media_play" in main and "R.drawable.pb_media_pause" in main
assert "showingPause = !showingPause" in main, "Play/pause must remain one toggle"
assert main.count('Triple("') - main.count('""EMPTY"') >= 14  # sanity; exact check below
assert len(re.findall(r'Triple\(".*?", ".*?", "(?!EMPTY)[A-Z_]+?"\)', main)) == 14
for old in ("pb_button_squircle", "pb_choose", "pb_backspace"):
    assert old not in main, f"Legacy resource still referenced: {old}"
assert "typeface = resources.getFont(R.font.morning_rainbow)" in main
for hue in RAINBOW:
    assert f"PocketBoardPalette.{hue}" in main
allowed_colors = set(APPROVED.values()) | {"FFFFFFFF", "00000000"}
for res in DRAWABLE.glob("*.xml"):
    for node in xml(res).iter():
        for k, v in node.attrib.items():
            if k in (NS + "fillColor", NS + "strokeColor", NS + "tint") and v.startswith("#"):
                assert argb(v) in allowed_colors, f"Unauthorized colour {v} in {res.name}"
for legacy in ("pb_button_squircle.xml", "pb_choose.xml", "pb_backspace.xml", "ic_launcher_art.xml"):
    assert not (DRAWABLE / legacy).exists(), f"Retired vector still ships: {legacy}"
assert not (ROOT / "assets/symbols").exists(), "Old symbol source directory not retired"

def validate_svg(source, dest):
    svg = xml(source)
    vector = xml(DRAWABLE / (dest + ".xml"))
    assert svg.tag.endswith("}svg") and vector.tag == "vector", source
    view = svg.attrib["viewBox"].split()
    assert [float(n) for n in view[2:]] == [
        float(vector.attrib[NS + "viewportWidth"]),
        float(vector.attrib[NS + "viewportHeight"]),
    ], source
    a = svg.findall("{http://www.w3.org/2000/svg}path")
    z = vector.findall("path")
    assert len(a) == len(z) and len(a) > 0, source
    for old, new in zip(a, z):
        assert norm(old.attrib["d"]) == norm(new.attrib[NS + "pathData"]), source
        assert new.attrib[NS + "fillColor"] == "#FFFCF4E9", source
        assert new.attrib.get(NS + "fillType") == (
            "evenOdd" if old.attrib.get("fill-rule") == "evenodd" else None
        ), source

for symbol, res in SYMBOLS.items():
    validate_svg(ROOT / f"assets/button-symbols/{symbol}.svg", res)
for shape in SHAPES:
    name = "connected" if shape == "connected-pill" else shape.replace("-", "_")
    validate_svg(ROOT / f"assets/button-silhouettes/{shape}.svg", f"pb_shape_{name}")
expected_bands = [APPROVED[k] for k in RAINBOW]
background = xml(DRAWABLE / "ic_launcher_background.xml")
header = xml(DRAWABLE / "pb_header_icon.xml")
assert [argb(p.attrib[NS+"fillColor"]) for p in background.findall("path")] == expected_bands
assert [argb(p.attrib[NS+"fillColor"]) for p in header.findall("group/path")] == expected_bands
for art in ("rainbow-background.svg", "preview-squircle.svg", "preview-circle.svg"):
    tree = xml(ROOT / "assets/launcher" / art)
    fills = [argb(p.attrib["fill"]) for p in tree.iter()
             if p.tag.endswith("}path") and p.attrib.get("fill", "").startswith("#")]
    assert fills[:7] == expected_bands, art
print("PocketBoard palette and 18 glyph + 17 silhouette SVG→Android contour contracts verified")
