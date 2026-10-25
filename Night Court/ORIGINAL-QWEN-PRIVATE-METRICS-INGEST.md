# Night Court original-film Qwen metrics preservation after private artifact expiry

**Source-free implementation; no original source video analysis claimed by this tool.**

The trusted original-picture micro-pilot in [ORIGINAL-QWEN-SOURCE-VIDEO-MICROPILOT.md](ORIGINAL-QWEN-SOURCE-VIDEO-MICROPILOT.md) can upload one compact **private, seven-day** JSON model report per original episode to GitHub Actions. This private report may include unreviewed textual screen description: it is **not automatically safe for a permanent repository commit**, and the original AVI/frames/audio must never be in the repo.

`tools/summarize_original_qwen_pilot_metrics.py` is the source-free evidence reduction gate. It accepts one or two locally held private result JSONs, validates each original episode/video/source SHA and fixed duration, exact original-source model/trusted pilot schema, exact pinned Qwen3-VL revision, single permitted 2-second source clip, bounded FFmpeg cut-candidate scan, explicit unaccepted reviewer state, source-media-deleted flags and stage timing sanity. It **drops** all model-generated prose, visual fields, misidentified actors, inferred actions, dialogue and private file paths. Its small result contains only source-verified IDs/SHA, source time positions, candidate count, model variant, JSON parse validity and actual timed source acquisition / model load / clip decode / inference cost.

After an actual successful two-episode source job, inspect private artifact reports for unsafe content or protocol failures; then run:

```bash
python3 'Night Court/tools/test_summarize_original_qwen_pilot_metrics.py' -v

python3 'Night Court/tools/summarize_original_qwen_pilot_metrics.py' \
  --report '/private/owner-qwen-S01E01.json' \
  --report '/private/owner-qwen-S09E19.json' \
  --output '/private/nc-qwen-source-safe-verified-metrics.json'
```

Review the derived JSON before selectively committing numeric provenance to `Night Court/research`. The default tool does not read remote FTP, invoke a model, modify a source screenplay or upload any artifact; it never overwrites inputs or output. If the private artifact was never produced, expired, or failed source identity/acceptance gates, do **not** replace it with inferred numbers or fabricated movie observations.

The original Qwen source attempt #40170849365 was a **real source-run failure** because both episodes abstained at conservative image-change cut selection; it had **no successful model report** and therefore cannot be fed to this summary tool. See the next bounded source-window selection experiment tracked by [PR #401](https://github.com/gamesbyian/general-purpose/pull/401). Neither that failure nor a future machine-result JSON authorizes stage-direction acceptance. The strict screenplay publication standard remains 0/193 independently AV-certified.
