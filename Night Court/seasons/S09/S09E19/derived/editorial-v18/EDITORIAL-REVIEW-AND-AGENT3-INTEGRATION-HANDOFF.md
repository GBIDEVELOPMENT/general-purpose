# S09E19 source-exact editorial v18 | October 26, 2026

**Status:** Additional chronological P0/P1 **dialogue-only editorial** completion from the now-integrated canonical `main` v17 script, plus evidence-scoped picture observations inherited from original-source review packets. It is not original sound or continuous-motion certification. Original untimed S09 source SHA-256: `659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2`.

## Recovered state and concurrent owners

Agent 3 had already merged [#507](https://github.com/gamesbyian/general-purpose/pull/507) and [#508](https://github.com/gamesbyian/general-purpose/pull/508), integrating S01 v18 and **S09 v17** into the durable `saved-private/pilot-current` reader, manuscripts and fan retrieval. This investigation started at live main commit `eb3b4aab91c9706207205e7eacd6a6592a4490bd`, reading `pilot-current-editorial-reader.jsonl` and its manifest. The input reader SHA is pinned as `88aee05506d7b85c23f61b767180d8a5a8e2466d044885e6f7815f13bb2205be`.

Agent 1 retains S01 editorial ownership, Agent 3 retains shared manifests and integration. This PR exclusively creates files in `S09E19/derived/editorial-v18/`. **Do not use this output to quietly modify the shared pilot paths or historic v16 baseline.** This v18 S09 draft should supersede S09 v17 **only after Agent 3 runs exact-source cross-checks and rebuilds the canonical private artifacts**.

## Defensible new P0 and P1 decisions

### P0: three previously fragmented anonymous continuations

1. **C002→C003**: “No problem” followed by a complaint about monotonous servile campaign work plausibly forms a single sardonic response. The proposal marks **the same anonymous actual speaker**, rather than guessing Dan, Bull or Mac. **Medium** contextual confidence and no sound review.
2. **C235→C236→C237**: the same first-person restaurant observer establishes a couples-watching premise, judges the hired substitutes' chemistry, and predicts a hot night. Consecutive source paragraphs plausibly compose one performed utterance. **High contextual** confidence, but **UNKNOWN** remains the voice identity.
3. **C238→C239**: the reply acknowledges the hot-night prediction and completes a contrasting arson punchline. Treat as one different anonymous reply/turn. **High contextual** confidence, but no speaker name invented.

These create four fewer editorial **display groups** while conserving **all seven original unaltered paragraph texts** and never declaring a performed-voice join certified from film.

### P1: two additional source-grounded provisional identities

- **C051.1 -> CHRISTINE SULLIVAN**, previously UNKNOWN: Christine's C046 question invites Roz to describe her pen pal; Roz tells her about Alex's outlook, this is the natural job follow-up, Dan jokes about the answer immediately afterward and Christine asks about their impending meeting at C054. **High narrative-context**, not AV-verified. A different on-scene questioner remains a viable alternative.
- **C229.1 -> THE GUY (PLAYING ALEX)**, previously UNKNOWN: The paid male stand-in asks Lisette about her fictional art collection at C227; she hesitates C228, and the opening “Well...” is the natural lead-in to that same stand-in's C230–C231 specific suggested topic, eighteenth-century Florentine neoclassics. **High contextual**, and the continuous-turn reading now places C229 with C230–C231. It does **not** transfer the real Alex's identity to his hired actor.

The prior v17 repairs are retained without reinterpretation: C287 Alex asks “Who was she?”, C288 Roz asks “Who was he?”, C291's first `He. ` remains UNKNOWN while `He was me.` retains the earlier provisional Alex label; C305 Roz, C306 Alex; the two-voice C277 snack split and presumed bartender/Alex handoff; and C129 acoustic quarantine.

## Whole-episode status and conservation

| Measure | Canonical v17 prior | Episode-local v18 |
| --- | ---: | ---: |
| Original untimed dialogue units | 347 | **347** |
| Editorial reading blocks | 323 | **323** |
| Entirely provisionally named units | 271 | **273** |
| Source units still containing UNKNOWN voice | 76 | **74** |
| Display groups | 244 | **239** |
| Independent original audio-confirmed actors or performed switches | 0 | **0** |

The generated `S09E19-v18-editorial-reader.jsonl` retains each exact original v17 `reading_block_id`, `caption_text` and `original_source_part_refs` with **no character changes**. A second in-memory comparison across **all 323 v17 original blocks** passed equality of full string characters and ordered part refs. Every source original unit C001–C347 is represented, and both original source SHA and `source_original_times_ms:null` are checked. The per-cue disposition index enumerates all 347 references after the edits. The original v16 C291 split remains exactly as inherited.

No subtitle timestamps are invented and no speech/audio/actor/picture acceptance changes. All v18 editorial grouping hints use explicit anonymous turn keys, not false named-role credit.

## Physical source picture context that is actually supportable

The screenplay's final evidence appendix includes existing source-still observations from `derived/source-photo-scene-overview-v1/observations.json` and `derived/physical-motion-original-v1/observations.json`. These document (1) a courthouse bench and book-lined office; (2) a **5fps original-image** sparking-floor incident with smoke and two unidentified people shielding behind a partition, sampled around original-video offset **684–704s**; (3) a burgundy-dressed woman dancing with a tall suited man in a restaurant, from **951–971s** sampled original images; and (4) later book-lined office images. The original 347-paragraph text is **untimed**, so those source-video offsets must never be promoted into synchronized line times or used to establish actual character voice, igniter, actor/action/recipient, or frame-accurate motion. This session did **not** newly view or listen to that original material. The stable sidecar observations are traceable to earlier recorded original-image evidence.

## Remaining editorial and soundtrack work

The 74 current units with UNKNOWN contain substantially different kinds of uncertainty. Closely review:

- **Early campaign scene C001–C009:** cannot safely infer which staff member responds to the flyers or asks about the filmed commercial just from occupation or scene attendance.
- **Office safe scene C097–C124 and closing payoff C339–C347:** masked or malformed responses, speakers possibly Harry/Dan, but actor-voice differences needed. The short exclamations should stay UNKNOWN.
- **C128–C130:** Harriet's mistaken ad and lime-green Pacer suggest same-speaker continuation but the original audio-model **C129 quarantine remains enforced**.
- **C188–C193 and C206–C215:** garbled mixed-voice dialogue, possible interjections and misidentified performance boundaries.
- **Restaurant observers and impersonator negotiations C222–C265:** an anonymous speaking-turn pattern is clearer, yet actual observers' identities and character attendance remain ambiguous. C225–C226 should not be stereotyped as Roz without sound.
- **C269–C291:** the money handback and nested pronouns leave potentially three speaking voices within C271, and prior inferred split points require targeted original film review.
- **C332/C334:** credited guest role “Man” is a candidate for a campaign supporter's remark, but cast-list presence cannot uniquely certify that on-screen voice.

**Next source-first gate:** listen to original AVI soundtrack windows around the anonymous restaurant spectators and real Alex/Roz encounter, verify every proposed join, and inspect original moving video for gestures and physical gags. Record exact original media SHA, source-aligned interval, observer, accepted speaker switch and actor→action→recipient for each certified claim. Retain genuine ambiguity when listeners cannot independently decide.

## Committed v18 artifacts and integration recipe

- `s09e19-editorial-v18-amendments.json`: original-source SHA-pinned guarded role edit and anonymous P0 join ledger.
- `S09E19-v18-editorial-reader.jsonl`: regenerated S09-only 323-line reader with reversible role and anonymous voice keys.
- `S09E19-v18-working-screenplay.md`: full 11-sequence screenplay with explicit source-evidence-only visual appendix.
- `S09E19-v18-source-provenance.jsonl`: every reader block and new display group traced back to v17 original IDs and source text.
- `S09E19-v18-manifest.json`: counts and immutable source guarantees.
- `S09E19-v18-all-347-cue-disposition-index.json`: source-complete 347-unit review results.

**Agent 3 integration:** consume S09 v18 only if the exact previous v17 current reader SHA and 323 per-row IDs, text and source-part refs still match; re-evaluate the original subtitle character-conservation test, regenerate `pilot-current-editorial-reader.jsonl`, current S09 manuscript and full retrieval, adjust counts from 655/96 combined to **657/94** while retaining S01 v18's 384/20 and 405 blocks, keep S09 323 blocks (combined 728), and persist validated outputs through existing durable mechanism. Do not touch `pilot-manual-context-speaker-v16.jsonl` or represent this evidence as original audiovisual acceptance.

This is progress toward **a useful finished episode**, not a declaration that 74 UNKNOWN voices are solved or original film performance has been reconstructed.
