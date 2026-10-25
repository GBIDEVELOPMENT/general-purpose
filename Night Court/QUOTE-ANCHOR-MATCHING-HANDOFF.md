## S01E01 opening attributed-dialogue sequence (2026-10-25)

First nine original timed SRT cues provide a useful P0 adversarial case: caption C2 contains two dash-marked voices, the other captions include several alternating Lana/Painter lines. IMDb's pilot quote page labels the conversation. The [minimal external attribution registry](research/s01e01-opening-attributed-sequence-v1.json) links **ten caption parts** to ten external character labels, with source SHA and small lexical guardrail fragments. This is an **attribution proposal**, not audiovisual identification. Page: https://www.imdb.com/title/tt0660578/quotes/

New `tools/align_attributed_quote_sequence.py` compares all attributed source parts in order against `build_caption_turns.parse_caption` (source cue + part lineage), checks short fragment containment, and reports adjacent same/different speaker hypotheses. The tool does **not** mutate scripts or accept identities. For S01E01:

```sh
python 'Night Court/tools/align_attributed_quote_sequence.py' \
  --registry 'Night Court/research/s01e01-opening-attributed-sequence-v1.json' \
  --output /tmp/night-court-opening-attribution.json
python 'Night Court/tools/test_align_attributed_quote_sequence.py'
```

The current P0 delimiter is conservative and will not automatically combine separate unlabeled same-speaker cues. The external sequence directly proposes which ones deserve source-original listening. Before adopting any proposed merge/character label, examine original audio and complete `validate_speaker_turn_reviews.py` with true attestation. Voice embeddings and cross-episode speaker propagation remain future work. The rest of the episode and S09E19 have **not** been seeded or reviewed by this narrow pilot.

Run actual source-linked CLI and tests before quoting any match counts as verified; GitHub file commits are not test execution. Preserve the latest cast/scene readers rather than overwriting with old caption-first outputs.

# Third-party attributed dialogue anchoring: initial executable lane

Status 2026-10-25: preliminary quote-to-caption matching infrastructure, not accepted speaker identification.

## Scope
`tools/match_quote_anchors.py` consumes a small per-episode JSON quotation registry with explicit external URL, attributed character and excerpt, then compares against **existing original source witness** caption text using normalized fuzzy matching over up to four consecutive cues. Emits unique lexical *candidates* with caption SHA/version and original cue IDs. All candidates have `speaker_identity_accepted=false`, `caption_turn_boundary_accepted=false` and `source_original_av_reviewed=false`. It never rewrites captions or advanced screenplays.

The small initial S01E01 seed registry is `research/quote-anchor-s01e01-short-seeds.json`, attributed to the [season 1 Wikiquote episode section](https://en.wikiquote.org/wiki/Night_Court_(season_1)). These are short quotation leads, not evidence that a whole source quote page was copied or an actor listened to. IMDb pilot URL is https://www.imdb.com/title/tt0660578/quotes/ but this pass did not obtain page contents from IMDb; never invent its exact quotes.

## Commands
From repository root:

```bash
python 'Night Court/tools/test_match_quote_anchors.py'
python 'Night Court/tools/match_quote_anchors.py' \
  --episode S01E01 \
  --registry 'Night Court/research/quote-anchor-s01e01-short-seeds.json' \
  --output /tmp/night-court-s01-quote-candidates.json
```

For S09E19 use a **different** independently sourced episode-specific registry once suitable attributed quotes exist. Do not pass S01 seeds as S09 evidence or infer source paragraph timestamps.

## Engineering next steps
1. Measure actual S01E01 lexical candidate yield and false matches with independent source replay. Keep all unknowns and unverified original cast headings unchanged.
2. Upgrade the matcher to **speaker-labeled quote sequence alignment**, with one-to-many and many-to-one cue/turn mappings, preserving P0 true speaker-turn boundaries and aligning quoted sentences inside compound captions rather than assuming whole-cue speaker identity.
3. Add rights-aware limited excerpt acquisition and exact source revision/URL provenance; URLs alone cannot establish rights.
4. Add cross-source relationship grouping to avoid counting copied IMDb/Wikiquote content as independent witness.
5. Integrate reviewed quote anchors with `propose_speaker_turns.py` and `validate_speaker_turn_reviews.py`: a quote alone proposes P1 naming, but cannot mark original audio AV-reviewed. Use episode cast ledger for name resolution, especially S09 Alex / The Guy distinctness.
6. Reserve some independently corroborated anchor dialogues as held-out evaluation. Measure P0 change/merge errors and P1 false attribution, confidence and coverage. Do not propagate identity to neighbors without additional acoustic/source confirmation.
7. Only after original source evidence anchors a character, store private minimal audio-embedding references by original-media SHA and acoustic-model version; do not commit voice audio, embeddings or weights to Git. Verify cross-episode identity separately.
8. Re-render the **advanced** cast/scene readers only after verified decisions, retaining all current visual notes and source cue mapping.

All unaccepted matches are proposals. Neither pilot or overall series is independently audiovisual certified.
