# Rubik's Cube colour palettes

The **muted** colourway is the current default, based on the user-supplied reference illustration (6 November 2026). The earlier brighter colourway is deliberately preserved, unmodified, as **original**.

The muted values are hand-matched approximations to the image, not instrument-calibrated extractions. The white is deliberately warm/off-white rather than pure white.

| Sticker | Original (legacy) | Muted (default) |
|---|---|---|
| Blue | `#2985F6` | `#438BB6` |
| Green | `#38CF60` | `#539A76` |
| Red | `#F33A41` | `#AE4044` |
| Orange | `#F19531` | `#C78861` |
| Yellow | `#FFCF35` | `#C9C260` |
| White | `#EEEEEF` | `#DFDDD6` |

The existing vivid palette was *already* `#EEEEEF` for white, rather than literal `#FFFFFF`. The new muted white is noticeably warmer and less bright.

## Integration

The same palettes are available in the normal and one-third-size vector animations.

```js
rubiksLoader.setPalette('muted');     // current default, updates in place
rubiksLoader.setPalette('original');  // preserved vivid version
rubiksLoader.start({ mode: 'solve', durationMs: 15000, palette: 'muted' });
```

Internally sticker state stores its physical face colour key rather than a rendered hex code, so swapping palettes never resets a scramble or interrupts the animation. Palette names and hex values should remain stable for backward compatibility.

### Files

- `index.html`: normal physical size; default muted
- `small-cube.html`: one-third size in world-space (same viewBox); default muted
- `PALETTES.md`: permanent record of both named palettes

Both demos have a palette picker, and neither requires a raster asset.
