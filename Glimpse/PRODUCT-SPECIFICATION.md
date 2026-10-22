> **CURRENT GLIMPSE READING RULE (2026-10-22).** This historical document remains the long-form feature source, but its Waltz title, Today/Rhythms/Scenes/Rules navigation, generic “Next” action, early release-sprint visual-polish ordering and high-confidence descriptions of OS-dependent features are **not current UI or platform authority**. For all **73** scenarios and testability, read [feature completeness](GLIMPSE-FEATURE-SPEC-COMPLETENESS-AUDIT.md), [technical behavior contracts](GLIMPSE-TECHNICAL-BEHAVIOR-CONTRACTS.md), [reel critique](GLIMPSE-REEL-UX-CRITICAL-AUDIT.md) and [screen census](GLIMPSE-UI-SURFACE-CENSUS.md). Approved visual *direction* is not proof that the specific v4 screenshots are accepted. Motion/rendering must be designed in M0/R0, **not postponed to a final polish phase**. W08, W11, W13, W19, W22, W27, W29 and W69 are explicitly platform/provider-gated rather than promised universal implementations. No Android app code yet.

STATUS: design proposal, not a functioning application. Imagery in screen concepts was generated specifically for the proposal. It is not a bundled wallpaper library, and screenshots depict intended interactions rather than implemented behavior.

# WALTZ: complete product specification

Working title; concept only. 21 October 2026.


## 1. Executive product thesis

Waltz is an open-source, local-first Android application that composes the user’s own folders and carefully vetted third-party image sources into reliable, explainable wallpaper schedules. Its ambition is to feel as considered as an excellent native first-party app while exposing the expressiveness of a serious automation system.

Its essential loop is Discover → Collect → Compose → Automate → Understand. People should be able to set one folder to rotate daily in under a minute, or construct sophisticated source, condition and destination rules without the interface collapsing into a wall of toggles.


### Hard product boundaries

- No Waltz-hosted image library, remote account, sync service, social feed, recommendation backend or subscription. Third-party sources remain external and are accessed directly from the device with lawful documented APIs.

- No forced analytics or advertising. No image uploads, identity profiling, device fingerprinting or off-device logs. Opt-in bug-report export is scrubbed and user-reviewed.

- No claim of exact background scheduling where Android does not promise it. The interface distinguishes elapsed timers, eligible windows, wake-triggered requests and actual completed changes.

- No privileged service, broad all-files access, accessibility-service surveillance, root or Shizuku dependency in the default experience. Advanced modes require explicit disclosure and are optional.

- No promise that static and live wallpapers can be manipulated independently on every OEM. Capability probing and honest fallbacks take precedence over deceptive toggles.


### Who it serves


| Persona | Primary job | Successful outcome |
| --- | --- | --- |

| Set-and-forget owner | Choose a folder and change once a day | Configured in <60 seconds with visible next-change state |

| Collector | Manage thousands of local photos | Persistent deduped collections, tagging, rapid exclude/undo |

| Curator | Discover legal new imagery | Search source catalogues with metadata and attribution |

| Automator | Write context-aware scene rules | Inspectable priority resolution and reproducible triggers |

| Accessibility-first user | Operate independently | TalkBack, large text, keyboard, touch and reduced-motion parity |





## 2026-10-21 priority addendum: the Rainbow Contract

The first end-to-end golden path, A001, is: import individually selected, potentially cloud-backed rainbow images from Android Photo Picker/Google Photos into a named Rainbows collection; make offline-ready verified copies; choose Home, Shuffle without replacement, Every 5 minutes, Start. This MUST be achievable from Collections without opening Rules. Google Photos album browsing may be offered by the Android picker, but bulk-selecting an entire album, observing future album changes, and ongoing Google Photos synchronization must NOT be promised by the picker flow. Those require separate provider/platform feasibility, user authorization and policy review.

Import behavior: transparent selected/imported/duplicate/failed counts, estimated storage and metered-network disclosure; staged and resumable cloud downloads; source photo remains untouched; SHA-based exact dedup; integrity, MIME, pixel dimensions and image-bomb validation; cancellation-safe Room transactions; retry after network interruption. A completed imported collection works in airplane mode and after source URI grant revocation. No Google account credentials or broad device media permission is demanded for this flow.

Schedule behavior: "Every 5 minutes" is **active-use eligibility**, not a claim of exact wall-clock updates during deep sleep, Doze or OEM restrictions. Use platform-compliant scheduling and event/lifecycle coordination; no busy polling or covert background execution. Show last applied and next eligible time with honest caveats, and never silently catch up missed intervals by cycling multiple photos. WorkManager periodic intervals cannot satisfy a 5-minute exact period.

After Start: active collection, last successful apply, next eligible change, Next / Pause / Change timing / Why. No shuffle duplicate within a complete eligible cycle; near-duplicate recognition is advisory. Preserve valid current wallpaper on failure, log reason, do not double-advance after process death/reboot. Respect independent home/lock capability and explicit destination selection.

