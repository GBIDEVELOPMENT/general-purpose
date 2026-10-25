## Action direction and parser failure priorities after second real video trial (2026-10-25)

The second exact original-source [Qwen physical-business run](ORIGINAL-QWEN-PHYSICAL-BUSINESS-RESULTS-2026-10-25.md) revealed two expensive failure modes: **a ten-field-JSON-valid model description reversed which participant touched the other's face**, and another expensive two-second source inference returned `non_json_model_output` at its 256-token limit. Existing sampled-image sequences suggest the directional reversal, but **do not substitute for watching the original moving movie with audio**.

The reviewer packet now adds `verify_action_actor_and_recipient_from_original_moving_video` when any `actions`, `physical_comedy` or `proposed_stage_direction` field mentions reach/touch/give/hand/pass/grab/raise/push/pull/point and similar visible interactions. This is a **review request**, never an automatic reverse edit or acceptance. It also surfaces the model's video sampling rate, original parser error code, and generation-token cap, explicitly warning that an incomplete response **alone cannot prove token-cap truncation**. Even if all ten JSON fields parsed, an apparent left/right actor inversion is a serious screenplay quality defect.

These small changes use the **existing single-pass source-once private reviewer packet**, with no new FTP/model downloads, and do not modify actual dialogue or privacy/acceptance gates. Any model claim must remain `deferred` until independently observed in the synchronized original movie.

## Reviewer attention flags from actual Qwen failure modes (2026-10-25)

The source-free [`prepare_video_stage_review.py`](tools/prepare_video_stage_review.py) now adds **heuristic review-priority flags** to each model field in the private Markdown review packet. Every underlying JSON verdict **remains `deferred`** until a reviewer checks the exact original continuous video. This is a reviewer workflow hint, **not a model error detector or an automatically corrected screenplay**.

Rules deliberately focus on patterns observed in the two actual source-video Qwen output reports: speculative words (`may`, `possibly`, `appears to`), supposed unheard conversation or listening/feelings, fine props such as hairpins or pocket squares, and absolute absence claims such as `None` for physical comedy or entrances. A model stage-direction field is **always** marked for source-review rather than safe to copy. Empty fields get a missing-observation warning. The static flags do **not** say that any hypothesized object is absent from original film; they only suggest what to inspect first.

The readable packet also escapes **model-controlled Markdown and HTML syntax**, including inline image/link constructions, so untrusted model output cannot quietly become an executable or externally fetched Markdown attachment in the private reviewer report. The private model JSON itself is untouched and remains usable for exact-SHA audit. No source movie, screenshot or original audio is introduced to PR CI. These changes reduce editorial navigation cost and exposure to untrusted model prose without changing the independent source audiovisual evidence requirements.

## Automated first draft of the review *questions*, not answers (2026-10-25)

The new [`tools/prepare_video_stage_review.py`](tools/prepare_video_stage_review.py) takes an **actual SHA-verified source-video model report**, including reports whose model generated malformed JSON, and creates both an edit-ready JSON decision template and optional human-readable clip-by-clip review packet. **All ten visual/staging questions per clip start `deferred`, with `direct_original_video_review_attested: false`; zero claims or gags are promoted.** This is designed to avoid manually rebuilding a 120-field reviewer queue for every 12-window comparison.

```bash
python3 'Night Court/tools/prepare_video_stage_review.py' \
  --model-report /private/s01-source-model.json \
  --decisions /private/s01-pending-review-decisions.json \
  --review-packet /private/s01-review-packet.md \
  --reviewer-id editor-unassigned
```

A reviewer plays the **actual SHA-matched original picture and audio**, updates `verdict` / `reviewer_text` / `reason` in the JSON, sets `direct_original_video_review_attested` only after direct inspection, and then runs the reviewed stage tool documented below. The Markdown report escapes untrusted model text, surfaces missed-action fields even when the model returned none, and stores **no movie, still frames or soundtrack**. Generating a template is not human review or original-series screenplay completion.

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
