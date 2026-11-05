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

Every asset has a tight `viewBox`, is filled white (`#ffffff`), and contains no button background, shadow, gradient, or label outside the symbol. These are **reference assets**, not a change to PocketBoard's current application UI. Existing button silhouettes in `../button-silhouettes/` are separate and untouched.

To recolour, change `fill="#ffffff"` to the desired solid colour or `currentColor`.
