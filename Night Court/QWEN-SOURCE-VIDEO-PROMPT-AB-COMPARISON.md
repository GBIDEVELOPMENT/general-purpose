# Compare Qwen action prompt A/B without publishing private model prose

After the [pre-registered exact original clip trial](ACTION-COMPACT-MATCHED-ORIGINAL-VIDEO-PILOT-2026-10-25.md), a useful result needs to prove the two candidate passes used **identical source frames** before measuring a structured-output or CPU-speed difference. The source-free tool `tools/compare_original_qwen_prompt_ab.py` accepts two **existing private original source-video JSON reports**, one from the unchanged `standard` prompt and one from opt-in `action_compact`. It uses the strict existing `summarize_original_qwen_pilot_metrics.source_safe_record` to reject wrong original full SHA, wrong Qwen revision, unpinned prompt, forged source/actor/screenplay review flags or wrong episode-candidate time range.

It separately requires the original source edition and exact two-second `start_ms/end_ms` to agree, with identical `video_sampling_fps`, `video_width_pixels`, 256-token cap, model ID/revision, duration and `physical_comedy` research focus. Any mismatch **fails closed** instead of giving the appearance that changing prompt wording improved a different shot. Both immutable prompt SHA-256 values and raw private input-report SHA-256 are retained. It records strict ten-field JSON status, exact parser error if any, load/inference/tool wall seconds, treatment-minus-control runtime and optionally whether the disposable encoded clip SHA is identical. **A matching encoded clip SHA is an integrity signal, not proof of native original video frame PTS or source audiovisual truth.**

```bash
python3 "Night Court/tools/test_compare_original_qwen_prompt_ab.py" -v

python3 "Night Court/tools/compare_original_qwen_prompt_ab.py" \
  --standard "/private/owner-standard-S01E01.json" \
  --action-compact "/private/owner-compact-S01E01.json" \
  --output "/private/S01E01-prompt-ab-safe-metrics.json"
```

The same applies to S09E19. The output includes **no generated model description, screenshot, soundtrack, transcript text or reviewer narrative**. The tool never uploads original media, overwrites an input, invokes an LLM, or claims to have watched the original film. It unconditionally sets `direct_original_moving_video_review_complete: false` and `model_factual_action_quality_comparison_established: false`. Those gates can be upgraded only by the separate original-moving-picture-and-audio direct human review tools.

This comparison is a production *decision aid*, not a shortcut to an episode screenplay. If the compact variant returns valid JSON where the control did not, that is a structural improvement only. If it still reverses the original agent/recipient action, it is a poor screenplay source regardless of fluency. Measure reviewer-approved staged *physical actions per total model/editor seconds* before trying to scale across 193 episodes.
