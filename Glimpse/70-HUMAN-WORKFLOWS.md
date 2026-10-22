# Waltz — 70 natural-language user workflows

Version: 2026-10-21. These are **design stress tests**, not claims of current implementation. Each is phrased as a human desire rather than a feature ticket. The original rainbow-import example is **W01** and becomes acceptance test A001.

Purpose: ensure casual flows remain effortless while nuanced, conditional, nested, and overlapping intents remain representable without asking people to learn an automation language.

## 01 · Personal collections and getting started

**W01.** “I've got about 300 rainbows in Google Photos. I just want to pick all the ones I like, call them Rainbows, and shuffle one onto my home screen every five minutes.”

**W02.** “My partner sends me a few lovely photos every week. I want to add them straight from Android's Share menu into our little collection without opening Waltz first.”

**W03.** “My pictures are scattered between Downloads, a camera folder and an SD card. I want one collection that looks unified without actually moving or duplicating the originals.”

**W04.** “I've got some photos in Google Photos that are only in the cloud. I want to import them once, then have them keep rotating even when I'm on a plane.”

**W05.** “I took 40 pictures at a concert and most of them are almost identical. I want Waltz to notice the near-duplicates and ask which to keep in rotation.”

**W06.** “I want to use only the photos I starred in a folder, but I don't want removing a star to delete anything or wreck the other collections that use the same photo.”

**W07.** “I have 12,000 wallpapers in one folder and I only want to see the new ones for a week before mixing them into everything else.”

**W08.** “I keep adding pictures to an album in Google Photos. I'd like the matching Waltz collection to stay updated automatically, but tell me honestly if that isn't something it can do.”

**W09.** “Sometimes I want to browse my existing collection and hit 'Use these five for the next hour,' then go back to the normal schedule.”

**W10.** “I want to combine three collections into a temporary mega-collection without losing their individual identities or editing the originals.”

## 02 · Rhythms, time and events

**W11.** “I want a fresh photo every time I unlock my phone, except if I just unlocked it thirty seconds ago.”

**W12.** “During working hours I'd like calming landscapes every hour; after work I'd like the silly drawings I made, changing every ten minutes.”

**W13.** “I want a particular sunset image at exactly 8 pm when I'm looking at my phone, but I'm not interested in waking it up just to make that happen.”

**W14.** “Give me a new wallpaper every morning, but only once I've actually picked up the phone, even if I sleep until noon.”

**W15.** “At sunrise I want bright images and at sunset I want darker ones, but if the weather is gloomy I'd rather the dark set win earlier.”

**W16.** “On Saturdays I want street photography, except on the first Saturday of the month when I want my favourite family photos.”

**W17.** “I want the wallpaper to change every five minutes while I'm charging at my desk, but only every hour when I'm on battery.”

**W18.** “When Battery Saver starts, I'd like Waltz to freeze the current wallpaper and quietly resume when it ends, not catch up by flashing six changes.”

**W19.** “While I'm travelling I want a special collection, but once I'm home it should automatically fall back to the schedule I had before.”

**W20.** “I want one change per day, at a slightly unpredictable time between lunch and dinner, with no more than a ten-minute deviation from the chosen moment if Android lets it.”

## 03 · Home, lock, themes and display contexts

**W21.** “I want the home screen to be a soft blurred version of whatever crisp photograph is on the lock screen.”

**W22.** “My lock screen should rotate through portraits every time I lock, but my home screen should remain the same abstract background all day.”

**W23.** “I want matching colours on the two screens, but I don't want the same image on both.”

**W24.** “When I turn on Android dark mode, use the dark variants of my artwork; when it turns off, use the light ones without advancing the shuffle twice.”

**W25.** “I want the lock-screen clock to remain readable over every photo, even when the subject is bright and right behind the clock.”

**W26.** “I use a launcher with scrolling wallpaper. I'd like the same subject to stay visible as I swipe between pages rather than being chopped off.”

**W27.** “When I connect an external display, I want the wallpaper to look sensible there, but I don't want a bad crop on my phone just to accommodate it.”

**W28.** “I have a folding phone and want separate framing for the closed and unfolded sizes without creating two copies of every photo.”

**W29.** “I love dynamic Android colours but some images produce hideous system palettes; can I pick a preferred palette for those images?”

**W30.** “I want my screen to remain totally still if I've enabled reduced motion, even though I'd normally prefer crossfades between photos.”

## 04 · Sources, discovery and availability

**W31.** “I want daily photos from NASA mixed with my own space pictures, but skip NASA days that are videos or have unclear reuse rights.”

**W32.** “I want Wikimedia Commons pictures tagged with 'brutalist architecture', but I only want photographs I can reuse and I want to see the creator credit.”

**W33.** “I want to sample a couple of dependable wallpaper sites without having to make a Waltz account or upload my own photos anywhere.”

**W34.** “When an internet source is down, quietly use my offline collection and try the source later without spamming errors.”

**W35.** “I want to mix 70% my own wallpapers and 30% newly discovered photos, but don't repeat a remote photo when it gets downloaded twice.”

**W36.** “I want to review five suggested images on Sundays; only the ones I approve should ever appear automatically.”

**W37.** “I use my own RSS feed of illustrations. I want to try it as a source without giving Waltz carte blanche to download arbitrary links.”

