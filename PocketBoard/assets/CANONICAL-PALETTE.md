# Canonical PocketBoard palette

The source of truth for Android UI colour is
`android/app/src/main/java/dev/pocketkeyboard/PocketBoardPalette.kt`.

The first eight button hues approximate the eight vivid source swatches. The ninth
reference swatch, cream, is reserved for foreground text/symbols. Six new hues
fill out fourteen distinct action-button colours.

| Order | Name | Hex | Origin |
| --- | --- | --- | --- |
| 1 | blue | `#008CFF` | Reference |
| 2 | teal | `#02B8B6` | Reference |
| 3 | pink | `#FA398F` | Reference |
| 4 | purple | `#7D3CEE` | Reference |
| 5 | orange | `#FD791E` | Reference |
| 6 | yellow | `#FFD42A` | Accessibility-adjusted reference |
| 7 | green | `#00875F` | Accessibility-adjusted reference |
| 8 | red pink | `#E92F61` | Reference |
| 9 | sky blue | `#22A3FF` | Companion |
| 10 | violet | `#A857FF` | Companion |
| 11 | coral | `#FF5A3C` | Companion |
| 12 | magenta | `#D94BDE` | Companion |
| 13 | lime | `#76DE1A` | Companion |
| 14 | indigo | `#4D62FF` | Companion |
| Foreground | Cream | `#FCF4E9` | Reference |

The reference samples are approximate because the source is a raster screenshot.

Secondary semantic colours: charcoal `#171923`, disconnected status
`#283040`, muted cream `#E6DDD0`, hint cream `#D0C9BE`.

Controls use the fourteen button colours in display order, skipping empty
positions. Connected uses green and cream; disconnected and searching stay
neutral. Discover and Microphone use purple; Clear uses red-pink. The connected pill uses the canonical emerald; after the 1.0.6 lightening, its cream-text contrast should be verified on-device.

The seven-band touchpad, launcher icon and in-app header icon now reuse
canonical colours in order: red-pink, orange, yellow, green, teal, blue,
purple. The input panel uses the approved disconnected neutral. Ripple feedback
uses the canonical cream with a fixed translucent alpha (`#33FCF4E9`).
Exact source traces preserve their original white glyphs for provenance;
shipping action symbols are canonical cream and the keyboard launcher symbol
may remain true white as explicitly approved by the reference art.

`android/verify_canonical_art.py` is the CI lock: any runtime colour outside
the 14 vivid, 5 semantic and 1 translucent press-feedback values must be
explicitly reviewed and approved with a manifest update. This applies to
launcher/header VectorDrawables as well as Kotlin-drawn UI. Button shapes and
symbols are now deployed, not merely archived.

## 1.0.3 colour-vision accessibility revision (2026-11-05)

The owner cannot distinguish the old yellow and green rainbow bands reliably.
Both canonical colours change throughout the touchpad, header, adaptive
launcher, preview SVGs and button set: yellow `#FFD42A` (bright sunflower),
green `#00875F` (slightly lighter emerald). The visual distinction from yellow and text contrast require renewed on-device checks. These are computational checks,
not a substitute for owner on-device discrimination testing.

Placeholder cream `#D0C9BE` is now 50% opaque (`#80D0C9BE`);
it remains the single approved translucent hint token. Original reference
rasters are not recoloured, preserving their provenance.

## 1.0.6 owner-requested adjustment

Blue is now `#008CFF`, a clearer bright blue distinct from indigo; emerald green is now the slightly lighter `#00875F`. These tokens apply to the rainbow pad, adaptive launcher, header icon, source SVGs and action backgrounds. The Tab and Esc silhouettes exchange assignments, while their symbols, colours, positions and commands stay unchanged. The cursor uses a two-contour reference trace in button-symbols/cursor-pointer.svg and the matching native vector.
