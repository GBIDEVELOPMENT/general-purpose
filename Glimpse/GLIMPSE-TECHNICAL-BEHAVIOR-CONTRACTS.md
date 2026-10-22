# Glimpse technical and behavior contracts: preimplementation specification

**Date 2026-10-22.** Normative cross-feature decisions, supplemented by [feature coverage audit](GLIMPSE-FEATURE-SPEC-COMPLETENESS-AUDIT.md), [native architecture](NATIVE-ANDROID-ARCHITECTURE.md), [reel UX critique](GLIMPSE-REEL-UX-CRITICAL-AUDIT.md), [current decisions](GLIMPSE-CURRENT-DECISIONS.md) and [motion architecture](GLIMPSE-MOTION-RENDERING-ARCHITECTURE.md). **No code/APK developed by this document.** This resolves reasonable semantics; OS/vendor or artistic decisions remain explicitly gated.

## 1. Vocabulary and provenance: stop the old/new naming collision

| Current user-facing term | Precisely means | Distinguish from |
|---|---|---|
| **Home** | The Glimpse control dashboard | Android **Home wallpaper** target; clarify with “phone Home screen” when both appear |
| **Collections** | Groups of owned/referenced assets | Sources, provider albums, rotation presets |
| **Discover** | Find external/licensed media and curated suggestions | Existing Collections; Glimpse-hosted feed does not exist |
| **Automation** | Rotation presets, named configurations, advanced rules, history | Basic browse; not a mandatory wizard |
| **Selected photo** | Image currently focused in Glimpse preview | Applied wallpaper, next scheduled wallpaper |
| **Current wallpaper** | Last successfully submitted/applied Glimpse wallpaper on named target, or unknown when externally changed | Selected browse photo |
| **Next photo** | Move **browse focus** one item | **Change wallpaper** or Queue next |
| **Change wallpaper / Change now** | Attempt a real immediate WallpaperManager operation | Browse next or schedule preview |
| **Show next** | Queue chosen image as next **eligible** rotation candidate | Immediate apply, guaranteed wall-clock time |
| **Start shuffle** | Enable active source/cadence configuration with precise best-effort disclosure | Force system to wake every N minutes |
| **Pause/Resume rotation** | Suspend/resume automated delivery on chosen destination(s) | Pausing a reel animation / freezing UI |
| **Hold until…** | Temporarily pin a chosen **applied** wallpaper against automation | Editing/deleting active rules |
| **Use this collection** | Set active rotation source, explicitly target and cadence | Opening/previewing a collection |
| **View all** | Conventional searchable/list/grid alternative for full library | Second photo wheel |
| **Reel / disk** | Visual, finite-window **selector of typed items** or noninteractive cover | Universal settings metaphor |

Keep internal `Rule`, `Scene`, `RotationCycle` as domain concepts even when navigation labels become shorter. Archived Waltz mockups should be stamped HISTORICAL in future updated decks; don't overwrite old user-facing words without noting meaning.

## 2. Command-to-state side-effect matrix (single truth across UI/widget/Tile/receiver)

Persistent domain objects use **stable IDs**, versioned recipes and monotonic operation IDs. A viewed image may have multiple collection memberships, editing variants and destination crops. UI pointer index or reel angle is **never** authoritative identity.

