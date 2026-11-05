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
5. In **Variations**, choose **+ Alternate** to select a source glyph (including unencoded glyphs by `#index`) and specify a target character, an OpenType feature (`aalt`, `salt`, `rand`, `ss01`, `ss02` or `calt`), and optional adjacent-repeat, preceding/following or two-sided context. **+ Ligature** supports `liga` and `dlig`. Tap existing rules to edit or remove them.
6. **Build font & preview on device** lazily loads the Python/WebAssembly compiler in a Worker, builds a real GSUB-equipped TTF, and displays before/after proof text with feature toggles. **Save compiled OpenType TTF** invokes Android's native file picker or downloads the file.
7. In **Preview**, test the outlines-only version of the font with customizable text.
8. **Save project** writes a self-contained .glyphmix ZIP via Chrome on Android's native Save As file picker. If unavailable, it uses a browser download. **Open** restores the embedded fonts and mapping decisions; no external font links are required.
9. **Export font** outputs a basic OTF when no variations are defined; when there are advanced rules it takes you to the GSUB-enabled TTF export to avoid silently dropping them.

## Headless and agent-driven OpenType assembly

A separate Python/fontTools engine in [headless/](headless/README.md) accepts versioned, declarative JSON recipes and generates downloadable OpenType TTF fonts containing **real GSUB alternate glyph rules**. Agents can take requests such as "Use A as the base, replace lowercase letters with B, add uppercase letters from C as contextual or selectable alternates, and name the result Z," translate them into [recipes](recipes/), then run the compiler through [GitHub Actions](../.github/workflows/glyph-mixer-headless.yml) or locally. The compiler supports Unicode reassignment, alternate feature tags (aalt, salt, rand, ss01, ss02), adjacent-repeat/neighbor-context calt, and optional liga/dlig. **The mobile Variations tab now authors these GSUB controls directly**, using the same recipe format and compiler as the headless workflow. Saved mobile `.glyphmix` projects can also be built headlessly with `--bundle`.

The 22 sample ZIPs are kept in [test-fonts/](test-fonts/) as fixtures; CI inventories all embedded fonts, round-trips actual donor glyphs from each archive, and verifies shaping with HarfBuzz. Generated fonts and reports are artifacts and are not committed to the repository.

## Scope and limitations, first release

- Imports .ttf, .otf, .woff, and ZIP archives of those formats. WOFF2, TTC, OTC, variable-font instancing, and color-glyph flattening are **not yet supported** for assembly. Unsupported formats must not be silently accepted or discarded.
- Supports up to 80 distinct sources, 30 MB per font and 160 MB per import/project for memory safety. Importing dozens of large fonts can still stress phone RAM.
- The basic exporter copies outlines and advances, scaling source units-per-em to the base font, producing an **outlines-only static OTF**. The Variations tab and headless compiler instead produce a **static TTF with actual GSUB features**.
- Neither exporter automatically preserves arbitrary pre-existing source GSUB/GPOS, complex-script shaping, native kerning pairs, hinting, color layers, or variable-font output tables. The advanced compiler explicitly creates supported GSUB alternates, contextual forms, and ligatures; source outlines can be selected by index even when unencoded. Base-character coverage here means mapped characters, **not** every behavior of the original font.
- Each Unicode position still has one default glyph, but the advanced compiler retains additional unencoded alternates under GSUB rules. Aalt/salt/rand/ss01/ss02 require application support. Calt adjacent-repeat and neighbor rules are deterministic and do not maintain document-wide history.
- The regular Preview tab reflects the basic OTF export. The Variations tab compiles an actual advanced TTF for its separate before/after OpenType proof; both previews update when rebuilt after mapping or rule edits.
- No backend, analytics, account, external uploads, or remote persistence. The first page load needs pinned CDN libraries and Google Ribeye; the first advanced compile additionally downloads a pinned Pyodide runtime and a pinned pure-Python fontTools wheel, then executes offline on the device. These dependencies can consume memory on constrained phones.
- Original font file licences and redistribution rights remain the user's responsibility when sharing exported hybrid fonts.

## Mobile UI reasoning

The app's main operation is selecting one destination and one source glyph. A narrow screen works best with **one grid at a time** rather than permanent side-by-side source/destination panels. Map, Variations, Sources and Preview are bottom navigation destinations with >=44 px targets. Destination selection opens a tall, scrollable bottom sheet containing source selection and a searchable source grid. The map begins with Common Latin (U+0020–U+024F); All/Outside Latin/Changes filters make larger character sets navigable without loading thousands of tiles at once. Glyphs are rendered as actual vector outlines on canvas, including glyphs mapped to other Unicode positions. Grid pages are capped at 180 for predictable phone performance.

See [Mobile UX research](docs/MOBILE-UX-RESEARCH.md) for source material and future experiments.

## Project file

A .glyphmix file is a ZIP containing project.json (format/version, family name, base id, source manifest, assignments, advanced variation rules, preview text) and the original source font bytes under fonts/*. It is deliberately self-contained and can be copied between devices. The project importer validates mapping references and restricts file counts and size. Future revisions should use explicit version migrations.

## Development

Open index.html from a static server (or GitHub Pages), then select local font files. No bundler is required.

Run tests:

    npm test --prefix GlyphMixer
    python -m unittest discover -s GlyphMixer/headless/tests -p 'test_*.py'

CI tests the mapping/recipe layer, saved mobile ZIP bundle round-trips, compiled GSUB with HarfBuzz, and all 22 ZIP fixtures. A separate targeted Chromium mobile workflow exercises the actual browser UI and on-device compiler. Physical Android Chrome native Save As, low-memory behavior, and accessibility remain release acceptance items.

## Near-term roadmap

1. Installed Android Chrome acceptance: multiple zipped fonts, 16+ sources, native Save As, restore from Downloads, and OTF installation.
2. Add font conversion for WOFF2 and collections, with clear face selection and resource limits.
3. Per-glyph alignment, scale, bearings, baseline and optical size controls.
4. Direct mapping by destination ranges, replace-all for sets, reusable recipes, batch undo/redo.
5. Extend GSUB editing to more contexts, alternate sequencing and explicit kerning/GPOS. Preserve selected inherited features where technically meaningful.
6. Optional Font Shelf interoperability (explicit import/export handoff only), while keeping independent routes and projects.
