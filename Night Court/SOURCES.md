# Source discovery and preservation ledger (2026-10-23)

## Held evidence vs discovery pointers

- **Stored CC BY-SA 4.0 snapshots:** two complete Wikipedia wikitext pages (original TV series + 193-episode list) and **193 episode-specific excerpted wiki capsules**. Every wiki article has revision-specific provenance; every episode capsule has its own `sources/wikipedia-capsule.provenance.json`. The two-part broadcasts receive shared synopsis text, explicitly marked as such.
- **Held factual metadata:** all 193 episodes' titles, dates, directors, writer credit strings and production codes; metadata sources TVmaze episode API and Wikipedia episode-list wikitext.
- **Not stored:** full scripts, closed captions, subtitles or proprietary review text. Those sources have pointers, not retained bytes.

| ID | Source | URL | Verified coverage | Storage treatment |
|---|---|---|---|---|
| fd | Forever Dreaming | https://transcripts.foreverdreaming.org/viewforum.php?f=1485 | 57 script topics, S01–S03 | Per-episode source pointers (not text). |
| sf | Springfield! Springfield! | https://www.springfieldspringfield.co.uk/episode_scripts.php?tv-show=night-court-1984 | 47 indexed scripts: 13 S01, 12 S02, 22 S03 | Constructed direct URLs separately flagged unverified. |
| sc4 | Subtitle Cat S04E01 | https://www.subtitlecat.com/subs/1120/night_court_s04e01_the_next_voice_you_hear.html | Episode caption display | Reference only. |
| sc9 | Subtitle Cat S09E22 | https://www.subtitlecat.com/subs/1592/S09E22%20-%20The%201992%20Boat%20Show.html | Series-finale caption display | Reference only. |
| sd | SUBDL | https://subdl.com/subtitle/sd1301097/night-court | Series and seasons; individual coverage not established | Reference only. |
| wp | Wikipedia episode list | https://en.wikipedia.org/wiki/List_of_Night_Court_episodes | 193 episode parts, 188 episode-list templates | Complete licensed wikitext with attribution + episode capsule files. |
| ws | Wikipedia original show | https://en.wikipedia.org/wiki/Night_Court | Original series article | Complete licensed wikitext with attribution. |
| fm | Night Court Wiki | https://nightcourt.fandom.com/wiki/List_of_Night_Court_episodes | Fan-maintained comprehensive index | Links; independently verify licensing on any article before retention. |
| vm | TVmaze | https://www.tvmaze.com/shows/1489/night-court/episodeguide | All 193 episode IDs, titles, broadcast dates and pages | Factual metadata in episode JSON. |
| tv | TheTVDB | https://www.thetvdb.com/series/night-court/allseasons/official | All-season episode guide | Index reference only. |
| im | IMDb | https://www.imdb.com/title/tt0086770/episodes/ | Episode summaries/credits/ratings | Reference; no review mirroring. |
| tg | TV Guide | https://www.tvguide.com/tvshows/night-court/episodes-season-1/1000231157/ | Capsules | Reference. |
| nb | NBC Archives fan wiki | https://nbcarchives.fandom.com/wiki/Night_Court_%281984%29 | Alternate titles/identifiers | Preserve variants, pending direct checks. |
| tr | Tropedia | https://tropedia.fandom.com/wiki/Night_Court | Fandom trope analysis | Reference and provisional research tags. |
| rd | r/sitcoms | https://www.reddit.com/r/sitcoms/comments/190ge0d | 2024 retrospectives | Time-indexed reception example; not representative. |
| ra | r/NightCourt | https://www.reddit.com/r/NightCourt/comments/1kccmr5 | 2025 retrospectives | Time-indexed reception example; not representative. |
| rb | r/NightCourt | https://www.reddit.com/r/NightCourt/comments/1r3lkxk/old_vs_new/ | 2026 original/revival comparison | Time-indexed reception example, keep original/revival separate. |

## Source quality tiers

- A: directly inspected episode page **or** physical licensed source with checksum/provenance.
- B: episode specifically listed in an inspected index.
- C: series or season guide without direct episode evidence.
- D: inferred/conjectured URL (always `verified: false`).

The repeated per-episode count of source pointers should never be presented as the number of unique recovered documents. The 193 capsules were extracted from the single licensed Wikipedia episode-list source and aren't 193 independent eyewitness accounts.

## Open work

Determine subtitle coverage by episode in seasons 4–9, discover additional script collections and contemporary production interviews, add fan wiki/reviews and criticism references, verify all source-specific alternative episode identifiers and rights, track link rot, and then construct cross-sourced canonical event/joke/character/production/fandom matrices. Avoid unverifiable assertions of preservation.

