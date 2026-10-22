> **GLIMPSE ARCHITECTURE AUDIT NOTE (2026-10-22).** This is an implementation proposal, not working Android code. Adopt [technical/side-effect contracts](GLIMPSE-TECHNICAL-BEHAVIOR-CONTRACTS.md) and [73-feature audit](GLIMPSE-FEATURE-SPEC-COMPLETENESS-AUDIT.md) for current behavior, [critical reel UX](GLIMPSE-REEL-UX-CRITICAL-AUDIT.md) for approved-vs-experimental interaction roles, and [motion architecture](GLIMPSE-MOTION-RENDERING-ARCHITECTURE.md) **from the first native rendering prototype**. In Section 13, the M4 “High-fidelity design implementation, motion” wording is a **historical sequencing error**: M0 must prototype the native reel motion/visual reference on device, M1 must use that deliberate motion system, and M4 may only extend/refine it. Old `io.github.<org>.waltz` is an example **not a package decision**. Do not imply automatic Google Photos album sync, exact background five-minute cadence, external-display mutation, cross-profile changes or arbitrary Android system palette override are available without a capability proof.

# Waltz — Native Android Technical Architecture and Delivery Blueprint

**Decision status:** architecture proposal / implementation authority for the first Android repository scaffold. **Date:** 2026-10-21. **Application status:** no native application implemented here yet. **Distribution:** signed APK, manually sideloaded; no Waltz server or proprietary wallpaper library.

Read with [PRODUCT-SPECIFICATION.md](PRODUCT-SPECIFICATION.md), [RAINBOW-QUICKSTART-CONTRACT.md](RAINBOW-QUICKSTART-CONTRACT.md), [WORKFLOW-DESIGN-RESPONSE.md](WORKFLOW-DESIGN-RESPONSE.md), and [SCREENSHOT-AND-LENS-FEATURES.md](SCREENSHOT-AND-LENS-FEATURES.md). This document decides the platform architecture; those files retain behavior and UX authority. Contradictions require an explicit ADR, not silently divergent implementations.

## 1. Architectural thesis and non-negotiable invariants

Build one **native Kotlin Android APK**, with **Jetpack Compose**, **Navigation 3**, a **pure rule/selection engine**, **Room-backed durable state**, **platform-specific wallpaper adapters**, and OS integrations implemented against supported Android APIs. No Flutter, React Native, WebView-based core UI, embedded JS engine, hosted account, Waltz image cloud, cross-platform abstraction layer, or permanent vendor API key baked into the APK.

The persistent user intent must outlive Activity death, service death, process eviction, device reboot and version upgrades. UI is a client of the same application command API used by widgets, shortcuts, share targets and automatic triggers. No widget, receiver, worker, renderer or screen independently mutates a rotation queue or calls WallpaperManager.

**Five invariants:**
1. **Safety:** never delete the user's source photo as a side effect of import, wallpaper set, cache eviction or exclusion. Explicit source deletion is a separately confirmed action, if ever supported.
2. **Truth:** distinguish *scheduled*, *eligible*, *attempted*, *applied*, *observed*, and *skipped*; never display a successful change when the system call failed or Android deferred execution.
3. **Integrity:** collection membership, edit recipes, shuffle queues and operation logs are crash-recoverable and versioned. Android wallpaper setting cannot join an SQLite transaction: reconcile it explicitly.
4. **Privacy:** user-selected images remain local unless the user intentionally shares or enables a remote image source. No telemetry by default, no hidden image upload, and no mandatory account.
5. **Accessibility:** every feature usable through semantic controls and without gestures, colour vision or animation; TalkBack and large-font acceptance precedes release.

## 2. Compatibility and build baseline

