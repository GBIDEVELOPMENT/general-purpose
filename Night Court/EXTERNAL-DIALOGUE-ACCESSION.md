# External dialogue lead accession: 23 October 2026

## Purpose

Convert actual third-party dialogue leads into source-preserved, versioned local assets **where access and retention are permitted**, minimizing future audio transcription. The authoritative machine-readable worklist is `catalog/dialogue-accession-register.json`, generated from the current 193-episode source queue. It records 229 non-inferred episode-level links (57 Forever Dreaming references and 172 Subtitle Cat references, including index-only leads). These are **links, not 229 distinct held documents**, and links sometimes repeat or cover overlapping content.

## Verified live spot checks

- S03E01: [Springfield! Springfield!](https://www.springfieldspringfield.co.uk/view_episode_scripts.php?episode=s03e01&tv-show=night-court-1984) presents readable script-like dialogue for the **original 1984 series**, with visible OCR-like defects. The current queue's automatically inferred Springfield episode URL is not treated as a validated held file.
- S03E01: [Subtitle Cat](https://www.subtitlecat.com/subs/1081/Night%20Court%20(1984)%20-%20S03E01%20-%20Hello%2C%20Goodbye%20(480p%20DVD%20x265%20Panda).eng.html) displays an English SRT download link and subtitle content. Accessibility of a download link does **not** establish a reuse license; historical site robots denials for bulk indexing are recorded elsewhere in the archive.
- S01E01: [Forever Dreaming](https://transcripts.foreverdreaming.org/viewtopic.php?t=82333) shows substantial readable dialogue, but S01E01 already has a retained English SRT. Any alternative transcript would be a new independent version, not a replacement of the existing witness.

These are **verified content-bearing pages**, not newly saved dialogue bytes. No inaccessible site or account protection should be bypassed. The public site copyright holder is not necessarily the person who uploaded a subtitle.

## Processing order

1. Focus on the **158 original-series episodes without retained dialogue**. Start with the 53 direct-page episodes, especially S03 and S04, before duplicating S01/S02.
2. For each lead, verify source identity (1984 show, exact episode, title/part, release); public access; downloadable/raw format; encoding; integrity; licensing/research-retention basis and website access rules. Record each assessment in an append-only evidence ledger.
3. Where full source preservation is allowed, download an exact, bounded file into `incoming/` or a dedicated staging area with original filename, URL and retrieval date, preserve the bytes and SHA-256, import through existing `tools/import_dialogue.py`/`import_dialogue_bundle.py` rather than adding another normalized database.
4. Regenerate `dialogue-coverage`, `dialogue-index`, `dialogue-quality`, `dialogue-variant-comparison`, `holdings-coverage`, `dialogue-source-queue` and `archive-status`. Confirm the queue changes from `direct_episode_page_found_not_held` to `held_dialogue_needs_quality_review` only when bytes physically exist and the manifest validator passes.
5. For source pages without demonstrably permitted retention, keep locator, independently written short descriptive metadata, accessibility result and the exact blocker. Do not secretly treat a pointer as a transcript. Use a separately sourced video/audio extraction or rights-cleared supplied file instead.
6. Detect identical source SHA-256 across mirrors/releases. If byte-different, perform normalized text comparison and edition mapping before classifying it as a new dialogue witness. Do not inflate coverage with duplicate mirrors.

## Accession status vocabulary

- `external_pointer_only`: URL on record, no dialogue bytes held.
- `access_verified`: original-series page currently displays text/caption, but no bytes saved.
- `rights_review_needed`: copying basis has not been determined.
- `retrieved_staging`: bounded bytes acquired and hashed, awaiting episode/format checks.
- `held_validated`: original bytes in immutable episode version and index/quality reports agree.
- `reviewed_against_video`: manually compared to the associated media edition, including truncation checks.
- `blocked_robots`, `blocked_access`, `blocked_rights`, `invalid_episode`, `duplicate_source`, `unavailable`: explicit disposition rather than silently removing the lead.

Do not equate SRT timestamps with completeness. The first two seasons already contain 35 English SRT tracks; S01E11 has an adjacent-repeat diagnostic to review. Speaker attribution and descriptive visual observations remain independent stages.

## Handoff and constraints

The GitHub connector reads and writes repository text, but it does not turn a web page into a downloadable GitHub artifact automatically. The register is a machine-readable accession queue, **not** an assertion that all 229 leads have been fetched. Fully mirroring non-user-supplied, unlicensed third-party scripts indiscriminately is not justified solely by being a private repository. Assess source access and permitted retention; for owner-provided files preserve the owner's source declaration and do not recopy the S01/S02 RARs.

Next highest-value engineering work: a restricted manual acquisition worker that takes a single verified original-series URL, retrieves only where allowed, SHA-hashes bytes, records rights provenance, imports into existing pipeline, updates reports, and fails closed on ambiguous mapping. Do not build an unattended third-party site crawler or replay earlier refused robot-index requests.
