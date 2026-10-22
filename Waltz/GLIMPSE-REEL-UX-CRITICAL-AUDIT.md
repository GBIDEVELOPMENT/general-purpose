# Glimpse reel mechanics: adversarial UI/UX and layout audit

**Date:** 2026-10-22. **Scope:** critical, task-led review of existing Glimpse v4 artwork and specifications, including asymmetric **multiple-reel** hypotheses. **Planning only; no native implementation and no aesthetic approval inferred.**  
**Current artistic direction preserved:** tactile paper, large image apertures, visible-but-cropped disc, photography first. The illustration is a *proposal*, not a certified screen layout.

## 0. The governing rule

**A reel is justified only if it navigates a coherent set whose members the user wants to inspect in sequence or compare by appearance.** For each proposed reel, write:
`{ setBeingTraversed, selectedId, ordering, consequenceOfSelection, applyBoundary, countAndEndpoint, previewFeedback, adjacentActions, alternativeNavigation, touchAccessibility, failureStates }`.

If you cannot answer these fields with domain data and observable behavior, **remove the reel** or demote it to an explicitly noninteractive collection illustration. Reels are not generic substitutes for menus, settings, number pickers, dropdowns, rule precedence, or source hierarchy.

The **paper object** is a visual motif; the **selector** is a real control. One may exist without the other, but the user must be able to tell which. Tapping a passive collection cover should enter that collection; it should not pretend to rotate.

## 1. Existing v4 reference screen audit, not an implementation screenshot

These judgments are from the `Glimpse_v4_Editable_Source_Archive.zip` source visuals: `source/screen-home.png`, `source/screen-collection.png`, `source/screen-grid.png`, `source/screen-browse.png`, `source/reel-five-wide-windows.png`, and the 57-slide deck. Their widths/heights are authored artwork. **They do not demonstrate live Android dp fit, touch, safe-area handling, image decoding or functional interaction.**

### Home: `source/screen-home.png`

**Keeps:** generous current wallpaper hero, cream background, elegant title, attractive side-cropped paper crescent, legible current collection.  
**Challenges:**
- The lower-right cropped disc currently has no named target, count or consequence; it risks being *decorative UI posing as an interactive control*.
- “Next” is ambiguous among next browser photo, next queued item and actually applying the next wallpaper. On Home, say **Change wallpaper** or **Change now**, and show verified result.
- “Eligible in about 3 min” lacks a clear association with the selected destination and rotation policy; show **Next change eligible** and destination, not an apparent exact countdown guarantee.
- Missing visible Home/Lock target, share/undo/recent image affordance, and clearer paused/suspended/error states.
- Distinct wallpaper image and collection cover reel must not imply they depict the same asset at the same time unless driven by domain data.
**Provisional change:** Keep a *small, partial collection reel* on Home **only if** tapping it clearly opens the active collection or reveals a labeled nearby-item selection affordance. A tiny cropped reel is **not a precision drag wheel**. If it carries no function, remove it from Home and keep the motif in collection thumbnails.

### Collection detail: `source/screen-collection.png`

**Keeps:** full hero photograph, true item count, five huge image apertures and offscreen cropped disc.  
**Challenges:**
- “Next” appears without “photo” and **Previous photo** is not shown even though the contract requires it.
- “Set now” is ambiguous about **destination** (Home/Lock/Both), whether it replaces active wallpaper and whether rotation continues.
- Text “Shuffle on” while position reads “1 of 50” does not explain *which ordering* determines the index; browsing order and active delivery queue must be independent.
- The enlarged disc dominates the lower screen yet much of it is clipped. Its central hub and several windows may be untouchable; test whether the actually exposed surface provides an effective swipe/tap zone.
- The reel is masked near the bottom controls and bottom navigation; motor gestures and screen-edge Back may collide.
- Fixed pointer is visually doubled/stacked in reference. Use one understandable, aligned focal indicator.
- Hero photo appears repeated in active reel aperture; acceptable for selected-item visual continuity **only if the exact same asset ID is used** and the selected window has an unmistakable state.
- No loading/error/empty/last-item presentation, selection accessibility, inspect details, edit, hide, share or direct image-position jump shown. These need clear reachable homes, but do not crowd the first-level actions.
- Overlarge reel and hero together squeeze controls at 200% font scale and on short usable-height phones.
**Provisional change:** Use a single bounded **reel viewport** below the hero; put stable **Previous photo / Next photo** near the index marker, with **View all** and primary **Set as wallpaper** separated from browse navigation. On small or large-text screens, the reel reduces before any essential control does. Keep index/total outside the paper.

