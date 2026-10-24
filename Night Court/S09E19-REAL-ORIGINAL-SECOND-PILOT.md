# S09E19 full original audiovisual source speed: second real pilot complete

[Trusted owner-only original AVI run #40126128202](https://github.com/gamesbyian/general-purpose/actions/runs/40126128202) successfully processed **all 22m 0.144s** of original-series S09E19 audiovisual material on a single ephemeral GitHub runner. One original source video retrieved, one PCM audio decoded, two independent free-decoding recognizers, a whole-video small-resolution contrast-change scan and ≤240 native-PTS-selected original JPEG samples. **Measured source-processing wall time: 215.140 seconds (3m35.140s)** excluding GitHub runner setup and software installation. The original AVI SHA and source 347-paragraph untimed transcript SHA were strictly checked.

### Measured original source processing

| Stage | Time |
|---|---:|
| Retrieve and verify source AVI | 3.132s |
| FFprobe | 0.097s |
| Decode whole episode audio | 4.622s |
| Pinned Vosk weights download/unpack | 9.950s |
| Vosk/Kaldi whole episode inference | 97.109s |
| Whisper tiny.en whole episode inference | 53.614s |
| Distinct-ASR lexical/timing agreement | 0.019s |
| Full episode 160px frame image-change scan | 25.133s |
| Plan source-aware capped frame selections | 0.009s |
| Extract and verify 202 original source-PTS JPEG stills | 21.248s |
| Probe original untimed source paragraph lexical candidates | 0.207s |

The audio models proposed **1,299 agreement words across 199 at-least-three-word spans** (independent recognizer hypotheses, not source-heard voice truth), preserving 1,989 unresolved individual-model word proposals. The video scan found **212 possible image-change edits**, not independently confirmed shot cuts. It produced **202 original PTS-checked JPEG stills**, 999,791 bytes in temporary scratch, all erased with original AVI/WAV/model weights when the source run completed.

The source paragraph text remains **347 completely untimed original paragraphs**. Exactly **40** distributed agreement spans underwent cheap text-only lexical probing, yielding **13 distinctive paragraph-source hypotheses** at inferred original-AUDIO times. All 13 source paragraph IDs appeared in increasing order, but **no original source paragraph timestamp has been fabricated**. The extra globally ordered source-text audit resides in `tools/reconcile_s09e19_untimed_source_order.py`, merged via [PR #288](https://github.com/gamesbyian/general-purpose/pull/288). Direct original source listening and full audiovisual script acceptance remain pending.

The complete original JSON is verified by SHA-256 `14e721068a10ceb1c84b62ef04169364edb2a58741aaf889afe4a5ef90daa51c`. Private artifact #12572627835 ZIP SHA `95af07bd3a2f5ad62a252fcb4171662b90e8ad926237479ad259280ee22eb0ca`, expires October 31, 2026. The SHA-locked trusted importer will permanently retain numeric/tiny text evidence under `seasons/S09/S09E19/derived/whole-source-once-v1/` and a ranked paragraph-order review before artifact expiry. Original image/audio video, username, secrets and model weights stay out of source control.

**Comparison:** S01E01 integrated original-source processing **239.826s** for a 24m08s timed-SRT episode, S09E19 **215.140s** for a 22m untimed-dialogue episode. Both used one real original AVI, two distinct recognizers and bounded full-video sampling. This supports a fast research first pass across different source types. It does **not** establish p95 across 193 episodes, source word certainty, calibrated speaker identification, actual image-content comprehension or production-ready stage directions. All original-series completed production scripts remain at 0/193 until audiovisual acceptance.

### Archival contract

The imported version is a preserved original research witness, **not a verified screenplay**. `tools/preserve_s09e19_source_once_evidence.py` validates full video SHA `51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649`, original text SHA `659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2`, exact original PCM SHA, 1320.144s full duration, model family separation and no source-time promotion. It saves an exact raw source research JSON, a reproducible ordered-lexical candidate report, a compact benchmark, and readable handoff notes. Synthetic/real-corpus adversarial QA runs offline. On branch `research/night-court-s09e19-real-evidence-import-trigger`, touching only `Night Court/research/trigger-s09e19-full-evidence-import.txt` dispatches reviewed-trusted-main import into a separate data PR branch. Trigger is closed without merging.
