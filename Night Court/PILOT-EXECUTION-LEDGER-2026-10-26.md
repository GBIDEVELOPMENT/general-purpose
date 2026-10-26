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
