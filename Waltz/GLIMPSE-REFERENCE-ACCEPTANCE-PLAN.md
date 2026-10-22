# Glimpse visual-reference and semantics acceptance contract (pre-build)

Date: 2026-10-22. **Planning only.** Translates Ring Road and ROYGBIV practice into a bounded Glimpse design-to-code protocol. No app screenshots, tests or device measurements are claimed.

## The three artifacts that must never be conflated

1. **Approved design reference**: user-reviewed original high-fidelity artwork, explicit geometry/tokens/typography, versioned asset hashes. This is the *target*, not a screenshot of working software.
2. **Executable behavior contract**: machine-readable screen/interaction expectations for real image IDs and Android state, including required, conditional and forbidden elements. This is the *truthful behavior*.
3. **Implementation evidence**: screenshot from **actual app build**, semantics tree, interaction result and GPU/device measurements, with device/build SHA attached. This is what was *observed*.

Agent-created approximations must not be automatically promoted to reference baselines, and a beautiful fixed photograph may not conceal disconnected actions.

## Minimum reference frames (baseline to curate with approved pixels)

| ID | View / state | Invariant |
|---|---|---|
| G00 | Icon coloured 48/72/192dp | Five broad distinct openings, legible hub and outer paper |
| G01 | Icon monochrome 24/48dp and masked launcher | Silhouette legible, no photo dependence |
| G02 | Home, actively rotating, small reel crescent | Hero image dominant; current wallpaper **applied** status |
| G03 | Collection list, collection size 0/1/3/50 | True counts; no fictional duplicated photo thumbnails |
| G04 | Reel browse 50 images, focus 12 | Partial reel cropped, selected hero still, “12 of 50,” View all |
| G05 | Reel quarter-notch, half-notch, settle | Real image identities continuous; masks don't leak; no ghost windows |
| G06 | Interrupted settling + reversal | No spatial jump, queued/dead input or focus ID mismatch |
| G07 | Last real image; non-loop and loop policy | Clear collection end vs intentional loop; no false infinity |
| G08 | Grid View all, same selected image | Actual photo ID preserved; navigation clear |
| G09 | Screenshot edit/Place/Finish | Original preserved, Use Now/Show Next/Just Save explicit |
| G10 | Share original vs crop | Accurate visual indicator of exported pixels, no wallpaper state mutation |
| G11 | Scheduler delayed/error/paused | Eligible, attempted, applied, paused are distinct |
| G12 | TalkBack, 200% fonts, reduced motion | Equivalent actions and source/result semantics |

For each, record target device window dimensions and safe insets; don't hardcode a 412x892 browser CSS pixel size as Android dp. Anchor physical-device profiles in measured Configuration and WindowMetrics.

## Machine-readable starter contract

The sibling [GLIMPSE-SCREEN-CONTRACT.json](GLIMPSE-SCREEN-CONTRACT.json) encodes the initial *design contract*, not a passing test result. It contains root navigation, five state distinctions, 12 critical screen conditions and forbidden assumptions. A future native harness should bind each entry to actual Compose semantics nodes and state repositories. Do not invent source selectors before code exists.

## Visual comparison rules

- Register captures to exact viewport, screen density, font and app mode; store approved image SHA and actual APK commit SHA.
- Compare major *regions*: large-window silhouettes and masks, rim/hub, photograph crop, stationary hero, labels, top/bottom system insets, action row.
- Geometry: image and real view coordinates, touch-area obstruction, window/rim ratio, partial-edge clipping, hero prominence. Photograph content itself must use **the same fixed licensed/user-provided fixture IDs**, not arbitrary generative substitutions.
- Retain side-by-side, 50% overlay and localized difference/edge map. Metric (SSIM/MAE etc.) is diagnostic, not an aesthetic acceptance threshold or a valid comparison across unrelated source states.
- Dynamic validation includes real frame checkpoints (0°, 18°, 36°, 54°, 72°), backwards equivalents, stop/reverse, pending image decode, empty reel and reduced motion. Keep geometry evaluation separate from photographic differences.
- A canvas image may be accurate while controls are dead, or responsive semantics correct while paper looks wrong. Maintain independent gates.

## Five acceptance classes

1. **Composition / style**: the paper object, photography and hierarchy match the approved target.
2. **Semantic accuracy**: every action changes the state users anticipate; preview/apply, selected/current, source/crop and due/applied distinctions maintained.
3. **Functional state integrity**: five apertures virtualize a finite collection without duplicate selection/skips, edge conditions and persistence coherent.
4. **Native device and accessibility**: actual Pixel 6 Pro after install, motion/GPU, real touch, TalkBack, text scaling, dark/light, navigation bars, orientation and reduced motion.
5. **Owner artistic judgment**: explicit view of the live implementation; never inferred from automated tests.

## Efficient CI, not a test factory

Normal screen/Compose changes: small set of semantic and visual checks for touched components. Reel/renderer/geometry changes: additional deterministic frame/crop and GPU interaction trace. Release candidates: full golden set, accessibility and physical handset checks. Don't run hundreds of screenshots for text-only PRs. Report pending/cancelled separately from failed.

**References:** [Ring Road source-visual protocol](https://github.com/gamesbyian/Ring-Road/blob/main/docs/sparse-reference-visual-verification.md), [wallgen canonical screen contract](https://github.com/gamesbyian/wallgen/blob/main/docs/ui-reference/canonical-screen-contract.json), [wallgen CI operations](https://github.com/gamesbyian/wallgen/blob/main/docs/CI-OPERATIONS-2026-10-22.md).

## 2026-10-22 added evidence classes for dual reels and the actual v4 art

- `G13` Collection parent reel→child photo reel with independent IDs, cancellation on parent change, visible labels; test against conventional picker + single reel.
- `G14` Paired Home/Lock preview with separate destination labels, apply actions and unsupported-target fallback; tablet vs narrow portrait with secondary collapsed.
- `G15` Ordinary grid photo selection visibly marks every selected ID; “Add to rotation” has an explicit queue/target effect, with no ambiguous counts.
- `G16` Discover source provenance and rights labels; no unlabeled imagery confused for bundled wallpaper.
- `G17` Home decorative crescent either has a defined action with usable bounds or is unambiguously passive.

All are future *proposed fixture identifiers*, **not approved reference screenshots or automated tests already executed**. The [v4 source art critique](GLIMPSE-UI-SURFACE-CENSUS.md) lists visible omissions. No new native implementation is asserted.
