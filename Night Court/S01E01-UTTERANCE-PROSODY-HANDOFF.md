# S01E01 vocal performance: utterance-level measurement lane

Status: implemented with a **permissively licensed** librosa/SoundFile/NumPy acoustic backend; source-media analysis pending trusted workflow run. October 23, 2026. This phase improves on earlier five six-second averaged audio mix measurements, but is still **not isolated voice diarization**.

## What is measured

The independently acquired faster-whisper tiny.en pass supplied ten candidate spoken spans in source-video seconds 60–90, with some original SRT cue matches. Instead of using a broad 6-second window, `tools/s01e01_utterance_prosody.py` extracts the exact known S01E01 AVI temporarily, fingerprints the complete file, decodes the fixed 30-second PCM window, and calculates per-candidate:
- RMS/peak digital level from the local window, explicitly of the **mixed soundtrack**, not a named performer's loudness.
- A YIN pitch track (65–550Hz) with amplitude-gated candidate frames; median and 10th/90th percentiles of the surviving **mixed** F0 proposals.
- An early-vs-late candidate pitch change in semitones, not an assertion of interrogative contour, sarcasm, emphasis, or another emotional quality.
- Source ASR segment index and SRT cue hint, bounds and model package versions. It does not change any archived dialogue or infer speakers.

All speaker/emotion/delivery fields remain null or false. Inference from laughter, music, effects or overlapping voices will be unreliable; short utterances are flagged. `YIN` can propose periodicity even on non-voice signals. The numerical features are intended for a later listener validation and speaker-isolated review.

## Provenance, rights and dependency boundaries

Only the exact previously SHA-verified **183,386,112-byte S01E01 AVI** is eligible. Source SHA-256: `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`. Original SRT SHA-256: `aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496`. Speech-model source is the existing immutable `scene-review-v1/asr-prosody-hypotheses.json`, not a fresh external transcript.

No raw audio, video or pretrained model weights enter the repository or artifact. The repo owner triggers only an inert PR; `.github/workflows/night-court-trusted-s01e01-utterance-prosody.yml` executes **trusted base SHA** code with the existing repository FTP secret. Source is deleted with the runner temporary directory.

The new dependency tier `tools/vocal-requirements-prosody-open.txt` uses librosa (ISC), SoundFile (BSD) and NumPy (BSD). It does not call openSMILE or require commercial openSMILE feature-extraction permission. Exact resolved dependency versions are retained in the eventual results.

## Review/acceptance ledger

| Check | State |
|---|---|
| Real S01E01 60–90s source AVI hashed and archived as metadata | Complete |
| Original SRT and candidate ASR cue/word mapping retained | Complete (45 exact-token ASR time proposals; not independently verified) |
| Per-utterance acoustic algorithm and offline synthetic pitch test | Implemented; CI pending |
| Real per-utterance F0 and loudness measured, checked against original source | Pending trusted run |
| Speech isolated from audience/music/overlapping speakers | Not done |
| Character voice/visual speaker attribution | Not done |
| Emotional or sarcastic/comic inflection validated | Not done |
| Full scene/performance screenplay verified | Not done |

Next: run the safe source-only workflow, inspect actual per-turn acoustic variability, compare with the source transcript and temporal frame review, then move to independent, listener-confirmed speaker turns. Do not infer spoken voice identity from costume or pitch.
