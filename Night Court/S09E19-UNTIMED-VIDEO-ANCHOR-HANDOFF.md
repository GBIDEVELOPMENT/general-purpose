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

## Independent acceptance ledger

| Requirement | Current state |
|---|---|
| Original S09E19 owner-specific 347 untimed paragraphs and immutable source SHA | Held and indexed |
| Exact FTP S09E19 AVI candidate (filename/size only) | Inventoried; AV content not verified |
| Original AVI bytes SHA, actual runtime and audio stream | Pending real run |
| Five 25-second source-video audio excerpts | Pending real run |
| Independent ASR vs all original untimed paragraphs | Pending real run |
| Human-confirmed utterance-to-paragraph time alignment | Not done |
| Full episode subtitle timestamp reconstruction | Not done |
| Character speaker identities and scene/action/inflection analysis | Not done |
| Original dialogue or episode AV completeness certified | Not done |
