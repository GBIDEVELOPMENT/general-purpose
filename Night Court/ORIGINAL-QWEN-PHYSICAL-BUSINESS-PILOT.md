# Night Court: source-once physical-business Qwen follow-up (2026-10-25)

**Implementation scope:** second original-film Qwen micro-pilot, focused on visible body/object business rather than first original verified source Qwen's mostly static two-second composition clips. **Nothing here certifies that a gag actually occurs in the candidate window or that Qwen can recognize it.**

The first actual completed original-video Qwen run was [#40225712304](https://github.com/gamesbyian/general-purpose/actions/runs/40225712304): S01E01 77–79s and S09E19 812–814s, valid 10-field JSON with largely compositional/interpretive observations. The subsequent [source-image sampled triage](SAMPLED-STILLS-VLM-CLAIM-TRIAGE.md) confirmed the principal visual figures but exposed unsupported motives, room assumptions, and unverified props. It did not examine original synchronized moving AV.

## Tighter, physically interesting samples

We used pre-existing **SHA-linked original source-derived 5fps visual-contact evidence**, which is stored privately, to choose the next practical two-second candidate windows. The source-frame windows and ordering are fixed code allowlists:

- **S01E01, judge-bench hand/coin business neighborhood:** prospective starts **845.8s, 846.0s, 845.6s, 846.2s or 847.0s**. The already reviewed original-still window covers 838–858s. Nearby stills show a woman in lavender at the court bench and a judge raising a hand toward her. Frame-pair differences in candidate start 845.8s peaked near **8.9 mean grayscale levels** at 5fps in the *JPEG sample proxy*. We have **not established** that the moving source contains a particular coin trick, sound cue, continuous edit or successful comic beat.
- **S09E19, courtroom bench close object-handling neighborhood:** prospective starts **555.8s, 556.0s, 555.6s, 556.2s or 559.0s**. Original still collection 551–571s shows a suited figure manipulating/indicating an object near another seated person. Candidate 555.8s peak was around **6.2** mean 8-bit grayscale levels in existing JPEG proxies. Again this is not proof of the original shot's exact motion or visual gag.

These are *candidate* windows only. The trusted source path will download each pinned original AVI once, verify SHA-256, run the existing **5fps gray 160×90 difference** gate on up to five fixed candidate starts, abstain if all fail, and run exactly **one 2-second silent Qwen3-VL-2B video inference per episode** (1fps, 256px width, 256 generated tokens). One sampled source + one model pass supplies people, props, physical motion, entrances, reactions, setting and provisional stage-direction hints without separate model calls.

**Important test limitation:** 1fps on a 2s excerpt yields only two sampled frames, potentially missing an action *between them*. This is an intentional cost-controlled baseline. A later 2–3fps trial or cheap frame-difference extrema selection should be justified by observed missed visual beats, not by automatic assumption that more frames are better. Neither the 5fps conservative selector nor the two sampled VLM frames can certify uninterrupted shot or camera continuity.

## Source security and dispatch

- Fixed original AVI allowlist and exact full-file SHA-256 from [the owner-source runner](tools/owner_qwen_original_video_pilot.py); no arbitrary downloads.
- `--focus physical_comedy` is **a research cohort flag**, not a declaration that physical comedy was observed. The default `--focus observational` preserves the first trial's static video offsets.
- The trusted workflow accepts a new inert trigger `Night Court/research/trigger-owner-qwen-physical-comedy.txt` only from exact same-repository account `gamesbyian` and branch `research/night-court-qwen-physical-comedy-trigger`, based on current trusted `main`, never the untrusted PR head. The prior observational branch is still separately hard-allowlisted for compatibility but should not be reused without an explicit new owner one-shot PR.
- Secrets enter only the fixed original AVI retrieval step, and original video/audio/frames/model weights are **not** retained. Seven-day **private model hypothesis + deferred review questions + numeric-safe metrics** bundle, 18-minute maximum job, and separate cheap CI lane.
- No dialogue cue, especially S09E19's **347 untimed source paragraphs**, gets fabricated source times based on model output.

## Independent acceptance after the run

1. Verify checkout SHA, exact original AVI hash, sampled model revision, source window, candidate counts and non-upgraded audiovisual state.
2. Compare the *actual original moving clip with soundtrack* against every Qwen field, including physical-comedy and props, using [deferred reviewer decisions](VISUAL-STAGE-EDITORIAL-REVIEW.md). Do **not** promote a stage paragraph based on stale visual stills, sound-free inference or character-list knowledge alone.
3. Use [event-truth scorer](VISUAL-MODEL-QUALITY-SCORECARD.md) to count misses/false positives and [editorial-yield/runtime comparator](VISUAL-REVIEW-YIELD-SCORECARD.md) to decide if Qwen is economically useful against manual stage directions.
4. If any supported stage direction is accepted, incorporate it in a **new source-preserving derivative working screenplay**, not in held original SRT/untimed dialogue witnesses. 0/193 complete independently source-AV-certified episode scripts remains unchanged.

**Decision threshold:** if 1fps Qwen cannot distinguish the significant original action from a static pose, keep expensive model inference selective and benchmark higher temporal sampling on only a few clips or alternative cheaper visual-action algorithms. Do not enable unreviewed mass inference across 193 episodes.

