# Night Court: the original NBC series (1984–1992)

**Independent research archive**, inside the private `gamesbyian/general-purpose` repository. Scope excludes the 2023 revival. The purpose is durable, provenance-aware research and a future LLM-readable knowledge base about the original program, its fictional and production history, comedic conventions, cultural moment, and fandom.

## Actually held (23 October 2026)

- **193/193** original-series episode records: `seasons/Sxx/SxxEyy/episode.json`, spanning 9 seasons (13, 22, 22, 22, 22, 22, 24, 24, 22).
- **193/193** titles, dates, directors, writer-credit lines and production codes, reconciled from TVmaze and Wikipedia. Source-specific aliases are retained; composite broadcasts and ambiguous numbering are flagged.
- **193/193 CC BY-SA-licensed, episode-specific encyclopedia synopsis/capsule files**: `seasons/Sxx/SxxEyy/authorized-text/wikipedia-episode-capsule.wikitext`, each with `sources/wikipedia-capsule.provenance.json`. A five-entry discrepancy between Wikipedia's 188 episode-list rows and 193 actual episode parts is explained by paired broadcasts, whose shared summaries are annotated.
- Full MediaWiki source of **two openly licensed articles**, `research/licensed-wiki/Night-Court.wikitext` and `research/licensed-wiki/List-of-Night-Court-episodes.wikitext`, each with a Wikipedia revision permalink, attribution and license manifest.
- **1,663 provenance-bearing episode source references**, including many repeated series-index pointers. The number is *not* an independently recovered document count.
- Episode-level bibliography plus original analyst-created first-pass fact sheets for S01E01 and S02E10; fandom observation examples, source inventory and canonical knowledge-model design.

**Not held:** full scripts, proprietary dialogue transcriptions, closed-caption or subtitle tracks, copyrighted fan reviews and articles without reuse permission. The corresponding discovery links are retained, and holdings explicitly record zero for these categories. A private repository alone does not authorize copying them. If authorized materials become available, ingest each version in the relevant episode directory with precise provenance.

## Repository organization

```text
Night Court/
  README.md                   archive status, architecture and collection contract
  SOURCES.md                  source coverage and verification tiers
  KNOWLEDGE-MODEL.md          schema and future cross-episode analytical matrices
  catalog/
    index.json                ordered 193 episode paths and series-level metadata
    episodes.jsonl            query-friendly factual catalog
  seasons/
    S01/S01E01/
      episode.json            episode ID, credits, source links and holdings
      authorized-text/
        wikipedia-episode-capsule.wikitext
      sources/
        wikipedia-capsule.provenance.json
    ...
    S09/S09E22/
  research/
    licensed-wiki/            CC BY-SA original article revisions and attribution
    case-studies/             original preliminary scene/narrative analyses
    fandom-observations.md   time-stamped, qualified reception examples
    collection-runs.md        harvester instructions
  tools/
    refresh_episode_metadata.py
    discover_transcript_urls.py
    collect_open_wiki.py
    enrich_wikipedia_credits.py
    validate.py
.github/workflows/night-court-harvest.yml
```

## Sources discovered

- Forever Dreaming: **57 full-dialogue indexed topics**, all 57 episodes of seasons 1–3. Direct post URLs are saved where independently confirmed; others retain the index link until verified.
- Springfield! Springfield!: **47 indexed scripts** (13 S01; 12 S02; 22 S03). Inferred direct URLs are explicitly marked as **unverified**.
- Subtitle Cat: verified caption-display pages for S04E01 and S09E22.
- SUBDL: original-series landing page with season filters, but complete per-episode availability remains **unverified**.
- Wikipedia, TVmaze, TheTVDB, IMDb, TV Guide, fan wikis and fandom threads: season-level and episode-level factual/reception discovery pointers.

`SOURCES.md` contains the actual URLs, and each episode has a structured source list. **An index link is not equivalent to an archived source document.**

## Collection and synthesis rules

1. Distinguish verified page, indexed episode listing, constructed URL, and physically stored file. Reflect the difference in machine-readable `episode_sources[].level`, `verified`, and `holdings`.
2. For each retained version save URL, author/publisher, revision, license/reuse basis, retrieval method, timestamp, hash if held, language, source-specific episode identifiers, and mapping confidence.
3. Preserve multiple captions, scripts, reviews, versions and contradictions independently. Prefer source-level evidence over any single synopsis and keep uncertain assignments explicit.
4. Separate fictional character and event graphs from actor/production/industry information; label narrative interpretation, joke taxonomy and reception claims as interpretations with supporting evidence.
5. Analyze fandom by era and community (contemporary criticism, syndicated reruns, later nostalgia, comparison with the revival). Never treat a few comments as representative consensus.
6. Use the existing project-level `KNOWLEDGE-MODEL.md` before generating canonical artifacts. Scene, character, comedy, affect, production and cultural-context matrices belong in a later evidence-led pass, not a fabricated transcription.
7. Do not modify independent repository tools or sensitive features such as the Shaw gateway.

