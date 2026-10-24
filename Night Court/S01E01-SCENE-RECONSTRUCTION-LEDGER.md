# S01E01: evidence-linked scene reconstruction pilot

Status **real 30-second source-evidence packet acquired, reviewed and retained**, October 23, 2026. This is a deliberately bounded 60–90s excerpt, not a complete episode and not a transcript accuracy certificate.

## Accepted first source-grounded scene evidence (owner-controlled run #40044673687)

Merged [PR #112](https://github.com/gamesbyian/general-purpose/pull/112) installed the fixed SHA-verified 60–90 second capture; an inert [PR #114](https://github.com/gamesbyian/general-purpose/pull/114) triggered it with trusted main code and was closed after the successful run. [PR #115](https://github.com/gamesbyian/general-purpose/pull/115) permanently imported the resulting actual JPEGs, nine original caption cues C19–C27 and five source-mix acoustic windows. CI validated individual JPEG digests and matching original AVI/SRT digests.

Saved episode location: [S01E01 derived scene-review-v1](seasons/S01/S01E01/derived/scene-review-v1/). Read `visual-observations.json` for evidence-linked image observations and `scene-script-review.md` for a limited screenplay-style setting and comic-context draft. Observable details include law-book shelving, wood trim, a desk and landline, papers, a person in lavender formal clothing, a uniformed officer, and the officer holding a telephone receiver in the sampled frame at 87s. Actual individual character identity, spoken-line alignment, the moment the phone was lifted and the intervening movement are **not** established.

We have now achieved **first reviewed static-frame setting and prop annotations from actual source media**. The stronger goal of audiovisual stage directions and spoken performance annotation is still not accepted. The separate [S01E01 ASR/prosody phase](S01E01-ASR-PROSODY-PILOT.md) is to supply candidate caption/audio anchors, not automatic truth.

## Media and subtitle provenance

- FTP candidate: one exact S01E01 AVI from the 193/193 reconciled inventory, 183,386,112 bytes. The *same bytes* as previously processed in [run #40042590948](https://github.com/gamesbyian/general-purpose/actions/runs/40042590948) are required, with SHA-256 `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`.
- Caption source: the immutable owner's S01 DVD English SRT, SHA-256 `aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496`.
- Selection: source-video seconds 60–90, ten 480px JPEG stills at 60,63,...87s, five six-second mixed-audio intervals and all overlapping original SRT cues, with complete SHA checks.
- **Not proven yet:** caption/video cut synchronization, source identity by content, speaker names, vocal tone, continuous gesture/movement, laugh causality, scene boundaries or audiovisual completeness.

## Execution architecture

`tools/build_s01e01_scene_evidence.py` reads a locally present AVI, validates its source fingerprint, extracts ten small individual JPEGs and 30 seconds of temporary PCM with FFmpeg, computes mix-level RMS/peak/activity measurements for fixed six-second windows, and writes an evidence JSON and a candidate subtitle passage Markdown. It deletes temporary WAV and does not export source audio or source video. It refuses edits to the original subtitles.

`tools/pilot_ftp_s01e01_scene.py` enforces the single fixed remote path/size, downloads to temporary private runner storage with SHA verification, and runs the above processor. The dedicated `.github/workflows/night-court-trusted-s01e01-scene-review.yml` is designed to be invoked using an inert PR marker. It uses `pull_request_target` with exact owner/branch/base guards but executes **only main's trusted source revision**. It does not check out contributor PR code. Artifacts remain private and expire after seven days; durable reviewed JSON and editorial reports belong back in the private repository.

## Visual and vocal review standards

- A **sampled still** may establish visible wardrobe, position and props in that single frame. It cannot prove what anyone did before/after. Stage directions about entrances, prop actions, gestures and visual comedy require subsequent short video or multiple time-consistent reviewed observations.
- A **mix RMS** is not dialogue loudness. The television mix contains laughter, music, effects and multiple voices; no emotion, sarcasm, vocal identity, true voice pitch or speaker turn may be inferred from the five six-second activity measurements alone.
- Original caption cues must be separately authenticated against audio. Their nominal SRT time markers remain `not_audio_verified` until content/word comparison or manual review. Distinguish dialogue utterance, speaker hypothesis, scene setting, acoustic cue and observed visual action.
- No broad 193-video factory until a real source-edition alignment, facial/voice tracking and scene-action sample pass acceptance.

## Acceptance ledger

| Gate | Status |
|---|---|
| 193 source video candidates matched by filename | Confirmed in PR #88 |
| S01E01 source hash from real FTP AVI | Confirmed run #40042590948 |
| 30-second exact source read with 10 JPEG hashes and 5 acoustic windows | **Completed, GHA #40044673687 and merged PR #115** |
| Relevant source subtitle cues preserved by ID/source hash | **Completed, nine original SRT cues C19–C27, PR #115** |
| Caption/video speech offset verified independently | **Local audio-caption content corroborated by 10 ASR segments in run #40045128799; exact word alignment, drift and independent verification remain open** |
| Observed appearance and set objects recorded from source frames | **Completed, ten frames, SHA-verified; visual character IDs unresolved** |
| Continuous motion and meaningful stage directions grounded in reviewed clip | Not yet |
| Final first scene screenplay accepted | Not yet |
| Full episode audiovisual completeness certified | Not yet |

## Next stages

First, inspect the emitted frame evidence and cue list; annotate **only genuinely visible facts**. Secondly, use local ASR and/or human listening to validate the SRT-to-video map and candidate speakers before promoting captions to screen dialogue. Third, inspect short video windows around actions before writing stage directions about movement. Add evidence-linked, reviewable script blocks and an explicit uncertainty ledger. Keep the pilot inside the original series.
