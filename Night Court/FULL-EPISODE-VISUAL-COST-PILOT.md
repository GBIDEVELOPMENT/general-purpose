# Original full-episode video throughput and coverage pilot

**First run pending.** Source S01E01 original SHA: `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`, 183,386,112 bytes, verified MPEG-4 640x480 at **30000/1001 fps**. Existing full original episode independent-audio model processing cost was **134.165 seconds** (Vosk/Kaldi and Whisper), excluding runner startup and installation. We need video decode and visual-model costs before any p95 end-to-end factory claim.

The one-source pipeline `tools/profile_s01e01_whole_visual_pass.py` retrieves exactly one unchanged source AVI, verifies its source fingerprint and FFprobe stream cadence, scans all ~24 minutes via original FFmpeg frame difference scoring **after resizing to 160px** (threshold .12), and saves only scored candidate edit timestamps. This is a **source video image-change statistic, not a cut or scene classifier**. It also carries the six historically sampled original visual editorial tasks, plus at most 26 deliberately uniform video coverage-probe suggestions across the rest of the episode. Coverage probes are *not claimed to be detected body motion*.

The merged `tools/plan_fast_visual_pass.py` limits sampling to **240 total planned frames, 100 baseline stills, 32 in-shot triads and 12 across-candidate-cut pairs**. The merged `tools/extract_fast_visual_plan.py` uses a **single FFmpeg frame-selection pass**, measures individual decoded source-frame PTS against nominal requested times and discards all JPEGs after bounding total image bytes to 10MB. If frame timestamps drift >125ms, the source test **fails**, rather than creating false stage-direction evidence.

Record **network acquisition, source metadata, full video low-resolution frame scoring, plan generation and actual limited JPEG decoding** individually. The trusted source output is only small JSON with image counts, hashes/provenance, score candidate times and timings. No images, full AVI, soundtrack, credentials or model weights leave the ephemeral runner.

## Running

PR-only CI uses a synthetic 12-second 24fps AVI with two deliberately hard cuts at 5 and 8 seconds, verifying detector timestamps and rate-correct, shot-aware plan construction. It also independently tests actual FFmpeg source-frame JPEG extraction.

After PR merge, open the exact one-shot trigger PR on branch `research/night-court-s01e01-whole-visual-trigger` adding `Night Court/research/trigger-s01e01-whole-visual-cost.txt`. The trusted workflow must run from GitHub base SHA exclusively, verify source SHA, and be closed without merging. The only retained result will be a compact metadata artifact. Offline CI must pass before dispatch.

**Success criteria:** technically correct full episode scan with native PTS and bounded sampled JPEGs, honest actual cost report, no source leak, conservative no-acceptance status. This does **not** establish physical-action recall, identify actors, validate every cut or time two visual-language model reviews. A blind image/action recall pilot and combined audio+video wall clock on at least two episodes are subsequent acceptance checks.
