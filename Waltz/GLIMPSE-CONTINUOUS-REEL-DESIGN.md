# Glimpse: tactile paper-reel identity and continuous collection browser

**Date:** 2026-10-22. **Status:** approved design direction for prototyping; no functioning Android UI or wallpaper engine is implied. **Former working name:** Waltz. **Primary source:** user-directed concept of a paper View-Master-inspired reel with much larger photographic windows, extending beyond the viewport. **Design references:** Glimpse Reel Identity Exploration (16-page design PDF), the newer tactile visual identity board, and the Glimpse v4 Continuous Reel Pitch Deck (57 slides; binary files currently conversation attachments, not yet GitHub assets).

This document is the authoritative *new visual UX direction*. Older Waltz mockups remain historical experiments and should not be shipped unchanged. Core architecture, platform limits, import/rotation/share promises and UX requirements in other Waltz specs remain binding.

## 1. One object, four jobs, no fake hardware

A **soft, tactile cream paper reel** with **five huge image-filled apertures**. The reel suggests an almost inexhaustible succession of delightful views. The reel does *not* represent the number of items contained in a collection. Its window count is a UI template; the number of assets is stored independently.

1. **Launcher identity:** simple 5-window disk + centre spindle. Monochrome themed icon retains the 5 cutouts. The photo version is a visual exploration; actual adaptive icon foreground must remain legible at small sizes, under arbitrary launcher masks. Do not use View-Master logos, characteristic trademarks or exact trade dress.
2. **Collection cover:** populate the five slots with representative images from that specific collection; source image identities determine the cover. Gracefully handle collections of 0–4 and unknown thumbnails with deliberately chosen paper-toned placeholders, not phantom duplicates.
3. **Collection browser:** oversized reel, its **left/right/lower edges clipped off screen** so the user understands more images can pass through it. One selected image is shown in a large, undistorted rectangular hero preview above it.
4. **Home / Now Playing:** a *small partial crescent* of the same reel becomes a visual signature beside a dominant wallpaper preview. Do not place giant disks in every screen or overwhelm first-run tasks.

**Rendering:** five wide angular windows at nominal 72° pitch, with a real photo filling each and a generous non-photographic central hub. Larger photograph apertures are more important than reproducing any exact historical reel geometry. Paper grain is restrained and optional; do not obscure the images with film-grain effects.

## 2. Continuous illusion versus actual data

The interface can look continuous **without claiming infinite content**. Keep at most five visible slots with a small offscreen thumbnail/preload buffer. Change the asset IDs bound to those reused slots as the focus index advances. A disk does not mean a collection contains five photos; the UI must always show a real count such as “12 of 50”.

- **In-order browsing:** collection gives a deterministic ordered list, stable image IDs and focus index. When the user reaches the final item, either stop with an “End of collection” cue, or enter *explicitly selected* “Loop when browsing” mode. Do not imply live arrival of new sources when looping existing images.
- **Shuffle:** order is a persistent seeded permutation and no-repeat cycle, respecting exclusions and the recent-repeat boundary. A physical reel turning through a completed cycle may visually loop, but the engine starts a new explicitly tracked shuffle cycle, not an unbounded random feed.
- **Dynamic membership:** if a user deletes, excludes, reorders or imports while browsing, maintain the selection by image ID and re-derive valid neighbours; skip missing items with an explanation. Do not index into a stale array or display old pixels for new IDs.
- **Nested/composite collections:** flatten and filter according to the existing domain rules, with provenance retained for image detail; do not force a nested reel-in-reel metaphor.
- **Empty/singleton/two images:** empty collection uses an unfilled illustrated reel with prominent Add photos; singleton shows one true photo and four subtly blank windows; two to four show exactly their true images. A loop may repeat those images in a *sequence*, but repeated slot artwork should never misrepresent collection cardinality.

**Never** implement by allocating an Android bitmap containing the entire list. The apparent infinite motion is a *small, stateful viewport*.

## 3. Screen anatomy and behaviors

### Collection reel view, portrait

