# S01E01 lexical and word-timing cross-model review

Current pilot: original-series S01E01, source interval 01:00–01:30. Two pre-existing, SHA-verified candidates:
- faster-whisper tiny.en independent open transcription, then exact-token matching against original subtitle words (45 usable word-time candidates)
- `facebook/wav2vec2-base-960h` Apache-2.0 original-subtitle-constrained CTC forced-alignment pass in trusted run #40048872758 (42 usable candidate word times, two low-acoustic-support abstentions, three unmatched/truncated speaking turns)

The two methods use the **same source audio** and the CTC analysis windows are placed using the *first* model's approximate segment boundaries. Therefore the resulting timings are not strictly independent evidence of absolute synchronization. A CTC path can produce reasonable-looking timings even for words not audibly present. Rare comedy words and truncated audio remain explicit review targets.

`tools/compare_s01e01_word_models.py` joins **every original source word by episode/cue/typographic turn/word index**, first verifying exact source AVI and SRT hashes and original lexical agreement. Each word is classified as two-model proximity of starts within 300ms, start disagreement, model-only, or neither. It writes:
- `seasons/S01/S01E01/derived/scene-review-v3/word-timing-model-comparison.json`: fully inspectable every-word review packet.
- `.../word-timing-model-comparison.md`: reading report and source-cue-based manual listening queue.

Initial independent arithmetic check on current immutable evidence: **39 words have start-time candidates from both methods; 37 fall within 300ms, two differ more; median CTC-minus-tiny start difference approximately −37ms.** This is evidence of plausible source cut/caption timing in the sampled window, not an episode edition/drift acceptance or human-verified phoneme/word timing.

The next explicit acceptance is independent listening to at least one low-agreement, one rare-word and one multi-speaker passage, and review against original video to ensure start/end word timing, speaker attribution and performance directions are correct. Do not turn numeric model agreement into the scripts' verified voice-acting emotion or speaker names.
