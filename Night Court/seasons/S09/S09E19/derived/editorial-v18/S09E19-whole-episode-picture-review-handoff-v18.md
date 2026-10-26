# S09E19: direct whole-episode sampled-picture audit | 2026-10-26

## Why this addendum exists

The S09 v18 episode editor had already completed its source-dialogue pass and [PR #509](https://github.com/gamesbyian/general-purpose/pull/509) was merged. The earlier whole-episode picture report had represented its 73 original-source thumbnails as past-work metadata, but the **original private evidence archive itself** was still available. I recovered and directly reviewed that archive to improve the picture/wardrobe/prop evidence actually embedded in the readable episode manuscript.

The source was the owner-only Action [#40137223223](https://github.com/gamesbyian/general-purpose/actions/runs/40137223223), artifact **#12578036143**. The recovered ZIP SHA-256 is **`fa5d4f5ed8791e26257d447c5d40b02d8cf8469e82784b52bbdee6f3a498717d`**, exactly matching its pre-existing evidence ledger. The original video source identifier remains SHA-256 **`51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649`** (source video itself not newly downloaded or hashed). The untimed original transcript witness remains **`659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2`**.

The archive contains one original-source JPEG sampled at 18-second intervals, totaling **73 frames**, with four chronological contact sheets. I inspected all four contact sheets. Independently computed SHA-256 matched **73/73 original frame JPEG files** and **4/4 contact sheet files** against the archive's original frame catalogue. No source audiovisual files, contact sheets, pictures, face crops or frames are committed.

## What changed in the screenplay

Every one of the existing **11 screenplay story-sequence headings** now has a brief clearly labeled *original-picture reference* with relevant set, wardrobe and prop details. Specific direct observations include:

- Bright cafe/diner serving area, table condiments, a vivid purple jacket, navy uniforms, kitchen/service counters and people with paper work (frames 001–007).
- Courtroom bench and rail, paper stacks, yellow and tan jackets, purple outerwear, navy official uniforms and the chamber's court desks (008–016).
- A law-book-lined dark wood office, legal desk and papers, a tan suit/patterned tie, reddish-brown jacket and an adult in uniform near a doorway (017–024).
- Diner tables with cups, bottles, red/orange/burgundy costumes and a navy-uniformed adult; later, a courthouse desk, bright yellow-collared burgundy patterned attire and folders (025–038).
- The sparking floor/wood partition, for which the separate **200-frame direct re-review** established an adult *approaching* the flare and bending toward it, contradicting the earlier retreat description; additional office material (039–045).
- A warm dark-wood restaurant, dressed tables, drinks, burgundy outfit, dark-suited bearded adult and servers, followed by the dancing couple (046–055).
- Restaurant bar counter, drinking vessels, snack bowl, vest-wearing adult and differently costumed other adults, including navy uniform and a gray suit (056–065).
- Cream-walled hall, red-orange tailored outfit, patterned clothing with circular badge, and final return to a book-lined office with people gathering near a table (066–072).
- **Frame 073** is a broadcast promo slate (“UP NEXT”), intentionally excluded from fictional props/actions and narrative screenplay.

The machine-readable evidence file is `S09E19-whole-episode-original-still-review-v18.json`, with 12 logically grouped subsets pointing to the original source frame catalogue and archive hashes.

## Important limitations

These images were recovered from already archived original-source-derived samples, but **no continuous film or original audio was newly played**. Eighteen seconds between frames is too coarse to certify small movements, entrances/exits, gestures, props being passed, comic timing, characters saying specific lines, exact camera cuts or the physical origin of a spark. There is **no actor naming from facial appearance**, no original film mouth/speaker attribution, no new subtitle timecode and no performance acceptance. Descriptions of the dancers and floor spark from the separately checked 5fps sequences remain similarly narrow.

In particular, the distinction between **The Guy (acting as Alex)**, **Lisette (acting as Roz)**, **real Alex**, and **real Roz** continues to be grounded in the episode's *dialogue and credited cast context*, not by retroactively naming people in sampled images. The new picture notes support story setting and wardrobe, not an independent acoustic attribution.

## Independent artifact integrity

- Original 347 transcript units unchanged; S09 latest v18 current episode reader stays **323 rows, 273 provisionally named /74 with UNKNOWN**.
- The only changed existing artifact is the **complete v18 screenplay's visually annotated sequence headings and its evidence appendix**; dialogue blocks and exact provenance JSONL remain byte-for-byte undisturbed.
- This is episode-local and leaves the shared current `saved-private/pilot-current` and S01 paths under Agent 3's ownership.
- When selecting S09 v18 into current portable pilot artifacts, Agent 3 should use this newest checked **full screenplay text**, not a pre-picture-addendum copy; recompute its hash and validate original source dialogue and per-block provenance as usual.
- The final audiovisual-certified screenplay gate remains **open**: genuine original-soundtrack speaking turns and acting, foreground/recipient physical actions, and all remaining UNKNOWN voices still need verified review.

## Source provenance

Original archive: [Action run 40137223223](https://github.com/gamesbyian/general-purpose/actions/runs/40137223223), artifact 12578036143, ZIP SHA above. Existing recorded source observation: `Night Court/seasons/S09/S09E19/derived/source-photo-scene-overview-v1/observations.json`. New supplementary direct inspection: `S09E19-whole-episode-original-still-review-v18.json`. Original 5fps motion sequence correction: `S09E19-direct-original-frame-review-v18.json`.