- **Language:** Kotlin with structured coroutines, Flow, sealed domain types and immutable UI models. Avoid Kotlin Multiplatform until an actual second client exists.
- **minSdk:** API 29 / Android 10 (product decision, not technical necessity); **compileSdk:** 37 / Android 17. **targetSdk:** aim for 37 from first release if acceptance matrix passes; any temporary target 36 fallback must be explicit, documented, time-boxed and tested on 37 devices. Review Android 17 all-app and target-specific changes.
- **Toolchain initial candidate:** AGP 9.1.1 / Gradle 9.3.1 / JDK 17 per Android's compatibility page. Reverify latest mutually compatible stable patch before scaffold. Android Gradle Plugin 9 includes built-in Kotlin integration: **do not blindly apply obsolete kotlin-android plugin assumptions**. Validate Compose compiler, KSP and Hilt compatibility in a skeleton build before freezing versions.
- **UI versions:** Compose BOM stable version (Android documentation currently illustrates 2026.09.00) and stable Navigation 3 1.2.0 (October 7, 2026); Room 2.8.5 (September 2026). Pin all versions in libs.versions.toml and Gradle wrapper; no dynamic '+', snapshots or alpha in release.
- **Application ID:** choose and check a permanent reverse-domain ID before first distributable APK, e.g. io.github.<org>.waltz only after namespace ownership validation. Never change ID casually: it changes app identity/storage. Configure versionCode monotonic and explicit versionName/ABI.
- **Architecture support:** arm64-v8a first for optional native ML/graphics modules only; standard Kotlin/Compose APK remains device-independent. Prefer no NDK in v1.

Refs: https://developer.android.com/build/releases/agp-9-1-0-release-notes ; https://developer.android.com/jetpack/androidx/releases/navigation3 ; https://developer.android.com/jetpack/androidx/releases/room ; https://developer.android.com/develop/ui/compose/bom ; https://developer.android.com/about/versions/17/behavior-changes-17

## 3. Stack and why (adopt stable versions, verify integration)

| Concern | Technology | Contract |
|---|---|---|
| Main UI | Jetpack Compose + Material 3 | Waltz design tokens/components override colour, shape, type and motion; use platform affordances, predictive back and edge-to-edge |
| Navigation | Navigation 3 | Typed destinations, owned back stack, deep links and restoration |
| State | ViewModel + StateFlow + collectAsStateWithLifecycle | UDF: immutable UiState, intents/commands, errors represented as state |
| Dependency injection | Hilt, KSP after compatibility check | No global service locators or ad-hoc singleton state |
| Business logic | Pure Kotlin domain package/module | Side-effect-free evaluation, immutable AST, independent JVM tests |
| Storage | Room/SQLite + schema export and migration tests | Authoritative local collection/schedule/history state |
| Settings | Preferences or Proto DataStore | Small scalar preferences only, not image catalogs or queue ledgers |
| Async | Coroutines / Flow | Structured cancellation, bounded concurrency, no GlobalScope |
| Reliable maintenance | WorkManager | Imports, remote prefetch, quota cleanup, reconciliations, <= system-guaranteed timing constraints |
| Static wallpaper | WallpaperManager | FLAG_SYSTEM/FLAG_LOCK capability probes; SET_WALLPAPER |
| Live mode | WallpaperService.Engine | Separate optional renderer; visibility/lifecycle-aware, no perpetual frames |
| Image preview | Coil for Compose, size bounded | Not the authoritative crop renderer |
| Image render | ImageDecoder + sampled decoding + Canvas/Matrix; streaming/file output | Exact non-destructive recipe, memory budgets, EXIF orientation, original preserved |
| HTTP | OkHttp + Retrofit + explicit JSON serialization | Per-provider adapters, host allowlists, bounded redirects, retries and ETags |
| Widgets | Jetpack Glance backed by Room-backed snapshot | No large bitmap parcels or business logic in widget callbacks |
| Quick settings | TileService | Minimal commands, locked-device safety, limited exported surface |
| Share/import | Android Sharesheet ACTION_SEND, SEND_MULTIPLE, Photo Picker, SAF, FileProvider | Scoped grants, private staged copies, external app capability detection |
| Diagnostics | Structured in-app event journal, user-exported scrubbed report | No default cloud logs, no private image paths in reports |
| Tests | JUnit, Compose UI/instrumentation, Room migration, Robolectric selectively, MockWebServer, Macrobenchmark, property-based tests | Real-device tests are mandatory for platform behavior |

Do not add RxJava, Realm, Firebase, analytics trackers, another navigation framework, or multiple image decoders without demonstrating a concrete unmet requirement. Use graphics AGSL (Android 13+) or Canvas as a staged optional extension; Vulkan/NDK only if measurement justifies it.

