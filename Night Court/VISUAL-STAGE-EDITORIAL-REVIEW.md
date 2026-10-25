# Night Court: video-model proposals to reviewed screenplay-stage notes

**2026-10-24, executable editorial bridge, synthetic test scope only.** Related: [headless video understanding](HEADLESS-VIDEO-DESCRIPTION-BENCHMARK.md), [two-pilot scripts](CURRENT-PRACTICAL-SCREENPLAY-DELIVERY.md), [publication gates](AV-SCRIPT-PUBLICATION-GATES.md), [source-once multi-goal reviewer packet](PARALLEL-AV-MULTIGOAL-EXECUTION.md) and issue [#302](https://github.com/gamesbyian/general-purpose/issues/302).

## Problem solved by this tool

The model runner [`tools/run_headless_video_description.py`](tools/run_headless_video_description.py) can create a structured **machine-proposed** action/setting/prop/shot/stage-direction object, but output must not automatically become fact merely because it fits a schema. This bridge, [`tools/review_video_stage_directions.py`](tools/review_video_stage_directions.py), takes **a pinned original-video model report** and **a separate reviewer decision file**. It records atomic decisions about one bounded source-video window and produces:
- A compact independent **audit JSON** holding model suggestions, reviewer-authored corrections, original-video attestation, exact source time/window, decision reason and hashes.
- An **optional separate Markdown staging appendix** with only reviewer-attested `proposed_stage_direction` fields accepted or corrected. It never rewrites a held SRT, original untimed S09 paragraph, or main screenplay.
- Counts of accepted, corrected, rejected, deferred and still-unreviewed **fields**, not a fake episode-completion metric. One approved snippet does not imply an entire shot, scene or 193-episode source has been reviewed.

**Editorial attestation is not cryptographically verified independent review.** This tool will *never* emit an `INDEPENDENTLY_AV_CERTIFIED` episode state. Reference movie/caption pointers still need source-time validation and the full independent publication review. S01E01 is source-caption timed, whereas S09E19's 347 original dialogue paragraphs remain **untimed** regardless of what timestamps an AV model proposes.

## Workflow

1. Run the local original-AVI SHA-verified model using a bounded source-once multi-goal packet (≤12 clips) and preserve the output `model.json` in an authorized **private** area, not an ordinary public PR.
2. Read or play the **actual** synchronized source video and soundtrack, with the exact original SHA and requested clip start/end. Use source video, not just the model's stage prose, to make decisions. If no direct source review occurs, **defer** with a reason.
3. Record each decision by `window_id` and one of the ten known fields: `setting`, `camera`, `people_and_positions`, `actions`, `props`, `entrances_exits`, `physical_comedy`, `reactions`, `uncertainty` or `proposed_stage_direction`. Verdict: `accepted` (model suggestion supported), `corrected` (source-observed different prose), `rejected` (unsupported), `deferred` (insufficient evidence).
4. Give accepted or corrected directions **reviewer-authored text**, including where the wording agrees with the model. Rejected/deferred decisions must include a short reason. Source-inspected decisions require `direct_original_video_review_attested: true`; deferred tasks can leave it false.
5. Record the report's actual SHA-256 (`sha256sum model.json`) and exact original AVI SHA in review JSON. Use `--model-report`, `--decisions` and unique output filenames. The tool refuses to overwrite existing evidence and rejects a forged source/video digest or accepted claim.
6. Compare the **stage appendix** with the latest two pilot v5 clean screenplay readers and integrate only source-supported passages through their existing source-aware script build path, preserving dialogue and existing picture observations. Do not directly paste prose into original caption sources.

Example **synthetic illustration** (not a real Night Court observation or proof that an actor did anything):

```json
{
  "schema": "night-court-visual-review-decisions/1",
  "episode_id": "S01E01",
  "source_video_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "model_report_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "reviewer_id": "editor-trial-01",
  "decisions": [
    {
      "window_id": "S01E01-AV-01",
      "field": "proposed_stage_direction",
      "verdict": "corrected",
      "source_window_ms": [1000, 2500],
      "direct_original_video_review_attested": true,
      "reviewer_text": "A figure reaches toward the bookcase.",
      "reason": null
    }
  ]
}
```

```bash
python3 "Night Court/tools/test_review_video_stage_directions.py" -v

python3 "Night Court/tools/review_video_stage_directions.py" \
  --model-report /private/pilot-model-report.json \
  --decisions /private/reviewer-decisions.json \
  --output /private/reviewed-stage-audit.json \
  --appendix /private/reviewed-stage-appendix.md
```

The two hashes in this example are **illustrative**; use the actual original-media and exact full report hashes in a real run. Original model observation wording is retained in the audit JSON alongside reviewer text. In a rejection or defer, no stage prose is rendered. A short motion clip can warrant one action note without establishing entrances from before the clip, character identity from appearance or the larger scene setting.

## Current acceptance & next integration

Synthetic/test-mode policy verifies real source-report/decision SHA matching, exact window matching, explicit reviewer attestation, duplicate-decision rejection, original-video cut-candidate gates, missing model field handling, CLI output immutability and no episode-acceptance promotion. **Zero original episode source-video model descriptions have been adjudicated by this new bridge.**

Next: validate model backend runtime first; measure SmolVLM2/Qwen outputs on short real original-video passages from the already-reviewed 5fps material, include low-change controls and difficult gag windows, then source-review their proposals using this reviewer and compare against existing original-film v5 stage annotations. This is the shortest route from *model claims* to *useful, source-supported screenplay text*, without repeating full-episode ASR.
