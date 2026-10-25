## Current episode-credited screenplay readers and cast evidence (2026-10-24)

**The working scripts have advanced beyond the last clean-reader release:**

- [**Latest S01E01: All You Need Is Love, credited court-case screenplay**](seasons/S01/S01E01/derived/cast-courtroom-reading-screenplay-v3/screenplay-courtroom-cast.md), [exact source dialogue/role index](seasons/S01/S01E01/derived/cast-courtroom-reading-screenplay-v3/courtroom-source-index.json). **336/336 original timed subtitle cues, 404 speaking units, 306 provisional named blocks, 98 still unknown.** Includes 17 previously reviewed original-video static setting notes and two 5fps bounded original-video physical-action passages.
- [**Latest S09E19: P.S. Do I Know You?, credited pen-pal/campaign screenplay**](seasons/S09/S09E19/derived/cast-continuity-reading-screenplay-v3/screenplay-cast-continuity.md), [exact source dialogue/role index](seasons/S09/S09E19/derived/cast-continuity-reading-screenplay-v3/continuity-source-index.json). **347/347 original UNTIMED paragraphs, 347 original speaking units, 147 provisional named blocks, 200 still unknown.** Original video scene observations remain separate from the script's unverified paragraph times. The separate S09 [source video-to-dialogue search map](seasons/S09/S09E19/derived/source-coarse-picture-dialogue-review-v1/picture-to-dialogue-search.md) remains a non-authoritative editorial guide.

Both are substantially more legible full-original-dialogue working manuscripts. **Combined provisional named speaking blocks: 453/751 (60.3%); 298 blocks still unidentified**. This is not verified voice recognition or an overall percent of production completion. **0/193 original-series episodes are yet completely editor-ready or independently audio+video-certified**. The source captions remain authoritative and were not rewritten by ASR.

Episode-credited research [cast ledger](research/pilot-episode-credited-cast-v1.json) is grounded in [S01 pilot IMDb credits](https://www.imdb.com/title/tt0660578/fullcredits/), [S09 IMDb credits](https://www.imdb.com/title/tt0660693/), [TVmaze pilot guests](https://www.tvmaze.com/episodes/134243/night-court-1x01-all-you-need-is-love), and [TVmaze's credited Alex character](https://www.tvmaze.com/characters/846493/night-court-alex). S01's court-case speakers include separately credited Phil and Louise Kerr, Carla Bouvier, and Hacksaw Hammond. **Critically, S09 credits James McDonnell as Alex and Alex Henteloff as the distinct character 'The Guy'.** We explicitly abstain from labeling ambiguous stand-in dialogue as a named person from still images. Actor/character identity was never inferred from photographs; the original images have been used for observable costume/action/setting research only.

Work merged this pass: [PR #351](https://github.com/gamesbyian/general-purpose/pull/351) creates the actor/episode-role references and first 82+18 cast-context proposals; trusted derived manuscripts [PR #353](https://github.com/gamesbyian/general-purpose/pull/353) delivered the real scripts. [PR #354](https://github.com/gamesbyian/general-purpose/pull/354) and [PR #356](https://github.com/gamesbyian/general-purpose/pull/356) added and delivered 106 more S01 original courtroom/case guest voice headings. [PR #357](https://github.com/gamesbyian/general-purpose/pull/357) and [PR #359](https://github.com/gamesbyian/general-purpose/pull/359) added and delivered 53 more S09 regular/guest role headings. All source-only CI and trusted derivation jobs passed. One-shot trigger PRs were closed unmerged. No full-episode original AVI/ASR rerun was needed.

**Highest-impact remaining actual screenplay editing:** original soundtrack spot-checks to distinguish voices behind the 298 unknown source dialogue units and challenge provisional context labels; additional genuinely observed shot/scene/motion coverage, especially physical comedy between sparse frames; and S09 untimed source text-to-action review with only independently supported alignment. The strict archival acceptance status stays separate from delivering more useful working scripts.

## Actual clean-reading screenplays delivered, October 24

Source free CI and trusted source-owned run [#40155221069](https://github.com/gamesbyian/general-purpose/actions/runs/40155221069) built the two uncluttered working-screenplay reader editions. Code merged via [PR #347](https://github.com/gamesbyian/general-purpose/pull/347), actual output plus exact-regeneration test merged through [PR #349](https://github.com/gamesbyian/general-purpose/pull/349):

- [**Read S01E01 clean screenplay**](seasons/S01/S01E01/derived/clean-reading-screenplay-v1/screenplay-clean.md), [separate original cue/part source index](seasons/S01/S01E01/derived/clean-reading-screenplay-v1/source-reading-index.json), **336 original timed cues / 404 reading dialogue blocks**.
- [**Read S09E19 clean screenplay**](seasons/S09/S09E19/derived/clean-reading-screenplay-v1/screenplay-clean.md), [separate original cue/part source index](seasons/S09/S09E19/derived/clean-reading-screenplay-v1/source-reading-index.json), **347 original untimed paragraphs / 311 reader dialogue blocks** after 36 audited text continuation joins.

This edition removes repetitive per-line cue/timestamp footnotes from the reader's narrative flow while retaining full provenance in the adjacent index and keeping source-supported picture directions. The full tagged originals and v6/v7 evidence-rich editions stay unchanged. It is a readability milestone rather than a source-audio speaker verification, completely staged filmed screenplay, or an independently AV-accepted product. **Still 2 working source-complete pilot scripts, zero editor-ready episodes, zero independently AV-certified episodes.**

## Recovered and integrated S09E19 picture-to-dialogue editorial packet (October 24, 2026)

Recovered live repo after interruption; the existing practical screenplay
scorecard had already landed, so no duplicate handoff was created.
[PR #343](https://github.com/gamesbyian/general-purpose/pull/343)
merged a validated source-only editor-packet generator.
Trusted-base source compilation
[run #40154714246](https://github.com/gamesbyian/general-purpose/actions/runs/40154714246)
succeeded. [PR #345](https://github.com/gamesbyian/general-purpose/pull/345)
then passed exact source-free CI and merged the actual
[**S09E19 complete screenplay plus picture-to-dialogue reviewer appendix**](seasons/S09/S09E19/derived/caption-first-editor-review-v7/screenplay-and-review-guide.md)
and [source-preservation manifest](seasons/S09/S09E19/derived/caption-first-editor-review-v7/editorial-manifest.json).

This is a concrete editorial convenience: the original 347 **untimed**
S09 dialogue paragraphs remain unchanged from the source-complete
v6 screenplay and are followed by **15 unverified, broad picture-to-paragraph
search suggestions plus 3 explicit abstentions**, derived from 13 archived
unverified lexical model anchors and previously inspected original film
frames/motion windows. It does **not** assign original paragraph
timestamps, connect names to faces/voices, or assert visual-comedy
completion. Source v6 manuscript hash and the exact review-map
SHA are recorded in the v7 manifest. The trusted one-shot
trigger [PR #344](https://github.com/gamesbyian/general-purpose/pull/344)
was closed unmerged. Original source AV was not downloaded or processed again.

**Current counters stay honest:** two complete held-source-dialogue
working pilot scripts, zero whole-episode editor-ready screenplays,
zero independently audiovisual-certified scripts. Next substantive
work is reviewing original S09 source dialogue with the corresponding
video and soundtrack, resolving anonymous speakers and action continuity,
and advancing actual finished scene-level screenplay quality.

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
