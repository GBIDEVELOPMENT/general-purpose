# Waltz product and UX pitch deck (textual navigation)

The full existing deck has **30 designed slides and sixteen original portrait mockups**. An updated **34-slide PPTX/PDF** exists as a conversation artifact, adding 4 slides describing the Rainbow quickstart and seventy-workflow complexity approach. This file is a searchable companion; it is NOT a replacement for rendered visuals.

**Visual system:** Paper #F7F4EE, tidal teal #196E6A, apricot #F17961, butter #FFD779, lavender #D7CAFA, ink #223630, comfortable typography and restrained ornamental gestures. Four destinations: Today, Explore, Collections, Rules. Reduced motion and TalkBack parity built into every screen.

**Sixteen screen mockups:** 01 Today, 02 Collections, 03 Collection detail, 04 Source directory, 05 Discover, 06 Rules, 07 Rule editor, 08 Crop, 09 Live effects, 10 Activity, 11 Diagnostics, 12 Widgets and Quick Settings, 13 Accessibility, 14 Onboarding, 15 Home/Lock, 16 Presets.

**Deck acts:** product promise; evidence from other open-source Android wallpaper changers; visual personality; navigation; Today/Collections/Explore/Rules; source rights; editing and presentations; accessibility; native integration; internal architecture; platform limitations; development roadmap; screen gallery.

**New slides 31–34:**
31. "Rainbows in five minutes" — New collection → Add photos → Import offline → Use as wallpaper → Shuffle every 5 minutes → Start.
32. "A kind promise, never a fake one" — snapshot import, offline copies, honest active-use cadence.
33. "70 lives. Four levels of control." — action / rhythm / scene / advanced rule.
34. "Make the small thing impeccable" — first release priority is dependable A001 before nested rule extravagance.

**Important:** Screens depict design concepts, not actual app captures. Original binaries and editable art are separately inventoried in ASSET-INVENTORY.md.


## V3 native architecture pitch deck revision (2026-10-22)

The original 34-slide UI/UX proposal is retained. The accompanying **Waltz_v3_Native_Android_Pitch_Deck.pptx** and **.pdf** add slides 35–42:

35. **Native stack:** Kotlin, Compose Material 3, Navigation 3, Hilt, Room, DataStore, Coroutines/Flow, signed APK; API29 minimum, API37 target subject to qualification.
36. **Unified commands:** user-facing app, widget, shortcut, rule trigger and TileService call a common command gateway and pure rule engine.
37. **Crash integrity:** request → prepare → apply → reconcile → explain, with persistent operation journal and outbox.
38. **Five-minute honesty:** static best-effort, live visible-only, eligible vs actual change; no sideload policy bypass.
39. **Image integrity:** Photo Picker/SAF/screenshots, immutable originals, bounded image processing, sharesheet export.
40. **Platform integrations:** Glance widgets, Quick Settings tile, shortcuts, scoped URI sharing, no privileged shortcuts.
41. **Release quality:** Pixel and OEM testing, API29–37, Gradle verification, signing identity, checksums, upgrades.
42. **Vertical roadmap:** M0 platform proof → M1 useful rainbow alpha → M2 daily-driver → M3 advanced engine → M4 live effects/polish.

The complete technical source authority is [NATIVE-ANDROID-ARCHITECTURE.md](NATIVE-ANDROID-ARCHITECTURE.md). Presentation remains a product/design proposal, not a tested Android implementation. The v3 binaries are conversation deliverables; do not falsely imply they are committed as GitHub assets until a binary transfer is verified.