1. System bars, top app bar with collection name and overflow.
2. Collection status: true item count, current sorting or Shuffle state.
3. Rectangular large current-image preview with focal point. Include visible “12 of 50” position.
4. Small label **Browse the reel** and a persistent ordinary **View all** affordance.
5. Large disk anchored below the hero preview. Its circle is wider than the device and its bottom is outside the clip region. A fixed coral triangular index marker points to the currently selected window.
6. Fixed semantic **Previous**, **Next**, **Set as wallpaper**, **Share** actions. These must have >=48dp targets and not move around as the disk turns. Secondary More menu handles crop, details, remove and source provenance.
7. System bottom navigation remains clear, legible and independent of disk clipping.

**Critical split:** browsing/turning the reel changes *only the preview*. WallpaperManager changes only after an explicit Set as wallpaper/Next wallpaper command in its own context. The two Next concepts are named distinctly on screens where ambiguity could arise: **Next photo** for reel browse, **Change wallpaper** for active rotation. Do not conflate “next image in visual browser” with “advance live lineup”.

### Home

Wallpaper preview dominates; show collection name, last actual application, honest next eligible time, quick **Change now / Pause / Share** controls. A restrained paper reel crescent on a secondary corner ties the brand together without using valuable gesture space. Do not promise exact five-minute changes during Doze.

### Collections landing

Cards may feature a portion of a reel filled with each collection’s photos. Collection title and actual count remain readable outside the disk. Preserve list/grid alternatives and accessible selection controls.

### Full grid

**View all** opens a conventional grid of the same items and preserves the focus asset ID. Multi-select, drag where available, search/filter and batch share belong here. Return to reel with the same selected image and persisted scroll position. Users can make Grid the default collection display.

### Landscape/tablet

Prefer a side-docked partial disk with hero photo and details in an adjacent pane. Avoid shrinking windows until their imagery becomes illegible. Use window-size classes, actual insets and bounded image regions, not hardcoded percentage positioning.

## 4. Interaction and motion

- Tap an exposed aperture to focus its asset if there is a reliable large hit area; the tappable region is *not* limited to the precise photo-shaped wedge. Use a semantic rectangular hit target where practical.
- Explicit Previous/Next buttons are always available. Optionally allow horizontal swipe over the reel region, with direction matching visual expectations and RTL tested; vertical swipes remain page scroll. Avoid letting drag gestures steal Photo Picker, system edge-back or assistive gestures.
- Advance by **one 72-degree notch per discrete request**; at most a controlled small number for kinetic swipe if interaction testing proves it. A slide can show a rotated disk but the actual source of truth is selected image ID. Motion duration candidate 180–240 ms with ease-out and optional subtle haptic; not a timer guarantee or a wallpaper transition.
- A fixed frame/index marker and a *stationary hero preview* reduce cognitive load. An optional gentle crossfade for the hero can follow the end of snap; should not jitter during drag.
- In reduced motion: instant image replacement without spinning, spring, inertial scroll or automatic cycling. Never auto-spin the reel merely because wallpaper rotation is enabled.
- Do not use mechanical noises by default, or perpetual decorative motion.

## 5. Wording and navigation

Brand = **Glimpse**. Provisional tag line **Something lovely, every time you look.**

Top-level destinations: **Home / Discover / Collections / Automation**. Maintain standard labels **Add photos**, **Crop**, **Rotate**, **Shuffle**, **Share**, **Set as wallpaper**, **Pause**, **Next photo**, **View all**, **Source**, **Rules**.

Preferred microcopy:
- “50 wallpapers · Shuffle without repeats”
- “Browse the reel”
- “View all”
- “12 of 50”
- “Set as wallpaper”
- “Next change eligible in about 3 min”
- “Couldn't change your wallpaper. Try now · Details”

Short editorial/warm phrases in empty states are welcome, but buttons, errors and permission requests must be unambiguously functional. No ornamental “spindle”, “cartridge”, “expose”, “advance the wheel” jargon in tasks.

## 6. Implementation design (Android native)

