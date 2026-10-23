# Night Court research: collection programme and evidence gates

**Scope:** The NBC original, 1984–1992, 193 episodes. Not the revival. This archive is for search, factual research and eventual carefully sourced interpretation of the program, creative processes and its audiences.

## Verified present state (October 23, 2026)

- 193 complete episode IDs, original air dates, titles, director/credited writer and production code.
- 193 per-episode CC BY-SA encyclopedia capsules, with revision provenance, and 2 entire archived Wikipedia article revisions.
- 193 machine-readable evidence dossiers plus readable notes derived from the licensed synopses; a global episode search JSONL, character-name index and lexical topic index.
- 193 episodes have episode-specific guestcast API credit coverage from TVmaze; 1,210 episode/actor/role credit edges. The show-level main cast and crew are separately attributed.
- 19 additional CC BY-SA Wikipedia articles preserved for principal cast, creators, and context; 2 attempted context titles were unavailable.
- Initial set of individual episode transcript/index pointers (Forever Dreaming 57, Springfield! Springfield! 47), subtitle display pointers and fan/wiki/review bibliographic references.
- Fandom API article capture attempted but refused at robots-policy check, recorded in `research/fandom-wiki/collection-status.json`. **Zero Fandom article full texts imported**.
- **Zero proprietary full scripts, complete TV subtitle tracks and full editorial reviews imported.** This limitation is explicit in the episode-by-episode holdings CSV/JSON.

Do not add together counts of pointers, excerpts, sentences and guest roles as if they were independent source documents.

## The evidence ladder

1. **Held primary version:** screenplay/captions/actual broadcast material when authorized, with timing/version data, rights provenance and checksum. None held yet.
2. **Held licensed secondary source:** Wikipedia pages, episode summaries, contextual articles with article revision, attribution and license manifest. These describe the work rather than constituting the work itself.
3. **Credited database relationship:** TVmaze show-level person-character role, TVmaze episode guest role, Wikipedia named episode writer/director. Credits are not automatically proof of scenes, onscreen appearances or authorship of any particular joke.
4. **Indexed reference:** third-party transcript/review site/season page. A listing may be stale, inaccessible or incomplete; it is not a stored copy.
5. **Machine-derived retrieval clue:** a character name or topic term appears in a synopsis. These are *search hints*, not canonical narrative facts.
6. **Interpretive assertion:** comedy mechanism, pathos, moral framing, topical reference, audience opinion, production hypothesis. Requires a source-linked human or reviewed machine explanation and separately stated confidence.

Everything built so far belongs to tiers 2–5. Treat all secondhand synopsis assertions as possibly incomplete, especially combined-broadcast capsules shared across two episodes.

## Files and scripts

| Path | Purpose |
|---|---|
| `catalog/episode-knowledge.jsonl` | 193 retrieval records with readable licensed synopsis, credit lines, lexical names/themes, source permalink |
| `catalog/character-mentions.jsonl` | Explicit character-name string detection (not onscreen appearances) |
| `catalog/theme-cues.jsonl` | Documentary term flags for future search and classification |
| `catalog/source-statements.jsonl` | Citation-addressable sentence fragments with text offsets, linked back to wikitext |
| `catalog/cast-relationship-graph.json` | Show-wide cast, episode guest credits and person/character IDs |
| `catalog/guestcast-edges.jsonl` | Flat one-episode-per-guest-role relationships |
| `catalog/production-relationships.json` | Production-credit partner counts by episode parts |
| `catalog/holdings-coverage.csv` | Machine-readable 193-row preservation gap matrix |
| `catalog/holdings-coverage.json` | Summary and per-season source/holdings counts |
| `research/licensed-wiki/context/` | 19 context article wikitext copies, manifest and revision/license provenance |
| `tools/query_corpus.py` | Conservative local command-line searches over the indexed episode evidence |

To retrieve, from repo root:

```sh
python "Night Court/tools/query_corpus.py" --text "Christmas"
python "Night Court/tools/query_corpus.py" --character dan-fielding --season 2
python "Night Court/tools/query_corpus.py" --theme romantic-relationships --limit 25
python "Night Court/tools/query_corpus.py" --actor "Rita Taggart"
python "Night Court/tools/query_corpus.py" --director "Jeff Melman" --limit 40
```

Do not confuse `--actor` guestcast matching with starring cast appearance: main-series cast has *no per-episode evidence* in this source. Future casting continuity work must independently locate credited or visible appearances.

## Outstanding work ordered by marginal information value

