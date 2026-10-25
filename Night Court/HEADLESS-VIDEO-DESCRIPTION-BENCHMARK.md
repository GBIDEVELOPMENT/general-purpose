## First executable implementation checkpoint (2026-10-24)

The first headless implementation is in **Night Court/tools/run_headless_video_description.py**, with its source-free test `tools/test_run_headless_video_description.py` and PR-only synthetic video workflow `.github/workflows/night-court-headless-video-smoke.yml`. This checkpoint adds:
- `--backend plan` from a SHA-bearing explicit window manifest **or** the existing `night-court-multigoal-original-AV-review/1` packet; no model/media is needed, zero claims promoted.
- Actual local original-video source hash and ffprobe duration verification before any inference, bounded temporary silent clips (≤12 windows, each ≤15s, total ≤120s, frame and bytes ceilings), and guaranteed temp directory cleanup.
- Lazy local Transformers **SmolVLM2-500M** / **Qwen3-VL-2B** adapters with immutable model revision requirement. These are *implemented interfaces but have NOT been run against owner original video or weights yet*; model/library compatibility and accuracy are still experimental.
- One constrained multi-goal per-clip prompt, strict 10-field JSON proposal parsing, abstention/review routing, per-stage timing and independently-unaccepted results. No actor identification or source dialogue overwrite.

**Offline CI only proves schema safety, reject-by-SHA and real synthetic FFmpeg clip processing with an injected model double.** It is not evidence of real SmolVLM2 or Qwen performance. See the below command examples after the implementation is merged.

```bash
python3 "Night Court/tools/run_headless_video_description.py" \
  --manifest /private/S01E01-review-packet.json \
  --backend plan --output /tmp/nc-vision-planned.json

# On a trusted local worker, after acquiring approved model weights/dependencies
python3 "Night Court/tools/run_headless_video_description.py" \
  --manifest /private/S01E01-review-packet.json \
  --media /private/S01E01-original.avi \
  --backend smolvlm2 --model-revision <40-character-immutable-huggingface-commit> \
  --device cpu --confirm-owner-media --output /private/S01E01-smol-vision.json
```

Substitute `--backend qwen3vl` on appropriate provisioned hardware. Install compatible Torch/Transformers/Decord and the documented per-model codecs **in an isolated, explicitly authorized worker**, not in default PR CI. Use the verified original file from the existing trusted owner workflow once integrated; **do not** have this tool fetch FTP content or place any media in Git. Use private transient report paths until output has been reviewed for sensitive content, unsupported claims and provenance.

# Headless video understanding for Night Court: benchmark and production plan

