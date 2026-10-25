## P0 review-validator implementation checkpoint

`tools/validate_speaker_turn_reviews.py` now exports an unreviewed template from a proposal JSON (`--proposals <file> --output-template <new-file>`) and strictly validates a completed-or-partially-unresolved review file (`--proposals <file> --reviews <file>`). Every boundary must be present exactly once; attested same-speaker/speaker-change/overlap decisions require original audio/AV evidence kind, nonempty source location, matching original SHA and reviewer attestation. Unresolved boundaries remain explicit; this validator cannot mark a whole episode AV-certified. Synthetic tests are in `tools/test_validate_speaker_turn_reviews.py`. This is **a validator and template**, not proof that source listening occurred. Run both new test modules with `cd 'Night Court/tools' && python -m unittest test_propose_speaker_turns test_validate_speaker_turn_reviews` and retain observed results.

# Current Night Court two-pilot execution handoff (2026-10-25)

**Scope:** original 1984–1992 series. Work only in `Night Court/` unless a precise trusted workflow change is needed. Never change the Shaw, Glimpse or unrelated media applications. Reconcile latest main, issues, PRs and source hashes at start, not historical SHAs.

## Owner-authoritative order

Read [SCRIPT-PRIORITIES-AND-ACCEPTANCE-2026-10-25.md](SCRIPT-PRIORITIES-AND-ACCEPTANCE-2026-10-25.md) before starting: **P0 authentic speaker-turn segmentation**, including same-speaker caption merging and multi-speaker cue splitting; **P1 character naming**, **P2 performance/tone**, **P3 wardrobe/props**, **P4 stage action/blocking**, **P5 precise timestamps (low)**. Shot/action reversals remain material review escalations. Caption word timing is source navigation, not the purpose of the screenplay.

## Verified repository reconciliation

As of this inspection the latest known main included PR #427 (first provisional, non-destructive turn-boundary sidecar). Historic source-reader report [CURRENT-PRACTICAL-SCREENPLAY-DELIVERY.md](CURRENT-PRACTICAL-SCREENPLAY-DELIVERY.md) says the best existing **source-only working screenplay readers** are:

- S01E01: `seasons/S01/S01E01/derived/cast-courtroom-reading-screenplay-v3/screenplay-courtroom-cast.md` and `courtroom-source-index.json`: **336/336 original SRT cues, 404 candidate speaking units, 306 provisionally named, 98 unknown**.
- S09E19: `seasons/S09/S09E19/derived/cast-continuity-reading-screenplay-v3/screenplay-cast-continuity.md` and `continuity-source-index.json`: **347/347 original untimed paragraphs, 347 candidate speaking units, 147 provisionally named, 200 unknown**.
- Thus **298/751 source-derived speaking units remain unnamed** in those versions. These are not independently listened-to speaking turns or verified identities. P0 merging/splitting may change denominators.
- Both working manuscripts preserve original dialogue, with bounded sampled-picture and cast-context research. Neither is independently whole-episode AV certified; current archival count **0/193**. More recent files may exist: compare generation/manifests/source SHA and substantive contents before naming the "latest" output.
- Prior source-once AV benchmark: S01E01 **239.826s**, S09E19 **170.522s** and **213.936s** measured on different runs, excluding runner setup/model install and human review. They do not establish complete screenplay production time or p95.
- S01E01 caption baseline **336 timed cues**. S09E19 witness is **347 untimed paragraphs**; do not fabricate per-paragraph timestamps. The two-source fingerprint constraints remain pinned in existing tools and manifests.

## Open PR and issue reconciliation (2026-10-25)

GitHub API revealed **five open PRs**:

- **#258**: real source S01E01 36-second tiny.en word hypotheses and C28 discrepancy. Historical handoff explicitly says safety-blocked; **do not merge or bypass** without checking current safety/CI and independently reviewing artifact constraints. Extract/transfer safe evidence via a newly validated path if needed; preserve the original branch.
- **#163, #164, #165**: planned original-video FTP moves for all seasons, deliberately held because they change episode media paths. **Do not merge while AV tooling references old FTP names**. First implement an exact path-migration compatibility/redirect plan and reconcile with live source inventory, then run trusted owner-path test.
- **#99**: unrelated Plex metadata for other television shows; do not merge in Night Court work.
- **Issue #302** remains open and correctly describes unfinished end-to-end parallel audiovisual evidence throughput and actual continuous-action acceptance. Keep open until measured objectives are met.

No suitable PR/issue was closed by this review: blocked source evidence, deliberate FTP holds, unrelated media, and incomplete performance objectives must not be falsely marked finished.

## Immediate practical pilot acceptance queue

**A. One source of truth for current readers (both pilots).** Verify latest renderer code, derived reader, cast attribution lineage and episode source SHA. Do not regenerate using the earlier caption-first-v1 script and erase later cast/scene improvements. Preserve exact original caption wording, order, and many-to-many original cue lineage.