**A. Original dialogue and timed captions, by specific episode/version.** Confirm exact subtitle/script coverage, starting with S04–S09, then complement S01–S03. Evaluate different DVD, syndication, streaming and broadcasting edits separately. When redistribution/reproduction is authorized, import source bytes and store checksum, timing, edition, provenance and mapping confidence. Otherwise retain a durable locator and independent original notes. Track failures rather than quietly deleting links. Avoid crawling sites that disallow it.

**B. Alternate licensed wiki and secondary recaps.** Look for source sites with clear reuse permissions. Preserve independent article revisions, by episode; separate amateur analysis from factual recaps and production trivia. Fandom's currently robots-blocked endpoint is not an invitation to circumvent its restrictions.

**C. Actual story-event, character, joke and cultural-reference annotations.** Begin with a small highly documented sample covering the pilot, Selma/Flo/Roz changes, multipart crises, courtroom-docket episodes, and the finale. Validate claims against full episode source where possible. Expand only with explicit source-to-claim evidence, contradiction flags and version identifiers. Do not promote lexical classifications to researched comedy taxonomies automatically.

**D. Production and continuity crosscheck.** Normalize credited co-writers to distinct people with aliases and source links; verify exact director/guest performer credits independently. Build character tenure/changes with evidence, not guessed season-wide presence. Production-code ordering and broadcast chronology may differ.

**E. Audience and fandom record.** Catalog 1980s contemporary reviews separately from syndicated/revival-era nostalgia, online fan discourse, and rewatch evaluations. Include source date, platform, sampling basis and disagreement. No claim that a handful of Reddit comments represents the whole fandom. Fandom mood, social conventions, cult phrases and subjective humor interpretation require attributed samples and contrary examples.

**F. Canonical artifacts.** Only after A–E provide adequate witness diversity, create `derived/canonical.json`, scene/event graph, joke evidence ledger, character arc matrix, period context, contested readings, and audience typology. Every normalized statement must expose source(s), source-version, evidence locator, confidence, what was inferred, and counterevidence.

## Agent handoff and execution boundaries

- Only work under `Night Court/` and its dedicated workflow files. Read the root `AGENTS.md` first; do not touch audit logs, Shaw gateway or unrelated projects.
- Use one writer per target research branch. The two harvest workflows now have disjoint automatic branches, avoiding races discovered and corrected during the October 23 research pass.
- Preserve prior source versions, don't overwrite historic provenance without retaining the prior revision. Check idempotency and run the offline validators before merge.
- Never claim a URL is an archived transcript or a synopsis is a canonical account of the episode.
- Avoid repeated broad scrape retries when a site's access rules deny the request. Prefer multiple *independent* licensed or factual information sources and provenance-rich interpretations.
- Current-generation corpus quality matters most; retrospective compatibility with tentative early indexing is lower priority than correcting the data model when evidence warrants.

## Acceptance for the next major corpus milestone

- All 193 episodes retain valid source references, rights basis, and byte-level verification for every held artifact.
- Per-episode missing-source matrix reports each required witness type (script, subtitles, independent synopsis, reviews and production) without fabricated coverage.
- At least one alternative independently authored episode summary is held under acceptable reuse rights for a representative set.
- A manually audited sample of 10 episodes has grounded character/event/comedies/cultural tags with explicit citations and contradicted-source examples.
- Retrieval queries distinguish guest credits, synopsis references and appearance claims by relationship type.
- Validations and bounded CI pass; any blocked sources are reported candidly.

### Latest subtitle-discovery gate

An independent indexer now retains 13 individually checked Subtitle Cat links for the original series and an episode-by-episode subtitle-location count. Its live index collection was blocked by robots; avoid repeating blocked bulk scans. Continue verified episode-specific discovery through accessible search indexes and licensed providers. Apple TV and Prime Video series listings provide additional distributor/caption leads but no stored subtitle bytes.


### Historical popularity evidence now indexed

Season-level national ranks and Nielsen-era ratings, plus episode metrics with units and missingness, are indexed in `catalog/broadcast-context.json`. Future analysis should verify contemporary television industry sources and contextualize scheduling and competition. Correlations with casting or narrative changes cannot establish causal effects.


### Original-period press leads now indexed

Read `research/press-evidence-brief.md` and `research/production-and-reception-claims.jsonl` before evaluating changes in the show's comedy, casting, or reception. They include creator/producer first-person statements from September 1991 and May 1992; credit and intention should not automatically become measured screen evidence. Four disagreements in `research/source-conflicts.json` require source-critical treatment. Highest-priority factual check is season-one ratings/rank discrepancy against original Nielsen and television-industry sources, followed by careful disambiguation of May 13 story finale and May 31 final scheduled episode.


