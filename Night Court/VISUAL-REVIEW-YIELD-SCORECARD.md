# Measuring video models by reviewer yield, not text fluency

**Implemented gate: reviewer-yield comparative scorecard.** Distinct from the separately merged [`score_video_description_quality.py`](tools/score_video_description_quality.py), which scores **independently labeled event-level visual truth** (false positives, misses, abstentions). This complementary reviewer-yield report scores **how many proposed stage directions survive editorial adjudication, at what model runtime cost**, and checks paired original-source windows. Do not conflate proposal acceptance with independent accuracy. Related [headless video benchmark](HEADLESS-VIDEO-DESCRIPTION-BENCHMARK.md), [stage review tool](VISUAL-STAGE-EDITORIAL-REVIEW.md), [work issue #302](https://github.com/gamesbyian/general-purpose/issues/302) and [first real model negative control](MODEL-RUNTIME-SMOKE.md).

`tools/compare_visual_review_yield.py` joins up to four **already-run, SHA-verified video-model reports** with their exact **reviewer-attested stage audits**. It is standard-library, source-free, weights-free, and read-only with respect to all original AVI/SRT material. It records observed model runtime and how many visually supported directions survived editorial review. It **never** treats grammatical fluency, model agreement, self-reported confidence or strict JSON validity as proof of screen truth.

Use after (1) making identical authorized bounded original source clips available to multiple models; (2) running each model; (3) getting a reviewer to accept/correct/reject/defer each source-time observation using `review_video_stage_directions.py`; and (4) preserving the model/audit JSON hashes. **The actual current SmolVLM2 procedural no-person video control hallucinated a suited person**, so the first go/no-go is detecting unsupported objects and persons, not enabling automatic production.

## Input contract

Create an owner-private file such as `/private/video-qa/comparison.json`:

```json
{
  "schema": "night-court-review-yield-comparison-input/1",
  "models": [
    {
      "label": "smolvlm2",
      "model_report": "smolvlm2-model.json",
      "review_audit": "smolvlm2-reviewed.json"
    },
    {
      "label": "qwen3vl",
      "model_report": "qwen3vl-model.json",
      "review_audit": "qwen3vl-reviewed.json"
    }
  ]
}
```

Paths are relative to the comparison file. The audit for each model must include the SHA-256 of that exact model report. Original film SHA and episode ID must match across both. A single model is supported to measure progress, but **fair paired comparative claims require two or more models, identical reviewed original-source time windows, at least one same-field direct source-reviewed decision, and the same reviewer ID**. Even then, the scores measure editorial usefulness on those reviewed clips, not blind population accuracy or proof of whole-film fidelity.

Run:

```bash
python3 'Night Court/tools/test_compare_visual_review_yield.py' -v

python3 'Night Court/tools/compare_visual_review_yield.py' \
  --comparison /private/video-qa/comparison.json \
  --output /private/video-qa/paired-review-yield.json
```

Outputs: number of candidate/identically shared windows and directly reviewed fields, nonempty model hypotheses, accepted/corrected/rejected/deferred fields, **explicitly unsupported rejected observation ratio**, accepted stage directions per model, measured clip inference/decode/tool seconds and **seconds per reviewer-approved stage direction** where defined. It does not infer human review minutes from CPU time. Human review minutes must be measured separately in the full production pilot. It intentionally omits textual source dialogue so that a clean, small aggregated scorecard can be compared without exporting TV scripts.

**Important limitations:** `accepted` means editorially affirmed proposal; `corrected` means a reviewer had to replace a suggestion; `rejected` means editorially unsupported, and is **not** necessarily a formally calibrated hallucination rate. Deferred or absent decisions produce **no asserted accuracy**. A score with only one or two reviewed clips cannot be extrapolated to 193 episodes or p95 production performance. When source windows differ or reviewer IDs differ, the output declares the comparison insufficiently paired. No episode is marked `INDEPENDENTLY_AV_CERTIFIED`.

## Next actual test

After the 256-token SmolVLM2 **negative-control** result, compare (A) simple synthetic human-absence controls and (B) a balanced set of source-reviewed physical-gag, visual-dialogue and low-motion scenes from S01E01 and S09E19. Trial a stronger Qwen3-VL model on suitable hardware, only if its measured quality-cost profile beats the current sampled/manual stage process. Then run the reviewer bridge and scorecard on each paired window. Reject any model that fabricates figures in person-free clips or misses key physical-action beats at an unacceptable rate. Publish **specific improved screenplay passages** after review, not only benchmark metadata.
