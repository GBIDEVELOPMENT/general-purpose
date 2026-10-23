# Frame-grounded scene descriptions and caption-to-script reconstruction

**Status (2026-10-23): design/acceptance contract, not an executed video interpretation.** Original 1984–1992 series only. Pairs with the audio-first, sparse-video script-factory design in PR #67. No video source, inferred speaker or visual description should be represented as independently verified merely because a model produced it.

## Reconciled baseline

- 193 canonical episode records; 35 physically retained English SRT witnesses, covering S01E01–S02E22, from two archived owner-supplied RARs (see `catalog/rar-ingestion-manifest.json` and `catalog/dialogue-coverage.json`).
- 158 episodes have no locally held dialogue; zero of 193 are audiovisually verified dialogue-complete.
- The Season 3 research pass mapped 22 externally hosted caption-display pages; links are source leads, **not** stored captions.
- The source queue currently classifies 35 as held-needs-QA, 53 as direct external episode pages but no held dialogue, 102 as index-only and 3 without episode-specific dialogue locators.
- An authenticated read-only FTP inventory identified `/downloads/Night Court TVRip S1-S9`. Video-file identity and completeness still require per-file validation; do not mistake an FTP filename for independent proof of the original-series episode or release.

## Desired output: one **editable, evidence-linked, screen-accurate research script** per cut

Combine separately retained layers, never silently overwrite them:

1. **Caption witness**: every original cue, source byte hash, source time, release/cut, original caption casing and stage directions. Normalize into utterance candidates; preserve caption segmentation as a second representation.
2. **Audio-derived witness**: optional local ASR with model/revision/language, diarization, alignment, voice or sound evidence, unresolved words, confidence and source-media hash. Preserve differences against captions rather than automatically letting ASR rewrite caption text.
3. **Video-derived visual observation**: characters visibly present where identifiable, entrances and exits, wardrobe/appearance details, posture, expressions, gestures, props, staging, important camera cuts and silent physical jokes. Report what the examined frames actually show; never fabricate intermediate movement from sparse snapshots.
4. **Reconstructed screenplay presentation**: scene headings, dialogue turns, action beats and text-form audio-description track, each pointing to the underlying timed evidence. Speaker names and scene boundaries carry confidence and an explicit `unresolved` option.
5. **Reviewed interpretation**: separately attributed comic mechanism, narrative consequence, affect, allusion and character-arc tags. Machine-suggested values remain hypotheses.

The frame-derived track should read like descriptive audio **written as text**, not as a narrated audio output. Its job is to convey visually meaningful things lost in the caption-only representation. Prioritize silent comedy and character reactions over describing every camera frame. A costume, expression or action must be observable in a frame or bounded reviewed clip; never infer it from the words of a caption.

## Episode pipeline

1. **Inventory and fingerprint** the selected media without committing large video to Git: exact FTP path/size (private), SHA-256 once read, ffprobe streams, duration, frame rate, audio channels, resolution, edition guess, safety/rights and original-series identity verification. Keep any private host/path redacted from public outputs.
2. **Extract once near the storage source**: bounded lossless mono audio for ASR (e.g. 16 kHz FLAC), sparse representative frames (~0.5–1 fps) plus shot-change frames, and short targeted higher-rate bursts around movement/expressive ambiguity. These rates are sampling defaults, not claims of coverage. Avoid extracting all 193 episodes upfront without storage and runtime budgets.
3. **Align captions to audio**, using a per-edition offset/drift model and anchor confidence; handle opening/closing credits, recaps, advertisements, edit gaps, near-identical repeated lines and multipart numbering. Store a piecewise time map whenever cut offsets change.
4. **Build candidate conversational turns**: caption text + audio alignment + text-only speaker roster and local visual evidence. Use `speaker_id: null` unless voice/onscreen/mouth-movement evidence or human review supports an assignment; an actor credit alone is not proof of utterance.
5. **Segment into candidate scenes** from video cuts, audio continuity, location clues and conversational boundaries. Give every scene a start/end and uncertain-boundary flags. A hard camera cut is not automatically a scene change.
6. **Observe visual action**. Generate image-grounded descriptions from source frames with timecodes and optionally a reviewed short clip for a gesture. Distinguish `visible` / `likely` / `uncertain` / `not_observable`. A single frame cannot prove a motion trajectory or that a character remains continuously present.
7. **Fuse cautiously**. Compose script turns and action interleaved by source time, using the audiovisual mapping for the chosen cut. Store links to caption cue IDs, audio interval IDs and frame observations. Allow explicit competing readings.
8. **Review and export** in scene order, plus time-coded descriptive-text track (JSONL, readable Markdown, optional WebVTT annotations) and a private visual QA atlas. No synthetic footage or audio is required.

