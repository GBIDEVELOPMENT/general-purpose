# Current Night Court pilot delivery: latest committed episodes versus published snapshot

**26 October 2026.** Original series (1984–1992), source-dialogue pilot screenplay work.

The **newest episode-editor manuscripts are durably committed and source linked**, but their latest combined automatic publication has **not yet completed**. The previous private canonical snapshot is an older, internally consistent fallback. Do not conflate these two states and do not present either as a fully independently audiovisual-accepted screenplay.

## Latest complete editorial manuscripts on `main`

| Episode | Latest source-first reader | Original speaking-unit refs | Provisional fully named | Contains UNKNOWN | Original reader blocks | Provisional display groups | AV-certified turns |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S01E01 “All You Need Is Love” | **Agent 1 v22** | 404 | 390 | 14 | 405 | 275 | 0 |
| S09E19 “P.S. Do I Know You?” | **Agent 2 v19** | 347 | 273 | 74 | 323 | 234 | 0 |
| **Combined** | | **751** | **663** | **88** | **728** | **509** | **0** |

Direct complete **S01 v22** manuscript: [saved-private/editorial-agent1-v22/S01E01-editorial-screenplay.md](saved-private/editorial-agent1-v22/S01E01-editorial-screenplay.md). Its full matching 405-row immutable-caption source/voice provenance is [saved-private/editorial-agent1-v21/S01E01-editorial-provenance.jsonl](saved-private/editorial-agent1-v21/S01E01-editorial-provenance.jsonl) and remains text/role/segmentation-identical in v22. [v22 manifest](saved-private/editorial-agent1-v22/manifest.json) pins the exact Git blob and evidence digests. There are 27 distinct original-film sampled-picture notes and three of five refinements directly incorporated, with two additional SHA-guarded physical-comedy notes in [v22 stage amendments](seasons/S01/S01E01/derived/editorial-agent1-v22-three-source-picture-stage-patches.json). S01 captured **510 checksum-matched directly inspected original JPEGs** across eleven reviewed sheets, plus earlier whole-episode sampled stills. This is picture evidence, not synchronized original sound/moving film certification.

Direct complete **S09 v19** manuscript: [seasons/S09/S09E19/derived/editorial-v19/S09E19-v19-working-screenplay.md](seasons/S09/S09E19/derived/editorial-v19/S09E19-v19-working-screenplay.md); [full current 323-row reader](seasons/S09/S09E19/derived/editorial-v19/S09E19-v19-editorial-reader.jsonl); [original source provenance](seasons/S09/S09E19/derived/editorial-v19/S09E19-v19-provenance.jsonl); [source dialogue QA](seasons/S09/S09E19/derived/editorial-v19/S09E19-v19-audit.json). **S09 original transcript is entirely untimed.** No original paragraph or soundtrack-derived character identity was invented.

The **exact original dialogue/role crosscheck** of these latest episode artifacts against the previous canonical source reader finds 728/728 original stable reading block IDs in order, exactly six newly context-named S01 reader voices and two newly context-named S09 reader voices, zero new missing original source unit refs, and no source text changes. The 509 proposed display groups are **not** 509 independently certified performed turns; 219 adjacent source reader pairings remain unverified from soundtrack.

## Canonical fan retrieval and automation publication state

The last **successfully persisted and independently source-integrity-tested** `saved-private/pilot-current/` snapshot is **S01 Agent1-v18 + S09 Agent2-v17**: 751 original source units, 655 provisionally named, 96 with unidentified portions, 728 reader blocks, 520 provisional display groups. That index is a genuine historically validated fallback, **not** the latest editorial source. Its private 193-episode fan retrieval reflects the older pilot manuscripts while the newest episode-local v22/v19 scripts can be read directly from their committed paths.

[PR #517](https://github.com/gamesbyian/general-purpose/pull/517) is merged and changes the trusted main-only workflow to regenerate canonical source reading, original-character-span provenance, private UNKNOWN voice review queue, all-193 retrieval, manifests and preserved private artifacts **from latest S01-v22 and S09-v19 together**. The generator explicitly checks the six/two role edits, original subtitle SHA, S01 C219 true source-character split, S09 originally untimed status, original candidate reading text, 27 picture annotations and all zero-AV-acceptance flags, refusing any unexpected source or edition drift. Old [PR #511](https://github.com/gamesbyian/general-purpose/pull/511), limited to S09 v18, was closed as superseded.

**Present external blocker:** GitHub Actions for PR #517 and its merge commit is failing within about 1–2 seconds **before any job's first step**. This includes unrelated standalone source-only, S09 audio and layout workflows. No runner logs or tests were produced by those jobs. The latest canonical rebuild/persistence/193-episode fan-index test is therefore **not verified as executed**, and the publisher deliberately retains the older last validated snapshot. Do not report the expected 663/88 as current `pilot-current` until a successful source-workflow run verifies and commits the exact regenerated snapshot.

## Actual final screenplay acceptance

The user wants **finished practical 1984 and 1992 pilot screenplays**, not a prolonged research exercise. Source dialogue is present end-to-end and the increasingly precise role and physical-comedy reading layers are preserved. Nevertheless, **neither full episode has yet been accepted as an original audiovisual-verified complete screenplay**. There are 14 S01 + 74 S09 source units still containing UNKNOWN voices. Source-first P0 performed turn boundaries, original soundtrack speaker confirmation, exact scene movements and delivery/inflection remain open. The prior acceptance ledger and issue [#441](https://github.com/gamesbyian/general-purpose/issues/441) stay open; no false completion claim or silent role invention is allowed.

**Operational next step:** restore healthy GitHub Actions runners, execute `.github/workflows/night-court-private-working-drafts.yml` on freshest `main`, inspect actual-source test results and ensure the `persist-private-editorial-snapshot` step commits exact current artifacts; after that, continue original-film audio/turn acceptance rather than manufacturing final signoff. If main advances while a run executes, stale-run refusal must prevail.
