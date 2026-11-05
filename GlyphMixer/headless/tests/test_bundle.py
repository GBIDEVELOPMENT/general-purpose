"""Verify that a saved Android project compiles with GSUB through headless mode."""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont

from GlyphMixer.headless import cli
from GlyphMixer.headless.bundle import compile_bundle
from test_cli import make_font


class BundleTest(unittest.TestCase):
    def test_mobile_save_restores_overrides_and_contextual_variations(self):
        with tempfile.TemporaryDirectory(dir=cli.ROOT/"GlyphMixer") as directory:
            folder=Path(directory)
            a,b=folder/"a.ttf",folder/"b.ttf"
            make_font(a,"Base",1000,{65:"A",97:"a",110:"n",111:"o",101:"e"})
            make_font(b,"Donor",2000,{65:"A",97:"a",110:"n",111:"o",101:"e"},
                      extra_glyphs=("swash",))
            base=TTFont(a)
            donor=TTFont(b)
            cmap=base.getBestCmap()
            order_base=base.getGlyphOrder()
            order_donor=donor.getGlyphOrder()
            assignments=[[cp,{"fontId":"f00001","glyphIndex":order_base.index(name)}]
                         for cp,name in sorted(cmap.items())]
            # Replace base lowercase a with donor's a; add an unencoded ornament at U+2605.
            assignments=[row for row in assignments if row[0]!=97]
            assignments.append([97,{"fontId":"f00002","glyphIndex":order_donor.index("a")}])
            assignments.append([9733,{"fontId":"f00002","glyphIndex":order_donor.index("swash")}])
            manifest={
                "version":1, "name":"Mobile Mixed",
                "baseId":"f00001",
                "preview":"Connect",
                "fonts":[
                    {"id":"f00001","filename":"a.ttf","file":"fonts/0001.ttf"},
                    {"id":"f00002","filename":"b.ttf","file":"fonts/0002.ttf"}
                ],
                "assignments":assignments,
                "variations":[
                    {"id":"v1","kind":"alternate","target":110,"sourceId":"f00002",
                     "glyphIndex":order_donor.index("n"),"feature":"calt","context":"repeat"},
                    {"id":"v2","kind":"alternate","target":110,"sourceId":"f00002",
                     "glyphIndex":order_donor.index("n"),"feature":"salt",
                     "context":"before","before":111}
                ]
            }
            bundle=folder/"project.glyphmix"
            with zipfile.ZipFile(bundle,"w") as archive:
                archive.writestr("project.json",json.dumps(manifest))
                archive.write(a,"fonts/0001.ttf")
                archive.write(b,"fonts/0002.ttf")
            outfile=folder/"result.ttf"
            report=compile_bundle(cli,bundle,outfile)
            self.assertEqual(report["mapped_characters"],6)
            self.assertIn("calt",report["features"])
            self.assertTrue(report["mobile_project"].endswith("project.glyphmix"))
            with TTFont(outfile) as font:
                self.assertEqual(font.getBestCmap()[9733],"u2605")
                self.assertIn("u006E.alt01",font.getGlyphOrder())
            raw=outfile.read_bytes()
            fontface=hb.Face(raw)
            font=hb.Font(fontface)
            def shape(text,features):
                buffer=hb.Buffer()
                buffer.add_str(text)
                buffer.guess_segment_properties()
                hb.shape(font,buffer,features)
                return [x.codepoint for x in buffer.glyph_infos]
            plain=shape("nn",{"calt":False})
            contextual=shape("nn",{"calt":True})
            self.assertEqual(len(plain),2)
            self.assertEqual(len(contextual),2)
            self.assertNotEqual(plain,contextual)
            donor.close();base.close()

    def test_reject_archive_path_traversal(self):
        with tempfile.TemporaryDirectory(dir=cli.ROOT/"GlyphMixer") as directory:
            folder=Path(directory)
            archive=folder/"evil.glyphmix"
            manifest={"version":1,"baseId":"f00001","fonts":[
                {"id":"f00001","file":"../secret.ttf"}],
                "assignments":[]}
            with zipfile.ZipFile(archive,"w") as z:
                z.writestr("project.json",json.dumps(manifest))
                z.writestr("../secret.ttf",b"unsafe")
            with self.assertRaises(cli.RecipeError):
                compile_bundle(cli,archive,folder/"test.ttf")

if __name__=="__main__":
    unittest.main()
