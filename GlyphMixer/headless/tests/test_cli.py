"""Real fontTools regression tests for headless Glyph Mixer."""
import json
import tempfile
import unittest
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from GlyphMixer.headless.cli import RecipeError, build, codepoint, codepoints, root_path


def make_font(path: Path, family: str, scale: int, cmap: dict[int, str]):
    glyph_order = [".notdef"] + sorted(set(cmap.values()))
    glyphs = {}
    metrics = {}
    for num, glyph in enumerate(glyph_order):
        pen = TTGlyphPen(None)
        if glyph != ".notdef":
            x = num * 10
            pen.moveTo((x, 0))
            pen.lineTo((x + scale // 3, scale // 2))
            pen.lineTo((x + scale // 2, 0))
            pen.closePath()
        glyphs[glyph] = pen.glyph()
        metrics[glyph] = (scale // 2, 0)
    fb = FontBuilder(scale, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap({cp: name for cp, name in cmap.items()})
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=int(scale * .8), descent=-int(scale * .2))
    fb.setupNameTable({"familyName": family, "styleName": "Regular"})
    fb.setupOS2(sTypoAscender=int(scale*.8), sTypoDescender=-int(scale*.2))
    fb.setupPost()
    fb.setupMaxp()
    fb.setupHead()
    fb.save(path)


class HeadlessTest(unittest.TestCase):
    def test_codepoint_parsing(self):
        self.assertEqual(codepoint("A"), 65)
        self.assertEqual(codepoint("U+2605"), 9733)
        self.assertEqual(codepoints("lowercase", {}), list(range(97, 123)))
        self.assertEqual(codepoints("chars:nAn", {}), [65, 110])
        with self.assertRaises(RecipeError):
            codepoint("U+D800")
        with self.assertRaises(RecipeError):
            root_path("../outside", must_exist=False)

    def test_mixed_font_gsub_and_unicode_survive_roundtrip(self):
        # Use actual TTF files generated on the fly so independent inputs
        # have different UPM and outlines.
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[2]) as tmp:
            folder = Path(tmp)
            a, b, c = (folder / f"{name}.ttf" for name in ("a", "b", "c"))
            make_font(a, "Base", 1000, {65: "A", 66: "B", 97: "a", 110: "n"})
            make_font(b, "Lower Donor", 2000, {97: "a", 110: "n"})
            make_font(c, "Upper Donor", 800, {65: "A", 66: "B"})
            relative = lambda p: str(p.relative_to(root_path(".")))
            recipe = {
                "version": 1,
                "name": "Recipe Hybrid",
                "base": "A",
                "sources": {"A": {"path": relative(a)},
                            "B": {"path": relative(b)},
                            "C": {"path": relative(c)}},
                "operations": [
                    {"action": "replace", "source": "B", "target": "lowercase"},
                    {"action": "alternate", "source": "C", "target": "uppercase",
                     "features": ["aalt", "salt", "ss01", "calt"],
                     "context": "adjacent-repeat"},
                    {"action": "reassign", "source": "B", "glyph": "n",
                     "destination": "U+2605"}
                ],
            }
            destination = folder / "hybrid.ttf"
            report = build(recipe, destination)
            self.assertEqual(report["mapped_characters"], 5)
            self.assertEqual(report["alternate_characters"], 2)
            self.assertEqual(report["features"], ["aalt", "salt", "ss01", "calt"])
            self.assertIn("missing", report["steps"][0])
            self.assertTrue(destination.with_suffix(".report.json").exists())
            with TTFont(destination) as font:
                cmap = font.getBestCmap()
                self.assertEqual(cmap[65], "u0041")
                self.assertEqual(cmap[97], "u0061")
                self.assertEqual(cmap[9733], "u2605")
                self.assertIn("u0041.alt01", font.getGlyphOrder())
                self.assertEqual(font["head"].unitsPerEm, 1000)
                self.assertEqual(set(record.FeatureTag for record in
                                     font["GSUB"].table.FeatureList.FeatureRecord),
                                 {"aalt", "salt", "ss01", "calt"})
                # Source B's 2000 UPM advance scales to the base 1000 UPM.
                self.assertEqual(font["hmtx"]["u0061"][0], 500)
                self.assertNotIn(0x2605, recipe["sources"]["A"])

    def test_missing_strict_glyph_aborts(self):
        with self.assertRaises(RecipeError):
            build({"version": 1, "name": "Invalid", "base": "bad",
                   "sources": {"A": {"path": "nonexistent.ttf"}},
                   "operations": []})


if __name__ == "__main__":
    unittest.main()