**Implementation priority correction:** the first shippable vertical slice includes Photo Picker multi-image import, private offline copies, 5-minute active-use shuffle, static wallpaper delivery and intelligible status. Advanced Rules are a progressive extension, not a prerequisite. The user-voiced requirement corpus is 70-HUMAN-WORKFLOWS.md; implementation/UX response is WORKFLOW-DESIGN-RESPONSE.md; acceptance cases A001-A015 are in RAINBOW-QUICKSTART-CONTRACT.md. Where the earlier Phase 2/3 schedule suggests otherwise, this addendum wins.


## 2. Product information architecture and user journeys

Primary navigation: Today, Explore, Collections, Rules. A persistent profile/settings destination is reachable from every top-level screen. Activity and Diagnostics are first-class destinations from Today and from contextual error details, rather than buried in developer settings.


| Screen / module | Purpose | Primary action |
| --- | --- | --- |

| Today | Current home/lock images, status, next event, skip/undo/pause | Surprise me now |

| Explore | Source directory, search, filters, rights and attribution | Add to collection |

| Collections | Local smart/manual lists, folders and shuffle controls | Create collection |

| Rules | Readable automation list, timeline and simulation | New rule |

| Compose | Image-specific preview/crop/effects with safe-area overlays | Save composition |

| Activity | Applied, skipped and failed events | Explain a change |

| Controls | Widgets, Quick Settings, shortcuts, automation | Install an action |

| Settings | Destinations, privacy, accessibility, backups, sources | Configure |




### Onboarding in four meaningful choices

1. Welcome: explain “nothing is uploaded; connect your own folder or supported source.” Provide Skip and demo with generated sample content that is visibly labelled and not a permanent library.

1. Choose one: system document tree, individually selected photos, Openverse, Wikimedia Commons or Wallhaven; permissions requested contextually, never on launch.

1. Preview first image on the actual display aspect ratio. Choose home, lock or both with device-specific capability explanation.

1. Choose a ready-made rhythm: every morning, daily during a flexible window, wake events in supported mode, or manual. Show expected semantics and finish with one safe wallpaper application.


### User flow invariants

- Any change of wallpaper has Undo (where the original bitmap can be safely retained), Skip, Hide this image, View source and Explain.

- A destructive action requires plain-language confirmation; removing an image from Waltz never deletes the user’s original file.

- Every advanced rule has a “plain English” summary and a future event simulator.

- Source/license details travel with the image through browsing, collections, history and exported metadata.

- No dead-end empty state: every empty screen offers the next meaningful action.


[Mock-up: Screen concept 01. Today provides current image, pending action and one-tap change., file: screens/01_today.png]


## 3. Visual and interaction design language

Personality: thoughtful, friendly and slightly playful. Waltz avoids the faux-technical wallpaper tools aesthetic: no endless wireframe gears, neon gradients or arbitrary particles. The visual delight comes from asymmetrical rounded compositions, warm colour relationships, restrained paper/ribbon motifs and exceptionally good photographs.


| Token | Proposal | Usage |
| --- | --- | --- |

| Ink | #223630 | Primary text on paper |

| Tidal teal | #196E6A | Primary action and active state |

| Apricot | #F17961 | Rare expressive CTA or accent |

| Butter | #FFD779 | Joyful secondary accent |

| Lavender | #D7CAFA | Rule categories and state chips |

| Paper | #F7F4EE | Primary background |

| Surface | #FFFDF9 | Cards and sheets |

| Focus ring | 2-3 dp visibly contrasting outline | Keyboard and assistive focus |



Typography: Inter Display or another properly licensed rounded-humanist display family for large headings; Inter for system controls and dense information. Final packaged fonts must be licensed and reviewed; Android system font fallback always supported. Sizes derive from scalable sp values. Do not force fixed height text containers.

Layout: compact top line, expressive headline, one primary action per screen, 4-dp spacing base, 16–24-dp corner radii, contextual bottom sheets, and bottom navigation with semantic labels. Keep primary controls within easy thumb range while preserving 48-dp or larger targets.

Motion: 180–260 ms interface navigation; 250–450 ms card transformations; 650–1000 ms optional wallpaper crossfades. The app follows operating-system animator scaling and accessibility reduced-motion preferences. Decorative animations stop when content is not visible. Every action provides immediate non-colour-only feedback.

Dark theme is individually designed with similarly accessible contrast, not merely inverted colours. Dynamic colour support is opt-in so the product retains coherent brand hierarchy; themed widgets align with the system where appropriate.


[Mock-up: Screen concept 13. Comfort and accessibility controls., file: screens/13_accessibility.png]


## 4. Sources, rights and local library


### Source eligibility contract

A source becomes a built-in adapter only after a documented API, lawful wallpaper use, reliability, metadata quality, image-resolution availability, privacy properties and attribution requirements pass review. Each adapter advertises capabilities; unavailable features are suppressed rather than emulated unreliably.


| Source | Launch tier | Allowed behaviour / gate |
| --- | --- | --- |

| Device folders & selected photos | Core / offline | ACTION_OPEN_DOCUMENT_TREE and persistable grants, file URI validation |

