# S01E01 source-cue-to-ASR word evidence review

Status: deterministic review-packet generator implemented; **not** an accepted forced alignment or speaker diarization. Date 2026-10-23.

## Why this matters

We already hold the original owner's 336-cue S01E01 SRT and SHA-verified 60–90s video evidence. Independent faster-whisper tiny.en identified ten candidate speech segments in that window, but mixed two-spoken-turn cues C19 and C22, missed unusual diction (“Minimifidian”, “extravasate”), and truncated C27 at the video-window boundary. A cue-to-segment similarity match is not valid proof that the caption appears at exactly that time.

`tools/build_s01e01_word_alignment_review.py` uses existing immutable `segments.jsonl` and `derived/scene-review-v1/asr-prosody-hypotheses.json` only. Its deterministic transformations:
1. Require the exact source SRT SHA, exact known AVI hash, model provenance, exact 60–90s window and nine expected cue IDs.
2. Split multi-speaker captions **only where the original explicitly uses leading dialogue hyphens**. No character assignments are made.
3. Choose at most one ASR segment candidate for each explicit source turn based on lexical compatibility; unmatched ASR and caption turns remain unassigned.
4. Link original caption tokens to actual candidate ASR word timestamps **only where the normalized tokens are exactly equal**; reject zero-length, out-of-window and malformed estimates. Do **not** interpolate missing words or overwrite source timings.
5. Record lexical mismatches, source boundary truncations, missing/low-confidence words, and model/human review gates in JSON and Markdown.

The derived evidence is at `seasons/S01/S01E01/derived/scene-review-v1/word-alignment-review.json` and `word-alignment-review.md` after PR CI generation. Model timestamps remain **hypotheses**, including where word identity is exact; the word estimates come from faster-whisper tiny.en, not a dedicated forced-alignment system.

## Next acceptance gates

- Review the 60–90s waveform or actual audio and verify source text and model times; specifically C19 first speaker falls before 60s, C22 uses unusual vocabulary and C27 is clipped.
- Run a proper original-text-constrained alignment model, compare against cue times, and obtain an independent listener review for difficult portions before claiming frame-accurate speech timing.
- Use independently identified voice evidence for named character labels. Neither lavender clothing nor a uniform proves a speaking character's identity.
- Analyze higher-density frame/clip evidence across prop actions before adding **movement** stage directions. Still frames prove only sampled states.
- Once 60–90s is reviewed, run the same design over additional contiguous windows with an auditable cut/offset hypothesis and drift estimates, rather than declaring the whole DVD cut synchronized.

Any model that cannot resolve a hard word or speaker should **abstain visibly**; the output quality goal is an honest, correct script, not an artificially high percentage of labels.