### Discover: `source/screen-browse.png`

**Challenges:** Three visually attractive landscape/flower cards do not show whether they are a provider, collection, wallpaper or search result; “New collection” at the bottom of Discover is contextually surprising. The screen lacks search/filters/attribution/licence/preview/approval/rights labels. The art may be mistaken for free bundled stock.
**Provisional change:** Each discovery card must state **what it is** (source, themed collection, single image) and provide the matching action. “Create collection” belongs to Collections unless a specifically explained capture flow leads from Discover to a new collection. Default Discover to a search/list/grid of accessible sources; reels are only optional for **small curated, strongly related image sets**, not the source directory itself.

### Grid: `source/screen-grid.png`

**Challenge:** More than a decorative grid alternative, this must support finding photo 137, jump/search/filter, multiselect, exclusion, batch import/share and source provenance. Make the same selected asset obvious when switching to/from reel; consistent count and ordering; avoid forcing per-image drilldown to identify selection. No rotating paper UI is needed inside bulk management.

### Identity art and existing SVGs

The **photographic wide-window paper disc** in the newer board is much stronger than earlier tiny-window historical variants. The repo SVG `design/glimpse-five-window-reel.svg` is a simplified, editable **schematic**, not a faithful extraction of tactile texture or photos. Explicitly classify raster board as *preferred exploratory art direction* and the SVG as *illustrative fallback*. Do not treat either as complete shader/geometry implementation truth without an approved source/asset atlas.

## 2. Reel types: a legitimate taxonomy

| Role | Data domain | Selection consequence | Suitability | UI recommendation |
|---|---|---|---|---|
| **Photo reel** | Ordered/shuffled list of `ImageAssetId` within collection | **Preview selected image only**; apply separately | **Core, strong** | One large clipped reel, stationary hero; grid alternate |
| **Collection reel** | Named `CollectionId` set (covers made of images) | Preview collection / open it; **not** silently activate schedule | **Strong if curated/small** | Medium selector with readable titles and counts; conventional list for large libraries |
| **Source exploration reel** | Curated related candidate `AssetId` within one source/query | Preview/approve/add candidate | **Conditional** | Use only for small coherent picks; normal search grid remains default |
| **Recent-history reel** | Applied wallpaper events, ordered by time | Inspect, undo/reapply through explicit action | **Conditional** | Short last-N history selector; event timestamps visible; full Activity list available |
| **Variant reel** | Small intentional crop/effect preview variants of **one selected image** | Select a recipe variation, not mutate source or apply automatically | **Conditional** | Compare 3–7 visual recipes; before/after direct comparison remains available |
| **Home vs Lock reels** | Two destination-scoped image/collection selections | Independently preview each target, explicit apply/queue per destination | **Promising dual-reel candidate** | One prominent + one subordinate on compact phone, side by side on wider screens |
| **Parent-collection + child photo reels** | Parent collection IDs and child asset IDs | Parent selection rebinds child domain; child selects image | **Promising dual-reel candidate** | Small parent reel + large child reel, offset and asymmetrical, selection displayed textually |
| **Rule/mode/settings reel** | Rules, booleans, periods, priorities, permissions | Would alter settings/automation | **Generally reject** | Standard segmented controls, lists, switches, time pickers and explicit editor |
| **Scheduling ‘clock’ reel** | Continuous time or numeric values | Changes interval / due time | **Reject** | Time/interval picker, presets and explanation; no image-window metaphor |
| **Decorative reel** | No user-selectable domain | None | **Allowed only as unmistakable art** | Cover/branding; does not respond to scroll/tap as a selection wheel |

Different reels may use common paper craftsmanship, masks, physics and slot virtualization. **Five windows is a visual brand geometry, not a requirement for all selectors**; never render five fictitious repeated categories to fill it.

## 3. When two reels genuinely help

### Candidate A: collection → photo (recommended exploration)

**Task:** “I want to browse the photos in my Forests, Oceans and Mountains collections without returning to a directory each time.”  
**Parent, smaller reel:** named collections `CollectionId`, selected by a stable title/counter.  
**Child, larger reel:** images belonging to the selected collection.  
**Causal relationship:** turning parent changes the child reel’s membership and resets or restores focus for that collection, **but does not apply a wallpaper or activate a rotation preset**. Turning child changes hero preview only.  
**Layout:** on a compact portrait screen the *smaller parent reel is a partial arc at upper-right or side*, accompanied by an obvious **Change collection** control; the larger photo reel is cropped along a different edge at bottom-left, creating asymmetric counterweight around the hero image. At 200% font or small usable height, collapse parent reel into a labelled collection selector; preserve full child controls. Tablet: two offset reel viewports with a visible “Collection → Photograph” relationship and distinct scales.  
**Failure:** empty collection: child shows empty paper windows + Add photos. Deleted/permission-lost collection: keep previous choice and explain.  
**Risk:** simultaneous kinetic movement, visually tangled photo covers, accidental parent changes. Exactly one active pointer target at a time; parent selection synchronously cancels child settle and announces reassignment.
**Decision:** prototype against simpler collection dropdown/chips + one photo reel. Do not assume dual wins because it is aesthetically appealing.

