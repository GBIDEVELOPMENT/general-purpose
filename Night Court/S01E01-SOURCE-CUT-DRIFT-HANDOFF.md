# S01E01 source-video cut drift audit: sparse independent samples

Status: original source sampling tooling merged, original trusted run #40049788603 identified a Whisper segment extending beyond the decoded 30-second window. Follow-up fix clamps such model proposals while excluding them from drift review, and deliberately drops fully invalid segments. Real sparse drift results remain unaccepted until a fixed trusted workflow passes. October 23, 2026.

The 01:00–01:30 S01E01 pilot now has two word timing models but they both focus on the **same 30 seconds**. Before trusting their cues for a full episode, check the original AVI against the held SRT at several locations spanning the 1448.256-second source cut.

## Five immutable sampling windows

| Window in original AVI | Existing original SRT cue range |
|---|---|
| 05:00–05:30 | C74–C77 |
| 10:00–10:30 | C152–C158 |
| 15:00–15:30 | C223–C230 |
| 20:00–20:30 | C295–C302 |
| 22:30–23:00 | C324–C332 |

The prior 01:00–01:30 pilot supplies the earlier anchor; it is not recomputed. The new `tools/s01e01_sparse_asr_drift_study.py` reads only the exact previously SHA-verified owner AVI (SHA `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`) and owner S01E01 English SRT (SHA `aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496`). It extracts five small transient 16-kHz audio windows from the one original AVI, runs independent faster-whisper tiny.en transcription, and compares each recognized phrase against actual source captions in that window.

The per-window report retains ASR text, source cue IDs and heuristic lexical-similarity/offset candidates, plus a median difference between source cue and recognized segment starts **only** for strong lexical matches. A spread of those window medians is a potential drift *review signal*, not a calibrated offset. No tool can infer a complete audiovisual cut from five brief samples. Audio, video and model weights are not preserved in Git or artifacts.

## Security and workflow

The offline [night-court-s01e01-drift-test.yml](../.github/workflows/night-court-s01e01-drift-test.yml) checks the exact five windows, source cue presence, matching behavior and explicit nonverification flags without network or FTP secrets. A separate, owner-only [night-court-trusted-s01e01-drift.yml](../.github/workflows/night-court-trusted-s01e01-drift.yml) uses a precisely named inert PR and executes **reviewed main SHA only** with the existing owner FTP secret. Avoid concurrent large-media scans or parallel multi-episode jobs while this is still a pilot.

Next acceptance: inspect sparse match results, mark incomplete/uncertain windows, compare with the 01:00–01:30 CTC/tiny.en candidates and obtain listening confirmation before assessing an actual source-to-SRT offset/drift. Keep the large original-season archive immutable and preserve AV uncertainty in all scene scripts.