## Proposed record contract (`derived/visual-observations.jsonl`)

One observation per visible moment or reviewed bounded interval:

```json
{
  "schema_version": 1,
  "episode_id": "S01E01",
  "media_version_id": "verified-release-id",
  "media_sha256": "<sha256-of-original-media>",
  "observation_id": "S01E01:V0001",
  "start_ms": 120000,
  "end_ms": 121000,
  "observation_mode": "single_frame",
  "frame_evidence": [{"frame_id": "f-120000", "source_time_ms": 120000, "sha256": "<frame-hash>"}],
  "visible_entities": [{"character_id": null, "appearance": "unidentified adult in dark jacket", "identification_status": "unresolved"}],
  "wardrobe": ["dark jacket"],
  "expression": null,
  "gesture_or_action": null,
  "setting_props": [],
  "description": "An unidentified person wearing a dark jacket stands near the courtroom doorway.",
  "evidence_status": "machine_observation_unreviewed",
  "confidence": "medium",
  "reviewed_by": null,
  "contradictions": []
}
```

This is a **synthetic schema illustration**, not a description of a real Night Court frame. For a reviewed clip, `observation_mode` may be `bounded_clip`, with the exact interval and evidence frames; for individual frames, movement statements require separate evidence. Speaker turns should link to observation IDs where appropriate, never copy visual guesses into the authenticated caption layer.

## Description editorial policy

- Describe wardrobe, posture, facial expressions, blocking, hand gestures, prop interactions, meaningful silent responses, visible entrances and exits, and physical-comedy setup/payoff.
- Avoid routine cinematographic narration unless framing affects understanding of a joke, reveal or interaction. Concise present tense; specific observable details rather than subjective adjectives.
- Avoid guessing motivation or internal emotion from facial expression. “Frowns and looks away” is observation; “feels ashamed” is interpretation.
- Do not guess protected personal attributes, diagnosis or offscreen relationships from appearance. Character identity, if claimed, requires an evidence source and disambiguation.
- Record continuity across shots only where verified. An event between sampled frames is unknown until a clip is checked.
- All output records must carry rights/provenance, model version, input hashes, timestamps, confidence, review state and reproducible generation parameters.

## QA gates and execution priority

**Pilot acceptance: S01E01**. Confirm episode/release match, SRT offset, every caption import checksum, visual frame timestamps, no invented lines, explicit unknown speakers, and at least one manually checked silent action with image evidence. Review all proposed entrances/exits, identity assertions and impactful comedy beats. Compare a generated script against the video from start to finish with gap ledger entries for undecodable lines and unsampled motion.

Quantify separately: captions held, ASR produced, alignment verified, turns assigned, frames sampled, reviewed visual observations, scenes reviewed, visual-action recall on reviewed spans, falsely attributed speakers, and genuinely AV-verified complete episodes. Never use a model confidence score alone as a completeness certificate.

**Then S01E02–S02E22**: reuse held captions for constrained ASR and frame-driven scene/action notes. **Then S03–S09**: prioritize verified local video inventory and audio-first ASR where captions are absent; source-lead pages alone cannot populate script dialogue.

### Blockers

The current GitHub connection can inspect text records and workflows but cannot itself view or decode FTP-hosted video. The README/FTP documentation reports a confirmed authenticated video root, not footage imported into the repository. Until a dedicated permitted workflow extracts and makes audio and sampled frames available to an actual transcription/vision worker, no audiovisual visual descriptions, timings, cast identification or completeness claims can be verified.

## Practical handoff

Read `README.md`, `DIALOGUE-INGESTION.md`, `RESEARCH-ROADMAP.md`, `KNOWLEDGE-MODEL.md`, `FTP-ACCESS.md`, `catalog/rar-ingestion-manifest.json`, `catalog/dialogue-coverage.json`, `catalog/dialogue-quality.json`, and `catalog/dialogue-source-queue.json` first. Reconcile PR #67's audio-first approach and the existing caption-turn/speaker-attribution implementation before adding any production frame-extraction code. Use bounded synthetic media tests, prefer metadata-only discovery until a worker/storage destination and source identity are confirmed, and do not collide with existing Night Court ingest workflows.
