# Sampled stills versus Qwen claims: cautious source-image triage

**October 25, 2026.** Companion to the [first successful original-video Qwen run](research/first-original-qwen-two-pilot-source-safe-metrics-2026-10-25.json), [reviewer packet](VISUAL-STAGE-EDITORIAL-REVIEW.md), [independent original-video quality labels](VISUAL-MODEL-QUALITY-SCORECARD.md) and [editorial yield](VISUAL-REVIEW-YIELD-SCORECARD.md).

## What source samples already show

An independent partial visual inspection was performed using the owner's existing **SHA-linked source-derived still frames**, **not the original AVI moving image and synchronized soundtrack**. For S01E01, the verified original-AVI-SHA-derived dense frame archive covers 75–90 seconds, 4fps, with nominal timestamps, individual JPEG SHA-256 and exact evidence-index SHA `4bdeeebb64b3f33c1c4dff50354266f7655546ece23fa713c7b3b59818b237d7`. The Qwen window 77–79s is sampled by eight sequential stills at nominal 77.00, 77.25 ... 78.75s. For S09E19, an existing derived contact-sheet PNG with local material SHA `2e5e906b71fcd1e8ec1debdb1b2a87ae0a55c4cdd1042742a1007673e5051037` covers several nominal 5fps frames around the 812–814s window. **Neither nominal sampling grid has independently original-frame-PTS-verified timestamps, and neither proves what occurred between successive samples.** Source film edition SHA is separately verified by the actual original-model run.

- **S01E01 77–79s:** the eight frames visibly support a uniformed man in the midground with a curly-haired woman in lavender at the edge/foreground and bookshelves/woodwork. Camera framing appears steady across the sample sequence. Those frames do **not** license a precise assertion about a police-station setting, the woman's unseen posture, dialogue, a confrontation, tension, intentions or an independently verified continuous two-second shot. The model's yellow hairpin/accessory, exact expression and reaction details are less certain than the general costume/positions. A stage direction announcing a confrontation would require evidence that is **not available in sampled stills**.
- **S09E19 812–814s:** sampled frames visibly support a bearded, suited man seated in foreground, with other figures visible behind; the framing stays similar. A burgundy/reddish tie appears, but a separately asserted **red pocket square** is not clearly established. A table and glass of water are not established by the cropped still reference. The model's explanation of a ballroom or social gathering, conversation, attentiveness and motives is not a verified observation. Facial/head-angle changes are observable across samples, but cannot authenticate speech or a specific physical gag.

**Crucial:** absence of an object, entry, edit or comic action from a sparse frame grid is NOT evidence it never occurred between samples. Neither episode has even one complete source-movie reviewer-accepted model staging statement on the strength of this triage. 0/193 independently complete original AV-certified scripts.

## Executable source-bound triage without changing source truth

`tools/triage_video_model_sampled_stills.py` lets a reviewer classify **all ten existing model fields** using source-matched sampled-picture evidence, while enforcing an exact immutable **original AVI SHA**, exact model report byte SHA and exact local source-sample index/image byte SHA. Each of the ten classifications is one of:

- `visibly_consistent`: at least the field's substantive claim is consistent with inspected pictures, not proof of complete motion.
- `mixed_claim`: field combines supported visual objects/framing with an additional unsupported or unresolvable assertion.
- `contradicted_in_samples`: the sampled image actually contradicts a positive claim, **not** merely something unpictured.
- `unsupported_interpretation`: a motive, cause, conversation, setting category or unseen action inferred beyond sampled imagery.
- `not_resolvable`: neither positive nor negative can be fairly decided from sampling.
- `model_absent`: model's entire string field is empty.

The review JSON follows `night-court-sampled-frame-claim-review/1`; it records `episode_id`, `source_video_sha256`, `exact_model_report_sha256`, `sampled_source_material_sha256`, `window_id`, `reviewer_id`, `sampled_stills_visually_inspected: true`, `original_moving_video_reviewed: false`, `original_soundtrack_reviewed: false`, `native_frame_pts_independently_verified: false`, `episode_independently_certified: false`, `nominal_sampling_fps`, sorted `nominal_sample_times_ms`, and exactly ten `field_reviews` containing `field`, `status`, `sampled_frame_observation`. All inputs are **private** because field notes and model report contain unreviewed scene text.

```bash
python3 "Night Court/tools/test_triage_video_model_sampled_stills.py" -v

python3 "Night Court/tools/triage_video_model_sampled_stills.py" \
  --model-report "/private/S01E01/nc-qwen-original-S01E01.json" \
  --sampled-review "/private/S01E01/sample-image-assessments.json" \
  --sample-material "/private/dense-frame-index.json" \
  --output "/private/S01E01/sample-only-numeric-result.json"
```

**Only the sanitized result is suitable for an ordinary repository ledger**, and even that needs review. Output retains source hashes, nominal sample count/time, and individual field `sampled_frame_status` classification and category counts, **not model prose, sampled-frame notes, copyrighted source imagery, soundtrack, actor identifications, or original subtitle text**. The program *always* marks `reference_is_original_full_motion_video: false`, `source_video_editorial_staging_approved: false` and `quality_accuracy_or_model_recall_established: false`. It actively rejects any input claiming otherwise or spoofing the original/video-report/sample bytes.

This task is deliberately a **third, lesser evidence tier**, not a shortcut through the existing stronger tools. `score_video_description_quality.py` still requires genuine directly original-moving-picture reviewed source references before producing visual accuracy claims, and `review_video_stage_directions.py` requires genuine original audiovisual review before permitting an editorial stage direction. A sampled still cannot sign either of those attestation fields. Use the private sample analyses to identify risky fields and ask better human review questions, not to automatically upgrade a screenplay.

## Engineering and production implications

From this first two original windows, the model is capable of describing room/people composition but tends to mix that useful visual material with inferred plot or conversational significance. **Proposed next trial:** a negative-control prompt explicitly discouraging motives, room-purpose guesses, absent props and tone. Compare a short constrained *visual observation* output against the current ten-field free-text form **on exactly matched source windows**, before spending more CPU time across complete episodes. Require 10/10 field coverage, identical original source SHA, numeric run wall time and independent moving-film review before claiming improved quality. Reuse private original source once per episode, keep model outputs bounded, and prefer human acceptance over model majority voting.

