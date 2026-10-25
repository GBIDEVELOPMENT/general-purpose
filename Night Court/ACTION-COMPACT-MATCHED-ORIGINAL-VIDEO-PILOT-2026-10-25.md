# Matched original-video action-compact prompt A/B, pre-registered before inference

**Date 2026-10-25. Status: trusted owner workflow implementation; results are NOT yet known.** This is the next source-once controlled test after [physical-business baseline #40230163151](https://github.com/gamesbyian/general-purpose/actions/runs/40230163151) and [compact prompt provenance implementation](ACTION-DIRECTION-COMPACT-VIDEO-PROMPT-EVALUATION.md). The goal is to distinguish **prompt effect** from frame-count effect. We deliberately **do not change video FPS, size, model weights or source window** in this trial.

## Exact original source and control identity

| Dimension | S01E01 | S09E19 |
|---|---|---|
| Original AVI SHA256 | `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962` | `51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649` |
| Episode source interval | **846000–848000ms** | **555800–557800ms** |
| Source review category | physical_business, *not* proven gag | physical_business, *not* proven gag |
| Qwen revision | `89644892e4d85e24eaac8bacfd4f463576704203` | same |
| Video sampling | 1fps / width 256 / silent | same |
| Generated tokens maximum | 256 | same |
| Previous control | valid ten-field JSON, **actor/recipient reversed on 5fps sampled frames** | `non_json_model_output`, physical prop hypothesis incomplete |
| New treatment | **`action_compact` prompt only** | **`action_compact` prompt only** |

**Hard gate:** the new reviewed-main source wrapper aborts **before inference** if the compact-profile clip selector yields any start other than 846000ms or 555800ms, or if the focus isn't exactly `physical_comedy`. The same original movie SHA is rechecked. This means a cut-score/probe variation cannot silently turn it into a different-shot comparison.

The prompt profiles and exact SHA256 digests are immutable code constants in [video model runner](tools/run_headless_video_description.py). The original `standard` prompt/default is unchanged. Existing source-safe numeric metrics now record `prompt_profile` and `prompt_sha256`; any profile-digest mismatch fails closed.

## Owner-only source workflow

Workflow `.github/workflows/night-court-owner-qwen-picture-pilot.yml` accepts an inert marker `Night Court/research/trigger-owner-qwen-compact-action.txt` only from same-repo **`gamesbyian`** branch `research/night-court-qwen-compact-action-trigger`, main base, reviewed-main `github.sha` checkout, no persisted Git token. It invokes `owner_qwen_original_video_pilot.py --focus physical_comedy --prompt-profile action_compact`. No arbitrary PR-head code or arbitrary model prompt is executed under the source secret. Original AVI/audio/frames, credentials and weights are ephemeral/private. One model invocation per source episode; owner results consist of seven-day private unaccepted JSON and **ten all-deferred** reviewer questions with source-safe metrics.

## Acceptance and performance decision

The experiment does not itself prove action accuracy. Require direct original moving-video-and-audio review of both A and B on the same clip and separately grade **who initiated contact, the physical recipient, object handoffs, presence/absence of physical comedy, unsupported scene motives and complete 10-field JSON validity**. Measure token budget and CPU load/inference/tool wall. A compact output could be less verbose yet still make the same role reversal. Success requires **more correctly grounded source-reviewed staging at comparable total CPU/reviewer time**, not prettier text or formal JSON alone. One two-clip paired experiment cannot justify 193-episode deployment; older original transcript dialogue and full episode AV certificate counts remain unchanged.

The control source-data digest ledger is [baseline physical-business record](research/physical-business-qwen-first-source-verified-results-2026-10-25.json); do not overwrite it. After the new one-shot run, preserve exact source/model/prompt/report hashes plus timings, but never commit unreviewed Qwen screenplay prose. Close the marker PR unmerged after evidence collection.