### Candidate B: Home versus Lock (explore, not default)

**Task:** “Use one photo on Home and a different one on Lock; adjust them independently or deliberately match them.”  
Two *destination-labeled* reels can communicate paired visual selections if the user repeatedly compares both, with corresponding **Home** and **Lock** previews. Clear controls **Apply Home**, **Apply Lock**, **Apply both**, **Link choices**, and actual applied statuses. Changes to either reel preview do not touch device wallpaper until committed. Android/OEM capability gating may disable a destination; explain.  
**Small phone:** do *not* squeeze two giant full reels into a viewport. Show Home larger and Lock as a small, partly visible reel on opposite side, each backed by large labeled destination tabs; switching active destination changes which reel gets the large interactive surface. **Landscape/tablet:** side-by-side asymmetry, independent virtualized reels, unambiguous independent focus and action row.  
**Risk:** users may think two reels select collections when they actually select images. Titles/counters must say “Home wallpaper” and “Lock wallpaper”; two full UI physics loops doubling texture use can harm performance. Limit active animation to the engaged reel; cache images for active only and neighbor hero across other.
**Decision:** conditional advanced *Destinations* editor mode, not permanent homepage ornament.

### Candidate C: selected photograph → alternate compositions (explore)

One photo/collection reel chooses the actual source asset; a **smaller recipe reel** chooses a *small finite set of previewable crop/effect variants*. It is meaningful because both selections are visual. Never use it to continuously dial saturation or alter all low-level settings.  
**Risk:** selected crop and selected source ambiguous; include badges **Photo** / **Crop idea**, source filename or accessible title, and an explicit **Save crop** outcome. Slider/manual crop remains primary for precision.  
**Decision:** exploratory only, after W51/W58 basics work.

### Candidate D: primary / secondary simultaneous collection (possible alternative)

When making a mixed collection or weighted schedule, two reels might show the two **included photo pools** with visual covers. However the critical operations are **weight, precedence, inclusion and rights**, not spinning discs. Prefer two labelled collection cards with preview reels attached, plus numeric or segmented weight controls. Never turn a decorative reel into a percent knob.

## 4. Composition rules for asymmetry

- Visual balance **not symmetry**: one dominant interactive reel, optional one smaller subordinate reel, separate centers and distinct arc positions. A visually balanced arrangement can use diagonally opposing crops, ample negative space and a stationary hero.
- **Purpose hierarchy:** Hero image remains largest semantic focal point for photo selection. Secondary reel is identifiable by *label and selected name*, not just differing circumference.
- **Minimum visible affordance:** enough paper plus one near-complete window and a partial neighbor to signal direction, without relying only on tiny pointer wedges. The portion visible must contain a genuine, reliable drag zone; the action region must not cross top system gestures or bottom navigation.
- **No overlapping interactive circles.** Clip and hit-test separate bounded regions; if two arcs visually overlap, only one may own that area and the layers must make it obvious. Prefer whitespace separation.
- **Stable pointer and single focus:** each reel has one unambiguous focal marker and stable selected label; multiple pointers may be in different places **only when both represent different domain objects**.
- **Responsive, not scaled screenshot:** phone portrait prioritizes hero + one active reel. Compact/200% text transforms secondary reel to chip/list, rather than shrinking typography or hit targets. On tablet/tall portrait dual is possible if measured layout fits. Landscape can dock large reel to one side and small reel at opposite corner.
- **Material unity, functional distinction:** same paper texture/tone, different geometry scale and clearly named roles; not arbitrary accent colours for role unless accessible.
- **Do not claim tactile depth through expensive constant blur/shadows.** Cache stable paper/rim and use source photo windows; animated motion should be purposeful and interruptible.
- **No perpetual carousel autoplay.** A reel changes only when user acts or a clearly disclosed passive state is genuinely updated; system wallpaper changes elsewhere should not spin an open selector.
- **No fabricated seamless collection size.** End-of-list behavior and loop/shuffle mode explicit; visible count always true.

## 5. One glance sufficiency test

