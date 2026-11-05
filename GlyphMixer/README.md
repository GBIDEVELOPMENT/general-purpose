# Glyph Mixer

An independent, mobile-first, local-only web app for constructing a hybrid font by starting from an existing base font and replacing selected Unicode mappings with glyphs from other fonts.

**Project home:** [GlyphMixer](./index.html)  
**Deployed Pages path:** /general-purpose/GlyphMixer/  
**Relationship to Font Shelf:** separate application, no cross-app links or dependency yet.

## First-use path

1. Select **Start with an existing font**, then choose a TTF/OTF/WOFF file (or ZIP archive containing fonts).
2. The first imported face becomes the base. Its Unicode character map is automatically filled; other imported faces become replacement sources.
3. In **Map**, tap a destination character. In the bottom sheet, choose a source font, locate a glyph, and tap it to assign it to that destination. Source and destination codepoints can differ.
4. Use **+ Position** to add arbitrary valid Unicode positions absent from the base. You can search by literal character, U+hex notation, or source glyph #index (including unmapped glyphs). **Use original**, **Remove position**, and **Undo** support revision.
5. In **Preview**, test with customizable text rendered through a generated font file.
6. **Save project** writes a self-contained .glyphmix ZIP via Chrome on Android's native Save As file picker. If unavailable, it uses a browser download. **Open** restores the embedded fonts and mapping decisions; no external font links are required.
7. **Export OTF** assembles mapped glyph outlines and emits a font file via the same native file-saving mechanism.

## Scope and limitations, first release

- Imports .ttf, .otf, .woff, and ZIP archives of those formats. WOFF2, TTC, OTC, variable-font instancing, and color-glyph flattening are **not yet supported** for assembly. Unsupported formats must not be silently accepted or discarded.
- Supports up to 80 distinct sources, 30 MB per font and 160 MB per import/project for memory safety. Importing dozens of large fonts can still stress phone RAM.
- The exporter copies outlines and advances, scaling source units-per-em to the base font. It produces a **static, outline-based OTF**.
- The exporter does **not** carry over full GSUB/GPOS, complex-script shaping, native kerning pairs, OpenType variation tables, contextual forms, hinting, color layers, or unencoded source glyphs unless explicitly selected by glyph index. Base-character coverage here means mapped characters, **not** every behavior of the original font.
- Unicode position mapping is one output glyph per codepoint. Two positions can reference the same source outline (stored twice in the output), but glyph-level OpenType substitutions and ligatures are future work.
- Preview uses a newly generated font to reflect actual export behavior; it is rebuilt when mappings or the family name change and the Preview tab is opened.
- No backend, analytics, account, external uploads, or remote persistence. The first page load needs a connection to the pinned CDN libraries and Google Ribeye face.
- Original font file licences and redistribution rights remain the user's responsibility when sharing exported hybrid fonts.

## Mobile UI reasoning

The app's main operation is selecting one destination and one source glyph. A narrow screen works best with **one grid at a time** rather than permanent side-by-side source/destination panels. Map, Sources and Preview are bottom navigation destinations with >=44 px targets. Destination selection opens a tall, scrollable bottom sheet containing source selection and a searchable source grid. The map begins with Common Latin (U+0020–U+024F); All/Outside Latin/Changes filters make larger character sets navigable without loading thousands of tiles at once. Glyphs are rendered as actual vector outlines on canvas, including glyphs mapped to other Unicode positions. Grid pages are capped at 180 for predictable phone performance.

See [Mobile UX research](docs/MOBILE-UX-RESEARCH.md) for source material and future experiments.

## Project file

A .glyphmix file is a ZIP containing project.json (format/version, family name, base id, source manifest, assignments, preview text) and the original source font bytes under fonts/*. It is deliberately self-contained and can be copied between devices. The project importer validates mapping references and restricts file counts and size. Future revisions should use explicit version migrations.

## Development

Open index.html from a static server (or GitHub Pages), then select local font files. No bundler is required.

Run tests:

    node --test GlyphMixer/tests/*.test.cjs

The tests exercise the pure mapping and export transformation layer. End-to-end Android Chrome file-picker, ZIP round-trip, OTF validation against a third-party font validator, and visual/keyboard accessibility should be added before labelling the app production hardened.

## Near-term roadmap

1. Installed Android Chrome acceptance: multiple zipped fonts, 16+ sources, native Save As, restore from Downloads, and OTF installation.
2. Add font conversion for WOFF2 and collections, with clear face selection and resource limits.
3. Per-glyph alignment, scale, bearings, baseline and optical size controls.
4. Direct mapping by destination ranges, replace-all for sets, reusable recipes, batch undo/redo.
5. Inspect and preserve selected kerning, ligatures and shaping features where technically meaningful. Add export validation.
6. Optional Font Shelf interoperability (explicit import/export handoff only), while keeping independent routes and projects.
