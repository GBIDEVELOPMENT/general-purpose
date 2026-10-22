# Waltz — Android wallpaper manager design project

**Status:** detailed product concept and engineering/UX research, not an implemented Android application. Original design files and updated presentations exist as conversation downloads; see ASSET-INVENTORY.md for publication gaps.

Waltz is a friendly, beautiful, open-source, local-first wallpaper manager that changes wallpapers from the user's own collections and vetted maintained external sources. It has no Waltz-hosted image catalogue, server, cloud sync service, subscription, or mandatory account.

## Read in order
1. **RAINBOW-QUICKSTART-CONTRACT.md:** golden-path Google Photos to 5-minute shuffle, honest platform restrictions, acceptance tests A001–A015.
2. **70-HUMAN-WORKFLOWS.md:** seventy first-person requests with nested conditions and peculiar but reasonable preferences.
3. **WORKFLOW-DESIGN-RESPONSE.md:** exact technical accommodations, UX grammar, conflict rules, delivery and roadmap.
4. **PRODUCT-SPECIFICATION.md:** complete foundational technical/product proposal plus override addendum.
5. **PITCH-DECK-OUTLINE.md:** visual system and outline of the original/updated pitch.
6. **ASSET-INVENTORY.md:** produced binary files and their verified publication status.

**Product standard:** easy usage requires no Rules editor; complex scenarios use progressive disclosure. Import selected cloud-backed photos via native Android Photo Picker; imported images are verified and stored offline. The user sees “every five minutes while in use” with truthful eligible/last-applied state rather than a fake guarantee during Doze.

No third-party API policy bypass, unverified image license, Photos scraping, invasive Android permission or privileged accessibility service.