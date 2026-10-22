> **2026-10-22 clarification:** This 70-row matrix is historical first-pass accommodation, **not a final implementable contract**. See [all 73 feature decisions, gaps and gates](GLIMPSE-FEATURE-SPEC-COMPLETENESS-AUDIT.md) for W01–W70 and F071–F073 and [technical behavior/side-effect contracts](GLIMPSE-TECHNICAL-BEHAVIOR-CONTRACTS.md). Its legacy screen entry names are not current Glimpse UI labels. “P0–P1” here is historical rough planning; use current M1–M4 ordering. None of these rows is evidence that Android support exists yet.

# Waltz — 70 workflow accommodation matrix

Each human-voiced requirement has an explicitly named engineering primitive and an approachable first place to find it. Tiers are design priorities, not functionality already built. Conditional platform features must be shown honestly, not faked. Reference: 70-HUMAN-WORKFLOWS.md.

| ID | User's desire (abbreviated) | Design/engineering accommodation | Visible entry point | Planning tier |
|---|---|---|---|---|
| W01 | I've got about 300 rainbows in Google Photos. I just want to pick all the ones I l… | Offline-verified cloud picker import; persistent no-repeat shuffle; five-minute active-use cadence | Collections / Import | P0–P1 |
| W02 | My partner sends me a few lovely photos every week. I want to add them straight fr… | Share-sheet import to named collection | Collections / Import | P0–P1 |
| W03 | My pictures are scattered between Downloads, a camera folder and an SD card. I wan… | Virtual union of files across SAF directories and SD media | Collections / Import | P0–P1 |
| W04 | I've got some photos in Google Photos that are only in the cloud. I want to import… | Download selected cloud photos to private local storage with checksum | Collections / Import | P0–P1 |
| W05 | I took 40 pictures at a concert and most of them are almost identical. I want Walt… | Perceptual dedup suggestions and user-review selection | Collections / Import | P0–P1 |
| W06 | I want to use only the photos I starred in a folder, but I don't want removing a s… | Favorites-filter and independent membership state | Collections / Import | P0–P1 |
| W07 | I have 12,000 wallpapers in one folder and I only want to see the new ones for a w… | Newly added image quarantine/rotation window | Collections / Import | P0–P1 |
| W08 | I keep adding pictures to an album in Google Photos. I'd like the matching Waltz c… | Explicit imported snapshot vs opt-in sync distinction | Collections / Import | P0–P1 |
| W09 | Sometimes I want to browse my existing collection and hit 'Use these five for the … | Expiring temporary five-item sub-scene | Collections / Import | P0–P1 |
| W10 | I want to combine three collections into a temporary mega-collection without losin… | Reversible composite collection without source duplication | Collections / Import | P0–P1 |
| W11 | I want a fresh photo every time I unlock my phone, except if I just unlocked it th… | Wake-cycle debouncer with cooldown | Today / Rhythms | P1 |
| W12 | During working hours I'd like calming landscapes every hour; after work I'd like t… | Workday/evening scene priority and time windows | Today / Rhythms | P1 |
| W13 | I want a particular sunset image at exactly 8 pm when I'm looking at my phone, but… | Clock-time eligible window with no forced wake | Today / Rhythms | P1 |
| W14 | Give me a new wallpaper every morning, but only once I've actually picked up the p… | First-use-of-day trigger with per-day idempotency | Today / Rhythms | P1 |
| W15 | At sunrise I want bright images and at sunset I want darker ones, but if the weath… | Sunrise/sunset with explicit optional weather condition | Today / Rhythms | P1 |
| W16 | On Saturdays I want street photography, except on the first Saturday of the month … | Nth-weekday exception precedence | Today / Rhythms | P1 |
| W17 | I want the wallpaper to change every five minutes while I'm charging at my desk, b… | Charging state changes rotation cadence | Today / Rhythms | P1 |
| W18 | When Battery Saver starts, I'd like Waltz to freeze the current wallpaper and quie… | Battery Saver suspension and non-burst resumption | Today / Rhythms | P1 |
| W19 | While I'm travelling I want a special collection, but once I'm home it should auto… | Temporary travel override with home fallback | Today / Rhythms | P1 |
| W20 | I want one change per day, at a slightly unpredictable time between lunch and dinn… | Random-but-bounded eligible window | Today / Rhythms | P1 |
| W21 | I want the home screen to be a soft blurred version of whatever crisp photograph i… | Derived blur presentation linked across destinations | Destinations / Composition | P1–P2 |
| W22 | My lock screen should rotate through portraits every time I lock, but my home scre… | Independent lock source and event cadence | Destinations / Composition | P1–P2 |
| W23 | I want matching colours on the two screens, but I don't want the same image on bot… | Correlated palette selection with distinct images | Destinations / Composition | P1–P2 |
| W24 | When I turn on Android dark mode, use the dark variants of my artwork; when it tur… | Dark/light variants without double shuffle advance | Destinations / Composition | P1–P2 |
| W25 | I want the lock-screen clock to remain readable over every photo, even when the su… | Lock clock readability advisory overlay | Destinations / Composition | P1–P2 |
| W26 | I use a launcher with scrolling wallpaper. I'd like the same subject to stay visib… | Launcher parallax-safe focal anchoring | Destinations / Composition | P1–P2 |
| W27 | When I connect an external display, I want the wallpaper to look sensible there, b… | External display composition capability testing | Destinations / Composition | P1–P2 |
| W28 | I have a folding phone and want separate framing for the closed and unfolded sizes… | Per-fold-state composition versions | Destinations / Composition | P1–P2 |
| W29 | I love dynamic Android colours but some images produce hideous system palettes; ca… | Per-image dynamic-colour opt-out/override | Destinations / Composition | P1–P2 |
| W30 | I want my screen to remain totally still if I've enabled reduced motion, even thou… | Global animation and strobe safety ceiling | Destinations / Composition | P1–P2 |
| W31 | I want daily photos from NASA mixed with my own space pictures, but skip NASA days… | Rights-verified APOD image-only source with local pictures | Explore / Sources | P2 |
| W32 | I want Wikimedia Commons pictures tagged with 'brutalist architecture', but I only… | Wikimedia Commons photography filter and attribution | Explore / Sources | P2 |
| W33 | I want to sample a couple of dependable wallpaper sites without having to make a W… | Multiple vetted no-account source adapters | Explore / Sources | P2 |
| W34 | When an internet source is down, quietly use my offline collection and try the sou… | Source health circuit breaker and offline fallback | Explore / Sources | P2 |
| W35 | I want to mix 70% my own wallpapers and 30% newly discovered photos, but don't rep… | Weighted 70/30 pools with cross-source identity dedup | Explore / Sources | P2 |
| W36 | I want to review five suggested images on Sundays; only the ones I approve should … | Weekly moderation/approval queue | Explore / Sources | P2 |
| W37 | I use my own RSS feed of illustrations. I want to try it as a source without givin… | Sandboxed user RSS/Atom source with security limits | Explore / Sources | P2 |
| W38 | I only want remote images downloaded over Wi-Fi, unless I explicitly tap 'Use this… | Metered-network download gate and explicit override | Explore / Sources | P2 |
| W39 | I want to hide an artist completely across every source and collection without acc… | Global artist exclusion without deleting files | Explore / Sources | P2 |
| W40 | One of my source providers changes its API rules. I want Waltz to tell me the sour… | Provider outage notice and preserved fallback selection | Explore / Sources | P2 |
| W41 | I want three days of colourful things, then one day of monochrome, but during that… | Three-day colour/one-day mono cycle with daily exception | Scenes / Rules | P2 |
| W42 | I have a collection of collections: Nature has Forests, Oceans and Mountains. Shuf… | Nested acyclic collections with fair child selection | Scenes / Rules | P2 |
| W43 | For my favourite collection, show every image once before repeating, but avoid sho… | Shuffle-bag with perceptual-neighbor avoidance | Scenes / Rules | P2 |
| W44 | I want the order to feel surprising, but the same exact photo shouldn't turn up mo… | Canonical-image 14-day cooldown across collections | Scenes / Rules | P2 |
| W45 | Every tenth wallpaper should be something from a small 'old favourites' set; the o… | Every-tenth-item injection strategy | Scenes / Rules | P2 |
| W46 | If an image from my 'Too Bright' tag comes up after sunset, substitute the next el… | Conditional exclusion without consuming shuffle candidate | Scenes / Rules | P2 |
| W47 | I want alternating moods: something serene, then something bizarre, then serene ag… | Alternating category composition with child shuffle | Scenes / Rules | P2 |
| W48 | On my birthday I'd like a celebration rule to override everything, except the acce… | Celebration priority bounded by accessibility safety | Scenes / Rules | P2 |
| W49 | I'd like a special photo to appear after I skip three wallpapers in a row, but onl… | Three-skips trigger with daily rate limit | Scenes / Rules | P2 |
| W50 | My evening rule uses a collection that itself mixes two smart collections; I want … | Human-readable nested source and rule execution trace | Scenes / Rules | P2 |
| W51 | I've got portraits where the subject is near the edge. I want Waltz to crop intell… | Manual crop override persisted after automatic focal detection | Image editor / History | P1–P2 |
| W52 | Some pictures are very wide; I'd rather have a tasteful blurred extension than cro… | Blurred-image extension instead of destructive hard crop | Image editor / History | P1–P2 |
| W53 | I want everything in a collection slightly desaturated, except three photos that I… | Collection effects with per-image untouched override | Image editor / History | P1–P2 |
| W54 | I accidentally skipped the perfect wallpaper. I'd like Undo to bring it back witho… | Undo tied to delivery history and shuffle rollback | Image editor / History | P1–P2 |
| W55 | I want a one-tap 'never show this again' control, but I want to be able to see and… | Reviewable persistent hide tombstones across reindex | Image editor / History | P1–P2 |
| W56 | Sometimes a wallpaper looks fine in the editor but bad behind my icons. I'd like a… | Preview with icon safe-area and contrast guide | Image editor / History | P1–P2 |
| W57 | I want to preview a day's rotation as a little filmstrip before I activate it, wit… | Side-effect-free schedule/filmstrip simulation | Image editor / History | P1–P2 |
| W58 | I want to make two different crops of the same picture, one for home and one for l… | Separate home and lock crop profiles per image | Image editor / History | P1–P2 |
| W59 | I want Waltz to notice a low-resolution photo and suggest a safer crop instead of … | Low-resolution warnings and quality-aware scaling | Image editor / History | P1–P2 |
| W60 | I'm happy with my current image. I want to pin it until tomorrow morning, even if … | Expiring wallpaper pin over normal rotation rules | Image editor / History | P1–P2 |
| W61 | I want a little widget that shows the next wallpaper and a big Skip button, but no… | Configurable accessible Skip/preview widget | Controls / Accessibility | P1 |
| W62 | I want a Quick Settings tile that rotates the lock-screen picture without changing… | Destination-specific Quick Settings command | Controls / Accessibility | P1 |
| W63 | I use Tasker. I want to tell Waltz 'start my Night Shift scene' and get a clear su… | Validated explicit Tasker action with success result | Controls / Accessibility | P1 |
| W64 | I'm switching phones. I want to restore my collections, crops and rules while bein… | Portable rule/crop archive with reconnect wizard | Controls / Accessibility | P1 |
| W65 | I want a backup I can keep locally, encrypted if I choose, and I absolutely don't … | Optional encrypted local backup excluding photos by default | Controls / Accessibility | P1 |
| W66 | I use TalkBack and a Bluetooth keyboard. I want to build the same schedule a sight… | TalkBack and keyboard equivalent advanced editor | Controls / Accessibility | P1 |
| W67 | My eyesight isn't great and I use huge system text. I want the entire app to reflo… | Adaptive large-font reflow and visible complete labels | Controls / Accessibility | P1 |
| W68 | I have strong photosensitivity. I want Waltz to block rapid flashes and animated t… | Non-optional photosensitivity policy across every transition | Controls / Accessibility | P1 |
| W69 | My partner and I both use different Android profiles on one phone. I want Waltz to… | Android multiuser boundary and profile capability explanation | Controls / Accessibility | P1 |
| W70 | A wallpaper stopped changing last night. I want to see exactly which rule ran, wha… | Detailed last-rule/last-image failure explanation and repair | Controls / Accessibility | P1 |

