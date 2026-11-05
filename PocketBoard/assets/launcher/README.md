# PocketBoard launcher icon source artwork

This folder contains four **separate, reusable SVG assets**, traced from the supplied reference images, and two assembled SVG previews.

- `keyboard-symbol.svg`: transparent, closely cropped, filled white keyboard silhouette. Raster-color thresholding (RGB channel minimum > 235, alpha > 200) isolated 12 connected white components from the 1254 × 1254 squircle PNG. Their contours were simplified by only 1.6 source pixels, preserving slightly uneven edges and key shapes. The main frame's inner cutout uses the even-odd fill rule.
- `squircle-mask.svg`: the reference PNG's alpha silhouette, cleaned of tiny peripheral artefacts and simplified by 4.2 source pixels. The resulting outline is normalized to a 1024 × 1024 viewBox.
- `circle-mask.svg`: a centered, full-size mathematically circular icon mask consistent with the circular reference.
- `rainbow-background.svg`: square seven-band red/orange/yellow/green/cyan/blue/purple background. The original straight band divisions remain, but their representative fills
  have been normalized to the seven approved canonical PocketBoard hues
  (red-pink, orange, yellow, green, teal, blue, purple). Gradients/pixel-level
  raster texture are not retained in this vector interpretation.
- `preview-circle.svg` and `preview-squircle.svg`: preclipped composites for checking the artwork or use outside Android. The legacy `assets/pocketboard-icon.svg` is now the squircle composite, not the outdated three-row keyboard.

## Android launcher behavior

Android 8+ uses adaptive launcher icons. `ic_launcher_background.xml` extends the **unclipped rainbow to the edges of the adaptive canvas** and `ic_launcher_foreground.xml` contains **only the traced white keyboard** in the central safe area. Both `@mipmap/ic_launcher` and `@mipmap/ic_launcher_round` reference these same two layers. The device launcher applies its configured mask, including circles, squircles, rounded squares and other vendor shapes. The app cannot force or reliably detect the launcher-selected exact silhouette; the exported masks are references and standalone assets, not overrides for Android launcher preferences.

`pb_header_icon.xml` renders a reference-squircle composite for the in-app header, where system adaptive masking is not applicable. Existing app ID, pairing, keyboard handling and Windows receiver are unchanged.

## Acceptance checks

1. Install the new Android APK and verify no black tile corners on a launcher using circular icons.
2. Change the launcher icon shape to rounded-square/squircle (where available) and verify the same keyboard and rainbow fill the shape without an inner preclipped icon.
3. Inspect the app header at 40dp and the icon at multiple launcher sizes to check legibility and clipping.
4. Run the existing Gradle Android build in CI. Android adaptive mask preference should be checked on a launcher/device; compilation alone does not validate visual presentation.

## 1.0.2 palette reconciliation

The original white keyboard paths and adaptive masks are unchanged. Only the seven
rainbow-band fills have been unified with PocketBoard's canonical palette.
The original raster references are inventoried in `../references/`.

## 1.0.3 contrast and header optical normalization

Canonical yellow/green fills are now `#FFD42A` / `#007E59`
throughout the launcher, header and preview SVGs. Keyboard geometry and
adaptive icon masks are unchanged. The in-app header ImageView applies
1.09× horizontal / 1.11× vertical scale to compensate for source artwork
padding and visually match its 40×40dp Discover neighbor. Launcher shape
and real-device optical alignment still require device acceptance.
