# Visual model accuracy scorecard and original-source negative controls

**2026-10-24.** Executable quality scoring for bounded video-description experiments. This is **source-free infrastructure**, not an accepted original *Night Court* episode analysis. It follows [the real SmolVLM2 negative-control evidence](research/smolvlm2-256-token-negative-control-2026-10-24.json), [headless video experiment](HEADLESS-VIDEO-DESCRIPTION-BENCHMARK.md), [review-to-script bridge](VISUAL-STAGE-EDITORIAL-REVIEW.md) and [issue #302](https://github.com/gamesbyian/general-purpose/issues/302).

## What is measured

`tools/score_video_description_quality.py` joins an actual `night-court-headless-video-description/1` model report with **independently source-reviewed labels** for the exact same episode, original AVI SHA-256, model-report SHA-256 and bounded source windows. Every reference event must be observed and documented without trusting the model's wording. It scores:
- True positives: visible event actually present and claimed.
- False positives: reviewer confirms an event/prop/person/scene element **absent**, yet the model claimed it (including negative-control hallucinations).
- False negatives: reviewed source event present but model missed.
- True negatives: reviewed absent object/action correctly not claimed.
- Explicit `unclear` cases: separate abstentions; the model receives neither false credit nor forced incorrect labels. Unclear on a real event reduces measured recall.
- Precision of explicit positive claims, recall against observed events, false-positive rate on **reviewed negative controls**, JSON structural success, inference time per window, breakdown by action/entrance_exit/prop/physical_comedy/reaction/setting/camera.

Metrics requiring no matching reference examples are `null`, NEVER `0` errors or (100%) accuracy. Calculated rates apply **only to labeled windows**, not an entire episode, series, or original film. A `reviewer_id` and `direct_original_visual_review_attested: true` are bookkeeping, **not** cryptographic proof of genuinely independent human review. Full episode certification stays false.

## Input contract

The first input is an actual model execution report; synthetic fake data may be used only in offline tests. The second is `night-court-visual-quality-review-labels/1`, a reviewer-written JSON with original edition SHA, exact model JSON raw-file SHA, reviewer identifier and `observations`.

An example (entirely **synthetic**; no original TV episode or verified human video event):

```json
{
  "schema": "night-court-visual-quality-review-labels/1",
  "episode_id": "S01E01",
  "source_video_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "exact_model_report_sha256": "<SHA256 of model-report.json bytes>",
  "reviewer_id": "reviewer-synthetic-01",
  "full_original_video_coverage_verified": false,
  "observations": [
    {
      "window_id": "W1",
      "event_id": "no-window",
      "source_window_ms": [0, 1500],
      "kind": "setting",
      "reference_truth": "absent",
      "model_claim": "present",
      "direct_original_visual_review_attested": true,
      "reference_note": "The independently inspected test pattern has no physical window."
    },
    {
      "window_id": "W1",
      "event_id": "no-human",
      "source_window_ms": [0, 1500],
      "kind": "entrance_exit",
      "reference_truth": "absent",
      "model_claim": "present",
      "direct_original_visual_review_attested": true,
      "reference_note": "The test pattern has no person."
    }
  ]
}
```

The `model_claim` field is **a reviewer classification of what the model actually output**, even if the untrusted response failed JSON parsing. No string-matching heuristic is allowed to automatically turn words like `person` into confidence or claims: `no person` also contains `person`. Every reference must be tied to a source window and make its negative/positive truth basis explicit. Reference classes are `action`, `entrance_exit`, `prop`, `physical_comedy`, `reaction`, `setting` and `camera`; claim labels are `present`, `absent` and `unclear`.

```bash
python3 "Night Court/tools/test_score_video_description_quality.py" -v
python3 "Night Court/tools/score_video_description_quality.py" \
  --model-report /private/original-S01E01-vlm-run.json \
  --reference-labels /private/source-reviewed-reference.json \
  --output /private/S01E01-model-score.json
```

Outputs are explicitly **non-certified**, never overwrite existing source/model/review files, remain small and record model/report/label SHA and measured throughput separately. **Do not commit original frames/audio or private visual captions to PRs.** Retain numerical aggregate/reviewer provenance only after checking rights and sensitive content.

## Rollout decision

The actual first 256-token 500M trial described a nonexistent suited person/window on a generated empty-of-people pattern. That is a negative-control failure in one example, not a statistical false-positive rate across sitcom material. The scorecard must be run over a stratified reference corpus (true actions, physical comedy, quiet dialogue, fast cuts, blank/low-motion controls) on both pilots and multiple source episodes before selecting a headless model as a bulk script annotation backend. Compare Qwen3-VL-2B or other appropriately provisioned models with the **same** windows and **blinded** source reference labels; track stage directions accepted per reviewer minute alongside these metrics.

Real source video analysis still requires a separately trusted reviewed-owner pipeline and must reuse already planned source-once packets. No 193-episode inference or unattended stage publishing is approved by synthetic CI.
