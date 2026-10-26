# S01E01 Agent 1 editorial v17: source-conserving screenplay, acceptance, integration handoff

**2026-10-26. Owner: S01E01 lead editor. Status: substantial provisional improvement, NOT finished / NOT audiovisual-certified.**

## Authoritative source and full-text audit

- Recovered `main` post-merge PRs #489 and #499. Source witness: 336 original S01 English SRT cues, SHA-256 `aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496`. The original film fingerprint, from earlier real source work, is `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`; **no source AV watched/listened to in this revision**.
- Read the entire current v16 saved manuscript in chronological order (278 display groups), scrutinized cue-linked held-context candidates, and parsed its entire 405-row provenance to check 404 unique original caption speaking-unit refs. V16 starting count **383 complete named / 21 containing UNKNOWN**; 405 reader blocks, 278 display groups, 127 display joins unverified. Do not use v5/v13/v15 as present baseline.
- Created an immutable-source-linked [v17 editorial decision ledger](editorial-agent1-v17-decisions.json) including every one of the original 21 UNKNOWN voice rows and alternatives; only **two** high-context corrections are promoted. The final v17 private snapshot is at `Night Court/saved-private/editorial-agent1-v17/`:
  - `S01E01-editorial-screenplay.md` (complete 404-source-unit dialogue reader)
  - `S01E01-editorial-provenance.jsonl` (all 405 source-reading blocks, cue windows and original source part refs)
  - `manifest.json` (SHA-256 for both current manuscript and provenance; v16 source hashes)
- **Correction 1, C028.1:** `BULL SHANNON` → `LANA WAGNER`, high contextual evidence from the farewell vocative, Lana's previous instruction and conversational continuity. **Not heard**. Rejoined only the *display layout* for adjacent C027/C028 Lana text, not a verified performance boundary.
- **Correction 2, C101.1:** UNKNOWN → `SHEILA GARDINER`, high contextual evidence: Harry directly addresses Miss Gardiner at C100.2, followed immediately by `- Be right there.` in the first part of original C101 (`419305–421296 ms`). The second part (`It'll cost you 50 bucks`) remains separately labeled Harry. **Not heard**.
- Recomputed complete v17 404 original source refs and 405 reader block coverage, 277 chronological display groups with 128 unverified display joins, **384 fully provisionally named source units / 20 with UNKNOWN**. No immutable text/clock/character offsets changed and no invented subcue timestamps. Original C219 Harry-plus-UNKNOWN source-exact internal split is preserved as two voices within one 879532–882330 ms cue. Original script/provenance SHA-256 digests were recomputed and matched the v17 manifest during generation.

## Whole-episode contextual sequence check

The following are *dialogue-defined editorial sequences*, not camera-certified scene cuts:

1. **C001–C028:** Lana/painter, unknown short greetings, Lana/Bull wordplay, the judge's appointment mystery and C028 farewell. Bull's dictionary-word monologue must retain Lana's interjections. C028 newly corrected.
2. **C029–C077:** incoming deliveries, Harry's unannounced arrival and judge reveal, Sheila and Dan's introduction. Ambiguous brief remarks C061, C066, C073 and C075–C077 remain unverified. Chess/Shecky lines C044 and C047 are already named Lana in v16, although a separate contextual pass hypothesized Dan; evidence is insufficient to overwrite those labels.
3. **C077–C105:** Bull's ceremonial opening continues across captions C077.2–C082.1; Hacksaw arrives, Harry handles the first minor case. C101.1 is now provisionally Sheila. C102–C103 brief court-record/file lines remain unknown.
4. **C106–C144:** Kerr couple fight and introduction, prosecutor's case summary and Harry's attempted coffee mediation. C106 mixed caption has two voices, both remain UNKNOWN pending orientation of Phil/Louise; C107 short speech requires audio. Carla Bouvoir/Bouvier spelling reflects different existing caption/editorial witnesses, not authority to rewrite original text.
5. **C145–C181:** Lana objects, Dan describes judicial oversight, Harry offers magic and argues for unorthodox judgment. Dan's C175.2 is already named; Lana's C180.1 completes an interrupted apology after the failed settlement.
6. **C182–C219:** couple returns, gallery spectator interrupts, Harry uses double-headed coin and talking gambit. Harry's C218/C219.1 syntactic continuation is already named; C219.2 affirmative reply is still UNKNOWN, potentially Phil but not discriminated by textual evidence.
7. **C220–C287:** Harry questions Kerrs' relationship, Carla's solicitation, Phil and Louise make up, coin trick revealed, Selma/Bull closing joke. The existing Phil/Louise identifications are coherent conversationally but original voices still need a real-source review.
8. **C288–C336:** counsel bench, C290.1 unknown consent reply, Dan questions Harry's appointment, Harry's Sunday-home punchline, closing Harry/Lana mutual-respect conversation. Full original dialogue remains accounted for.