## 4. Module graph (lean but with hard boundaries)

Start with ~9 modules; do not fragment into 30 micro-libraries:
```
:app                     // application, DI root, manifest, Compose Navigation 3, theme
:core:model              // immutable IDs, image metadata, rules/AST, errors, operations
:core:engine             // pure rule compiler/evaluator, collection flattening, no-repeat shuffle, conflict resolution
:core:database           // Room entities, DAOs, migrations, outbox/journal and validation
:core:media              // importer, crop/rotate recipe, previews, rendering cache, external share grants
:core:android            // WallpaperManager gateway, scheduler adapters, lifecycle, capabilities
:core:sources            // SourceProvider contract + local/picker/SAF and approved remote adapters
:feature:library         // collections, imports, image detail, editor, quick-start
:feature:automation      // rhythms/scenes/rules and simulator, activity and diagnostics
:feature:integration     // widgets, tile, external intents, shortcuts (split if needed)
:benchmark               // Android Macrobenchmark/Baseline Profile generator
```
11 including feature integration and benchmark is a reasonable initial maximum, not a mandatory fixed number. Module dependencies point inward. `:core:engine` cannot import android.*, Compose, networking or Room. Feature modules never import DAOs or platform wallpaper APIs. Use explicit interfaces in domain; wire platform implementations at the app boundary. Create Gradle convention plugins only after the first reliable skeleton, not an elaborate plugin ecosystem prematurely.

## 5. Data architecture and explicit record types

**Room source of truth** with foreign keys, indexed joins and exported schemas. Suggested tables:
- `ImageAsset(id, sha256, mime, width, height, sourceType, provenance, license, attribution, localPath, status, createdAt, lastVerifiedAt)`
- `Collection(id, name, artworkId?, sortMode, createdAt)`
- `Membership(collectionId, imageId, includedAt, excludedAt?, position?, weightOverride?)`
- `CompositeEdge(parentCollectionId, childCollectionId, weight, filterExpression?)` with graph cycle detection and bounded expansion.
- `EditRecipe(id, imageId, revision, orientation, rotation, cropRectNormalized, position, colourAdjustments, createdAt)`
- `Scene(id, name, destinationBindings, sourceExpressionId, displayPolicyId)`
- `Rule(id, scope, trigger, conditionAstVersion, priority, actionAstVersion, enabled, createdAt)`
- `ActiveSelection(destination, sceneId, imageId, recipeId, selectedAt, verifiedAt, sessionId)`
- `RotationCycle(destination, sceneId, queueVersion, seededPermutation, cursor, recentExclusionRing)` (or normalized ordered queue)
- `Operation(id, idempotencyKey, origin, target, desiredImageId, status, attemptCount, lastErrorCode, timestamps, appliedWallpaperId?)`
- `TriggerEvent(id, origin, observedAtUtc, elapsedRealtime?, timeZoneId, conditionSnapshot, eligibilityDecision, operationId?)`
- `SourceHealth(sourceId, status, retryAfter, etag, lastSuccess, lastFailure, availableCount)`
- `ExportJob` / `ImportJob` for resumable file operations.
Do not store pixels in SQLite. Files in private filesDir; ephemeral previews, rendered crops and remote image caches in bounded cacheDir. Record SHA-256 for dedupe; separate image identity from collection membership and from edit variants. Track asset retention through explicit references before cleaning private copies. Never use arbitrary provider URI permission as the only durable record for a cloud-backed photo.

Use *Room transactional operations plus a durable outbox pattern*: DB transaction records intent, a single executor attempts external wallpaper application, then records outcome. The platform call is not atomic with Room. If process dies between setBitmap and committing the outcome, reconcile system wallpaper ID where available, persisted operation and last-known state, **never assume two-phase commit or magically roll back the system wallpaper**.

Backups: documented versioned JSON manifest of user metadata and rules, with optional image-data bundle. Include source locator/remapping, assets' content hashes, schema version, app version, recipe version and encrypted secret-handling strategy. Exclude cache and temporary share files from ordinary Auto Backup. Restore cannot silently authorize external source access or assume Google Photos URI persistence.

## 6. Command bus and deterministic rule engine

