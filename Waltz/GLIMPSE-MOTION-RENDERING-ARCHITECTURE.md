# Glimpse motion and reel rendering architecture
**Proposed implementation contract · 2026-10-22**  
Depends on [GLIMPSE-CONTINUOUS-REEL-DESIGN.md](GLIMPSE-CONTINUOUS-REEL-DESIGN.md) and [NATIVE-ANDROID-ARCHITECTURE.md](NATIVE-ANDROID-ARCHITECTURE.md). Status: researched design direction; **not yet implemented or benchmarked**.

## Decision
Build Glimpse as **native Kotlin + Jetpack Compose** with a custom 2D paper-reel drawable based on Compose Canvas/drawWithCache and selective graphicsLayer transforms, backed by Android's HWUI/Skia rendering pipeline. Maintain a **single logical motion coordinator** with frame-clock-bound `Animatable` and a typed, testable reel browsing state machine. Use Coil/Android decoders for bounded, preloaded thumbnails. Preserve Compose components and native semantics for all controls. **Do not start with OpenGL ES, Vulkan, a Unity-like game loop, Lottie for the reel, runtime procedural paper texture or a continuously ticking animation clock.**

This architecture is intended to deliver fluid native animations while preserving coherent layout, accessibility, Android navigation, low idle CPU/GPU use and reference fidelity. **Do not assert a guaranteed 120 FPS** from framework choice alone. Measure and optimize on Pixel 6 Pro and additional OEMs in release-profiled builds.

## Renderer shape and visual hierarchy

1. **Retained UI:** Compose Material 3 for navigation, typography, image detail, action buttons, settings, accessibility and responsive layout.
2. **Reel artwork:** original signed-off source geometry with five **wide photo windows**, paper face, subtle rim/shadow and central opening, all in a single normalized coordinate system. Asset provenance, source approval and exact export hashes live alongside code. Don't synthesize approximations to approved mockups.
3. **Image viewport:** decode/cache **only current and near-neighbor** thumbnails at window pixel size (plus modest overscan for transforms), not full image originals or a 10k collection. Hero-preview bitmap independently sized. Loading work on background dispatchers.
4. **Cached geometry:** create annular wedge Paths, image masks, rim and static paper effects when size/density/theme or asset changes, not each frame. `drawWithCache` is appropriate for reusable expensive objects.
5. **Motion:** rotate a contained drawing/layer through a transform (typically `graphicsLayer { rotationZ = controller.angle }` or canvas `rotate`) with **the angle state read in the draw phase**, keeping Compose recomposition and layout work out of each frame. Choose the cheaper of isolated reusable layer vs direct canvas after profiling actual overdraw; avoid unnecessarily rasterizing a full oversized reel into an enormous offscreen RGBA texture.
6. **Clipping:** clip at the intentional reel viewport, respecting system bars and interaction/action regions. Hardware-accelerated wedge clipping or an alpha-mask atlas may be compared in a performance spike. A non-rectangular crop must be antialiased and must not visibly alter the original photographs.
7. **Interactive hit model:** the visible circular art does **not** own controls. Provide separate stable Compose hit targets and semantics for Previous photo, Next photo, Set as wallpaper, Share and View all. Aperture touch region may be larger than the visible image window for reliable tapping.
8. **Accessibility:** reel is an optional visual alternative to a semantic linear list/grid. Announce selection and real count. Reduced motion uses instant replacement rather than an animated disk.

## Two independent coordinate spaces

**Domain coordinates:** persistent `collectionId`, stable `assetId`, ordered index/shuffle permutation, real count, membership. Immutable in a preview unless a meaningful user operation occurs.

**Presentation coordinates:** ephemeral **angular offset** in degrees (and temporary touch velocity). At rest, `angle = 0` relative to the current focus anchor; a next-item gesture targets one `72°` interval for the five-window reel. After the new focus settles, update the logical anchor and shift visible slot bindings behind the clipped viewport, then rebase presentation angle to the same visual orientation **without a visible jump**. Rebind only fully hidden slots, not a window that is still passing through view.

