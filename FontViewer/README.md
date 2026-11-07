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

## Default interface typeface

The general UI uses the bundled `P22 Stanyan Regular Regular.ttf`. The uppercase **FONT SHELF** title and uppercase **CHARACTER MAP** headings use the bundled `ScribbleBoxDemo-gyWq.ttf`. The title keeps a lighter “FONT” and heavier “SHELF” visual treatment, synthesized because Scribblebox provides one face. Imported font previews still display their respective font faces.

The GitHub Pages workflow publishes both TTF assets along with the HTML. **Pages assets are publicly retrievable even when their source repository is private.** Ensure the font license allows this use and public distribution.

## Android app

`android/` contains the dedicated Java WebView shell. It serves the existing browser UI from a secure app-assets HTTPS origin, preserving app-private IndexedDB without requesting Android-wide file access. The system document picker imports multiple TTF/OTF/WOFF/TTC/OTC/ZIP files. The debug APK build workflow is `.github/workflows/font-shelf-android.yml`; its `FontShelf-debug-apk` artifact is kept for seven days. Check the workflow run before calling a build qualified.

The app restores saved fonts on startup in small batches. Tags can apply to whole families or to individual faces, lists have user-set titles, and the shelf can be filtered by list or tag. Hidden fonts remain in Library; permanent deletion removes font bytes and updates saved list references. Only the user-authorized system picker reads external documents. This initial wrapper still needs internet connectivity for the existing pinned ZIP/parser dependencies during **new imports**, while restoration of previously imported fonts uses app-private local storage.

This is a first Android implementation, not yet a device-qualified release. Tests needed: clean installation, 100+ font import, kill/restart persistence, hidden-family recovery, list editing and deletion, storage-quota failure, upgrade survival, Android picker across providers, browser dependency outage and performance traces.

## Run

Open `index.html` in Chrome on Android, or serve the directory as a static site. No build step or backend is necessary. For convenient phone access, publish the directory using an appropriate static-site host. **This implementation uses two pinned CDN dependencies**, so a network connection is required to load those libraries: `fflate@0.8.2` for ZIP extraction and dynamically imported `fontkit@2.0.4` via esm.sh for font-name, Unicode-cmap, collection, and variation inspection. Font files are *not* transmitted to those services.

Imported font files, Unicode metadata, family tags and named lists are persisted in local IndexedDB. Hiding a family removes it from the visible shelf but retains its locally stored font bytes; Library can restore it without accessing the original document again. The separate **Delete** command permanently removes saved font files. The character map intentionally displays up to 420 glyphs from common Unicode blocks per font; it reports the full number of mapped characters.

## Safety limits and known constraints

To keep large archives manageable on a phone, the app applies limits of 30 MiB per extracted font, 180 MiB total compressed selection, and 250 processed font files. Large fonts and ZIP archives may still use significant memory during parsing and decompression.

This is an initial implementation. JavaScript syntax has been checked, but automated on-device import/render tests across WOFF, WOFF2, TTC, OTC, and variable fonts have not yet been completed. Runtime compatibility of the Fontkit ESM CDN build in Android Chrome still requires verification. ZIP archive processing is synchronous and may temporarily block rendering on particularly large archives.

## Source layout

- `index.html`: browser UI, styles and font rendering.
- `library.js`: IndexedDB metadata, saved font bytes and named-list storage.
- `android/`: small Android WebView shell and Gradle project.
- `tests/smoke.cjs`: source-level syntax and grouping/persistence checks.

## Suggested next steps

1. Vendor pinned JavaScript dependencies, validate the browser Fontkit bundle and eliminate import-time CDN reliance for truly offline Android use.
2. Add unit and browser tests covering multiple imports, ZIPs, duplicate handling, missing Unicode cmaps, and font-face cleanup.
3. Qualify Android IndexedDB persistence, font restoration and list/tag upgrades on a real device.
4. Improve huge character-map navigation with range filters and progressive rendering.

## Family grouping examples

Regression scenarios verified against the family-matching helper: Zounderkite's 3D, Semi-Italic and Super-Italic faces; Stoutface and SC Small Caps; KBYoureJustMyType and Thin; Gargle's differently encoded styles. Negative cases: Super Comic vs Super Hockey; Patrick Hand vs Unkempt, despite a shared ZIP; DKJalebi vs DKNewBeginnings. These are source-level checks, not full Android Chrome acceptance tests.
