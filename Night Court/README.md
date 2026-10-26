## Current engineering gate: identify missing or incorrect speakers first (owner directive, 2026-10-25)

The highest-priority deliverable is **resolving unknown or falsely identified speakers across the original-series pilot episodes, with correct within-caption speaker turn boundaries before assigning character names**. Do not divert to fan cards, wardrobe, tone, or stage description until this P0/P1 work advances.

**Current source-exact working coverage: 590 provisionally named / 161 UNKNOWN across 751 original caption-derived speaking units** (historical v4/v5 baseline 487 / 264). The source-first [v8 private generator](tools/build_original_audio_speaker_reader_v8.py), [private 193-episode export](tools/export_fan_retrieval_chunks.py) and [SQLite fan speaker evidence index](tools/fan_sqlite_index.py) use the newer names while preserving every held original caption/source SHA. **No new identities have yet been independently confirmed by human review of original audio/video.** Published quotes and voice-embedding proposals are clearly labeled as supporting hypotheses, not AV identity certification. A previous guessed Lana attribution was corrected to Harry after published-quote comparison.

**Actual original soundtrack source progress:** [S01E01 original-voice comparison](https://github.com/gamesbyian/general-purpose/actions/runs/40252708569) evaluated 42 original UNKNOWN audio windows, providing four new provisional source-acoustic role suggestions; its known-role holdout was 56/75, not verified ground truth. [S09E19 source audio locator](https://github.com/gamesbyian/general-purpose/actions/runs/40253914693) found **231/347** original untimed paragraph audio-position candidates (116 unlocated). [First S09 voice pass](https://github.com/gamesbyian/general-purpose/actions/runs/40256897493) found 39 UNKNOWN audio windows but only two usable known-reference character groups, yielding no eligible new names. The improved [source-checked S09 voice bank](S09-ORIGINAL-SPEAKER-EMBEDDING-REVIEW.md) tested four proposed character references (Christine, Roz, Dan, Mac) on the **actual second S09 original soundtrack run** [#40257892582](https://github.com/gamesbyian/general-purpose/actions/runs/40257892582): **18/26 seed-role holdout and three cautiously accepted *editorial* S09 name proposals**, with a suspicious fourth C129 model output **quarantined as UNKNOWN**. This is not true human actor-voice verification. See [speaker identity first](SPEAKER-IDENTITY-FIRST-2026-10-25.md), [current 161-source-unit review queue](tools/plan_next_speaker_review_v9.py), and [P0 within-caption switch queue](research/probable-internal-speaker-switches-v1.json).

The source has at least one verified editorial split of one original paragraph into two likely speaking roles, and 12 additional potential internal voice changes flagged for review. Consequently **751 is the immutable original-caption source-unit denominator, not proof the finished episode has exactly 751 true performed speaker turns**. Accurate attribution outranks inflating the apparent named count. The original subtitle/transcript witnesses and prior v5 full staged manuscripts remain unchanged.

## Purpose: build an LLM-ready Night Court obsession corpus (owner directive, 2026-10-25)

The actual consumer is an LLM performing deep, well-grounded *Night Court* fandom, not a video-understanding research benchmark. See the [fan-corpus product contract](FAN-OBSESSION-DELIVERABLE-2026-10-25.md) and [borrow-first upstream adoption review](UPSTREAM-REUSE-FOR-FAN-CORPUS-2026-10-25.md). Respect the ranked P0 turn → P1 speaker → P2 delivery → P3 props/wardrobe → P4 action priorities and retain the separate independent AV-certification ledger (still 0/193) without blocking provisional fan-use products.

**Immediate reproducible retrieval seed:** `python 'Night Court/tools/export_fan_retrieval_chunks.py' --output /tmp/night-court-fan-retrieval` yields local/private episode/source-SHA-tagged JSONL chunks from the two richer v5 pilots plus 191 source-only scaffolds. `--pilot-only` restricts to both pilots. This export does not add factual annotations, authenticate speakers, publish copyright text or contact any model/API; source-only chunks must not be presented as filmed scenes. Run the offline synthetic test: `PYTHONPATH='Night Court/tools' python -m unittest test_export_fan_retrieval_chunks`.

## Authoritative screenplay priorities (owner direction, 2026-10-25)

Read [SCRIPT-PRIORITIES-AND-ACCEPTANCE-2026-10-25.md](SCRIPT-PRIORITIES-AND-ACCEPTANCE-2026-10-25.md) before any script reconstruction or agent dispatch. Rank 0 turn segmentation (including consecutive same-speaker caption merging and intra-cue switches), 1 character attribution, 2 tone/delivery, 3 wardrobe/props, 4 physical stage directions, 5 timestamp accuracy. Preserve original cue evidence and approximate offsets, but do **not** optimize for precise timestamps ahead of script comprehension. Historical pilots are not independently AV certified.

## Action direction is now an explicit, source-first review gate (2026-10-25)

The real original-film Qwen 1fps→2fps test **did not correct the S01E01 touch actor/recipient reversal**. To avoid spending more CPU on fluent but incorrect action accounts, the [source-first directed-action reviewer procedure](SOURCE-FIRST-DIRECTED-ACTION-REVIEW.md) and [private all-pending action form / safe count exporter](tools/source_first_action_review.py) now ask a human reviewer to document **initiator, physical action, recipient/object and actual original-moving-video evidence**. The form is exact-original-source-SHA and exact-model-report-byte-SHA bound and cannot record observed actions without explicit continuous-source review. The safe export contains **only counts and provenance hashes**, not copyrighted source frames, dialogue, reviewer prose or model hypotheses. This is review infrastructure, **not completion of an AV inspection**: 0/193 whole episodes remain independently AV-certified.

## Actual Qwen original-video temporal experiment: extra frames did not fix actor direction (2026-10-25)

Trusted original-source [2fps run #40237088693](https://github.com/gamesbyian/general-purpose/actions/runs/40237088693) completed for the same exact film excerpts as prior [compact 1fps run #40235589077](https://github.com/gamesbyian/general-purpose/actions/runs/40235589077). Both produced valid ten-field JSON. S01E01 inference **120.394→52.106s**, S09E19 **134.147→34.912s** in these individual CPU executions, but the model **still attributes the S01 cheek-touch gesture to the standing person rather than the seated judge** against existing original-SHA-derived stills and also appears to place contact on the arm rather than cheek. More FPS did **not** establish better physical-action recognition. These unexpectedly large runtime differences are measurements, not a causal throughput guarantee. [Exact source-safe report/clip/model/prompt hash ledger](research/real-original-qwen-compact-1fps-vs-2fps-2026-10-25.json) · [limitations and next reviewer gate](ORIGINAL-QWEN-COMPACT-1VS2FPS-RESULTS-2026-10-25.md). No original moving-film audiovisual reviewer approved action, and **0/193** episodes independently audiovisual certified.

## Original-film Qwen A/B: compact output faster, but same action-direction failure (2026-10-25)

The exact source-video [standard-prompt run #40230163151](https://github.com/gamesbyian/general-purpose/actions/runs/40230163151) and [compact-prompt run #40235589077](https://github.com/gamesbyian/general-purpose/actions/runs/40235589077) used **byte-identical temporary clips** for each pilot (full original video edition SHA and excerpt clip SHA match), same 2B revision, 1fps/256px, silent picture and 256 generated tokens. Changing only the immutable prompt improved ten-field JSON validity from **1/2 to 2/2**, with Qwen inference time **160.659→120.394s** in S01E01 and **163.603→134.147s** in S09E19. However S01E01 **still reversed who touched whom** against source-derived ten-frame reference, and S09 object/hand positions remain unverified. See [durable numeric/source proof](research/real-original-qwen-standard-vs-compact-prompt-ab-2026-10-25.json), [reasoning and acceptance gates](ORIGINAL-QWEN-COMPACT-PROMPT-MATCHED-RESULTS-2026-10-25.md). **This is format/cost improvement on two snippets, not verified visual-action or screenplay-quality improvement. No source original-movie AV-staging approval, 0/193 episode certifications.**

## Action-rich Qwen source pilot exposes wrong actor attribution (2026-10-25)

The second [trusted original-movie Qwen run #40230163151](https://github.com/gamesbyian/general-purpose/actions/runs/40230163151) succeeded technically on **S01E01 846–848s** and **S09E19 555.8–557.8s**, with one verified owner-original AVI download and one silent two-second Qwen3-VL-2B CPU inference per episode. S01 produced valid ten-field JSON after **160.659s inference** (191.077s model tool); S09 took **163.603s inference** (193.490s model tool) but returned `non_json_model_output` at the 256-token cap. Both jobs produced private unaccepted hypothesis, all-deferred risk-first reviewer packet and compact numeric performance files. No source media, dialog, frames or model prose committed.

**Concrete failure:** ten original-SHA-linked sampled stills from S01 show the seated judge reaching to the standing woman's cheek, while Qwen **reverses the person performing the touch**. This is an actionable stage-accuracy defect even though the model JSON passed. A separate S09 ten-frame sequence depicts a small-object hand interaction, but Qwen's incomplete response cannot qualify for stage claims. [Source-safe numeric record](research/physical-business-qwen-first-source-verified-results-2026-10-25.json) · [detailed evidence limits and next gates](ORIGINAL-QWEN-PHYSICAL-BUSINESS-RESULTS-2026-10-25.md). These **sampled-image** observations are not independent full-motion audiovisual acceptance; 0/193 complete episodes certified. Prioritize who-did-what-to-whom verification, then a tiny matched-window 1fps vs 2–3fps test, before further bulk model inference.

## Source-still-supported Qwen triage, not original audiovisual acceptance (2026-10-25)

The first actual Qwen source-film descriptions have now been compared with **existing sampled original-picture evidence**. An independently read S01E01 source-SHA-linked 4fps index (77–79s; eight frames) and S09E19 5fps contact sheet (812–814s; ten nominal frames) were used to mark **all twenty proposed model fields**, without pretending the original film was played in continuous motion or with synchronized sound. **5 fields were visibly consistent, 7 mixed, 4 unsupported interpretations and 4 unresolvable** on those small sampled references. No field was called definitively contradicted merely because a property could not be seen. In particular, model speculation about interpersonal confrontation, social gathering, a glass of water or a red pocket square cannot be promoted to screenplay fact from these pictures.

See [sampling limitations and decision protocol](SAMPLED-STILLS-VLM-CLAIM-TRIAGE.md), [source-hash-only numeric triage](research/qwen-two-pilot-sampled-stills-numeric-triage-2026-10-25.json) and the [executable sampled-frame consistency gate](tools/triage_video_model_sampled_stills.py). The richer field-by-field private review remains **outside Git**. **No original moving-video review has yet accepted any of these twenty fields, no episode's visual event recall has been measured, and 0/193 independently AV-certified complete episodes remains the archival state.** The next concrete editorial task is direct film/video-and-audio review at both precise offsets, with real source-time/claim corrections, not automatic insertion of Qwen prose.

## First two source-verified, original-series Qwen visual-language trials (2026-10-25)

**Real original audiovisual source milestone, machine-proposed only:** [trusted original-video Actions run #40225712304](https://github.com/gamesbyian/general-purpose/actions/runs/40225712304) downloaded each **owner-original AVI exactly once**, verified the known original episode SHA-256/duration, used the [source-calibrated grayscale candidate-selector fix #405](https://github.com/gamesbyian/general-purpose/pull/405), and completed **actual local Qwen3-VL-2B-Instruct inference** on one silent two-second original-picture excerpt per pilot. Both source-bound reports yielded **valid strict ten-field JSON**, **no original video/audio/stills were committed or uploaded**, and both machine descriptions remain **unreviewed/unaccepted**. No actor, voice, scene, original transcript cue time or screenplay has been certified by these model calls.

- **S01E01, 77–79 seconds:** chosen from three 5fps/160×90 low-resolution candidate-change checks, model load **28.796s**, inference **159.346s**, total model tool **188.598s** (not GitHub runner bootstrap). Original full video SHA matched the pinned source. Visible model claims concern a uniformed man and woman in a room with bookshelves; psychological “confrontation” interpretation and exact room identity are speculative and must not be pasted into a screenplay unreviewed.
- **S09E19, 812–814 seconds:** selected in one low-resolution candidate check, model load **53.743s**, inference **96.293s**, total tool **150.842s**. Original full video SHA matched the pinned source. Visible model claims concern a seated formally dressed man with background people; social-gathering/conversation motives or precise props remain to be checked against the actual moving original source.

**Durable machine-readable numbers with zero stage prose:** [first two-pilot Qwen provenance and timings](research/first-original-qwen-two-pilot-source-safe-metrics-2026-10-25.json), preserving original AVI SHA, private model-report digest, immutable model revision, exact video offsets, selection counts and source/model timings. Full **unreviewed prose** exists only in seven-day private GitHub Action artifacts; use [single-pass deferred review-packet workflow #406](https://github.com/gamesbyian/general-purpose/pull/406) and [original-video reviewer acceptance rules](VISUAL-STAGE-EDITORIAL-REVIEW.md) for future runs. This very small two-clip success does **not** establish useful physical-comedy coverage, model accuracy, full-episode throughput or the 30-minute/fleet-p95 target. **0/193 complete original-film-independent audiovisual episode certifications** remains the truthful release status.

## Current Night Court pilot quality and visual-model status (2026-10-25)

**Current pilot deliverables (supersede older version-3 and 453/751 counts below):** [S01E01 complete-dialogue v5 filmed-staging working manuscript](seasons/S01/S01E01/derived/additional-original-film-staged-reader-v5/screenplay-extra-observed-business.md) preserves **336 original timed SRT cues / 404 source speaking units**, with **306 provisional named and 98 unknown**. [S09E19 complete-dialogue v5 filmed-staging working manuscript](seasons/S09/S09E19/derived/additional-original-film-staged-reader-v5/screenplay-extra-observed-business.md) preserves **347 original *untimed* dialogue paragraphs/speaking units**, with **181 provisional named and 166 unknown**. The [canonical unit ledger](catalog/current-night-court-original-speaking-unit-coverage.json) reports **487/751 (64.8%) provisionally attributed and 264 remaining unknown**. Six directly inspected additional original-video action passages inform the v5 stage readings, including explicit refusal to invent anticipated gags not visible in the actual movie. **Zero of 193 episodes are completely independently source-AV certified**; provisional names are not voice authentication.

**Headless visual understanding, now executable in synthetic CI:** the local [video model runner](tools/run_headless_video_description.py), [shot detector comparator](tools/compare_shot_detectors.py), [original-video review bridge](tools/review_video_stage_directions.py), [independently labeled event-truth scorecard](tools/score_video_description_quality.py) and [paired editorial-yield/runtimes scorecard](tools/compare_visual_review_yield.py) form a testable chain. The two complementary scorecards deliberately separate **hallucinated/missed visual events** from **reviewer-usable screenplay stage directions**. New source-reviews and accepted stage prose still require real original-film inspection.

**Actual source-free model performance:** real SmolVLM2-500M weights loaded and inferred on a procedural 2-second no-person film in trusted bounded GitHub Actions. A 256-token control [#388](https://github.com/gamesbyian/general-purpose/pull/388) hallucinated a suited person/window and failed strict structured-output parsing; another 64-token [one-shot #389](https://github.com/gamesbyian/general-purpose/pull/389) recorded 29.669s model load, 13.121s inference and 43.019s total tool time, also without valid structured JSON. **Do not automatically use the 500M model for factual physical-business stage directions.** **Qwen3-VL-2B real CPU synthetic inference also succeeded:** [Actions #40169276648](https://github.com/gamesbyian/general-purpose/actions/runs/40169276648) loaded the immutable 2B revision and measured 28.157s model load, 87.837s inference for 1.5 seconds of procedural picture at 64 generated tokens, and 116.215s total tool wall time; its output did not pass the ten-field JSON parser. This establishes technical CPU compatibility, **not** source-video visual accuracy or an acceptable 193-episode processing speed. A subsequent **256-token Qwen CPU synthetic test** [#395](https://github.com/gamesbyian/general-purpose/pull/395) successfully returned **valid 10-field JSON**, including correctly saying no people were visible in the person-free test pattern, with 27.881s model load, 152.833s inference and 180.962s total processing; however its proposed interpretation of a broadcasting malfunction was unsupported. See the [source-free result ledger](research/qwen3vl2b-256-token-synthetic-control-2026-10-25.json). **Structured output works, but source-reviewed stage correctness and 193-episode throughput remain open.** See [video model quality evaluation](VISUAL-MODEL-QUALITY-SCORECARD.md), [review-yield comparison](VISUAL-REVIEW-YIELD-SCORECARD.md) and [CPU model runtime handoff](MODEL-RUNTIME-SMOKE.md). The first real two-pilot stronger-model microclip run has now completed (see top); the next highest-value gate is independent **original moving video** review of those two concrete reports and accepted/corrected stage notes, not another complete transcription pass.

## Executable headless video/shot benchmark foundations (2026-10-24)

Two new **synthetic-CI-accepted** engineering lanes are now on `main`, coordinated under [AV throughput and evidence issue #302](https://github.com/gamesbyian/general-purpose/issues/302):

- [PR #376](https://github.com/gamesbyian/general-purpose/pull/376) delivered [`tools/run_headless_video_description.py`](tools/run_headless_video_description.py) and a synthetic-video CI suite. It ingests the project's existing multi-goal review packets; verifies original local video SHA/duration; cuts bounded **temporary, silent** original-source video windows; and has optional local SmolVLM2-500M and Qwen3-VL-2B inference adapters with immutable model revision pins. Any output is a **machine-proposed, independently unaccepted** visible-action/shot/setting/prop/stage-direction candidate.
- [PR #380](https://github.com/gamesbyian/general-purpose/pull/380) delivered [`tools/compare_shot_detectors.py`](tools/compare_shot_detectors.py) with source-verified comparison of the existing FFmpeg candidate cuts against PySceneDetect 0.7.2. Its synthetic video CI confirmed two hard cuts at 2s/4s and rejects bad hashes. Detector frame times remain **nominal** until independently source-PTS checked; cut detection cannot by itself identify dramatic scenes.

Both tools work headlessly on approved locally accessible media, **do not fetch the owner's FTP files or require any privileged CI secrets**, and leave original dialogue and publication gates intact. **Historical 2026-10-24 baseline:** at that point neither original pilot AVI had been run through these new detectors/models. As of 2026-10-25, both source-video Qwen micro-pilot inferences have now run successfully (see the first section above), but their **actual visual accuracy, stage direction acceptance and performance advantage are still unestablished**.

Start with the [headless video benchmark and execution quickstart](HEADLESS-VIDEO-DESCRIPTION-BENCHMARK.md), [PySceneDetect benchmark quickstart](SHOT-DETECTOR-IMPLEMENTATION-2026-10-24.md) and [broader tooling/workflow audit](MODERN-TOOLING-AND-WORKFLOW-REVIEW-2026-10-24.md). Reuse the latest original picture source from [physical-comedy capture #370/#371](https://github.com/gamesbyian/general-purpose/pull/370) instead of duplicate owner-media downloads. Next acceptance gate is **real two-pilot footage, source-attested shot truth, measured visual model inference and source-video-reviewed stage directions**.

## Current episode-credited screenplay readers and cast evidence (2026-10-24)

**The working scripts have advanced beyond the last clean-reader release:**

- [**Latest S01E01: All You Need Is Love, credited court-case screenplay**](seasons/S01/S01E01/derived/cast-courtroom-reading-screenplay-v3/screenplay-courtroom-cast.md), [exact source dialogue/role index](seasons/S01/S01E01/derived/cast-courtroom-reading-screenplay-v3/courtroom-source-index.json). **336/336 original timed subtitle cues, 404 speaking units, 306 provisional named blocks, 98 still unknown.** Includes 17 previously reviewed original-video static setting notes and two 5fps bounded original-video physical-action passages.
- [**Latest S09E19: P.S. Do I Know You?, credited pen-pal/campaign screenplay**](seasons/S09/S09E19/derived/cast-continuity-reading-screenplay-v3/screenplay-cast-continuity.md), [exact source dialogue/role index](seasons/S09/S09E19/derived/cast-continuity-reading-screenplay-v3/continuity-source-index.json). **347/347 original UNTIMED paragraphs, 347 original speaking units, 147 provisional named blocks, 200 still unknown.** Original video scene observations remain separate from the script's unverified paragraph times. The separate S09 [source video-to-dialogue search map](seasons/S09/S09E19/derived/source-coarse-picture-dialogue-review-v1/picture-to-dialogue-search.md) remains a non-authoritative editorial guide.

Both are substantially more legible full-original-dialogue working manuscripts. **Combined provisional named speaking blocks: 453/751 (60.3%); 298 blocks still unidentified**. This is not verified voice recognition or an overall percent of production completion. **0/193 original-series episodes are yet completely editor-ready or independently audio+video-certified**. The source captions remain authoritative and were not rewritten by ASR.

Episode-credited research [cast ledger](research/pilot-episode-credited-cast-v1.json) is grounded in [S01 pilot IMDb credits](https://www.imdb.com/title/tt0660578/fullcredits/), [S09 IMDb credits](https://www.imdb.com/title/tt0660693/), [TVmaze pilot guests](https://www.tvmaze.com/episodes/134243/night-court-1x01-all-you-need-is-love), and [TVmaze's credited Alex character](https://www.tvmaze.com/characters/846493/night-court-alex). S01's court-case speakers include separately credited Phil and Louise Kerr, Carla Bouvier, and Hacksaw Hammond. **Critically, S09 credits James McDonnell as Alex and Alex Henteloff as the distinct character 'The Guy'.** We explicitly abstain from labeling ambiguous stand-in dialogue as a named person from still images. Actor/character identity was never inferred from photographs; the original images have been used for observable costume/action/setting research only.

Work merged this pass: [PR #351](https://github.com/gamesbyian/general-purpose/pull/351) creates the actor/episode-role references and first 82+18 cast-context proposals; trusted derived manuscripts [PR #353](https://github.com/gamesbyian/general-purpose/pull/353) delivered the real scripts. [PR #354](https://github.com/gamesbyian/general-purpose/pull/354) and [PR #356](https://github.com/gamesbyian/general-purpose/pull/356) added and delivered 106 more S01 original courtroom/case guest voice headings. [PR #357](https://github.com/gamesbyian/general-purpose/pull/357) and [PR #359](https://github.com/gamesbyian/general-purpose/pull/359) added and delivered 53 more S09 regular/guest role headings. All source-only CI and trusted derivation jobs passed. One-shot trigger PRs were closed unmerged. No full-episode original AVI/ASR rerun was needed.

**Highest-impact remaining actual screenplay editing:** original soundtrack spot-checks to distinguish voices behind the 298 unknown source dialogue units and challenge provisional context labels; additional genuinely observed shot/scene/motion coverage, especially physical comedy between sparse frames; and S09 untimed source text-to-action review with only independently supported alignment. The strict archival acceptance status stays separate from delivering more useful working scripts.

## Current screenplay deliverables and live editorial quality

**Start here:** [CURRENT-PRACTICAL-SCREENPLAY-DELIVERY.md](CURRENT-PRACTICAL-SCREENPLAY-DELIVERY.md).
The newest original-source-caption reading editions are S01E01 v6
(inline original timed picture stage notes) and S09E19 v5
(untimed dialogue, observed video in separate chronological appendix).
Both contain complete *held-source* dialogue, 195 provisional named
units combined, and 556 still anonymous units. The project currently
has **two source-dialogue complete working drafts, zero editor-ready
full visual scripts and zero independently original-AV-certified
screenplays**. S09 has a 15-pointer/3-abstention picture-to-source-
paragraph reviewer map, not invented subtitle timestamps.

## October 24: full-source pilot screenplays revised with real motion and contextual roles

**Five distinct product stages exist. Do not conflate their counters.**
The held dialogue source archive still has 193/193 episodes, and the
source-only initial dialogue scaffolds remain 193/193. Actual generated
and checked-in working scripts exist for the two current pilots, not
yet the rest of the series.

After source-only, scene-photo and caption-first draft improvements,
the original SHA-pinned source-video motion run
[#40139082891](https://github.com/gamesbyian/general-purpose/actions/runs/40139082891)
succeeded for **both** episodes, extracting **410 5fps original-picture
frames across four targeted windows totaling 82 seconds**. The
source image sequences were directly inspected, and source-supported
physical-business writing was recorded with exact original AVI, source
text, JPEG/contact-sheet, evidence-report and temporary artifact hashes:
[S01 original motion observation ledger](seasons/S01/S01E01/derived/physical-motion-original-v1/observations.json)
and [S09 original motion observation ledger](seasons/S09/S09E19/derived/physical-motion-original-v1/observations.json).
The original image artifacts are temporary/private. This is a bounded
*picture-only* performance review, not synchronized audio/listening or
complete source-video examination.

The tested physical-action renderer and ledgers merged through
[PR #326](https://github.com/gamesbyian/general-purpose/pull/326);
the real generated screenplay files from trusted source-only run
[#40140316952](https://github.com/gamesbyian/general-purpose/actions/runs/40140316952)
passed source-rebuild CI and merged in
[PR #328](https://github.com/gamesbyian/general-purpose/pull/328).
The script now describes observed office-window gesturing, a near-empty
courtroom/bench reveal, a floor-level sparking and smoke effect with
people sheltering behind courtroom furniture, and the restaurant
couple's close dancing and separation. These are grounded in the
original 5fps samples. The exact staging and causal timing still need
full motion-with-sound review before independent certification.

To avoid leaving every line anonymous, editorial reading of captions
produced **38 clearly provisional textual speaker proposals**: 18 S01
and 20 S09, documented with exact source cue, source phrase and
contextual evidence references, not face recognition or unreviewed
ASR. The editor and ledgers merged through
[PR #329](https://github.com/gamesbyian/general-purpose/pull/329);
both resulting v4 screenplay documents were compiled by trusted
source-only run
[#40140734663](https://github.com/gamesbyian/general-purpose/actions/runs/40140734663)
and merged in
[PR #331](https://github.com/gamesbyian/general-purpose/pull/331):

- [**Latest S01E01 working screenplay: 336/336 original timed cues, real source motion action and 18 added provisional contextual speakers**](seasons/S01/S01E01/derived/caption-first-speaker-context-v4/screenplay-dialogue-context-edit.md).
- [**Latest S09E19 working screenplay: 347/347 original untimed paragraphs, real source motion action and 20 added provisional contextual speakers**](seasons/S09/S09E19/derived/caption-first-speaker-context-v4/screenplay-dialogue-context-edit.md).

Their exact source manifests and editorial cue-proposal ledgers reside
beside the script output files. The earlier complete v1/v2/v3 drafts
remain untouched for comparison. Original wording was never rewritten
by ASR. The S09 original paragraphs were never given fictional times.

**Status: 2 complete original-held-dialogue scene-and-action-enriched
working pilot scripts; 38 additional provisional source-text speaker
labels; 0 full editor-ready screenplays; 0 independently whole-original-AV
certified screenplays.** The largest remaining bottleneck is not another
ASR contest, but source-video-plus-sound scene observation and
resolving dialogue roles throughout the *rest* of each episode.
Do not report 38 proposed labels as verified, or a small set of
motion clips as complete physical-comedy coverage. Next engineering
should deliver more finished scenes rather than only archival metadata.

## Actual original-video scene editing delivered, 2026-10-24

**This is screenplay content progress, not merely a pipeline benchmark.**

[PR #315](https://github.com/gamesbyian/general-purpose/pull/315)
implemented source-bound original AVI whole-episode image overview;
trusted original-video [run #40137223223](https://github.com/gamesbyian/general-purpose/actions/runs/40137223223)
completed **both** pilot sources. This produced **80** uniformly source-time-spaced
S01E01 frames and **73** S09E19 frames across each complete original
episode. Private temporary seven-day contact-sheet artifacts are
**#12577216339** (S01) and **#12578036143** (S09), with exact AVI,
frame and artifact ZIP hashes preserved in the repository's derived
source-photo evidence ledgers. No AVI, audio, model weights, original
images or speaker voiceprints were committed.

[PR #317](https://github.com/gamesbyian/general-purpose/pull/317)
preserved **33 actual directly visually inspected image observations**:
17 S01E01 and 16 S09E19, individually referenced to original-frame
SHA-256. Room transitions and visible stage *states* now cover the
book-lined office, courtroom/bench, nighttime bridge insert, diner,
court-office and restaurant/bar instead of blanket unspecified scene
settings. The preview images helped locate possible physical-business
research, but 18-second gaps cannot prove all fast gags, precise cuts,
or observed voice identity.

Trusted owner original-caption source [run #40138198200](https://github.com/gamesbyian/general-purpose/actions/runs/40138198200)
produced two new, separately regenerated source-dialogue-complete
**scene-edit v2 screenplays**. They passed CI and were merged through
[PR #320](https://github.com/gamesbyian/general-purpose/pull/320):

- [S01E01 complete dialogue with 17 inline original-image stage notes](seasons/S01/S01E01/derived/caption-first-scene-edit-v2/screenplay-scene-edit.md)
  and [source manifest](seasons/S01/S01E01/derived/caption-first-scene-edit-v2/scene-edit-manifest.json).
  All **336 SRT caption cues** are preserved, and two speaking turns
  have **provisional self-identification from dialogue**, rather than
  image-based actor naming.
- [S09E19 complete original untimed dialogue with 16 original-image notes and eight textual story beats](seasons/S09/S09E19/derived/caption-first-scene-edit-v2/screenplay-scene-edit.md)
  and [source manifest](seasons/S09/S09E19/derived/caption-first-scene-edit-v2/scene-edit-manifest.json).
  All **347 untimed transcript paragraphs** remain untimed. The
  image chronology is explicitly separate from proposed source-text
  story-breaks; one self-identifying name remains a claim by a
  speaking voice, not proof of character identity.

[PR #321](https://github.com/gamesbyian/general-purpose/pull/321)
then added source-bounded, original-AVI **5fps dense physical gag**
candidate capture for two valuable windows per episode. First owner
run encountered a decoder failure (not accepted motion evidence).
[PR #323](https://github.com/gamesbyian/general-purpose/pull/323)
added bounded single-thread decoding and actionable error diagnostics;
a separate owner-only retry was dispatched. Do not mark that second
capture or any continuous gag as complete before its real artifact
and direct review are confirmed.

**Honest measurable current state:**
- 193/193 source-only original episode text scaffolds.
- **2/193** complete held-source-dialogue *scene-enriched drafts*,
  containing 33 new genuine photo observations and eight S09
  caption-textual scene beats.
- **0/193** truly editor-ready full visual/action/speaker screenplays.
- **0/193** independently whole-original-video-certified archival scripts.

The remaining major workload is assigning a comprehensible speaker
to most dialogue, actually watching source motion to describe physical
gags, finding precise scene divisions and reconnecting S09 untimed
paragraphs to the picture. None of these should be blocked on
running two competing full-episode speech recognizers again by
default. Priority is source-grounded *writing and editing* now.

## Actual complete held-dialogue pilot draft delivery, October 24

The *code* from [PR #310](https://github.com/gamesbyian/general-purpose/pull/310),
its output correction [PR #312](https://github.com/gamesbyian/general-purpose/pull/312),
and the **two generated, source-reconciled artifacts** from
[PR #313](https://github.com/gamesbyian/general-purpose/pull/313) are now
merged. This is a concrete draft-production advance beyond research and
scaffolding.

- [S01E01 working screenplay](seasons/S01/S01E01/derived/caption-first-working-draft-v1/screenplay-draft.md)
  reproduces all **336 original timecoded cues**, forming **404**
  caption-typographic reading units, with six sampled source-video
  observations and a targeted list of **16** ASR/caption mismatch cases
  plus **eight** distributed checks. Dialogue defaults to the original
  caption. No unknown dialogue is silently overwritten by ASR.
- [S09E19 working screenplay](seasons/S09/S09E19/derived/caption-first-working-draft-v1/screenplay-draft.md)
  reproduces all **347 untimed original source paragraphs**; it
  includes six sampled picture notes scoped to the 15:00–15:25
  candidate AV passage, while never fabricating original paragraph
  times. Eight distributed source-paragraph controls are pending.
- Both drafts have `draft-manifest.json` and `targeted-review.json`.
  The exact-SHA regeneration test passes; both original source
  witnesses remain untouched.

**New measured draft status:** **2/193 complete-held-source-dialogue
working drafts generated**, **0/193 editor-ready full-scene
screenplays**, **0/193 independently AV-certified screenplays**.
The original 193/193 source-only scaffolds still exist independently.
These two initial drafts are currently *not* products that fully
reconstruct action: substantial whole-episode setting, scene,
speaker and physical-comedy work remains. The next genuine quality
milestone is a human-usable screenplay with characters and key gags,
not a new multi-model agreement artifact. We should use captions
by default and selectively investigate disagreements rather than
repeating whole-audio transcription.

## Fast caption-first working screenplay drafts

The [working-screenplay standard](CAPTION-FIRST-WORKING-SCREENPLAY-POLICY.md)
now prioritizes producing usable **complete-held-dialogue** script drafts
before exhaustive source certification. The first two pilot generators
are `tools/build_caption_first_working_drafts.py --episode S01E01` and
`--episode S09E19`. Original subtitle text is authoritative for the
working draft; ASR flags exceptions without silently rewriting words.
Observed source-frame descriptions supplement bounded passages. The
stricter archival AV publication gate remains separate and unchanged.
These drafts do **not yet** reconstruct all scenes or key physical
comedy and are not labeled editor-ready until that substantive work
is performed.

# Night Court: the original NBC series (1984–1992)

**Independent research archive**, inside the private `gamesbyian/general-purpose` repository. Scope excludes the 2023 revival. The purpose is durable, provenance-aware research and a future LLM-readable knowledge base about the original program, its fictional and production history, comedic conventions, cultural moment, and fandom.

## Current acquisition acceptance, October 23, 2026

**Dialogue source presence: 193/193 episodes, with no remaining unheld episode IDs.** The authoritative, automatically regenerated records are [dialogue coverage](catalog/dialogue-coverage.json), [dialogue source queue](catalog/dialogue-source-queue.json), [dialogue quality](catalog/dialogue-quality.json) and [archive status](catalog/archive-status.json). Historical sections below record earlier acquisition checkpoints and are *not* current coverage statements.

Season-by-season held episodes: **S01 13/13, S02 22/22, S03 22/22, S04 22/22, S05 22/22, S06 22/22, S07 24/24, S08 24/24, S09 22/22.** All except S09E19 have original timed English caption sources. S09E19 holds 347 original display paragraphs (approximately 2,337 words) as **untimed text**, not an SRT and not a confirmed full script.

The automated quality report has **56 witnesses with at least one heuristic review flag**, and zero independent AV-completeness certifications. Such flags may reflect legitimate overlaps or silent scenes. No cross-episode identical long-text collisions were detected. The remaining work is edition-aligned audio/video QA, overlap and cue-gap review, speaker attribution, scene boundaries and evidence-linked visual actions, not wholesale rediscovery of episode captions. See [S09E19 source acquisition](research/s09e19-final-dialogue-acquisition.json) for the sole untimed source and [the source-to-script factory plan](AV-SCRIPT-FACTORY-PLAN.md) for the next pipeline.

## Anonymous voice-similarity evidence

The S01E01 [anonymous vocal comparison](seasons/S01/S01E01/derived/scene-review-v3/anonymous-voice-similarity.md) has now processed real source audio with a separate speaker-embedding model. Seven candidate spoken intervals yielded 21 uncalibrated acoustic similarity scores; three short utterances abstained. The model executed without FTP credentials and **retained no embeddings or original audio**. These comparisons do not identify Harry, Dan, Bull or any other character, determine reliable voice clusters, or establish acting emotion. Named dialogue remains an audiovisual review task.

## Production-script quality gates now in place

The S01E01 [editorial acceptance worklist](seasons/S01/S01E01/derived/editorial-review-v1/acceptance-worklist.md) identifies the **11 source speaking turns and six physical-action observations** that need direct audio/video review before a performance script can be accepted. [Reviewer decision template](seasons/S01/S01E01/derived/editorial-review-v1/review-decisions-template.json) enforces explicit evidence records and leaves all 17 tasks pending; it does not authenticate a reviewer or establish source truth automatically. Five additional [original-video subtitle drift samples](seasons/S01/S01E01/derived/source-sync-review-v1/drift-acceptance-triage.md) were recovered from a successful owner-triggered run and preserved with strict checks. Duplicate-caption ASR hallucinations mean **no episode-wide subtitle drift or offset is accepted**. See [current production workboard](AV-SCRIPT-PRODUCTION-WORKBOARD.md) for the remaining priorities.

## Second evidence-linked audiovisual script: S09E19

The only originally **untimed** held English dialogue witness, S09E19, now has genuine source-video research. The actual 22-minute AVI was SHA-256 fingerprinted; five independent 25-second audio windows produced 50 ASR speech candidates and **15 distinctive possible source-paragraph matches**, all retained separately from the unchanged 347 untimed source paragraphs. [S09E19 source timing review](seasons/S09/S09E19/derived/source-timing-review-v1/sparse-source-paragraph-review.md).

A separate 100-frame 4fps source-image pass documented six provisional physical/shot observations from the match-rich 15:00–15:25 interval, and [the first integrated S09E19 script excerpt](seasons/S09/S09E19/derived/scene-review-v1/source-linked-scene.md) renders the five lexical dialogue candidates alongside visible actions. **Speaker identities, actual source paragraph timestamps, expressive delivery, continuous-motion action timing and full episode completeness remain unverified.** [Visual source notes](seasons/S09/S09E19/derived/visual-review-v1/scene-visual-observations.md).

## First multimodal script evidence: S01E01 pilot

The project's first source-grounded [**integrated script excerpt**](seasons/S01/S01E01/derived/scene-review-v3/scene-script-v3.md) now combines genuine S01E01 spoken-caption witnesses with reviewed static and temporally ordered visual evidence from the original SHA-fingerprinted AVI, including a desk-telephone action. The evidence covers **01:00–01:30 only**, not a full episode. Read the [machine-readable claim/evidence map](seasons/S01/S01E01/derived/scene-review-v3/scene-evidence-map.json) for provenance and limits.

The [utterance acoustic report](seasons/S01/S01E01/derived/scene-review-v3/utterance-acoustic-review.md) records actual mixed-TV-audio pitch and intensity candidates for ten ASR-proposed speech spans. It does **not** validate speaker identity, expressive emotion, sarcasm, independent word-level forced alignment, continuous-video completeness or a finished production screenplay. These missing gates drive the [AV script factory plan](AV-SCRIPT-FACTORY-PLAN.md) and [S01E01 acceptance handoff](S01E01-AV-PILOT-HANDOFF.md).

## All-episode reading-script scaffolds

Every original episode now has a [source-only reading script](seasons/S01/S01E01/derived/source-script-scaffold-v1.md) in its `derived/` directory, built from the held caption witness with original source cues and an explicit **UNIDENTIFIED VOICE** label wherever the source is unattributed. [PR #156](https://github.com/gamesbyian/general-purpose/pull/156) passed all-193 CI, producing 70,804 original cues, 72,733 candidate dialogue units and 1,173 caption-gap blocks across 193 scripts. [See complete scaffold coverage](catalog/source-script-scaffold-coverage.json). These are **not** claimed to be actual production screenplays: they have no verified settings, speaker assignments, physical action, vocal-performance interpretation or episode-wide AV completeness. The first actual multimodal scene example is [S01E01 scene v3](seasons/S01/S01E01/derived/scene-review-v3/scene-script-v3.md).

## Actually held (23 October 2026)

- **193/193** original-series episode records: `seasons/Sxx/SxxEyy/episode.json`, spanning 9 seasons (13, 22, 22, 22, 22, 22, 24, 24, 22).
- **193/193** titles, dates, directors, writer-credit lines and production codes, reconciled from TVmaze and Wikipedia. Source-specific aliases are retained; composite broadcasts and ambiguous numbering are flagged.
- **193/193 CC BY-SA-licensed, episode-specific encyclopedia synopsis/capsule files**: `seasons/Sxx/SxxEyy/authorized-text/wikipedia-episode-capsule.wikitext`, each with `sources/wikipedia-capsule.provenance.json`. A five-entry discrepancy between Wikipedia's 188 episode-list rows and 193 actual episode parts is explained by paired broadcasts, whose shared summaries are annotated.
- Full MediaWiki source of **two openly licensed articles**, `research/licensed-wiki/Night-Court.wikitext` and `research/licensed-wiki/List-of-Night-Court-episodes.wikitext`, each with a Wikipedia revision permalink, attribution and license manifest.
- **1,825 provenance-bearing episode source references**, including many repeated series-index pointers. The number is *not* an independently recovered document count.
- Episode-level bibliography plus original analyst-created first-pass fact sheets for S01E01 and S02E10; fandom observation examples, source inventory and canonical knowledge-model design.

**Now held:** **193/193 original-series episodes have a versioned English dialogue witness**: 192 timecoded SRTs (35 owner-supplied for S01–S02, plus 157 acquired original-series online sources) and one source-page-derived **untimed** transcript (S09E19). Every witness has source provenance and the canonical episode dialogue index. **Not established:** independent audiovisual completeness, speaker identity, original production screenplays, or publication/reuse rights for externally hosted scripts. Original caption downloads, held dialogue witnesses, external research leads, and AV-verified complete transcripts remain distinct evidence types.

## Repository organization

```text
Night Court/
  README.md                   archive status, architecture and collection contract
  SOURCES.md                  source coverage and verification tiers
  KNOWLEDGE-MODEL.md          schema and future cross-episode analytical matrices
  catalog/
    index.json                ordered 193 episode paths and series-level metadata
    episodes.jsonl            query-friendly factual catalog
  seasons/
    S01/S01E01/
      episode.json            episode ID, credits, source links and holdings
      authorized-text/
        wikipedia-episode-capsule.wikitext
      sources/
        wikipedia-capsule.provenance.json
    ...
    S09/S09E22/
  research/
    licensed-wiki/            CC BY-SA original article revisions and attribution
    case-studies/             original preliminary scene/narrative analyses
    fandom-observations.md   time-stamped, qualified reception examples
    collection-runs.md        harvester instructions
  tools/
    refresh_episode_metadata.py
    discover_transcript_urls.py
    collect_open_wiki.py
    enrich_wikipedia_credits.py
    validate.py
.github/workflows/night-court-harvest.yml
```

## Sources discovered

- Forever Dreaming: **57 full-dialogue indexed topics**, all 57 episodes of seasons 1–3. Direct post URLs are saved where independently confirmed; others retain the index link until verified.
- Springfield! Springfield!: **47 indexed scripts** (13 S01; 12 S02; 22 S03). Inferred direct URLs are explicitly marked as **unverified**.
- Subtitle Cat: verified caption-display pages for S04E01 and S09E22.
- SUBDL: original-series landing page with season filters, but complete per-episode availability remains **unverified**.
- Wikipedia, TVmaze, TheTVDB, IMDb, TV Guide, fan wikis and fandom threads: season-level and episode-level factual/reception discovery pointers.

`SOURCES.md` contains the actual URLs, and each episode has a structured source list. **An index link is not equivalent to an archived source document.**

## Collection and synthesis rules

1. Distinguish verified page, indexed episode listing, constructed URL, and physically stored file. Reflect the difference in machine-readable `episode_sources[].level`, `verified`, and `holdings`.
2. For each retained version save URL, author/publisher, revision, license/reuse basis, retrieval method, timestamp, hash if held, language, source-specific episode identifiers, and mapping confidence.
3. Preserve multiple captions, scripts, reviews, versions and contradictions independently. Prefer source-level evidence over any single synopsis and keep uncertain assignments explicit.
4. Separate fictional character and event graphs from actor/production/industry information; label narrative interpretation, joke taxonomy and reception claims as interpretations with supporting evidence.
5. Analyze fandom by era and community (contemporary criticism, syndicated reruns, later nostalgia, comparison with the revival). Never treat a few comments as representative consensus.
6. Use the existing project-level `KNOWLEDGE-MODEL.md` before generating canonical artifacts. Scene, character, comedy, affect, production and cultural-context matrices belong in a later evidence-led pass, not a fabricated transcription.
7. Do not modify independent repository tools or sensitive features such as the Shaw gateway.

## Operational controls

The dedicated GitHub Actions workflow runs a **single bounded 12-minute job**, validates records, retrieves TVmaze facts, discovers only transcript *links* (respecting robots policy), collects two explicitly CC BY-SA Wikipedia wikitext snapshots with attribution, imports 193 sets of production metadata and licensed capsules, then commits only `Night Court/` on its designated research branch. Manual invocation is also available. These stages are rerunnable and leave existing data intact on most individual-source failures.

Locally run:

```sh
python "Night Court/tools/validate.py"
python "Night Court/tools/refresh_episode_metadata.py"
python "Night Court/tools/discover_transcript_urls.py"
python "Night Court/tools/collect_open_wiki.py"
python "Night Court/tools/enrich_wikipedia_credits.py"
python "Night Court/tools/validate.py"
```

## Expanded evidence indexing and guest credits, 23 October 2026

The second bounded GitHub Actions pipeline (`.github/workflows/night-court-knowledge.yml`) has populated the episode retrieval corpus and new contextual sources:

- **193/193 evidence dossiers** (`seasons/Sxx/SxxEyy/derived/evidence-dossier.json`) and human-readable reading notes (`derived/reading-note.md`) with explicit links to the original licensed Wikipedia source and revision.
- **342 source-authored synopsis statements**, with character offsets and per-episode `annotations/synopsis-statements.jsonl` files, available together as `catalog/source-statements.jsonl`. They are not verified events or scene transcripts.
- **440 character-name mention relationships** and **255 topic keyword signals**, queryable through the `catalog/character-mentions.jsonl`, `catalog/theme-cues.jsonl`, `catalog/episode-knowledge.jsonl` and `tools/query_corpus.py` files. Labels expressly warn that text mention does not prove appearance.
- **1,210 TVmaze episode guest actor-character credit edges**, covering all 193 episodes; a series-level main cast of **14 credited relationships**, with **797 distinct credited people** and **974 distinct credited character IDs** overall. See `catalog/cast-relationship-graph.json`, `catalog/guestcast-edges.jsonl` and `catalog/tvmaze-guestcast-coverage.json`. These are *credits*, not direct evidence of on-screen appearances.
- **19 additional Creative Commons-licensed Wikipedia articles**, mostly bios of series cast and creators, stored with exact revision, SHA-256 and attribution at `research/licensed-wiki/context/`.
- A cautious Fandom collector checked access and recorded **`blocked_by_robots`**. No Fandom wiki articles were copied. See `research/fandom-wiki/collection-status.json`.
- `catalog/holdings-coverage.json` and `catalog/holdings-coverage.csv` audit all 193 episode directories. **Full scripts held: 0. Caption tracks held: 0. Full critic/reviewer articles held: 0.** Links and source discovery are not conflated with preserved content.

The indexed guest cast is unusually useful: it supplies specific credit links between actors, recurring or one-off roles and episodes, including cast names not present in the short encyclopedia synopses. Separately, the source-statement ledger makes it possible to inspect exactly why a lexical search result was returned.

**Try the local retrieval CLI** from the repository root:

```sh
python "Night Court/tools/query_corpus.py" --character harry-stone --limit 5
python "Night Court/tools/query_corpus.py" --actor "Rita Taggart"
python "Night Court/tools/query_corpus.py" --theme politics-and-government --limit 20
python "Night Court/tools/query_corpus.py" --director "Jeff Melman" --season 4
```

See [RESEARCH-ROADMAP.md](RESEARCH-ROADMAP.md) for the next source-acquisition passes, licensing requirements, evidence-quality gates, canonicalization plan and handoff boundaries.

Canonical scene, event, mood, joke, fandom and period-context knowledge remains **unbuilt**. The current corpus is a large, testable evidence and retrieval substrate, not an allegedly transcript-complete or eyewitness-validated reconstruction.


## Subtitle location follow-up, October 23, 2026

A dedicated research lane added **21 individually verified episode-specific Subtitle Cat caption-display URLs** to the record set, including examples in seasons 1, 2, 3, 4 and 9. The per-episode source records and `catalog/subtitlecat-discovery.json` preserve each URL and distinguish an externally readable caption display from a held SRT. The audited total is now **1,672 source pointers**; exactly **21 episodes** have a located Subtitle Cat page, while **0 complete subtitle files** are held in the repository.

The site's robots policy blocked automated search/upload-index collection, so the metadata harvester saved only previously verified episode page URLs. It did not fetch subtitle text, invent search coverage, or bypass the site's access restriction.

Additional **legal streaming/caption witnesses** discovered for the original are [Apple TV's original-series listing](https://tv.apple.com/ca/show/night-court/umc.cmc.3v8igla11dgg4chywljv2og89), showing English (US) CC, and [Prime Video season-one episode listings](https://www.primevideo.com/detail/0JKQMQRYLQ7AQRRSNOGZQAN1PB). These are distributor/catalogue references, not proof of any locally saved caption or separate episode synopsis text.


## Original broadcast and reception measurements

The new `catalog/broadcast-context.json` and `broadcast-context.csv` reconstruct season-level U.S. television-series rankings, annual season household ratings, episode household rating/share and later reported U.S. viewer counts from the revision-pinned Wikipedia episode list. Its `research/broadcast-context.md` gives a short human-readable overview.

These fields **cannot all be compared directly**: household rating points, shares and viewers in millions have different denominators. Jointly broadcast multi-part episodes are not double-counted in the season summaries. This is historically useful audience evidence with secondary-source provenance, not a claim about why the comedy's popularity changed.


## Contemporary press and reception source provenance

`research/contemporary-press-bibliography.jsonl` now indexes **15 separately identified** press, industry, historic broadcasting, criticism and fandom sources, emphasizing two contemporaneous interviews with original producers and actors. `research/production-and-reception-claims.jsonl` holds **12 attributed analytical/production claims**, each with supporting source identifiers, confidence, boundaries and caveats. `research/press-evidence-brief.md` is a readable, original interpretive note; third-party full articles and reviews are *not* copied. Dates and original-series vs revival identity are explicit.

`research/source-conflicts.json` records **four significant interpretive or source disagreements**, including two different Season 1 ranking/rating values published in different Wikipedia revisions, the distinction between the May 13, 1992 story finale and May 31 last broadcast, and contradictory modern fan-ranking sources. Never resolve the season-one statistical discrepancy merely by preference for a more recent revision. The `night-court-press.yml` workflow validates source-link integrity and claim provenance.


## Immutable preservation of revision-pinned encyclopedia sources

All **21 currently held licensed Wikipedia source articles** (two original-series reference articles and 19 cast/production/context articles) now also have their own immutable copies in `research/licensed-wiki/revisions/` using a canonical article/revision-ID path. Each copy has a separate attribution/license manifest and SHA-256 digest. `catalog/wiki-revision-archive.json` indexes those **21 saved revisions**, not the entire upstream edit history.

Run `tools/preserve_wiki_revisions.py` both **before and after** future encyclopedia source refreshes, as now wired into the dedicated harvest and indexing workflows. Identical revision IDs with different bytes fail closed, while subsequent revisions accumulate without overwriting older held versions. This guards against upstream edits and disappearing pages beyond Git's commit history.


## Dialogue import is now operational

The repository includes a **source-preserving dialogue import pipeline** for materials supplied by the researcher: SRT, VTT and plain-text transcripts. See [DIALOGUE-INGESTION.md](DIALOGUE-INGESTION.md) for the local command, Android/GitHub upload workflow, edition/rights manifest, checksums, multiple-version handling and independent completeness QA. Import goes to `seasons/Sxx/SxxEyy/dialogue/versions/`; `catalog/dialogue-index.jsonl`, `catalog/dialogue-coverage.json` and `catalog/dialogue-coverage.csv` report genuinely held witnesses separately from external source pointers. Test fixtures are synthetic.

**Historical checkpoint (superseded): at this earlier stage, no actual full scripts or caption tracks had yet been imported. See the current acquisition acceptance above.** The tooling and GitHub Actions pipeline can preserve multiple full source witnesses once they are supplied. Each track's declared completeness is recorded, but only future audiovisual verification can establish whether it is genuinely episode-complete. No DRM circumvention or scraping is performed by the importer.

Research and private-copying exceptions may be relevant to legitimate user-held sources, subject to the circumstances. The archive retains an explicit rights/source declaration without claiming to make a definitive legal finding.


### Search and source-quality diagnostics

`tools/search_dialogue.py` provides source-attributed search over the *held* transcript/caption versions and the 193 licensed episode capsules. Search hits return cue timestamps, explicit speaker markers when present, edition and source checksum; a synopsis result is explicitly marked **not dialogue**. With no held dialogue, only synopsis search has results.

`tools/audit_dialogue_quality.py` produces SHA-tied per-version QC and `catalog/dialogue-quality.json` / CSV, including approximate counts, cue overlaps, suspect source gaps and flags requiring audiovisual review. These metrics do not prove completeness or missing dialogue. The existing GitHub Actions import workflow tests and regenerates them on each imported batch.


### Local-source episode media to dialogue

`tools/extract_local_media.py` adds a way to generate source-preserved SRT dialogue witnesses from **locally held, DRM-free episode containers**, using embedded text subtitle streams or opt-in offline faster-whisper speech recognition when captions are unavailable. It can inspect individual media, extract specific or all subtitle streams, and batch-process a folder of SxxEyy-labeled original-series videos. It requires explicit original-series and source/rights confirmation before importing, and keeps video/audio outside the repository. [Detailed commands and limitations](DIALOGUE-INGESTION.md). A separate narrow synthetic MKV workflow checks the end-to-end subtitle extraction path.

### Dialogue source acquisition priority matrix

`catalog/dialogue-source-queue.json`, CSV and Markdown now classify all 193 original episodes by direct dialogue link, index-only lead, unverified pattern or no episode-level lead. They rank episodes needing independent collection and preserve actual source URLs without misrepresenting linked pages as downloaded transcript text. S01E03 and S04E15 added as individually inspected Subtitle Cat pages (15 caption-page episodes total). Run `tools/build_dialogue_source_queue.py` after source inventories change; it also reconciles `catalog/archive-status.json` against the actual holdings audit.


### Bulk subtitle source packages

For up to 500 caption/transcript files at once, `tools/import_dialogue_bundle.py` accepts a single bounded ZIP plus one original-series provenance declaration. It maps every SxxEyy file to its episode directory, preserves originals and source fingerprints, and reruns the existing dialogue-search/quality infrastructure. The private GitHub Actions upload workflow imports ZIPs automatically. [Usage and safeguards](DIALOGUE-INGESTION.md).


### Multiple-dialogue-witness concordance

`tools/compare_dialogue_versions.py` compares each episode's separately held dialogue variants without naming any of them canonical. It preserves original edition/hash provenance, reports likely duplicate wording, subset overlap and divergent transcript passages, and warns about identical long text assigned to different episodes. The global file is `catalog/dialogue-variant-comparison.json`. As with the quality ledger, its value will grow when the first complete original-series dialogue witnesses are actually imported.

### Latest episode-specific caption discovery

The checked external Subtitle Cat inventory now contains **21 original-series episodes with 22 separately located caption page versions**, including new season-five, seven and eight examples. [Source locations and ranked gap queue](catalog/dialogue-source-queue.md) exposes a truthful status for all 193 episodes. The archive also maintains a quarantine list of two 2023-revival/misnumbered subtitle sources to prevent similarly numbered episodes from contaminating the original research corpus.

## Season-three caption source verification (23 October 2026)

A separately researched public [Subtitle Cat upload index](https://www.subtitlecat.com/list_page.php?from=1666800) identifies all **22** episodes of the original 1984–1992 series' third season, in a 9 May 2025 batch of English DVD-caption display pages. All 22 episode-specific page URLs were individually checked and saved in `research/season03-caption-page-locations.json`, and the corresponding episode source records were reconciled without storing the caption text itself.

The latest **193-episode acquisition queue** is now **44 episodes with direct external dialogue-page links, 19 with index-only pointers, and 130 without an episode-specific locator**. Across Subtitle Cat specifically, the archive records 40 episode IDs and 41 page variants. The **full locally held episode dialogue count remains zero**. See `catalog/dialogue-source-queue.json`, `catalog/holdings-coverage.json`, and `catalog/subtitlecat-discovery.json` for distinct denominators and source statuses.

## Later-season original-series caption listings (23 October 2026)

A dated [June 2025 Subtitle Cat upload cluster](https://www.subtitlecat.com/list_page.php?from=1710700) contains independently observed **105 original-series English subtitle *listings*** for seasons 5–9. These are mapped episode-by-episode in `research/later-season-2025-caption-upload-listings.json`, with the exact source-index page of each listing. The listing itself is not a verified individual caption display page and no caption text was copied.

The 193-episode acquisition queue now reports **44 episodes with direct external dialogue page URLs**, **121 with episode-labeled source-index coverage**, and just **28 without an episode-specific dialogue lead**. All 22 episodes of seasons 5 and 6, 22/24 of season 7, all 24 of season 8, and 16/22 of season 9 have at least a source locator. External source discovery is not source acquisition: held complete dialogue remains **0 episodes**. See `catalog/dialogue-source-queue.json` and the rights notes in `DIALOGUE-INGESTION.md`.


## Season 4 dialogue-source evidence: complete external page mapping (October 23, 2026)

A separate evidence pass mapped **all 22** original 1984-series Season 4 episodes to their individual Subtitle Cat caption-display pages, including **20** episodes previously lacking any dialogue-specific locator. Verified source upload indexes from June 21, 2025: [1710150](https://www.subtitlecat.com/list_page.php?from=1710150) and [1710200](https://www.subtitlecat.com/list_page.php?from=1710200). The exact per-episode external URLs and source observations are in `research/season04-caption-page-locations.json`, with references attached to each episode's `episode_sources`.

After rebuilding `catalog/dialogue-source-queue.json`, **64/193** episodes have direct external dialogue/caption pages, **121/193** have index-only leads and **8/193** still lack specific dialogue locators (S07E03–E04, S09E06, E08, E17, E19–E21). **No episode-complete copyrighted subtitle file was downloaded or mirrored** during this pass. The SRT/VTT/local-media ingestion and audiovisual quality tools remain ready for separately provided files.


### Original S07/S09 caption-source cleanup

Five more independently opened external caption-display pages have been mapped to S07E03, S07E04, S09E06, S09E20 and S09E21. A source-specific title variant calls the finale `Opportunity Knock Knocks`, while the catalogue records `Opportunity Knocks`; aliases are not conflated with different episodes.

The updated 193-episode acquisition queue now shows **69 direct episode pages**, **121 episodes indexed at a series/season source**, and **3 without a specific dialogue locator**: S09E08, S09E17 and S09E19. These counts measure research pointers, not locally saved scripts or subtitle files. `research/s07-s09-remaining-direct-pages.json` records source URLs and evidence without copying the protected dialogue.


### Caption-enabled licensed-provider viewing for the final three missing dialogue leads

The only three episodes not yet linked to an external downloadable transcript/caption-display page or an episode-specific caption-upload index are S09E08, S09E17 and S09E19. Each now has an **episode-specific Apple TV listing explicitly advertising English (US) CC**, catalogued as `episode_streaming_catalog` instead of a transcript locator. Their source metadata, platform regions and reported runtimes appear in `catalog/streaming-cc-fallbacks.json`.

These publisher listings may require access, purchases or regional availability. They do **not** deliver an exported SRT, confirm a source-video match, or authorize copying protected captions. The acquisition queue continues to report **69 direct third-party caption/transcript pages, 121 index-only leads and 3 episodes with no exported-dialogue source**, while the streaming-CC supplement covers those three for future audiovisual research.


## Owner-provided Seasons 1–2 SRT dialogue acquisition: complete import

Both owner-uploaded RARs have been extracted and relocated to `research/source-archives/`. All **35 episode-specific English SRT files** are physically held, one per S01E01–S02E22 episode, with **12,995 timestamped cues** and roughly **91,345 transcript words**. The existing importer keeps original subtitle bytes as `original.srt`, plus `segments.jsonl`, `readable.txt`, `manifest.json` and `quality.json` under each episode's `dialogue/versions/` directory. Original archive hashes and all 35 original member filenames are indexed in `catalog/rar-ingestion-manifest.json`.

Thirty-four tracks had no automated quality flags. **S01E11** received one review flag for adjacent repeated caption text. Although the files reach roughly 22–23 minutes of source timing, **none is independently video-verified as complete**. `catalog/dialogue-coverage.json`, `catalog/dialogue-quality.json` and `catalog/dialogue-index.jsonl` now reflect actually held source text. See [the source import and quality report](research/season1-season2-subtitle-import-report.md). Next acquisition priority is Season 3 onwards, not reacquiring these 35 episodes.


## Text-only AI character attribution programme (source-backed preparation)

The first two user-supplied seasons comprise 35 locally held English dialogue tracks. A bounded offline preparer now splits their 12,995 original caption cues into 15,014 *potential utterances*, producing 370 overlapping text-only attribution work packets, plus per-version credited-character rosters, direct-address clues and cautious provisional scene boundaries. These are **unattributed work units**. No agent has yet claimed an actual named speaking part from this process.

The complete multi-agent strategy, worker/skeptic contracts, model calibration and limits are documented in [TEXT-ONLY-SPEAKER-ATTRIBUTION.md](TEXT-ONLY-SPEAKER-ATTRIBUTION.md). `tools/prepare_speaker_attribution.py` creates the evidence packets; `tools/reconcile_speaker_votes.py` validates separately submitted agent votes and renders an explicitly provisional script when at least one voting file exists. Low-confidence/conflicting assignments remain UNKNOWN. In particular, the caption's addressee is not automatically the caption's speaker, credited guest appearances are not guaranteed, and scene headings are not invented from unseen footage.

## FTP integration (S60-compatible)

The dedicated read-only inventory and one-file staging workflow is described in [FTP-ACCESS.md](FTP-ACCESS.md). It reuses S60's Seedhost FTP host/account configuration and requires **a separate `FTP_PASSWORD` Actions repository secret in `gamesbyian/general-purpose`**. Credentialed FTP access is manual-dispatch only. The existing 35 S01/S02 subtitle tracks are already preserved; do not download them again merely to establish FTP access.

## Audiovisual script-generation plan

See [AV-SCRIPT-FACTORY-PLAN.md](AV-SCRIPT-FACTORY-PLAN.md) for the proposed episode processing factory: source-faithful mono FLAC, optional Opus listening copies, sparse timestamped visual references with targeted 3–4 fps windows, ASR alignment, speaker diarization, source-backed scripts, and separate FTP/Drive storage. Existing remote TVRip root is `/downloads/Night Court TVRip S1-S9`; the existing FTP video metadata workflow still requires a manual dispatch for a real inventory. The 35 S01/S02 subtitle witnesses are already preserved and must not be reimported unnecessarily.
