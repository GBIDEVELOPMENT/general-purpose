# Font Shelf (FontViewer)

A small, phone-first browser application for inspecting local TrueType and OpenType fonts.

## Features

- Import multiple `.ttf`, `.otf`, `.woff`, `.woff2`, `.ttc`, `.otc`, or `.zip` files; import more without clearing the current shelf.
- ZIP import discovers TTF/OTF/WOFF/WOFF2/TTC/OTC files in nested archive directories. Collections unpack individual faces for display. Duplicate faces across formats are consolidated by embedded PostScript/family/style metadata, preferring OTF, TTF, WOFF2, WOFF, OTC, TTC in that order.
- Read the names embedded in font metadata, preview arbitrary text across every font, and inspect mapped Unicode characters.
- Variable-font previews and glyphs expose sliders for each declared variation axis.
- Group fonts using normalized style-free name stems and supporting ZIP-package evidence. This combines families such as Zounderkite (3D, Bevel, Chrome, etc.), Gargle's style variations, Stoutface / Stoutface SC Small Caps, and KBYoureJustMyType / Thin, while avoiding naive first-two-word collisions (for example, Super Comic vs Super Hockey) and unrelated faces that happen to share one ZIP (Patrick Hand / Unkempt). One card per family, with previous/next arrows alongside the remove button when multiple faces are available. Navigation buttons display the imported face's literal `<` and `>` glyphs; dismissal displays its literal `x` glyph. The dismiss button removes the entire family and all of its variants. The displayed count counts rendered family cards, not individual face files.
- Variant changes update only the selected card, and expanded character maps populate on scroll in small animation-frame batches to reduce UI lag. Character maps start collapsed, can be expanded independently per family, and retain their expand/collapse state while switching variants.
- Dismiss an entire font family or clear all families at once.
- Ascending/descending name sorting and a sticky mobile header with preview field and light/dark toggle.
- Processing occurs entirely in the browser, without a font upload API.

## Run

Open `index.html` in Chrome on Android, or serve the directory as a static site. No build step or backend is necessary. For convenient phone access, publish the directory using an appropriate static-site host. **This implementation uses two pinned CDN dependencies**, so a network connection is required to load those libraries: `fflate@0.8.2` for ZIP extraction and dynamically imported `fontkit@2.0.4` via esm.sh for font-name, Unicode-cmap, collection, and variation inspection. Font files are *not* transmitted to those services.

No imported font files are persisted between page reloads. Only the theme preference is saved to local storage. The character map intentionally displays up to 420 glyphs from common Unicode blocks per font; it reports the full number of mapped characters.

## Safety limits and known constraints

To keep large archives manageable on a phone, the app applies limits of 30 MiB per extracted font, 180 MiB total compressed selection, and 250 processed font files. Large fonts and ZIP archives may still use significant memory during parsing and decompression.

This is an initial implementation. JavaScript syntax has been checked, but automated on-device import/render tests across WOFF, WOFF2, TTC, OTC, and variable fonts have not yet been completed. Runtime compatibility of the Fontkit ESM CDN build in Android Chrome still requires verification. ZIP archive processing is synchronous and may temporarily block rendering on particularly large archives.

## Source layout

- `index.html`: self-contained UI, CSS, and application code.

## Suggested next steps

1. Vendor pinned JavaScript dependencies, validate the browser Fontkit bundle, and add an offline service worker.
2. Add unit and browser tests covering multiple imports, ZIPs, duplicate handling, missing Unicode cmaps, and font-face cleanup.
3. Optionally persist font collections with IndexedDB (opt-in only).
4. Improve huge character-map navigation with range filters and progressive rendering.

## Family grouping examples

Regression scenarios verified against the family-matching helper: Zounderkite's 3D, Semi-Italic and Super-Italic faces; Stoutface and SC Small Caps; KBYoureJustMyType and Thin; Gargle's differently encoded styles. Negative cases: Super Comic vs Super Hockey; Patrick Hand vs Unkempt, despite a shared ZIP; DKJalebi vs DKNewBeginnings. These are source-level checks, not full Android Chrome acceptance tests.