| Command | Allowed mutation | Forbidden side effect | UI confirmation / recovery |
|---|---|---|---|
| `SelectBrowseAsset(id)` | Temporary selection and per-collection remembered focus | WallpaperManager, queue cursor, scheduled eligibility | Hero/index changes, no device wallpaper change |
| `SelectBrowseCollection(id)` | Active browser collection and child focus restore | Starting/stopping rotation, changing actual wallpaper | Title/count/hero and child reel update; empty-state explanation |
| `OpenGrid`, `ReturnReel` | View mode, viewport position and same selected asset ID | Queue/applied changes | Maintain stable selected item |
| `ActivateCollectionForRotation(id,targets,policy)` | Versioned active rotation binding and next-eligible state | Apply immediately unless explicit user choice | Explain target, policy and scheduler limits |
| `QueueNext(assetId,target)` | One durable queue override/reservation | Apply currently, secretly consume unrelated bag | “Added next for Home” with cancel/reorder |
| `SetNow(asset,targets,recipe)` | Operation journal + OS apply attempt + last acknowledgment | Unintended other destination, deleting image, advancing browse cursor | Attempting → applied/partial/failed/unknown, per target |
| `ChangeNow(target)` | Resolve next eligible, reserve, apply, commit cursor on success | Consume queue on retry failure or unconstrained other screen | Preserve previous valid wallpaper if failure |
| `Pause(targets)` / `Resume(targets)` | Paused flags and due-window recalculation | Burst replay of all missed changes | Status and resume rule shown |
| `Pin(target,asset,expiry)` | Reversible override and expiry | Destroy underlying rule/queue order | “Held until …” with Release now |
| `ImportSelected(uris,targetCollection)` | Staged immutable private assets, membership and provenance | Source mutation, wallpaper apply by default | Counts, estimated storage, per-file retry |
| `SaveRecipe(asset,scope,recipe)` | Reversible image/destination edit revision | Source bytes modified, wallpaper applied | Save location and undo version |
| `ExportOrShare(asset,variant)` | Temporary rendered payload, URI grant and export log | Scheduler, queue, original asset bytes | Export prepared/chooser opened; not “recipient received” |
| `HideAsset(id,scope)` | Exclusion tombstone with Undo/reveal | Deletion from storage or all memberships unless explicit | Scope explanation and restore path |
| `SimulateFuture(context)` | Ephemeral simulation model only | Real schedule writes, wallpaper apply or shuffle cursor | “Preview only, timing not guaranteed” |
| `CreateRule`/`EditRule` | Validated, versioned AST and activation state | Unexpected immediate wallpaper change | Save/activate distinction; conflict and prerequisites |

Use *one command gateway* from UI, widget, shortcuts and permitted external intents. De-duplicate based on command identity/time-window/target. Distinct target requests may share a high-level intent but each destination gets its own outcome. Background events cannot silently execute an unrelated immediate foreground command.

### Applied truth and unknown external state

Android can report an application ID/return or throw on `WallpaperManager`, but on modern releases Glimpse cannot universally read back arbitrary system wallpaper bytes. Preserve **`lastAcknowledgedAppliedByGlimpse`**, last attempt timestamp and (where API supports) known ID; expose **unknown/unverified** if the OS was changed externally or reconciliation lacks sufficient evidence. Never say “currently installed” with certainty from stale DB alone. Distinguish *platform accepted* from *visually observed by user* in diagnostics.

## 3. Durable media identity, sources and lifetime

- `SourceEntry`: provider ID, external item ID/version, current capability status, attribution and licence metadata. Source URL strings are not canonical image IDs.
- `ImageAsset`: immutable or content-addressed imported bytes, hash, dimensions, orientation, colour profile, rights/provenance, validation state. Exact same bytes can have multiple logical source records.
- `CollectionMembership`: collection ID + image ID with ordering, tags, exclusions and audit history; membership never owns image bytes.
- `ImageVariant/EditRecipe`: source ID, ordered non-destructive operations, destination and revision. Home/Lock variants share original bytes.
- `QueueState`: destination, activation/config revision, deterministic seed, eligible filter revision, reserved IDs, cursor and applied history. Real position in queue != visually selected gallery photo.
- `AppliedState`: target ID, operation ID, acknowledged image ID and recipe, platform result confidence, last actual successful timestamp.
- `BrowseState`: screen/collection, focused image ID, view type (reel/grid), sorted order ID, visible offset and transient angle; restoration keyed to IDs.

**Lifetime:** staging file → metadata/codec/hash validation → atomic promotion into private storage → membership commit → cache thumbnails; rollback temp on import failure without erasing old assets. Asset deletion only after explicit user delete and reference count/retention scan; removing collection alone doesn't delete external originals. Source grants can disappear; mark missing/relink rather than silently selecting placeholder as wallpaper.