| Wikimedia Commons | Core | MediaWiki API; fetch imageinfo and extmetadata; preserve author/licence/URL |

| Openverse | Core | Open-licensed search index; verify upstream rights; obey rate and pagination rules |

| Wallhaven | Core or beta | Public SFW search plus optional BYO key for other permitted endpoints; 429 backoff |

| NASA APOD | Opt-in source | Image entries only; third-party copyrighted images subject to separate permission/rights review |

| RSS/Atom and user URLs | Phase 2 / guarded | HTTPS allowlist, content-type, rights disclosure, SSRF protections |

| Unsplash/Pexels | Excluded by default | Public API policies prohibit replica wallpaper applications without separate permission |

| Reddit/Bing | Research only | Policy/API instability or rights clearance before any connector release |



Openverse results can carry incorrect licence metadata; the product must never claim an image is legally verified solely because it appeared in search. Display “Licence reported by source; confirm on original page.” For Commons, preserve raw licence identifiers, creator, attribution text and file page URL. Avoid embedding external-provider SDK trackers.


### Source adapter interface

Adapter API (Kotlin): capabilities(), authenticate(config), search(query, filters, pageToken), getDetails(remoteId), streamOriginal(candidate), healthCheck(), revoke(). Expose stable SourceId, provider provenance, remote ETag/version, mime, dimensions, creator/licence URLs, media rights state, content warnings and attribution format. All requests pass through shared HTTP rate limits and sanitization.

Error taxonomy: NETWORK_OFFLINE, TIMEOUT, RATELIMIT_429, AUTH_401, FORBIDDEN_403, PROVIDER_5XX, MALFORMED_METADATA, UNSUPPORTED_MEDIA, RIGHTS_UNCLEAR, FILE_GONE, PERMISSION_REVOKED. A retriable failure must be distinguishable from a user action required. Each source provides an independent circuit breaker and next-attempt time.


### Collection semantics

- Manual collection: stable ordered or shuffleable set of asset references.

- Smart collection: saved filter over tags, colour, orientation, date, source, licence or favorite status; evaluated locally.

- Watched folder: persistable document-tree grant, incremental reconciliation by document ID and metadata, no broad all-files permission.

- Exclusions: persistent ignore records for current image and source IDs; safe across rescans and restored backups.

- Near duplicates: perceptual hash and aspect-aware thresholding, user-reviewable suggestions; never auto-delete originals.

- Favourite and history are separate from collection membership. Unfavourite does not silently remove a photo from every rule.


### Caching policy

Always cache thumbnails and a bounded number of render-ready images when permitted; never establish a hidden remote media library. Use an explicit storage budget (defaults proposed: 512 MB; user-selectable 128 MB–4 GB). A cache purge removes regenerable pixels while preserving metadata, collection membership and history. For offline collections, file access is rechecked before swaps.

Prefetch only when permitted by network/battery settings. Maintain the current and next eligible prepared image; use versioned cache keys = source ID + source version/ETag + crop/effect pipeline revision + target resolution. Validate checksum, decoded dimensions and MIME before cache promotion.


## 5. Wallpaper rendering and delivery


### Static mode: default

Call WallpaperManager.setBitmap(bitmap, cropHint, allowBackup, flags) on supported API levels with FLAG_SYSTEM / FLAG_LOCK as indicated by verified device capabilities. The app prepares a target-size bitmap, applies non-destructive crop/effect pipeline, then commits to Android and records success only after API completion and any available verification. Never assume a successful worker start means application succeeded.

Use one serialized delivery coordinator and a deduplicating per-target queue. Guard a swap with an idempotency key (rule ID, due window, destination, selected asset, revision). When both destinations are requested, document and record partial success rather than pretending the update was atomic at the OS level.


### Live mode: optional, staged

A dedicated WallpaperService.Engine draws visible scenes and can crossfade, slide or lightly parallax artwork. It stops animation and heavy work when the surface is invisible; releases textures on lifecycle transitions; obeys reduced motion; provides colour information through onComputeColors/notifyColorsChanged on supported releases. Home/lock behavior is capability-gated because live wallpaper destination handling differs across Android/OEM implementations.

The live engine cannot directly guarantee a change on every physical unlock merely from its own visibility callbacks; define a “wake cycle” trigger carefully and explain OEM limitations. No always-running foreground service is required for the default periodic static mode. An optional monitored event mode may use a user-enabled foreground component only when Android policy permits; offer a persistent notification and clear battery disclosure.


### Cropping & composition

- Persist normalized focal point, zoom and crop per image AND destination, with reversible edits and composition revision.

- Preview against real device ratio, wallpaper safe regions, launcher scrolling/parallax allowances and adjustable lock clock guides; guides are advisory because launchers differ.

- Modes: smart-fill, fit with blurred/solid edge, manual focal point, full-frame and safe-centre. Never distort image by default.

- Later offline-assisted focal detection is optional, model provenance and licence verified, runs only with user opt-in, and can be overruled by hand.

