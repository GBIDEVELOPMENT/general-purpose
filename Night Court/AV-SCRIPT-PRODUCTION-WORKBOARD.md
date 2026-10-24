# Nine-season evidence-linked screenplay production workboard

## Second original-series integrated audiovisual script excerpt: S09E19

[S09E19-INTEGRATED-SCENE-V1-HANDOFF.md](S09E19-INTEGRATED-SCENE-V1-HANDOFF.md) joins five high-lexical but still unverified original-untimed paragraph candidates to six frame-hashed video observations in the 15:00–15:25 source window. The output is an evidence-linked script excerpt and machine-readable research map, separate from the immutable untimed 347-paragraph original witness. It is **not** a source-timed SRT, confirmed speaker attribution, performance interpretation, complete scene or episode completeness verification. The renderer undergoes offline CI and must not confuse visually adjacent actors with any proposed spoken line.


## S09E19 real scene/physical-action video evidence pilot

The [S09E19-VISUAL-SCENE-HANDOFF.md](S09E19-VISUAL-SCENE-HANDOFF.md) adds a **strictly bounded 15:00–15:25, 100-frame 4fps** source-image worker for the accepted AVI SHA and the window with five independent ASR-to-untimed-paragraph candidate matches. Unlike the source text scaffolds, this gathers actual original-series video evidence for future setting and stage-action review. **The frames are not visually reviewed merely by extracting them**, and no speaker, performance, stage directions, timing or episode completeness is promoted automatically. A separate SHA-verified image import/review stage remains necessary.


## Highest-priority remaining untimed source: S09E19

[S09E19-UNTIMED-VIDEO-ANCHOR-HANDOFF.md](S09E19-UNTIMED-VIDEO-ANCHOR-HANDOFF.md) defines a separately owned, five-window original-video ASR experiment for the single 347-paragraph untimed dialogue witness. The actual 183,377,920-byte AVI is now SHA-fingerprinted from trusted [run #40054051699](https://github.com/gamesbyian/general-purpose/actions/runs/40054051699) (22m 0.144s) and its **125 seconds of sampled audio** produced 50 ASR segments and 15 distinctive candidate matches to retained paragraph IDs (roughly source paragraphs 49–331). No original source timestamps were invented and **1195 seconds of this cut remain unsampled**. The compact result is being stored separately under S09E19 derived source-timing evidence. Lexical matches are merely proposed source anchors, not invented SRT cue timecodes or evidence of speaker identity. This lane must not interfere with S01E01 voice/review work or the 193 reading-script scaffolds.


## Anonymous S01E01 voice similarity lane

The owner-only [ECAPA voice experiment #40052520049](https://github.com/gamesbyian/general-purpose/actions/runs/40052520049) succeeded and [PR #205](https://github.com/gamesbyian/general-purpose/pull/205) retained [21 pairwise anonymous similarity measurements](seasons/S01/S01E01/derived/scene-review-v3/anonymous-voice-similarity.md) for seven sufficiently long proposed 60–90s spoken spans; three short candidate turns abstained. This is **not diarization, voice identification or character attribution**. Source extraction was isolated from third-party model execution at the credential boundary; no raw embeddings, voiceprints, AVI/audio or model weights were retained. Prioritize these pairs for original-source listening and actual mouth/voice corroboration before promoting any speaker claims. See [anonymous voice handoff](S01E01-ANONYMOUS-VOICE-HANDOFF.md).

## Editorial acceptance pilot: S01E01

The `S01E01-EDITORIAL-REVIEW-HANDOFF.md` lane adds an explicit source-linked acceptance packet for the first 60–90s original-video passage. It joins source SRT turns/55 words, two acoustic timing proposals, unseparated mix-level pitch reports and six SHA-backed sampled-motion observations. The packet **passed CI and merged in [PR #191](https://github.com/gamesbyian/general-purpose/pull/191)**. Its [worklist](seasons/S01/S01E01/derived/editorial-review-v1/acceptance-worklist.md) ranks eleven source-voice tasks and six visual-action checks by missing/contradictory evidence. [PR #197](https://github.com/gamesbyian/general-purpose/pull/197) added adversarial tests and a zero-acceptance reviewer decision schema, so **every speaker, dialogue, vocal-expression, word-time and physical stage-action gate is still unverified**. This provides a bounded editorial workflow beyond the first rendered script while the source-cut drift samples undergo separate quality review. [PR #194](https://github.com/gamesbyian/general-purpose/pull/194) preserved all five real-source ASR windows, rejected duplicated/hallucinated model anchors and correctly declined to infer global subtitle drift. The two offline PR workflows passed. These are evidence-reconciliation and decision-gating results, **not another listener/video confirmation**.


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