**2026-10-24 · proposal, not a deployed model or accepted video description.**
Scope: 1984–1992 original series, in the private `gamesbyian/general-purpose/Night Court` tree. Companion: [technology/workflow review](MODERN-TOOLING-AND-WORKFLOW-REVIEW-2026-10-24.md), [AV factory](AV-SCRIPT-FACTORY-PLAN.md), [fast factory](FAST-EPISODE-FACTORY-THROUGHPUT.md), [shot-bounded review](SHOT-BOUNDED-CONTINUOUS-REVIEW.md), [parallel work issue #302](https://github.com/gamesbyian/general-purpose/issues/302).

## Decision and measured starting point

**Decision: benchmark existing headless shot detection + short-video language models; do not build a bespoke video-description model.** Prefer source-once extraction, cheap shot analysis, a lightweight model for the ordinary footage, adaptive escalation for challenging physical comedy, and a timestamped evidence packet that the current screenplay assembler can consume. No automatic audiovisual-certification promotion.

Existing project evidence:
- 193/193 original episodes have held dialogue witnesses and source-only scaffolds (192 timed, S09E19 one **untimed** 347-paragraph witness). Two original-dialogue-complete *working pilot scripts*, **0/193** independently source-AV-certified complete screenplays.
- Original source-once S01E01 pipeline took **239.826s** for FTP source retrieval + checksum, one PCM decode, Vosk + faster-whisper whole-audio recognition, video image-change scan and 212 selected original-PTS JPEGs, **without video-language semantic inference, diarization or editorial acceptance**. S09E19 serial original-source pass was **170.522s** under its separately measured conditions. Faster is not necessarily better unless screenplay-content recall holds.
- S01E01 source AVI stream is **30000/1001 ≈29.97fps**, not assumed cinematic 24fps. Time bases and presentation timestamps must come from each actual verified source. PTS can be repeated or out of decoded order.
- Existing whole-source cut candidates are FFmpeg pixel-score *hypotheses*, not certified shot cuts, scene changes or observed human actions. Existing bounded 5fps physically reviewed sequences total only a fraction of pilot runtime. The newest source-motion extension is [PR #370](https://github.com/gamesbyian/general-purpose/pull/370), with a trusted one-shot source trigger [PR #371](https://github.com/gamesbyian/general-purpose/pull/371) open at planning time. Reuse its result; do not launch competing extraction jobs.

## Tools to trial, deliberately separated by job

| Layer | Candidate | Why / scope | Operational constraint |
|---|---|---|---|
| Headless shot boundaries | **PySceneDetect 0.7.2** (`scenedetect-headless`), starting `detect-adaptive` and `detect-content` | Deterministic CPU-first cuts/fades to benchmark against existing FFmpeg image-change candidates; timestamped cut list | It finds **shots**, not dramatic scenes, intent, or physical actions. V0.7 changed timecode/VFR behavior: use actual source-PTS conversion and a pinned version. |
| Alternative boundary detection | **TransNet V2** | Learned detector only if PySceneDetect/FFmpeg misses significant cuts/dissolves on independently reviewed controls | More runtime/dependency burden. Check exact code/checkpoint rights and CPU throughput before adoption. |
| Cheap video descriptions | **SmolVLM2-500M-Video-Instruct** | Open-weight Apache-2.0 lightweight video QA/captioning; first CPU/memory hypothesis | Its model card reports ~1.8GB **GPU** RAM for video inference; this does **not** prove acceptable speed or 8GB-runner fit on CPU. |
| Quality-oriented video descriptions | **Qwen3-VL-2B-Instruct** | Temporal/spatial video comprehension and text-timestamp grounding, structured description candidates | Benchmark actual batch/resolution/fps/VRAM/quantization. Do not assume it will run well in a standard 2vCPU GHA runner. |
| Escalation quality | **Qwen3-VL-8B-Instruct**, optional **VideoLLaMA3** | Second independent implementation for difficult actions where smaller models miss key gags | GPU-equipped runner/local worker only after a measured quality lift justifies added cost. Not every clip, not every episode. |
| Source decode | Existing **FFmpeg/ffprobe**, current original source SHA/PTS planner | Retain proven source-once decode and existing ≤240 JPEG *baseline* budget | Don't add a second source download. Separate additional continuous-clip budget from initial JPEG budget and measure its bytes. |

Primary upstream: https://www.scenedetect.com/docs/latest/ ; https://github.com/Breakthrough/PySceneDetect/releases ; https://github.com/soCzech/TransNetV2 ; https://huggingface.co/HuggingFaceTB/SmolVLM2-500M-Video-Instruct ; https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct ; https://github.com/QwenLM/Qwen3-VL ; https://github.com/DAMO-NLP-SG/VideoLLaMA3 . Recheck published model licenses, inference compatibility, pinned commits, weight access and security before first download. PySceneDetect 0.7.2 released October 2026; avoid unpinned `pip install --upgrade` in trusted source workflows.

## Source-once execution graph

1. **Preflight**: run from reviewed/trusted `main` only with explicit original-series/rights and owner source access; fetch one source into ephemeral disk, verify expected SHA/length, ffprobe stream cadence/PTS/duration; retrieve held immutable caption/transcript SHA separately. No model/PR-originated workflow gets FTP credentials.
2. **Reuse source**: one scene-cut scan (existing FFmpeg + optional PySceneDetect *comparative* pass); one PCM decode for existing audio lanes; reuse already planned PTS-correct frames and cut proposals. Measure whether parallel independent CPU work on 2vCPU makes elapsed time worse; S09 parallel trial was **242.378s**, slower than older 170.522s and 213.936s serial runs, with changed stages. Serial is current default.
3. **Clip budget**: run whole-runtime coverage of shot transitions and shot representatives; use speech/shot boundaries plus existing action candidates to form short temporally ordered windows. Start 6–15s per window, refine if actions/edits cross a boundary. Include context before/after key actions, never treat a cut-spanning image triad as continuous action. Tag low-motion controls. Extract tiny temporary playable clips or timestamped image groups; bound total decoded frames, inference requests, model tokens and private artifact size **separately** from the existing ≤240 stills.
4. **Caption-neutral model pass**: provide video/frames plus a neutral constrained instruction, **without** leading character names, guessed stage directions or scene synopsis. Ask for visible observations and uncertain alternatives. Maintain visible people as `person_1`, `person_2` until independent source evidence connects a fictional character identity; don't identify actors from images.
5. **Multi-goal single inference** per bounded clip: produce shot/camera notes; room/set and meaningful props; entrants/exits; ordered person/object actions; interactions/gestures/reactions/physical gags; scene-boundary hypotheses; quality/visibility/uncertainty; suggested screenplay stage direction. One result can serve *all* these outputs. Don't infer spoken text, speaker name, voice emotion, sound cues, motives or causality solely from pictures.
6. **Targeted escalation**: trigger Qwen3-VL higher-quality model on disagreeing low-confidence outputs, long/rapid action sequences, suspected gag misses, jump cuts, complex prop transfers and pre-identified editorial highlights. Escalate some low-change samples independently to detect selection bias. Where useful, reframe around a full shot instead of trying to increase sampling without bound.
7. **Fuse existing ground truth**: attach immutable source-caption cue IDs, source-time candidate alignment, anonymous audio diarization evidence and cast-episode roster as *separate* fields. Source subtitles remain presumptive dialogue; never overwrite them with free ASR. For S09E19, source paragraphs remain **untimed**, with only explicitly provisional audiovisual-to-text alignment hints.
8. **Human review packet**: one scene/window packet lets a reviewer adjudicate picture, audio, line, speaker, stage direction and uncertainty at once. Accepted corrections feed new clean reading screenplay output and a linked knowledge-model event, preserving every claim's provenance and rejection history.

## Explicit versioned output contract (prototype only)

Retain the original SHA and source provenance in the top-level envelope, and an array of independent atomic observations. Example shape:

```json
{
  "schema": "night-court-video-observations/v1",
  "episode": "S01E01",
  "source_video_sha256": "<verified-source-sha>",
  "audio_source_sha256": null,
  "caption_source_sha256": "<held-dialogue-sha>",
  "tool": {
    "shot_detector": "scenedetect-headless@PIN",
    "video_model": "HuggingFaceTB/SmolVLM2-500M-Video-Instruct@PIN",
    "decode": "ffmpeg@PIN",
    "parameters_sha256": "<hash>"
  },
  "window": {
    "start_pts_seconds": 100.0,
    "end_pts_seconds": 108.0,
    "frame_timestamps_seconds": [100.0, 100.5, 101.0],
    "crosses_candidate_cut": false
  },
  "observations": [{
    "kind": "visible_action",
    "start_seconds": 101.0,
    "end_seconds": 102.4,
    "actors": ["person_1"],
    "text": "A person reaches toward the desk.",
    "status": "machine_proposed",
    "source_frame_sha256s": [],
    "uncertainty": ["hand partially occluded"],
    "reviewer_decision": null
  }],
  "speaker_identity": null,
  "visual_scene_boundary": "candidate_only",
  "source_media_retained_in_git": false
}
```

The illustrative times/text/hashes above are **not actual episode evidence**. Enforce JSON Schema validation, allowed `kind` values, source sha equality, increasing PTS, clip-span containment, no fabricated timestamps, prompt/model build ID and all results `machine_proposed` pending source review. Optional reported model confidence is not calibrated probability. A per-shot review can reject or split actions; no auto-promotion to independently accepted state.

## Calibration corpus and acceptance (two pilots, not just cherry-picked gags)

- **S01E01 and S09E19**: bounded reference set including established office/courtroom/restaurants, new #370/#371 physical-comedy windows (once available), speech-only/static controls, missed-action low-change controls, fast gestures/props, fades/cuts, entrances/exits, overlapping people, continuity and exceptional untimed S09 dialogue.
- Select at least **12 diverse windows per episode** for first model shootout, then expand adaptively so evaluation is meaningful; include *whole-episode random shot sampling* to estimate missed events. Label the reference set from actual original audio+video review **independent of the model output**. No benchmark validity from machine agreement alone.
- Score cut precision/recall with frame tolerance, **shot-vs-scene confusion**, action/prop/entrance/exit precision and recall, missed-gag recall, unsupported descriptions, false character/speaker naming, timestamp overlap/IoU, abstention calibration, and stage directions accepted per reviewer minute. For dialogue/sound claims, count forbidden inferences.
- Record source retrieval/size, model weight cold start, peak RSS/GPU memory, frame/token count, prompt+inference wall time per window, serialized metadata bytes, end-to-end p50/p95 **only after multiple representative episodes**, dollars / model invocation, and quality-cost Pareto results. Two unique pilot episodes cannot establish population p95.
- **Go/no-go:** choose the **lowest-cost** model meeting independently rated useful screenplay-annotation recall, with no unacceptable hallucinated gags or character attribution. If model doesn't measurably beat the current reviewer packets, don't deploy. A human-usable draft may be generated while strict original-AV publication gates remain 0/193.
- **Performance contract** remains the existing ≤30 minutes p95 for the initial ~24-minute source evidence pass including retrieval (stretch 15m), **not a proven video-language-inference budget**. If models exceed it, stage inexpensive first pass + queued deferred enriched annotation and measure editor time saved; no invisible work or claims of complete source coverage.

## Suggested implementation PR sequence

- **V1, infrastructure**: `tools/benchmark_headless_video_description.py` configurable `--dry-run`, non-privileged synthetic 3-shot fixture and JSON Schema/tests; deterministic shot detector backend contract `existing_ffmpeg|pyscenedetect`; no FTP or model downloads in PR CI.
- **V2, true video understanding**: under approved trusted-owner real-media workflow, pin the smallest model and run 12× two-episode source clips. Keep ephemeral clips/weights in private temporary runners, report only compact source-hash-verified structured observations and metrics. Use pre-existing image/manual reviews as comparison, not as invented model truth.
- **V3, quality & escalation**: alternate small and 2B Qwen model over same held-out clips, external reviewer reference decisions, confusion matrices and playback review packets. Add learned shot boundaries only if errors warrant them.
- **V4, integrator**: JSON-schema-governed stage-direction candidates linked to existing clean screenplay and canonical `KNOWLEDGE-MODEL.md` scene/event references, with explicit rejected/deferred provenance.
- **V5, measured scale-up**: pooled/pinned GPU model runtime if justified, batching and cache by verified `(video SHA, exact PTS, sampled frames SHA, model+revision, prompt/version, parameters)`, backpressure; stage 10+ diverse source episodes before 193-series rollout.

## Safety, legality and operations

Private repo is not a license to redistribute episodes or model assets: only use owner-authorized sources, keep AV and screenshot/voice artifacts private and short-lived per existing policy, respect model/checkpoint/dependency terms, keep a minimal provenance-only retained output and explicit rights caveats for any derived text. Do not put original AVI, WAV, JPEG, voiceprints, weights, FTP passwords or unreviewed copyrighted source exports in PR commits or logs. Don't send original video to an external hosted inference endpoint without separate authorization. Never run secrets in an untrusted PR workflow; use current reviewed-main owner worker. A failure emits a fully resumable reason and leaves source accepted-state unchanged.

**Evidence/source links:** [repo original source-once measurements](FAST-EPISODE-FACTORY-THROUGHPUT.md), [continuity clip-planner limitations](SHOT-BOUNDED-CONTINUOUS-REVIEW.md), [strict publication gates](AV-SCRIPT-PUBLICATION-GATES.md), [current script state](CURRENT-PRACTICAL-SCREENPLAY-DELIVERY.md); upstream links in the tool table above.
