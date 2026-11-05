# PocketBoard: traced button symbols

This directory holds **18 separate white-on-transparent SVG symbols** traced from the PocketBoard reference images.

The 17 symbols on the reference sheet are:
- `connected-check`, `search`
- `clear`, `microphone`
- `volume-down`, `volume-up`, `mute`, `previous-track`, `pause`, `next-track`
- `apps-grid`, `overlapping-windows`, `windows-check`, `windows-plus`
- `escape`, `tab`, `enter`

The eighteenth, `play.svg`, comes from the separate large Play-button reference.

## Fidelity and extraction

These are source-image **tracings**, not replacements assembled from a stock icon set or typographic glyphs. Outlines were found at subpixel precision from the white/cream regions of the supplied raster images and simplified with a nominal maximum 0.45-pixel tolerance (0.6 pixel for large Play). Each symbol maintains its source-specific proportions, lumpy corners, line ends, offsets, and internal cutouts. Multiple disconnected marks remain in one SVG per symbol. Negative space is transparent, including the holes in Search, window overlays and the check/plus marks.

The only fidelity limit is the raster source itself: screenshot antialiasing and JPEG artifacts do not expose the original pre-raster Bézier control points. The paths follow the visible pixel boundaries without attempting to substitute idealized geometry.

Every asset has a tight `viewBox`, is filled white (`#ffffff`), and contains no button background, shadow, gradient, or label outside the symbol. These are the **canonical source assets deployed in PocketBoard 1.0.2**.
The matching native Android VectorDrawables are in
`../../android/app/src/main/res/drawable/pb_*.xml`. The conversion preserves
pathData and even-odd cutouts, while applying canonical cream at runtime.
Their original white SVG fills remain unchanged for provenance. Button
silhouettes are independently traced under `../button-silhouettes/`.
Copy/Select All & Copy/Paste use the overlapping-windows/check/plus glyphs;
Choose and Connected use the same traced check. Play and Pause are swapped
within one background on every press.

To recolour, change `fill="#ffffff"` to the desired solid colour or `currentColor`.

## Trackpad cursor

`cursor-pointer.svg` preserves two independently traced cream and dark-slate contours from the owner's generated marker pointer image. The deployed vector is `android/app/src/main/res/drawable/pb_cursor_pointer.xml`. The prior hand-coded cursor Path is retired.

## Refresh glyph (PocketBoard 1.0.7)

`refresh.svg` is a two-contour source-image trace from the owner-supplied transparent PNG. Each arrow was isolated using its actual alpha mask, spurious disconnected raster speckles were excluded, and each outline was traced to approximately 1.25 source pixels before a tightly cropped, transparent viewBox was applied. The original unequal arrow curves, rounded arrowheads and slightly hand-drawn irregularities are retained. The source paths are white; `pb_refresh.xml` in Android drawable resources uses the canonical cream foreground. The new action reuses `pb_shape_apps_grid` for its coloured background.
