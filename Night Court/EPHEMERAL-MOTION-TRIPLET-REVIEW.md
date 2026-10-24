# Ephemeral source-verified motion-triplet triage (October 24, 2026)

**State:** executable exploratory pixel-difference stage; awaiting live original-video speed and human action-recall calibration. No scene, speaker, gesture, emotional intent or screenplay acceptance is implied.

## Engineering behavior

After the original AVI is SHA-256 checked, FFmpeg samples the already-planned ≤240 bounded native-PTS JPEGs into scratch. Before scratch deletion, `tools/summarize_motion_triplets.py` groups at most 32 already-selected three-frame bursts. Each group must have the same provisional cut partition, the same exact plan and extracted original-media SHA, independent image byte hash checks, and *strictly increasing actual decoded video PTS*. Duplicate or reversed source PTS force an abstention rather than suggesting temporal continuity. It rejects image paths within the GitHub checkout and traversals/symlinks.

For eligible groups, the system decodes three temporary images into 64×48 grayscale grids and computes consecutive normalized pixel mean absolute differences and fraction of pixel changes at least 24/255. The reported mean is only a **review-priority heuristic**, not calibrated optical flow, identifiable physical movement, camera-edit verification, inferred performance, or evidence of a continuous actual shot. Source JPEGs, pixel grids, audio, and model weights are discarded. The original full-frame scan is not repeated.

Data contract `night-court-ephemeral-triad-pixel-change-metadata/1` includes each source verified event ID, actual three PTS times, retained SHA references to deleted scratch images, two consecutive pixel-difference reports, ranking value and explicit zero-acceptance flags. Original `source_frame_pts_ms_actual` never becomes the source transcript paragraph time for S09E19.

## Validation and cost discipline

`tools/test_summarize_motion_triplets.py` creates real synthetic JPEGs and tests a sudden visual change, duplicate decoded PTS abstention, altered bytes, mismatched partition, and unverified source provenance. The dedicated source-free pull-request workflow also exercises the FFmpeg synthetic-video actual-PTS test and existing source workers. Only trusted-main owner-triggered source jobs with an existing local verified AVI may compute live evidence; the offline PR test cannot contact the FTP source.

Each real episode will now report `ephemeral_three_frame_pixel_difference_seconds` separately, eligible and abstained triple counts and the top 12 candidate events, with **no** existing benchmark rewritten. The previous two *genuine* integrated whole-source wall times are **239.826s S01E01** and **215.140s S09E19**, both *before* this additional image-content stage. Both underlying image collections were ephemeral, not retained. No p95 claim is justified by two pilots.

### Next accuracy gate

On an owner-controlled original source run, compare ranking against independently reviewed continuous video clips for high-priority physical comedy and camera activity. Measure actual clip-level recall (including missed low-scoring events), false cut-segmentation, human reviewer time, source pixels bytes in scratch, persistent metadata bytes and elapsed `ephemeral_three_frame_pixel_difference_seconds`. Pixel-change ranking is not semantically meaningful until calibrated. Add selective real video or visual-language interpretation only for uncertain, high-score and randomly held-out low-score windows, respecting the 30-minute p95 initial-factory target. Never promote stage directions based exclusively on the triplet heuristic.

Current editorial acceptance: S01E01 0/17, S09E19 0/11, full series **0/193**.
