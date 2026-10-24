# Parallel AV lanes and multi-goal review: production experiment

**Implemented 2026-10-24; real parallel speed and semantic output unverified.**
Work item: [#302](https://github.com/gamesbyian/general-purpose/issues/302).

## Current executable path

- `tools/source_once_av_lanes.py` runs two source-processing functions in
  serial or in a bounded two-worker pool; strict worker exceptions propagate.
  Exactly one SHA-pinned original AVI is downloaded by the existing owner-only
  workflow. The audio worker decodes its PCM once; the video worker reads the
  same immutable AVI. Both use isolated scratch.
- S01E01 `profile_s01e01_one_source_factory.py --execution-mode parallel`
  overlaps whole-episode free-decoding Whisper/Kaldi work with low-resolution
  original video scanning and PTS-checked image extraction. It preserves the
  historical `--execution-mode serial` fallback and now exports actual
  overlapped seconds rather than treating the sum of stage costs as wall time.
- S09E19 `profile_s09e19_source_once_factory.py --execution-mode parallel`
  overlaps its existing full-frame video scan with PCM decode, two independent
  ASR passes and word comparisons; other sequential image tasks remain after
  source-time candidates are known.
- `tools/build_multigoal_review_packet.py` uses the same unaccepted
  original-source report to produce a tiny review plan: every selected original
  picture+audio window has *eleven independent pending questions* (real shot,
  room, visible cast, arrivals, gestures, props, physical comedy, nonverbal
  sound, voice delivery, mouth/voice link and proposed stage directions).
  Coverage is a distinct interval union, **not** a sum of overlapping windows.
  It never promotes speaker identity, dialogue, action or script acceptance.
- Both pre-existing trusted, owner-only source workflows select `parallel`
  for the next empirical original-AVI run, followed by the multi-goal builder
  and a bounded private text/number artifact. In neither case is a PR-head
  implementation checked out with credentials. No extra AVI is acquired for
  the review-packet phase.

## Real benchmark and stop/go

Historical **serial** original-source values: S01E01 **239.826s**; S09E19
**170.522s** pixel pilot and later **213.936s** integrated report. Runner
startup, pip/FFmpeg installs, semantic vision model calls, human listening,
script editing and independent acceptance are excluded.

The next trusted run must compare measured full processing wall-clock to these
exact baselines **without claiming causality from a single variable run**.
If CPU/I/O contention erases gains, switch back to serial. The S01 scheduler
uses two workers; source ASR remains internally sequential, so this is *not*
three simultaneous model instances. The S09 video scan overlaps ASR, but Vosk
and Whisper inference remain internally sequential. Model downloads, thread
counts and host sizing deserve another controlled experiment before expanding
parallelism. Report host model, cores, memory, model and source IDs, model
download time, worker startup, stage elapsed, overall wall, peak memory and
bytes transferred. Compare on both pinned original editions repeatedly.

There is no claim that a faster metadata pass is a finished screenplay.
The 12 S09E19 original playback requests cover roughly 32.5s of a 22-minute
source before any deduplication; whole-episode stage action, continuity,
named voices, inflection, setting, and dialogue remain unreviewed. Do not launch
193 media jobs or call the factory release-ready until representative
semantic and independent-review calibration measures actual error, recall,
coverage and total reviewer time, including low-activity holdout shots.

## Acceptance boundary and next work

The publication standard remains [AV-SCRIPT-PUBLICATION-GATES.md](AV-SCRIPT-PUBLICATION-GATES.md).
Next: actual timecoded original picture+sound reviewer interpretation (or a
tested accessible video model and independent review), sample true scene/action
coverage, reconcile the S01E01 16 disputed text windows, diarize anonymous
speakers and match voices to synchronized screen evidence, and produce two
complete independently reviewed pilot screenplay manuscripts. The current
work does **not** itself interpret visuals or create accepted stage directions.
Private source material and model weights stay outside Git.

### First measured parallel S09E19 checkpoint, October 24

Trusted actual original AVI run [#40133282389](https://github.com/gamesbyian/general-purpose/actions/runs/40133282389)
succeeded: **242.378s** source processing excluding runner setup and
dependency install; stage clocks sum **269.694s**, with **27.316s** measured
overlap. It emitted **202** PTS-matched source JPEG candidates, a 12-window
multi-goal original-source AV pending review (31.392s *distinct* selected
runtime) and **three** small semantic microbatches with **zero** actual vision
model interpretation. The strict artifact SHA and stage breakdown are
[archived here](research/s09e19-first-parallel-source-wall-evidence-2026-10-24.json).

The measured source-processing wall is **slower** than older S09E19 serial
runs of 213.936s and 170.522s. Model download and inference stage times
also changed; this cannot establish that parallelism caused the slowdown.
The trusted S09E19 owner workflow therefore now selects **serial** again,
retaining a command-line parallel mode for controlled future comparisons.
Neither p95 production speed nor screenplay content improved or was accepted.

### Cold runner installation mitigation

The first parallel S01E01 source job #40133280264 spent unexpectedly long
in its fixed-dependency install step, while S09E19 completed installation
normally. Do **not** mistake installer time for model inference or assume
a cause without the completed job logs. Both trusted source workflows now
first test for already installed `ffmpeg` and `ffprobe`; fallback APT is
time-bounded, and fixed-version Python package install has explicit limited
retries and network timeouts. The SHA-verified source worker and source media
publication gate are unchanged. Verify end-to-end job duration on a subsequent
owner-controlled run before claiming improved startup reliability.