- Decode progressively with sampled bitmaps; mitigate GPU texture-size overflow and orientation/EXIF inconsistencies.


## 6. Automation engine and truthfulness


### Rule definition

Rule = immutable UUID, enabled, priority, trigger, optional condition expression, collection/source strategy, target flags, transition profile, policy overrides, effective time window, cooldown and failure policy. All UI configuration serializes to a versioned rule DSL; validation occurs before saving.


| Trigger | Proposed behavior | Execution caveat |
| --- | --- | --- |

| Manual, widget, shortcut, Tile, share target | Immediate user-initiated command | OS may limit background launches; queue request where required |

| Every N minutes / hours | Flexible periodic eligibility | WorkManager periodic minimum 15 min; actual run inexact |

| At clock time / day-of-week | Eligible in time window; reschedule after timezone/DST | Exact alarm only if legally/technically appropriate; no default exact-alarm demand |

| Sunrise / sunset | Offline solar calculation based on user-specified place or permission | Location is optional; no passive background location |

| Screen wake / lock | Use event mode/live engine where supported | Not guaranteed across OEM and process death without extra lifecycle support |

| Theme / Battery Saver / charging / Wi-Fi | Rule condition snapshots where legitimately observable | Only documented signals; do not access sensitive device data surreptitiously |

| App-sent intent / automation tool | Validated explicit intent or secure PendingIntent | Security-checked and rate-limited |




### Precedence and conflict resolution

1. Manual user choice is first unless paused with an explicit locked-mode policy; direct user change may present “resume schedule?” and never silently erase the manual choice.

1. Global Pause and per-destination Pause disable automated applications. Privacy/network restrictions and user-initiated temporary quiet periods remain hard gates.

1. Filter eligible rules by trigger, conditions, cooldown, source availability and destination capability. Resolve priority descending; stable UUID tie-break and a visible ordered rule stack.

1. For two rules targeting different destinations, allow both. For competing rules targeting the same destination, apply the winner and log why the other lost.

1. Select from a persisted per-collection/per-destination shuffle bag; remove visited items until exhaustion; prevent cycle-boundary repeat; preserve selection for retry rather than consuming another image.

1. Pre-decode selected image and only then attempt OS application. Commit success, lastApplied and shuffle advance in a transaction following confirmed call result; on partial/ambiguous platform outcome, reconcile before retry.

1. On failure, apply explicit fallback policy: cached next -> previous valid image -> keep existing. Never automatically replace the user’s wallpaper with black, default artwork or unrelated stock content.


### Explainable schedule

The Today screen shows next eligible time, the scheduling mechanism, last success and any pending policy limitation. A rule simulator evaluates a future time/device-state input and reports winner, losers, reasons and expected image pool. Diagnostics capture event IDs, stage durations, provider response classes and OS error codes without retaining filenames or URLs in a shared report unless the user permits it.


### Offline, reboot and DST behaviors

- On BOOT_COMPLETED and package update, reconcile persisted rules and re-enqueue eligible work; do not assume unrestricted foreground service startup.

- If exact time is missed due to sleep, use configurable catch-up windows: skip, next eligible, or at most one catch-up. No burst applying ten missed images.

- Persist timezone ID for user rules; recompute daylight-saving transitions and sunrise/sunset after timezone/location changes.

- When a source is down, preserve prepared local candidate if licensed and cached; otherwise keep the current wallpaper and show actionable status.

- Under memory pressure or cancellation, maintain a durable IN_PROGRESS record that can be reconciled without double advancement.


## 7. Native Android integration


| Integration | V1 behavior | Notes |
| --- | --- | --- |

| App widgets / Glance | Small Next, medium current/next, large preview/control, pause | Widget state derived from local store; responsive and accessible |

| Quick Settings Tiles | Next wallpaper, Pause / Resume | Prompt via requestAddTileService on Android 13+ contextually |

| App shortcuts | Next, Choose collection, Pause, Open Today | Support dynamic/pinned shortcuts and launcher differences |

| Android share sheet | Add image to collection or Apply now | Validate URI grants, mime, source attribution |

| Intents for Tasker/MacroDroid | Documented explicit contract + secure optional action token | No exported arbitrary filesystem/network action |

| Wallpaper picker | Live mode and preview entry | User confirmation where Android requires it |

| Material You | Live-colour updates where supported; opt-in theme adoption | Respect launcher and system precedence |

| Notifications | Only exceptional failures, active optional service and user requested status | Runtime permission and channel controls |

| Backup/export | SAF ZIP of rules, collections, metadata and optional explicit images | No proprietary sync/account |

| Accessibility services | TalkBack semantics, keyboard, D-pad, large text | Never request AccessibilityService privileges |



The UI should never imply that an action was installed before Android confirms it (e.g., a launcher-pinned shortcut request only proves a request, not user acceptance). Widget controls must be usable after process death via safe cold-start commands.


## 8. Data model, modules and reference architecture


| Entity | Key fields | Consistency notes |
| --- | --- | --- |

| Source | sourceId, type, endpoint, capabilities, health, credentialRef | No secrets in Room plaintext |

