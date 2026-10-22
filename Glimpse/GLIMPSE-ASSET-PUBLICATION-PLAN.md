# Glimpse design assets: publication and provenance plan

**Audit 2026-10-22.** Current location: `Glimpse/` in `gamesbyian/general-purpose`, brand **Glimpse**. This is a file-publication checklist, **not evidence of a completed binary upload**. The current conversation container holds the exact files below and has verified their SHA-256 digests against [ASSET-INVENTORY.md](ASSET-INVENTORY.md). Repository GitHub connector is text/inline-content only; no container-to-GitHub binary transport is available here. The container's ordinary git network DNS is unavailable. Do not assert that a file is uploaded until the GitHub blob is checked.

## Newest reference package, in publishing priority

| Priority | Upload target | Source artifact | SHA-256 | Why |
|---|---|---|---|---|
| P0 | `Glimpse/artifacts/Glimpse_v4_Editable_Source_Archive.zip` | `/mnt/data/Glimpse_v4_Editable_Source_Archive.zip` | `3fe31b1560c32ffef671dbc0698d7956c0617358395f16a248223df1a1e99641` | **Best complete handoff**: includes pitch/PDF, hero art, reel renders, screen PNGs, and the original deck-generation Python source |
| COMPLETE | `Glimpse/artifacts/glimpse_tactile_wallpaper_identity_board.png` | `/mnt/data/glimpse_tactile_wallpaper_identity_board.png` | `cddbb2a70913de1d2f345a6ec3a60fb4b3dfced428a0c0d3e4c334797661c705` | Most vivid selected tactile paper / large-window reference; **concept accepted as direction, not every precise visual pixel approved** |
| P0 | `Glimpse/artifacts/Glimpse_v4_Continuous_Reel_Pitch_Deck.pptx` | `/mnt/data/Glimpse_v4_Continuous_Reel_Pitch_Deck.pptx` | `d1e27a58d04067717fefc62a107859caa1f992c47b0f8e323fda3110e28a0dd2` | Editable presentation |
| P1 | `Glimpse/artifacts/Glimpse_v4_Continuous_Reel_Pitch_Deck.pdf` | `/mnt/data/Glimpse_v4_Continuous_Reel_Pitch_Deck.pdf` | `0414b95672e9d18e9cac344eb5107da53c3f6ebe37896cd9270081c1d52da9d7` | Reviewable exact deck |
| P1 | `Glimpse/artifacts/Glimpse_v4_Reel_Design_Section.pdf` | `/mnt/data/Glimpse_v4_Reel_Design_Section.pdf` | `30e35eeefac4637de3a3beaa4a1706fd9ecbad028553637d1439a568c00448f5` | Concise review reference |
| P1 | `Glimpse/artifacts/Glimpse_Reel_Identity_Exploration.pdf` | `/mnt/data/Glimpse_Reel_Identity_Exploration.pdf` | `cd4fcf148f48f72fe409973e9fc71458db8e594519d9088162882f0d4ea9c3af` | Historical 16-page exploration, includes superseded smaller-window alternatives |

The source ZIP has these files under `source/`: `build_v4.py`, six `art*.jpg` photo assets, `screen-home.png`, `screen-browse.png`, `screen-collection.png`, `screen-grid.png`, `reel-five-wide-windows.png`, `reel-next-frame.png`, `reel-last-frame.png`, `reel-monochrome.png`, `reel-virtualization-sequence.png`, `contact.png`. These are **source/design assets**, not proof of a native-running application. The original `build_v4.py` has `/mnt/data` absolute working paths and needs path normalization plus licensed font/photo fixture decisions before it is truly a reproducible build script.

### Previous-generation artifacts

