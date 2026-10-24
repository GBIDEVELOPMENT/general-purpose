# S01E01 audiovisual editorial acceptance packet

**Status:** implementation under PR review; existing original-series evidence is preserved and immutable. Scope is exactly 01:00–01:30 from the previously fingerprinted S01E01 AVI, not a full episode or finished screenplay.

## Why this stage exists

The first multimodal script [v3](seasons/S01/S01E01/derived/scene-review-v3/scene-script-v3.md) combines original dialogue, 4fps motion observations and measured mixed-soundtrack acoustics, but still has **no verified named speaker**. The two [independent-model word proposals](seasons/S01/S01E01/derived/scene-review-v3/word-timing-model-comparison.md) have matching timing candidates for 37/39 jointly proposed source words within 300ms, but they share an earlier ASR-based segmentation window. Neither method constitutes independent listening or source-cut acceptance.

The new `tools/build_s01e01_editorial_review.py` prepares a deterministic, evidence-linked review dossier, joining:
- all 11 existing source caption speaking turns and 55 original source words from C19–C27;
- exact per-word tiny.en vs Wav2Vec2 CTC timing proposals with missing/timing-disagreement flags, preserving unusual comic words;
- the ten existing per-utterance mixed-TV-audio pitch and loudness summaries, never character-specific emotion labels;
- six frame-hashed motion observations over the 75–90s interval, with explicit caveats that sampled frames do not prove precise continuous motion;
- source SHA-256 for both the English SRT and the approved original AVI.

Outputs in `seasons/S01/S01E01/derived/editorial-review-v1/`: `acceptance-worklist.json` (source-linked review tasks and blank decisions) and `acceptance-worklist.md` (readable priority queue). The editor can check failed/missing word candidates and visual actions without having to collate five previous research outputs manually.

## Editorial decision integrity gate

`tools/validate_editorial_decisions.py` creates an all-PENDING JSON template for the 11 original dialogue-turn tasks and six physical-action checks, then validates any future completed editorial decisions against the exact source AVI/SRT SHA and original-source time range. Its adversarial tests reject invented speaker names from cast/wardrobe, expressive delivery from mixed pitch alone, stage-motion acceptance based only on stills, altered original source hashes, missing original cue tasks or unaudited decisions.

- A **voice text** acceptance must include an identified reviewer's explicit attestation of listening to original audio **and** checking the preserved source caption.
- Naming a **speaker** further requires synchronized continuous video/mouth-to-voice evidence; cast credits or a costume alone are never enough.
- A **vocal delivery** acceptance requires a separate original source listen and self-attested isolated-voice review. Numerical F0 alone is not an emotion label.
- A **physical stage direction** acceptance requires the reviewer to attest to continuous-video review. The original 4fps source frames can be used for pre-review observations, not independently timed full-action claims.

The validator checks *record format and source provenance* only. A person could falsely report having listened or watched; **reviewer identity and evidence quality are not cryptographically verified**, and valid JSON is not automatic truth. The template is deliberately pending, with zero accepted claims. The next editorial run must be authorized, source-linked, and independently QA-checked before any character/performance script is declared correct.

## Hard acceptance boundary

**Zero speaker identities or voice performances are automatically accepted.** Every speaker, word-timing, vocal-delivery and stage-motion review field is deliberately `not_reviewed`, `null` or `false`. Nearby sampled images supply only contextual timing, not proof that the visible individual spoke. No model agreement becomes a certified word timestamp, and no vocal pitch contour becomes sarcasm, anger or emphasis without separate evidence. Original caption source bytes stay untouched.

The offline CI tests every source hash, all 55 word indices, model-time categories, 60 sampled-frame evidence hashes, eleven source turns and six visual-motion tasks before committing the compact derived packet. No video transfer, credentials, speech model or network access is required.

## Next real editorial work

1. Independently listen to difficult 60–90s voice turns, especially C19, C22's two speakers, C24's unusual vocabulary and C27's excerpt edge, checking subtitle fidelity and start/end boundaries.
2. Align distinct acoustic voice turns and identify characters only after actual voice/face corroboration. Production roster credits and clothing alone are not sufficient.
3. Independently review short continuous video passages around the 82.5–88.5s telephone action and all other six motion notes. Record onset and acting reactions separately from sampled-frame inference.
4. Extend independently verified source-cut timing across early/middle/late episodes without inferring it from a 30s scene alone. A separate S01E01 sparse-drift workflow is being pursued in the repo and should not be duplicated or interfered with here.
5. Compile production-facing scene headings, dialogue, performance directions and temporal action only when each editorial claim has an accepted evidence pointer and review decision. Then assess full episode completeness.

The dossier is a step toward proper scene scripts, not an assertion that the pilot is complete.

## Source-time evidence integrity hardening (October 23 continuation)

The earlier reviewer-decision validator checked the source AVI SHA and whether an evidence clip fell anywhere in the episode, but did not require the cited clip to include the **specific source speaking turn or visual observation** being accepted. A valid source hash and a review of the wrong minute could therefore satisfy a text, voice or stage-action acceptance method. The tightened validator now requires **each evidence method on an accepted decision** to contain the full original source-caption interval (voice tasks) or sampled-observation interval (visual tasks). Rejected / needs-recheck decisions may retain partial investigative observations, but they cannot confer an acceptance. Synthetic tests reject unrelated clips, one-millisecond truncations at either edge and Boolean timestamp values.

This deliberately exposes the boundary of the existing **01:00–01:30** pilot: C19 starts at 00:58.912 and C27 ends at 01:31.074. A reviewer must inspect the original source **outside** the sampled excerpt to accept either complete caption turn. A 30-second model-generated excerpt cannot validate those margins. The interval check is mechanical provenance hygiene, not proof that a reviewer truly watched or listened; all 17 live decisions remain PENDING and no speaker, inflection or action is promoted.

PR verification uses a small read-only, no-FTP-secret CI check on a designated same-repository branch rather than reusing an older merged feature branch or altering the credential-bearing media workflows.
