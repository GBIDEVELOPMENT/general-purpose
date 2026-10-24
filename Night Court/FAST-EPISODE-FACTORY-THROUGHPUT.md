# Fast episode factory: bounded, measurable design

**Status (2026-10-24):** the first **offline planning implementation**, not a completed end-to-end runtime benchmark. The original-series source inventory has 193 episodes, 192 timed subtitle witnesses and one untimed S09E19 witness. No complete episode script has been accepted. This document is a performance contract and pilot plan, not proof the targets have been met.

## Throughput is an acceptance gate

**Target:** one ordinary ~24-minute episode should finish its initial full-episode evidence pass within **30 minutes elapsed at p95** on the selected production hardware, **including media retrieval**, with a **stretch target of 15 minutes** once caching, stage overlap and model selection are measured. Reject architectures that need hours of repeated image or ASR inference per episode. The next pilots must log wall time, CPU/GPU utilization, decoded audio seconds, network bytes, image/model inference counts, peak memory and retained evidence bytes **per stage**. Never interpret a GHA runner's allocated timeout as an actual benchmark.

Suggested initial **time allocations** for a 30-minute baseline, *not measured performance*:

| Stage | Proposed p95 wall-time allowance |
|---|---:|
| Verify/download one original video (SHA pin; ideally process near FTP storage) | 5 min |
| Probe real video cadence, audio extraction and lightweight low-resolution full-frame cut candidates, sharing one source checkout | 4 min |
| Two **free-decoding and architecturally distinct** ASR models on the **same audio**, concurrent only when profiling shows a speedup | 10 min |
| Deterministic ASR+SRT time alignment, disagreement scoring and selective anonymous diarization | 4 min |
| Budgeted visual inference, only on source-selected triads/stills/cut pairs, then draft evidence manifest | 6 min |
| Export compact bundle, measure and discard temporary source media | 1 min |

Do not blindly add these stage targets to parallel jobs: the measurement is **end-to-end wall time**, and actual overlap depends on hardware. Cut/detector scan processes full video at reduced spatial resolution; the capped frame budget limits *image extraction and visual model calls*, not source-video decoding or transfer time. Benchmark the full scan, especially on CPU, rather than claiming it is free.

If the hardware cannot hit 30 minutes p95 after calibration, make the initial fast pass cheaper (smaller/faster decoder, fewer selected events or cached local source), flag deferred expensive checks and retain an exact work queue. **Never silently sacrifice rare jokes, unsupported speakers, unusual words or high-priority physical comedy to pass the clock.**

## Pilot implementation: no blanket frame dumping

`tools/plan_fast_visual_pass.py` accepts compact source-linked timing hypotheses in `night-court-fast-visual-input/1`, and returns a **metadata-only shot-aware candidate plan**. This tool does **not** decode video, transcribe speech, assert source-frame PTS, or verify cuts, speaking identities or physical movements. A separate executor must verify the exact AVI SHA, ffprobe cadence and decoded frame PTS before trusting any nominal time.

1. At most **100 sparse baseline stills** at nominal 15-second intervals for a normal-length episode, evenly spread if a longer episode would exceed the cap.
2. At most **32 prioritized three-frame bursts** (96 individual frames), with source-frame cadence inferred from a rational ffprobe value. A `gesture` triad samples about 167ms apart at 24fps; `adjacent` samples every frame. Keep triads inside one **candidate** shot, with one nominal frame of margin at its boundaries. Defer a motion event that touches a cut instead of inventing continuity.
3. At most **12 cut-boundary pairs** (24 frames), explicitly segregated from motion sequences. These review shot edits, not action continuity.
4. Hard ceiling **240 individual image candidates per episode**, deduplicated by nominal frame index. Selection consumes priority motion events before baseline. The event list, missed events and reasons stay in evidence. Downstream image executor must also cap artifact bytes and crop/scale on-device; consider **320px stills and ≤10MB** derived images per episode as an initial unmeasured target, never raw original video in the repo.
5. Candidate cuts can be false positives: scored FFmpeg contrast is not an established editorial cut, let alone a dramatic scene boundary. Future stages need independent dissolve/fade and rapid-motion validation. No one can interpret cut-neighbour pairs as uninterrupted action.