Use Compose Canvas graphics / Path clip for photowindows backed by Coil-prepared, resolution-bounded thumbnails, with a separately managed gesture/semantic interaction layer. Avoid per-frame image decode or recreating large Path objects per animation frame. Prefer cached Paint/path geometry, remember values, stable immutable slot models. Rectangular hero image uses standard Coil/Compose. Use native state restore keyed by `AssetId` and `CollectionId`, not just ordinal indices. A finite `List<WindowSlot>` projected around the focus asset ID is the entire visible reel; collect underlying collection state through the existing pure domain engine.

Sample projection:
```kotlin
data class ReelUiState(
    val collectionId: CollectionId,
    val focusImageId: ImageId?,
    val focusIndex: Int,
    val totalCount: Int,
    val reelSlots: List<WindowSlot>, // 0..5, never entire collection
    val browseMode: BrowseMode,       // STOP_AT_END | LOOP
    val isShuffle: Boolean,
    val isAnimating: Boolean
)
```
The reel composes `focusIndex-2..focusIndex+2` where permitted, assigning stable ids and explicit placeholders. When motion finishes, recenter the five rendered slots (virtualization) rather than continuously increasing a conceptual global angle or allocating unbounded intermediate frames. Separate the current gallery focus from the active system wallpaper. On high resolution/density, downsample thumbs to actual window bounds + small overscan, not source image dimensions; release previews with library viewport changes.

### Performance and reliability gates

- No UI-thread decode; scroll/turn no stutter on real Pixel 6 Pro under a 10k-image synthetic library.
- Bounded decoded bitmap memory, cache eviction policies, placeholders for images that are slow/corrupt/remote.
- Preserve browsing focus after rotation, process death and app resume; live wallpaper update must not unexpectedly rotate an open browse wheel.
- No duplicate or skipped item when 20 consecutive Next events, removal during animation or a shuffle cycle boundary occurs.
- Low battery/Reduced motion mode immediately stops extra animation; battery impact measured, not assumed.
- Check Compose semantics/TalkBack: announce “Golden Hour, image 12 of 50; Next photo; Previous photo; View all; Set as wallpaper”. Expose accessible alternate linear list. Support Switch Access, keyboard, 200% text, large touch targets, high contrast, RTL, orientation and font scale.

### User validation and gate

Prototype the wheel as a standalone Compose screen with fake image data before integrating with the live engine. Test the 3-way comparison: continuous partial reel / all-image grid / simple swipe pager. Tasks: discover next picture, understand how many photos exist, apply selected wallpaper, return to current wallpaper, find image 137, share image, manage a 3-item collection, operate with TalkBack. Ship reel browsing only if task clarity and battery/performance match ordinary controls; the grid is not an optional escape hatch and must work independently.

## 7. Responsive geometry and visual requirements

Nominal portrait illustration: reel **diameter ~1.65–1.85× the collection content region width** (illustrative, not a hard dp rule). Anchor disk center below the browsing viewport and clip within its content layer. About the upper semicircle is visible; actual extent depends on insets, large text and device posture. Photo wedges ideally span roughly 60–70% of the annular radial width. Keep the paper as an outer rim and small radial separators; it should not occupy most of the visual area.

Tablet and landscape: dock partial disk to a side; centre hero photo in available pane. The clipped reel is never allowed to cover Android back affordances, persistent buttons, navbar, labels, or progress diagnostics. If height constraints become severe, shrink or hide the reel and make the grid/pager primary.

**Colour direction:** tactile ivory `#F6F0E6`, deep blue-green `#153F46`, coral `#E8876C`, sunlight yellow `#F0C970`, sage `#87B7A6`. Reconsider chroma/contrast in dark mode. Original imagery should lead.

## 8. Deliverables / publication integrity

The new pitch deck adds a **15-slide Glimpse visual-UX section** in front of the earlier 41 exploratory/technical slides and fully replaces the original cover. Editable text is rebranded Glimpse where possible; *legacy raster mockup screenshots remain visibly historical* and are superseded by the new reel screens. The deck totals **57 slides**.

