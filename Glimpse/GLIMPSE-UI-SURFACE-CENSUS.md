# Glimpse UI surface census and reverse-navigation audit

**2026-10-22 | Planning-only, adversarial inspection.** References: `Glimpse_v4_Editable_Source_Archive.zip` current image files (concept screenshots), old Waltz 16-screen gallery (historical), [feature completeness](GLIMPSE-FEATURE-SPEC-COMPLETENESS-AUDIT.md), [reel critique](GLIMPSE-REEL-UX-CRITICAL-AUDIT.md), [human expectations](GLIMPSE-HUMAN-EXPECTATIONS-WALKTHROUGHS.md).

## Navigation is not the same as action ownership

The proposed four top-level destinations remain sound *pending task testing*: **Home**, **Discover**, **Collections**, **Automation**. Other surfaces are contextual, not extra permanent tabs: current image detail, reel, Grid, Crop/Edit, Home/Lock destinations, Quick Import, Share/Export, rule studio, Activity/Diagnostics, Sources, Settings, Backup and accessibility.

For every screen the first question is *what job brought the person here?*, not “where should another reel fit?” Every action must either complete the current job or lead to an explicitly named neighboring job. Returning via Back restores focus, not silently reruns a command.

## Complete surface-by-surface critique and rationale

| Screen / flow | Human job and required visual hierarchy | Reel disposition | First-class controls and states to demonstrate |
|---|---|---|---|
| **Home** | See actual applied wallpaper and whether rotation works. Image dominates, status immediately under image, controls close to thumb. | Small reel crescent **only if** opens current collection; otherwise decorative clearly noninteractable or remove | Change wallpaper, Pause, Share, current target(s), last acknowledged outcome, next eligible, override, error/unknown and Activity |
| **Collections list** | Locate named collection, size, active status, sort/reorder/create. | Artwork-filled paper reels as **collection covers**; tap cover opens collection. Optional collection-selector reel in a focused browse mode, not default navigation | Add photos, New collection, search, filter, rename, duplicate/mix, collection storage and sources |
| **Collection detail** | Enjoy/inspect a photo, browse nearby items, set or share selected picture. | **Primary large clipped photo reel** + stationary hero. Candidate small **parent collection reel** for switching sibling collections | Previous/Next photo, selected index, true count, View all, Set as wallpaper (target), Share, Details, Edit, Hide, empty/end/reorder |
| **View all / Grid** | Find known item, pick multiple, exclude, move, sort, filter. | No prominent wheel; return to reel via clear control preserving selected image ID | Search/jump, selected badges, multi-select mode, Add to rotation explicitly target/queue meaning, export/share, remove/hide, cancel |
| **Discover** | Find credible sources and licensable photographs. Differentiation, rights and search before delight. | **Conditional small curated photo reel** for a related set; avoid giant reel for provider directory | Provider/source identity, search/filters, license/creator, add to collection, report/offline/failure and limits |
| **Source detail** | Understand provider, provenance, rights and download/select consequences | Optional finite photo preview reel *only for curated sets* | Search/next page, source health, creator/attribution, import, network limits, original URL, opt-in permissions |
| **Photo inspect/detail** | See image metadata, destination crops, inclusion and operations | Photo variant mini-reel candidate if real related recipe choices exist | Set Home/Lock/Both, crop/edit, share, provenance/credit, hide/unhide, member collections |
| **Quick screenshot intake** | Fast capture from Android Share, rotate/crop and choose outcome | **No wheel by default**. One photo plus three explicit actions is faster | Crop/rotate, target collection, Just save, Show next, Use now, back/cancel, source URI errors |
| **Crop and composition editor** | Precisely adjust framing, home/lock, safe areas and non-destructive effects | Normal crop canvas and numeric controls. Optional crop-variation reel *only for a few visual proposals* | Move/zoom/rotate, reset, Undo, Home/Lock crop, blurred extension, compare, Apply/save/export distinction |
| **Home/Lock destinations** | Compare which wallpapers will be shown on the two Android surfaces | **Dual reel candidate** on wider devices; phone one active reel plus smaller counterpart/tab | Per-target selected/applied status, apply to one/both, linked vs independent crops, unsupported-target explanation |
| **Rotation quick-start** | Start simplest available shuffle quickly after import | **No reel for interval/target values**; collection cover can be clicked | Collection, destination, interval/eligibility, shuffle/no-repeat, Start, summary of OS limits |
| **Automation overview** | See whether rules/overrides are active; find why and next | No general reels; timeline/list conveys time and priority better | Active preset, pause/hold, rules list, priorities, overrides, next eligible, preview future, failures |
| **Rules editor** | Express conditions and precedence without confusion | **No reel** for boolean, logic, priority or time; typed controls | Trigger, sources, destination, precedence, preconditions, conflicts, optional nested expressions, Save/Activate |
| **Schedule simulator** | See hypothetical future output without changing wallpaper | Possibly a small **photo history/forecast reel**, clearly “Simulation”; a filmstrip/list usually better for time ordering | Simulate date/time/context, why image chosen, assumptions, no actual apply, validation |
| **Activity / History** | Recover previous photo, inspect attempted/applied/failed events | Small recent-photo reel conditional; list is authoritative for timestamps/errors | Applied/skipped/unknown statuses, reapply/Undo, events by destination, event details and privacy |
| **Diagnostics** | Discover why rotation failed and how to fix it | No reel; meaningful status, dates, codes and remedies | Last attempted/applied, permission missing, battery restrictions, storage/source errors, retry, export redacted report |
| **Widgets** | Perform one or two actions from launcher | Maybe static tiny reel icon/collection cover, **not a finger-wheel** | Current/Next + Change now/Pause; user action returns verified status |
| **Quick Settings / shortcuts** | Immediate trusted commands outside app | Icon silhouette only | Specific target, result and error, no ambiguous unlabeled “Next” |
| **Settings / permissions** | Configure privacy/storage/theme/source policy | **No reels** | Permissions/capabilities, storage, network, motion, notifications, privacy, export, device compatibility |
| **Backup/restore** | Save recoverable data and reconnect images | No reels | Preview included/excluded photos and secrets, encryption, restore conflict/remap, verification |
| **Onboarding** | Start useful behavior without reading the full app | Animated paper reel may show *what browsing means*, but stop once instruction delivered | Add photos, privacy/no cloud, Home target, cadence with truthful limits, preview result, Skip |
| **Empty/errors/permissions** | Understand what cannot happen and how to resume safely | Wheel may show blank apertures but cannot conceal necessary text/actions | Actionable failure state, retry/repair, no phantom photos, offline and low storage fallback |
| **Accessibility preferences** | Operate everything without sight, small targets, rapid motion or precise gestures | No special reel-only settings; equivalent navigation everywhere | TalkBack/keyboard/switch, motion/contrast/font scale, announcement of states and actions |

