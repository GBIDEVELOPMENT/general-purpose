# Fast shot-aware visual executor: no 4fps whole-episode screenshot flood

The [metadata-only visual plan](tools/plan_fast_visual_pass.py) merged in PR #260 limits each episode to ≤240 source image requests, ≤32 3-frame bursts, ≤12 shot-boundary pairs and ≤100 spaced context frames. Existing original S01E01 real AVI has **encoded 30000/1001fps**, with repeated/out-of-order sampled decoded PTS. Nominal frame times must **not** be silently treated as actual source frame PTS.

`tools/extract_fast_visual_plan.py` turns a **locally available verified AVI plus a rate-grounded plan** into JPEGs in an explicitly external scratch folder, using **one FFmpeg input decode/selection process** (not up to 240 FFmpeg program starts, FTP downloads or media re-reads). The decoder selects source frame indices, emits scaled 320px JPEG stills and `showinfo` presentation timestamps. For every selected image it records original media SHA, nominal target frame index and time, **actual decoder PTS**, absolute timing difference, image size, image SHA, candidate-shot partition and original motion/cut task id. The sampled images are never automatically linked to dialogue/speaker identity or claimed as continuous visual review.

The tool rejects unverified synthetic-frame-rate plans, changed original SHA, duplicate requested frames, plans >240 JPEGs, any unexpected source frame deficit, a single JPEG >120KB or total images >10MB, and output directories within the Git checkout or already occupied. Actual frame-time deviations over 125ms are **reported and fail the `all_samples_within_source_pts_tolerance` evidence gate**, not silently coerced. This is a bounded *research* image extractor: callers must check that gate before interpreting source proximity. Cut crossings remain segregated from motion bursts.

```bash
python 'Night Court/tools/test_extract_fast_visual_plan.py'
python 'Night Court/tools/extract_fast_visual_plan.py' \
  --media '/private/original/source.avi' \
  --plan '/private/original/verified-rate-frame-plan.json' \
  --output '/private/ephemeral/source-frame-evidence'
```

The existing [S01E01 31-frame dry-run input](research/s01e01-fast-visual-dryrun-input.json) still explicitly labels **24fps unverified synthetic assumption** and **will be rejected**, rightly, until rederived from [actual source FPS JSON](research/s01e01-native-cadence-and-cost.json) using the source cadence and original SHA. A full original-source run should prepare the verified rate plan and execute this same extractor **in the same ephemeral source transfer as audio analysis**, otherwise repeated downloads undermine throughput. No second FTP run is added merely to sample 31 frames.

**Offline independent QA:** `tools/test_extract_fast_visual_plan.py` synthesizes a 24fps AVI, requests a within-shot gesture triad and across-shot cut pair, makes FFmpeg actually decode JPEGs, validates recorded source PTS and sha256, and asserts oversize/unverified-plan refusal. It does not use private video and does not establish source-image inference accuracy. Next measurable go/no-go is **visual model recall on significant gags and actual full-episode FFmpeg scan/extraction wall time**, rather than simply trusting image count reduction.

Script publication remains blocked: 0/193 complete; no human speaker or performance acceptance can come from these sampled frames.
