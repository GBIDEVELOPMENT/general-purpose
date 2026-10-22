# Glimpse: controlled reel layout comparison and decision record

**Date:** 2026-10-22  
**Status:** visual research/prototypes only; **no running Android UI, device acceptance, or human preference test**.  
**Decision level:** single large Photo reel is the **recommended baseline**, not a final visual signoff. Collection→Photo and destination-pair are **comparison candidates**. Retain the previously approved *warm tactile paper and large photo windows* as brand direction. The illustrative mockup geometry is not a pixel-approved master.

## Open the actual artifacts (verified in GitHub)

- [Eight-page compact review PDF](artifacts/Glimpse_Reel_Layout_Comparison_Review.pdf) (rendered, deliberately smaller review export)
- [Complete reproducible source ZIP](artifacts/Glimpse_Reel_Comparison_Reproducible_Source.zip) (generator + six actual photo fixtures + manifest)
- [Editable mockup source directory](design/reel-comparison/) and [fixture identities/SHA-256](design/reel-comparison/COMPARISON-MANIFEST.json)
- The larger, sharper, text-selectable eight-page PDF is preserved in ChatGPT Library at `/Glimpse/Comparison/Glimpse_Reel_Layout_Comparison_v1.pdf`; this is a different export of the same study, not a separate design.

**Technical proof of Git publication:** Both repo binaries were committed as real `100644` Git blobs, and SVG reference files and six original JPEGs are also Git-tracked. Do not confuse these with the larger *earlier v4* source archive, which still has its own unresolved publication inventory.

## Controlled experiment design

**Fixtures:** six specific photographic artworks `art1.jpg`…`art6.jpg` from the earlier Glimpse v4 editable-source archive, reused unchanged. No outside images are added to make a particular candidate look better. All variants use same palette, typography, target button language and source photograph for the main selected Golden Hour preview. Exact file hashes and design assumptions are in `COMPARISON-MANIFEST.json`.

**Geometry:** five wide paper apertures; one photo per active aperture, two blank apertures for a three-member collection reel, no fabricated duplicate items. Six real photos overall in the study. Phone composition `420×900` *design units*, wide `960×540`; these are **illustration canvases, not verified Android dp or safe-area sizes**. A 24–48dp icon study and actual inset measured layouts remain separate gates.

**Confounding controls:** same content, identical device proportion for all phone comparisons, same major action labels, same wallpaper-apply boundary. Differences intentionally isolated to selection topology and amount of visual space consumed. All photographed outcomes are mocked states, not interactive or physical device screenshots. No user task metrics are claimed.

## The six visual variants

| Variant | What its paper reel(s) actually select | Decision | Main trade-off |
|---|---|---|---|
| [A: one Photo reel](design/reel-comparison/A_single_photo_reel.svg) | One selected `ImageAssetId` in Golden Hour; only the preview changes | **Recommended compact baseline** | Largest hero and simplest mental model; collection switching uses ordinary navigation |
| [B: asymmetric Collection → Photo](design/reel-comparison/B_asymmetric_collection_photo.svg) | Parent `CollectionId` changes child source set; child `ImageAssetId` changes preview | **Prototype candidate** | Fun and meaningful nested selection, but shrinks hero and crowds controls; only worthwhile when switching collections frequently |
| [B compact fallback](design/reel-comparison/B_compact_fallback.svg) | Labeled collection picker + one Photo reel, same typed transitions as B | **Required responsive fallback if B explored** | Functional preservation at lower visual density, avoids two tiny drag targets |
| [C0: Home/Lock tabs](design/reel-comparison/C_destinations_tabs_baseline.svg) | Selected destination and photo, one active reel | **Recommended compact target-selection baseline** | Clear destination ownership and full hero |
| [C1: compact paired preview](design/reel-comparison/C_destinations_compact.svg) | Main Home photo reel + smaller explicit Lock preview/Edit Lock action | **Prototype candidate** | Maintains second destination context without pretending a small arc is a precision wheel |
| [D: wide Home/Lock dual](design/reel-comparison/D_destinations_wide_dual.svg) | Two independent `ImageAssetId` previews, separately applied to Home/Lock | **Wide-layout candidate** | Wider panes permit two real touch-controlled reels; must still validate visible hit surface and no accidental cross-target apply |

### What the pictures themselves reveal