### Source revision retention: implemented

The 21 currently held Wikipedia article revisions are backed up immutably by numeric source revision ID with SHA-256 verification and separate license manifests. Future archival agents must run `tools/preserve_wiki_revisions.py` before and after article refresh, then `validate_knowledge.py`, retaining all prior snapshots rather than replacing them. Where content has no approved reuse basis, retain only provenance, independently authored notes and links.


### Full-dialogue source ingestion, implemented

The previously missing ingestion facility now accepts user-provided SRT, VTT and TXT dialogue witnesses via `tools/import_dialogue.py`, a GitHub-mobile-friendly `incoming/` staging directory, or a local/Termux command. Exact bytes are retained, hashes checked, cues/paragraphs normalized, editions kept separately and the 193-episode dialogue coverage matrix regenerated. See `DIALOGUE-INGESTION.md`, `catalog/dialogue-coverage.json`, `tools/validate_dialogue.py`.

A *claimed* full transcript is not yet a *verified* one. Actual dialogue source acquisition remains to be done, and present repository holdings contain **zero complete television transcript tracks**. Future quality gates include comparing runtimes, sampling against source video, identifying character speakers and differentiating streaming, syndication, DVD and broadcast cuts. Avoid promoting legal interpretations or rights declarations into validated source quality statements.


### Source-to-dialogue pipeline from local episode media

The supported source acquisition mechanism now includes `tools/extract_local_media.py`: inspect an authorized local media container with ffprobe, convert embedded **text** subtitle streams to SRT using ffmpeg, or explicitly opt into local offline ASR with faster-whisper. Generated tracks are versioned and attached to the original 193-episode corpus with rights and edition metadata; no video is pushed to GitHub. Image-based subtitles and CEA-608/708 streams not exposed as text remain an identified gap, along with human source/version audits and per-scene speaker assignment. See `DIALOGUE-INGESTION.md`. A real episode media source is still required to make the actual held dialogue count positive.

### Dialogue-source gap and acquisition matrix

`tools/build_dialogue_source_queue.py` produces JSON/CSV/Markdown prioritization for all 193 episodes, with evidence ranks that distinguish individually verified source pages from season index listings and inferred URL patterns. Current coverage: 26 direct-page episodes, 37 index-only and 130 without episode-specific dialogue leads; 21 original-series episodes have verified Subtitle Cat pages. The least-covered late seasons are the highest-value next search target. This work does not bypass sites, copy full dialogue or claim that an external page is an archived source. The queue must be regenerated whenever source references change.


### Alternate transcript source concordance

A bounded word-level source-witness alignment tool now compares multiple held editions of the same episode, preserving source SHA and exposing overlap, differences, likely duplicates and potential cross-episode identity collisions. Use `tools/compare_dialogue_versions.py` after every import; inspect `catalog/dialogue-variant-comparison.json` and per-episode `dialogue/variant-comparison.json` before proposing canonical dialogue. Automatic similarity is *not* enough to select a factual ground truth or attribute a joke to a performer.

Further source discovery has expanded individually checked external caption pages to 21 episodes and 22 versions, including S05E01, S07E23 and S08E06. The updated queue gives 26 direct-episode-page leads, 37 index-only, and 130 episodes still lacking a specific dialogue locator. Quarantined revival matches are recorded in `catalog/rejected-dialogue-source-matches.json`. Focus next on seasons 4–9 rather than repeatedly revisiting indexed seasons 1–3.

### Source locator coverage improved for Season 3

A verified 2025 DVD-caption upload cluster supplies episode-specific public pages for all 22 third-season episodes, now saved as URL-only provenance. The 193-row source queue has **44 direct-page episodes**, **19 index-only**, and **130 still without an episode-specific locator**. Prioritize the latter, especially original-series seasons 4–9, rather than repeatedly researching S03. A browser-visible caption display page is not a stored transcript or a reuse license.

### Later-season English caption source indexing: substantial gap reduction

The June 2025 batch yielded **105 individually episode-labeled upload-index entries across seasons 5–9**, maintained as index-only leads rather than falsely verified direct caption pages. The **current source queue is 44 direct external pages, 121 episode-labeled/index-only leads, and 28 without any specific lead**, but none is an archived full television transcript. Next target is confirming direct page links and identifying the remaining S04, S07 and S09 gaps; prioritize acquisition from independently authorized input files through the existing full SRT/VTT/TXT and local ASR pipelines.
