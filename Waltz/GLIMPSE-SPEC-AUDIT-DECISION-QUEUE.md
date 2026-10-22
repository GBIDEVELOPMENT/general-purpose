# Glimpse: specification audit decisions and next-work queue

**Current: 2026-10-22. Owner: Glimpse design/engineering planning.** All status statements reflect document/source inspection only; **no Android app or new prototype has been built**. Keep this short queue alongside [current decisions](GLIMPSE-CURRENT-DECISIONS.md). This queue is the operational action list for the two full audits and is not a second full product spec.

## Resolution statuses

**Specified:** documented unambiguously enough to design/prototype later; does not imply working.  
**Proposed:** pending targeted user design comparison; don't promote as approved.  
**Platform-gated:** cannot guarantee without a documented Android/OEM/source proof.  
**Asset-gated:** actual canonical high-fidelity artwork still needs publication/version control.  
**Historical:** superseded guidance preserved for provenance; not a competing authority.

## P0: stop future agents implementing contradictory or decorative behavior

| ID | State | Decision / deliverable | Acceptance / handoff |
|---|---|---|---|
| S01 | **Specified** | Glimpse brand, current file authority, legacy Waltz meaning and UI glossary | [Current decisions](GLIMPSE-CURRENT-DECISIONS.md) and [technical contracts](GLIMPSE-TECHNICAL-BEHAVIOR-CONTRACTS.md) linked from README |
| S02 | **Specified** | All **W01–W70 and F071–F073** categorized with concrete feature approach, UI result and proof limitations | [73-row register](GLIMPSE-FEATURE-SPEC-COMPLETENESS-AUDIT.md); no gaps/duplicates |
| S03 | **Specified** | Selected browse photo, queued photo, applied/acknowledged wallpaper, eligible schedule and share variant are independent | Typed command side-effect matrix; JSON screen contract |
| S04 | **Specified** | A reel must select a finite, typed set; five paper apertures are a **view**, not fake content count | [Reel critical audit](GLIMPSE-REEL-UX-CRITICAL-AUDIT.md) |
| S05 | **Specified** | Complete screen inventory and human-job rationale from Home through sharing/settings | [UI census](GLIMPSE-UI-SURFACE-CENSUS.md) |
| S06 | **Specified** | Motion from **first native reel** rather than M4 afterthought | Native architecture note reconciled with motion contract |
| S07 | **Asset-gated** | Publish full v4 *editable source ZIP*, deck PPTX and corresponding PDFs on GitHub with validated Git blobs | [Asset plan](GLIMPSE-ASSET-PUBLICATION-PLAN.md) and [issue #28](https://github.com/gamesbyian/general-purpose/issues/28); tactile board PNG **already verified** |
| S08 | **Proposed** | Give *exact* visual approval to icon/hero/reel reference art, not entire mock screen | Record chosen source SHA(s), role and viewport; mark untouched old art historical |
| S09 | **Proposed** | Remake v4 Collection screen: Previous/Next photo, Set as wallpaper destination, Grid and non-overlapping reel | Prototype three edge states and 200%-font case before new deck is asserted |
| S10 | **Proposed** | Define explicit action or passive identity for Home reel crescent | Test discoverability and choose open-active-collection or noninteractive illustration |
| S11 | **Proposed** | Clarify Grid “3 selected” and “Add to rotation” meaning | Visual markers and side-effect copy tied to `QueueNext`/`ActivateCollection` |
| S12 | **Proposed** | Discover cards must identify sources/assets/rights instead of unlabeled pretty pictures | Prototype rights and import action visibility |

## P1: evaluate actual multiple-reel opportunities

| ID | State | Compare | Acceptance |
|---|---|---|---|
| R01 | **Proposed** | **Small Collection reel + large Photo reel**, asymmetric, against picker+photo reel | First-click goal and selected-ID correctness, avoid accidental schedule start |
| R02 | **Proposed** | **Home/Lock paired reels**, mainly wide layouts, against destination tabs+one wheel | Clear independent results, target capability gate and no compact-phone crowding |
| R03 | **Proposed** | Crop-variant mini reel against crop preset cards, only if visual choices are finite | Identity of source vs recipe; reversible and non-destructive |
| R04 | **Proposed** | Recent-history reel against chronological list | Timestamps, restore outcome and diagnostic truth remain visible |
| R05 | **Specified rejection** | Numeric/time/boolean/permission/rule-priority reel | Use native semantic controls; no rotating setting dollhouse |
| R06 | **Specified** | Responsive role for each disc | At most one fully interactive large reel on compact phone; secondary collapses to named chooser; tablet can show two if measured |
| R07 | **Specified** | Reduced-motion/keyboard/TalkBack mechanism for any reel | Fixed semantic actions, no gesture-only selection; do not rotate just because automatic wallpaper changes |
| R08 | **Specified** | No same-frame slot rebinding while visible | Stable IDs, cached masks, prefetch, hidden-slot rebinding and no phantom content |
| R09 | **Proposed** | Asymmetric layout with two distinct non-overlapping clip/hit zones | Hero remains focal, 48dp+ controls, no interference with system bars |

## P1 platform feasibility before making user promises

| ID | Status | Proof required, not a guarantee |
|---|---|---|
| P01 | **Platform-gated** | Native five-minute active-use timing under Doze/screen states; actual vs eligible stats |
| P02 | **Platform-gated** | Real `WallpaperManager` Home/Lock/Both behavior and unknown externally changed wallpaper |
| P03 | **Platform-gated** | Cloud-backed Photo Picker imports and verified offline copies; whole-album sync not assumed |
| P04 | **Platform-gated** | W11/W13/W14/W19/W22/W27/W28/W29/W69 event/display/colour/profile limitations |
| P05 | **Platform-gated** | Provider licences and policy for Commons, Openverse, NASA APOD, other adapters |
| P06 | **Platform-gated** | Source-free share capability and actual Android target availability, no fake Lens API |
| P07 | **Platform-gated** | Desktop/emulator vs real Pixel GPU reel behavior, gestures, memory and actual frame traces |
| P08 | **Pending owner/technical** | Permanent application ID, distribution signing custody, license choice before first APK |

## Suggested evidence-efficient design work, **without app building**

1. **Canonical art promotion:** after binary GitHub publication, create a small reference manifest that marks exact assets as “approved direction,” “candidate” or “historical,” with hashes. A visual *direction* approval is not pixel approval.
2. **Three layout comparison sheets:** one-reel baseline; asymmetric Collection→Photo; target-separated Home/Lock. Maintain same fixture photos/counts to avoid misattributing preference to imagery.
3. **Microcopy and state plates:** Home applied/unknown/paused; Collection selected/not applied, Grid multi-select; Import Save/Queue/Apply; schedule simulated/not guaranteed.
4. **Human-expectation checkpoint:** small owner trial testing tasks W01, W54, W57, W60 and F071/F073. Agent first-click guesses are not observations.
5. **Technical readiness:** decide direct native component/fixture mappings and hardware proof plan before code. Avoid huge automatic CI suites and invented benchmark passes.

## Closure rule

An audit document is complete when it records the *expected state and honest fallback*, not when an AI declares every ambitious feature feasible. An implementation phase can begin only on an explicitly scoped user request; this audit authorizes **no app construction**. Update this queue when concrete proof or owner visual decisions exist, preserving older reasoning in Git history rather than stacking additional conflicting status paragraphs.
