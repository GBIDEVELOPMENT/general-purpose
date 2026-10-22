# Waltz — Android wallpaper manager design project

**Status:** detailed product concept and engineering/UX research, not an implemented Android application. Original design files and updated presentations exist as conversation downloads; see ASSET-INVENTORY.md for publication gaps.

Waltz is a friendly, beautiful, open-source, local-first wallpaper manager that changes wallpapers from the user's own collections and vetted maintained external sources. It has no Waltz-hosted image catalogue, server, cloud sync service, subscription, or mandatory account.

## Read in order
1. **RAINBOW-QUICKSTART-CONTRACT.md:** golden-path Google Photos to 5-minute shuffle, honest platform restrictions, acceptance tests A001–A015.
2. **70-HUMAN-WORKFLOWS.md:** seventy first-person requests with nested conditions and peculiar but reasonable preferences.
3. **WORKFLOW-DESIGN-RESPONSE.md:** exact technical accommodations, UX grammar, conflict rules, delivery and roadmap.
4. **PRODUCT-SPECIFICATION.md:** complete foundational technical/product proposal plus override addendum.
5. **WORKFLOW-COVERAGE-MATRIX.md:** every W01–W70 need mapped to specific engineering and UX accommodations.
6. **PITCH-DECK-OUTLINE.md:** visual system and slide outline.
7. **design/**: editable tokens, rainbow flow and 16 self-contained vector screen sketches (simplified, not the original screenshot pixels).
8. **ASSET-INVENTORY.md:** produced high-fidelity binary files and their verified publication status.

**Product standard:** easy usage requires no Rules editor; complex scenarios use progressive disclosure. Import selected cloud-backed photos via native Android Photo Picker; imported images are verified and stored offline. The user sees “every five minutes while in use” with truthful eligible/last-applied state rather than a fake guarantee during Doze.

No third-party API policy bypass, unverified image license, Photos scraping, invasive Android permission or privileged accessibility service.

## Additional requirements (October 21, 2026)
- [Screenshot quick import + Google Lens handoff](SCREENSHOT-AND-LENS-FEATURES.md): first-class Share/Paste → rotate/crop → save → Use Now/Add Next/Just Save workflow, plus privacy-preserving per-image Lens sharing and failure/compatibility tests S071-01–S072-04. This is additive to the original 70 scenarios.

- **Universal sharing (F073):** any image or selected batch can be shared via Android Sharesheet to compatible chat apps, email, ChatGPT, Drive, or editors; save copies via system document providers; dedicated Lens remains a contextual shortcut. See [SCREENSHOT-AND-LENS-FEATURES.md](SCREENSHOT-AND-LENS-FEATURES.md#requirement-f073-universal-outbound-image-sharing-and-editing-supersedes-lens-only-action-design).

## Native Android engineering direction (2026-10-21)
- **[NATIVE-ANDROID-ARCHITECTURE.md](NATIVE-ANDROID-ARCHITECTURE.md):** authoritative proposed Kotlin/Compose/Room/Hilt/Navigation 3 architecture, Android 17 SDK baseline, scheduler truthfulness, typed deterministic rules, reliable outbox + image pipeline, Glance widgets, strict security/privacy, sideload APK signing, developer-verification planning, release gates and ordered engineering backlog. This is a specification; no application code or signed APK exists yet.