## Operational controls

The dedicated GitHub Actions workflow runs a **single bounded 12-minute job**, validates records, retrieves TVmaze facts, discovers only transcript *links* (respecting robots policy), collects two explicitly CC BY-SA Wikipedia wikitext snapshots with attribution, imports 193 sets of production metadata and licensed capsules, then commits only `Night Court/` on its designated research branch. Manual invocation is also available. These stages are rerunnable and leave existing data intact on most individual-source failures.

Locally run:

```sh
python "Night Court/tools/validate.py"
python "Night Court/tools/refresh_episode_metadata.py"
python "Night Court/tools/discover_transcript_urls.py"
python "Night Court/tools/collect_open_wiki.py"
python "Night Court/tools/enrich_wikipedia_credits.py"
python "Night Court/tools/validate.py"
```

## Expanded evidence indexing and guest credits, 23 October 2026

The second bounded GitHub Actions pipeline (`.github/workflows/night-court-knowledge.yml`) has populated the episode retrieval corpus and new contextual sources:

- **193/193 evidence dossiers** (`seasons/Sxx/SxxEyy/derived/evidence-dossier.json`) and human-readable reading notes (`derived/reading-note.md`) with explicit links to the original licensed Wikipedia source and revision.
- **342 source-authored synopsis statements**, with character offsets and per-episode `annotations/synopsis-statements.jsonl` files, available together as `catalog/source-statements.jsonl`. They are not verified events or scene transcripts.
- **440 character-name mention relationships** and **255 topic keyword signals**, queryable through the `catalog/character-mentions.jsonl`, `catalog/theme-cues.jsonl`, `catalog/episode-knowledge.jsonl` and `tools/query_corpus.py` files. Labels expressly warn that text mention does not prove appearance.
- **1,210 TVmaze episode guest actor-character credit edges**, covering all 193 episodes; a series-level main cast of **14 credited relationships**, with **797 distinct credited people** and **974 distinct credited character IDs** overall. See `catalog/cast-relationship-graph.json`, `catalog/guestcast-edges.jsonl` and `catalog/tvmaze-guestcast-coverage.json`. These are *credits*, not direct evidence of on-screen appearances.
- **19 additional Creative Commons-licensed Wikipedia articles**, mostly bios of series cast and creators, stored with exact revision, SHA-256 and attribution at `research/licensed-wiki/context/`.
- A cautious Fandom collector checked access and recorded **`blocked_by_robots`**. No Fandom wiki articles were copied. See `research/fandom-wiki/collection-status.json`.
- `catalog/holdings-coverage.json` and `catalog/holdings-coverage.csv` audit all 193 episode directories. **Full scripts held: 0. Caption tracks held: 0. Full critic/reviewer articles held: 0.** Links and source discovery are not conflated with preserved content.

The indexed guest cast is unusually useful: it supplies specific credit links between actors, recurring or one-off roles and episodes, including cast names not present in the short encyclopedia synopses. Separately, the source-statement ledger makes it possible to inspect exactly why a lexical search result was returned.

**Try the local retrieval CLI** from the repository root:

```sh
python "Night Court/tools/query_corpus.py" --character harry-stone --limit 5
python "Night Court/tools/query_corpus.py" --actor "Rita Taggart"
python "Night Court/tools/query_corpus.py" --theme politics-and-government --limit 20
python "Night Court/tools/query_corpus.py" --director "Jeff Melman" --season 4
```

See [RESEARCH-ROADMAP.md](RESEARCH-ROADMAP.md) for the next source-acquisition passes, licensing requirements, evidence-quality gates, canonicalization plan and handoff boundaries.

Canonical scene, event, mood, joke, fandom and period-context knowledge remains **unbuilt**. The current corpus is a large, testable evidence and retrieval substrate, not an allegedly transcript-complete or eyewitness-validated reconstruction.


## Subtitle location follow-up, October 23, 2026

A dedicated research lane added **13 individually verified episode-specific Subtitle Cat caption-display URLs** to the record set, including examples in seasons 1, 2, 3, 4 and 9. The per-episode source records and `catalog/subtitlecat-discovery.json` preserve each URL and distinguish an externally readable caption display from a held SRT. The audited total is now **1,663 source pointers**; exactly **13 episodes** have a located Subtitle Cat page, while **0 complete subtitle files** are held in the repository.

