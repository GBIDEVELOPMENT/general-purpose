# S01E01 original-frame-rate scene-change score evidence

**Actual original AVI source run:** [GitHub Actions #40066444160](https://github.com/gamesbyian/general-purpose/actions/runs/40066444160), successful. Temporary video was downloaded with original 183,386,112-byte size, verified against AVI SHA `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`, decoded at actual source frame rate and discarded. The bounded metadata-only output was [artifact #12549059487](https://github.com/gamesbyian/general-purpose/actions/runs/40066444160), ZIP SHA `ab06ec21ac325fd9d568df47ecfe984f43852809e0823edadcf94e5b460f1b07`, original JSON SHA `b80e087ffd25766bf25f7c213a860fad0223fe0a797a27c5a9af758cac21c11a`. Artifact expires October 31, 2026; the source result is now preserved as [scene-candidates.json](seasons/S01/S01E01/derived/shot-change-pts-v1/scene-candidates.json).

The reviewed 00:56.912–01:33.074 source window produced **seven FFmpeg image-change scores above 0.12** at these decoded original-AVI presentation-time candidates:

| Original-video time candidate | FFmpeg image-change score | Nearby previously reviewed 4fps evidence, if any |
|---|---:|---|
| 00:59.026 | 0.306012 | S01-V3-01 sampled change ~00:58.662–00:58.912 |
| 01:00.928 | 0.143181 | S01-V3-03 sampled change ~01:00.662–01:00.912 |
| 01:08.268 | 0.138734 | S01-V3-04 superimposed image ~01:07.912–01:08.412 |
| 01:14.107 | 0.277865 | Previously undescribed source-frame-rate candidate, needs picture review |
| 01:16.777 | 0.261383 | Near OBS-V2-01 earlier sampled angle change ~01:16.250–01:16.500 |
| 01:20.948 | 0.140563 | Within OBS-V2-02 source sampled change ~01:20.750–01:21.000 |
| 01:22.382 | 0.140819 | Near sampled OBS-V2-03 handset-action passage, not established to be an edit |

These are **detector candidates only**. Their score is a frame-image difference statistic and is not a calibrated cut confidence. The fourth candidate was not separately documented in previous sampled-stage observations; the final one may be motion rather than a camera cut. The absence of further candidates after 01:22.382 means only that no subsequent source frame crossed this specific detector threshold in this bounded window, not that the shot is proven continuous. The precise scene transition at 01:08 and all proposed edits require independent watching of original uninterrupted video.

The tool's synthetic regression initially exposed a source-time leak: FFmpeg's output seek could allow score metadata from out-of-window frames through the filter. The correction uses `trim` **before** `select(scene)` so each accepted candidate was scored inside the exact requested interval, preserving original PTS. The synthetic 24fps two-hard-cut test passed on the repaired implementation, before the trusted source run. No audio was heard or saved and no actor, fictional character, dialogue alignment, physical-action onset or whole-episode screenplay was verified.

Reviewer priorities: inspect the original frames surrounding all seven times, especially 01:14.107 and 01:22.382; cross-check source-AVI container presentation timestamps with viewable continuous video; separately listen to difficult caption cues C19/C22/C24/C27; preserve all 17 original S01E01 decisions pending until genuine independent audiovisual checks. The original caption witness and source AVI remain unchanged.
