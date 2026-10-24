# Untimed original dialogue: safe ordering of independent recognizer proposals

S09E19's original 347-paragraph caption witness has **zero actual source paragraph timecodes**. The existing sparse source excerpts generated a handful of unique high-similarity proposed paragraph matches. The second full-episode source-once pilot is now measuring whether two independent recognizers provide enough original-audio lexical evidence to grow these proposed anchors quickly.

`tools/reconcile_s09e19_untimed_source_order.py` uses only existing preserved immutable source text and **at most 40** original-audio intervals selected from the second episode's independent model agreement report. It rechecks source SHA, exact paragraph count 347, fully untimed original source, plausible original AVI and source-audio interval, independently compares each candidate text to the official 347 paragraph source and tests exact lexical uniqueness. A maximum-score increasing sequence separates globally order-consistent, distinct lexical candidates from conflicts requiring review.

**This is a lightweight research filter, not forced alignment.** The source paragraph timestamp field remains **null** for every candidate, no matter how convincing a model-ASR time looks. It neither rewrites the original paragraph text nor certifies actor voice, emotional performance, physical action, real shot/scene edits or production screenplay completion. An excluded anchor may be true but ambiguous or affected by ASR errors. A selected anchor may be wrong due to two models sharing language mistakes. Those distinctions must remain explicit in the output.

Unit QA uses genuine original S09E19 untimed paragraphs to exercise the source matcher with synthetic audio interval candidates. It rejects a source-time invention, order regression, incorrect source SHA, wrong paragraph count or fraudulent human-acceptance flag before any original AVI is retrieved.

**Speed:** no further audio/video decodes or third recognizer. Its only substantive work is matching ≤40 already-available snippets to 347×(1..3)-paragraph candidates, plus a bounded ≤40-entry monotonic check. Verify actual runtime and usefulness from original second pilot before scaling to entire seasons.

The 193-episode publication gate remains 0 AV-complete screenplays. The 30-minute p95 source-first evidence factory target requires testing multiple representative original episodes and budgeting downstream image/video-language understanding, not just this transcript ordering step.