The site's robots policy blocked automated search/upload-index collection, so the metadata harvester saved only previously verified episode page URLs. It did not fetch subtitle text, invent search coverage, or bypass the site's access restriction.

Additional **legal streaming/caption witnesses** discovered for the original are [Apple TV's original-series listing](https://tv.apple.com/ca/show/night-court/umc.cmc.3v8igla11dgg4chywljv2og89), showing English (US) CC, and [Prime Video season-one episode listings](https://www.primevideo.com/detail/0JKQMQRYLQ7AQRRSNOGZQAN1PB). These are distributor/catalogue references, not proof of any locally saved caption or separate episode synopsis text.


## Original broadcast and reception measurements

The new `catalog/broadcast-context.json` and `broadcast-context.csv` reconstruct season-level U.S. television-series rankings, annual season household ratings, episode household rating/share and later reported U.S. viewer counts from the revision-pinned Wikipedia episode list. Its `research/broadcast-context.md` gives a short human-readable overview.

These fields **cannot all be compared directly**: household rating points, shares and viewers in millions have different denominators. Jointly broadcast multi-part episodes are not double-counted in the season summaries. This is historically useful audience evidence with secondary-source provenance, not a claim about why the comedy's popularity changed.


## Contemporary press and reception source provenance

`research/contemporary-press-bibliography.jsonl` now indexes **15 separately identified** press, industry, historic broadcasting, criticism and fandom sources, emphasizing two contemporaneous interviews with original producers and actors. `research/production-and-reception-claims.jsonl` holds **12 attributed analytical/production claims**, each with supporting source identifiers, confidence, boundaries and caveats. `research/press-evidence-brief.md` is a readable, original interpretive note; third-party full articles and reviews are *not* copied. Dates and original-series vs revival identity are explicit.

`research/source-conflicts.json` records **four significant interpretive or source disagreements**, including two different Season 1 ranking/rating values published in different Wikipedia revisions, the distinction between the May 13, 1992 story finale and May 31 last broadcast, and contradictory modern fan-ranking sources. Never resolve the season-one statistical discrepancy merely by preference for a more recent revision. The `night-court-press.yml` workflow validates source-link integrity and claim provenance.


## Immutable preservation of revision-pinned encyclopedia sources

All **21 currently held licensed Wikipedia source articles** (two original-series reference articles and 19 cast/production/context articles) now also have their own immutable copies in `research/licensed-wiki/revisions/` using a canonical article/revision-ID path. Each copy has a separate attribution/license manifest and SHA-256 digest. `catalog/wiki-revision-archive.json` indexes those **21 saved revisions**, not the entire upstream edit history.

Run `tools/preserve_wiki_revisions.py` both **before and after** future encyclopedia source refreshes, as now wired into the dedicated harvest and indexing workflows. Identical revision IDs with different bytes fail closed, while subsequent revisions accumulate without overwriting older held versions. This guards against upstream edits and disappearing pages beyond Git's commit history.


## Dialogue import is now operational

The repository includes a **source-preserving dialogue import pipeline** for materials supplied by the researcher: SRT, VTT and plain-text transcripts. See [DIALOGUE-INGESTION.md](DIALOGUE-INGESTION.md) for the local command, Android/GitHub upload workflow, edition/rights manifest, checksums, multiple-version handling and independent completeness QA. Import goes to `seasons/Sxx/SxxEyy/dialogue/versions/`; `catalog/dialogue-index.jsonl`, `catalog/dialogue-coverage.json` and `catalog/dialogue-coverage.csv` report genuinely held witnesses separately from external source pointers. Test fixtures are synthetic.

**As of this change, no actual full scripts or caption tracks have been imported.** The tooling and GitHub Actions pipeline can preserve multiple full source witnesses once they are supplied. Each track's declared completeness is recorded, but only future audiovisual verification can establish whether it is genuinely episode-complete. No DRM circumvention or scraping is performed by the importer.

Research and private-copying exceptions may be relevant to legitimate user-held sources, subject to the circumstances. The archive retains an explicit rights/source declaration without claiming to make a definitive legal finding.


### Search and source-quality diagnostics

`tools/search_dialogue.py` provides source-attributed search over the *held* transcript/caption versions and the 193 licensed episode capsules. Search hits return cue timestamps, explicit speaker markers when present, edition and source checksum; a synopsis result is explicitly marked **not dialogue**. With no held dialogue, only synopsis search has results.

`tools/audit_dialogue_quality.py` produces SHA-tied per-version QC and `catalog/dialogue-quality.json` / CSV, including approximate counts, cue overlaps, suspect source gaps and flags requiring audiovisual review. These metrics do not prove completeness or missing dialogue. The existing GitHub Actions import workflow tests and regenerates them on each imported batch.
