## Live post-editorial integration outcome (Agent 3, 26 October 2026)

**Main deliverable commit:** [9193315](https://github.com/gamesbyian/general-purpose/commit/9193315ec26f9ae2b02251a79771ba6d46eafe62). [Successful actual-source CI/persistence/issue publication #40413540356](https://github.com/gamesbyian/general-purpose/actions/runs/40413540356). Both [S01E01 v18](saved-private/pilot-current/S01E01-working-screenplay.md) and [S09E19 v17](saved-private/pilot-current/S09E19-working-screenplay.md) are **current** exact-original dialogue working manuscripts, with current row-level provenance and [editor evidence manifest](saved-private/pilot-current/pilot-current-editorial-manifest.json). The original v16 source reader remains in the snapshot as history; the authoritative integrated reader is `pilot-current-editorial-reader.jsonl`.

**Exact source-unit coverage:** S01 404 original, 384 provisionally wholly named, 20 with UNKNOWN, 405 reader blocks, 276 proposed display groups (129 unverified joins); S09 347 original untimed, 271 named, 76 with UNKNOWN, 323 reader blocks, 244 proposed groups (79 unverified joins); together **751 original, 655 named, 96 unresolved-containing, 728 proposed reader blocks, 520 proposed groups, 208 joins**, **zero independently source-AV verified actor identities or performed turns**. These are independent dimensions. Current private-review packet contains 98 source-reader records covering the **96** unresolved original source units. The original source paragraph/cue sequence is word-and-punctuation-character conserved; exact source SHA pinned for both. The 193-episode current private fan index has **3,151 chunks**, current pilot hashes equal screenplay hashes, and 191 remaining episodes are source-only.

**Integration:** [PR #507](https://github.com/gamesbyian/general-purpose/pull/507) brought committed S01 Agent1-v18 and S09 Agent2-v17 into canonical private generation, all fan retrieval, post-editorial worklist and durable publisher; [PR #505](https://github.com/gamesbyian/general-purpose/pull/505) enforces word-and-punctuation conservation; [PR #502](https://github.com/gamesbyian/general-purpose/pull/502) adds dynamic source/provenance/fan snapshot checks and stale publisher protection. S01 C028/C101 provisional role repairs, C175 context-only same-Dan join and 11 historical sampled original-picture observations persist; S09 has 11 reversibly source-guarded contextual role amendments and exact C291 uncertain split. Independent original audio was not listened to in this integration. S09 remains originally untimed. **Artifact delivery PASS; both full scripts editorially NOT ACCEPTED as final; whole-episode archival audiovisual NOT CERTIFIED (0/2, 0/193).** See [independent acceptance risks and open gates](PILOT-INDEPENDENT-ACCEPTANCE-2026-10-26.md) and keep [issue #441](https://github.com/gamesbyian/general-purpose/issues/441) open.

## Independent integration and acceptance disposition (Agent 3, 2026-10-26)

The [independent two-pilot acceptance review](PILOT-INDEPENDENT-ACCEPTANCE-2026-10-26.md) inspected the committed v16 manuscripts, full SHA-linked provenance, current source review rows and fan retrieval. [Actual held-source CI #40410530501](https://github.com/gamesbyian/general-purpose/actions/runs/40410530501) passed the new dynamic source-integrity validator. Current: **404+347=751** immutable original source units; **383+268=651** wholly provisionally named; **21+79=100** units with unidentified portions; **405+322=727** reader blocks; **278+247=525** display groups with 202 unverified joins. None of these is an independently certified performed-turn count. Both durable private manuscripts and 193-episode fan corpus are already committed. [Merged #502](https://github.com/gamesbyian/general-purpose/pull/502) prevents stale generation writes and verifies evolving counts. **Accepted: artifact integrity and private availability. Not accepted: either complete editorial screenplay or independent original AV certification (0/2, 0/193).** Open P0/P1 source-voice review and P2–P4 scene/physical-comedy coverage are owned by the episode editors; avoid issue closure/status promotion without new evidence.

## Manual-context speaker editorial update, v16 (2026-10-26)

**Current leading private working-draft evidence tier: source-first v16, editorial/dialogue context only, not original-audio-certified.** The older 621/130 and 726 reading blocks above remain valid **v15 input baselines**, not the active downstream v16 output.

| Measure | S01E01 | S09E19 | Total |
| --- | ---: | ---: | ---: |
| Immutable original speaking-unit refs | 404 | 347 | 751 |
| Entire source unit with no remaining UNKNOWN voice, provisionally | 383 | 268 | 651 |
| Source units still having at least one UNKNOWN voice | 21 | 79 | 100 |
| Provisional v16 reader blocks | 405 | 322 | 727 |
| Original soundtrack identities independently accepted | 0 | 0 | 0 |

The private original-caption pipeline performs **32** new provisional reader-block speaker assignments and corrects **two previously named** labels (S09 C305 Alex→Roz, C306 Roz→Alex). Thirty *whole original source units* newly become fully provisionally named. S01 C219 and S09 C206 remain partially UNKNOWN because only one of two voice fragments was contextually identified. **S09 C277 is split into two exact-character, still-UNKNOWN fragments**; source C291 remains role-sensitive and held. The C028 Bull-vs-Lana suspicion and S09 C129 role quarantine remain unresolved. No sounds/frames were independently reviewed by these edits.

The authoring ledger is [research/manual-context-editorial-speaker-review-v16.json](research/manual-context-editorial-speaker-review-v16.json); the generic post-v15 apply/render is [tools/apply_manual_context_pilot_review_v16.py](tools/apply_manual_context_pilot_review_v16.py). All original dialogue and clocks are preserved and the v15 reader is not mutated. The private full-193 fan retrieval now reads the v16 output through the existing working screenplay selector. [Manual-current review queue](tools/plan_remaining_manual_v16_review.py) rebuilds the 100 source-unit P0/P1 review list with source-locator leads; older 130-unit queue stays as a historical v15 QA stage, not current fieldwork.

**Actual scene prioritization:** Source listen to (1) S01 C028 speaker and C219 reply; (2) S09 C277 exact switch and bartender/real Alex cues; (3) S09 C305–306 roles against real voices even though the narrative inference is strong; (4) S09 C129 quarantine; (5) S09 C291 possible intra-cue switch. Then cluster remaining 21 S01 and 79 S09 cue windows, correcting false names as well as unresolved names. Before marking any scene editorially ready, add its photographed stage/reactions and genuinely heard delivery, and independently audit source-conserving performed speaker turns.

# Two-pilot execution ledger (2026-10-26)

**Scope:** original *Night Court* (1984–1992), S01E01 and S09E19. This ledger is the current short operational handoff; the longer documents remain historical evidence. Priority authority: [SCRIPT-PRIORITIES-AND-ACCEPTANCE-2026-10-25.md](SCRIPT-PRIORITIES-AND-ACCEPTANCE-2026-10-25.md).

## Reconciled main (commit 4ecee011, merged PR #482)

| Measure | S01E01 | S09E19 | Combined |
|---|---:|---:|---:|
| Immutable original caption-derived speaking units | 404 | 347 | 751 |
| Current provisionally unidentified original units | 34 | 96 | 130 |
| Current provisionally named original units | 370 | 251 | 621 |

These are **source units**, not audited distinct performed turns. Current private reader proposes **726 reading-turn blocks**, not 726 independently confirmed actor turns. Fifteen original cue positions have been split provisionally; S09 C291 is expressly held for role-sensitive review. S01 C219 now has two distinct UNKNOWN parts inside the **same real timed SRT cue**; never fabricate subcue timestamps. S09 source is an **untimed** 347-paragraph witness. No pilot is editorially complete or independently AV-certified (0/2; fleet 0/193). No newly proposed character identity was independently verified by original-soundtrack human listening.

**Do not accidentally regress to 487/264.** `catalog/current-night-court-original-speaking-unit-coverage.json` is explicitly a **historical v5 baseline** despite its misleading name; its 487/264 numbers are not live attribution counts. V5 picture-based manuscripts remain historical working drafts, not the current speaker-first source of truth. The most recent source-exact generator / queue / FTS handoff is described on the front page of [README.md](README.md). Keep immutable source text and hashes unmodified.

## Finish the pilots, in this order

1. **P0 speaker-turns**: generate the private 726-block source-first reader using the present toolchain and source SHA checks; adjudicate S09 C291 and all other high-risk same-speaker joins / in-cue switches through real source listening, not caption boundaries or dialogue plausibility. Every split and cross-cue join must conserve original source characters and ordered source-part refs.
2. **P1 speaker identification**: use `tools/plan_next_speaker_review_v9.py` for the current 130 UNKNOWN original-unit queue (34 S01, 96 S09). Cluster adjacent scene windows, replay each original AVI once and reuse small source-SHA-bound voice exemplars. Resolve possible falsely named lines too (notably S01 C028.1, “Bye, Bull”). Cast rosters, IMDb/Wikiquote and purchased teleplays provide *candidates*, not independent original-audio validation. Preserve S09 C129 UNKNOWN acoustic quarantine.
3. **Independent P0/P1 acceptance**: log exact original film/audio edition SHA, scene window, actual heard speaker turn and identity, correction or abstention, reviewer and elapsed review effort. Calculate false-name precision and abstention by episode. No automatic claim that a contextual or model name has been heard.
4. **Regenerate two complete readable screenplay drafts** from accepted source-preserving amendments: proper scene sequence, one header per continuing speaking turn, unknown identities intact, source span sidecars and no invented S09 timestamps. Also rebuild 193-episode private retrieval and FTS indexes from that same accepted role ledger, avoiding contradictory versions.
5. **Only after P0/P1**: source-listen for delivery, then source-view props/wardrobe and physical blocking, carefully checking actor/action/recipient (the early Qwen cheek-touch experiment reversed the actor). Keep unsupported claims out of the final script.
6. **Independent final scene-by-scene review**: test complete cue conservation, original caption exactness, correct named character and turns, meaningful performance and physical gags, film-supported scene transitions, no fabricated timing. Update publication ledger only on genuine reviewed evidence.

## Priority and cleanup controls

- One canonical *current* status table; keep old measured historical baselines marked historical rather than deleting them.
- Do not rewrite all source-to-dialogue generators for each new named unit. Use the existing generic role and P0 amendment ledgers and their exact text/hash guards.
- Use shared source-once decodes and brief clustered reviewer packets, not slow redundant full-film VLM passes. The currently demonstrated Qwen motion-direction errors make unsupervised stage narration a poor use of time.
- Do not merge unrelated **FTP video rename plans** PR #163–165 without explicit source-path coordination; do not merge unrelated Plex PR #99 as Night Court cleanup. These are deliberately held separate from current dialogue processing.
- The old issue #441 body describes the superseded 490/261 stage; its live unresolved workload is **130**. Issue #302 is a performance research backlog, subordinate to finishing actual P0/P1 pilot scenes.
- No new original audiovisual acceptance was performed as part of this desk/repository reconciliation. A repository-only pass cannot establish the real actors or complete the two pilots by assertion.

## Immediate success measure

Every review pass should reduce **source-audio-adjudicated uncertain speaker spans**, correct false identities where found and increase completed **whole scenes**. Merely increasing the provisional named counter is not a success metric. The deliverable is two accurate, readable, fully source-reviewed pilot scripts fit to teach a deeply informed fan persona, with private reusable provenance and complete original dialogue retained.

## Newly working: readable private screenplay drafts (same date)

The [source-preserving private renderer](PILOT-WORKING-SCREENPLAY-RENDERER.md) now generates both working dialogue manuscripts from the current v15 private source reader, plus one exact-block provenance JSONL per episode and SHA-bound numeric manifests. The actual-source original-caption CI [run #40389885348](https://github.com/gamesbyian/general-purpose/actions/runs/40389885348) succeeded: **S01E01 405 original-reader blocks displayed in 284 provisional groups; S09E19 321 displayed in 260 provisional groups; 726 original-reader blocks total**. [Synthetic privacy/identity tests #40389885234](https://github.com/gamesbyian/general-purpose/actions/runs/40389885234) also passed.

This work discovered that the v15 source-role reader can interleave older S01 cue rows after S09 rows. The new renderer restores **source cue and cue-part chronology for display only**, while keeping the input reader bytes and original source part refs unchanged. It refuses to join two portions of the **same original caption cue**, even when they share a provisional character. Scene settings, identities, delivery, physical business and original AV acceptance remain *unresolved*; 284/260 are **not** proof of actual performed-turn counts. Full dialogue drafts are generated only into private temporary paths, not committed. Next required gain remains reviewed P0/P1 roles and turns, especially the 34 + 96 UNKNOWN source units.