```
UI / Glance / Tile / intent receiver / schedule event
  -> CommandGateway.execute(Command, Origin)
  -> Capability and authorization checks
  -> domain evaluator: RuleContext -> Decision + Explanation
  -> durable Operation journal/idempotency
  -> ImageResolver -> EditRenderer -> WallpaperDelivery
  -> result verification + persisted status
  -> Flow refresh for UI/widgets + next schedule
```

Strong typed commands: `ImportAssets`, `AddMembership`, `SetNow`, `QueueNext`, `SaveOnly`, `Advance`, `Pause`, `Resume`, `EvaluateTrigger`, `ActivateScene`, `ShareImage`; each carries origin, target, idempotency token and timestamp. Prioritize explicit foreground user action over automatic trigger for the same target, serialize within each destination (home/lock) and coordinate `Both` as one high-level operation with two recorded platform outcomes. Never mutate two destinations casually from one result.

Rule expression: typed, versioned AST (Trigger + conditions + source expression + destination + priority + exception + fallback). Human-facing constructs: **Rhythm** (simple preset), **Scene** (named configuration), **Rule** (condition), **Override** (time-bounded precedence). Logic: `NOT > AND > OR`; ordered priorities; manual override > user-pinned hold > explicit narrow rule > scene default > global fallback, with user-customizable ordering only where deterministic. Detect contradictory destinations, impossible predicates, empty sources and recursion before activation. Store trace like “Selected image 18 because collection Rainbows active, 5-minute active-use rhythm eligible, skip-last-10, home screen only.”

Shuffle without replacement across eligible set; avoid boundary repeats across reshuffle cycles; deterministic RNG seed for tests, resilient cursor on collection mutations, weighted sampling with explicit fairness explanation. Nested collection graph acyclic by default, depth and expansion bounded to avoid pathological cardinality explosion. Use pure property-based and fuzz tests for 73 human workflows and randomized command sequences.

Time representation: instants UTC + local zone + monotonic elapsed time for within-session delays. DST, timezone changes, date changes, reboot and clock rollback explicitly handled. Scheduler requests **eligibility evaluations**, not direct bitmap application.

## 7. Timing model: truthful, robust and Android-policy-compliant

**There is no general-purpose, OS-guaranteed sub-15-minute periodic WorkManager API.** Periodic WorkManager minimum is 15 minutes; runs are inexact. Android doze, standby and OEM background policies can defer alarms and work. Sideloaded APKs do not bypass these restrictions.

Provide three distinct and clearly named behaviors, capability-gated:

1. **Efficient static / best effort** (default): WorkManager periodic for >=15 min, and deliberately selected inexact AlarmManager one-shot/foreground catch-up for user-chosen shorter cadences, with stored next-eligible timestamp, deadline tolerance and rate limiting. Do not claim a 5-minute cadence is exact in background. Never request exact alarms by default.
2. **Visible live wallpaper** (optional): WallpaperService.Engine schedules next image/transition while **its surface is visible** and halts rendering and timers when invisible. Visibility is not synonymous with screen awake while other apps are foreground: the UI must not imply always-on 5-minute changes across every application.
3. **Advanced scheduling mode** (research-only until device-proof): evaluate whether a user-visible foreground execution model genuinely fits an Android 14+ declared foreground service type. `specialUse` cannot be treated as a blanket permission hack; `shortService` is limited; `dataSync` describes imports, not continuous five-minute cycling. Exact-alarm special access requires valid use case and user authorization, and `USE_EXACT_ALARM` is not an eligible shortcut for arbitrary wallpaper rotation. No hidden long-lived battery optimization exemption request.

For five-minute Rainbow Contract: show *“Every 5 minutes while eligible; Android may delay changes when the app is sleeping or restricted”*; expose Last applied, Next eligible, Current engine, Delay cause, Next now. If scheduler wakes after three missed intervals, **advance once**, not three times. Any user-triggered Next works immediately subject to platform API availability.

Testing: instrument Pixel 6 Pro Android 17, Samsung and secondary vendor, emulator API29/33/34/35/36/37; screen on idle, screen off, Doze, standby bucket, DND, Battery Saver, reboot, force-stop (note Android force-stop can suppress scheduled work until re-open), timezone change, airplane mode, 10k library, app upgrade. Record eligible/request/actual elapsed times and p50/p95 delay by condition; no ungrounded precise timing SLA.