## Existing source-film evidence that can be used without guessing actions

`seasons/S01/S01E01/derived/scene-review-v3/scene-script-v3.md` preserves actual reviewed *sampled* source images around 01:22.5–01:28.5: a uniformed adult reaches to a black desk phone, raises receiver, holds it against ear and lowers it. Furniture, bookshelves, folders, dark uniform and lavender clothing are similarly grounded to those frames. That identifies an **observed appearance/prop/action sequence**, without certifying who speaks which subtitle, continuous gestural detail, emotional delivery, scene-wide wardrobe or an exact action recipient. The v17 reader preface links this existing source observation; the full manuscript remains free of fabricated unseen physical comedy or performed-tone labels.

## Known remaining editorial problems

- **P0**: the 128 display group joins are only readability continuations. The whole episode has been *text-read*, **not** independently checked against the original voices, overlap or edited picture. C219.2 is a retained separate UNKNOWN voice; C061, C106 and other short/mixed captions require special playback. Further correct/incorrect turn boundaries may exist beyond currently flagged cases.
- **P1**: 20 original source units still have unidentified speech. Each is individually keyed by original source part, complete cue envelope, contextual alternates and abstention in `editorial-agent1-v17-decisions.json`. All 384 v17 named units, including the new assignments, remain provisional and could contain falsely named turns.
- **P2/P3/P4**: only the bounded source-frame set evidence above has been reviewed historically; no independent episode-wide tone/delivery, wardrobe, action or physical-comedy acceptance is claimed. Revisit actor/action/recipient specifically to avoid earlier reversed-action error.
- **Certification**: no full sound/picture continuous review occurred this session. Episode is **not editorially final**, and distinct independent original-archive certification remains **0**.

## Exact handoff to Agent 3: wire the scoped overlay into current private generation

**Agent 3 owns shared generator changes.** Avoid rewriting the full pipeline or touching S09 editorial material. Apply the two pinned role changes from `editorial-agent1-v17-decisions.json` *after* the current v16 private source-first stage. Regenerate the canonical current S01 working manuscript, 405-row provenance, and `private-fan-retrieval` from the same updated rows, preserving role/provenance integrity. Use the versioned v17 outputs as a bit-for-bit editorial target for S01. Do **not** copy pre-edited prose over changed source, bypass source hashes, or forget that C101 contains a separate Harry turn. Preserve all C219 parts and S09 outputs.

Current pipeline has hard-coded v16 counts in `.github/workflows/night-court-private-working-drafts.yml`, `.github/workflows/night-court-pilot-screenplay-layout.yml`, related validation and publisher assertions. These must be updated **only after actual checked regeneration**, from **651/100 → 652/99 combined provisional source-unit coverage**, **S01 383/21 → 384/20**, **S01 405 blocks unchanged**, **S01 278→277 display groups**, **S09 268/79 and 322 reading blocks unchanged**, **727 combined reading blocks unchanged**, **0 independent accepted voices/turns**, and original SRT hashes unchanged. Keep trusted main-only private artifact publication, isolated PR checks and size/type safeguards from #499. Avoid any publisher racing or overwriting a better edit with v16. No S09 role changes from this branch.

## Scope and verification of this batch

Generated edits applied to the *current saved v16* SHA-matched manuscript, not historical outputs. Checks in the editorial construction included: original v16 manuscript SHA-256 matching live manifest; unique exact text replacement anchors; exactly 405 provenance rows, 404 unique source part refs, 20 UNKNOWN source units, 277 display groups, 128 display continuations, no accepted original-AV flags; SHA-256 of revised manuscript and provenance recorded in companion manifest. The remote branch has real GitHub commits for each new artifact. **These are source-conservation and bookkeeping checks, not a claim of rendered-dialogue performance accuracy.**

Next hands-on priority is original-AVI replay of C028, C101 and C219, then every other UNKNOWN/brief mixed-source cue and the whole episode scene-by-scene. Record any contradictions to these proposed corrections and retract them if the audio disagrees.
