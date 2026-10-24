# S01E01 exploratory speech and prosody alignment

Date: 2026-10-23. Status: **implementation awaiting synthetic/PR verification; real source run not yet dispatched**.

This phase follows the successfully acquired original-source 60–90 second scene packet ([run #40044673687](https://github.com/gamesbyian/general-purpose/actions/runs/40044673687)). Real source frames, caption cue IDs and mix-level acoustic measurements are retained in `seasons/S01/S01E01/derived/scene-review-v1`.

## Purpose

Compare the source video's soundtrack against its separately imported first-season DVD SRT before promoting any line to a fully time-aligned screenplay. Use independent ASR as a *check*, not as truth. Derive pitch/eGeMAPS features directly from 30s of temporary source audio, while noting that a television mix with other voices, laughter, music and effects cannot establish isolated performer prosody.

## Reproducible algorithm

- Existing FTP source remains exactly S01E01 with SHA-256 `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`.
- Existing source SRT SHA-256 `aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496`.
- At source video 60–90s, extract one temporary 16kHz mono WAV.
- Locally install CPU `faster-whisper`; explicitly download only the public `tiny.en` model to a temporary model cache. No model weights are retained or committed. Decode word-timestamped ASR segments with language='en', beam=3 and no silence-filter shortcut.
- Compare normalized word strings against all intersecting original SRT cues C19–C27 using an explicitly low-authority SequenceMatcher heuristic. A match above 0.3 receives a **candidate** cue ID, and only matches above 0.55 receive a coarse start-offset hypothesis. Cue/ASR segmentation differences, distinctive word misrecognition and television soundtracks can defeat this method.
- Extract five six-second F0 YIN contours and openSMILE eGeMAPSv02 summaries from the mixed soundtrack. This does not certify voice quality, emotion, speaker or sound-source attribution.
- Emit one text-only JSON with source/audio hashes, actual ASR hypotheses and word starts/ends, cue references, offset hypotheses and anonymous acoustic measurements. No raw source media, WAV, model weights or credentials in the artifact.

## Security and execution

`.github/workflows/night-court-trusted-s01e01-asr-prosody.yml` executes **only trusted main-branch code** and is triggered solely by an inert same-owner PR from `research/night-court-s01e01-asr-trigger`. Source is fixed to S01E01 and a single <=30s excerpt. The repository's existing FTP secret remains in the protected Actions job and must never be printed or supplied to a PR checkout. A separate no-secret PR offline job tests the heuristic and compilation.

## Acceptance thresholds

- Source SHA, SRT SHA and source-window checks must pass before any inference runs.
- Successful ASR or acoustic extraction is **not** an audiovisual-completeness certificate.
- All ASR text remains alternative reading; no source caption is overwritten, speaker names remain unknown, and proposed character-performance directions remain unreviewed.
- At least two distinct substantive dialogue matches and a manually checked word/audio timing relationship will be needed before calling the 60–90s passage speech-aligned.
- Human/video review of motion remains necessary for actual physical stage directions.

After a successful real run, inspect candidate offsets and errors, merge a source-linked result artifact, update the scene script and the visual/audio acceptance ledger, and select a longer episode span only if the quality warrants it.