Refs: https://developer.android.com/develop/background-work/services/alarms ; https://developer.android.com/develop/background-work/background-tasks ; https://developer.android.com/develop/background-work/services/fgs/service-types

## 8. Android wallpaper delivery and rendering

**Static first:** `WallpaperManager.setBitmap(bitmap, cropHint, allowBackup, which)` or `setStream` overloads with `SET_WALLPAPER` permission. Probe `isWallpaperSupported()`, `isSetWallpaperAllowed()`, and API flags before presenting Home/Lock/Both. Device/launcher combinations can treat lock screens and static/live wallpaper overrides differently. Maintain a wallpaper destination capability matrix and genuinely test results, not just methods returning without throwing.

Use normalized crop/position recipes (source space and display viewport), respect image orientation, density, screen ratio, launcher parallax/crop differences, gesture/nav/status safe areas. Keep original unaltered. Bound decoded memory by requested target resolution, avoid loading multiple original 12k x 12k bitmaps, reuse buffers only when safe, precompute next thumbnail/Wallpaper bitmap on IO/Default dispatchers and prevent heavy work on main thread. Expose manual focal-point correction. Device color/WallpaperColors integration gated on actual results.

**Optional live v2:** WallpaperService.Engine responds to visibility, surface changed/destroyed, offsets, preview and color requests; render-on-demand rather than frame loops while idle. Start with Canvas/AGSL-supported effects before GPU-native architecture. Must support system reduced motion, explicit crossfade disable, colour stability and energy profiling. Static mode fully functional when live disabled.

Ref: https://developer.android.com/reference/android/app/WallpaperManager ; https://developer.android.com/reference/android/service/wallpaper/WallpaperService.Engine

## 9. Source import/adapters and outbound sharing

- **Owned photo imports**: Photo Picker including selected cloud-backed Google Photos on supported configurations (not assumed globally). Immediately stream selected image through verified private import before adding to active rotation. Google Photos album continuous synchronization is **not** provided by native picker; separate service authorization and policy assessment required if proposed later.
- **Folder access:** SAF ACTION_OPEN_DOCUMENT_TREE and persistable URI grants where supported; correctly handle revoked permissions, cloud provider latency, moved files, SD removal; avoid broad MANAGE_EXTERNAL_STORAGE.
- **Screenshot intake:** ACTION_SEND/ACTION_SEND_MULTIPLE, user-invoked clipboard read and picker fallback. Stage ephemeral URI quickly; original + non-destructive edit recipe, explicit Use Now / Add Next / Just Save.
- **Remote sources:** typed SourceProvider interface: `search(query,cursor)`, `resolve(id)`, `fetch(id)`, `health()`, capabilities, provenance and attribution. Start vetted Wikimedia Commons/Openverse with image-rights validation; Wallhaven subject to current API and filtering; NASA APOD rights per image; disable unsupported commercial APIs such as Unsplash/Pexels wallpaper-use restrictions. Each adapter isolated with MockWebServer contract tests and contract fixture snapshots.
- **Network:** HTTPS standard platform TLS verification, strict timeouts, connection/payload ceilings, MIME sniff/decoder validation, per-host redirect allowlist, safe filename rules and quota. Exponential backoff with jitter and server Retry-After, ETag conditional fetch, no endless retry loops, no silent provider failure. Image safety checks and offensive-content filter defaults where source supports them.
- **Export:** ACTION_SEND/ACTION_SEND_MULTIPLE with FileProvider content:// temporary read grants; Android Sharesheet for compatible ChatGPT, chat, mail, Lens, edit and Drive apps. SAF ACTION_CREATE_DOCUMENT for Save copy. Original/edited/cropped preview; EXIF and location scrubbing options, no fake private Lens API.

## 10. UI quality, accessibility and responsiveness

Waltz's deliberately playful visual identity must be built as **tokens and reusable accessible components**, not rasterized screens. Use Compose Material 3 semantics underneath custom colours, type and shapes. Surface primary commands: Add, Next, Use Now, Share, Pause. Short journeys use Rhythm preset; only advanced intents reveal Scene and Rule editor. Rule editor has natural-language preview, conflict checker, simulation timeline and explanation “why this image?”.

