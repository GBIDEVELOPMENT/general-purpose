# Blind original-audio model comparison: calibration protocol

The [fast episode factory](FAST-EPISODE-FACTORY-THROUGHPUT.md) currently
runs `faster-whisper tiny.en` and a truly distinct Vosk/Kaldi recognizer.
Their output agreement is useful **positive machine evidence**, but it is
not proof that a line was actually spoken. Nor does agreement measure
performance tone, named identity or completeness.

`tools/calibrate_original_asr_truth.py` now supports an **offline,
source-listened** model comparison. It computes each model's normalized
word error rate and, most importantly, the rate at which the first two
recognizers agree with one another but disagree with independently
listened original words. It refuses any episode-wide acceptance claims.

## Calibrate without contaminating the models

1. Select the already identified **16 S01E01 caption/model disagreement**
   passages (71.9 seconds of planned direct original-source playback),
   add uncommon invented phrases, overlapping voices, laughter and quiet
   dialogue **plus randomly selected agreement windows**. Selecting only
   disagreements will bias model accuracy estimates.
2. Independently *listen to the SHA-verified original audiovisual edition*
   without reading model output, then create short attested reference texts.
   Each contains `case_id`, `source_interval_ms`,
   `verified_original_text`,
   `original_audio_independently_listened: true` and
   `reviewer_attested_original_words: true`. These flags must only be set
   after actual source listening. Time windows remain original-source
   clip boundaries, not guessed word times.
3. Provide free-decoder hypotheses keyed to exactly the same original
   SHA/case/time pairs, with distinct architectural-family labels and
   `original_subtitle_or_other_decoder_prompt_used: false`. Do not feed
   the reference, original subtitle or another recognizer's answer to
   a free decoder.
4. Run
   `python 'Night Court/tools/calibrate_original_asr_truth.py' --independently-listened-gold GOLD.json --models MODELS.json --output REPORT.json`.
   The report preserves the SHA of each input and separate per-model WER,
   consensus windows and jointly wrong consensus windows.
5. Compare bounded CPU and GPU candidates **on the same blind reference**:
   start with the currently pinned Whisper/Kaldi, then a stronger
   faster-whisper or one genuinely independent Conformer/CTC decoder.
   Prefer the best accuracy/latency trade-off for original sitcom jokes
   and overlap, not a generic published leaderboard winner. Forced
   alignment is not independent free decoding and belongs in a later
   original-word timing stage.

This instrumentation is **implemented and source-free tested**. No such
independently source-listened calibration gold is yet available for the
full original episodes, so no genuine WER, best model, model-derived
dialogue acceptance or faster end-to-end screenplay production is
claimed. No original sound/video, model weights or sensitive access data
are stored by the scorer. Original transcription witnesses remain intact.
