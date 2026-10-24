# S09E19: original untimed source-to-video anchor pilot

Status: bounded acquisition/independent-speech matching implementation, October 23, 2026. Original series only. This is an evidence-gathering experiment, **not** an audiovisual completeness certificate, dialogue rewrite, source timecoded SRT, or verified stage/performance script.

## Reason to prioritize S09E19

Of the 193 original-series episodes, S09E19, *P.S. Do I Know You?*, is the **only** held dialogue witness without source caption timestamps. The original Subtitle Cat HTML-derived text is preserved as 347 untimed paragraphs, SHA-256 `659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2`; there is no independently verified complete S09E19 dialogue or authenticated source audio. Its counterpart AVI appears in the owner FTP inventory only by **filename and byte size**:
`/downloads/Night Court TVRip S1-S9/Night.Court.S09.DVDRip.DivX/Night Court - 9x19 - P.S. Do I Know You.avi`, 183,377,920 bytes.

## Fixed five-window research protocol

This pilot accesses **only that exact inventory item**. It acquires its SHA-256 and FFprobe duration/streams, then transiently extracts five 25-second mono audio samples at source seconds **180–205, 405–430, 660–685, 900–925, and 1200–1225**. The exact source AVI is deleted after extraction. The credentialed acquisition process ends before the faster-whisper tiny.en speech model is installed and run; the later analysis step has **no FTP_PASSWORD**. The final GitHub Actions artifact contains **JSON only**, not audio/video/model weights.

`tools/match_s09e19_untimed_paragraphs.py` compares each speech-model segment against every 1–3 paragraph contiguous stretch among all 347 original text paragraphs. Only >=5-word proposed ASR phrases with high lexical similarity and a substantial margin over nonoverlapping alternatives can receive a **tentative source-paragraph locator**. Too-short, ambiguous, hallucinated, noisy or clipped ASR spans abstain. The source paragraph's `start_ms`/`end_ms` values **stay null**, even with a plausible candidate. An episode-wide time map is *not* deduced from five samples or forced from transcript order.

## Implementation, CI and security gates

The read-only source selection, checksum checks, source timestamp-null checks and synthetic ambiguous/duplicate paragraph fixtures are tested in `.github/workflows/night-court-s09e19-source-anchor-offline.yml`. After its acceptance and merge, an inert owner-authored PR at branch `research/night-court-s09e19-untimed-anchor-trigger`, touching only `Night Court/research/trigger-s09e19-untimed-anchors.txt`, activates `.github/workflows/night-court-trusted-s09e19-untimed-anchor.yml`. The trusted `pull_request_target` job checks out **`github.sha` on main**, not attacker-editable PR code; its exact owner, same-repository, branch and base guards are mandatory.

The next task after a successful real run is to preflight the compact JSON artifact against the held 347-paragraph SHA and discovered AVI fingerprint, retain it under `seasons/S09/S09E19/derived/source-timing-review-v1/`, and create a prioritized listening/word-alignment queue. Any transcript paragraph promoted to timing requires **actual audio review**, preferably across multiple anchored passages with speaker overlap checks. Until then its original text remains untimed. Failure to match is useful evidence and must not trigger automatic replacement of the original source.

## Real source acquisition success and first independent content correspondence

Owner-triggered [PR #218](https://github.com/gamesbyian/general-purpose/pull/218) launched trusted [run #40054051699](https://github.com/gamesbyian/general-purpose/actions/runs/40054051699), which **completed successfully**, from the reviewed [PR #217](https://github.com/gamesbyian/general-purpose/pull/217) toolchain. Actual S09E19 AVI is 183,377,920 bytes, MPEG-4/MP3 media with actual runtime **1320.144 seconds (22m 0.144s)**, SHA-256 `51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649`. The original AVI and five WAV excerpts were removed after processing; only source-hashed JSON artifact **#12544941126** was retained for in-repo import.

The independent speech model produced **50 ASR segments** across five 25-second excerpts, and the conservative whole-document paragraph matcher found **15 distinctive high-lexical-match candidates** (3, 2, 1, 5, 4 by source window). Proposed paragraph IDs progress in source order: **49–54**, **117–120**, **190**, **240–253** and **324–331**, respectively. Some have similarity 1.0 after normalization; others are below 1.0 but above the explicit threshold with a distinct alternative margin. All source paragraph timing fields remain **null**. The matching is preliminary evidence of episode content/cut compatibility, **not independently audited audio, a full source-to-video time map, speaker identity, verified screen action or a complete screenplay**.

A strict importer `tools/import_s09e19_source_anchors.py` re-evaluates every one of these candidate matches against the 347 original source paragraphs and rejects any altered AVI/text fingerprints, audio bounds, source-timecode invention, unverifiable speaker claims or mismatched candidate counts. Its CI preserves only the compact derived JSON and an episode-local review report. The five audio sample windows total **125 seconds**, so **1195 seconds of this video cut have not been sampled by this experiment**.

## Independent acceptance ledger

| Requirement | Current state |
|---|---|
| Original S09E19 owner-specific 347 untimed paragraphs and immutable source SHA | Held and indexed |
| Exact FTP S09E19 AVI candidate (filename/size only) | Inventoried; AV content not verified |
| Original AVI bytes SHA, actual runtime and audio stream | **Confirmed by run #40054051699, source SHA pinned** |
| Five 25-second source-video audio excerpts | **Completed, 125 seconds processed, AVI/WAV deleted** |
| Independent ASR vs all original untimed paragraphs | **50 segments, 15 unique high-lexical proposed anchors, pending listener acceptance** |
| Human-confirmed utterance-to-paragraph time alignment | Not done |
| Full episode subtitle timestamp reconstruction | Not done |
| Character speaker identities and scene/action/inflection analysis | Not done |
| Original dialogue or episode AV completeness certified | Not done |
