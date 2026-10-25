# Night Court: broader tooling and workflow review (2026-10-24)

**Status: audited proposal, not an implementation or new original-media acceptance.** Companion implementation specification: [HEADLESS-VIDEO-DESCRIPTION-BENCHMARK.md](HEADLESS-VIDEO-DESCRIPTION-BENCHMARK.md). This review uses the live main repository docs/benchmarks and upstream project docs as of 2026-10-24. GitHub issue [#302](https://github.com/gamesbyian/general-purpose/issues/302) already owns much of the time-to-screenplay optimization; this document contributes a **prioritized decision matrix**, not a competing agent queue.

## Goals, hard boundaries and current bottleneck

**Actual project goals** (from README, KNOWLEDGE-MODEL, AV-SCRIPT-FACTORY-PLAN and CAPTION-FIRST-WORKING-SCREENPLAY-POLICY):

1. Private, source-traceable archive/research knowledge base for **all 193 episodes of the 1984–1992 series**: people/characters, events/cases, plots, physical and verbal jokes, historical references, production evidence, archival contradictions and reception.
2. **Useful complete held-dialogue working screenplays first**, with real scene settings, visual stage directions, entrances, physical comedy and legible speaker labels. Separate provisional editorial attribution from independently audiovisual-verified original script fidelity.
3. Later, independently reviewed AV-certified whole-source screenplay/episode evidence, if achievable. Exact media edition, captions, speaker/action/time/sound reviews and acceptance must be auditable.
4. **Fast, affordable headless episode factory**: one verified source acquisition, efficient reuse of audio/visual features, automatic generated candidates, reusable review packet and genuinely better final scripts; avoid multimodel ritual when already-held captions answer the question.
5. Preserve private media/credentials and existing trusted reviewed-main workflow boundary; do not redistribute episode AVI/audio/screenshots/weights via Git or PR artifacts.

**As actually measured:** 193 held dialogue source witnesses (192 SRT; S09E19 original untimed 347 paragraphs); 193 source-text scaffolds; two original-held-dialogue-complete pilot working manuscripts and multiple better reading editions; zero independently AV-certified complete episode screenplays. Most recent top-level README records **298 of 751** pilot speaking units still unidentified after provisional cast-aware editing, although later PRs contain targeted fixes; check each latest manuscript before using that figure as an ongoing metric. Only bounded picture/motion windows have been actually inspected. The source-once first pass has measured 239.826s for S01E01 and 170.522s for one S09E19 serial run, excluding semantic visual inference and editorial labor. The **242.378s** S09E19 parallel trial was slower than prior serial trials and has been reverted to serial default; this is *not causal proof* that concurrency never helps. Source cadence must be probed; S01E01 AVI is 30000/1001fps.

**Real limiting factor:** not missing dialogue transcripts or 10-hour full-episode ASR; it is **observing enough full-runtime visual performance and identifying speaking roles to turn those sources into genuinely readable, believable stage directions**. A separate goal is making the completed archival corpus queryable and useful for analysis; do that after stable evidence/scene objects exist.

## Prioritized tool opportunities

| Priority | Candidate / job | What it replaces or adds | Next evidence gate / constraints |
|---|---|---|---|
| **P0** | `scenedetect-headless==0.7.2` vs existing FFmpeg cut score | Explicit fast-cut, fade, adaptive shot boundaries; makes clip planning, representative image sampling and camera annotations more coherent in **one** pass | First compare **both** on source-PTS hand-labeled pilot shots; no assumption it is more accurate. New 0.7.2 improved VFR/timing fixes but may change threshold results. Shot ≠ dramatic scene. |
| **P0** | SmolVLM2-500M and Qwen3-VL-2B video model shootout | Direct headless natural-language **temporal action/staging/prop/reaction** descriptions; currently missing beyond manual 4/5fps observation | Strong held-out gags + random low-motion controls, measured misses/hallucinations, no automatic actor/voice naming; CPU performance unknown, GPU provision separately. [Detailed trial](HEADLESS-VIDEO-DESCRIPTION-BENCHMARK.md). |
| **P0** | `ffsubsync` **0.5.1** | Newer readily available **non-destructive** SRT-vs-source speech activity offset/framerate/split correction proposals, without another ASR run | On S01/S02 pilot and diverse timed episodes compare model-proposed global / multi-segment shifts to **original soundtrack listening** and held cue alignment. Never silently rewrite immutable SRT or confuse VAD with spoken words. S09 untimed original has no SRT to sync. |
| **P0** | Minimal integrated reviewer packet/editor | One seekable original-AV scene packet with captions, proposed speaker/shot/action/props, frame/clip hashes, alternatives and accept/defer/reject. Existing 11-question JSON is a skeleton, not a reviewed script. | Actual reviewer minutes per useful stage direction, callback from reviews into rendered script, persistent decisions without media in repo. Existing owner-private temporary media can be served to local/offline review only. |
| **P1** | `pyannote/speaker-diarization-community-1` | Whole-audio anonymous turn segmentation, overlap detection and exclusive diarization useful for existing unidentified-speaker backlog | Hugging Face **gated terms/access token**, 16k mono, CC BY 4.0. Verify speaker-embedding diarization error on overlapped laugh-track sitcom passages; **cannot name a character**. |
| **P1** | WhisperX **forced alignment** of held source dialogue | Correct word/phrase time candidates and gap flags; potentially replaces scattered custom Wav2Vec2 timing components, while reusing faster-whisper where appropriate | Restrict to **source-corrected** timestamped paragraphs, verify with spot listening; forced alignment does **not** prove words were spoken or solve speaker naming. S09 original untimed source timing remains provisional until independently matched. GPU/Python requirements and staged package isolation. |
| **P1** | `Silero VAD` / ffsubsync VAD | Cheap speech/activity map, gap triage and speech regions for both audio-sync and targeted audio checks | Compare VAD quality against laugh-track/music/quiet voices before using it to skip regions. Avoid duplicate decode: feature derived from existing one PCM stream. |
| **P1** | NVIDIA Parakeet FastConformer/TDT 0.6B (v2 English / v3 multilingual) | Architecturally different high-quality independent ASR candidate, on a *small selection of disputed lines* rather than default Vosk+Whisper full-episode repeated work | Measure **same-source real language/joke WER** and joint mistakes against independent listened controls; inspect actual NeMo/GPU environment, model terms and runtime. 24m exact limits/chunking caution. |
| **P1** | FFmpeg/AudioSet audio-event model (e.g. YAMNet) | Speech-external *candidate* sound effects, laughter, applause, music/silence transitions to help editors find comedic beats | Weak-label acoustic candidates only: studio laugh track is not proof of an onstage audience, and a soundtrack effect does not establish visual cause. Benchmark false positives vs low-cost audio energy baseline first. |
| **P1** | `SQLite FTS5` (stdlib) or `DuckDB` FTS/Parquet | Query source-linked dialogue, cast, scenes, jokes, cultural/production claims across 193 episodes, without relying on fuzzy LLM recall | Pick **one** index as a derived cache (start SQLite FTS5 for zero extra runtime); immutable provenance and rebuild-from-JSON requirement. DuckDB only when columnar analytical queries need it. |
| **P2** | image/scene embeddings (SigLIP/OpenCLIP) + ANN | Repeated set recognition, visual continuity across shots, candidate same-person clusters, choose review clips | Visual embedding similarity is not a person's identity; sampling/memory/cold-start costs may exceed benefit. Test only after temporal VLM outputs. |
| **P2** | Source-grounded `Fountain` screenplay export | Standard human-editable production-style scene headings, action and dialogue beyond Markdown readers | Add after named dialogue/stage structure stabilizes; export should not mutate original source or collapse provisional labels. |
| **P2** | self-hosted `CVAT Community` reviewer | Full video temporal annotation and multi-reviewer QA when bespoke packet genuinely slows down | Significant hosting and video-handling overhead. No reason to deploy before a lightweight offline scene-packet workflow demonstrates its limits. |
| **Defer** | VideoLLaMA3, Qwen3-VL-8B+, TransNetV2, SAM2 video tracking, actor face models, speculative emotion classifiers | Potential escalation rather than default pipeline | Require a proved missed-gag/shot/identity bottleneck, meaningful quality delta and positive CPU/GPU cost calculation. Prohibit automatic face-to-actor identification without independent contextual evidence. |

Upstream review links: [PySceneDetect release and migration](https://github.com/Breakthrough/PySceneDetect/releases), [FFsubsync current changes](https://github.com/smacke/ffsubsync/blob/master/HISTORY.rst), [FFsubsync audio/subtitle alignment](https://ffsubsync.readthedocs.io/en/latest/how_it_works.html), [SmolVLM2 card](https://huggingface.co/HuggingFaceTB/SmolVLM2-500M-Video-Instruct), [Qwen3-VL](https://github.com/QwenLM/Qwen3-VL), [WhisperX](https://github.com/m-bain/whisperX), [pyannote Community-1](https://huggingface.co/pyannote/speaker-diarization-community-1), [Silero VAD](https://github.com/snakers4/silero-vad), [Parakeet 0.6B TDT](https://catalog.ngc.nvidia.com/orgs/nvidia/-/collections/parakeet-tdt-0.6b/), [DuckDB FTS](https://duckdb.org/docs/current/guides/sql_features/full_text_search), [CVAT](https://github.com/cvat-ai/cvat). These are **candidates**, not evidence of the project installing/running them.

## Higher-leverage workflow changes than another model

### A. Work backwards from finished scenes, not artifact throughput

Per episode, maintain two separate scorecards:
- **Production/editing tier**: source dialogue completeness; percentage of latest screenplay reading units with non-ambiguous, externally grounded/provisional/unidentified headings; real settings/shot actions/entrances/prop gags; sampled physical-comedy recall; number of **completed readable scenes**; unresolved reviewer items and minutes invested.
- **Archival verification tier**: source edition match, direct original audio caption accuracy, source-probed shot and scene coverage, independent character/voice and performance evidence, reviewer-signed acceptance. This remains 0/193 until warranted; no model vote can promote it.

The result of an analysis pass should feed **new screenplay prose** or a definite reviewer decision, not another isolated derived score file. Measure improvements against the current S01E01 and S09E19 clean/cast-aware manuscripts, including current fixes from PRs #364–#369.

### B. Make one expensive operation serve multiple goals

1. **One original AVI transfer and SHA** → video probing, original frame source hashes, PCM, scene-cut boundaries, targeted action clips, source edition record; no second FTP retrieve.
2. **One PCM extraction** → speech activity, subtitle sync proposal, ASR discrepancy review, anonymous diarization candidates, selected prosody, sound-event candidates; independently versioned output slices.
3. **One video clip semantic call** → shot/room/props/entrances/action/reactions/physical jokes/uncertainties/stage-direction proposal, all source timestamped and separately reviewable.
4. **One editor pass through source AV** → accepted/rejected evidence for visual stage, speaker, caption alignment, nonverbal sound, acting delivery, dramatic scene boundary, knowledge-base claims, and corrected script.
5. **One verified structured scene event** → screenplay render, searchable archive, character-appearance proposal, case/plot/joke tag, QA ledger.

Avoid double-decoding through separate workflow jobs when the 2vCPU host gains nothing from parallelism. If shared-AVI audio/video workers are tested again, benchmark **including job startup and dependency/model fetch**, bounded thread counts, peak RAM and safe serial fallback. Cached model weights should be pinned/checksummed and isolated from untrusted PR jobs.

### C. Skip work intelligently, audit the skipped regions

Caption-first policy already correctly allows one routine ASR exception pass rather than two full recognizers for *every* episode. Improve routing:
- Clean timed captions plus no edition mismatch → direct dialogue working draft plus lightweight sync/VAD sample; investigate disagreements, speaker changes and sparse random agreement controls.
- Suspicious gaps/drift, joke wordplay, overlap or guest turn → targeted independent ASR and direct listening; force alignment only after text is selected.
- Video: full-runtime cheap cut/representative pass + stratified low-motion controls; VLM selected windows and expansions for key gags and uncertainties. **Never interpret a shot detector's edit as a whole story scene.**
- S09E19 is exceptional: original 347 untimed paragraphs require source-to-text matching and human review; no artificial original subtitle timestamps.

Abstention and deferred work are normal explicit statuses; unseen moments cannot silently become described actions.

### D. Break the CI/media bottleneck without weakening trust

- **PR code checks:** tiny synthetic AVI/audio, deterministic schema and replay, original dialogue SHA preservation, no FTP, no giant model weights, no untrusted model code, no secrets.
- **Reviewed owner source run:** trusted default-branch scripts only, repository secret isolated, one original checked acquisition, short-lived private media/model cache, bounded resources, source-timed JSON evidence, reproducible provenance. Manual/owner-triggered current workflow path may be used; do not create a new duplicate privileged entrypoint just for a model test.
- **Independent edit/publish:** validate per-claim source links and human review; apply only new reviewed screenplay derivatives; preserve rejected hypothesis history. A single small PR per bounded deliverable; never PR raw AVI/WAV/frames.
- **Retry/caching:** content-addressed by media SHA, caption SHA, sampled exact PTS/frame SHA, model checksum, prompt/schema/flags version. Safe retry of failed *stage*, not entire FTP/ASR job. Keep private short-lived artifacts and a durable small decision ledger; do not mistake expiring artifacts for preserved media.
- **Security:** supply-chain scan and dependency pins, tokens read only on reviewed main, no PR write access to source secret, generated model outputs treated as untrusted data, exact log redaction and explicit rights/legal audit.

GitHub's standard private-repo Ubuntu runner is **2 vCPU/8GB RAM**; eligible larger runners include an NVIDIA **T4 with 16GB VRAM** but have additional cost/provisioning. Default CPU and GPU availability must be verified before choosing a model runner. Sources: https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job and https://docs.github.com/en/actions/reference/runners/larger-runners .

### E. Evaluate with truth, not model agreement or saved files

- **Captions:** stratified blind original-audio sample including comedy proper nouns, invented words, laughter/overlap, late/early scenes and agreement controls; report real WER/coverage and **joint errors even when two ASR systems agree**. Captions are strong presumptive working text, not an independently measured perfect reference.
- **Shot/scene:** shot cut frame tolerance and boundary precision/recall vs source review; scenes need separate dialogue/location/edit grouping and human acceptance.
- **Visual action:** action/gesture/entrance/prop state/physical-gag recall, unsupported causal claims, source time-span alignment and omissions in *low pixel motion* samples.
- **Speakers:** anonymous diarization error and separately reviewed named-character correctness/abstention. Cast credits constrain possibilities, never prove speech in a frame.
- **Performance:** honest observable vocal/acoustic notes vs interpretation. Existing openSMILE/librosa/eGeMAPS lane is already built; no reason to reinstall another emotion classifier by default.
- **Value:** author/reviewer minutes per completed stage-rich scene and objectively improved screenplay readability, plus model inference CPU/GPU time, cold start and cost. Controlled A/B against current script edits, preferably independent reviewer.

## Product roadmap by gate (recommended next implementation order)

**Gate 0: reconcile running work.** Inspect trusted original source clip result for existing [#370](https://github.com/gamesbyian/general-purpose/pull/370) / owner trigger [#371](https://github.com/gamesbyian/general-purpose/pull/371); avoid overlap. Keep [#302](https://github.com/gamesbyian/general-purpose/issues/302) central and documentation links discoverable. Do not merge open blocked legacy PRs #258 or old source-import branches as part of tooling changes.

**Gate 1: inexpensive accuracy quick wins.** Build headless PySceneDetect-versus-FFmpeg shot-reference test on synthetic then source-viewed small clips, and an ffsubsync audio/CAPTION offset *proposals only* benchmark. Neither modifies original captions. Generate one combined time/shot/duration/quality report in a small JSON envelope.

**Gate 2: first true headless semantic stage.** Execute the [video description benchmark](HEADLESS-VIDEO-DESCRIPTION-BENCHMARK.md): two real pilots, >=12 diverse independent-reviewed windows each, 500M vs Qwen 2B; neutral no-character-name visual prompts; measure candidate descriptions, hallucinated props, missing physical business, inference latency, reviewer minutes and per-scene usefulness.

**Gate 3: targeted speaker/word alignment.** pyannote Community-1 anonymous segments and WhisperX alignment in ambiguous **already-caption-supported** clips, with robust overlap/short exclamation abstention. Route ~highest-value unknown pilot speaking blocks to original source listening. Test Parakeet only when independent audio accuracy/control results justify cost.

**Gate 4: complete both pilots as actual stage-rich working manuscripts.** Automatically propose visual descriptions for rest of each episode; independent editorial adjudication, preserve untimed S09 status, scene-completeness/gag coverage audit, republish improved clean screenplay and source indexes, separate production vs archive tiers.

**Gate 5: series-scale factory and knowledge products.** Sample ten or more diverse seasons/editions for quality and elapsed-time distributions before rollout; measure p95 source-first ≤30m per typical episode (stretch 15m) with real semantic cost included. Build derived searchable JSONL/SQLite index from source-grounded scenes/claims; produce episode/character/plot/joke/production/reception matrices. Don't use a retrieval index to invent original source claims.

## Explicit non-recommendations

- No full-episode multi-model transcript competition as default: it makes good research but delays the actual stage directions, given already-held source dialogue and short measured ASR baselines.
- No blind 24fps assumptions, image triplets crossing cuts, single-frame action claims or fictionally exact S09 paragraph times.
- No cloud video transfer, premium API or persistent self-hosted GPU simply because available: require a specific runtime/security/economic advantage and approval.
- No auto-identification of an actor from an image, single-model confidence converted to reviewer truth, or screenplay `INDEPENDENTLY_AV_CERTIFIED` promotion without source AV review.
- No premature massive annotation platform, vector database or elaborate orchestration until two pilot manuscripts become substantially better with a simple reviewer loop.

## Implementation ownership and done criterion

Issue #302 remains the umbrella for throughput and parallel lane measurements. The companion VLM benchmark owns actual headless visual description tests; the existing caption-first and source-AV production plans own screenplay transformations and publication. Each PR must identify an **observable before/after screenplay improvement or measured reduction in work**, exact source provenance, cost and acceptance limitations; only ship changes that survive synthetic CI and evidence inspection. New tools are *proposals* until executed on owner-authorized original videos.