Use 5 artistically visible apertures, with photo decode prefetch for at least 2 upcoming and 2 previous assets. If more than one full notch can be travelled in a flick, perform safe stepwise virtualized rebasing as hidden slots pass through invisible portions. Otherwise limit a gesture to one/two notches until tested. Never create an infinitely accumulating Float angle. When the entire reel is visible (large device), don't fake an invisible seam: dock/crop it, limit browsing or use a different pager model.

The *hero image* should remain stationary while the disc rotates. Once focus selection commits, transition to the new preview via a bounded crossfade (not a full source decode during animation). Do **not** confuse browse selection with the actual Android wallpaper apply operation.

## Input and motion controller

Model explicit states: `Idle`, `Dragging(pointer)`, `Settling(targetAssetId, velocity)`, `Rebasing`, `DisabledOrReducedMotion`.

- Touch down cancels an ongoing settle and captures the **current rendered angle and velocity**, rather than jumping back to a previous logical position.
- Drag maps tangent-directed movement to angular delta using a defined pivot; avoid unstable delta near the hub. Test both left/right segments and Android back-edge gestures.
- Release records angular velocity using `VelocityTracker`. Use `Animatable` with `snapTo`, `animateTo` and optionally a **bounded** decay to target a legal nearest notch. Prefer a critically or slightly overdamped spring for tactile settling, not a rubber-band bounce. Retarget/interruption continuity is mandatory.
- Fixed Previous/Next buttons settle precisely one notch; no unbounded fling and no animation queue that continues after a new user gesture.
- If the source list shrinks or collection changes mid-motion, cancel/retarget based on stable image IDs, never stale indices.
- If a next image is not ready in cache, let the *paper motion* settle but preserve/replace the photographic window with a tasteful stable placeholder and finish image reveal only when decode completes. No blocking bitmap fetch on drag/release. Prefer preloading to make placeholders rare.
- Clear haptic click only at **meaningful completed notch**, never on each rendered frame; use Android-supported feedback. Avoid forced audio effects.
- All animations cancel on screen disposal, lifecycle stop or navigation where relevant; no perpetual looping animation or always-on GPU thread.
- Exact ordering/queue history is maintained in a pure Kotlin selector, independent of any graphics angle.

## Unified motion language (initial tuning candidates; revise by tactile device review)

| Interaction | Proposed motion | Candidate envelope |
|---|---|---|
| Tap Next photo | Single 72-degree reel advance; calm settling | ~220–320 ms |
| Drag and release | Velocity-aware travel; spring to legal notch | device/velocity dependent, usually <400 ms |
| Hero photo change | Soft opacity crossfade, no dramatic scale | ~140–220 ms |
| Collection cover -> collection browser | Stable shared image element / bounds transition when supported | ~260–400 ms |
| Grid <-> reel | Preserve selected image ID; simple shared image transition or modest crossfade | ~200–300 ms |
| Add imported image | Short, directed acknowledgment from import result to collection | ~160–260 ms |
| Wallpaper applied | Deliberate success affordance only after platform call succeeds | ~150–200 ms |

These are **prototype parameters**, not obligations to use exactly those durations. The app-wide tokens should encode intent: `instant`, `quiet`, `reveal`, `mechanicalSettle`, `screenContinuity`. Screen semantics own when they are used, so animations don't become a random grab bag.

Use springs primarily for directly manipulated motion; tweens for controlled image fades; shared-element transitions selectively for navigation. Avoid stacking simultaneous, independent scale/blur/translation/opacity effects that visually fight. Do not animate dimensions/placement during fast reel movement. Honor system animator scale, accessibility reduced motion, pause/resume and Power Saver design decisions; instant changes remain semantically identical.

## Compose-level implementation layering

```text
GlimpseScreen (Compose)
  ├─ HeroPreview (Coil image, independent image transition, semantics)
  ├─ ReelViewport (Compose clip, no controls hidden behind graphics)
  │   ├─ ReelPainter (cached Path masks, static paper/rim, ~5 thumbnails)
  │   └─ graphicsLayer { rotationZ = reelAngle.value }  // draw-phase read
  ├─ SelectedAssetMetadata
  ├─ Controls (semantic Compose buttons / TalkBack)
  └─ ViewAllGrid (LazyVerticalGrid, stable keys / type)
        ↑
ReelInteractionController (Animatable + velocity + transition state)
        ↕
BrowseReducer (pure; stable asset IDs, finite order, rebasing actions)
        ↕
Repository / images / prefetch  (no wallpaper writes during browse)
```