Target **48dp or larger** touch areas, TalkBack labels and meaningful grouping, switch access, keyboard, large font at 200%, minimum AA contrast for core text/control boundaries, reduced motion and system animator scale, dynamic colour optional (never obscures brand accessibility), landscape/foldable layout and predictive back. Crop tools require numeric adjustment controls besides pinch gestures. Widget semantics tested separately from Compose app UI.

Use Glance for widgets, noting that Glance is **not the same component API as Compose UI**. Android 17 target 37 imposes a strict RemoteViews Bitmap/Icon memory budget (1.5 × screen width × height × 4 bytes) and can throw fatal IllegalArgumentException if exceeded: send compact thumbnails and minimize updates. Widgets should be controls (Next / Pause / Now playing) not a constantly ticking slideshow. Quick Setting Tile and shortcuts use same CommandGateway. External automation intent exported narrowly and permission/confirmation-gated for sensitive operations.

Refs: https://developer.android.com/develop/ui/compose/accessibility/semantics ; https://developer.android.com/develop/ui/compose/accessibility/api-defaults ; https://developer.android.com/develop/ui/compose/glance/create-app-widget ; https://developer.android.com/about/versions/17/behavior-changes-17

## 11. Security/privacy and threat model

- Minimize manifest permissions: SET_WALLPAPER, INTERNET only for enabled source providers, appropriate receiver/TileService/Glance declarations; **no** QUERY_ALL_PACKAGES, MANAGE_EXTERNAL_STORAGE, always-on clipboard watcher, accessibility service, overlay permission, root or VPN dependency. INTERNET is install-time and not toggleable per provider in manifest; disabling providers at runtime stops outbound traffic.
- Explicitly define exported components/intent filters and permissions; reject untrusted deep-link parameters, oversized bundles and malicious content URIs. Prevent URI traversal, EXIF location leakage and cache use-after-delete.
- Treat foreign image bytes and metadata as adversarial. Enforce maximum compressed size and decoded dimensions; stream to bounded temp disk, validate codec, hashes and decode. Avoid loading untrusted SVG into permissive HTML/WebView and avoid unsafe native image libraries.
- Do not embed upstream API secrets in APK. Keyless endpoints preferred; user-owned credentials entered explicitly, stored protected under Android Keystore as justified; secrets must never appear in repository or exported diagnostics. Trust anchors/platform TLS, no custom “trust all certificates”.
- Source licences and provenance stored per image; ambiguous/unknown rights prominently displayed rather than guessed.
- Local caches quotas and expiry; shred/zeroization promises prohibited (flash storage realities). Implement privacy-aware export of event journal with review/redaction.
- No analytics SDK, crash-report cloud, advertising identifier or image telemetry by default. Opt-in manually exported diagnostics are sufficient for first release.

## 12. Continuous quality, release engineering and sideload reality

**Testing pyramid**
1. Pure JVM unit/property/fuzz tests: shuffles, weights, rule precedence, recursion/cycles, DST, boundaries, crash-replay model and all 73 scenario families.
2. Room migration tests from *every* released schema, foreign-key checks, 100k-asset synthetic query benchmarks and large-batch imports.
3. Fake platform gateways and MockWebServer: no image loss, expected retries, corrupted image, stale source, permission revoked, offline, cache eviction, double user commands, network backpressure.
4. Robolectric for narrow Android behaviors where trustworthy, Compose UI tests, TalkBack/keyboard checks.
5. Emulator instrumentation matrix 29/33/34/35/36/37; physical hardware Pixel 6 Pro, current Samsung and non-Pixel OEM for background behavior, app widgets, lock screen and OEM wallpaper rules.
6. Macrobenchmark startup/grid/image transitions and Baseline Profiles; thermal/battery profiling for long-term live mode; leak/ANR watch.
7. Golden screenshot semantics and design snapshot review across font scale, gesture/3-button navigation, dark/light, reduced motion and RTL.
8. Install/upgrade/backup/restore/rollback drills using APK signed with **the same permanent release key**.

