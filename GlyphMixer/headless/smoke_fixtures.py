#!/usr/bin/env python3
"""Exercise every checked-in ZIP as a donor, exporting and parsing a complete font."""
import json
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

from GlyphMixer.headless.cli import ROOT, build, open_font, RecipeError


def main():
    archives = sorted((ROOT/"GlyphMixer/test-fonts").glob("*.zip"))
    base_path = "GlyphMixer/test-fonts/Unkempt.zip"
    baseline, _ = open_font({"path":base_path})
    base_cmap = baseline.getBestCmap() or {}
    used = set(base_cmap)
    destination = next(cp for cp in range(0xE000, 0xF900) if cp not in used)
    passes, failures = [], []
    for path in archives:
        alias_path = str(path.relative_to(ROOT))
        font = None
        try:
            font, member = open_font({"path":alias_path})
            cmap=font.getBestCmap() or {}
            if not cmap:
                raise RecipeError("Donor has no mapped characters.")
            cp = next((n for n in (65, 97, 110) if n in cmap),
                      next(iter(cmap)))
            name = path.stem.replace(" ","-")[:60]
            target = ROOT/"GlyphMixer/build/_smoke"/(name+".ttf")
            recipe = {
                "version":1,"name":"Smoke "+name,
                "base":"A",
                "sources":{"A":{"path":base_path},"B":{"path":alias_path}},
                "operations":[{"action":"reassign","source":"B","glyph":"U+%04X"%cp,
                               "destination":"U+%04X"%destination,"strict":True}]
            }
            report=build(recipe,target)
            with TTFont(target) as generated:
                if destination not in generated.getBestCmap():
                    raise AssertionError("Reassigned donor glyph absent in output.")
            passes.append({"archive":path.name,"member":member,
                           "source_cp":"U+%04X"%cp,
                           "mapped":report["mapped_characters"]})
            target.unlink(missing_ok=True)
            target.with_suffix(".report.json").unlink(missing_ok=True)
        except Exception as exc:
            failures.append({"archive":path.name,"error":str(exc)[:300]})
        finally:
            if font is not None:
                font.close()
    baseline.close()
    summary={"archive_count":len(archives),"passed":len(passes),
             "failed":len(failures),"results":passes,"failures":failures}
    report=ROOT/"GlyphMixer/build/fixture-assembly-smoke.json"
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps({"archive_count":len(archives),"passed":len(passes),
                      "failed":len(failures),"failures":failures},indent=2))
    if len(archives)!=22 or failures:
        return 1
    return 0


if __name__=="__main__":
    raise SystemExit(main())
