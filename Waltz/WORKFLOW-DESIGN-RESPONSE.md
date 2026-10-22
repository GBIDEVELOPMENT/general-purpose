# Architecture and UX answer to the 70 human workflows

## Core design question
How can Waltz support idiosyncratic, nested, conditional and conflicting desires while making W01 (rainbow photo import, five-minute random rotation) trivial?

**Solution: one composable internal rules system, four visible levels.** Basic usage creates that system's records automatically rather than confronting people with it.

1. **Actions:** Next, Pause, Undo, Pin, Hide, Add Photos. One-tap Today, widget, Tile, share sheet.
2. **Rhythms:** Use as wallpaper → Home/Lock → shuffle/order → every N minutes / on unlock / daily → Start. Default path for most users, editable in collection detail.
3. **Scenes:** named sets of collections, presentation settings, destinations, and timing ("Workdays", "Rainbows", "Travel"), with clear temporary overrides and preview.
4. **Rules:** guided, conditional **When / If / Use / Where / Unless / Otherwise** authoring. Only appear when people ask for exceptions or combinations. Always render natural-language description and simulator.

## Typed, composable domain model
**Asset** (canonical identity, source rights, hashes, original-grant and optional verified offline copy), **Collection** (manual or smart set, nested *DAG* of collection references), **Scene** (source selection, weights and presentation), **Rule** (versioned trigger + Boolean conditions + priority + destination + cooldown + failure policy), **Presentation** (per image/destination crop, effect overrides and safety ceiling), **ShuffleState** (persistent selection bag, quotas, recent history), **DeliveryEvent** (idempotency key, selection explanation, preparation, per-destination application), **Policy** (battery, privacy, permissions, reduced motion, network, OEM capability).

Nested collection membership and scenes use a directed acyclic graph; reject cycles visibly with a breadcrumb such as "Nature → Forests → Nature would make a loop." Limit nesting by tested performance and candidate quotas. A rule must not recursively trigger itself through wallpaper change broadcasts; all reactions are bounded and debounced. Exclusions and tombstones survive folder rescans.

## Deterministic selection/delivery pipeline
1. Establish current device state and user-initiated actions, pins, and per-destination Pause.
2. Apply hard safety, rights, accessibility, network and permission gates before choosing an image.
3. Evaluate eligible rules and subconditions with one pure function; no unsafe hidden background polling.
4. Resolve each destination: manual/pin overrides > explicitly prioritized scenes > ordinary schedules > fallback. Stable tiebreaker and a visible loser explanation.
5. Evaluate nested collection DAG and mixed strategies: shuffle bag, sequential, weighted-fair 70/30, alternating categories, every-N special, cross-collection identity dedup and 14-day cooldowns. Bound attempts and show what constraints excluded everything.
6. Reserve eligible candidate durably, prepare bounded image, validate and apply via serialized WallpaperManager or optional live engine. Independent Home/Lock outcomes recorded.
7. Commit success and advance history/shuffle only after platform completion; detect unknown/partial results on restart. Never swap to black or hidden generic art as error fallback.
8. If remote provider fails, use prepared approved offline fallback or keep current wallpaper, with bounded backoff and one actionable status.

## Specific UX patterns tied to workflow IDs
- **Imports / reimports (W01–W10):** native Photo Picker, explicit snapshot vs connected-folder vs remote-source semantics, resumable downloads, progressive import count, duplicate review, temporary subset, Combine collections. Never silently delete originals.
- **Time / conditions (W11–W20):** choice chips with plain-English operational semantics; exception chips and previews, no phantom exact alarms; time-zone and DST simulator; three types of Pause (global, destination, temporary) visibly distinct.
- **Home / lock / presentation (W21–W30):** paired previews, independently linkable crops, theme variants, safe-area overlays, OEM capability detection, accessibility-first visual policies and reduced motion.
- **Online sources (W31–W40):** vetted API/rights registry; provenance alongside each image; optional explicit Wi-Fi-only and review-before-use; provider health, fallback simulation and no Waltz-operated cloud or accounts.
- **Nested composition (W41–W50):** Combine as a visual operation, include/exclude/weights, scene chains as DAG, shuffle fairness, conflict explanation and deterministic representative examples. Visual rule-builder supports AND/OR grouping with text summary, not a generic programming language.
- **Quality and editing (W51–W60):** non-destructive crop profiles and overrides; instant Hide, Pin until, Undo, upcoming preview and history. Informational resolution warnings, never silently change the image's ownership or files.
- **Android and accessibility (W61–W70):** widgets, Quick Settings, secure explicit intents to Tasker/MacroDroid, OS sharesheet, local encrypted optional backup, per-profile honesty, TalkBack/large text/keyboard parity, one-tap "Why did it not change?" diagnostics.

## UX navigation
**Today** contains active Home/Lock images, current collection/scene, Next/Pause/Pin, last applied, next eligible, "Why?" and failure recovery.
**Collections** provides New/Add/Combine/Filters. Detail exposes large **Use as wallpaper**, a visible schedule summary and "Add a condition" as progressively advanced action.
**Explore** shows sources with rights and maintenance health, approve/disallow controls and offline fallback.
**Rules** shows readable timelines, precedence and optional advanced editor with When/If/Use/Where/Unless/Otherwise and "Preview tomorrow".
**Settings > Controls** previews add-widget, request Tile, create Shortcut, configure secure automation; don't claim Android confirmed an installation before it does.

## Prioritized slices and acceptance
**P0:** Android Picker/Google Photos supported selection, verified local copies, safe imports, collection details, static home/lock delivery, persisted no-repeat shuffle and five-minute *active-use* eligibility. Tests A001–A015. User never enters rule editor.
**P1:** multiple collections, external shares, watched folders, exclusions, pin/undo, scenes, deterministic rules, battery/time/theme triggers, accessible simulator, widgets/Tiles/shortcuts/Tasker, backup, diagnostics.
**P2:** vetted Wikimedia/Openverse/other policy-approved sources with source health and rights, nested collection DAG, weighted compositions and robust remote cache.
**P3:** smart focal-point crop, dynamic colour policy and optional WallpaperService animation with OEM acceptance matrix. Never compromise P0 reliability for live effects.

**Measurable gates:** 9/10 uncoached users complete W01; 100% A001–A015 tests on device matrix; no duplicate per shuffle cycle; 70 workflow fixtures each tagged supported/conditional/unavailable-with-explanation; model-based property tests for cyclic references and priority resolution; no unauthorized network in offline-only mode; accessibility parity for all primary and advanced flows; observed battery/runtime performance under Doze and manufacturer restrictions documented instead of guessed.

## Platform/rights caveats
Android Photo Picker may include Google Photos cloud media, but no guaranteed whole-album bulk selection or unattended continuous album sync. WorkManager periodic min 15 minutes; a five-minute option needs an Android-compliant *active-use* event scheduling path with disclosed deferrals, not false precision. APIs and home/lock behavior are conditional on actual platform/OEM capability. Remote image providers require ongoing legal policy review and explicit attribution; prohibit Unsplash/Pexels wallpaper competitors absent separate permission.

**Verification references:** https://developer.android.com/training/data-storage/shared/photopicker ; https://android-developers.googleblog.com/2024/02/cloud-photos-now-available-in-android-photo-picker.html ; https://developer.android.com/reference/android/app/WallpaperManager ; https://developer.android.com/topic/libraries/architecture/workmanager/how-to/define-work#schedule_periodic_work
