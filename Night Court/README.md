# Night Court: the original NBC series (1984–1992)

**Independent research archive**, inside the private `gamesbyian/general-purpose` repository. Scope excludes the 2023 revival. The purpose is durable, provenance-aware research and a future LLM-readable knowledge base about the original program, its fictional and production history, comedic conventions, cultural moment, and fandom.

## Current acquisition acceptance, October 23, 2026

**Dialogue source presence: 193/193 episodes, with no remaining unheld episode IDs.** The authoritative, automatically regenerated records are [dialogue coverage](catalog/dialogue-coverage.json), [dialogue source queue](catalog/dialogue-source-queue.json), [dialogue quality](catalog/dialogue-quality.json) and [archive status](catalog/archive-status.json). Historical sections below record earlier acquisition checkpoints and are *not* current coverage statements.

Season-by-season held episodes: **S01 13/13, S02 22/22, S03 22/22, S04 22/22, S05 22/22, S06 22/22, S07 24/24, S08 24/24, S09 22/22.** All except S09E19 have original timed English caption sources. S09E19 holds 347 original display paragraphs (approximately 2,337 words) as **untimed text**, not an SRT and not a confirmed full script.

The automated quality report has **56 witnesses with at least one heuristic review flag**, and zero independent AV-completeness certifications. Such flags may reflect legitimate overlaps or silent scenes. No cross-episode identical long-text collisions were detected. The remaining work is edition-aligned audio/video QA, overlap and cue-gap review, speaker attribution, scene boundaries and evidence-linked visual actions, not wholesale rediscovery of episode captions. See [S09E19 source acquisition](research/s09e19-final-dialogue-acquisition.json) for the sole untimed source and [the source-to-script factory plan](AV-SCRIPT-FACTORY-PLAN.md) for the next pipeline.

## First multimodal script evidence: S01E01 pilot

The project's first source-grounded [**integrated script excerpt**](seasons/S01/S01E01/derived/scene-review-v3/scene-script-v3.md) now combines genuine S01E01 spoken-caption witnesses with reviewed static and temporally ordered visual evidence from the original SHA-fingerprinted AVI, including a desk-telephone action. The evidence covers **01:00–01:30 only**, not a full episode. Read the [machine-readable claim/evidence map](seasons/S01/S01E01/derived/scene-review-v3/scene-evidence-map.json) for provenance and limits.

The [utterance acoustic report](seasons/S01/S01E01/derived/scene-review-v3/utterance-acoustic-review.md) records actual mixed-TV-audio pitch and intensity candidates for ten ASR-proposed speech spans. It does **not** validate speaker identity, expressive emotion, sarcasm, independent word-level forced alignment, continuous-video completeness or a finished production screenplay. These missing gates drive the [AV script factory plan](AV-SCRIPT-FACTORY-PLAN.md) and [S01E01 acceptance handoff](S01E01-AV-PILOT-HANDOFF.md).

## All-episode reading-script scaffolds

