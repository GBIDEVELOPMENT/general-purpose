# Glimpse: feature-by-feature specification completeness audit

**Date:** 2026-10-22 · **Status:** normative pre-build contract and risk ledger; **no implementation exists**. Companion to [current decisions](GLIMPSE-CURRENT-DECISIONS.md), [technical contracts](GLIMPSE-TECHNICAL-BEHAVIOR-CONTRACTS.md), [reel critique](GLIMPSE-REEL-UX-CRITICAL-AUDIT.md), [70 human workflows](70-HUMAN-WORKFLOWS.md) and [screenshot/share features](SCREENSHOT-AND-LENS-FEATURES.md).

## Method, forwards and backwards

**Forward:** user scenario ID → intent and expected feedback → proposed native architecture → state transitions and fallbacks → screen entry → implementability/acceptance. **Backward:** screen/reel action → domain command → persistent record → Android/app effect → original user scenario. Any orphan is a requirement gap (no interface), invention (no user intent), or unacknowledged platform gamble.

Every feature needs: preconditions and permissions; user-facing entry; typed affected state; whether it changes the real wallpaper; failure/offline behavior; persistence/undo or backup; accessibility alternative; minimal verification. This register states what is reasonably clear **now** and flags research-dependent paths rather than making impossible promises.

**Tier labels**: M1 core first usable app; M2 personal daily driver; M3 expert/provider functions; M4 optional live/advanced experiments. They are *ordering only*, not completed work. **Gate labels:** `D` implementation spec sufficiently defined for first prototype, `R` remaining interaction/technical research, `P` OS/provider permission or feasibility gate, `A` visual accessibility/design approval. None signifies running code.

## All 73 workflow contracts