| Asset | assetId, sourceId, originId, URI, mime, size, hash, licenceRef | Stable identity independent of cache file |

| Collection | collectionId, name, kind, query, version | Membership via join rows; tombstone exclusions |

| CropProfile | assetId, destination, focalX/Y, zoom, styleRev | Non-destructive and versioned |

| Rule | ruleId, priority, triggerDSL, conditionDSL, target, policy | Validated; revisioned |

| ShuffleState | collectionId, destination, cycleId, order, cursor | Transactional compare-and-set |

| DeliveryEvent | eventId, requestId, reason, phase, result, elapsed | Redactable diagnostic audit trail |

| SourceLicence | workId, creator, licenceName, URLs, dateChecked | Attribution travels with asset |

| PreparedImage | cacheKey, assetId, bytes, checksum, expiry | Garbage-collectable, not authoritative |




### Module boundaries

Android app/ui (Compose + Navigation); design-system; domain-model; rules-engine (pure Kotlin); source-api and source implementations; storage (Room/DataStore); image-pipeline (decode, crop, preview, prepared file); delivery-static; wallpaper-live (separate optional service); scheduler (WorkManager/events); android-integrations (widgets, tile, shortcuts, share); diagnostics; backup-import; testing fixtures.

Prefer Kotlin coroutines/Flow and dependency injection with Hilt/Koin as chosen during architectural spike. HTTP via OkHttp/Retrofit; image loading via Coil or equivalent. Failures use typed sealed results, not swallowed exceptions. Avoid building proprietary servers simply to conceal API credentials; use anonymous endpoints and user-provided keys where allowed, or omit a source that demands a secret proxy.


### Operation pipeline

Trigger → snapshot of device/context → rule evaluation → winner(s) → shuffle reservation → source/cache resolution → decode and crop → per-target apply → verify outcome where possible → transactional state/diagnostic commit → widget/notification update. Every boundary gets independent tests, structured error codes, and cancellation behavior.


### Security

- Credentials in Android Keystore-backed secure storage; no API keys in screenshots, URLs, logs or backup by default.

- Allow HTTPS only for remote images unless explicitly permitted; redirect cap, DNS/IP reassessment, content-length cap, decompression-bomb checks, pixel-count cap, MIME sniffing and image decoder sandbox limitations.

- External intent receivers use exported=false by default; exported automation integration requires explicit package/action validation, rate limiting and authorization tokens where applicable.

- Image provenance/license metadata rendered as escaped text and links opened through safe intents; never trust remote HTML as code.

- Backup import validates JSON schema/version, path traversal, zip bombs, ID collisions, duplicate entries, references, and user confirmation before applying.


## 9. UX, accessibility and internationalization acceptance


| Requirement | Acceptance target |
| --- | --- |

| Target sizes | At least 48 × 48 dp on interactive controls; 8 dp separation where feasible |

| Text contrast | WCAG 2.2 AA target: 4.5:1 normal / 3:1 large; 3:1 important non-text |

| Scaling | 200% font scale without clipping essential controls; key flows tested at larger settings |

| TalkBack | Every interactive control labelled with action, state and result; logical reading/focus order |

| Input | Hardware keyboard, D-pad, switch access where applicable, predictive back navigation |

| Motion | Respect remove-animations and OS animator setting; no essential information conveyed through motion |

| Errors | Clear cause, action, retry semantics and recovery path; never only red/green status |

| Language | Localization-ready string resources, plural rules, right-to-left, time formats and units |

| Visual accessibility | Avoid text over unbounded photography without scrim/contrast check; user-selectable high contrast |



Testing should include the Pixel 6 Pro as a reference layout and real hardware representative of Samsung One UI and a more aggressively managed OEM. Screenshots in the pitch deck use conceptual examples, not physical-device captures.


## 10. Nonfunctional performance and quality budgets


| Dimension | Proposed release gate / method |
| --- | --- |

| Reliable scheduled updates | ≥99% eligible successful applications under controlled test conditions, excluding intentional OS deferrals; log and classify exclusions |

| Swap latency | Cached image: p95 ≤2.5 s on chosen reference device under foreground/manual conditions |

| Idle CPU | No deliberate polling, image decode or animation when inactive; profiler audit |

| Memory | Decode at target size, avoid redundant full-size bitmaps; investigate peaks >220 MB on reference devices |

| Local database | 20k-image import and 100k-image synthetic query test without full-table cursor materialization |

| Network | 0 requests during offline-only mode; honour metered/network-only settings, 429 retry-after |

| Battery | Compare against plain static wallpaper over 24–72h, quantifying source mode cost rather than publishing unmeasured claims |

| Crash resilience | Inject cancellation, kill during delivery, missing document provider, unplugged storage and boot reboot |

| Accessibility | Zero critical Accessibility Scanner/TalkBack journey failures in release matrix |



Budgets are acceptance proposals, not measured performance results. Document exact OS version, battery conditions, display resolution, image sizes and number of runs before publishing any figures.


## 11. Testing, telemetry and release engineering


### Layered tests