## October 23, 2026: new verified and archived sources

- [TVmaze API](https://www.tvmaze.com/api) explicitly offers series-wide cast and crew and season-wide `episodes?embed=guestcast` endpoints under CC BY-SA. Successful retrieval: all 9 seasons, all 193 episode guestcast collections, 1,210 credited person-character-episode relationships. Source objects retain TVmaze URLs and source/license attribution. See `catalog/tvmaze-guestcast-coverage.json` and `catalog/cast-relationship-graph.json`. A cast credit does not prove physical appearance.
- Additional **19** revision-specific Wikipedia CC BY-SA context articles were archived, including cast/creative biographies and New York City Criminal Court context. `research/licensed-wiki/context/manifest.json` includes successful revisions and two unresolved requested titles. No claim is made that all biographies directly discuss the show.
- [Fandom's network licensing policy](https://www.fandom.com/licensing) generally makes independently authored wiki text available under CC BY-SA, subject to the specific wiki license and separate rights for media and imported material. However, the Night Court Wiki API failed the robots access check in this run; `research/fandom-wiki/collection-status.json` records the block. **No full Fandom pages were archived.** Preserve visible episode/source references without bypassing access rules.
- 193 source-indexed evidence dossiers and 342 sentence-like source statements were derived from the already-held encyclopedia capsules. These are **not new independent source documents** and are not scripts or verified scene accounts. The episode-level `holdings-coverage.csv` is the authoritative source-acquisition coverage matrix.
- Overall episode source pointers currently total **1,672** (including repeated series-wide references); per-episode *exact episode page* pointers total **13**. Pointers, pages, factual role credits, excerpts and full retained third-party documents have different units and must never be combined into a misleading total.


## Additional original-series caption/capsule locations, 2026-10-23

- **Subtitle Cat individual episode pages:** 21 unique original-series episode IDs now have verified public caption-display URLs, stored in `catalog/subtitlecat-discovery.json` and associated `episode_sources`. S01E05; S02E01, E03, E05, E11, E15, E16, E20; S03E04, E13, E15; S04E01; S09E22. These are references to externally hosted captions, never locally saved SRTs. Automated indexing was not permitted by robots, and `catalog/subtitlecat-discovery.json` records both refused index requests.
- **Apple TV original show**: https://tv.apple.com/ca/show/night-court/umc.cmc.3v8igla11dgg4chywljv2og89 explicitly lists subtitles English (US) CC for the original 1984–92 series. This is a distribution availability and format reference, not a caption download.
- **Prime Video original series S01**: https://www.primevideo.com/detail/0JKQMQRYLQ7AQRRSNOGZQAN1PB supplies third-party episode catalogue capsules and release listings, possible independently authored synopsis witnesses. No prose has been copied, and individual episode URLs are not yet mapped.
- **All-episodes season/retailer index**: https://www.justwatch.com/ca/tv-show/night-court lists 193 original-series episodes across nine seasons and is useful for distribution/caption-source lookup, not for dialogue acquisition.

**Scope risk:** A web search for "Night Court S01E01" frequently returns the 2023 revival instead of the 1984 original. A source without explicit 1984 identity or independently verified original character/cast context must not be mapped to the original-series corpus. Caption versions and alternative streaming cuts may differ from an original NBC broadcast.


## Broadcast context evidence

The revision-pinned [Wikipedia original-series episode-list source](https://en.wikipedia.org/wiki/List_of_Night_Court_episodes) includes annual U.S. series ranks, season household ratings and many episode-specific household rating/share or U.S.-viewer figures with references to contemporary press reports. `catalog/broadcast-context.json`, `catalog/broadcast-context.csv` and `research/broadcast-context.md` preserve these as separately typed data, including a five-entry composite-episode distinction. The source is a **retrospective secondary compilation** and should be crosschecked against the underlying 1980s/90s press before making definitive historical audience claims.


## Added contemporary and reception evidence

`research/contemporary-press-bibliography.jsonl` preserves metadata and independently authored summaries of 15 sources across contemporary 1986–1992 reporting, post-broadcast reviews, modern audience ratings and professional oral-history leads. Particularly informative are the [September 1991 Associated Press creator/producer interview](https://www.latimes.com/archives/la-xpm-1991-09-29-tv-4438-story.html), the [May 1992 L.A. Times cast-and-producers end-of-series retrospective](https://www.latimes.com/archives/la-xpm-1992-05-13-ca-1601-story.html), and the [March 1992 NBC network scheduling commentary](https://www.latimes.com/archives/la-xpm-1992-03-14-ca-3200-story.html).

Twelve `research/production-and-reception-claims.jsonl` source-attributed observations cover production recalibration, contemporary critical reputation, scheduling, local syndication and modern fan perspectives, with interpretation caveats. See `research/source-conflicts.json`: older Wikipedia/Kiwix mirrors show season-one national ranking **41** and season household rating **12.7** versus current revision **47** and **15.5**, which are not independent estimates. Underlying period ratings press must arbitrate. No copyrighted full editorial content retained.


## Immutable backup and source-drift protection

The initial 21 CC BY-SA Wikipedia sources are retained under `research/licensed-wiki/revisions/<article>/<revision_id>.wikitext`, with exact checksum, revision-specific attribution and licensing at `*.provenance.json`. Their manifest is `catalog/wiki-revision-archive.json`. Future refreshes may add a second or third revision of the same article: older snapshots must remain intact, and any same-ID byte mismatch is an error. Archives cover only revisions actually retrieved and preserved, **not** all upstream revision history. Dedicated offline preservation script and successful GitHub Actions check: `tools/preserve_wiki_revisions.py`, `.github/workflows/night-court-preserve-wiki.yml`.


### New path for held, episode-complete dialogue

`DIALOGUE-INGESTION.md` describes local and GitHub-mobile import of **user-supplied/authorized** .srt, .vtt and .txt versions. Original bytes are stored under the owning episode in `dialogue/versions/`, with a SHA-256, edition, language, source-name and source-rights declaration. Timed cue JSONL and a text view support research. A full-source claim is retained as a **claim** until independently checked against video. The `catalog/dialogue-coverage.csv` and JSON distinguish external *availability* from *held* and *AV-verified* completeness. Source text is not fetched from the web by this tool.

## Expanded original dialogue source locators

Two additional Subtitle Cat pages were directly inspected and indexed: [S01E03, The Former Harry Stone](https://www.subtitlecat.com/subs/1079/Night%20Court%20(1984)%20-%20S01E03%20-%20The%20Former%20Harry%20Stone%20(480p%20DVD%20x265%20Panda).eng.html) and [S04E15, A Day in the Life](https://www.subtitlecat.com/subs/1120/Night%20Court%20s04e15%20A%20Day%20in%20the%20Life.html). The canonical per-episode records and `catalog/subtitlecat-discovery.json` now recognize **21** episodes with separately located caption-display pages, without retaining transcript bytes.

`catalog/dialogue-source-queue.json`, CSV and readable Markdown build a 193-episode lead-priority matrix; **26 episodes have at least one verified direct dialogue page, 37 have topic-index evidence only, and 130 lack an episode-specific dialogue locator.** These totals can change when new sources are found and never imply held full transcript availability.

### Additional checked captions and quarantined reboot collisions

Additional external original-series caption pages were confirmed for S01E01, S01E07, S02E12, S05E01, S07E23 and S08E06 (a Dutch-language listing), plus a distinct second S09E22 subtitle version. Current Subtitle Cat coverage is **21 episodes across 22 page versions**. They are indexed, not imported as copyrighted caption text. The refreshed 193-row dialogue-source queue now has **26 direct-page episodes, 37 index-only episodes, and 130 lacking episode-specific dialogue leads**.

`catalog/rejected-dialogue-source-matches.json` records deceptive apparent original-series hits: a so-called Night Court season-three ZIP on TVSubtitles and a S01E05 “The Apartment” file actually conflict with the 1984 original episode names. Future ingestion must not assign those sources by season and episode number alone. [SRTFiles original-series landing page](https://www.srtfiles.com/subtitles/night-court-1984-1992) is an additional general-source lead, with no per-episode coverage assumed.

## Original season-three subtitle page cluster

[Subtitle Cat uploads 1666800–1666850](https://www.subtitlecat.com/list_page.php?from=1666800) publicly indexes **S03E01–S03E22** of the original Night Court (1984) as separate English-caption page listings uploaded May 9, 2025. All 22 individual episode page URLs were checked and preserved in `research/season03-caption-page-locations.json`. The metadata import did not retrieve, download, mirror, translate or quote the caption contents, and the site's known robots restrictions remain respected. The episode acquisition queue now lists 44 direct-page episodes, compared with 26 before this source pass.

## Dated June 2025 original-series caption upload list, seasons 5–9

The following six public Subtitle Cat upload-index pages show 105 manually checked distinct episode-labeled entries from the 1984 show: [1710550](https://www.subtitlecat.com/list_page.php?from=1710550), [1710600](https://www.subtitlecat.com/list_page.php?from=1710600), [1710650](https://www.subtitlecat.com/list_page.php?from=1710650), [1710700](https://www.subtitlecat.com/list_page.php?from=1710700), [1710750](https://www.subtitlecat.com/list_page.php?from=1710750), and [1710800](https://www.subtitlecat.com/list_page.php?from=1710800). The source rows are mapped to episode IDs in `research/later-season-2025-caption-upload-listings.json`. Each row is a **shared index URL**, not an independently opened episode caption page. Indexing metadata does not establish redistribution rights. The current verified-locator queue now identifies 121 episodes with index-only coverage (44 with direct page links) and 28 with no episode-specific lead.


## All original Season 4 caption-display URLs located

The [Subtitle Cat upload-page 1710150](https://www.subtitlecat.com/list_page.php?from=1710150) and [1710200](https://www.subtitlecat.com/list_page.php?from=1710200) both enumerate original-series Season 4 uploads from June 21, 2025. Their links and titles identify all **S04E01–S04E22**, confirmed against the actual episode pages. `research/season04-caption-page-locations.json` records each episode ID, permalink, source index, original display label and validation basis. `tools/add_verified_s04_caption_links.py` merges them as source **metadata only**, leaving caption contents and reuse rights unclaimed. Latest source-queue count: 64 direct pages, 121 index-covered episodes and eight with no dialogue locator.


## Five more exact original-series subtitle pages

Original caption-display pages now indexed: [S07E03](https://www.subtitlecat.com/subs/1121/night_court_s07e03_the_cop_and_the_lady.html), [S07E04](https://www.subtitlecat.com/subs/1121/night_court_s07e04_come_back_to_the_five_and_dime.html), [S09E06](https://www.subtitlecat.com/subs/1121/night_court_s09e06_guess_who_s_listening_to_dinner.html), [S09E20](https://www.subtitlecat.com/subs/1121/Night%20Court%20s09e20%20Opportunity%20Knock%20Knocks%201.html), and [S09E21](https://www.subtitlecat.com/subs/1121/night_court_s09e21_opportunity_knock_knocks_2.html). The URL mapping reflects each source's original-series episode identity and title variants. In `research/s07-s09-remaining-direct-pages.json` and each episode's `episode_sources` these are rights-unconfirmed *location references*, not copied TV dialogue.


### Verified publisher caption-enabled viewing alternatives for remaining three

Apple TV original-series episode pages explicitly advertise English (US) CC for [S09E08 *Teacher's Pet* (CA)](https://tv.apple.com/ca/episode/teachers-pet/umc.cmc.3um8xaumz7w0mjrn891m2sg4k?showId=umc.cmc.3v8igla11dgg4chywljv2og89), [S09E17 *Party Girl, Part 2* (US)](https://tv.apple.com/us/episode/party-girl-part-2/umc.cmc.5xgh3ov4a2c9kru8vn3n09xol?showId=umc.cmc.3v8igla11dgg4chywljv2og89), and [S09E19 *P.S. Do I Know You?* (CA)](https://tv.apple.com/ca/episode/ps-do-i-know-you/umc.cmc.55pw7ljknq3ttj9993slpfkdg?showId=umc.cmc.3v8igla11dgg4chywljv2og89). This establishes **caption-enabled streaming catalogue availability**, not availability of independently downloadable dialogue tracks. Content is copyrighted, region/payment requirements may apply, and zero caption file bytes were retrieved. See `catalog/streaming-cc-fallbacks.json`.


## Owner-imported original-series dialogue, 2026-10-23

**Two actual user-uploaded RARs physically preserved** in research/source-archives: 13 S01 SPRiNTER-labelled English SRTs and 22 S02 OSiTV-labelled English SRTs. All 35 subtitle files are stored as original bytes alongside source cue JSONL, readable text, hashes and edition/source attribution in their own episode dialogue/version directories. The precise byte-level source manifest is catalog/rar-ingestion-manifest.json; independently constructed inspection notes are research/season1-season2-subtitle-import-report.md. This is a source-acquisition milestone, unlike the previously catalogued external caption and transcript links. Full TV-episode completeness remains unverified.

## 28 October 2026: multilingual speaker-attribution screening

See [multilingual caption source audit](research/multilingual-speaker-evidence-audit-2026-10-28.md). The owner AVI videos contain no embedded subtitle tracks. Subtitle Cat offers translated S01E01 files (Afrikaans, Greek, Hebrew and Spanish), but the site explicitly identifies the upload's original language as English; these **do not add an independent speaking-character witness**. The original-season SUBDL season-one index visibly holds an English pack only and season nine displays no results. The German dubbing index provides limited episode-specific cast candidates but no per-line speaker labels. The screen confirmed **zero** standalone foreign-language transcripts with independently verified speaker attribution; keep all prior UNKNOWN and AV-verification status unchanged. For new finds, first distinguish original language from a translation button, then inspect actual voice-label syntax, and preserve immutable-source SHA and provenance family before proposing English speaker anchors.
