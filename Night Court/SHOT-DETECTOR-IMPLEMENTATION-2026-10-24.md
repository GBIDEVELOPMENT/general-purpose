# Executable PySceneDetect versus existing FFmpeg shot benchmark

**Status: source-free synthetic acceptance, original pilot cut calibration still pending.** This implements Gate 1 of [modern workflow review](MODERN-TOOLING-AND-WORKFLOW-REVIEW-2026-10-24.md), and coordinates with [original SHA/PTS image-planner](FAST-EPISODE-FACTORY-THROUGHPUT.md), [headless VLM benchmark](HEADLESS-VIDEO-DESCRIPTION-BENCHMARK.md) and [issue #302](https://github.com/gamesbyian/general-purpose/issues/302). No changes to the existing trusted owner media workflows.

`tools/compare_shot_detectors.py` compares existing saved FFmpeg image-change **candidate** cut positions with a local **PySceneDetect 0.7.2** content or adaptive detector. A hand-reviewed reference list is optional; the tool only reports precision/recall/missed cuts when such a list is actually supplied. False cuts and missed cuts are one-to-one time-tolerance matched, never counted twice. The detector's FrameTimecode is **nominal stream timing**, not a verified native decoded-frame presentation timestamp; existing original PTS verification remains mandatory before using cuts for physical-motion excerpts.

For a temporary local authorized source with matching SHA, create an explicit input JSON (all values here are **synthetic examples**, not a pilot claim):

```json
{
  "schema": "night-court-shot-benchmark-input/1",
  "episode_id": "S01E01",
  "source_video_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "duration_ms": 6000,
  "existing_ffmpeg_cuts_ms": [2010, 4010],
  "independently_reviewed_cuts_ms": [2000, 4000]
}
```

```bash
# Metadata-only comparison of existing cut candidates: no media required
python3 'Night Court/tools/compare_shot_detectors.py' \
  --manifest /private/source-verified-shot-reference.json \
  --detector existing --output /private/existing-cuts.json

# After locally installing a pinned PySceneDetect 0.7.2 and opencv-python-headless,
# on trusted owner-provided media only (script does not access FTP/secrets):
python3 'Night Court/tools/compare_shot_detectors.py' \
  --manifest /private/source-verified-shot-reference.json \
  --media /private/sha-verified-original.avi \
  --detector content --confirm-owner-media \
  --output /private/content-detector-comparison.json
```

Change `--detector adaptive` to compare adaptive thresholds. The source duration must be ≤40m, source file ≤2GB and all candidate cuts ordered/unique; detection uses a new local read of the same already-cached file, **not another FTP retrieval**. No video/frames/actor recognition/model weights are saved. The PR CI runs a synthetic hard-cut 3-color, 6-second film, tests actual FFmpeg source hashing, and uses PySceneDetect real inference over 2s and 4s cuts, no owner media and no secrets.

**Next source-facing step:** choose ≥12 original independently reviewed shot transitions plus several non-transition fast gestures and fades from both pilots, annotate reference times directly from synchronized source video and keep them **private**. Compare content/adaptive/older FFmpeg proposed cuts, frame-level PTS tolerance, missed hard cuts, dissolves, false positives on gestures, and time including decode. Prefer the existing FFmpeg detector if no meaningful quality/throughput gain. Do not treat a detected shot cut as a scene change or promote any screenplay action without actual video interpretation.