`graphicsLayer` may record reusable drawing instructions and transform them without reissuing all draw code. However, the renderer must be benchmarked on the real GPU: large offscreen layers, deep clip nesting, alpha-heavy shadows and continuous blurs can erase benefits. Avoid `RenderEffect` blur in the main animation path. Paper texture can be one small static compressed bitmap or vector-tinted material; don't regenerate noise on every frame. Use AGSL on API 33+ **only as a measured, optional embellishment** with simple 29–32 fallback, never as a prerequisite for the core wheel.

## Platform separation: *UI reel* versus *system wallpaper*

The paper reel is an **app UI visualization**. Its smooth animation is not the system wallpaper transition. A `WallpaperManager` call can complete independently and might not animate the home/lock wallpaper across OEMs. UI success is shown only after a real apply result. The optional `WallpaperService.Engine` for animated wallpaper transitions has its **own lifecycle-aware renderer and visibility restrictions**; it should share image recipes/cache format and a small set of motion parameters, **not** a live Compose view hierarchy or a perpetual animation loop.

## Reference-fidelity gate (Ring Road + wallgen)

Do not implement from a slide image alone. Commit source geometry, image fixture IDs, material samples, design tokens, preferred fonts, photo masks and sample frames in one canonical source package with checksums.

Classify evidence:
- **Direct design reference:** paper, frame/window silhouettes, five-slot proportions, typography, hero/browse layout.
- **Source-derived motion:** 0, .25, .5, .75 and 1 notch transforms, computed from approved geometry.
- **Application-observed:** empty/1/3/50/10k collections, stale image URI, async loading, drag interruption, updated membership, TalkBack, real GPU frame captures.
- **Inferred:** physically plausible shadow updates or motion dynamics not specified by a still mockup. Require designer/user review.

Create a visual reference storyboard with static checkpoints at 0°, ±18°, ±36°, ±54°, ±72° in both directions; real running captures at matching state, overlays and semantic-region crops. Full-image pixel MAE is **diagnostic**, never aesthetic signoff or proof of correct runtime state. Screenshots of source implementation must be labeled device/emulator/build SHA; never quietly replace canonical reference with the latest implementation screenshot.

## Performance and battery quality gates

The first prototype should run a **repeatable 100-next/100-back and 60-second drag/settle trace** with at least 50 and 10,000-record fixture libraries, both light/dark and normal/reduced motion. Test real photos with varying aspect ratios, 12-megapixel originals, slow decode, memory pressure and dynamic deletions.

- Device baseline: real **Pixel 6 Pro**, 120 Hz capable when enabled; second 60 Hz low/mid-range device and one Samsung/OEM. Record actual display mode/refresh; 120 Hz nominal frame interval ≈8.33ms, 60 Hz ≈16.67ms; **frame deadline includes UI, render and GPU work**.
- Use Android `Macrobenchmark` with `FrameTimingMetric`, `Perfetto` traces, and optionally `JankStats`; never infer hardware performance from emulator screenshots. Benchmark **profileable release-like** builds, not debugger-on debug builds.
- Proposed targets for interactive reel drag: 60 Hz baseline, 120 Hz on capable hardware when device actually exposes that mode. Aim **>=99% of frames on time** in controlled main-device runs after warm-up; capture p50/p90/p95/p99 frame timing, missed-vsync clusters, time to first visible frame, prefetch stalls, peak bitmap GPU/Java heap. Record deviations and trace causes, rather than reporting unsupported “always 120 FPS.”
- For a single frame budget, avoid any main-thread image decoding, file IO, SQL query, JPEG recompression, thumbnail allocation or rule evaluation. High-frequency state reads in draw phase, not whole-screen Compose recomposition. Use stable keys and bounded slots.
- Tune overdraw and GPU layers by trace; no infinite shader/animation when the UI is idle, screen is stopped or motion is disabled.
- Physical side-by-side screen recording must confirm no texture flicker, disappearing wedge, photo pop or crop seams. Battery Saver and thermal throttling are **different test regimes**, not hidden failure of the normal baseline.
- Test repeated touch interruption, rapid direction reversal, pointer up/down, accidental system-edge back, 200% text, switch access, RTL, screen rotations, process death and app backgrounding.

