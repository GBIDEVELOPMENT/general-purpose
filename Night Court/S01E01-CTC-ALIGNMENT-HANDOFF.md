# S01E01 original-text-constrained CTC alignment experiment

Status: CTC offline proof passed ([PR #152](https://github.com/gamesbyian/general-purpose/pull/152)); owner-only [real-source alignment run #40048872758](https://github.com/gamesbyian/general-purpose/actions/runs/40048872758) **succeeded**, launched from inert [PR #153](https://github.com/gamesbyian/general-purpose/pull/153). The 16,765-byte compact JSON artifact (#12542019756) contains 42 word-time candidates, 2 low-acoustic-support word abstentions and three source turns that could not be aligned (C19 first voice, C22 second voice, C27 truncated boundary). Model revision: `22aad52d435eb6dbaf354bdad9b0da84ce7d6156`. Real-result retention remains gated by importer CI. Original 1984–1992 *Night Court* S01E01, fixed 60–90-second passage.

## Goal and method

The original 30-second script has nine SRT cues and 11 explicit speaker turns; tiny.en's independent ASR matched common words but not all comic vocabulary. A correct full-script pipeline needs word timing **constrained by the original subtitle witness**, independent of Whisper's tendency to silently replace difficult words. This experiment introduces a separate acoustic model and CTC Viterbi aligner for source text:
- Model: [facebook/wav2vec2-base-960h](https://huggingface.co/facebook/wav2vec2-base-960h), Apache-2.0 licensed. Downloaded ephemerally; actual model commit revision retained in outputs. No model weights in Git.
- `tools/ctc_source_aligner.py`: independent NumPy dynamic programming; handles repeated characters, blanks and impossible source texts, and allows low-acoustic-support **abstention**. This deliberately avoids TorchAudio's discontinued `functional.forced_align` API.
- `tools/s01e01_ctc_source_pilot.py`: reads only the SHA-accepted original AVI and the already retained SRT/ASR sources. For each eligible subtitle turn, computes Wav2Vec2 CTC emissions over a tightly bounded, padded audio interval and aligns the **original source words**. Skips absent/unmatched speaking turns and C27 truncated beyond 90 seconds. The program never modifies the subtitle witness and never invents a speaker.
- `.github/workflows/night-court-ctc-offline.yml` tests the CTC algorithm offline, including repeated letters, impossible paths and low-confidence abstentions. The trusted `night-court-trusted-s01e01-ctc-align.yml` uses an inert owner-PR marker and checks out only reviewed base-code, never PR code with credentials.

## Quality and acceptance limits

A CTC forced alignment is a **hypothesis that the text was spoken**; it can align an incorrect transcript onto background noise. Use word-level acoustic scores, source-cue versus candidate differences, source ASR corroboration and listening for acceptance. Long words such as “Minimifidian” and “extravasate” are particularly vulnerable. Lack of score calibration, background music, laugh track and overlap prevent automated certified timing. The experiment outputs candidate word spans for review, no verified global offset or drift. Media hash `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`; source English SRT `aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496`.

**Only after a successful live run and source review** should its derived word candidates be saved in `seasons/S01/S01E01/derived/scene-review-v3/`, separately from the original SRT, v1 tiny.en guesses and v2 source-image action evidence. Do not silently promote word timestamps to voice characterization or AV-completeness certificates.

Next: independent listening and speaker turns (including difficult mixed cue C22); visual mouth/voice corroboration; full-scene cut alignment with a start/end drift check; then longer episode passes.

## Durable acquisition and acceptance requirements

`tools/import_s01e01_ctc_source_evidence.py` re-reads the existing original-text turn packet; it will reject any CTC result with a changed AVI/SRT SHA, missing/duplicate cue turn, changed original source words, missing model revision, out-of-range/nonmonotonic candidate timestamps or a claim of verified speakers/emotions. Successful importer CI regenerates `derived/scene-review-v3/ctc-source-word-review.md` and preserves exact acoustic model predictions separately as JSON. These remain review-only hypotheses and do **not** edit the previously approved screenplay excerpt or source captions.