## 4. Rule execution and concurrency: the happy case is not enough

- Take immutable snapshot of relevant event/clock/target capabilities; resolve matching rules and filters in a pure engine. Priority = explicit user action/override, safety gate, pinned hold, narrower rule, active preset, fallback as specified; **global Pause and safety restrictions are hard gates**. Define manual ChangeNow policy explicitly when paused rather than surprising exceptions.
- Selected candidate is **reserved**, not consumed, before expensive decode/apply. A reservation is keyed by `{target,rotationRevision,eligibleWindow,assetId,operationId}`. On transient failure, retry *same* candidate unless explicit fallback policy says otherwise. On confirmed success, atomically commit cursor/history.
- If two commands race to target same destination, serialize through one destination-aware executor; `Both` has per-destination result and partial completion. Later user command supersedes eligible background operation only when not already irreversibly applied; log race rather than rewriting history.
- Persist event lifecycle: `SCHEDULED → ELIGIBLE → RESERVED → PREPARED → ATTEMPTED → ACKNOWLEDGED_APPLIED / FAILED / UNKNOWN / CANCELLED`. A failure after platform call but before DB update is **UNKNOWN** until reconciliation, not safe to blindly replay.
- Use wall-clock for user policy, monotonic clock for cooldowns in one boot, stable timezone/event IDs for DST/reboot. Reboot resets elapsed realtime semantics; reconstruct due policy from persisted absolute time/zone.
- Across app upgrade and restore, unknown AST versions are disabled with explanation, not silently misinterpreted. Detect cycles in nested collections, bound evaluation depth and filtering cost.

## 5. Scheduling: four separate promises, not one rotating disc

| Mode | Technical baseline | User-facing language | Unsupported claim |
|---|---|---|---|
| Foreground explicit change | Immediate accepted user request on app/widget/tile when OS allows | “Change now” and real outcome | Guaranteed pixel-visible success on every launcher |
| Static best-effort cadence | WorkManager >=15 min periodic, chosen inexact alarms/foreground triggers for shorter intervals; durable eligibility | “Every 5 min while eligible; Android may delay” | Exact five-minute background wake |
| Visible live wallpaper (optional) | WallpaperService.Engine when surface genuinely visible; event-driven/visibility-bound rendering | “Change while this wallpaper is visible” | Runs visibly across every foreground app |
| Experimental OEM-specific event mode | Documented eligible receivers/notifications with explicit permission/lifecycle | “Available on this device” | All unlock, weather and location triggers universally available |

Do not request exact-alarm permissions or foreground-service exceptions as a workaround for wallpaper cycling. Distinguish planned eligible time, worker invocation time, OS apply attempt, acknowledged result and skip reason. No catch-up burst. Persist pause, selected destination, rule revision and next eligibility through reboot. Source failure uses verified prepared fallback if authorised, otherwise keep current wallpaper and explain.

## 6. Image pipeline, framing and sharing

Input sources: Photo Picker (user-selected local/cloud), SAF tree where allowed, inbound Sharesheet, user-invoked clipboard, capability-vetted remote adapter. None implies continuous Google Photos album sync; if W08 is pursued, require a separate consented integration and provider rights audit.

Import safety: streaming and capped temp space, content sniff/codec validation, maximum decoded pixels, EXIF orientation, durable hash, default stripping of location metadata when exporting and no unexpected remote transfer. Cryptographic SHA-256 exact identity; perceptual similarity only advisory and user-reviewed.

Edit order: apply EXIF orientation → source-space normalized transform/focal and crop → destination composition → optional filter/effect stack → bounded colour-profile-aware rasterization → final wallpaper/share output. **One canonical recipe renderer** must serve preview/export/apply; Coil is for image loading/thumbnail previews, never the sole source of final pixels. Always retain source and recipe revisions, support Undo.

