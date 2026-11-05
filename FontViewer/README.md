# Font Shelf (FontViewer)

A small, phone-first browser application for inspecting local TrueType and OpenType fonts.

## Features

- Import multiple `.ttf`, `.otf`, or `.zip` files; import more without clearing the current shelf.
- ZIP import discovers TTF/OTF files in nested archive directories.
- Read the names embedded in font metadata, preview arbitrary text across every font, and inspect mapped Unicode characters.
- Remove individual imports or clear the complete shelf.
- Ascending/descending name sorting and a sticky mobile header with preview field and light/dark toggle.
- Processing occurs entirely in the browser, without a font upload API.

## Run

Open `index.html` in Chrome on Android, or serve the directory as a static site. No build step or backend is necessary. For convenient phone access, publish the directory using an appropriate static-site host. **This initial implementation uses two pinned CDN dependencies**, so a network connection is required to load those libraries: `fflate@0.8.2` for ZIP extraction and `opentype.js@1.3.4` for font-name and Unicode-cmap inspection. Font files are *not* transmitted to those services.

No imported font files are persisted between page reloads. Only the theme preference is saved to local storage. The character map intentionally displays up to 420 glyphs from common Unicode blocks per font; it reports the full number of mapped characters.

## Safety limits and known constraints

To keep large archives manageable on a phone, the app applies limits of 30 MiB per extracted font, 180 MiB total compressed selection, and 250 processed font files. Large fonts and ZIP archives may still use significant memory during parsing and decompression.

This is an initial implementation. Automated on-device testing, offline dependency vendoring, and broader typeface coverage tests have not yet been completed. ZIP archive processing is synchronous and may temporarily block rendering on particularly large archives.

## Source layout

- `index.html`: self-contained UI, CSS, and application code.

## Suggested next steps

1. Vendor pinned JavaScript dependencies and add an offline service worker.
2. Add unit and browser tests covering multiple imports, ZIPs, duplicate handling, missing Unicode cmaps, and font-face cleanup.
3. Optionally persist font collections with IndexedDB (opt-in only).
4. Improve huge character-map navigation with range filters and progressive rendering.
