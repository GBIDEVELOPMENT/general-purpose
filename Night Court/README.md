# Night Court (NBC original, 1984–1992): source archive and knowledge corpus

Scope: **only** the Harry Anderson / Reinhold Weege original series, not the 2023 revival. A dedicated project inside the private general-purpose repository; independent of all other utilities and audit data.

## Current material, 2026-10-23

- All **193 season/episode identities**, nine seasons, have their own `seasons/Sxx/SxxEyy/episode.json` records. Season counts: 13, 22, 22, 22, 22, 22, 24, 24, 22.
- **80 episode titles** verified from public episode indices are seeded (S01–S03 and S09; also S04E01), with **113 title slots intentionally unfilled** awaiting automated source reconciliation.
- The catalog retains **57 episode-level Forever Dreaming transcript index entries** (S01–S03) and **47 Springfield! Springfield! transcript-index entries** (13 + 12 + 22), plus isolated caption pages for S04E01 and S09E22. A verified index does not mean the full text is stored here.
- Six source-guide/index references are attached to each episode record as broad discovery pointers. Episode-specific evidence is distinguished by `level` and `verified`.
- No third-party full scripts, subtitle files, review articles or wiki content has been copied into this repository. `holdings` arrays remain empty until a lawful/licensed/user-supplied artifact is ingested and checked.

## Folder contract

```text
Night Court/
  README.md
  SOURCES.md
  KNOWLEDGE-MODEL.md
  catalog/
    index.json
    episodes.jsonl
  research/
    fandom-observations.md
    case-studies/
      S01E01.md
      S02E10.md
  seasons/
    S01/S01E01/episode.json  ... S09/S09E22/episode.json
  tools/
    refresh_episode_metadata.py
    validate.py
```

Subsequent holdings inside an episode directory:
```text
sources/           per-source manifests, retrieval records, link rot checks
authorized-text/   only content with suitable reuse rights, plus attribution/license
derived/           original canonical episode synopsis, story beats, character arc claims
annotations/       structured scenes, jokes, historical references, emotion and tone
```

## Source and evidence rules

1. Record **every version independently**: captions (with timecodes), fanscripts, DVD/streaming subtitles, contemporary listings, episode recaps, criticism, fandom discussions. Do not flatten conflicting observations.
2. Provenance is first-class: URL, publisher, author, accessed timestamp, rights basis, retrieval success, normalized identifier, content hash (if held), version, language, season/episode mapping confidence.
3. `verified: true` means the page or its containing index was inspected; check `level` before interpreting it as direct episode coverage.
4. Do not infer that a listing implies downloadable subtitles for all episodes, nor that a URL constructed from a known pattern was fetched.
5. Respect source rights and terms: a private repository is not itself permission to reproduce entire copyrighted dialogue, subtitles, articles or reviews. For material without redistribution/reproduction rights, preserve precise pointers, bibliographic data and original analytical summaries. Imported licensed or user-provided material can live under `authorized-text/`, with rights provenance.
6. Use mechanically generated IDs by season/episode rather than source-specific overall numbering. Keep aliases and disagreements. Never let a recap override actual episode evidence silently.
7. Separate **what happens in the fiction**, **how a joke works**, **production facts**, **period context**, and **viewer commentary**, each with its own evidence confidence and temporal scope.

## Next collection passes

- Use the local refresh tool to fill remaining titles, air dates and TVmaze identifiers from the public episode API, then validate the nine-season shape. Be prepared for divergent episode splitting/numbering and do not invent resolutions.
- Harvest *metadata and canonical URLs* from episode indexes and fan wiki backlinks, season by season, respecting rate limits and robots policies. Track source availability, timestamp and redirects.
- Capture independent audience reception by date and community; isolate present-day rewatch commentary from first-broadcast reception. Never frame a Reddit sample as fandom consensus.
- Create canonical analysis **after** a representative multi-source sample is indexed, with explicit source-to-claim citations and contradictions, not from a single synopsis.
- Maintain continuity and cast/crew change graph across episode boundaries.

See `SOURCES.md` and `KNOWLEDGE-MODEL.md`.