**W38.** “I only want remote images downloaded over Wi-Fi, unless I explicitly tap 'Use this now' on mobile data.”

**W39.** “I want to hide an artist completely across every source and collection without accidentally deleting images I've already imported.”

**W40.** “One of my source providers changes its API rules. I want Waltz to tell me the source is paused and show how my existing schedule will continue.”

## 05 · Sequencing, nesting and strange-but-reasonable rules

**W41.** “I want three days of colourful things, then one day of monochrome, but during that monochrome day I still want one colourful wildcard at lunchtime.”

**W42.** “I have a collection of collections: Nature has Forests, Oceans and Mountains. Shuffle the three categories fairly, then shuffle the images within whichever category comes up.”

**W43.** “For my favourite collection, show every image once before repeating, but avoid showing pictures with almost the same composition back to back.”

**W44.** “I want the order to feel surprising, but the same exact photo shouldn't turn up more than once in fourteen days even if I have it saved in several collections.”

**W45.** “Every tenth wallpaper should be something from a small 'old favourites' set; the other nine should come from the usual collection.”

**W46.** “If an image from my 'Too Bright' tag comes up after sunset, substitute the next eligible one without counting it as already shown.”

**W47.** “I want alternating moods: something serene, then something bizarre, then serene again, and within each mood I still want a fair shuffle.”

**W48.** “On my birthday I'd like a celebration rule to override everything, except the accessibility rule that stops intense animation.”

**W49.** “I'd like a special photo to appear after I skip three wallpapers in a row, but only once per day so it doesn't become annoying.”

**W50.** “My evening rule uses a collection that itself mixes two smart collections; I want to understand which child collection supplied today's wallpaper and why.”

## 06 · Editing, quality and control

**W51.** “I've got portraits where the subject is near the edge. I want Waltz to crop intelligently but let me fix the ones it gets wrong and remember the correction.”

**W52.** “Some pictures are very wide; I'd rather have a tasteful blurred extension than crop out the interesting part or get black bars.”

**W53.** “I want everything in a collection slightly desaturated, except three photos that I've manually marked as untouchable.”

**W54.** “I accidentally skipped the perfect wallpaper. I'd like Undo to bring it back without scrambling the entire shuffle history.”

**W55.** “I want a one-tap 'never show this again' control, but I want to be able to see and restore everything I've hidden later.”

**W56.** “Sometimes a wallpaper looks fine in the editor but bad behind my icons. I'd like a real home-screen preview with safe areas and adjustable contrast.”

**W57.** “I want to preview a day's rotation as a little filmstrip before I activate it, without actually changing the wallpaper twelve times.”

**W58.** “I want to make two different crops of the same picture, one for home and one for lock, without touching my original file.”

**W59.** “I want Waltz to notice a low-resolution photo and suggest a safer crop instead of silently upscaling it into a blurry mess.”

**W60.** “I'm happy with my current image. I want to pin it until tomorrow morning, even if several rules would normally change it.”

## 07 · Devices, automation, privacy and accessibility

**W61.** “I want a little widget that shows the next wallpaper and a big Skip button, but not the rest of the app's controls.”

**W62.** “I want a Quick Settings tile that rotates the lock-screen picture without changing my home screen.”

**W63.** “I use Tasker. I want to tell Waltz 'start my Night Shift scene' and get a clear success or failure result rather than a silent intent.”

**W64.** “I'm switching phones. I want to restore my collections, crops and rules while being told which image files I still need to reconnect.”

**W65.** “I want a backup I can keep locally, encrypted if I choose, and I absolutely don't want my photos included unless I explicitly ask.”

**W66.** “I use TalkBack and a Bluetooth keyboard. I want to build the same schedule a sighted touch user can, with every control clearly announced.”

**W67.** “My eyesight isn't great and I use huge system text. I want the entire app to reflow instead of cutting off labels and hiding important buttons.”

**W68.** “I have strong photosensitivity. I want Waltz to block rapid flashes and animated transitions everywhere, including the wallpaper itself.”

**W69.** “My partner and I both use different Android profiles on one phone. I want Waltz to be upfront about which profile and screens it can control.”

**W70.** “A wallpaper stopped changing last night. I want to see exactly which rule ran, what photo it tried, why Android or the source stopped it, and how to fix it without reading logs.”

## Two additional user-suggested workflows (F071–F072; original seventy preserved)

- **F071.** “I've just taken a screenshot and I want to paste or share it into Waltz, rotate it and crop out the rubbish, save it into one of my collections, and choose whether it replaces my wallpaper right now or just joins the lineup.”
- **F072.** “I'm looking at a wallpaper I've saved and I want to send it to Google Lens to find out what I'm looking at, then come straight back without changing anything.”

Detailed contracts, platform limitations and release tests: [SCREENSHOT-AND-LENS-FEATURES.md](SCREENSHOT-AND-LENS-FEATURES.md).

- **F073.** “I found a picture in my Waltz collection and I want to drop it into my chat with a friend, attach it to an email, ask ChatGPT about it, open it in my editing app, save a copy to Drive, or try Google Lens, without going hunting for the file or changing my wallpaper.”

Universal Android sharing contracts and S073 test cases: [SCREENSHOT-AND-LENS-FEATURES.md](SCREENSHOT-AND-LENS-FEATURES.md).
