# Retired PocketBoard art (non-shipping)

Historical symbols and Android VectorDrawables are preserved for provenance and regression archaeology. They are **not** part of `android/app/src/main/res/drawable` and must not be reintroduced to the UI. The live UI uses the individually traced symbols in `../button-symbols/`, the individual silhouettes in `../button-silhouettes/`, and their generated native vectors.

- `legacy-symbols/`: pre-reference SVG symbols, including the generic squircle.
- `legacy-android-vectors/`: removed native resources for Choose, Backspace, the generic squircle and old launcher composition.
- `coarse-connected.svg`: first coarse connected contour. Superseded by the detailed `../button-silhouettes/connected-pill.svg`, which is the sole connected-status shape used at runtime.

This is an archive, not an alternate asset library.
