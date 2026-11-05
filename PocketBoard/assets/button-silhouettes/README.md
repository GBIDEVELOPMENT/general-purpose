# PocketBoard button silhouette archive

This directory preserves **17 individually traced button-background silhouettes** from the supplied PocketBoard button-reference composite located at the root of the PocketBoard project. The shapes are not standardized: variations in corner curvature, side bulge, aspect ratio, and visual balance are intentional.

All SVGs have a tight, native-pixel `viewBox`, one closed fill-only path, and `fill="currentColor"`. Set CSS `color` or the SVG's fill to recolor the shape. No button glyphs, shadows, gradients or lettering are embedded.

## Shapes

| Section | Filenames |
| --- | --- |
| Connection/search | `connected-pill.svg`, `search.svg` |
| Text entry | `clear.svg`, `microphone.svg` |
| Media | `volume-down.svg`, `volume-up.svg`, `mute.svg`, `previous-track.svg`, `pause.svg`, `next-track.svg` |
| Utility | `apps-grid.svg`, `overlapping-windows.svg`, `windows-check.svg`, `windows-plus.svg` |
| Navigation | `escape.svg`, `tab.svg`, `enter.svg` |

## Method and limitations

Shapes are contour traces of the colored backgrounds in the reference raster, isolated by saturation, with limited edge smoothing and contour simplification. They preserve the **observed silhouette** at reference-image resolution, including irregularities from the original image and its rasterization; they are not recovered original vector artwork or exact parametric reconstructions. SVG paths are straight-segment approximations to the smoothed traced outline.

The partially painted-over icon areas in the source image were intentionally excluded because their boundaries cannot be determined faithfully. The reference palette swatches, sectional header pills, and dividers are also excluded since they are not the app's button shapes.

The shapes are **canonical live assets as of PocketBoard 1.0.2**: exact
source contour paths are present as `pb_shape_*.xml` native Android vectors.
The connected status uses the more detailed, independently traced
`connected-pill.svg` rather than the earlier coarse `connected.svg` (now in
`../retired-art/coarse-connected.svg`). The media play/pause toggle uses the
single Pause silhouette; the symbol alone changes. Some obscured reference
buttons have no recoverable contour and are not fabricated; Choose reuses the
Apps family silhouette.

Source aspect ratios and subpixel irregularities remain in the SVG paths.
Android tinting changes fill colours without redrawing their geometry.