Sharing: render requested original or crop/edited output into short-lived `FileProvider` URI with temporary read grants and Android chooser; never infer that ChatGPT/Lens/Drive/email handler exists from the name. Explain loss of original pixels and metadata when editing. Support multiple images with bounded batch assets, cancellation cleaning and privacy-aware EXIF choice. Export confirmation means **prepared/handed to platform**, not remotely delivered.

Remote rights: provider searches need term/rate limit checks; source licences are metadata reported by provider, not legal certification. Store creator, attribution, URL, licence evidence and retrieval date. Disable sources on API/policy change while preserving already legally held user media.

## 7. Accessibility, visual and reel causality

A reel exists only to choose a typed visually recognizable member of a finite ordered set. Photo IDs, Collection IDs, destination-scoped selections and image variant recipes are appropriate; arbitrary Rule AST nodes, percentages, colour temperature, privacy permissions and schedule times are not.

A dual reel requires *two clearly distinct state ownerships* and a legitimate relation: e.g. `SelectedCollectionId` → `SelectedImageId`, or `PreviewHomeImageId` ↔ `PreviewLockImageId`. Each reel owns one fixed pointer and visual label; the child must know how selection changes when the parent changes. Same-screen changes always explicit preview-only unless applying.

Accessible controls for reel: Previous photo, Next photo, View all, photo position/count, and independently labelled Set as wallpaper. TalkBack/Switch Access must never depend on precise angular finger path. Minimum hit region 48dp; do not anchor to clip-hidden wedge. At large text, collapse secondary visual reel first. Reduced motion changes rendering not the semantic state transition.

Custom motion physics is downstream from selection identity: drag uses temporary angular position and velocity, settle picks legal ID, rebases hidden slots without changing selected source mid-visible frame; screen stops animation when backgrounded. Do not decode on UI thread or queue unlimited notches. One active touch-controlled reel at a time on a phone; avoid double GPU-layer allocation until measured.

## 8. Technical implementation decisions and their bounded alternatives

| Concern | Preferred technique | Acceptable fallback / decision gate |
|---|---|---|
| Native shell | Kotlin, Compose/Material3, Navigation 3, ViewModel/StateFlow | Pin toolchain only when scaffold exists; no unmeasured framework switch |
| Durable state | Room with tested versioned migrations, separate DataStore for small preferences | Backup manifest and source remap for loss of URI grants |
| Pure selection | Kotlin independent `core:engine` with seeded deterministic strategies | Rule/queue simulator must call same engine |
| Async work | Coroutines, WorkManager for durable inexact work, select AlarmManager events only if legal | No secret 5-minute repeating service |
| Wallpaper delivery | Single platform gateway and journal-backed target executor | Acknowledge partial/unknown result rather than fake atomic apply |
| Photo thumbnails | Coil with size negotiation, disk cache and prefetch | Colour/photo codec handling validated against final renderer |
| Hero/wheel | Compose Canvas/drawWithCache + selectively cached drawing layer/graphicsLayer | Try alternative mask techniques by measured Pixel 6 Pro trace |
| Paper material | Source-approved raster/vector texture cached, no runtime noise generator on drag | Simpler static paper if GPU overdraw problematic |
| Animation | Interruptible `Animatable`, velocity-aware bounded spring, tactile notches | Full reduced-motion instant alternative |
| Two-reel layout | Shared renderer instances, independent controllers, bounded concurrent decode | Compact fallback picker + one full reel |
| Widgets/tile | Glance, TileService, command gateway, bounded bitmaps | Disabled action with capability explanation |
| Remote provider | OkHttp typed adapter, strict rate, media validation, rights policy | Hide unqualified API provider |
| Source packaging | Signed APK with reproducible manifest and stable application ID/signing key | No APK work in planning-only phase |

Do not over-modularize. Existing native architecture proposal ~11 Gradle modules is an upper planning sketch, **not a required starting count**. Likewise arbitrary numbers in performance budgets are targets to measure, not proofs.

## 9. Security, lifecycle and resource boundaries

