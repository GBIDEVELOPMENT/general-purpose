# Mobile glyph-assembly interaction research (2026-11-05)

## Task model

Most sessions begin with a fairly complete base font and involve **sparse substitutions**, rather than assembling a font from an empty canvas. The interface must make three things obvious: the destination Unicode position, the actual source glyph independent of that position, and whether the destination still comes from the base.

## Prior art and observations

- [FontForge UI introduction](https://designwithfontforge.com/en-US/General_UI_Introduction.html) describes separate Font View grid, Character View, Metrics View and Font Info window. Glyph Mixer adopts the **conceptual separation** but turns it into a single narrow-screen experience rather than expecting multiple desktop windows.
- [FontReForge Android](https://github.com/fontforge/fontforge/discussions/5848), July 2026, describes a 4-column glyph grid, cached thumbnails, multi-selection, searchable glyph browser, and fast-scroll for very large collections. This supports a paginated touch-friendly grid rather than a text-only character list; 5 columns at a 412 px CSS viewport is an initial hypothesis to verify on actual hardware.
- [opentype.js](https://github.com/opentypejs/opentype.js) exposes glyph outlines and writing of OpenType fonts. Glyph-aware canvas rendering is essential for glyph reassignment: showing the destination character in the **source font** would display the wrong outline.
- [Web Features Explorer: File System Access](https://web-platform-dx.github.io/web-features-explorer/features/file-system-access/) records showSaveFilePicker on Android Chrome 132+ with non-Chromium gaps. Use the native save picker from a direct click and retain downloads as fallback.

## Screen architecture

- **New project screen:** one big base-font import action and a secondary open-project action. Do not start with an empty glyph editor.
- **Persistent project header:** family name, Save project, Open, Export OTF; compact and outside scrolling glyph content.
- **Map tab (default):** destination character grid, Common Latin/All/Changes/Outside Latin filters and search. Highlight replaced positions.
- **Selection sheet:** scrollable 80%-height bottom sheet with source picker, glyph search (literal, Unicode or #glyph index), source glyph tiles, revert and removal. Tap a glyph assigns it without leaving the sheet, supporting quick experimentation.
- **Sources tab:** source list, base status, counts, and add/removal actions.
- **Preview tab:** editable proof text, size control, live generated font, refresh action.
- **Bottom nav:** Map/Sources/Preview with 55 px minimum hit zones, stable on short and tall devices.

## Constraints and follow-up testing

- 412×892 and 320×700 CSS pixel screens, safe-area inset, on-screen keyboard, and no horizontal overflow.
- Screen-reader labels on controls and per-glyph buttons; color never serves as the sole changed-state indicator (a star marking too). Native focus return when the sheet closes should be implemented after TalkBack testing.
- More than 5,000 mapped positions: window/virtualize grid and add jump-to-range rather than forcing massive DOM or full re-render. The current 180-tile batching is a first release compromise.
- Tab change must preserve map filter, search and approximate scroll position.
- Confirm the Save As picker actually gives a writable .glyphmix file on the target Android Chrome build; test recovery from cancelled picker and reimport from Files.
- Beware that a mobile screen's keyboard covers a bottom sheet. Measure picker scroll/height with Chrome dynamic viewport and reduced-motion settings.
- Compare 4, 5 and 6 columns on the actual handset. Favor legible glyph shapes and codepoint labels over density.
- A major next-level tool would be a **before/after** details sheet showing base, candidate and composed result at matched optical sizes.

## Proposed device acceptance checks

1. Base TTF with >1,000 glyphs. Inspect original U+0041 and changed assignment from another OTF; export and reopen generated OTF.
2. Assign source glyph U+2605 to destination U+0041 and also to U+2603, then verify both mappings independently.
3. Source glyph by #index without existing Unicode mapping; export at a newly added position.
4. Save .glyphmix with 3+ sources; close page, import project via Android Files, compare mapping count and glyph previews.
5. Negative ZIP: oversized entry, malformed font, missing manifest, wrong referenced glyph.
6. Import 16 mixed fonts, filter and search large maps, scroll sheet with keyboard visible.
7. Light/dark theme, touch controls, reduced motion, screen reader labels, landscape and accessibility font scaling.

## Deferred choices

Potential additions include an alphabet keyboard for destination selection, swipe-to-compare alternatives, drag-and-drop from sources, range replacement, variable-font instancing, embedded image/color font support, and import integration with Font Shelf. None is a prerequisite for the current project's independent identity.
