# Source-first directed action evidence: reviewer gate

**2026-10-25.** Actual SHA-verified source-film Qwen tests, comparing standard/compact prompts and 1fps/2fps, repeatedly reversed which person initiated a face-touch in the S01E01 original-source 5fps frame reference. More frames and valid JSON did not solve stage accuracy. This workflow prioritizes **observed physical acts** over model narration.

The source-free `tools/source_first_action_review.py` creates a **private, all-unknown action form** from an exact source-A/V-verified model report and then validates later reviewer annotations. It binds the form to the exact original AVI SHA256, model report byte SHA256, episode ID and exact 2-second source window. It does **not** extract actor names, dialogue, or actions from machine text into any approved screenplay.

The initial form contains one all-`pending` action placeholder. During a **human review of the continuous original film with synchronized sound**, the reviewer can add action records, using anonymous initiator, action verb, recipient/object, visible evidence note, timing/cut note and optional synchronized sound observation. `observed`, `corrected`, `absent`, and `uncertain` require source review; `pending` cannot contain facts. Completion requires explicit moving-video **and** soundtrack review, no pending records and a source-attested reviewer ID. The complete review form remains **private**. Each record is limited in length and count; unknown directional assertions cannot silently be promoted.

```bash
python3 "Night Court/tools/source_first_action_review.py" \
  --model-report "/private/nc-qwen-original-S01E01.json" \
  --new-private-form "/private/S01E01-source-action-review.json"

# After direct original continuous movie+soundtrack review and editing the private form:
python3 "Night Court/tools/source_first_action_review.py" \
  --model-report "/private/nc-qwen-original-S01E01.json" \
  --private-review "/private/S01E01-source-action-review.json" \
  --safe-summary "/private/S01E01-source-action-counts-only.json"
```

The safe summary contains only immutable source/report/review document hashes, source window, reviewer identifier, source-review attestation flags, **counts of pending/observed/corrected/absent/uncertain**, and no copyrighted imagery, dialogue, actor details, action prose or untrusted model wording. It unconditionally sets `stage_directions_automatically_accepted: 0` and `complete_original_episode_certified: false`. Source-review attestation is a reviewer's statement, not cryptographic proof or a whole-episode certificate.

**Editorial next step:** directly play S01E01 **846–848 seconds** and S09E19 **555.8–557.8 seconds** with original synchronized sound, complete source-first action forms, then adjudicate machine statements using existing `review_video_stage_directions.py` and `score_video_description_quality.py`. Preserve original S01 timed subtitles and S09 untimed source paragraphs. No model text can become a stage direction simply because JSON parsed. At present **0 of 193** whole-episode scripts independently source-AV certified.

**Production gate:** measure properly source-reviewed actions and accepted stage directions **per wall-clock editor/model minute** before another bulk CPU VLM or 3fps research factory. This initial implementation adds useful review infrastructure, not evidence that the original film has actually been watched end-to-end.