| ID | Job and recommended implementation contract | Actual consequence and UI/fallback | Gate / tier |
|---|---|---|---|
| W01 | Selected Google Photos rainbows → named collection, local verified imports, seeded no-repeat queue, 5-minute active-use eligibility | Collections > Add photos > Rainbows > Start; report imported/duplicate/failed, last applied and next eligible; no exact background promise | D/P · M1 |
| W02 | ACTION_SEND and SEND_MULTIPLE share-target import into staged private copies | Quick-import sheet chooses collection; just save doesn't apply; reject revoked/malicious URI with retry | D · M1 |
| W03 | SAF document-tree access with independent source records and virtual membership | Unified collection without relocating originals; explain missing SD/permission revoked and remap | P · M2 |
| W04 | Stream chosen cloud-backed picker content to atomic private immutable copy with hash and MIME checks | Offline playable after verified import; cancel/retry missing network; never claim future cloud auto-sync | D/P · M1 |
| W05 | Local perceptual hash, aspect-aware matching and non-destructive duplicate suggestion | Review and choose exclusions; never silently delete concert originals; threshold needs photo trials | R · M2 |
| W06 | Represent favorite flags separately from membership and source metadata | Unstar filters future selection, not deletes shared image; provider stars require exposed API/grant | P · M2 |
| W07 | Persist import timestamp and temporary new-only view/query; avoid loading 12k in memory | New this week selector with real count; automatic expiry returns to ordinary pool | D · M2 |
| W08 | Import snapshot only from native picker; ongoing album sync requires separately approved provider API | Label Imported on date, not Linked album; provide manual Refresh import unless legal sync is proven | P · M3 |
| W09 | Expiring override with five explicitly selected asset IDs and source collection identity | Use selected for 1 hour; count, expiry and Return to schedule shown; no destructive reordering | D · M3 |
| W10 | Virtual union/composite edges to original collection IDs; cycle check and stable identity dedup | Create mix, choose membership; removing mix leaves child collections intact | D · M3 |
| W11 | Observe permitted wake/visibility events with monotonic debounce and durable idempotency | Change on eligible wake where supported; disclose missed/unsupported events, no covert AccessibilityService | P · M3 |
| W12 | Local time-window triggers with named scenes and deterministic precedence | Weekday/evening presets; preview timeline and missed-event policy | D · M3 |
| W13 | Clock window event only while eligible/awake; no default exact-alarm special access | Set target time and tolerance; if unavailable, show Missed/Next eligible rather than fake precision | P · M3 |
| W14 | Day-keyed first-user-activity trigger with persisted last-fired day and timezone | One morning change when recognized; skip duplicates after app/process restart | P · M3 |
| W15 | Solar times from chosen city/location plus optional documented weather provider | Opt-in location/weather; offline solar only; explain fallback and stale data | P · M3 |
| W16 | Nth-weekday calendar predicate and priority exceptions with DST-aware calendar | Explicit first-Saturday-over-Saturday preview; finite sample dates tested | D · M3 |
| W17 | Charging observed state controls rotation eligibility interval, not background polling | Show charging/normal schedule now active; last applied doesn't catch up in bursts | P · M3 |
| W18 | Battery Saver high-priority suspension with no catch-up burst | Paused by Battery Saver, Resume policy and one next change shown | D/P · M2 |
| W19 | Manual trip preset or user-approved foreground location mode; no undisclosed background location | Travel mode with explicit expiry/return; geofence automation only if platform/policy feasible | P · M3 |
| W20 | Deterministic seeded pick of one eligible time inside daily interval | Explain chosen time, OS tolerance, and next retry; do not promise ≤10m under sleep | P · M3 |
| W21 | Same source photo, two independent destination recipes: blurred home / sharp lock | Preview both and apply with per-target partial-success accounting; unsupported OEM explains limitation | P · M3 |
| W22 | Independent destination queues and event triggers for lock versus home | Lock event mode only where truly observable; preserve static home selection | P · M3 |
| W23 | Palette correlation from local metadata/colour analysis, enforce different asset IDs | Home/Lock compare preview; if no matching pair found show constraint explanation | R · M3 |
| W24 | Theme-change condition selects variant by stable image family ID; never double-consume shuffle | Light/dark variants shown; if system event not delivered defer and explain | P · M3 |
| W25 | Advisory lock clock-safe area with manual override and contrast sampling | Explain real lock clock placement is OEM-dependent; no guarantee of overlaid widgets | P · M2 |
| W26 | Per-launcher focal/safe-area recipe and preview margins without API-dependent false promises | User tests swiping launcher pages; stored crop remains reversible | P · M2 |
| W27 | If accessible, per-display composition preview using display metrics; otherwise graceful single display | Do not promise OS can set arbitrary external-display wallpaper from third-party app | P · M4 |
| W28 | Per-fold-state crop profiles keyed by window posture/window metrics where permitted | Responsive in-app previews; actual external wallpaper behavior device-qualified | P · M3 |
| W29 | Offer crop/colour adjustments and in-app Dynamic Color toggle; do not claim arbitrary OS Monet palette override | Explain wallpaper system colour extraction is OS-controlled; unsupported manual palette control absent | P · M3 |
| W30 | Global no-automatic-motion preference honored by app and optional wallpaper service | Same actions/state and accessibility feedback without animated reel or crossfade | D · M1 |
| W31 | Opt-in NASA APOD source with image-only filter and per-item rights review | Source metadata, attribution, offline fallback; no right to reuse all APOD assets implied | P · M3 |
| W32 | Commons MediaWiki query and attribution/license provenance, image-only filters | Source pages and license labels accessible; verify rights before using as wallpaper | P · M3 |
| W33 | Capability-advertising provider adapters only after current API/terms audit | Provider settings explain sign-in/key needs; no Glimpse account or hidden backend | P · M3 |
| W34 | Independent source circuit breaker, bounded retry and cached offline fallback | Source status and why offline pool used; no repeated notification spam | D · M3 |
| W35 | Persist fair weighted pool selection (70/30 target over documented window) and canonical hash dedup | Weight controls with preview; show fairness semantics and how few remote photos affect target | R · M3 |
| W36 | Moderation queue with user approval before candidate joins automatic eligible pool | Sunday review if eligible, no automatic insertion; pending count and skip choice | D/P · M3 |
| W37 | Restricted HTTPS RSS/Atom fetch, explicit source authorization and media rights checks | Sample preview, rejection of private/internal addresses and dangerous redirects | P · M3 |
| W38 | Require unmetered Wi-Fi if explicitly requested; handle Android network cost and reachability truthfully | Ask before metered user-initiated override, no silent cellular downloads | P · M3 |
| W39 | Local global creator/artist exclusion keyed by stable identity with conflict policy | Hide from future selection, don't delete private image; restore excludes later | R · M3 |
| W40 | Provider policy/version and health gating, no remote kill switch required | Disable incompatible adapter on update; explain paused source and active offline schedule | D/P · M3 |
| W41 | Versioned cycle counter for 3-colour/1-mono days plus bounded daily exception | Rule simulator shows exact active cycle and override; no conflict ambiguity | D · M3 |
| W42 | Acyclic nested composite collections with weighted child choice and child shuffle bag | Fair child distribution; trace exact supplying child and skip missing | D · M3 |
| W43 | No-repeat shuffle with adjacent perceptual similarity constraints and bounded relaxation | Never deadlock with similar/small pool; explain quality compromises | R · M3 |
| W44 | Canonical image equivalence dedup and persisted 14-day recent-use filter across all collections | On insufficient eligible photos, prompt relax restriction or keep current | R · M3 |
| W45 | Deterministic modulo-10 injection and history persistence with failure/reservation semantics | Visible every-tenth source rule and simulation; skip unavailable favorite safely | D · M3 |
| W46 | Predicate-based eligibility filter before shuffle reservation commit | Excluded bright candidate not counted as shown; daylight rule and explanation | D · M3 |
| W47 | Alternating typed mood pools with independent per-pool shuffle state | No same mood twice if next mood populated; deterministic fallback when empty | D · M3 |
| W48 | Birthday calendar exception priority bounded by accessibility safety policy | Celebration rule never overrides reduced-motion/photosensitivity limits | D · M3 |
| W49 | Debounced three-manual-skips event + daily idempotency limit | Trigger only on genuinely applied changes; explain skipped behavior | D · M3 |
| W50 | Trace recursive resolution path through child collections and rules with IDs | Explain why selected image, named nested sources; no private URI in exported trace | D · M3 |
| W51 | Manual normalized source-focal crop overriding optional opt-in detection | Pin crop profile per destination; Undo and raw source intact | D · M2 |
| W52 | User-chosen blurred-extended canvas variant preserving original pixels and aspect | Compare crop vs blur extension; memory/quality limits on tiny images | D · M2 |
| W53 | Collection-wide non-destructive adjustment recipe with per-item bypass flag | Preview global effect and three exempt files; no destructive source write | D · M3 |
| W54 | Reversible applied-image history and shuffle reservation cursor snapshot | Undo restores prior target(s) with explicit OS apply; failures do not corrupt queue | D · M2 |
| W55 | Persistent exclusion tombstone by asset and chosen scope, with restore UI | Don't show again with scope described; Undo; avoid deletion | D · M2 |
| W56 | Icon/clock/safe-area mock overlay using adjustable device/profile guides | Advisory mock, not guaranteed actual launcher icons; editable focal positioning | P · M2 |
| W57 | Pure read-only rule simulator producing sequenced filmstrip from hypothetical future context | No actual Android wallpaper update; clearly say simulated vs guaranteed schedule | D · M3 |
| W58 | Independent Home and Lock normalized crop recipes on one immutable asset | Side-by-side preview when supported; save both without duplicating source file | D · M2 |
| W59 | Compute source effective pixels after crop at target resolution; warn at threshold | Offer safer framing / fit; never silently claim upscaled image is higher detail | D · M2 |
| W60 | Destination-scoped pinned hold with start/end time and resume policy | Hold until tomorrow with current wallpaper preserved; show time and release action | D · M2 |
| W61 | Glance thumbnail + explicit Skip command; memory-bounded RemoteViews | Next target shown only if actually selected; widget click reports result via app command gateway | P · M2 |
| W62 | TileService destination-scoped command with lifecycle handling | Explicit Lock-only action, safe when unavailable/unlocked; tile doesn't run rule engine itself | P · M2 |
| W63 | Validated explicit external Intent/PendingIntent adapter, token/permission checks | Tasker-friendly documented result/event, user-granted commands only | P · M3 |
| W64 | Versioned manifest with collection/crop/rule IDs, remap images by hash/source | Restore preview reports missing files; no silent state or credential corruption | D · M2 |
| W65 | Optional encrypted export of settings; raw image inclusion off by default | Explain metadata/images/secrets choices; require decryption credentials and test wrong key | R · M2 |
| W66 | Compose semantics, keyboard/D-pad, named commands for all advanced rules | Rule editor complete without tactile reel or gesture-only input | D/A · M2 |
| W67 | 200%+ scalable text, WindowMetrics responsive breakpoints, logical focus | Reflow all critical controls; compact photo reel collapses before text truncation | D/A · M1 |
| W68 | Reduced intensity/motion and no involuntary rapid flashes across app/live optional | Enforce upper brightness-change/flash safety, no override by rules | R/A · M1 |
| W69 | Android profile-isolated app data and explicit support matrix for per-user wallpaper behavior | No cross-profile permissions/access claims; disclose unsupported behavior | P · M3 |
| W70 | Per-operation reason journal scheduled→eligible→attempted→applied/skipped/unknown | Show why rotation failed and repair path; preserve privacy, retention limits | D · M2 |
| F071 | Screenshot Share/Picker → stage copy → rotate/crop → choose collection → Save/Show next/Use now | Separate collection/queue/current wallpaper outcomes; source intact, retry URI failure | D · M1 |
| F072 | Offer Android Sharesheet to compatible Lens/visual search target if installed | Don't promise private Lens API or specific app destination; general share fallback | P · M2 |
| F073 | Universal original-versus-crop sharesheet export to supported receiving apps | Target URI grants and EXIF location choice, success only for export/handoff not remote completion | D · M1 |
## Gap and risk classification

