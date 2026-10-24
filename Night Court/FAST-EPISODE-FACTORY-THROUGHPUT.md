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
