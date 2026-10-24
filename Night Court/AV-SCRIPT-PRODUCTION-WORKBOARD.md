# Nine-season evidence-linked screenplay production workboard

## Editorial acceptance pilot: S01E01

The `S01E01-EDITORIAL-REVIEW-HANDOFF.md` lane adds an explicit source-linked acceptance packet for the first 60–90s original-video passage. It joins source SRT turns/55 words, two acoustic timing proposals, unseparated mix-level pitch reports and six SHA-backed sampled-motion observations. The packet will rank every source voice turn and each motion review task with missing-evidence flags, but **every speaker, dialogue, vocal-expression, exact word time and stage-action acceptance gate remains unverified**. This provides a bounded editorial workflow beyond the first rendered script while the separate sparse source-cut drift test is being developed. Results are generated through an offline PR workflow and must not be conflated with a new video review.


Every original *Night Court* episode now has a source-only reading script, neutral source-cue turn data, speaker-attribution work packets, provisional caption-gap scene participation notes, and a candidate local-video filename. These five inventories need to stay **one-to-one by episode/source hash** before richer audio-visual processing scales.

`tools/build_av_script_production_queue.py` performs that reconciliation, joining all **193** original-series entries from:
- `catalog/source-script-scaffold-coverage.json` (70,804 cues, 72,733 subtitle-derived reading units)
- `catalog/dialogue-qa-review-queue.json` (quality flags)
- `catalog/speaker-attribution-preparation.json` (72,823 source turn units and 1,804 agent packets, no accepted identities)
- `catalog/scene-participation-evidence.json` (508 caption-gap source scene candidates, not actual screen cuts)
- `catalog/ftp-video-inventory-2026-10-23.json` (193 filename-size video candidates, not independently identified audiovisual content)

Its output, `catalog/av-script-reconstruction-queue.json`, is the shared future agent workboard. Every episode includes exact source SHA, episode-local source-reading script, candidate roster/turn packet location, provisional participant evidence, known quality warnings and all as-yet-unmet AV gates. **S01E01 remains the active, partially measured pilot**, not a full production-accepted episode. All others are source-prepared and awaiting cut-by-cut media QA. S09E19 needs an entirely new original-source audio time map because its retained text is untimed. The ordering follows *existing* caption QA priority and keeps S01E01 first; it does not estimate actual episode accuracy.

The live pilot S01E01 source-cut drift worker tests a sparse five-window sampling plan before making any claims about a synchronized source edition. Those results belong in `source-sync-review-v1` after an independent, checksum-gated import, not embedded as fabricated timestamps in the 193 source reading editions.

After AV validation, each separate reviewed script version should be generated with evidence pointers rather than editing the source-only scaffold. A scene may only be declared complete after independent checks for dropped dialog, participants, physical gags, sound cues and timing. Do not assign named voices from cast credits, caption vocatives, or still-image appearance.

The [Night Court master AV script factory plan](AV-SCRIPT-FACTORY-PLAN.md) remains normative for these quality gates. No mass episode media scan, upload, content redistribution or credential transfer is authorized by this offline workboard.