**CI**
- GitHub Actions PR gate: lint, ktfmt/Spotless, detekt where valuable, Gradle build, dependency verification, unit tests, Room schema migration checks, dependency/license audit and secret scanning. CI instrumentation nightly/on release.
- Lock dependencies with Gradle versions catalog + dependency verification checksums; SBOM generation, dependency scanning (OSV/Dependabot), pinned GitHub Action SHAs. Avoid unreviewed build scripts and dynamic plugins.
- Build reproducibility target: deterministic build inputs, embed source commit SHA/version, produce APK checksums + provenance manifest. Reproducibility verified by independent rebuild where feasible; signing may prevent byte-for-byte identity without controlled key.
- Release channel: `debug` signed with disposable local key; `internal` with controlled test key/package; `release` with hardware/offline-protected stable keystore. **Never commit release private key to GitHub**. Prefer locally signing verified unsigned CI artifacts or tightly controlled protected release signing. Public GitHub Releases artifact with SHA-256, changelog and release notes after approval. Use apksigner verify and zipalign; test adb install -r upgrade preserves data and signer identity.
- No automatic self-updater unless signed update metadata and explicit user consent. Before considering UpdateManager/PackageInstaller code, satisfy sideload and Android 2026–27 developer verification requirements.

**2026–27 sideloading reality:** Android developer verification's September 30, 2026 initial enforcement covers certain stores and regions; Google's guidance says direct sideloading outside those participating stores was not in that phase, with broader rollout scheduled for 2027. Limited-distribution registration for hobbyists (up to 20 devices) and ADB/advanced install flows exist. Investigate current verification status and choose registration/limited distribution before broad release. A signed APK alone is not a guarantee of identical install UX on all future Android devices. ADB installation remains supported according to official FAQ.

Refs: https://developer.android.com/developer-verification/guides ; https://developer.android.com/developer-verification/guides/faq ; https://developer.android.com/topic/performance/baselineprofiles/create-baselineprofile

## 13. Vertical milestones, sequence and explicit stop/go gates

**M0: Skeleton and research spikes (1–2 weeks estimate for one experienced full-time Android engineer).** Validate AGP/Kotlin/KSP/Hilt/Compose/Nav3/Room with compileSdk37 and API29 baseline; single-activity navigation, one sample widget, one static WallpaperManager call. Prove verified provider-URI import and one five-minute best-effort scheduling spike on physical Pixel. No shipping claims before actual test metrics. ADRs for decisions.

**M1: Golden-path alpha (3–5 weeks).** Photo Picker -> offline import -> collection -> seeded no-repeat rotation -> Home/Lock/Both -> 5-minute eligibility engine with truthful diagnostics -> reliable resume/reboot/corrupt input handling. Include Use Now/Add Next/Save Only, Next/Pause, basic accessible editor. Gate: A001–A015 from Rainbow Contract and new screenshot/share tests mandatory; physical Pixel validation.

**M2: Safe daily driver (3–5 weeks).** Folder SAF, full accessible crop/rotate/share, multiple collections, backup/restore, source integrity and exclusions, widgets/Quick Tile, complete event diagnostics, external editing. Gate: 7-day unattended test, failure-recovery matrix, no data loss and proven static mode behavior.

**M3: Rule and source expansion (4–6 weeks).** Scenes, nested collections, typed AST, fairness/weights, simulator, conflicts, approved external sources with provider health and licences, content attribution. Gate: 73 workflows classified as implemented/not yet/policy-limited, property/fuzz tests, reliable fallback offline.

**M4: Visual refinement and optional live mode (3–5 weeks).** High-fidelity design implementation, motion, wallpaper service visibility lifecycle, accessible transition controls, performance/thermal profiling. Gate: live disabled as default unless physical-device evidence supports it.

Estimates are tentative, assume one experienced engineer with functioning CI and available test devices, and may change dramatically after scheduler and OEM feasibility research. Reorder work by evidence; do not implement broad adapter catalogs before baseline reliability.

## 14. Go/no-go measurable acceptance