Example offline dry run (contains **actual source-proposed S01E01 cut times**, six original editorial event centers, but **deliberately assumes 24.000fps** because we have not yet retained source ffprobe cadence):

```bash
python 'Night Court/tools/test_fast_visual_pass.py'
python 'Night Court/tools/plan_fast_visual_pass.py' \
  --input 'Night Court/research/s01e01-fast-visual-dryrun-input.json' \
  --output '/tmp/night-court-s01e01-fast-visual-dryrun.json'
```

This 36.162-second sample proposes **31 unique frames, five valid motion triads, seven cut-review pairs, two baseline stills and one explicitly deferred event**. This is an offline *plan* and not a comparison of actual image-analysis accuracy or runtime; its source cut timings remain candidate cuts. The old source run captured **145 actual 4fps stills** in that window. A reduction from 145 requested stills to 31 planned ones does not yet imply equivalent coverage.

## Do not assume all AVI sources run at 24.000fps

For every original AVI, first `ffprobe` its video `avg_frame_rate`, `r_frame_rate`, `time_base`, stream start PTS and, if reliable, frame count; check decoded frame timestamps where frame cadence appears variable or duplicated. This should happen in the same already-needed authenticated read, not a separate 183MB download. Accept `24000/1001`, `24/1` or other **measured** stream metadata. The visual planner records whether the nominal rate is **verified_local_ffprobe** or a clearly labeled **synthetic_unverified_assumption**, and never asserts nominal indexes are decoded source PTS. The next real S01E01 trusted source run should record these exact stream properties and source-hash provenance, together with stage wall times.

## Two independently decoded ASR witnesses, not a transcription factory

- Decode **one** whole-episode 16kHz mono audio stream to ephemeral scratch once and reuse it for two free-decoding models. Both infer independently: no subtitle prompts, no transcript passed from model A into B, no model-specific vocabulary hint from the answer key. Whisper-family variants alone are insufficient evidence of substantial error independence; pilot e.g. faster-whisper vs a genuinely separate CTC/Conformer model, with actual English sitcom WER/time measured. Subtitle-constrained CTC forced alignment is a **timing proposal**, not a second independent decoder.
- Align both hypotheses to each other **and separately** to the immutable original SRT. Categorize exact or near-exact normalized model-model agreement, agreement with independent subtitle witness, disagreements, gaps, overlapping voices, nonsense/vocabulary and unmatched model additions. Record model family and version, confidence provenance and source timestamp. Genuine independent decoder agreement is affirmative **machine-corroborated dialogue evidence**, not a claim of a human listening or of statistically independent errors.
- Make easy consensus cheaply reusable for script drafts, and spend targeted third-model inference or human listening on contradictions, strange idioms, deliberately unusual words and caption edges. Tune the promotion rule against a truly listened blind pilot, recording **joint-error rate conditioned on agreement**, precision of automatically corroborated words, coverage and human review minutes saved. Treat laughter, music, silence and overlap as potential shared-error failure modes.
- Voice diarization across the complete episode can cluster voices more reliably than isolated 30-second cuts, but distinct diarizers agreeing on clusters does **not** name Harry/Dan/Bull. Confirm character identity from anchored audiovisual/voice evidence separately.
- Never run expensive multimodel prosody or all-frame action classification by default. Target only uncertain and performance-rich passages, preserving explicit deferred review work.

## Calibration and go/no-go before 193-episode launch

