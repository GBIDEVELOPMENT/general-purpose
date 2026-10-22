# Glimpse: current decisions and non-building handoff

**Current as of 2026-10-22.** This is the short routing authority for pre-implementation decisions. Historical Waltz documents remain valuable evidence, **not competing current decisions**. The project folder was renamed from `Waltz/` to **`Glimpse/`** in a content-preserving Git tree commit; historical references to Waltz name remain historical only. Do not build an app under this planning task.

## 2026-10-22 two-way audit status

- **Completed on paper:** [All 73 feature contracts](GLIMPSE-FEATURE-SPEC-COMPLETENESS-AUDIT.md), [technical behavior and typed command semantics](GLIMPSE-TECHNICAL-BEHAVIOR-CONTRACTS.md), [critical reel alternatives](GLIMPSE-REEL-UX-CRITICAL-AUDIT.md), [complete UI surface census](GLIMPSE-UI-SURFACE-CENSUS.md), and expanded [screen contract](GLIMPSE-SCREEN-CONTRACT.json).
- **Confirmed direction:** paper reel with broad photographic windows, honest finite collection indexing, primary large photo reel and Grid alternative.
- **Unapproved hypotheses:** dual collection/photo reels, dual Home/Lock reels, variant/history reels, specific asymmetric placements and screenshots that were not expressly approved. Compare with conventional controls before implementation.
- **Outstanding empirical decisions:** human first-click and meaning tests, genuine Android capability results, device motion/size measurements, exact approved asset bundle.
- **No app implementation performed** in this audit.

**Execution/status queue:** [GLIMPSE-SPEC-AUDIT-DECISION-QUEUE.md](GLIMPSE-SPEC-AUDIT-DECISION-QUEUE.md) is the prioritized non-building plan for specification repair, dual-reel design comparisons, technical proof gates and reference upload.

## Current priorities and precedence

1. **User-approved experience:** Glimpse, warm tactile paper reel, five **large** photographic apertures, deliberately cropped off-screen, a stationary full-sized hero photo, real finite counts, and a permanent conventional Grid / View all alternative. [Visual spec](GLIMPSE-CONTINUOUS-REEL-DESIGN.md).
2. **Expected results, not component names:** [human expectations and cognitive walkthroughs](GLIMPSE-HUMAN-EXPECTATIONS-WALKTHROUGHS.md) derived from [research handoff #29](https://github.com/gamesbyian/general-purpose/issues/29). Agent hypotheses are not evidence of human observation.
3. **Render and motion fidelity:** Compose/HWUI paper reel, stable asset identity independent of angle, bounded image textures, interruptible drag/snap, clear reduced-motion alternative, physical Pixel proof. [Motion contract](GLIMPSE-MOTION-RENDERING-ARCHITECTURE.md).
4. **Android implementation:** Kotlin/Compose/Room/command journal/WallpaperManager/Glance; sideloadable signed APK; no hosted service. [Native architecture](NATIVE-ANDROID-ARCHITECTURE.md).
5. **Feature behaviors:** 73 natural-language workflows, with golden Rainbows import-to-shuffle path, screenshot crop/rotation, original-or-crop sharing to compatible Android targets, and truthful five-minute scheduling. [Workflows](70-HUMAN-WORKFLOWS.md), [Rainbow contract](RAINBOW-QUICKSTART-CONTRACT.md), [sharing](SCREENSHOT-AND-LENS-FEATURES.md).

Where text conflicts, the more recent *specific* user decision takes precedence; flag unresolved technical contradictions via this document, **not ad hoc code shortcuts**. Do not promote visual mockups or old status commentary into normative authority.

## Explicitly resolved

| Topic | Current decision | Common trap |
|---|---|---|
| Brand | Glimpse (Waltz historical only) | Leaving old name in *current* user-visible UI |
| Reel | Original five-window **paper** form, large photo apertures | Literal View-Master windows, tiny images, stationary decorative disk |
| Motion | Interruptible, precise and physics-aware; warm visual tone | Infinite GPU animation, queueing taps while disc spins |
| Reel selection | Browsing updates preview only | Calling wallpaper API when a window rotates |
| Current wallpaper | Separate state with verified applied result | Calling preview or scheduled eligibility “applied” |
| Collection size | True finite count, visible position | Implying five windows = five images or inexhaustible feed |
| Browsing modes | Reel **and** Grid; preserve selected photo | Hiding Grid behind metaphor |
| Background changes | Android-managed, best effort and honestly explained | Guaranteeing exact five-minute static changes under Doze |
| Imports | Android picker/SAF/Share, durable local copies | Implying Photo Picker synchronizes a Google Photos album |
| Sharing | Universal Android Sharesheet; original or edited copy | Dedicated unreliable Lens-only integration |
| Motion accessibility | Equivalent actions and information at reduced motion | Visual animation as the only feedback |
| Source assets | Approved binary references + versions + checksums | Reconstructing reference from markdown or falsely claiming upload |
| Acceptance | Separate visual, semantic, functional, device and human evidence | Replacing user approval with AI screenshot similarity |

## Missing pre-build documents / decisions (ordered)

**P0 before first implementation PR**
- **Canonical visual source of truth**: actual editable and raster reference assets in repo, with provenance/approved-vs-exploratory flags, hashes, and viewport/pose naming. Present **blocked by binary upload**; see [publication manifest](GLIMPSE-ASSET-PUBLICATION-PLAN.md) and [#28](https://github.com/gamesbyian/general-purpose/issues/28).
- **Screen state and semantics contracts**: machine-readable required/conditional/forbidden elements, real data state distinctions, component ownership and semantic-action assertions, adapted from wallgen without reproducing an overlarge test factory. See [acceptance plan](GLIMPSE-REFERENCE-ACCEPTANCE-PLAN.md).
- **Owner review:** confirm five-window aesthetic at launcher sizes and giant cropped viewport, and whether visual `Next photo` is understandable as *preview* rather than *applied wallpaper*. This is pending, not silently approved.
- **Project location/package ID/signing key custody**: decide before distributing an APK; recommend a dedicated source repo once application building is requested. Don't use general-purpose credentials or create code now.

**P1 during first prototype, not a prerequisite to planning**
- Build a Compose reel with source fixtures and explicitly labeled UI state; photograph/geometry/hero/index continuity; real Pixel 6 Pro GPU and gesture traces.
- Conduct brief owner cognitive walkthroughs (W01, W57, F071, F073, W60) before escalating to a large icon atlas or motion-effect toolkit.
- Validate runtime/performance/Android scheduler claims on real devices; report actual measured results rather than aspiration.

**P2 later**
- Source provider rights/API terms, recursive rule editor usability, more exhaustive OEM matrix, external editing roundtrip, optional GPU shader embellishments.
- Curated release-grade icon variants, monochrome, dark/light, 16–48dp / adaptive masks, font licence audit.
- Replace historical screenshots in deck with real implemented Glimpse screenshots *once available*, preserving them as older explorations until then.

## Minimal agent workflow

1. Read this page, then only the owning current contract.
2. Map user's natural-language task to expected perceptual outcome and the exact state affected.
3. Cite approved reference asset and distinguish direct pixels, derived transforms, code-observed behavior and inference.
4. Inventory required / conditional / forbidden screen elements before design or implementation.
5. Prefer a narrow implementation test plus visual side-by-side for changed regions; deep suites only on relevant risk.
6. Real Android hardware/user approval remains separately open. Never claim Photoshop-like mockups demonstrate runtime fidelity.
7. Update one current owner document, and link from here, rather than appending a new contradicting release-status paragraph throughout the spec.
