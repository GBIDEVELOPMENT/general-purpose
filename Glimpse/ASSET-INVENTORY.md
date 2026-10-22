# Glimpse artifact inventory and publication status

This GitHub repo contains the canonical **textual** specification, 70 user workflows, quickstart test plan, architecture/UX analysis, and pitch-deck navigation. The full **binary presentation and visual mockups were produced and updated in the conversation workspace, but have not been published into this GitHub directory**. Do not claim otherwise.

Session artifact names (available in original conversation downloads):
- Waltz_Product_Specification_and_Implementation_Plan.docx (updated; 17-page formatted specification)
- Waltz_Product_Specification_and_Implementation_Plan.pdf (updated)
- Waltz_Product_Specification_and_Implementation_Plan.md (original baseline; updated canonical version in PRODUCT-SPECIFICATION.md)
- Waltz_UI_UX_Pitch_Deck.pptx (updated; 34 slides)
- Waltz_UI_UX_Pitch_Deck.pdf (updated; 34 slides)
- Waltz_16_Screen_Contact_Sheet.jpg
- Waltz_16_Screen_Mockup_Gallery.pdf
- Waltz_Visual_Assets_and_16_Mockups.zip (sixteen PNG screenshots, generated illustrative art and palette)
- a_single_composite_image_made_of_six_vertical_pane.png

Editable presentation construction sources remain in session workspace: waltz_work/create_screens.py, build_deck.js, write_spec.py with waltz_work/screens and assets. Import them together to preserve exact visual fidelity. Use a binary-capable GitHub upload path when available, then update this inventory with actual verified blob SHAs. Never invent a GitHub link to a non-existent uploaded binary.

## Verified updated binaries available as conversation downloads, not GitHub blobs

- `Waltz_v2_Specification.docx` (16 pages in tested PDF rendering), SHA-256 `5030594404712d43f75e45f59c50e160def79c613f34c3c5e2813ee94506a1bc`
- `Waltz_v2_Specification.pdf`, SHA-256 `3327e52300af1f4b90c0e5b3370e38237f967034ad1acaf314b0113b11d43aaa`
- `Waltz_v2_Pitch_Deck.pptx` (34 slides), SHA-256 `7555c73d140c2af1a323916d8f227d0c582fc368800875d22a272ab6a4eed3ff`
- `Waltz_v2_Pitch_Deck.pdf`, SHA-256 `215f5b0aab06227cf72ca2714c0f1b39698965d6776a243dc5696133e185a84e`
- `Waltz_Complete_Design_Archive.zip` includes original high-fidelity screens, generated artwork, updated exports and source scripts. SHA-256 `7e849434901b01e022284d67e89bb3c5bccfcdb2c83a2af2746b1be7beebffc5` (28 MB). Available in the originating ChatGPT conversation; it is **not published to GitHub**.

## Actual graphics committed to GitHub

`design/brand-tokens.json`, `design/rainbow-flow.svg` and `design/vector-previews/01_today.svg` through `16_presets.svg` are GitHub-tracked original schematic SVGs. They are smaller, editable design sketches and **do not reproduce** the exact archived PNGs or the presentation visuals.

## 2026-10-22 Glimpse reel refresh: asset audit and SHA-256

Current product brand **Glimpse**. The following actual files have been generated in the current conversation container and verified locally:

| Binary / deliverable | Bytes | SHA-256 | GitHub status |
|---|---:|---|---|
| `Glimpse_v4_Continuous_Reel_Pitch_Deck.pptx` | 11,520,835 | `d1e27a58d04067717fefc62a107859caa1f992c47b0f8e323fda3110e28a0dd2` | Pending upload |
| `Glimpse_v4_Continuous_Reel_Pitch_Deck.pdf` | 3,741,252 | `0414b95672e9d18e9cac344eb5107da53c3f6ebe37896cd9270081c1d52da9d7` | Pending upload |
| `Glimpse_v4_Reel_Design_Section.pdf` | 3,383,219 | `30e35eeefac4637de3a3beaa4a1706fd9ecbad028553637d1439a568c00448f5` | Pending upload |
| `Glimpse_v4_Editable_Source_Archive.zip` | 37,644,562 | `3fe31b1560c32ffef671dbc0698d7956c0617358395f16a248223df1a1e99641` | Pending upload |
| `Glimpse_Reel_Identity_Exploration.pdf` | 4,516,220 | `cd4fcf148f48f72fe409973e9fc71458db8e594519d9088162882f0d4ea9c3af` | Pending upload |
| `glimpse_tactile_wallpaper_identity_board.png` | 2,066,345 | `cddbb2a70913de1d2f345a6ec3a60fb4b3dfced428a0c0d3e4c334797661c705` | **Published, Git blob verified** |

Verified repository-authored *editable text/vector* artifacts (GitHub):
- [Glimpse reel visual specification](GLIMPSE-CONTINUOUS-REEL-DESIGN.md)
- [Original five-window reel vector](design/glimpse-five-window-reel.svg)
- [Clipped browser concept vector](design/glimpse-reel-browser-concept.svg)
- Updated [pitch deck outline](PITCH-DECK-OUTLINE.md), [product specification](PRODUCT-SPECIFICATION.md), and [README](README.md).

The GitHub connector currently supports creating UTF-8 source files and Git blobs from provided inline bytes. The locally generated binary bytes cannot be transferred directly by the currently available container-to-GitHub actions in this session. Do not replace a real upload with a misleading GitHub file link. Preserve downloads in the originating conversation and the source archive. The pending-binaries issue remains open.

## Canonical upload manifest (2026-10-22)

The local file size/hash inventory above was independently verified from the actual files in this conversation. The [dedicated asset publication plan](GLIMPSE-ASSET-PUBLICATION-PLAN.md) now owns **publication priority, target paths, approval/evidence caveats, source archive member inventory and upload verification**, including why the large editable ZIP is a higher-value handoff than individual legacy PDF copies. Binary publication is still **pending**, and [issue #28](https://github.com/gamesbyian/general-purpose/issues/28) remains open.

## Repository asset verification (2026-10-22)

The **tactile Glimpse visual board PNG is now verified in GitHub** at [Glimpse/artifacts/glimpse_tactile_wallpaper_identity_board.png](artifacts/glimpse_tactile_wallpaper_identity_board.png): Git blob SHA-1 `0a53b73ef54fe54815f9ff63bce521dbeef91fd2`, size **2,066,345 bytes**, exactly matching the local original (local `git hash-object` reproduced that SHA; SHA-256 `cddbb2a70913de1d2f345a6ec3a60fb4b3dfced428a0c0d3e4c334797661c705`). This supersedes earlier remarks calling **all** Glimpse binaries uncommitted. **Do not** duplicate-upload this PNG. Remaining deck PPTX/PDF, reel section PDF, original exploration PDF and 37.6 MB editable source ZIP still need separate GitHub verification. The board is an expressive **reference direction**, not blanket approval of all its depicted controls.

### Additional published comparison assets (2026-10-22)

In `Glimpse/artifacts/`, the *compact 8-page reel comparison review PDF* and *reproducible Python/fixture source ZIP* are verified real GitHub binary blobs. All six editable SVG visual variants and photo fixtures are in `Glimpse/design/reel-comparison/`. The older v4 57-slide deck and full 37 MB editable archive are **different artifacts** and remain pending per the publication plan. The directory was atomically renamed from Waltz to Glimpse, preserving existing Git object identities.
