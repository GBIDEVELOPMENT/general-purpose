# Glimpse (formerly Waltz) — native Android wallpaper manager design project

**Status:** detailed product concept and engineering/UX research, not an implemented Android application. Original design files and updated presentations exist as conversation downloads; see ASSET-INVENTORY.md for publication gaps.

Waltz is a friendly, beautiful, open-source, local-first wallpaper manager that changes wallpapers from the user's own collections and vetted maintained external sources. It has no Waltz-hosted image catalogue, server, cloud sync service, subscription, or mandatory account.

## Read in order
1. **RAINBOW-QUICKSTART-CONTRACT.md:** golden-path Google Photos to 5-minute shuffle, honest platform restrictions, acceptance tests A001–A015.
2. **70-HUMAN-WORKFLOWS.md:** seventy first-person requests with nested conditions and peculiar but reasonable preferences.
3. **WORKFLOW-DESIGN-RESPONSE.md:** exact technical accommodations, UX grammar, conflict rules, delivery and roadmap.
4. **PRODUCT-SPECIFICATION.md:** complete foundational technical/product proposal plus override addendum.
5. **WORKFLOW-COVERAGE-MATRIX.md:** every W01–W70 need mapped to specific engineering and UX accommodations.
6. **PITCH-DECK-OUTLINE.md:** visual system and slide outline.
7. **design/**: editable tokens, rainbow flow and 16 self-contained vector screen sketches (simplified, not the original screenshot pixels).
8. **ASSET-INVENTORY.md:** produced high-fidelity binary files and their verified publication status.

**Product standard:** easy usage requires no Rules editor; complex scenarios use progressive disclosure. Import selected cloud-backed photos via native Android Photo Picker; imported images are verified and stored offline. The user sees “every five minutes while in use” with truthful eligible/last-applied state rather than a fake guarantee during Doze.

No third-party API policy bypass, unverified image license, Photos scraping, invasive Android permission or privileged accessibility service.

## Additional requirements (October 21, 2026)
- [Screenshot quick import + Google Lens handoff](SCREENSHOT-AND-LENS-FEATURES.md): first-class Share/Paste → rotate/crop → save → Use Now/Add Next/Just Save workflow, plus privacy-preserving per-image Lens sharing and failure/compatibility tests S071-01–S072-04. This is additive to the original 70 scenarios.

- **Universal sharing (F073):** any image or selected batch can be shared via Android Sharesheet to compatible chat apps, email, ChatGPT, Drive, or editors; save copies via system document providers; dedicated Lens remains a contextual shortcut. See [SCREENSHOT-AND-LENS-FEATURES.md](SCREENSHOT-AND-LENS-FEATURES.md#requirement-f073-universal-outbound-image-sharing-and-editing-supersedes-lens-only-action-design).

## Native Android engineering direction (2026-10-21)
- **[NATIVE-ANDROID-ARCHITECTURE.md](NATIVE-ANDROID-ARCHITECTURE.md):** authoritative proposed Kotlin/Compose/Room/Hilt/Navigation 3 architecture, Android 17 SDK baseline, scheduler truthfulness, typed deterministic rules, reliable outbox + image pipeline, Glance widgets, strict security/privacy, sideload APK signing, developer-verification planning, release gates and ordered engineering backlog. This is a specification; no application code or signed APK exists yet.


## 2026-10-22 planning refresh
- [Native architecture and APK delivery blueprint](NATIVE-ANDROID-ARCHITECTURE.md) is the core technical decision document.
- [Pitch-deck outline](PITCH-DECK-OUTLINE.md#v3-native-architecture-pitch-deck-revision-2026-10-22) now describes the 42-slide v3 proposal, retaining 16 screen designs and adding eight Android-native engineering slides.
- The binary v3 PPTX/PDF were generated and visually inspected in the conversation environment. They are **not yet uploaded to this GitHub repository**; see conversation downloads and the existing binary-publication gap.

## Glimpse identity and continuous reel (2026-10-22)

**Current product name: Glimpse.** Waltz was the working title. We are retaining the `Waltz/` source-of-truth document path temporarily to preserve prior links and project history; do not interpret the folder name as the current branding.

The user's selected direction is a tactile **paper reel with five large image windows**, visually extending beyond its viewport to suggest a continuous succession of photographs. The reel is a virtualized browse surface, not a claim of infinite source content. Collection browsing and WallpaperManager changes remain distinct. A conventional **View all** grid is always available.

Read [GLIMPSE-CONTINUOUS-REEL-DESIGN.md](GLIMPSE-CONTINUOUS-REEL-DESIGN.md) for the normative UX/engineering contract and acceptance criteria.

New repository-tracked original editable assets:
- [Five-window tactile reel SVG](design/glimpse-five-window-reel.svg)
- [Off-screen reel browser concept SVG](design/glimpse-reel-browser-concept.svg)

The **Glimpse v4 Continuous Reel** deck contains 57 slides: a Glimpse-branded cover, 15 new reel/UX slides, and the 41 prior foundational slides (legacy embedded UI imagery is superseded). See [PITCH-DECK-OUTLINE.md](PITCH-DECK-OUTLINE.md) and [ASSET-INVENTORY.md](ASSET-INVENTORY.md) for precise binary publication status.

## Motion from day one (2026-10-22)
- [Glimpse motion / rendering architecture](GLIMPSE-MOTION-RENDERING-ARCHITECTURE.md): Compose Canvas/HWUI, cached 5-window paper geometry, selective graphicsLayer transforms, bounded image prefetch, interruptible spring/drag controller, hidden-slot virtualization, native GPU profiling and real-device animation acceptance. **No Glimpse motion benchmark or implementation has yet been performed.**

## Human-centered agent design (2026-10-22)

- [Glimpse human-expectations and cognitive walkthroughs](GLIMPSE-HUMAN-EXPECTATIONS-WALKTHROUGHS.md) translates the merged ROYGBIV IA and creative-composition research ([handoff #29](https://github.com/gamesbyian/general-purpose/issues/29)) into Glimpse-specific first-click/feedback checks for reel browsing, Rainbow import, screenshots, external sharing and automation. Agent theories are not presented as observed user findings; small owner-device studies remain explicitly pending.

## Start here: active Glimpse decisions (2026-10-22)

**[GLIMPSE-CURRENT-DECISIONS.md](GLIMPSE-CURRENT-DECISIONS.md)** is the short current authority; this README and earlier Waltz appendices preserve project history. New preparation-only materials:
- [Visual fidelity and semantic acceptance plan](GLIMPSE-REFERENCE-ACCEPTANCE-PLAN.md)
- [Machine-readable screen and action contract](GLIMPSE-SCREEN-CONTRACT.json)
- [Asset publication manifest, verified hashes and blockers](GLIMPSE-ASSET-PUBLICATION-PLAN.md)

**No Android code, project scaffold, APK or executable UI was created by this planning update.** The newest Glimpse deck/board/source ZIP remain available as originating conversation files, not verified GitHub binary assets.

## 2026-10-22 end-to-end specification and reel critique

The [73-scenario feature completeness audit](GLIMPSE-FEATURE-SPEC-COMPLETENESS-AUDIT.md), [cross-feature technical and behavior contracts](GLIMPSE-TECHNICAL-BEHAVIOR-CONTRACTS.md), [purpose-led critical reel audit](GLIMPSE-REEL-UX-CRITICAL-AUDIT.md), and [full UI surface census](GLIMPSE-UI-SURFACE-CENSUS.md) are the latest non-building specification review. These **supplement and clarify** the old product requirements, not imply native implementation or approval of dual reels. The [v4 deck](PITCH-DECK-OUTLINE.md) depicts **provisional** screens; the user's approved direction is paper material, large image apertures and meaningful cropped-reel selection, not every label/position in the raster mockups.