- Pure Kotlin property-based tests: deterministic rule conflicts, DST/sunrise boundaries, shuffle fairness, duplicate handling and idempotent retries.

- Adapter contract tests: mocked 200/401/403/429/5xx, malformed JSON, redirects, content-type spoofing, network disconnection, attribution retention and rights ambiguity.

- Image pipeline golden tests: EXIF rotation, portrait/landscape, extreme aspect ratios, oversized image, animated format fallback, broken bytes and ICC colour.

- Storage integration tests: Room migrations, transactional state, import interruption, 100k rows, update/delete/restore, revoked SAF permission and file rebinding.

- Android integration tests: WorkManager due windows, widget cold starts, TileService lifecycle, shortcut acceptance, intent security, reboot behavior and policy permission refusal.

- Device acceptance: Pixel 6 Pro Android 17, Pixel Android 14–16/emulators, Samsung One UI, Xiaomi/HyperOS or comparable aggressive OEM, tablets, foldables and landscape.

- Accessibility QA: TalkBack, Voice Access, Switch Access, 200% font, high contrast, RTL, reduced motion and external keyboard.

- Chaos tests: simulated clock changes, network throttling, provider outages, API 429, low storage, low RAM, Doze, process death, foreground/live app switching.


### Diagnostics and privacy-preserving observation

Local event journal is enabled by default with short bounded retention (proposed 30 days / 2,000 events). An optional export creates a user-reviewable scrubbed ZIP of app version, device API/OEM, request category, anonymous event IDs, failure codes and timings. Never auto-upload. No hidden telemetry SDK.


### Source operational health

Each connector owns a contract test and health status with last successful retrieval, outage state, backoff expiry and resolution guidance. Provide an independent policy audit every release and a human-readable provider changes changelog. Disable compromised/forbidden integrations via an app update or locally bundled policy version; without a Waltz backend there is no silent server-side kill switch.


## 12. Implementation plan: vertical slices, dependencies, release gates

Planning assumption: a small team of 2 Android engineers, 1 part-time designer, and periodic QA/accessibility/security review. Estimates below are engineering weeks per slice and can overlap. No work has yet been implemented.


| Phase | Scope / owner emphasis | Estimate | Ship gate |
| --- | --- | --- | --- |

| 0 — Feasibility | API/legal policy audit, benchmark spikes, device behavior matrix, font/icon licence audit | 2–3 wk | Approved source list, compile/target decision, real-device static/live proofs |

| 1 — Foundation | Project modules, Compose shell, design tokens, Room/DataStore, CI/tests | 2–3 wk | Navigation and theming accessible; migrations tested |

| 2 — Offline core | SAF folder/photo import, collections, cache, crop, static apply, shuffle bag | 4–5 wk | 10k+ image import, no-repeat, reboot recovery, manual change |

| 3 — Scheduling | WorkManager, timeline, rule engine, pause, simulator, diagnostics | 3–4 wk | Deterministic conflicts, no missed-state corruption, offline resilience |

| 4 — Source adapters | Commons, Openverse, Wallhaven, APOD gated, licence/credit flows | 3–4 wk | Provider contract tests, 429/auth/offline and attribution pass |

| 5 — Native integration | Glance widgets, QS tiles, shortcuts, share, backup/export | 2–3 wk | Cold-start control actions, permissions and accessibility pass |

| 6 — Visual polish | Compose motion, fine UX, dual destinations, local effects; dark mode | 2–3 wk | Visual regression and 200% font size pass |

| 7 — Live engine opt-in | WallpaperService, transition rendering, visibility lifecycle, OEM matrix | 3–5 wk | No runaway frames, no black surface after lifecycle torture |

| 8 — Release hardening | Battery profiling, fuzzing, security, translations, issue triage | 2–4 wk | Published test evidence, privacy audit, staged release |




### Development sprints and deliverables

1. Sprint A: ADRs for static-vs-live, API source policy, source capabilities, data schema v1, OS permissions matrix. Ship a small proof app on a Pixel, not an elaborate polished shell.

1. Sprint B: durable URI handling + transactional image selection + one stable collection and undoable manual swaps. This is the first end-to-end minimum viable loop.

1. Sprint C: rules with time windows and predictable shuffle, crash replay and reboot tests. Add user-facing event explanations before advanced triggers.

1. Sprint D: Commons/Openverse adapters and their licence/attribution UI; Wallhaven after policy sign-off; NASA APOD behind image-rights gate.

1. Sprint E: widgets, shortcuts, tiles, shared UI components, backups, a11y audits and performance baseline.

1. Sprint F: live engine research branch, provider error simulation, OEM matrix and only then production gating.


### Dependencies and critical path

Rule engine depends on stable asset identity and delivery coordinator. Automated source rotation depends on rights metadata + adapter contract. Widgets and Quick Settings depend on the same idempotent command entry point as Today. Live effects depend on decoded/render-ready assets and capability checks. Never build the visual designer in isolation from lifecycle/testing assumptions.


### Release tracks