Recently created conversation binaries:
- `Glimpse_Reel_Identity_Exploration.pdf` (16 pages)
- `glimpse_tactile_wallpaper_identity_board.png`
- `Glimpse_v4_Continuous_Reel_Pitch_Deck.pptx` and `.pdf`
- `Glimpse_v4_Reel_Design_Section.pdf` (16-page quick review)
- Older `Waltz_v3_Native_Android_Pitch_Deck.pptx/pdf` retained as historical baseline

**Binary GitHub publication:** Verify actual upload, not just markdown links. The GitHub text connector can create UTF-8 files, but the installed runtime currently provides no direct binary file upload path from the slide-rendering container to GitHub. Keep the binary items listed as pending until truly uploaded. The repository can preserve this spec, editable text outlines and SVG design assets in the meantime. Do not claim binary files are committed.

## 9. Design inspirations checked

- Android Compose/Material carousel behavior: https://developer.android.com/develop/ui/compose/components/carousel
- Android MotionLayout carousel illustrates recycled views and circular wrap: https://developer.android.com/develop/ui/views/animations/motionlayout/carousel
- Material 3 carousel guidance and accessibility: https://m3.material.io/components/carousel/overview
- Compose semantics/accessibility: https://developer.android.com/develop/ui/compose/accessibility/semantics
- Android performance: https://developer.android.com/topic/performance

**Document priorities:** native system and privacy contracts continue unchanged. This is Glimpse’s new *interface design direction*, not an exception to Android scheduling limitations or source-image rights.

## Rendering and animation authority (2026-10-22)
Read [GLIMPSE-MOTION-RENDERING-ARCHITECTURE.md](GLIMPSE-MOTION-RENDERING-ARCHITECTURE.md) for the first-class native motion system and performance acceptance. Use cached geometry, bounded image textures, Compose Canvas/drawWithCache and selectively retained graphicsLayer draw transforms; `Animatable` preserves drag interruption and physics continuity, with a real-asset-ID domain anchor separate from transient angle state. No 120 Hz performance promise before physical-device traces. The reel must not be a looping GIF or independent global animation timer.

## Human expectations / cognitive walkthroughs (2026-10-22)

See [GLIMPSE-HUMAN-EXPECTATIONS-WALKTHROUGHS.md](GLIMPSE-HUMAN-EXPECTATIONS-WALKTHROUGHS.md), adopted from [ROYGBIV research handoff issue #29](https://github.com/gamesbyian/general-purpose/issues/29). The reel must be tested as a **human expectation surface**, not just as geometry. Before the user touches it, ask what turning a window would change; inspect whether the visible count conveys a large-but-finite collection, and whether the user distinguishes **preview selection** from **setting the phone's wallpaper**. Compare the reel with Grid using identical tasks. Hypotheses are explicitly not observed user findings. Keep the existing approved paper-reel identity and semantic action labels unless evidence supports revision.

## 2026-10-22 critical audit: purpose before reel count

Read [GLIMPSE-REEL-UX-CRITICAL-AUDIT.md](GLIMPSE-REEL-UX-CRITICAL-AUDIT.md) and [GLIMPSE-UI-SURFACE-CENSUS.md](GLIMPSE-UI-SURFACE-CENSUS.md). Previous single-reel sketches are **reference hypotheses**, not evidence that a decorative Home crescent, missing Previous control or “Next/Set now” copy is acceptable. Each reel must navigate a real typed set (photographs, collections or carefully constrained visual variants) with a clear preview/apply boundary. Evaluate an asymmetric **small Collection reel → large Photo reel**, and a paired **Home/Lock photo preview** on larger layouts, against conventional pickers/tabs. Both are **unapproved** until they demonstrably improve selection and preserve accessibility. Never place a reel simply to balance a composition. The current image and Grid retain conventional actions, no live wallpaper apply on browse gestures; source tech detail [here](GLIMPSE-TECHNICAL-BEHAVIOR-CONTRACTS.md).