A first-time person should identify within a short look:
1. What is currently applied as wallpaper?
2. What image or collection is merely selected for preview?
3. Which reel does what?
4. How to go forward **and backward**, including without a gesture?
5. How to find a specific item among hundreds?
6. Whether tapping a window saves, selects, queues or applies.
7. How to get out, pause, undo, or recover a mistaken action.

If those cannot be answered by the app's actual labels/feedback, the reel has failed *regardless of visual loveliness*.

## 6. Mobile accessibility and fatigue

A wheel asks for circular/tangential manipulation. Ensure standard horizontal swipe semantics or a clear button alternative; motor-impaired users should not need circular motion, velocity, precise pointer capture or long drag. Compose semantics should expose stable collection/image names, counts and custom actions where warranted. Avoid pathological long wheel traversal. A 1,000-image collection requires Grid search/jump and position picker. Wheel should never be the only route to anything important. Compare use with one hand, large font, high contrast, TalkBack, external keyboard, switch access, reduced motion, and smaller phones. Each wheel may have independent focus, but reading order should follow domain relationship (Collection before Photo).

## 7. Comparison plan before deciding multi-reel layouts

Keep exact image fixtures and domain states constant and compare:
- **Baseline B0:** collection picker + large photo reel, full Grid.
- **B1:** small collection reel + large photo reel (asymmetric).
- **B2:** two destination reels in **Destinations** mode versus simple Home/Lock tabs.
- **B3:** single-photo inspector + crop suggestions reel versus standard crop presets.

Human tasks: navigate Forests→Oceans and pick image 17; find a known photo in 1,000 items; preview one image without applying; set Lock only; use paired photos for Home/Lock; switch to source grid; undo mistaken selection; operate reduced-motion/large-text.

Observe initial expectation **before teaching**: meaning of each reel, predicted action outcome, mistaken apply assumptions, first action, corrections, perceived delight, effort, and reach. Record qualitative owner responses without invented statistical rates. **Reject dual reels if worse at comprehension, task completion or visual priority even if the composition looks impressive.**

## 8. Priority audit findings

| Priority | Problem / correction | Owner |
|---|---|---|
| P0 | Define every reel as a selector of **one typed domain** and explicit state transition; reject generic setting wheels | Reel UX contract |
| P0 | Collection screenshot missing Previous; ambiguous Next/Set now; real bottom controls may overlap clipped disk | Collection screen specification |
| P0 | Home crescent has no interaction purpose; either Open collection action or non-interactive cover | Home |
| P0 | Distinguish Preview/Apply/Queue/Activate rule as separate visual states, labels and confirmations | Cross-screen state model |
| P0 | Findability: Grid/list/search/jump exists outside sequential reel | Collections |
| P0 | Reference thumbnails, photo rights, real state fixtures, edge-state layouts and user-visible semantics missing | Visual reference package |
| P1 | Experiment with hierarchical **Collection + Photo dual reels** and **Home + Lock** paired reels using asymmetry | Design prototype only |
| P1 | Source discovery cards need identities/licence and actions; new collection action misplaced | Discover |
| P1 | Cover/splash SVG and full photo reel art need provenance and approval classification | Art assets |
| P2 | Crop variant reel and recent-history reel, conditioned on actual demonstrated task improvement | Image editor / Activity |

## 9. Research and precedents

- [NN/g Mobile Carousels](https://www.nngroup.com/articles/mobile-carousels/): sequential access and discoverability weaknesses; partial-item continuation is a useful signifier, but not a search mechanism.
- [NN/g Effective Carousels](https://www.nngroup.com/articles/designing-effective-carousels/): clear navigation, content meaning and alternate access.
- [Android Compose semantics](https://developer.android.com/develop/ui/compose/accessibility/semantics): custom actions and semantic alternatives to complex drag gestures.
- [Android Compose minimum touch targets](https://developer.android.com/develop/ui/compose/accessibility/api-defaults): accessible hit sizing.
- [Nielsen Norman Group cognitive walkthroughs](https://www.nngroup.com/articles/cognitive-walkthroughs/): four questions for notice/intention/association/feedback.
- Cross-project design contracts: [ROYGBIV canonical plate](https://github.com/gamesbyian/wallgen/blob/main/docs/ui-reference/canonical-screen-contract.json), [Ring Road source image protocol](https://github.com/gamesbyian/Ring-Road/blob/main/docs/sparse-reference-visual-verification.md).

**Not approved by this audit:** second live reel on Home, reel-per-setting, auto-activation from reel selection, rebranding an exact interval control as a reel, arbitrary nested wheels, endless simulated spinning.
