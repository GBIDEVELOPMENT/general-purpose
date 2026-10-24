# Fast positive corroboration from two independently decoded speech witnesses

**Status:** offline text/time evidence reconciler implemented; actual full-episode second ASR model, independent source-listening calibration and complete runtime benchmarks **not done**. The first real S01E01 36s Whisper tiny.en candidate has one model only ([open import PR #258](https://github.com/gamesbyian/general-purpose/pull/258)); do not pretend it is multi-model verified.

`tools/compare_independent_asr.py` uses only the Python standard library. Its input schema is `night-court-two-independent-asr-words/1`: episode ID, SHA256 of the original video and a **single shared decoded audio input**, source time interval and exactly **two** word-timed, independent free-decoding model outputs. Each model declares `model_id`, `architecture_family` (distinct across the pair), `free_decoding: true`, `srt_or_other_model_prompt_used: false` and `words` (verbatim token, source-local start/end ms). The trust boundary must actually verify the source SHA and common decoded PCM hash before constructing this input. Mere strings claiming independent architectures cannot prove model training/data/error independence.

The reconciler builds token/time indexes, finds candidate equal words within **600ms**, preserves increasing word order and groups runs of at least **three consecutive matching tokens**. It calls those spans `independently_machine_corroborated_dialogue_candidate`; this is an affirmative evidence class, **not** just a disagreement worklist. Verbatim text, both models' word index ranges, original time interval and maximum time discrepancy are retained. Single/two-word matches and model-only extra or conflicting tokens are separately listed as unresolved. This deliberately prioritizes precision and abstention; it can miss genuine dialogue with imperfect word alignment. It does not assign character identity, certify lip synchronization, infer emotion or claim human source listening.

Performance: the offline synthetic **10,000-word-per-model** regression completed locally in approximately **0.1s** on the current test machine. That tests only text reconciliation; no speech-model inference or actual full-episode source decoding is included. Per-model word arrays are hard-bounded at 15,000 and the code requires a source window <=7,200s. For actual episodes, measure runtime separately and retain unrecognized terms as deliberate review candidates.

Example CI:
```sh
python 'Night Court/tools/test_compare_independent_asr.py'
python 'Night Court/tools/compare_independent_asr.py' --input /private/episode-two-asr.json --output /private/consensus.json
```

**Next:** benchmark a genuinely distinct, affordable free-decoding CTC/Conformer/RNNT model against the current Whisper family, *without source subtitle prompts*, on an original S01E01 audio excerpt. Test processing cost and rare comic vocabulary first, then extend to whole-episode parallel/sequential comparisons. Align consensus to the immutable independent SRT in a separate stage and estimate the actual **joint error rate when both models agree** from blind listened passages. Never use subtitle-constrained CTC forced alignment as a purported second independent recognizer. Keep original SRT, independently corroborated candidate, confirmed spoken words and cast-speaker identity as different evidence layers.
