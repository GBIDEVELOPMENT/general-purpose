# S01E01 Agent 1 v19: five additional provisional voice identities

**Episode scope: S01E01 only. Date: 2026-10-26.** This artifact advances the fully preserved v18 source-picture manuscript. It does not imply finished audiovisual editorial acceptance, soundtrack-recognized speakers, exact performed turns, or authenticated delivery/tone.

## Exact S01 artifacts on main after merge

- **Complete, further corrected source-dialogue screenplay:** `Night Court/saved-private/editorial-agent1-v19/S01E01-editorial-screenplay.md`
- **Its complete matching 405-row original-caption provenance:** `Night Court/saved-private/editorial-agent1-v19/S01E01-editorial-provenance.jsonl`
- **New reversible v19 contextual voice decisions:** `Night Court/seasons/S01/S01E01/derived/editorial-agent1-v19-five-speaker-context-decisions.json`
- **SHA-256 digests, invariants and status:** `Night Court/saved-private/editorial-agent1-v19/manifest.json`

| Source speaking ref | v18 | v19 | Confidence *kind*, why |
| --- | --- | --- | --- |
| C010.1 | UNKNOWN | **BULL SHANNON** | Medium-high textual: a greeting after painter is expelled, immediately before Lana explicitly greets Bull |
| C011.1 | UNKNOWN | **PAINTER** | High textual: complaint about being almost done has a specific interrupted-window-watching antecedent for painter |
| C084.1 | UNKNOWN | **DAN FIELDING** | High textual: an unfinished address to judge leads into Dan's continuous courtroom-procedure objections after Harry's visual prank |
| C102.1 | UNKNOWN | **LANA WAGNER** | High textual: fine amount must be entered and court clerk Lana has been told to work on Hammond's case |
| C103.1 | UNKNOWN | **LANA WAGNER** | High textual: the case-file handoff follows Lana's clerk instruction and fine recording, with Harry closing case |

These are **five new source-unit provisional names, not five independently heard voices**. They are anchored in immutable cue refs, immediate dialogue, scene participation and episodic role definitions; the evidence ledger retains plausible alternatives for every attribution. In particular **C010 Bull remains medium-high, not certain**. No combined roles are propagated from chronology alone.

## Conservation gates checked at write time

- 336 source SRT cues unchanged; immutable source SRT hash `aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496`.
- 404 distinct source speaking-unit *reference keys* in original reading provenance unchanged; 405 private reader rows remain because C219 has an extra logically split reply with the same source ref.
- **389 fully provisionally named** source speaking units, **15 containing UNKNOWN**, an exact partition of 404. The 405 rows include a source ref that occurs once as Harry and once as an UNKNOWN reply: do not naively count all nonnull rows as fully named source units.
- 276 provisional display groups and 129 AV-unverified presentation joins, unchanged from v18.
- v18's 11 staged original-picture observations, unique `PIC-01` through `PIC-11`, preserved exactly. C175's two original subtitle parts still share one Dan *display* unit without invented subturn timestamps, retained from v18.
- Zero newly soundtrack-verified voice identities; zero newly acoustic-validated display joins; original film not replayed to support five P1 amendments. Do not add tone or direction claims beyond existing source-picture observations.
- No edits to S09, original captions/media, shared parser/generator code, automatic publisher or private fan index in this S01-specific PR.

## Cross-episode integration: Agent 3

**Check newest live main before touching the shared generator or canonical `pilot-current`.** On branch creation, Agent 3 had incorporated v18 S01 and v17 S09 into the private canonical scripts and 193-episode retrieval index, and the published two-pilot status was 655 named/96 UNKNOWN. Agent 2/3 may have since integrated further S09 revisions. Never downgrade S09 or overwrite the shared index with an older source.

Incremental S01 **only** patch to canonical, starting from exact hash-matching v18: C010.1 null→Bull, C011.1 null→Painter, C084.1 null→Dan, C102.1 null→Lana, C103.1 null→Lana. Regenerate both complete canonical screenplay **and** provenance from the source/decision layer; update SHA-indexed 193-episode fan retrieval and all derived counters; validate against true source quotes/fingerprints and test persisted main-only private artifacts. The role overlay should reject unexpected original speaker values, changed original cue text and SRT hash mismatch, preserve source-read exact clocks, C219's partial UNKNOWN, P0 C175 join and 11 visually sampled notes. Do not merely copy formatted text and silently desynchronize publisher source/provenance.

**Projected combined count conditional on S09 retaining 271 provisionally named/76 UNKNOWN:** 389+271=660 named / 15+76=91 containing UNKNOWN of 751 source units. **If S09 changes, recompute its figures from live evidence; do not reuse these example totals.** Per-episode S01 acceptance: 0 actor voices/turns originally soundtrack-certified, 0 completed full-episode source-AV review.

## Remaining 15 unidentified S01 rows

The current source-part roster remains C061.1, C061.2, C066.1, C073.1, C075.1, C076.1, C077.1, C094.1, C106.1, C106.2, C107.1, C124.1, C125.1, C219 reply and C290.1. High risk: speaker orientation of Louise/Phil in Kerr argument C106–C107, possible Dan/Lana/Sheila court interjections in C094/C124/C125, C219 short separate voice. Leave UNKNOWN when original audio or stronger external attributed textual material is absent. Verify all 69 multipart source cues and 129 same-speaker presentation joins from film audio; P0 is the user's higher-order priority.

**Actual editorial completion remains blocked on independent complete original-film audio/video validation and frame-supported acting/performance and scene directions; this manuscript is a genuine complete dialogue-source reader but not yet a finished screenplay.**