Every original episode now has a [source-only reading script](seasons/S01/S01E01/derived/source-script-scaffold-v1.md) in its `derived/` directory, built from the held caption witness with original source cues and an explicit **UNIDENTIFIED VOICE** label wherever the source is unattributed. [PR #156](https://github.com/gamesbyian/general-purpose/pull/156) passed all-193 CI, producing 70,804 original cues, 72,733 candidate dialogue units and 1,173 caption-gap blocks across 193 scripts. [See complete scaffold coverage](catalog/source-script-scaffold-coverage.json). These are **not** claimed to be actual production screenplays: they have no verified settings, speaker assignments, physical action, vocal-performance interpretation or episode-wide AV completeness. The first actual multimodal scene example is [S01E01 scene v3](seasons/S01/S01E01/derived/scene-review-v3/scene-script-v3.md).

## Actually held (23 October 2026)

- **193/193** original-series episode records: `seasons/Sxx/SxxEyy/episode.json`, spanning 9 seasons (13, 22, 22, 22, 22, 22, 24, 24, 22).
- **193/193** titles, dates, directors, writer-credit lines and production codes, reconciled from TVmaze and Wikipedia. Source-specific aliases are retained; composite broadcasts and ambiguous numbering are flagged.
- **193/193 CC BY-SA-licensed, episode-specific encyclopedia synopsis/capsule files**: `seasons/Sxx/SxxEyy/authorized-text/wikipedia-episode-capsule.wikitext`, each with `sources/wikipedia-capsule.provenance.json`. A five-entry discrepancy between Wikipedia's 188 episode-list rows and 193 actual episode parts is explained by paired broadcasts, whose shared summaries are annotated.
- Full MediaWiki source of **two openly licensed articles**, `research/licensed-wiki/Night-Court.wikitext` and `research/licensed-wiki/List-of-Night-Court-episodes.wikitext`, each with a Wikipedia revision permalink, attribution and license manifest.
- **1,825 provenance-bearing episode source references**, including many repeated series-index pointers. The number is *not* an independently recovered document count.
- Episode-level bibliography plus original analyst-created first-pass fact sheets for S01E01 and S02E10; fandom observation examples, source inventory and canonical knowledge-model design.

**Now held:** **193/193 original-series episodes have a versioned English dialogue witness**: 192 timecoded SRTs (35 owner-supplied for S01–S02, plus 157 acquired original-series online sources) and one source-page-derived **untimed** transcript (S09E19). Every witness has source provenance and the canonical episode dialogue index. **Not established:** independent audiovisual completeness, speaker identity, original production screenplays, or publication/reuse rights for externally hosted scripts. Original caption downloads, held dialogue witnesses, external research leads, and AV-verified complete transcripts remain distinct evidence types.

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

A dedicated research lane added **21 individually verified episode-specific Subtitle Cat caption-display URLs** to the record set, including examples in seasons 1, 2, 3, 4 and 9. The per-episode source records and `catalog/subtitlecat-discovery.json` preserve each URL and distinguish an externally readable caption display from a held SRT. The audited total is now **1,672 source pointers**; exactly **21 episodes** have a located Subtitle Cat page, while **0 complete subtitle files** are held in the repository.

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

**Historical checkpoint (superseded): at this earlier stage, no actual full scripts or caption tracks had yet been imported. See the current acquisition acceptance above.** The tooling and GitHub Actions pipeline can preserve multiple full source witnesses once they are supplied. Each track's declared completeness is recorded, but only future audiovisual verification can establish whether it is genuinely episode-complete. No DRM circumvention or scraping is performed by the importer.

Research and private-copying exceptions may be relevant to legitimate user-held sources, subject to the circumstances. The archive retains an explicit rights/source declaration without claiming to make a definitive legal finding.


### Search and source-quality diagnostics

`tools/search_dialogue.py` provides source-attributed search over the *held* transcript/caption versions and the 193 licensed episode capsules. Search hits return cue timestamps, explicit speaker markers when present, edition and source checksum; a synopsis result is explicitly marked **not dialogue**. With no held dialogue, only synopsis search has results.

`tools/audit_dialogue_quality.py` produces SHA-tied per-version QC and `catalog/dialogue-quality.json` / CSV, including approximate counts, cue overlaps, suspect source gaps and flags requiring audiovisual review. These metrics do not prove completeness or missing dialogue. The existing GitHub Actions import workflow tests and regenerates them on each imported batch.


### Local-source episode media to dialogue

`tools/extract_local_media.py` adds a way to generate source-preserved SRT dialogue witnesses from **locally held, DRM-free episode containers**, using embedded text subtitle streams or opt-in offline faster-whisper speech recognition when captions are unavailable. It can inspect individual media, extract specific or all subtitle streams, and batch-process a folder of SxxEyy-labeled original-series videos. It requires explicit original-series and source/rights confirmation before importing, and keeps video/audio outside the repository. [Detailed commands and limitations](DIALOGUE-INGESTION.md). A separate narrow synthetic MKV workflow checks the end-to-end subtitle extraction path.

### Dialogue source acquisition priority matrix

`catalog/dialogue-source-queue.json`, CSV and Markdown now classify all 193 original episodes by direct dialogue link, index-only lead, unverified pattern or no episode-level lead. They rank episodes needing independent collection and preserve actual source URLs without misrepresenting linked pages as downloaded transcript text. S01E03 and S04E15 added as individually inspected Subtitle Cat pages (15 caption-page episodes total). Run `tools/build_dialogue_source_queue.py` after source inventories change; it also reconciles `catalog/archive-status.json` against the actual holdings audit.


### Bulk subtitle source packages

For up to 500 caption/transcript files at once, `tools/import_dialogue_bundle.py` accepts a single bounded ZIP plus one original-series provenance declaration. It maps every SxxEyy file to its episode directory, preserves originals and source fingerprints, and reruns the existing dialogue-search/quality infrastructure. The private GitHub Actions upload workflow imports ZIPs automatically. [Usage and safeguards](DIALOGUE-INGESTION.md).


### Multiple-dialogue-witness concordance

`tools/compare_dialogue_versions.py` compares each episode's separately held dialogue variants without naming any of them canonical. It preserves original edition/hash provenance, reports likely duplicate wording, subset overlap and divergent transcript passages, and warns about identical long text assigned to different episodes. The global file is `catalog/dialogue-variant-comparison.json`. As with the quality ledger, its value will grow when the first complete original-series dialogue witnesses are actually imported.

### Latest episode-specific caption discovery

The checked external Subtitle Cat inventory now contains **21 original-series episodes with 22 separately located caption page versions**, including new season-five, seven and eight examples. [Source locations and ranked gap queue](catalog/dialogue-source-queue.md) exposes a truthful status for all 193 episodes. The archive also maintains a quarantine list of two 2023-revival/misnumbered subtitle sources to prevent similarly numbered episodes from contaminating the original research corpus.

## Season-three caption source verification (23 October 2026)

A separately researched public [Subtitle Cat upload index](https://www.subtitlecat.com/list_page.php?from=1666800) identifies all **22** episodes of the original 1984–1992 series' third season, in a 9 May 2025 batch of English DVD-caption display pages. All 22 episode-specific page URLs were individually checked and saved in `research/season03-caption-page-locations.json`, and the corresponding episode source records were reconciled without storing the caption text itself.

The latest **193-episode acquisition queue** is now **44 episodes with direct external dialogue-page links, 19 with index-only pointers, and 130 without an episode-specific locator**. Across Subtitle Cat specifically, the archive records 40 episode IDs and 41 page variants. The **full locally held episode dialogue count remains zero**. See `catalog/dialogue-source-queue.json`, `catalog/holdings-coverage.json`, and `catalog/subtitlecat-discovery.json` for distinct denominators and source statuses.

## Later-season original-series caption listings (23 October 2026)

A dated [June 2025 Subtitle Cat upload cluster](https://www.subtitlecat.com/list_page.php?from=1710700) contains independently observed **105 original-series English subtitle *listings*** for seasons 5–9. These are mapped episode-by-episode in `research/later-season-2025-caption-upload-listings.json`, with the exact source-index page of each listing. The listing itself is not a verified individual caption display page and no caption text was copied.

The 193-episode acquisition queue now reports **44 episodes with direct external dialogue page URLs**, **121 with episode-labeled source-index coverage**, and just **28 without an episode-specific dialogue lead**. All 22 episodes of seasons 5 and 6, 22/24 of season 7, all 24 of season 8, and 16/22 of season 9 have at least a source locator. External source discovery is not source acquisition: held complete dialogue remains **0 episodes**. See `catalog/dialogue-source-queue.json` and the rights notes in `DIALOGUE-INGESTION.md`.


## Season 4 dialogue-source evidence: complete external page mapping (October 23, 2026)

A separate evidence pass mapped **all 22** original 1984-series Season 4 episodes to their individual Subtitle Cat caption-display pages, including **20** episodes previously lacking any dialogue-specific locator. Verified source upload indexes from June 21, 2025: [1710150](https://www.subtitlecat.com/list_page.php?from=1710150) and [1710200](https://www.subtitlecat.com/list_page.php?from=1710200). The exact per-episode external URLs and source observations are in `research/season04-caption-page-locations.json`, with references attached to each episode's `episode_sources`.

After rebuilding `catalog/dialogue-source-queue.json`, **64/193** episodes have direct external dialogue/caption pages, **121/193** have index-only leads and **8/193** still lack specific dialogue locators (S07E03–E04, S09E06, E08, E17, E19–E21). **No episode-complete copyrighted subtitle file was downloaded or mirrored** during this pass. The SRT/VTT/local-media ingestion and audiovisual quality tools remain ready for separately provided files.


### Original S07/S09 caption-source cleanup

Five more independently opened external caption-display pages have been mapped to S07E03, S07E04, S09E06, S09E20 and S09E21. A source-specific title variant calls the finale `Opportunity Knock Knocks`, while the catalogue records `Opportunity Knocks`; aliases are not conflated with different episodes.

The updated 193-episode acquisition queue now shows **69 direct episode pages**, **121 episodes indexed at a series/season source**, and **3 without a specific dialogue locator**: S09E08, S09E17 and S09E19. These counts measure research pointers, not locally saved scripts or subtitle files. `research/s07-s09-remaining-direct-pages.json` records source URLs and evidence without copying the protected dialogue.


### Caption-enabled licensed-provider viewing for the final three missing dialogue leads

The only three episodes not yet linked to an external downloadable transcript/caption-display page or an episode-specific caption-upload index are S09E08, S09E17 and S09E19. Each now has an **episode-specific Apple TV listing explicitly advertising English (US) CC**, catalogued as `episode_streaming_catalog` instead of a transcript locator. Their source metadata, platform regions and reported runtimes appear in `catalog/streaming-cc-fallbacks.json`.

These publisher listings may require access, purchases or regional availability. They do **not** deliver an exported SRT, confirm a source-video match, or authorize copying protected captions. The acquisition queue continues to report **69 direct third-party caption/transcript pages, 121 index-only leads and 3 episodes with no exported-dialogue source**, while the streaming-CC supplement covers those three for future audiovisual research.


## Owner-provided Seasons 1–2 SRT dialogue acquisition: complete import

Both owner-uploaded RARs have been extracted and relocated to `research/source-archives/`. All **35 episode-specific English SRT files** are physically held, one per S01E01–S02E22 episode, with **12,995 timestamped cues** and roughly **91,345 transcript words**. The existing importer keeps original subtitle bytes as `original.srt`, plus `segments.jsonl`, `readable.txt`, `manifest.json` and `quality.json` under each episode's `dialogue/versions/` directory. Original archive hashes and all 35 original member filenames are indexed in `catalog/rar-ingestion-manifest.json`.

Thirty-four tracks had no automated quality flags. **S01E11** received one review flag for adjacent repeated caption text. Although the files reach roughly 22–23 minutes of source timing, **none is independently video-verified as complete**. `catalog/dialogue-coverage.json`, `catalog/dialogue-quality.json` and `catalog/dialogue-index.jsonl` now reflect actually held source text. See [the source import and quality report](research/season1-season2-subtitle-import-report.md). Next acquisition priority is Season 3 onwards, not reacquiring these 35 episodes.


## Text-only AI character attribution programme (source-backed preparation)

The first two user-supplied seasons comprise 35 locally held English dialogue tracks. A bounded offline preparer now splits their 12,995 original caption cues into 15,014 *potential utterances*, producing 370 overlapping text-only attribution work packets, plus per-version credited-character rosters, direct-address clues and cautious provisional scene boundaries. These are **unattributed work units**. No agent has yet claimed an actual named speaking part from this process.

The complete multi-agent strategy, worker/skeptic contracts, model calibration and limits are documented in [TEXT-ONLY-SPEAKER-ATTRIBUTION.md](TEXT-ONLY-SPEAKER-ATTRIBUTION.md). `tools/prepare_speaker_attribution.py` creates the evidence packets; `tools/reconcile_speaker_votes.py` validates separately submitted agent votes and renders an explicitly provisional script when at least one voting file exists. Low-confidence/conflicting assignments remain UNKNOWN. In particular, the caption's addressee is not automatically the caption's speaker, credited guest appearances are not guaranteed, and scene headings are not invented from unseen footage.

## FTP integration (S60-compatible)

The dedicated read-only inventory and one-file staging workflow is described in [FTP-ACCESS.md](FTP-ACCESS.md). It reuses S60's Seedhost FTP host/account configuration and requires **a separate `FTP_PASSWORD` Actions repository secret in `gamesbyian/general-purpose`**. Credentialed FTP access is manual-dispatch only. The existing 35 S01/S02 subtitle tracks are already preserved; do not download them again merely to establish FTP access.

## Audiovisual script-generation plan

See [AV-SCRIPT-FACTORY-PLAN.md](AV-SCRIPT-FACTORY-PLAN.md) for the proposed episode processing factory: source-faithful mono FLAC, optional Opus listening copies, sparse timestamped visual references with targeted 3–4 fps windows, ASR alignment, speaker diarization, source-backed scripts, and separate FTP/Drive storage. Existing remote TVRip root is `/downloads/Night Court TVRip S1-S9`; the existing FTP video metadata workflow still requires a manual dispatch for a real inventory. The 35 S01/S02 subtitle witnesses are already preserved and must not be reimported unnecessarily.