**B. P0: start with conversation-unit boundaries.** Run `tools/propose_speaker_turns.py` separately for S01E01 and S09E19, creating local/private derived review packets. The current tool merges only adjacent explicitly matching source speaker labels on short gaps, and abstains for unlabelled adjacent cues. It **does not** establish true diarized turns; inspect known multi-dash within-cue alternation and long same-speaker speeches. Incorporate proposed candidate turns into a human/AV-review decision schema, explicitly recording `merge / split / different speaker / overlap / unresolved` with source unit and cue IDs and exact evidence. Never use the fact that two caption segments are next to each other as proof they have the same speaker.

**C. P1: use speaker identity evidence.** In turn order, resolve unknown candidates with verified spoken audio, episode credited cast/guest roles, acoustic consistency and picture lip/action context. Existing provisional source-context names are **not gold**. Inspect speaker confusion pairs and note when inferred names are withdrawn. S09 cast caution: credited James McDonnell character Alex and Alex Henteloff character 'The Guy' are different people.

**D. P2: delivery.** For each confirmed turn, perform short source audio listening for meaningful delivered tags: exasperated, sarcastic, confused, coy, hesitant and mechanically audible whisper/shout/pause. Align change of inflection to part of turn only as necessary. Do not infer sarcasm solely from caption wording or promote soundtrack pitch/loudness statistics to performance truth.

**E. P3: useful costumes and props, then P4 physical blocking.** Use verified source picture, sparse shot-aware candidate frames and targeted continuous original-video review. Recognize cut boundaries; record actor, action, target/recipient, location, shot/scene and relevant prop. Specific source known issue: automated Qwen original-source picture description repeatedly **reversed initiator/recipient in an S01E01 cheek-touch gesture** even when FPS increased. Never paste unreviewed vision model descriptions directly into a script. Identify silent reactions and physical jokes that no audio/caption system captures.

**F. Two independent completion gates.** A *useful editorially ready script* needs coherent character-attributed dialogue, supported delivery, scene settings, and material physical/prop continuity; an *independently AV-certified episode* requires true whole-film audio+video evidence and review of omissions per [AV-SCRIPT-PUBLICATION-GATES.md](AV-SCRIPT-PUBLICATION-GATES.md). Neither may be reached by generating more derived files alone.

## Source-safe execution principles

- Read owner original AV sources once per task when feasible; verify AVI/source caption SHA, gather multiple measurements from the same transient download, and avoid storing original video/audio/stills, original dialogue dumps, model weights or unapproved sensitive data in public artifacts.
- Build independent transcript/acoustic/photo interpretations on their own evidence; do not train a second ASR directly on captions and call agreement independent.
- Selectively review disputed words, ambiguous turn boundaries, guest speakers, scene shifts and important physical gestures before dense compute. Use existing original source-once evidence, manifests and short exact-hash windows.
- Time initial evidence passes and human review separately. Spend expensive review on P0/P1/P2 uncertainties first, with material action-direction exceptions. Approximate timestamps can live in evidence sidecars and need not clutter script.
- Every accepted editorial claim should be traceable to its input witness, media hash and reviewer disposition; record abstentions clearly.

## Work queue for immediate implementation

1. **P0 annotation format and tests**: add `review_decisions.jsonl` parser/validator (source SHA, unit pair IDs, decision enum, evidence flags, immutable cue lineage); reject unattested approvals, cross-source merges and unit-loss.
2. **Episode review queue**: generate small reversible per-episode boundary task files from source-derived units, with priority buckets (same-source source-label merges, uncertain cue joins, intra-cue switches, >2s gaps), counts and explicit no-certification provenance.
3. **Renderer adapter**: after reviewed P0 decisions exist, feed their resolved contiguous turns to the highest-quality cast/scene reader without discarding costumes, props or physical staging. Render one character header for a continued turn; keep original captions in sidecar.
4. **Independent tests**: synthetic and adversarial source-part preservation; run source-free test suite and both pilot dry runs; record outcomes and input SHAs. No real-world accuracy estimates without original media listening.
5. **Original soundtrack/picture editorial run**: resolve a bounded sample of S01 C19–C28 and S09 ambiguous/no-time dialogues, plus both pilots' key physical business; populate accepted vs deferred decisions. Evaluate gain per reviewer minute.
6. **Final pilot QA**: whole-episode source coverage, P0/P1 confusion and completeness, performance tags, prop/action correctness, sound/scene reconciliation, handoff hashes and truthful editorial/certification status.

## Next-agent launch instruction

> Continue the Night Court S01E01 and S09E19 pilots in `gamesbyian/general-purpose`. Recover live main and open issues/PRs; read `Night Court/SCRIPT-PRIORITIES-AND-ACCEPTANCE-2026-10-25.md`, this handoff, `CURRENT-PRACTICAL-SCREENPLAY-DELIVERY.md`, publication gates and actual latest pilot reader/manifests. Implement P0 reviewed boundary decisions over the already merged conservative proposals; integrate accepted speaker-turn segmentation into the advanced scene/cast readers without regressions; run source-free and source-attested checks as available. Work through P1 character attribution, P2 tone, P3 wardrobe/props and P4 actions; treat exact timestamps as low priority. Keep owner source hashes and independent reviewer claims honest. Do not merge safety-blocked PR #258 or FTP-mover PRs #163–#165 without solving their blockers. Keep #302 open until measured parallel factory quality is shown. Commit qualified changes via PR, retain clear artifacts/handoff, and continue toward two complete independently reviewed screenplay pilots.
