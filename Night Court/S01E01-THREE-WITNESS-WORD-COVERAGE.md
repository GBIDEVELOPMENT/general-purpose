# S01E01 independent speech corroboration: correct episode-wide denominator

**Why this measurement matters:** An actual SHA-pinned original source ASR/SRT witness imported in [PR #284](https://github.com/gamesbyian/general-purpose/pull/284) found 184 substantial three-text-witness correspondences in 200 independent model-agreement spans. **184/200 = 92% of selected machine-consensus spans**, not 92% of the episode's dialogue and certainly not a 92% independently human-confirmed transcript.

`tools/measure_s01e01_three_witness_srt_coverage.py` now checks the exact immutable source SRT byte SHA and original 200-span ASR/SRT JSON SHA, decodes the real 336 source cues, and measures how many **distinct original subtitle token positions** are covered by ordered, exact textual model-model-original-SRT correspondences in the 184 positive spans. A source word occurring twice in separate episode cues counts as two positions; repeated model spans matched to the same source cue word count **once**. Any of the 16 model/SRT lexical dispute cases do not contribute to strict three-witness correspondence coverage.

It outputs the whole SRT word denominator, strict distinct covered-word count and fraction, number of original SRT cues with any textual evidence, and remaining uncovered cues. This remains **machine text correspondence**, not ground-truth spoken-word accuracy. The original SRT could omit speech, contain homophones or a different edition; model agreement may share systematic errors. No source text is overwritten and no speaker, delivery or performance is confirmed.

Run read-only with no secrets, video, models or FTP:

```bash
python 'Night Court/tools/test_measure_s01e01_three_witness_srt_coverage.py'
python 'Night Court/tools/measure_s01e01_three_witness_srt_coverage.py' --output /tmp/original-srt-source-coverage.json
```

This budget-aware coverage metric is a much more useful acceptance indicator than counting how many selected ASR spans agree with existing captions. For 193 episodes, the product target remains a fast (<30m p95) first audiovisual pass and an independently measured **blind original-audio evaluation of model-model agreement joint errors** before auto-accepting dialogue. Existing 0/193 AV-complete production-screenplay gate remains unchanged.