### Critical (P0) gaps exposed by reversing the trace

1. **Naming/authority:** current PRODUCT-SPECIFICATION and NATIVE-ANDROID-ARCHITECTURE still have user-visible **Waltz, Today, Rhythms, Scenes, Rules, Next** while Glimpse uses **Home, Collections, Discover, Automation, Next photo/Change now**. Do not bulk replace domain terms: Scene and Rule remain valid **internal concepts**. Use [current decisions](GLIMPSE-CURRENT-DECISIONS.md) and an explicit glossary.
2. **First-action state:** one “Next” button cannot cover browse-next, rotate-now, queue-next and simulator-next. Commands and copy must be distinct. See [typed state contract](GLIMPSE-TECHNICAL-BEHAVIOR-CONTRACTS.md).
3. **Reel scope:** previous designs specified a reel *image browser* but not a selector for collections, destinations or visually previewable variants. [Critical reel audit](GLIMPSE-REEL-UX-CRITICAL-AUDIT.md) now offers candidate types with strong rejects for arbitrary settings.
4. **Native schedule limitation:** WorkManager cannot promise a periodic five-minute wake; background wake/lock/geofence/precise 8pm claims are gated proposals. Sideload status does not relax Android battery rules. Confirm actual hardware/API behavior before advertising automatic results.
5. **Google Photos auto-sync:** Photo Picker provides user-selected media, not ongoing whole-album sync. W08 must remain explicit stretch feasibility, not a standard supported adapter.
6. **System-wide dynamic palette:** W29 requests changing OS extracted Material You colours. Glimpse can control its own theme and image content; arbitrary global wallpaper-derived colours may not be exposed to third-party apps. Label unsupported until verified.
7. **External display / multi-profile**: W27 and W69 cannot promise cross-display/system-user wallpaper mutation; Android capabilities and user boundaries first.
8. **Actual visual references:** v4 screenshots omit many required actions and edge states. They are art, not exhaustive UI specs. Bind reference regions + machine screen contract before implementing.
9. **Permission/rights:** remote sources, weather and location need explicit legal/capability gate and visible absence states. Metadata licensing claims must not become fabricated rights certification.
10. **Asset publication:** new tactile binary PNG is in GitHub, but the full deck source ZIP and PDFs may still need publication; verify current tree and hashes rather than repeat stale “nothing uploaded” claims.

