# Canonical PocketBoard palette

The source of truth for Android UI colour is
`android/app/src/main/java/dev/pocketkeyboard/PocketBoardPalette.kt`.

The first eight button hues approximate the eight vivid source swatches. The ninth
reference swatch, cream, is reserved for foreground text/symbols. Six new hues
fill out fourteen distinct action-button colours.

| Order | Name | Hex | Origin |
| --- | --- | --- | --- |
| 1 | blue | `#0E70F7` | Reference |
| 2 | teal | `#02B8B6` | Reference |
| 3 | pink | `#FA398F` | Reference |
| 4 | purple | `#7D3CEE` | Reference |
| 5 | orange | `#FD791E` | Reference |
| 6 | yellow | `#FDC405` | Reference |
| 7 | green | `#03CE43` | Reference |
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
neutral. Discover and Microphone use purple; Clear uses red-pink. The green
pill's cream text follows the reference art but has limited contrast, which
should be assessed for accessibility before release.

The existing seven-stripe rainbow touchpad is artwork, not the UI palette,
so its colours are intentionally unchanged. The application layout, button
shapes, icons, fonts and remote-control semantics are unchanged.