## Validation agreement

- P0 demands A001–A015: native photo selection with supported Google Photos cloud media, verified offline copies, durable shuffle and honest five-minute active-use rotation.
- For every row, create a deterministic fixture containing source assets, observed device state, rule priority, eligible images, expected destination updates, user feedback, and offline/Doze/failure result.
- The underlying collection dependency graph is acyclic and checked on edit and restore. No wallpaper-change event may recursively trigger itself without a cooldown and explicit permission.
- All requested Android permissions and external image rights are platform-/provider-gated; when unsupported, explain the limitation and propose the nearest safe alternative.
- Usability protocol: first-time users must never enter the advanced Rule Studio for W01. Tests for TalkBack, extreme font scale, keyboard, reduced motion and one-tap diagnostics apply across tiers.

| F071 | I just took a screenshot; I want to paste/share it, rotate/crop it, save to a collection, and decide whether it becomes my current wallpaper or joins next. | ACTION_SEND receiver and user-driven clipboard paste; durable private copy; non-destructive edit recipe; queue placement; apply-result state | Share to Waltz / Collections > Add > Paste image | P0 Share and edit, P1 clipboard variants |
| F072 | I'm looking at a wallpaper and want to send that exact image, or its crop, to Google Lens without changing my collection. | FileProvider URI and ACTION_SEND/chooser with explicit grants; capability detection and honest fallback; zero rotation-state mutation | Image detail > Search with Google Lens | P1 |

| F073 | I want to send any picture to chats, email, ChatGPT, Google Drive, Google Images/Lens or an editor, or share several together. | Android ACTION_SEND/ACTION_SEND_MULTIPLE Sharesheet with scoped content URI, explicit original-versus-crop choice; SAF Save copy; target capability detection, EXIF sanitization and external edit variant reimport | Image viewer > Share; grid multi-select > Share; image > Open in editor / Save copy | P0 generic shares, P1 refinements |
