# Original Night Court (1984–1992): all-episode dialogue-source acquisition acceptance

**Acceptance checkpoint: October 23, 2026.** 193 of 193 canonical original-series episode folders contain one physically held English dialogue source. The 2023 revival is excluded. This is a source-preservation milestone, **not** a claim of original-NBC-cut correctness, complete or perfect dialogue, transcription accuracy, copyright clearance, speaker identification, or audiovisual verification.

## Verified source accounting

| Evidence dimension | Held count |
|---|---:|
| Original-series episodes indexed | 193 |
| Episodes with at least one stored dialogue witness | **193** |
| Episodes with timed English subtitle witnesses | **192** |
| Episodes with only untimed original-caption-page text | **1 (S09E19)** |
| Timed tracks extracted from owner-provided S01–S02 RAR archives | 35 |
| Timed SRT tracks acquired from public original-series episode pages | 157 |
| Untimed caption-page English paragraph witnesses | 1 |
| Independently verified complete against episode video | **0** |
| Missing episode dialogue sources | **0** |
| Identical long-dialogue text detected across different episode IDs | **0** |

Held-by-season: S01 **13/13**, S02 **22/22**, S03 **22/22**, S04 **22/22**, S05 **22/22**, S06 **22/22**, S07 **24/24**, S08 **24/24**, S09 **22/22**. The sole non-SRT witness is S09E19, stored as paragraph text extracted from an exact, SHA-verified original-caption-page HTML snapshot; it has no recoverable timing in that source. Its provenance and limits are in `research/s09e19-final-dialogue-acquisition.json`.

Sources of truth, rather than this prose snapshot: `catalog/dialogue-index.jsonl`, `catalog/dialogue-coverage.json`, `catalog/dialogue-quality.json`, `catalog/dialogue-source-queue.json`, `catalog/archive-status.json` and the original immutable `seasons/Sxx/SxxEyy/dialogue/versions/*/original.*`. Run `tools/reconcile_archive_status.py` after regenerating dialogue indexes and the quality/source reports.

## QA results and interpretation

The heuristic quality audit lists **56 witness tracks with flags** across its 193 witnesses, with 21 tracks flagged for overlapping source cues, 9 for adjacent exact repetition, 30 for several long gaps, and 1 untimed source flagged for separate completeness checks. These categories overlap. There are **no AV-complete episodes** yet. Automatic warnings are review assignments, not proof of corrupted subtitles: speaker overlap, sound effects, scene cuts and silent action produce legitimate gaps and overlapping captions.

Each imported track retains its raw file bytes, SHA-256, original source URL/edition when available, a version-specific manifest, normalized segments, readable text, and QA diagnostics. Do not overwrite a retained source with an alternative version. Hash and compare additional sources as separate witnesses.

## Priority after acquisition

1. **Verify source edition against actual video.** Resolve precise episode identity, runtime, intro/outro and cut differences using the verified owner FTP TVRip source, starting with a first-season pilot with known RAR-sourced captions. Record audiovisual match separately from presence.
2. **Investigate the 56 flagged sources.** Prioritize long-caption gaps, repeated adjacent lines, overlapping cue logic and missing first/last scenes. Confirm by listening/viewing, not just an arbitrary automated silence threshold.
3. **Evaluate S09E19 timed restoration.** The preserved untimed paragraph witness allows dialogue research. Align it to authorized local audio using existing ASR/alignment tools. Record derived timecodes as a new edition with source/algorithm provenance; do not change the source-page witness.
4. **Speaker turns and scene-action observations.** Use existing speaker-attribution preparation, actual frames and audio to propose grounded character identity and visible physical comedy, with confidence and time-scoped evidence. Cast metadata does not prove a performer appears in a particular scene.
5. **Finish independent full-episode AV acceptance.** Reserve `independently_video_verified_complete` for actual source-edition review. Mere SRT duration, cue count, coherent sentences, and source indexing do not prove completeness.

## Rights and evidence boundaries

The first two season archives were supplied by the owner. Other original-series online subtitles and episode-page English captions were acquired for the private research corpus; their upstream copyright and reuse permissions were **not independently determined**. This ingestion project is not a redistribution license. Do not publicize a raw transcript dump through GitHub Pages, public releases, issue comments or logs. GitHub Actions artifacts are temporary staging, not the definitive archive. The canonical private repository episode witnesses now hold the persisted bytes.

Do not return to broad source crawling just because historical roadmap text mentions “missing captions”: re-check `dialogue-coverage.json` first.
