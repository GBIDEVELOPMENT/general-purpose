# Original Night Court pilot delivery, actual published state

**26 October 2026, updated after organization transfer, successful original-source CI, and one-pass review work.** This file supersedes its former GitHub Actions and stale-canonical blocker report. Older named editorial manuscripts remain in Git history for provenance, not as active episode files.

## Verified canonical source-first products on private main

[Latest working manuscript and provenance directory](saved-private/pilot-current/) was published by [full successful private publication run 40441814247](https://github.com/GBIDEVELOPMENT/general-purpose/actions/runs/40441814247) and reverified by the subsequent source-stable [run 40444379513](https://github.com/GBIDEVELOPMENT/general-purpose/actions/runs/40444379513).

| | S01E01 | S09E19 | Combined |
|---|---:|---:|---:|
| Canonical integrated edition | Agent1-v22 | Agent2-v19 | |
| Original source speaking refs | 404 | 347 | **751** |
| Original reader blocks | 405 | 323 | **728** |
| Proposed displayed turns (not verified performed turns) | 275 | 234 | **509** |
| Unverified proposed caption joins | 130 | 89 | **219** |
| Adjacent reader-block P0 source boundary decisions needed | 404 | 322 | **726** |
| Unknown-containing source units | 14 | 74 | **88** |
| Independently original-AV-certified actors and performed boundaries | 0 | 0 | **0** |

Both canonical manuscript SHA256 digests and the 193-episode **3,153-chunk** private fan index were independently crosschecked after actual successful main publication:

- S01 `85ff8bfb7408b8ddf731bf21980724ff913973cef7bbcd9eb094506fd41fd5c5`
- S09 `da9ed43ff498d46471248c33cc56c16602149afc2989223825f735ea4ced2f5a`

The original episode evidence is still incomplete with respect to source-listened voices, continuous motion, performance and original full-film acceptance. The source caption/transcript witnesses are conserved in exact order with SHA guards and may not be replaced by invented dialogue.

## Current faster path to original-AV acceptance

[ONE-PASS EPISODE FINISH](ONE-PASS-EPISODE-FINISH.md) is now the production entry point, not 20 numbered versions or five handoff agents. [Offline source-film workbench](episode-finish-workbench.html) can load exact-dialogue private packets and a locally owned original episode video, then export one editor ledger covering every adjacent P0 join/break, P1 identity, P2 delivery, P3 wardrobe/props and P4 actual physical action. One current canonical screenplay and one private episode decision file should be maintained instead of new numbered script editions.

- [S01 current one-pass original-AV packet](saved-private/episode-finish-current/S01E01-one-pass-av-review.json): **34** sequential playback batches, **405** reading blocks, **404** adjacent P0 decisions, exact dialogue SHAs and source-caption candidate clocks.
- [S09 current one-pass original-AV packet](saved-private/episode-finish-current/S09E19-one-pass-av-review.json): **27** sequential playback batches, **323** reading blocks, **322** adjacent P0 decisions; immutable **untimed** original source. The saved [original-audio source locator](saved-private/episode-finish-current/S09E19-original-audio-locators.json) reuses the original-film ASR lexical matching of **231/347** untimed paragraphs. All 27 review batches have at least one original-audio candidate seek hint. These hints are *not verified source cue timestamps, speaker identities, or performed turns*.

The single [one-pass GitHub workflow](../.github/workflows/night-court-episode-finish.yml) follows, via explicit dispatch, only after the existing canonical private [publisher](../.github/workflows/night-court-private-working-drafts.yml) has succeeded. Its [first successfully chained current packet run 40443791289](https://github.com/GBIDEVELOPMENT/general-purpose/actions/runs/40443791289) and [S09 locator persistence run 40444421357](https://github.com/GBIDEVELOPMENT/general-purpose/actions/runs/40444421357) passed. They do **not** run speech recognition anew for every manuscript edit and do not confer AV certification by virtue of successful GitHub Actions tests.

## Still open, without euphemisms

**0 of 2 pilots are finished to the requested audiovisual/performance standard.** Actual continuous synchronized original-film listening/viewing and source-bound editorial decisions are still required. Independent review remains mandatory for the source-voice or shot uncertainties; the software's packet/decision validators can enforce completeness and SHA linkage, but cannot prove somebody truly observed the moving audiovisual evidence. Do not close overarching screenplay acceptance [issue #441](https://github.com/GBIDEVELOPMENT/general-purpose/issues/441) until the performed turns, voices and material staging have been adjudicated and incorporated in the **same** final readable screenplay.