- **A:** purpose is unmistakable. Main weakness is that changing collections requires leaving/using a picker, which may be fine for the majority of wallpaper journeys.
- **B:** a *real hierarchical selection relationship* justifies a second reel in principle. Yet the small upper reel carries low information density and takes room away from the hero. It must outperform a regular collection selector in natural discovery and subjective delight before adoption. If there are fewer than five collections, draw empty apertures rather than fake repeated selections.
- **B fallback:** shows that design integrity is **retaining semantic results**, not keeping two circles on screen at all costs.
- **C0/C1:** a compact phone should prioritize one destination for precision selection. A persistent small Lock preview may aid comparison without needing two simultaneous 2D gesture systems. Traditional Home/Lock tabs remain the strong control.
- **D:** two reels represent genuinely separate Android destinations, so two are defensible when space and OS capability allow. They remain *preview selectors*. Two independent Apply buttons report separate API results. A wider design must earn actual continuous wheel interaction (enough visible aperture and touch zone), not simply feature two cropped images of reels as scenery.

## Typed causality and gestures

**A:** `SelectBrowseAsset(assetId)` → update selected photo, hero, `3 of 6`; no `WallpaperManager`, queue, or automatic schedule change. Separate `SetNow(assetId,target)` attempts OS apply and reports acknowledged/failed/unknown.

**B:** `SelectBrowseCollection(collectionId)` → cancel child's interrupted animation, restore last valid child focus by stable ID or first eligible photo, update actual count; **no schedule activation**. `SelectBrowseAsset(assetId)` → preview only. Nested child cannot inherit stale photo ID from previous collection.

**C/D:** `SelectDestination(HOME|LOCK)` and `SelectPreviewAsset(target,assetId)` → change only that target's preview. `Apply(target)` may change actual OS wallpaper for target if supported. Never change opposite target, unless explicit both/linked-choice action. Last-acknowledged state and unknown external changes handled as in [technical behavior contracts](GLIMPSE-TECHNICAL-BEHAVIOR-CONTRACTS.md).

**User motion:** all gestures interruptible, no hidden auto-spin, no need for circular dragging for TalkBack/keyboard/Switch Access. Standard Prev/Next controls remain. Parent and child reels must not both respond to the same drag. Index/count and labels must remain stationary and outside paper windows.

## Decision questions before promoting dual reels

1. Does an unfamiliar user correctly say what each reel selects *before any coaching*?
2. Does the smaller parent reel help more than a labeled collection picker on a phone where photo enjoyment dominates?
3. Can a person confidently choose another image in **three gestures or fewer**, and find a known item using Grid rather than rotary traversal?
4. Can they tell what is **previewed**, **queued**, and actually **applied**?
5. Are same data identities and selections preserved when switching Reel ↔ Grid ↔ destination tabs and in reduced motion?
6. Does a 200%-text/short-height layout restore normal controls before shrinking hits or obscuring the photo?
7. Does a two-reel wide layout have genuinely usable independent visible drag zones, not just attractive partially clipped covers?
8. Do parent changes cause visible photo popping, skipped identity, or simultaneous wheel animations?
9. Is the paired destination flow even supported for independent Home/Lock apply on the physical device?

**Proposed short owner test:** 8 tasks: browse 3 photos without applying; switch Golden Hour→Wild Places; return to original selection; find specific image in Grid; apply Lock only; choose two separate crops; operate with reduced motion; explain last applied and next eligible. Record prediction→first action→result→misinterpretation. Compare A and B; compare C0 and C1; evaluate D only at a relevant wide window. Small task walkthrough, not a synthetic questionnaire or fabricated quantitative study.

## Changes to current plans

- Maintain [single-reel photo browser](GLIMPSE-CONTINUOUS-REEL-DESIGN.md) as baseline in upcoming native prototype.
- Reframe **secondary reels as domain-driven experiments**, not compulsory decorations; implement only after interaction/user evidence supports them.
- Add the variant, artifact SHA and screenshot region mapping to [visual acceptance](GLIMPSE-REFERENCE-ACCEPTANCE-PLAN.md) and [screen contract](GLIMPSE-SCREEN-CONTRACT.json) when one layout is approved for coding.
- Avoid three default navigation implementations: share typed state and commands, change presentation only where suited.
- No motion-system programming or Android app building authorized by this comparison. All values, image selection and interaction consequences here are *specification and visual intent only*.

## Sources and method

- [ROYGBIV → Glimpse human-expectations handoff #29](https://github.com/gamesbyian/general-purpose/issues/29)
- [Glimpse critical reel UX audit](GLIMPSE-REEL-UX-CRITICAL-AUDIT.md)
- [Glimpse screen census](GLIMPSE-UI-SURFACE-CENSUS.md)
- [Ring Road visual reference evidence standard](https://github.com/gamesbyian/Ring-Road/blob/main/docs/sparse-reference-visual-verification.md)
- [Nielsen Norman Group: Mobile Carousels](https://www.nngroup.com/articles/mobile-carousels/)
- [Android adaptive app guidance](https://developer.android.com/develop/adaptive-apps/guides/adaptive-dos-and-donts)
- [Android edge-to-edge / gesture insets](https://developer.android.com/design/ui/mobile/guides/layout-and-content/edge-to-edge)
