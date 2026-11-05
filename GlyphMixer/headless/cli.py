#!/usr/bin/env python3
"""Headless Glyph Mixer: deterministic font assembly and OpenType GSUB recipes.

Run: python GlyphMixer/headless/cli.py build --recipe GlyphMixer/recipes/example.json
Source file paths are relative to the repository root. No external uploads.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import zipfile
from collections import OrderedDict
from pathlib import Path

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, TTCollection

ROOT = Path(__file__).resolve().parents[2]
EXTENSIONS = {".ttf", ".otf", ".woff", ".woff2", ".ttc", ".otc"}
MAX_ARCHIVE = 160 * 1024 * 1024
MAX_MEMBER = 30 * 1024 * 1024
MAX_FILES = 300
MAX_GLYPHS = 35000
VALID_SOURCE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]{0,35}$")


class RecipeError(ValueError):
    pass


def root_path(relative: str, *, must_exist: bool = False) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise RecipeError("Paths must be nonempty and repository-relative.")
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise RecipeError("Refusing path outside repository: " + relative)
    if must_exist and not path.is_file():
        raise RecipeError("File not found: " + relative)
    return path


def read_font_data(spec: dict) -> tuple[bytes, str]:
    path = root_path(spec["path"], must_exist=True)
    if path.stat().st_size > MAX_ARCHIVE:
        raise RecipeError("Font input exceeds 160 MB: " + str(path))
    if path.suffix.lower() != ".zip":
        if path.suffix.lower() not in EXTENSIONS:
            raise RecipeError("Unsupported font format: " + str(path))
        return path.read_bytes(), path.name
    with zipfile.ZipFile(path) as zf:
        names = [
            z for z in zf.infolist()
            if not z.is_dir() and Path(z.filename).suffix.lower() in EXTENSIONS
        ]
        if len(zf.infolist()) > MAX_FILES or sum(z.file_size for z in zf.infolist()) > MAX_ARCHIVE:
            raise RecipeError("Archive violates size or entry limits: " + str(path))
        names = [z for z in names if z.file_size <= MAX_MEMBER]
        member = spec.get("member")
        if member:
            matches = [z for z in names if z.filename == member]
            if not matches:
                raise RecipeError("Requested ZIP member is absent: " + str(member))
            chosen = matches[0]
        else:
            if not names:
                raise RecipeError("Archive has no usable fonts: " + str(path))
            priority = {".ttf": 0, ".otf": 1, ".woff2": 2, ".woff": 3, ".ttc": 4, ".otc": 5}
            chosen = min(names, key=lambda z: (priority.get(Path(z.filename).suffix.lower(), 99), z.filename.lower()))
        if chosen.file_size > MAX_MEMBER:
            raise RecipeError("Font exceeds 30 MB.")
        data = zf.read(chosen)
        if len(data) != chosen.file_size:
            raise RecipeError("Incomplete ZIP entry.")
        return data, chosen.filename


def open_font(spec: dict):
    data, member = read_font_data(spec)
    face = spec.get("face", 0)
    if not isinstance(face, int) or face < 0:
        raise RecipeError("Face index must be a nonnegative integer.")
    if member.lower().endswith((".ttc", ".otc")):
        collection = TTCollection(io.BytesIO(data))
        if face >= len(collection.fonts):
            raise RecipeError("Font collection face index out of range.")
        font = collection.fonts[face]
    else:
        if face:
            raise RecipeError("Face index may only be set for TTC/OTC.")
        font = TTFont(io.BytesIO(data), lazy=False, recalcBBoxes=False)
    font.flavor = None
    if "cmap" not in font or "hmtx" not in font or not any(t in font for t in ("glyf", "CFF ", "CFF2")):
        raise RecipeError("Font lacks required mappings, metrics, or outlines: " + member)
    axes = spec.get("axes", {})
    if not isinstance(axes, dict) or any(not isinstance(v, (int, float)) for v in axes.values()):
        raise RecipeError("axes must be a map of axis tags to numeric values.")
    if axes and "fvar" not in font:
        raise RecipeError("Variation axes requested on a non-variable font.")
    if axes:
        from fontTools.varLib.instancer import instantiateVariableFont
        font = instantiateVariableFont(font, axes, inplace=False)
    return font, member


def codepoints(selector, base_cmap: dict[int, str]) -> list[int]:
    if isinstance(selector, list):
        if not all(isinstance(x, (str, int)) for x in selector):
            raise RecipeError("Invalid list of characters.")
        return sorted(set(codepoint(x) for x in selector))
    if not isinstance(selector, str):
        raise RecipeError("target must be a character set name, text, or list.")
    presets = {
        "lowercase": range(0x61, 0x7B),
        "uppercase": range(0x41, 0x5B),
        "digits": range(0x30, 0x3A),
        "basic-latin": range(0x20, 0x7F),
        "latin-1": range(0x20, 0x100),
        "all": base_cmap.keys(),
    }
    if selector in presets:
        return list(presets[selector])
    if selector.startswith("chars:"):
        return sorted(set(map(ord, selector[6:])))
    if selector.startswith("U+") or selector.startswith("0x"):
        return [codepoint(selector)]
    raise RecipeError("Unknown target: " + selector)


def codepoint(value) -> int:
    if isinstance(value, int):
        cp = value
    elif isinstance(value, str) and value.startswith("U+"):
        cp = int(value[2:], 16)
    elif isinstance(value, str) and value.startswith("0x"):
        cp = int(value[2:], 16)
    elif isinstance(value, str) and len(value) == 1:
        cp = ord(value)
    else:
        raise RecipeError("Use a character, U+hex, or integer codepoint: " + str(value))
    if not (0 < cp <= 0x10FFFF) or 0xD800 <= cp <= 0xDFFF:
        raise RecipeError("Invalid Unicode scalar value.")
    return cp


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", name)[:110]


def glyph_name(cp: int) -> str:
    return "u" + format(cp, "04X")


def build(recipe: dict, output: Path | None = None) -> dict:
    if not isinstance(recipe, dict) or recipe.get("version") != 1:
        raise RecipeError("Recipe version must be 1.")
    specs = recipe.get("sources")
    if not isinstance(specs, dict) or not 1 <= len(specs) <= 80 or any(not VALID_SOURCE.fullmatch(k) for k in specs):
        raise RecipeError("sources must contain between 1 and 80 named fonts.")
    base_id = recipe.get("base")
    if base_id not in specs:
        raise RecipeError("base must name one of the sources.")
    sources, members, cmaps = {}, {}, {}
    for alias, spec in specs.items():
        if not isinstance(spec, dict) or "path" not in spec:
            raise RecipeError("Source entries require a path.")
        font, member = open_font(spec)
        sources[alias] = font
        members[alias] = member
        cmaps[alias] = font.getBestCmap() or {}
    base = sources[base_id]
    upm = base["head"].unitsPerEm
    requested = OrderedDict((cp, (base_id, name)) for cp, name in sorted(cmaps[base_id].items())
                            if 0 < cp <= 0x10FFFF and not 0xD800 <= cp <= 0xDFFF)
    alternates: dict[int, list[tuple[str, str]]] = {}
    feature_sets: dict[int, set[str]] = {}
    context_repeat: set[int] = set()
    contextual_rules: list[tuple[int, tuple[str,str], int|None, int|None]] = []
    ligatures: list[tuple[tuple[int, ...], tuple[str, str], str]] = []
    warnings = []
    stats = []
    operations = recipe.get("operations", [])
    if not isinstance(operations, list) or len(operations) > 300:
        raise RecipeError("operations must be a list of at most 300 steps.")
    for index, op in enumerate(operations):
        if not isinstance(op, dict):
            raise RecipeError("Each operation must be an object.")
        action = op.get("action")
        donor = op.get("source")
        if donor not in sources:
            raise RecipeError("Unknown source for step " + str(index + 1))
        if action == "ligature":
            seq = tuple(ord(c) for c in op.get("sequence", ""))
            if not 2 <= len(seq) <= 8:
                raise RecipeError("Ligature sequence must be 2-8 characters.")
            source_cp = codepoint(op.get("glyph", op.get("sequence", "")[0]))
            name = cmaps[donor].get(source_cp)
            if name is None:
                raise RecipeError("Ligature source glyph is missing.")
            ligatures.append((seq, (donor, name), op.get("feature", "liga")))
            continue
        if action not in ("replace", "alternate", "reassign"):
            raise RecipeError("Unknown operation " + str(action))
        if action == "reassign":
            cps = [codepoint(op["destination"])]
            donor_cps = [codepoint(op["glyph"])]
        else:
            cps = codepoints(op.get("target"), cmaps[base_id])
            donor_cps = cps
        features = op.get("features", ["aalt", "salt"])
        if action == "alternate" and (not isinstance(features, list) or
            any(f not in ("aalt", "salt", "rand", "ss01", "ss02", "calt") for f in features)):
            raise RecipeError("Unsupported alternate feature. Use aalt, salt, rand, ss01, ss02, calt.")
        copied, missed = 0, []
        for cp, donor_cp in zip(cps, donor_cps):
            source_name = cmaps[donor].get(donor_cp)
            if source_name is None:
                missed.append("U+" + format(cp, "04X"))
                continue
            if action in ("replace", "reassign"):
                requested[cp] = (donor, source_name)
            else:
                if cp not in requested:
                    missed.append("U+" + format(cp, "04X"))
                    continue
                reference = (donor, source_name)
                if reference != requested[cp]:
                    if reference not in alternates.setdefault(cp, []):
                        alternates[cp].append(reference)
                    feature_sets.setdefault(cp, set()).update(features)
                    context = op.get("context")
                    if isinstance(context, dict):
                        before = codepoint(context["preceded_by"]) if "preceded_by" in context else None
                        after = codepoint(context["followed_by"]) if "followed_by" in context else None
                        if before is None and after is None:
                            raise RecipeError("Context object requires preceded_by and/or followed_by.")
                        contextual_rules.append((cp, reference, before, after))
                    elif context == "adjacent-repeat" or ("calt" in features and context is None):
                        context_repeat.add(cp)
                    elif context is not None:
                        raise RecipeError("Unknown context rule: " + str(context))
            copied += 1
        if missed and op.get("strict"):
            raise RecipeError("Missing glyphs in step " + str(index+1) + ": " + ", ".join(missed[:20]))
        if missed:
            warnings.append(f"step {index+1}: {len(missed)} missing target/source glyphs; e.g. {', '.join(missed[:8])}")
        stats.append({"step": index+1, "action": action, "source": donor, "assigned": copied, "missing": len(missed)})
    if len(requested) + sum(map(len, alternates.values())) + len(ligatures) > MAX_GLYPHS:
        raise RecipeError("Recipe would exceed the 35,000-glyph limit.")

    glyph_order = [".notdef"]
    refs: dict[str, tuple[str, str]] = {}
    glyph_map: dict[int, str] = {}
    alternate_names: dict[int, list[str]] = {}
    def register(name: str, reference: tuple[str, str]):
        if name in refs:
            raise RecipeError("Internal duplicate output glyph name: " + name)
        glyph_order.append(name)
        refs[name] = reference

    # Base .notdef is retained at glyph zero; other source glyphs use unique names.
    refs[".notdef"] = (base_id, base.getGlyphOrder()[0])
    for cp, reference in sorted(requested.items()):
        name = glyph_name(cp)
        glyph_map[cp] = name
        register(name, reference)
    for cp, refs_for_cp in sorted(alternates.items()):
        if cp not in glyph_map:
            continue
        alternate_names[cp] = []
        for num, reference in enumerate(refs_for_cp, 1):
            name = glyph_name(cp) + ".alt" + str(num).zfill(2)
            register(name, reference)
            alternate_names[cp].append(name)
    ligature_subs = []
    for i, (seq, reference, feature) in enumerate(ligatures):
        if feature not in ("liga", "dlig"):
            raise RecipeError("Ligature feature must be liga or dlig.")
        if any(cp not in glyph_map for cp in seq):
            warnings.append("Ligature skipped: input sequence missing in output cmap.")
            continue
        name = "lig_" + str(i+1).zfill(4)
        register(name, reference)
        ligature_subs.append((seq, name, feature))

    glyfs, metrics = {}, {}
    pen_cache: dict[tuple[str, str], tuple[object, tuple[int, int]]] = {}
    for out_name in glyph_order:
        alias, source_name = refs[out_name]
        key = (alias, source_name)
        if key not in pen_cache:
            source_font = sources[alias]
            scale = upm / source_font["head"].unitsPerEm
            glyphset = source_font.getGlyphSet()
            if source_name not in glyphset:
                raise RecipeError("Source glyph is missing: " + alias + "/" + source_name)
            draw = DecomposingRecordingPen(glyphset)
            glyphset[source_name].draw(draw)
            target = TTGlyphPen(None)
            scaled = TransformPen(Cu2QuPen(target, max_err=1.0), (scale, 0, 0, scale, 0, 0))
            draw.replay(scaled)
            outline = target.glyph()
            advance, bearing = source_font["hmtx"].metrics[source_name]
            pen_cache[key] = (outline, (max(0, round(advance*scale)), round(bearing*scale)))
        glyfs[out_name], metrics[out_name] = pen_cache[key]

    builder = FontBuilder(upm, isTTF=True)
    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(glyph_map)
    builder.setupGlyf(glyfs)
    builder.setupHorizontalMetrics(metrics)
    asc = max(0, round(base["hhea"].ascent))
    desc = min(0, round(base["hhea"].descent))
    builder.setupHorizontalHeader(ascent=asc, descent=desc)
    family = str(recipe.get("name") or "Glyph Mixer Hybrid").strip()[:100] or "Glyph Mixer Hybrid"
    builder.setupNameTable({
        "familyName": family, "styleName": "Regular",
        "uniqueFontIdentifier": "GlyphMixer:" + family,
        "fullName": family + " Regular",
        "psName": safe_name(family.replace(" ", "")) + "-Regular",
        "version": "Version 1.000",
    })
    builder.setupOS2(
        sTypoAscender=asc, sTypoDescender=desc, usWinAscent=max(0, asc),
        usWinDescent=max(0, -desc), sTypoLineGap=0
    )
    builder.setupPost()
    builder.setupMaxp()
    builder.setupHead(unitsPerEm=upm)
    output_font = builder.font

    # Real GSUB features: alternate glyphs have no Unicode; text stays unchanged.
    features: dict[str, list[str]] = {k: [] for k in ("aalt", "salt", "rand", "ss01", "ss02", "calt", "liga", "dlig")}
    for cp, names in sorted(alternate_names.items()):
        original = glyph_map[cp]
        class_names = "[" + " ".join(names) + "]"
        flags = feature_sets.get(cp, set())
        for feature in ("aalt", "salt", "rand"):
            if feature in flags:
                features[feature].append(f"sub {original} from {class_names};")
        for feature, offset in (("ss01",0), ("ss02",1)):
            if feature in flags and len(names) > offset:
                features[feature].append(f"sub {original} by {names[offset]};")
        if cp in context_repeat:
            # First repeated character remains default, the next is replaced.
            # A later repeat can follow a different output glyph, deterministically.
            cycle = [original] + names
            for left, right in zip(cycle, cycle[1:] + cycle[:1]):
                features["calt"].append(f"sub {left} {original}' by {right};")
    for cp, reference, before, after in contextual_rules:
        if (before is not None and before not in glyph_map) or (after is not None and after not in glyph_map):
            warnings.append("Context skipped: surrounding glyph is not mapped for U+%04X" % cp)
            continue
        if reference not in alternates.get(cp, []):
            continue
        name = alternate_names[cp][alternates[cp].index(reference)]
        parts = ([glyph_map[before]] if before is not None else []) + [glyph_map[cp] + "'"] + ([glyph_map[after]] if after is not None else [])
        features["calt"].append("sub " + " ".join(parts) + " by " + name + ";")
    for seq, lig_name, feature in ligature_subs:
        features[feature].append("sub " + " ".join(glyph_map[cp] for cp in seq) + " by " + lig_name + ";")
    fea_parts = [f"feature {name} {{\n  " + "\n  ".join(rules) + f"\n}} {name};"
                 for name, rules in features.items() if rules]
    if fea_parts:
        addOpenTypeFeaturesFromString(output_font, "\n\n".join(fea_parts))
    if output is None:
        output = root_path(recipe.get("output") or ("GlyphMixer/build/" + safe_name(family) + ".ttf"))
    if output.suffix.lower() != ".ttf":
        raise RecipeError("Headless output currently supports .ttf OpenType fonts only.")
    output.parent.mkdir(parents=True, exist_ok=True)
    output_font.save(output)
    # Verify that the actual written file remains parseable and that all cmap entries survive.
    roundtrip = TTFont(output)
    built_cmap = roundtrip.getBestCmap() or {}
    if set(built_cmap) != set(glyph_map):
        output.unlink(missing_ok=True)
        raise RecipeError("Round-trip validation failed: character maps differ.")
    if fea_parts and "GSUB" not in roundtrip:
        output.unlink(missing_ok=True)
        raise RecipeError("Round-trip validation failed: GSUB features absent.")
    report = {
        "output": str(output.relative_to(ROOT)),
        "family": family,
        "glyphs": len(glyph_order),
        "mapped_characters": len(glyph_map),
        "alternate_characters": len(alternate_names),
        "ligatures": len(ligature_subs),
        "features": [k for k, rules in features.items() if rules],
        "sources": {key: {"path": specs[key]["path"], "member": members[key],
                          "mapped": len(cmaps[key])} for key in sources},
        "steps": stats,
        "warnings": warnings,
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    roundtrip.close()
    for source in sources.values():
        source.close()
    return report


def inventory(directory: str) -> dict:
    path = root_path(directory)
    result = []
    for item in sorted(path.glob("*.zip")):
        entry = {"archive": str(item.relative_to(ROOT)), "members": []}
        with zipfile.ZipFile(item) as zf:
            for member in zf.infolist():
                if member.is_dir() or Path(member.filename).suffix.lower() not in EXTENSIONS:
                    continue
                details = {"member": member.filename, "bytes": member.file_size}
                try:
                    if member.file_size > MAX_MEMBER:
                        raise RecipeError("Font exceeds 30 MB limit")
                    font, selected = open_font({"path": str(item.relative_to(ROOT)),
                                                "member": member.filename})
                    details["family"] = font["name"].getDebugName(1)
                    details["glyphs"] = len(font.getGlyphOrder())
                    details["mapped"] = len(font.getBestCmap() or {})
                    font.close()
                except Exception as exc:
                    details["error"] = str(exc)[:250]
                entry["members"].append(details)
        result.append(entry)
    return {"archives": len(result), "items": result}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("build", help="Build a hybrid font from a JSON recipe.")
    run.add_argument("--recipe", required=True, help="Repository-relative JSON recipe path")
    run.add_argument("--output", help="Override output with repository-relative .ttf filename")
    inv = sub.add_parser("inventory", help="List fonts inside the checked-in ZIP fixtures.")
    inv.add_argument("--directory", default="GlyphMixer/test-fonts")
    inv.add_argument("--output", help="Write machine-readable JSON report to this path")
    args = parser.parse_args(argv)
    try:
        if args.command == "inventory":
            report = inventory(args.directory)
        else:
            recipe = json.loads(root_path(args.recipe, must_exist=True).read_text())
            report = build(recipe, root_path(args.output) if args.output else None)
        payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.command == "inventory" and args.output:
            destination = root_path(args.output)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(payload)
        print(payload)
        return 0
    except (RecipeError, OSError, ValueError, KeyError, AssertionError) as exc:
        print("Glyph Mixer error: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