### Design-open (P1) decisions to evaluate, not dictate

- Single large photo reel versus asymmetric **Collection → Photo** dual reels on larger screens; compact portrait fallback collection picker.
- Optional **Home/Lock** pair visual editor, with independent application actions and capability gating.
- Recent-history or crop-variant reel, only when it improves preview/recovery relative to list/cards.
- Rule entry/scene configuration naming; whether Automation needs distinct Presets/Rules/Activity subsections and contextual cross-links.

### Tech-open (P1/P2) proof spikes

- Physical 5-minute active-use scheduler and how status is exposed across battery modes.
- WallpaperManager result reconciliation when a wallpaper is changed *outside* Glimpse: API visibility is limited on newer Android; report “unknown/last confirmed” rather than falsely knowing current home/lock image.
- Device-specific Home/Lock separation, launcher scrolling, external display, foldables.
- Photo Picker URI and cloud-stream behavior, including offline verification.
- Real component frame-time and overlay/clip GPU performance for one or two large paper reels.

## Pre-build acceptance rule

Feature rows are **specified hypotheses**, not declared platform implementations. Before shipping any row, its owning PR must link a real device/API capability record (if gated), data transition test, accessibility alternative and visible no-success/failure state. M3/M4 rows do not block the M1 personal APK.  