## First implementation slices

**R0** Build fake-data native Compose ReelViewport + MotionController *before* the full app. Five large apertures, real paper artwork, source-image fixtures, stable image IDs, clip behavior and optional grid. Show approved 0/18/36/54/72-degree frames. Record GPU trace from Pixel 6 Pro.

**R1** Implement finger following, bounded spring snap, interruption/velocity preservation, semantic buttons and reduced-motion instant state. Build the deterministic frame-script harness (drive angle programmatically for screenshots; no fake app outputs).

**R2** Add cache/preload, stable hidden-slot rebinding, async failure placeholders, 10k collection simulation. Verify no visible seam, no identity skips, no bitmap OOM.

**R3** Integrate with collection domain and image importer while retaining preview/apply separation. Shared selected-image transitions across Home, Reel and Grid. Test real APK on physical Pixel; record per-build perf and reference diff artifacts.

**R4** Add optional richer paper/shadow effect only after the above is comfortable, reference-faithful, accessible and measured. Refuse shader effects that worsen scrolling or battery.

## Research sources (checked October 2026)

- Compose animation performance / draw-phase state: https://developer.android.com/develop/ui/compose/animation/quick-guide
- Graphics layers / drawWithCache: https://developer.android.com/develop/ui/compose/graphics/draw/modifiers
- State reads by phase: https://developer.android.com/develop/ui/compose/performance/modifier-phases
- Gesture interruption and velocity: https://developer.android.com/develop/ui/compose/animation/advanced
- Shared elements, including clipping caveats: https://developer.android.com/develop/ui/compose/animation/shared-elements
- Performance tracing, benchmarks and Baseline Profiles: https://developer.android.com/topic/performance/baselineprofiles/measure-baselineprofile
- AGSL Android 13+ constraints: https://developer.android.com/develop/ui/views/graphics/agsl
- Internal precedents: https://github.com/gamesbyian/Ring-Road/blob/main/docs/painted-physical-device-acceptance.md ; https://github.com/gamesbyian/wallgen/blob/main/docs/ui-reference/README.md

**No motion benchmark has yet been executed for Glimpse.** These are explicit implementation and test commitments, not results.

## Human interpretation of motion (2026-10-22)

Follow [GLIMPSE-HUMAN-EXPECTATIONS-WALKTHROUGHS.md](GLIMPSE-HUMAN-EXPECTATIONS-WALKTHROUGHS.md) for cognitive checks from the cross-project [issue #29](https://github.com/gamesbyian/general-purpose/issues/29). Every drag, velocity-release, interrupted settle, hidden-slot rebinding and delayed photo decode must give the human an intelligible answer to “Which photograph is selected?” and “Did my actual wallpaper change?” The response is tested first as an expectation, then as a real native state transition. **Motion fidelity** and **mental-model accuracy** are separate release gates; a smooth 120 Hz reel that falsely implies successful wallpaper application has failed UX acceptance. Reduced-motion mode must convey identical state and choices without animation.

## 2026-10-22 paired-reel motion constraint

Multiple reel widgets share rendering and paper geometry but maintain **independent typed selector IDs and angular controllers**. An interaction on one must not silently rotate the other; a parent Collection reel may trigger a **deterministic, cancelable data rebinding** of the child Photo reel. Only the engaged reel should animate at full frequency on compact devices. Degrade the secondary reel to a labeled selector when height, memory, 200% text or gesture conflicts arise. Never launch two enormous off-screen layer textures unmeasured. Reference [critical reel UX](GLIMPSE-REEL-UX-CRITICAL-AUDIT.md) and [technical contract](GLIMPSE-TECHNICAL-BEHAVIOR-CONTRACTS.md).