- **No silent success:** 100% of forced-failure test wallpaper applies report failure/retry; observable last success and next eligibility.
- **No import data loss:** 100% of injected process-kill/low-storage tests preserve preexisting collection and recover incomplete operations.
- **Determinism:** Same immutable rule context, clock and seed produce identical decision and explanation; all nested collections cycle-checked.
- **Performance initial budgets (targets to measure, not asserted):** <1.5 s warm app launch on Pixel 6 Pro; <250 ms library scroll interactions excluding slow provider fetch; user-triggered apply p95 <2s for predecoded local image on the Pixel, measured cold/warm and recorded; thumbnail cache bounded and no large bitmap UI parcel. Measure then refine.
- **Battery:** no unnecessary continuous rendering while wallpaper invisible; 24-hour idle drain attributable to Waltz measured under at least two scheduler modes, baseline controlled before launch.
- **A11y:** 100% critical journeys complete in TalkBack and 200% font scale without clipping or gesture-exclusive actions.
- **Distribution:** release APK verified signer, install+upgrade proven on API29 and 37 devices; no debug keys or analytics SDK.
- **Compatibility:** schedule guarantees disclosed separately for static, live-visible and optional experimental modes; documented OEM fallback.
- **Legal:** no default remote provider until API terms, attribution and per-image rights have been reviewed.

## 15. Pending decisions with bounded default answers

1. **Release app id/signing ownership:** pending user/repository-specific identity; do not invent a name requiring later migration.
2. **GPL vs Apache/MIT:** choose after dependency/license compatibility review; retain source notices and provenance. Recommend Apache-2.0 for modular adapter reuse if legally compatible, user approval required.
3. **Material You dynamic color:** user-toggle with Waltz accessible theme primary; default Waltz brand with system theme compatibility.
4. **Five-minute exactness:** best-effort default, no blanket exact-alarm/FGS workaround. Research real device constraints before advanced service commitment.
5. **Source expansion:** Wikimedia Commons/Openverse first subject to validation; no Unsplash/Pexels API wallpaper cloning without explicit contractual authorization.
6. **Storage policy:** app-private copy of selected cloud-backed photos, bounded preview/processing caches; storage dashboard and remove/original controls; do not automatically upload.
7. **Direct Lens integration:** no undocumented API; use Android share/chooser.
8. **Future Android verification:** if only personal devices, limited distribution or ADB; keep monitoring 2027 changes.

## 16. Initial implementation backlog ordered by dependency

A00 Create standalone Waltz Android source repository or app subtree (design files remain in general-purpose) and permanent application ID after review.
A01 CI toolchain pin, Android 17 build, API29 emulator, DI/navigation/Room schema tests.
A02 Pure command/rule/queue contracts and domain model; fixture-based verification.
A03 Photo Picker/SAF staging pipeline, bounded decoders, import ledger, local thumb cache.
A04 WallpaperManager gateway & physical Pixel proof-of-concept for home/lock, device capability record.
A05 Inexact/WorkManager scheduler adapters, five-minute active-use semantics, fake clock tests.
A06 Transactional outbox and journal, crash replay/reboot/clock-change work.
A07 Golden-path Compose screens, accessible crop/rotate and original preservation.
A08 Glance widget, TileService, shortcuts and Sharesheet all call common commands.
A09 Rights-checked source adapters and network resilience fixtures.
A10 Scene/rule simulator and explainability, nested collections and weight fairness.
A11 Seven-day real-device reliability/battery matrix and maintenance work.
A12 APK signing, reproducible release evidence, checksum, upgrade/restore rehearsal.

**References should be checked at implementation time** because SDK, vendor behavior and policy continue to evolve. This document is a build blueprint, not evidence that any app code, signing pipeline or runtime test already exists.

## Added UI rendering decision: Glimpse motion (2026-10-22)
Adopt the detailed [reel renderer and animation plan](GLIMPSE-MOTION-RENDERING-ARCHITECTURE.md) as the native Compose rendering authority. Add a first-development milestone for a measured, fake-data five-wide-window paper-reel Compose component with retained/cached masks, draw-phase angular transform, interruptible drag/settle, reduced-motion semantics, a non-animation-dependent browse state reducer, and benchmark screenshots/traces on Pixel 6 Pro. Optional AGSL embellishments and wallpaper live engine follow real device performance evidence, not as prerequisites.