## Specific screen-art defects to resolve when next deck is revised

**`screen-grid.png`:** reads “50 photos · 3 selected” but the three selected photos are not visually identified in the raster. The bottom button “Add to rotation” does not say whether selected photos form an override queue, enter the active collection, or immediately replace wallpaper. Require selection marks, cancellation and explicit consequence.

**`screen-collection.png`:** navigation order is “Next / Set now / Grid”; no Previous photo, target choice, or clearly attached reel hit region. The reel's focal pointer should be singular. Hero photo at top competes with huge cut-off paper lower down; budget action bars and system insets before decorating.

**`screen-home.png`:** visual Home disc at lower right has no visible label/semantics. “Next” is ambiguous; “Eligible in about 3 min” needs target and mechanism; pause status and applied verification uncertain. No clear Share, Recent/Undo or destination separation.

**`screen-browse.png` (actually Discover):** three photo cards do not show provider/collection/image type, rights, attribution or action. “New collection” CTA belongs in Collections unless the intended interaction is expressly importing a discovery into a new collection. Placeholder system glyphs are not acceptable production icons.

### Do not treat historic 16-screen deck as hidden approval

Older Waltz art covers Today, Sources, Rules Studio, Composition, Widgets, etc. Its structure helps identify absent surfaces, but its typography, old nav names, card groupings and visual effects are now **exploratory ancestry**, not a reason to retrofit Glimpse's paper reels into every old card. New reference artworks need one current rationale per surface.

## A clearer visual grammar

- **Photograph:** rectangular, undistorted hero, largest visual subject. Use genuine representative assets, not fake repetitions.
- **Paper reel:** coherent sequential visual selection; fixed marker plus clear count; cropped beyond a bounded viewport.
- **Cards/sheets:** reversible settings and rules editing; not fake cartridges or reels.
- **Typography:** collection/image name and result verb near the object it affects; important status never inside a rotating/photo texture.
- **Accent:** coral focal marker, deep teal applied-state action, cream paper, other palette restrained and checked for contrast.
- **Asymmetry:** varying arc positions and scale **only when it clarifies which selector is primary and which is subordinate**. A second disc just to visually balance a page is usually a design mistake.
- **Motion:** primarily a property of user intention. Automatic wallpaper changes elsewhere update Home state, do not continually rotate an open browser reel.
- **Escape:** View all/Grid, Back, labels, regular list and large touch targets exist at all times when appropriate.

## Reverse trace: what should each prominent element mean?

| Visual element | Must map backwards to | Or remove/relabel |
|---|---|---|
| Five paper apertures | Bounded real set of nearby `ImageAssetId` (or labeled `CollectionId` covers) | If static art, mark noninteractive |
| Red triangular index | Exactly one focused ID and position/count | No purely decorative duplicate pointer |
| Home crescent | Open active collection or valid nearby-image selector | If no action, never make it look draggable |
| “Next” control | Either `SelectBrowseAsset(next)` or `ChangeNow(target)`, **never both** | Rename Next photo / Change wallpaper |
| Grid selected count | Exact set of selected IDs with visible per-tile marks | Do not show fabricated 3 selected state |
| “Add to rotation” | Explicit queue/override/membership edit with destination and duration | Use Show next / Use for one hour / Add to collection |
| Discover image card | Source/provider, asset identity, attribution/rights and open/import affordance | Do not mislabel as a collection |
| Two reels on one page | Two independent typed selectors with a causal relationship | Replace secondary wheel with label/chip/list if not helpful |
| Settings toggle | Stored setting/permission, enabled/disabled feedback | Standard Material control, never photo wheel |
| Status pill | Proven state: applied/eligible/failed/unknown | Never infer success from a timer or preview |

## Evaluation: fast and skeptical

Before UI implementation, perform only a few reference/prototype comparisons: (1) current one-reel detail vs parent/child dual; (2) paired Home/Lock reels vs destination tabs; (3) 1/3/50/1,000 photo states; (4) reduced motion/200% text; (5) quick tasks where a wheel would be slow. Ask predictions before teaching. Keep full app tests scoped. **No visual signoff, human usability metric, or device performance is claimed here.**