1. **S01E01:** original ffprobe cadence, single verified source acquisition, dual independent **whole-episode** decoders, source SRT agreement, shot-aware visual-plan-to-actual-frame matching, and measured runtime. Include difficult C19/C22/C24/C28 as blind error probes.
2. **S09E19:** untimed 347-paragraph original witness is a tougher alignment and absent-timestamp case. Establish the same full-episode runtime ceiling, ASR agreement and point-in-time source anchoring without inventing any original subtitle timestamps.
3. Compare (A) old dense 4fps approach and (B) fast adaptive sampling on **reviewer-judged high-priority gestures and shot transitions**, with recall/precision, missed motions, transcript agreement joint errors, transfer time, cache hits, peak memory and generated bytes. Estimate budgets from measured p50/p95 on at least these two different pilots. Do not mass dispatch until the results are acceptable.
4. Source audiovisual screenplay acceptance and human-reviewed performance/identities remain separate downstream gates. Budgeted fast draft production is **not** a shortcut around those evidence distinctions.

**Current boundaries:** PR #258 holds S01E01 36-second model word hypotheses on an open branch, not main; do not infer any second independent ASR model from that. No source fps was established by the historical FFmpeg fake-24fps regression. No full-episode dual ASR throughput benchmark has yet run.

## First real original-source cadence / stage-cost measurements

