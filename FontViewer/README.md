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

The app restores saved fonts on startup in small batches. Tags can apply to whole families or to individual faces, lists have user-set titles, and the shelf can be filtered by list or tag. Hidden fonts remain in Library; permanent deletion removes font bytes and updates saved list references. Only the user-authorized system picker reads external documents. The installed Android APK bundles the version-pinned ZIP reader and font parser locally. Imports and restoration no longer require reaching a CDN. The Google-hosted Pages version publishes those same self-contained JavaScript assets.

A debug APK was built and asset-verified in CI [run #28](https://github.com/GBIDEVELOPMENT/general-purpose/actions/runs/42346040564), with four executable IndexedDB lifecycle tests passing. The separate Android 15 / API 35 [installed emulator run](https://github.com/GBIDEVELOPMENT/general-purpose/actions/runs/42346736856) **also passed its one full WebView lifecycle test**: offline parser and ZIP roundtrip, font save, hide, Activity recreation, restore, face/family tags, named list, second Activity recreation. These checks establish a working installed Android path, not physical-device or broad-format qualification. Remaining acceptance includes system picker providers, 100+ font ZIP imports, quota failure, verified signing-preserving app upgrades, and performance traces. Read [Android signing and upgrade safety](android/SIGNING.md) before daily use: initial CI preview APKs use transient debug signing unless the stable debug keystore secret is configured.

## Run

For local web development, run `npm install` and `npm run build:vendor` inside `FontViewer/`, then serve that directory over HTTP(S). The build creates `.generated/vendor/fontkit.js` and `fflate.js`; copy these into `vendor/` beside `index.html` when hosting the web variant outside the provided GitHub Pages workflow. For Android, `FontViewer/android/` is a Gradle 8.11.1 / Android Gradle Plugin 8.9.2 project and the debug workflow stages vendor assets into the APK automatically. Neither version sends imported font files to a remote server. The web version uses the local origin's IndexedDB, separate from Android's app-private origin; there is no implicit cross-origin migration.

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

1. Qualify offline imports in installed Android WebView, including ZIPs and fontkit parsing across formats.
2. Add unit and browser tests covering multiple imports, ZIPs, duplicate handling, missing Unicode cmaps, and font-face cleanup.
3. Qualify Android IndexedDB persistence, font restoration and list/tag upgrades on an emulator and physical device.
4. Improve huge character-map navigation with range filters and progressive rendering.

## Family grouping examples

Regression scenarios verified against the family-matching helper: Zounderkite's 3D, Semi-Italic and Super-Italic faces; Stoutface and SC Small Caps; KBYoureJustMyType and Thin; Gargle's differently encoded styles. Negative cases: Super Comic vs Super Hockey; Patrick Hand vs Unkempt, despite a shared ZIP; DKJalebi vs DKNewBeginnings. These are source-level checks, not full Android Chrome acceptance tests.
