# Night Court: current practical screenplay delivery and measured quality

_Updated October 24, 2026, Calgary local date. Original 1984–1992 series only._

## What can actually be read now

The original subtitle-first production approach has delivered **two full held-source dialogue working manuscripts**, not just research packets:

- [S01E01 latest source-staged screenplay](seasons/S01/S01E01/derived/caption-first-source-stage-in-scene-v6/screenplay-with-stage-directions.md), with its [source and quality manifest](seasons/S01/S01E01/derived/caption-first-source-stage-in-scene-v6/stage-direction-manifest.json).
- [S09E19 latest readable original-transcript screenplay](seasons/S09/S09E19/derived/caption-first-readable-screenplay-v5/screenplay-readable.md). [Source and dialogue preservation manifest](seasons/S09/S09E19/derived/caption-first-readable-screenplay-v5/reader-manifest.json). The unchanged v6 edition also exists, but source-video action must remain separate from its **untimed** transcript.

Read the screenplay prose first. Original caption cue markers and evidence ledgers are there for the editor, not a reason to demand archival audiovisual certification before doing ordinary script editing.

## Real measurable quality, without pretending this is completion

| Metric | S01E01 | S09E19 |
| --- | ---: | ---: |
| Original held-source dialogue cues/paragraphs preserved | 336/336 | 347/347 |
| Held source speaking units | 404 | 347 |
| Named **provisional** source-context dialogue units | 118 | 77 |
| Still-unidentified source speaking units | 286 | 270 |
| Distinct original-source still images across the runtime | 80 | 73 |
| Directly reviewed static-photo annotations | 17 | 16 |
| 5fps original-video motion samples reviewed | 210 frames across 42 s | 200 frames across 40 s |
| Actual sampled physical action scenes described | 2 | 2 |
| Motion/still notes beside timed dialogue | 19 | 0, originally untimed source |
| Repaired arbitrary paragraph continuity breaks | n/a | 36 |
| Coarse original-video photo search proposals | n/a | 15 candidates; 3 abstentions |
| Source-audio verified character identities | 0 | 0 |
| Whole-episode screenplay editor-ready | **No** | **No** |
| Independently entire-AV certified | **No** | **No** |

**Project counters: 193/193 held source-only episode scaffolds, 2/193 original-held-dialogue complete screenplay working drafts, 0/193 editor-ready full-episode visual/dialogue screenplays, 0/193 independently AV-certified episodes.** The editorial named-label fraction, **195 of 751 source speaking units**, is approximately **26% provisional coverage**; it is *not* a voice recognition accuracy score or an overall project completion percentage.

## What recently shipped to main

[PR #333](https://github.com/gamesbyian/general-purpose/pull/333) introduced the readable v5 screenplay renderer and 154 additional editorial source-caption speaker hypotheses, verified against original cue content. [PR #335](https://github.com/gamesbyian/general-purpose/pull/335) checked in the actual generated readable manuscripts after source-text SHA and cue-order QA.

[PR #336](https://github.com/gamesbyian/general-purpose/pull/336) added the S01 in-scene physical action renderer; [PR #338](https://github.com/gamesbyian/general-purpose/pull/338) checked in its exact regenerated v6 manuscripts. S01 has 17 original-camera still descriptions and two short observed original-motion passages beside nearby SRT dialogue, each explicitly denying exact cut/speaker sync.

[PR #339](https://github.com/gamesbyian/general-purpose/pull/339) made S09 conservative audio-text/video review anchors from already cached original-source evidence. The resulting [coarse picture-to-paragraph review map](seasons/S09/S09E19/derived/source-coarse-picture-dialogue-review-v1/picture-to-dialogue-search.md) was generated and merged through [PR #341](https://github.com/gamesbyian/general-purpose/pull/341). It reuses 13 *unverified* original-independent-model lexical proposals to suggest 15 broad transcript search locations for visually inspected source images or action samples and to abstain on three. It does **not** assign original paragraph timecodes. A model agreement and interpolation are review clues, not independently listened proof.

All source AVI/audio, original frames, model weights and secrets stayed out of Git. The original pilot source SHA fingerprints and both originals' dialogue text remain unchanged.

## Highest-value next implementation and editorial pass

First, **make the 556 still-anonymous source speaking units intelligible**, focusing on the major courtroom exchanges and the pen-pal/campaign plot. Reuse the exact source cue/part backlog generated beside each v5/v6 script. Favor character self-identifications, sustained monologues and linked replies when strongly supported. Keep adjacent multiple-speaker captions unresolved when punctuation, turn or source semantics are genuinely ambiguous; the source soundtrack or lips may resolve them. Don't automatically assign characters just because a nearby frame contains somebody.

Second, **complete scene-oriented staging with actual source pictures**. More than 18-second sparse photography and four short 5fps passages are required to catch the important *Night Court* physical comedy. Select short clips around plot-relevant scene gaps rather than spending time in another full ASR contest. Align with visible source and sound when cheap; never invent performance/voice emotions.

Third, for S09E19, use the newly generated picture-to-paragraph table as a **navigation guide**, not video-to-caption clock truth. Check candidate ranges where scene subject and source dialogue actually correspond. Place a theatrical action in the manuscript only after editorially reviewing the relevant source clip and its connection to the exact dialogue passage. Keep its original 347 paragraphs untimed.

Fourth, measure **real prose-quality progress**: identifiable dialogue proportion, real observed scene transitions and key gags represented, number of unresolved speaker/caption collisions, total editor minutes and genuinely readable continuous episodes. Only after the two pilots pass a practical editor-ready screen should the 193-episode run scale.

**Do not downgrade this work to zero merely because archival verification hasn't passed.** Two screenplay-length manuscripts and many original scene observations are real delivery. Equally, do not promote these to two completed, fully staged screenplays: neither is that yet.