Alpha: fully offline manual + daily rotation on API-supported devices. Beta: rule studio, diagnostics and vetted internet sources. 1.0: accessibility complete, native controls, robust migration/backup and no critical open reliability regressions. Optional live engine can remain beta if device matrix shows instability; it must not block a safe static 1.0.


## 13. Risk register and explicit decisions


| Risk | Impact | Mitigation / decision |
| --- | --- | --- |

| Android Doze/OEM kills | Rotation skipped | Honest windows, no busy loops, optional user-visible event mode, recovery trace |

| Restricted API terms | Legal/provider outage | Source eligibility gate, no Unsplash/Pexels default adapter |

| Wallpaper destination quirks | Wrong lock/home result | Capability tests, prompt and partial success logging |

| Heavy image decode/GPU mismatch | OOM, black surfaces | Sampling, dimensions cap, prepared cache, live visibility stop |

| Credential exposure | Provider/account compromise | No embedded secrets, Keystore, redacted diagnostics |

| Large folder import | Cursor/ANR/stale state | Paged Room queries, incremental reconciliation, transactional commits |

| Live wallpaper overrides | Loss of user-selected live wallpaper | Explicit opt-in, confirmation and restore guidance |

| Rule complexity | Unexpected rotation | Readable DSL, priorities, simulator, conflict explanations |

| Source attribution uncertainty | Licence violations | Keep metadata, original link and human-verification disclaimer |




## 14. Functional acceptance tests (must pass)

- AC-01 — Import 20,000 SAF images, kill during indexing, restart and reconcile without duplicate membership or a crash.

- AC-02 — Rotate a 7-image bag 7 times without repeats; on cycle boundary do not immediately repeat last image.

- AC-03 — Revoke a folder grant, attempt rotation, preserve the existing wallpaper and show re-grant action.

- AC-04 — Lose network during download, recover source with bounded retry and no black/reset wallpaper.

- AC-05 — Two equal-priority rules for one target resolve identically after app/process reboot; simulator matches executor.

- AC-06 — Two independent target rules change only their destinations on a verified capable device.

- AC-07 — Manual Next from widget/QS works with application process cold; one physical tap creates at most one recorded delivery.

- AC-08 — Time zone and DST jump does not duplicate or permanently skip an eligible scheduled window.

- AC-09 — A media candidate without adequate rights/attribution does not silently become shareable or exportable.

- AC-10 — A 100 MP malicious or malformed image fails safely; remaining library is still usable.

- AC-11 — At 200% font scale, TalkBack and keyboard, user can complete onboarding, set schedule, diagnose error and pause.

- AC-12 — Live mode stops draw loop while invisible and survives 50 landscape/portrait/lock/launcher switches on test OEMs.

- AC-13 — Cancel and restart import/backup; old DB remains valid and restored rule references do not break.

- AC-14 — Source returns 429 with Retry-After; no hammering, user sees accurate next retry.

- AC-15 — Every action carries readable failure/skip/success log entry and optionally exports scrubbed diagnostic report.

- AC-16 — No network activity in offline-only profile across full daily use scenario.


## 15. Deliverable inventory and next engineering decisions

- Engineering: Gradle multi-module template; ADRs; schema and migrations; adapter SDK; pure rule engine; UI component library; tested static pipeline; test fixtures and CI matrix.

- Design: Figma-ready tokens, component specifications, 16 annotated conceptual mockups, interaction prototypes, high-contrast and dark-theme variants, landscape/tablet layouts.

- Documentation: user guide, accessibility statement, privacy policy, source-rights checklist, compatibility matrix, backup format, diagnostics handbook, licence notices.

- Before coding: choose open-source licence (Apache-2.0 recommended for reusable adapters, pending dependency review), product name clearance, minimum/target SDK based on tested platform matrix, and approved source terms.


## Appendix A. Source and platform reference links

WallpaperManager static API: https://developer.android.com/reference/android/app/WallpaperManager

WallpaperService Engine lifecycle: https://developer.android.com/reference/android/service/wallpaper/WallpaperService.Engine

Android scheduling / alarms: https://developer.android.com/develop/background-work/services/alarms

Jetpack Glance widgets: https://developer.android.com/develop/ui/compose/glance

Quick Settings tiles: https://developer.android.com/develop/ui/views/quicksettings-tiles/index

Android Storage Access Framework: https://developer.android.com/training/data-storage/shared/documents-files

Android selected-photos access: https://developer.android.com/about/versions/14/changes/partial-photo-video-access

Openverse API: https://api.openverse.org/v1/

Openverse licence warning: https://docs.openverse.org/api/reference/made_with_ov.html

Wikimedia image info API: https://www.mediawiki.org/wiki/API:Imageinfo

Wallhaven API: https://wallhaven.cc/help/api

NASA API rate limits: https://api.nasa.gov/

NASA APOD rights: https://science.nasa.gov/apod/apod-about/

Unsplash restrictions: https://help.unsplash.com/en/articles/2511245-unsplash-api-guidelines

Pexels wallpaper app restriction: https://help.pexels.com/hc/en-us/articles/4405588861721-Can-I-use-the-API-as-a-wallpaper-app