[Source run #40070932182](https://github.com/gamesbyian/general-purpose/actions/runs/40070932182) succeeded, and a [hash-pinned metadata record](research/s01e01-native-cadence-and-cost.json) is retained. **S01E01 is actually encoded at 30000/1001 (29.970fps)**, not the 24fps default in the earlier fixture. A 3s PTS sample around 700s had 90 distinct times among 91 rows, one repeated timestamp and one non-monotonic decoded-order PTS. Median positive presentation interval was **33.367ms**. Do not assume other episodes share this encoding or that the filmed underlying motion rate is necessarily the AVI output rate.

The source took **4.796s** to FTP-retrieve and SHA-check, **0.055s** to probe, **0.078s** for sample timestamps and **1.148s** to run original AVI frame-level shot scoring over a 36.162s excerpt. This sums to **6.077s** of measured stages on that runner, excluding installation/runner setup. The same six review events and seven detected cut proposals produce **31 planned frames even at the actual 29.970fps cadence**. No real image inference, full-episode shot scoring, or dual whole-episode ASR runtime has been measured; no 30-minute p95 claim is accepted yet.

**Next performance gate:** retrieve source just once, decode audio once, benchmark two genuinely different *free decoding* ASR models on the full 1448s episode (sequential versus parallel on actual available hardware), and measure full-episode low-resolution shot scan plus ≤240 source-PTS-confirmed visual candidates. Record true end-to-end wall clock including staging and worker startup. After two qualitatively different pilots, validate the p95 runtime target over a sufficiently broad representative sample, not just two episodes.

## First full-episode independent ASR actual measured cost and agreement

[Trusted source benchmark run #40071950255](https://github.com/gamesbyian/general-purpose/actions/runs/40071950255) **succeeded** with original SHA-pinned complete S01E01 AVI (1448.256s). Two *genuinely distinct architectures* freely recognized the **same** one-time-decoded original soundtrack, with no subtitle or other-model answer prompts: `vosk==0.3.45` small English Kaldi HMM/WFST (2205 retained words) and `faster-whisper==1.2.1` tiny.en CPU int8 beam1 (2362 retained words). Measured original acquisition and SHA verification **3.157s**, whole audio PCM decode **3.642s**, Vosk weight download/unpack **3.993s**, Vosk source inference **79.603s**, Whisper whole episode inference **43.755s**, deterministic model-model word/time agreement **0.015s**, total **134.165 seconds** across these source-processing stages (2m14s), **excluding** runner setup/OS and Python dependency install. Compact signed-source-numeric [result summary](research/s01e01-whole-dual-asr-benchmark-summary.json); full temporary private model-output artifact #12551588072, source ZIP SHA `69cbb9f2f07036053c8c58912c90f38288b680bb3943548bd47b4fdbb7e30e7a`, original JSON SHA `197404e41a68b4c373770e1771d7059d23b993efcdc38e6cee0db1fe8f8c666b`, expires October 31, 2026.

The positive **machine-corroborated dialogue** class contains **1447 agreeing source-timed word candidates in 200 ≥3-word runs**, from 1645 individually paired proposed words; the unresolved list preserves **1673 single-model word candidates**. **238 additional Whisper word-time proposals failed a strict timing validity gate** and require error-category analysis; do not misrepresent them as actual absent or incorrect original words. Both models agree on the basic 'Did you say Mercurial?' question, while the invented vocabulary around later jokes remains contested, demonstrating useful selectivity. Neither model was prompted with existing SRT text; source SRT comparative agreement and blind joint-error calibration remain **pending**, so the 1447 machine agreements are positive independent-model evidence, not human verified dialogue.

**Throughput:** Actual source acquisition and two CPU recognizers on this original episode take a little over two minutes, not ten hours. However full-episode shot analysis, actual image extraction/vision inference, diarization, captions-to-source cut verification, character attribution, stage/performance description, runner cold start and **p95 across a representative sample** are not in the measurement. Retain <=30-minute p95 end-to-end initial pass as an unproven go/no-go criterion rather than claiming production readiness from one source.


## Complete original S01E01 source video: measured 55.239 seconds (October 24)

The trusted base-only original source run [#40114720483](https://github.com/gamesbyian/general-purpose/actions/runs/40114720483) **succeeded** over the full 1448.256-second S01E01 MPEG-4 640×480 30000/1001 AVI with verified SHA `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`. It did not assume the source was 24fps. The 160px frame-to-frame FFmpeg detector found **212 unverified image-change/possible-cut candidates** at threshold 0.12. A bounded 240-frame-max plan chose **212 actual extracted JPEG frames**, including **95 contextual baseline stills, 31 shot-bounded triads (93 frames), 12 across-cut pairs (24 frames)**, and **one explicitly deferred original visual event**. All 212 original decoded presentation timestamps passed the 125ms proximity check; those JPEGs together occupied **908,395 bytes** and were then discarded.

**Genuine measured source stages:** FTP source transfer + hash 4.089s, ffprobe source metadata 0.064s, complete low-resolution original AVI shot scan 27.624s, plan 0.009s, one-pass exact original source JPEG extraction 23.453s: **55.239 seconds** total (excluding runner startup/installation). Reproducible small [source-hash-verified numeric summary](research/s01e01-full-video-throughput-summary.json) linked to the exact source-run private metadata artifact #12568510039, original ZIP SHA-256 `2ea1ff770be898cea2d5dc46eb0ca93b065b366a5161fd62b44147b78592b7cd` and original JSON SHA-256 `11162478a37d0c1d7718908bd7ee38b15ebde42124f227aa6fe689e704c48545`. Artifact expires October 31.

The previous complete **two-family independent ASR** source-run stages were **134.165 seconds**. The **separately measured stages add to 189.404 seconds (3m 9s)**, but this is **not** a measured combined source-once full pipeline runtime. It excludes visual-model comprehension, diarization, performance inspection, script revision and human quality acceptance. This stage confirms full-frame video decode plus carefully bounded JPEG export need not take hours, but does not prove recall of physical comedy, edits or acting subtleties. Proposed edits are merely image statistics, uniformly selected triads are **coverage probes not detected motions**, and speaker/scene/action claims remain pending.


## Source-once integrated first-pass benchmark: real 239.826 seconds

The first **single original AVI, one downloaded/verified source file, one decoded PCM, two independent whole-episode ASR families, full-frame-change video scan and native-PTS checked bounded JPEG pass** completed successfully on trusted-main source run [#40115701804](https://github.com/gamesbyian/general-purpose/actions/runs/40115701804). It processed the verified original 1448.256-second S01E01 AVI with video SHA `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962` and PCM SHA `7fd284e99af1d69ca429496060c876241f181738666a86e8cb1335d5b869861a`. **Actual uninterrupted source-processing wall clock: 239.826s (3m59.826s)**, not the arithmetic sum of previous separately run pilots. Individual stage measurements sum to **239.559s** (small scheduling/orchestration difference).

Detailed stage timings in seconds: retrieve+SHA **5.275**; mono audio decode **5.985**; Vosk model download/unpack **32.290**; Kaldi/Vosk full episode inference **87.384**; Whisper tiny.en full episode inference **57.268**; word/time reconciliation **0.019**; source ffprobe **0.065**; all-video low-res FFmpeg image-change scan **27.576**; plan **0.010**; 212 native-PTS JPEG decode **23.687**. The original video was obtained once. **198 independent model agreement spans (1,417 words)** were positively corroborated by architecturally different freely decoding models, with **1,729 unresolved** word candidates. Whisper rejected **343** candidate word timestamps due specifically to zero or reversed durations after 1ms rounding; no timestamps were auto-salvaged or promoted. The 212 selected images totaled **908,395 bytes**, all passed original video frame PTS checks and were deleted with the ephemeral source directory.

A durable [source and audio SHA pinned full-episode metric summary](research/s01e01-one-source-integrated-wall-clock-summary.json) links private source artifact #12567609259 (artifact expires October 31 2026), original artifact ZIP SHA `a0964a640c28814aeb18e89fcab9ce8d892fa3cc8f80d5e7e3aaa62d8b214033`, extracted original JSON SHA `c45b85e9bb17193cb0eeb6d60e86524349c00ea6e8d39d34bb01ea95989bd67d`.

This establishes a **real, fast first source evidence pass** on S01E01, including entire original audio and entire original video scanning, but **not** visual-language image comprehension, full-source diarization/named characters, emotional expression or motion verification, human original-source listening, scene script completeness, GHA runner bootstrapping/install time or 193-episode p95. Candidate cuts are not certified shot/scene boundaries; one source still does not validate general runtime distribution. Original source/editors still have 0/17 human acceptance tasks S01E01, 0/11 S09E19, and 0/193 complete production-verified original-series screenplays.


## October 24 source-import closure and candidate-triad pixel scoring

The [S09E19 original full-source metadata archive PR #292](https://github.com/gamesbyian/general-purpose/pull/292) merged after exact rederivation CI [#40127342881](https://github.com/gamesbyian/general-purpose/actions/runs/40127342881) passed, with only the locally measured microbenchmark sort-seconds field excluded from strict deterministic comparison. Trusted source original-run wall time is **215.140s**, identical to its prior evidence and **not** a new benchmark. PR #291 and PR #286 were closed unmerged as one-shot owner source triggers.

`tools/summarize_motion_triplets.py` introduces a source-PTS/SHA checked, ≤32-triad *post extraction* image difference ranking stage, measuring separately the time required to inspect downscaled 64×48 gray images while all source frames remain ephemeral. This avoids an extra source download or entire-video decode but adds a small as-yet-unmeasured image decode cost. The top 12 candidate review events are ranked by consecutive temporal pixel differences, with dedicated abstention for non-increasing PTS. These are **not** motion semantics, editorial cuts, or evidence-grounded stage directions; the original stills cannot be recovered from retained hash metadata. See [method and evaluation constraints](EPHEMERAL-MOTION-TRIPLET-REVIEW.md). 30-minute p95 including genuine visual interpretation is **unproved** and no 193-episode production roll-out is accepted.


## October 24 S09E19 original-source pixel-triad profiling: real 53ms stage

[Trusted full-source run #40128021777](https://github.com/gamesbyian/general-purpose/actions/runs/40128021777) succeeded using the production-like trusted-main source worker including `summarize_motion_triplets.py`. Original S09E19 SHA remained `51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649` with 1320.144s original video and 347 unmodified **untimed** text paragraphs. **Measured end-to-end original source-processing wall: 170.522s** (excluding job startup/dependency installation). Measured *new* ephemeral image triplet stage: **0.053s** for 31 64×48 luminance-feature three-frame bursts, zero invalid PTS order, retaining only 12 ranked metadata candidates. Source once: 202 native-PTS-confirmed temporary JPEG frames/999,791 bytes, original downloaded once, one PCM decode, two independently decoded Whisper/Kaldi models, whole-frame contrast-change scan. Individual stage seconds sum to 170.519s; difference of 0.003s is expected per-stage monotonic rounding/orchestration.

**Actual stage breakdown (seconds):** FTP+SHA 5.041; ffprobe .237; PCM decode 2.523; Vosk model weights 42.044; Kaldi inference 67.152; Whisper tiny.en inference 27.247; independent-model reconciliation .011; full video low-res scan 14.264; plan .005; bounded frame extraction 11.835; pixel triplets **.053**; untimed paragraph probe .107.

The older S09E19 original source 215.140s benchmark is preserved unchanged; older source run generated 199 ASR agreement spans, newer run 189. Faster *overall* time is mostly other stage variation, including 42.044s newer Vosk download versus 9.950s older and faster ASR/video inference elsewhere. No pair establishes population p95 or accuracy. This new run has **no actual continuous-action visual understanding** beyond score-based prioritization. Scores require sampled physical-comedy event reviewer calibration and low-score holdout inspection. See [numerical provenance](research/s09e19-original-triad-stage-speed-2026-10-24.json), archived under artifact #12572964697 (expires October 31, 2026), ZIP SHA `1098410992cd41e9a488ba93273e33c947568becda1eeaba73beee8e8db3084a`, JSON SHA `9032cd9308e904d2c52da261c6f8b2538565555a0588cbef0ff7388e390dfa57`. Original source SRT and transcript paragraphs remain immutable. All 193 completed screenplays remain unaccepted.


### Shot-bounded review packet added to the fast episode path

Both source-once workers now generate a tiny candidate-shot-bounded *playback request* from existing scored cut timestamps, native-PTS triplets and source SHA. The manifest is capped at 12 video windows, each clipped to the candidate shot interior using a 150ms guard with at most ±1200ms context, and deliberately includes two low-scoring control excerpts when possible. Full scene recognition remains absent. This additional metadata planning stage uses `shot_candidate_bounded_review_planning_seconds`, a **newly instrumented** cost not yet present in the 170.522s source run. Neither the existing whole-episode source benchmark nor the unproved ≤30-minute p95 goal changes. No extra AVI decode happens for the planner. See [review contract](SHOT-BOUNDED-CONTINUOUS-REVIEW.md).

## October 24 bounded parallel AV source and multi-goal review implementation

[Parallel AV/multi-goal execution contract](PARALLEL-AV-MULTIGOAL-EXECUTION.md)
and [issue #302](https://github.com/gamesbyian/general-purpose/issues/302)
describe the now-executable serial-versus-parallel pilot switch and joint
source-linked reviewer packets. The source-once S01E01 worker can run one
whole-audio worker and one full-video worker concurrently using the same
SHA-verified AVI. S09E19 can overlap its original-video scan with the
original-audio work. Original media, independent ASR models, unchanged
subtitle/untimed paragraph witnesses, source-PTS checks and 240-image limit
remain protected. The existing trusted-owner workflows will test parallel
source execution and emit one pending multi-goal packet per original passage.

**No original-AVI parallel speedup has yet been measured or independently
accepted in a scene.** Historical serial baselines and the 0/193 gate remain
unchanged. Inference/model contention might negate CPU overlap; compare actual
source wall clocks and revert to serial if slower. The multi-goal packet is
*review instructions with source references*, not a vision model, a source
listening result or verified physical action. Full-video understanding and
whole-scene coverage are still blockers.