- Never request `MANAGE_EXTERNAL_STORAGE`, AccessibilityService privileges, always-on clipboard access, or broad package visibility for ordinary wallpaper jobs.
- External automation receiver must require explicit authorization/token/permission and validate source/target/rate; no arbitrary URL/file execution through exported intents.
- Private content URIs to recipient apps are intentionally temporary; revoke/clean up when safe and cap export lifetime. Never include original geo coordinates inadvertently.
- Application files versus evictable `cacheDir`: verified offline imports are **not** disposable thumbnails. A cache-clear action may never delete the last offline copy of an imported cloud image.
- Android profiles and external displays are not a shared universal wallpaper namespace Glimpse can command at will. Capability/UI gating before claiming.
- Image thumbnail memory and rendering GPU area are bounded to viewport, not full reel/world coordinates. A 37 MB source artwork archive is build-time source material, not runtime wallpaper media bundled by default.
- Notify state changes using stored IDs and typed flows, no accumulating uncollected listeners or nonstop animations. WorkManager cancellation and force-stop caveats explicit.
- Human-readable event journal uses bounded retention and scrubbed export; no mandatory telemetry backend.

## 10. Acceptance traces: every result tied back to an intent

| User task | Minimum executable story (future) | Acceptance evidence |
|---|---|---|
| W01+W04 | Select cloud media → verified offline copy → Start 5-minute eligible rotation → airplane mode → change now | Original saved; real applied ID, correct counts and truthful schedule |
| W54 | Apply next twice → Undo → fail OS apply → resume queue | Restores previous image, no skipped IDs, outcome journal accurate |
| W57 | Preview next day's timeline → close → check device wallpaper and persisted queue | Zero OS changes and zero queue consumption |
| W60 | Pin until tomorrow → candidate due event → expiry → resume | No background override during hold, deterministic first post-hold selection |
| F071 | Receive screenshot → crop/rotate → Just save → Show next → Use now | Three distinct effects; original unchanged |
| F073 | Share original vs crop to Android target → cancel → return | Correct temporary output, no wallpaper changes, no false recipient success |
| Dual Collection→Photo | Change parent while child wheel is settling → inspect/choose photo | Child cancels/rebinds by IDs, no phantom current image, no OS apply |
| Dual Home/Lock | Preview different photos in each → Apply Lock only → unsupported mode | Home unaffected, lock result independently reported, unavailable action disabled |

**No claim that these traces have run.** First implementation must supply actual source refs and physical-device evidence, using [visual acceptance procedure](GLIMPSE-REFERENCE-ACCEPTANCE-PLAN.md). For every feature, work is accepted only when there's a verified action, data effect, failure/rollback policy, accessible alternative and UI location.

## 11. Known unsolved and intentionally nonpromised capabilities

- Continuous auto-sync of arbitrary Google Photos albums via system Photo Picker.
- Guaranteed exact static wallpaper change at five-minute intervals under deep sleep/Doze.
- Arbitrary overriding of Android wallpaper-derived system Dynamic Color palettes.
- Reliable arbitrary wallpaper control on attached external displays and across user profiles.
- Universal detection of every lock/unlock without intrusive privileges or an always-running supported mechanism.
- Guaranteed live-wallpaper independence for Home and Lock across all OEMs.
- Capability to know actual externally changed current wallpaper bytes on modern Android.
- Provider rights verification based solely on search metadata.
- Guaranteed receiver app share completion.
- Five huge reels at once on a compact phone with 200% text and Android system navigation.

These requests remain in the [feature register](GLIMPSE-FEATURE-SPEC-COMPLETENESS-AUDIT.md) with a gate. **Do not silently drop, fake, or claim them implemented.**

**Research:** [Android WallpaperManager API](https://developer.android.com/reference/android/app/WallpaperManager), [Compose semantics](https://developer.android.com/develop/ui/compose/accessibility/semantics), [WorkManager periodic minimum](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work), [Android Photo Picker](https://developer.android.com/training/data-storage/shared/photopicker), [NN/g mobile carousel limitations](https://www.nngroup.com/articles/mobile-carousels/).
