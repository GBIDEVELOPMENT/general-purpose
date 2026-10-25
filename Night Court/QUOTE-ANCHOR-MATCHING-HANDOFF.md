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
