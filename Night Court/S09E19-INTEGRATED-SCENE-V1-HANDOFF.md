# S09E19: first source-linked audiovisual script excerpt

Status: v1 renderer implemented; acceptance depends on offline CI and source-hash checks. This is the **second** original-series episode with genuine source-linked dialogue and video observations, after the S01E01 pilot. It is not an independently verified production screenplay.

## Exact sources and results

Original-S09E19 AVI SHA-256: `51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649`. The owner held 347 untimed source dialogue paragraphs with original text SHA `659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2`. A trusted five-window real-source ASR run located 15 unique high-lexical candidate paragraph occurrences in their expected overall source order. Its 15:00–15:25 video window supplied five original-paragraph matches.

A second trusted run produced 100 actual original-AVI frames (nominal 4fps) for the same interval, which were reviewed and saved with six source-frame-linked observations in `derived/visual-review-v1`. The observed views include people at an interior counter, a cut to a seated person in burgundy and a conspicuous yellow collar making hand/head movements, then a cut to a bearded suited person. Camera-change bounds are between neighboring sampled frames, not independently inspected original frame-accurate cut times.

`tools/render_s09e19_source_scene.py` reconciles the source AVI SHA, original paragraph text SHA, all five model dialogue candidates, and all six checksum-backed visual notes. It outputs:

- `seasons/S09/S09E19/derived/scene-review-v1/source-linked-scene.md`: a readable stage- and dialogue-oriented research excerpt
- `seasons/S09/S09E19/derived/scene-review-v1/source-linked-scene.json`: the per-event source/time/frame evidence map

## Critical limits

Every original dialogue line remains **untimed at the source**. ASR provides approximate video-time *proposals*, not source SRT cues or acceptance that the whole line was spoken. Speaker identities, facial-to-voice attribution, emotional delivery, actual shot continuity and complete episode dialogue remain unverified. The proposed venue is deliberately generic; the exact set, fictionally named characters and camera cut timings have not been independently validated.

Unit tests require five distinct preserved source paragraph candidates, six real reviewed visual frame observations, 347 unchanged original paragraphs and no claimed speaker/AV completeness. A later human/audiovisual review must confirm words, visible performance, gestures, scene setting and episode cut before promoting any event into a canonical screenplay.

The original Season 9 witness and the existing 193 source-only reading scripts are not modified.