Android touch targets: https://support.google.com/accessibility/android/answer/7101858


## Appendix B. Relationship to visual pitch deck

The accompanying presentation features sixteen application mockups and original colour, icon, wallpaper-image and component proposals. All screen art is generated illustrative content. The deck is intended as a design direction and implementation brief, not an assertion that the app or source connectors have already been built.

## Addendum: Screenshot quick import and Google Lens (October 21, 2026)
Two additional approved user workflows, F071 and F072, are specified normatively in [SCREENSHOT-AND-LENS-FEATURES.md](SCREENSHOT-AND-LENS-FEATURES.md). Screenshot editing and Share-to-Waltz are P0; clipboard-paste UX and dedicated Lens targeting are contingent on platform capability. The addition specifies non-destructive rotate/crop, explicit Use Now/Add Next/Just Save queue semantics, transactional import, URI-grant handling, accessible controls, and external Google Lens sharing through supported Android intents with fallback. Its tests S071-01 through S072-04 join the release gates. Do not infer a public direct Lens SDK or automatically read clipboard in the background.

### F073 universal share/export addendum (October 21, 2026)
Treat Android outbound sharing as a baseline cross-cutting capability, never only a Lens-specific feature. The normative [F073 contract](SCREENSHOT-AND-LENS-FEATURES.md#requirement-f073-universal-outbound-image-sharing-and-editing-supersedes-lens-only-action-design) specifies ACTION_SEND/ACTION_SEND_MULTIPLE, original-versus-flattened-crop selection, FileProvider grants and lifetime, batch limits, external editing round-trip, SAF Save copy, EXIF privacy, the Android Sharesheet, and capability-aware destinations (chat, email, Drive, ChatGPT, Lens, Google Images). P0 generic share; P1 destination shortcuts and enhanced round-trip editing. Added tests S073-01–10.

## Native Android architecture decision reference (October 21, 2026)
The detailed [native-stack and delivery blueprint](NATIVE-ANDROID-ARCHITECTURE.md) refines the high-level module and platform plans here. Kotlin, Compose, Navigation 3, Hilt, Room, DataStore, Coroutines/Flow, WorkManager, capability-gated AlarmManager, WallpaperManager, optional WallpaperService, Glance and scoped Android intents form the baseline. It also specifies crash-recoverable command/outbox operations, target 37 qualification, Android 17 widget-memory budgets, real-world five-minute schedule semantics, signed APK release engineering, and Android developer verification planning for sideloading. New architecture decisions must be recorded and proven via CI + device test, rather than silently inferred from mockups.


## 2026-10-22 consolidated implementation and pitch-deck update

The **native Android architecture** is now concretely specified by [NATIVE-ANDROID-ARCHITECTURE.md](NATIVE-ANDROID-ARCHITECTURE.md). Adopt Kotlin and Jetpack Compose/Material 3, Navigation 3, ViewModel/StateFlow, Hilt, Room, DataStore, structured coroutines, WorkManager for durable non-exact jobs, careful AlarmManager eligibility, WallpaperManager static delivery, optional visibility-aware WallpaperService.Engine, Coil previews, bounded image rendering, and Glance/native Android sharing integrations. The intent is one downloadable signed APK, minSdk29 proposed, API37 target qualification required. Release versions and compatibility must be pinned and proven before scaffold.

Implementation priorities are explicitly **M0 platform proof; M1 tested rainbow alpha; M2 reliable native daily driver; M3 expressive rules and rights-checked external content; M4 optional live effects and finish**. Do not make the advanced rules engine or live graphics prerequisites for the usable first APK.

The presentation has been revised to 42 slides (34 prior screens/design slides and eight native engineering slides); see [PITCH-DECK-OUTLINE.md](PITCH-DECK-OUTLINE.md). No runtime implementation is claimed. Add release gates for deterministic command execution, process-death recovery, actual success versus eligibility, accessibility, OEM wallpaper behavior, sideload package signing continuity and image source rights.

## 2026-10-22 rebrand and paper-reel interface authority

**Product name: Glimpse (formerly Waltz).** Adopt the new [continuous-reel identity/UX specification](GLIMPSE-CONTINUOUS-REEL-DESIGN.md) over earlier visual mockups, preserving the underlying native Android architecture, local-first privacy rules, reliability gates and universal sharing. The chosen identity is a tactile paper reel with **five broad photo windows**. A physically oversized reel can be clipped at the collection browser's left, right and bottom edges, but it is a bounded, virtualized viewport over a potentially large (and actually finite) collection. Never generate endless image records or conflate browsing with actual wallpaper changes.

The primary UI must provide an image hero, true current index/count, semantic Next photo / Set as wallpaper, and **View all** as a first-class grid. Support assistive technology, reduced motion, orientation and dynamic type. Keep Android foreground/static scheduler truth separate from the reel animation. The new 57-slide Glimpse v4 deck is a conceptual product design, not deployed Android UI. Editable SVG reel assets have been committed; PDF/PPTX/PNG binaries are tracked separately until uploaded.
