# Source-only reading scripts for all original Night Court episodes

**Completed:** [PR #156](https://github.com/gamesbyian/general-purpose/pull/156), successful all-episode CI [run #40049496881](https://github.com/gamesbyian/general-purpose/actions/runs/40049496881). **193/193** reading scripts, **70,804** original caption cues, **72,733** script units, **1,173** provisional gap blocks, **192 timed + 1 untimed**. Source presence does not imply verified audiovisual completeness.

## Intent and evidence standard

A **source-reading scaffold** is not a production screenplay, complete transcript, verified scene breakdown, performed actor script or copyright license. It is a chronological, readable working document that makes each retained original-series subtitle/dialogue source available to subsequent visual/speaker QA agents, without inventing information the source does not contain.

The corpus baseline is **193 original 1984–1992 episode dialogue witnesses**: 192 timed English subtitle tracks and one S09E19 untimed transcript-page witness. All 193 are preserved in their respective `dialogue/versions/` directories, with original bytes and SHA manifests. No source episode has been independently AV-certified complete.

## Implementation

`tools/build_source_script_scaffolds.py` uses exactly the indexed held dialogue versions and invokes the existing `build_caption_turns.build` algorithm directly on the immutable `segments.jsonl` of each source. This is important because many late-season episodes **do not yet have** cached `candidate-turns.jsonl`/`conversation-packets.jsonl`; the reading script must not depend on those optional derived caches. All source text, cue IDs and existing source labels are preserved. Only explicit multi-dash caption typography causes unattributed voice turns to be split. The source's own labels, if any, are flagged **unverified**, not asserted as character identities.

It creates `seasons/Sxx/SxxEyy/derived/source-script-scaffold-v1.md` per original-series episode, and a complete `catalog/source-script-scaffold-coverage.json` to quantify progress. Each candidate dialogue block is a **caption-gap heuristic**, not an interior/exterior or set-specific scene location. The Markdown uses `UNIDENTIFIED VOICE` and refuses to fabricate stage actions, soundscapes, performances, reactions, location headings or speaker identities. S09E19 retains **UNTIMED SOURCE PARAGRAPHS**, without invented clock positions.

The original dialogue and fully evidenced S01E01 `scene-review-v3` research edition remain separate from these automated source-only reading scripts. Production scenes, source AV verification and character performance annotation are to be layered onto future reviewed script versions, not overwritten into these source scaffolds.

## Independent quality gates

Run `python "Night Court/tools/test_source_script_scaffolds.py"` before acquisition/derivation changes. It tests all 193 source manifests, all original cue IDs, no lost candidate turns, S09E19's untimed-only status and the absence of full-script verification claims. The dedicated PR-triggered CI runs the builder, validates the complete corpus, checks **193/193, 192 timed + 1 untimed**, and commits each new reading edition to the original episode folder. There is no FTP or model download and no special Actions secret.

## What must happen before calling the scripts proper

1. Validate subtitle timing and words against *the same* source AVI edition, with explicit alternate-source readings where useful.
2. Establish actual scene boundaries and locations from temporal video evidence. A caption silence gap is not a stage cut.
3. Attribute each voice using independent diarization, source audio and visually grounded appearances, retaining UNKNOWN when uncertain.
4. Extract time-scoped visual action and physical jokes, with evidence links to frames and short reviewed clips. Stills alone cannot prove rapid movement.
5. Add measured/performance-reviewed expressive delivery, vocal emphasis and laughter/sound effects, keeping emotional interpretations distinct from acoustic observations.
6. Independently audit full episode runtime for dropped dialogue, source-version drift and scene/visual completeness.

The existing `S01E01` 60–90s integrated scene is the first worked audiovisual example. The scaffolds provide every later episode a deterministic **place to attach better evidence**, not a false claim that all 193 scripts are finished.

## Repository-wide caption-turn cache catch-up

The accepted scripts were derived on the fly because `catalog/caption-turn-coverage.json` previously indexed only 35 episodes. A separate bounded CI batch regenerates the existing `candidate-turns.jsonl` and `conversation-packets.jsonl` per every original subtitle witness. It must reconcile **193 episodes, 70,804 source cues, 72,733 candidate dialogue units and 1,173 gap packets** against the immutable source-only reading-script catalog. This is purely source preparation: it does not detect actual scenes, certify speakers or touch FTP audio/video.
