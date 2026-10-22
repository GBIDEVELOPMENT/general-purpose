# Waltz: Screenshot Quick Capture and Google Lens Handoff

Status: approved product requirements, implementation pending. Updated 21 October 2026. These additions extend the quick-start contract, not the advanced rule grammar.

## Requirement F071: Screenshot to collection in seconds

**Human need:** "I just captured a screenshot, and I want to paste it into Waltz, straighten or rotate it, crop out the irrelevant bits, save it with my rainbow wallpapers, and decide whether it's the wallpaper I see right now or simply joins the rotation."

### Entry routes (equivalent results)
1. Android screenshot toolbar -> Share -> Waltz, by exported ACTION_SEND image/* receiver; accept ACTION_SEND_MULTIPLE as optional batch intake.
2. Waltz -> prominent **Add** -> **Paste image**, reading a user-initiated image MIME ClipData URI from ClipboardManager; if unsupported/expired clipboard, explain and offer Photo Picker or Share.
3. Waltz -> **Add** -> Photos / Files with system Photo Picker or SAF.
4. Optional pinned launcher shortcut or Quick Settings tile opens the user-driven quick-import sheet, but never captures the screen itself.

No background clipboard polling, accessibility-service screen interception, MediaProjection acquisition, blanket photo-library permission, or invisible surveillance. Android screenshot interfaces vary across OEMs; sharing is the portable primary route. A screenshot may be saved in the gallery yet *not* available through clipboard; show the picker fallback prominently.

### Proposed 3-stage quick sheet
**1. Edit**: full-screen edge-to-edge immersive image, pinch/drag to pan and zoom; prominent 90-degree clockwise/counterclockwise rotation, fine straightening (-45 to +45 degrees), Reset, Undo/Redo, screen ratio guide with home/lock safe areas, free crop, portrait preset, pixel-resolution feedback. Keep EXIF orientation correct. Avoid destruction: store original and edit recipe separately; save render for wallpaper.
**2. Place**: target collection (last used preselected, searchable, create new inline); duplicate detected? add membership without copying redundant original unless user chooses a distinct edited variant. Provide explanatory storage-size estimate for large imports.
**3. Finish**: three mutually exclusive options:
- **Use Now**: save in collection, immediately apply on chosen destination(s), pin as the current item in active rotation, then resume normal schedule from now by default; optional “hold this wallpaper” period.
- **Add Next**: save then queue as the next eligible rotation item without altering currently shown wallpaper.
- **Just Save**: save to collection, respect existing shuffle/rotation queue and do not apply now.
Destination choice Home / Lock / Both appears if supported. Defaults remember last selection but never silently change both destinations. Completion confirms photo saved, current wallpaper status, next eligible change, and Undo.

### State and integrity semantics
- Single transactional content-import boundary: stage bytes from granted URI into private temp storage; verify MIME, pixel bounds, actual decode and size; hash for duplicate detection; persist immutable source plus crop/rotation recipe; commit collection membership in Room; atomically publish staged bytes; reconcile crash interruptions.
- Clipboard URI permissions can be temporary: persist a local copy before editing. Never store ephemeral provider URIs as the sole long-term image.
- Apply wallpaper and DB mutation are not one atomic operation across Android APIs: record intent, attempt application, record real result, expose retry and diagnostics; failed wallpaper apply must not lose imported image.
- Re-edit original, view history, restore crop, remove from lineup without deleting source. Explicitly distinguish “collection membership” vs “current wallpaper” vs “next queue position”.
- Support PNG, JPEG, WebP and supported HEIF/AVIF via Android decoders; cautiously reject unexpected file content, giant dimensions, animated/multiframe ambiguities; scale previews without full-resolution OOM.
- Content remains on-device. Deletion of imported original must be explicit and independently confirmed.

### UX/accessibility
- User can reach **Share to Waltz -> Rotate -> Crop -> Use Now** in approximately five actions with default collection and destination.
- Rotation has labelled controls, not gesture-only operation. Screen-reader crop alternative uses accessible four-edge sliders and numeric angle input. Every action has announced results.
- Preserve touch target >=48dp; larger text, magnification and landscape orientation; image preview offers contrast outline and safe-area labels, never relies on colour alone.
- Pending “Use Now” shows actual apply result, not an optimistic success toast.

## Requirement F072: Search any image with Google Lens

**Human need:** "I see a photo in my wallpaper collection and wonder what that building, plant or object is. I want to send it to Google Lens right there without exporting it manually or changing my wallpaper."

### Product surfaces
- Image detail -> overflow **Search with Google Lens** with familiar search icon and “Sends a copy to Google” disclosure the first time.
- Long-press grid item -> Search with Lens (where available); current wallpaper activity card -> same operation; batch selection excludes Lens because Lens is inherently image-at-a-time.
- Choose **Original image** (default) or **Wallpaper crop** from a non-blocking sub-choice, remembering last preference. The image is not added to an app-specific shared cloud.

### Android implementation
- Google does not supply Waltz a guaranteed stable, general-purpose public Lens image-submission API. Do not hardcode undocumented private actions or component names, scrape Google Photos, or claim the target is installed.
- First prefer a validated public share/intent handler when actual device package resolution shows a capable Lens destination. Otherwise use Android Sharesheet ACTION_SEND with image/* and EXTRA_STREAM content URI, temporary URI permission grants (FileProvider), appropriate ClipData, and explicit read-grant flag.
- Handle ActivityNotFoundException, no handler, cancellation, target failures and revoked image data. Offer **Share image** or “Open in Google Photos and use Lens” guidance where relevant, without guaranteeing Lens itself can consume the payload.
- Since Lens is an outside Google feature, it may require internet and shares the image with Google's services per their terms; no data goes to a Waltz backend.
- Selecting Lens must not modify source image, current wallpaper, rotation queue, collection membership or user settings.

### Contract tests
S071-01 Share fresh screenshot via Android Sharesheet -> Waltz editor preloaded; no broad media permission.
S071-02 Clipboard image URI -> paste success; clipboard text/expired URI -> comprehensible Photo Picker fallback.
S071-03 Rotate 90 degrees and crop; reopened original remains lossless and user can revise recipe.
S071-04 Use Now with active no-repeat shuffle -> current selection changes, future queue stays coherent, timer restarts as labelled.
S071-05 Add Next -> next eligible item; Just Save -> no immediate wallpaper change.
S071-06 Process killed during import or apply -> recovery without orphaned DB rows/files, item remains retriable.
S071-07 10k-pixel screenshot, malformed MIME, duplicate screenshot, out-of-disk and revoked grants -> no crash, clear recovery.
S071-08 TalkBack, 200% text scaling, keyboard/switch controls and landscape all complete edit and apply flow.
S072-01 Any cached user image -> choice original/crop -> external share/compatible Lens, unmodified app state.
S072-02 Lens unavailable -> user-visible Sharesheet fallback, never dead button or undocumented direct intent.
S072-03 URI access to recipient scoped and temporary; recipient can decode full image; no external activity leaks private paths.
S072-04 Cancel and return -> Waltz returns to same image/scroll location with edit state intact.

### Roadmap and priority
F071 screenshot share/import/edit = P0 (first release); editor non-destructive rotation/crop and Use Now semantics P0. Clipboard paste P1 due to provider differences; never postpone screenshot **Share** intake. F072 Lens via general sharing = P1; dedicated Lens label contingent on verified supported target. Native per-image Share = P0. Add compatibility tests on Pixel and representative Samsung/OEM builds.

### Platform references
- https://developer.android.com/develop/ui/compose/sharing/receive
- https://developer.android.com/develop/ui/views/touch-and-input/copy-paste
- https://developer.android.com/develop/ui/compose/sharing/send
- https://support.google.com/googleplay/android-developer/answer/14115180
- https://www.google.com/mobile/goggles/index.html