Keep the Waltz v2 specification, 34-slide deck, v3 native architecture deck, 16-screen mockup archive and their original references under `Glimpse/artifacts/history/` **only if needed for provenance**. They are historical; do not make an agent load all of them automatically or mistake outdated UI screens for current Glimpse acceptance. Existing [issue #28](https://github.com/gamesbyian/general-purpose/issues/28) tracks previously blocked publication.

### Presently published, confirmed in GitHub

- [Glimpse five-wide-window reel original vector](design/glimpse-five-window-reel.svg)
- [Off-screen collection browser diagram](design/glimpse-reel-browser-concept.svg)
- [Decision register](GLIMPSE-CURRENT-DECISIONS.md), [human expectations](GLIMPSE-HUMAN-EXPECTATIONS-WALKTHROUGHS.md), [reference acceptance](GLIMPSE-REFERENCE-ACCEPTANCE-PLAN.md), and [screen contract](GLIMPSE-SCREEN-CONTRACT.json).

The SVGs are **smaller editable schematic originals**, not replicas of the photographic board or slides.

## Publishing protocol

1. Use an authorized **binary-capable Git client/upload mechanism** and this exact source archive; no raw GitHub API UTF-8 substitution for PNG or PPTX.
2. If the repo has size constraints or wishes to avoid repeatedly committing big binaries, publish to a **GitHub Release** and commit a verified download manifest; choose one durable canonical location. A 37 MB archive is under GitHub's 100 MB object hard limit but still large for Git history. Do not upload archive **and all contents** blindly.
3. Verify size, SHA-256, zip contents and actual GitHub URLs; commit a manifest with Git blob/Release asset identifiers and which reference is **approved vs exploratory**. Only then move issue #28 toward resolution.
4. Build no app and start no Android implementation as part of publication.
5. Avoid a copied PDF being treated as the editable canonical source. Extract/check in portable geometry, token and design scripts, with linked photo fixture rights, as a separate future pre-build publishing task.

## Explicit blockers

- **For remaining binaries:** a container-to-GitHub binary transport is not verified in this session. The tactile board PNG has already been independently Git-blob verified, so don't generalize this blocker to every file. Other local files exist and have checksums, but text connector does not accept an arbitrary container file path, and ordinary container git DNS has failed previously.
- **Visual authority:** user's paper-reel preference and larger-window request are approved direction. Every raster asset is **provisional until explicitly selected as a canonical reference** for implementation.
- **Font and photo licensing:** review rights before making original stock/prompt imagery or exact licensed fonts distributable source fixtures.

**Do not close issue #28** until the bytes actually exist in the repository or a persistent linked Release asset.

## 2026-10-22 preservation improvement: durable ChatGPT Library copies

The six newest Glimpse binaries have also been uploaded successfully into the user's persistent **ChatGPT Library folder `/Glimpse/`**, not merely left in an originating chat's temporary file links:

- `Glimpse_v4_Editable_Source_Archive.zip`
- `Glimpse_v4_Continuous_Reel_Pitch_Deck.pptx`
- `Glimpse_v4_Continuous_Reel_Pitch_Deck.pdf`
- `glimpse_tactile_wallpaper_identity_board.png`
- `Glimpse_v4_Reel_Design_Section.pdf`
- `Glimpse_Reel_Identity_Exploration.pdf`

Library upload operations all returned **succeeded**. This removes the ephemeral-conversation-file dependency and makes source material recoverable from ChatGPT Library in future sessions. **It does not grant GitHub agents access to those binary bytes**. Issue #28 remains blocked until the contents actually reach GitHub. Do not represent Library entries as repository blobs or GitHub release assets.

## Repository asset verification (2026-10-22)

The **tactile Glimpse visual board PNG is now verified in GitHub** at [Waltz/artifacts/glimpse_tactile_wallpaper_identity_board.png](artifacts/glimpse_tactile_wallpaper_identity_board.png): Git blob SHA-1 `0a53b73ef54fe54815f9ff63bce521dbeef91fd2`, size **2,066,345 bytes**, exactly matching the local original (local `git hash-object` reproduced that SHA; SHA-256 `cddbb2a70913de1d2f345a6ec3a60fb4b3dfced428a0c0d3e4c334797661c705`). This supersedes earlier remarks calling **all** Glimpse binaries uncommitted. **Do not** duplicate-upload this PNG. Remaining deck PPTX/PDF, reel section PDF, original exploration PDF and 37.6 MB editable source ZIP still need separate GitHub verification. The board is an expressive **reference direction**, not blanket approval of all its depicted controls.

### Renamed path notice (2026-10-22)

All current project files, including the already-published comparison review PDF and reproducible source ZIP, moved from `Waltz/` to `Glimpse/` with their Git blob IDs unchanged. [Compact comparison PDF](artifacts/Glimpse_Reel_Layout_Comparison_Review.pdf) and [reproducible source ZIP](artifacts/Glimpse_Reel_Comparison_Reproducible_Source.zip) are **complete GitHub uploads**, distinct from the larger older 57-slide v4 deck and 37 MB editable archive still pending. References that begin `Waltz/` in historical issue comments are superseded by this path.
