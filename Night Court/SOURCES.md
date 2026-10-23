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
