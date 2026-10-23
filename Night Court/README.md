# Night Court: the original NBC series (1984–1992)

**Independent research archive**, inside the private `gamesbyian/general-purpose` repository. Scope excludes the 2023 revival. The purpose is durable, provenance-aware research and a future LLM-readable knowledge base about the original program, its fictional and production history, comedic conventions, cultural moment, and fandom.

## Actually held (23 October 2026)

- **193/193** original-series episode records: `seasons/Sxx/SxxEyy/episode.json`, spanning 9 seasons (13, 22, 22, 22, 22, 22, 24, 24, 22).
- **193/193** titles, dates, directors, writer-credit lines and production codes, reconciled from TVmaze and Wikipedia. Source-specific aliases are retained; composite broadcasts and ambiguous numbering are flagged.
- **193/193 CC BY-SA-licensed, episode-specific encyclopedia synopsis/capsule files**: `seasons/Sxx/SxxEyy/authorized-text/wikipedia-episode-capsule.wikitext`, each with `sources/wikipedia-capsule.provenance.json`. A five-entry discrepancy between Wikipedia's 188 episode-list rows and 193 actual episode parts is explained by paired broadcasts, whose shared summaries are annotated.
- Full MediaWiki source of **two openly licensed articles**, `research/licensed-wiki/Night-Court.wikitext` and `research/licensed-wiki/List-of-Night-Court-episodes.wikitext`, each with a Wikipedia revision permalink, attribution and license manifest.
- **1,651 provenance-bearing episode source references**, including many repeated series-index pointers. The number is *not* an independently recovered document count.
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

The workflow and analysis are work-in-progress. No scene-complete transcript corpus or canonical knowledge matrices have been produced yet.
