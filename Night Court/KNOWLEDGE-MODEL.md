# Proposed canonical knowledge model (research stage)

The goal is a *traceable* interpretation of the 1984–1992 original, suitable for retrieval, reasoning, narrative analysis, cultural criticism and fandom characterization. No synthesized claim is treated as fact merely because an LLM generated it.

## Objects and IDs

- `episode`: `SxxEyy`, airing chronology, title variants, source IDs, broadcast context
- `version`: episode release, broadcast / syndicated / DVD / streaming edits, caption and transcript variants
- `source`: `source_id`, type, URL, author, publication date, retrieved date, accessibility, license, content hash, language, extraction method, mapped episode ID, trust caveats
- `person`: actor, writer, director, guest performer, creator, production member; real-world entity, never conflated with character
- `character`: named/unnamed fictional identity, aliases, role/occupation, appearances, arc continuity and conflicting depictions
- `event`: ordered events and causal relations, knowledge-state changes, participant roles, narrative consequence
- `scene`: timecode or ordinal, location, participants, A/B plot assignment, setup, payoff and tonal progression
- `comedic_beat`: formal mechanism (misdirection, reversal, physical comedy, character-based incongruity, callback, taboo, topical allusion, insult, pun), target and performance evidence
- `cultural_reference`: exact named referent, 1980s/90s interpretation, original-airdate contemporaneity, present-day reception contrast
- `production_event`: casting transitions, episodic credits, writers-room conventions, soundtrack, network and industry context
- `reception_claim`: specific viewer/critic author, platform, published date, review vs. nostalgic recollection vs. revival comparison, viewpoint, sentiment, representativeness caveat
- `claim`: atomic fact/inference `predicate`, `object`, `evidence[]`, `confidence`, `contradictions[]`, `status`.

## Matrices for future generation

1. **Episode × character:** presence, narrative agency, screen-time estimate only when measured, development, relationships, defining behavior, cast status.
2. **Episode × storyline:** opening premise, A/B/C plot, locations, cases, continuity, resolution, unresolved threads.
3. **Episode × comedy:** mechanism, target, setup/payoff distance, deadpan/absurdist/sentimental blend, joke density if measured, comic persona and period sensibility.
4. **Episode × affect:** dominant mood, tonal shifts, serious subject matter, pathos, warmth, discomfort, laugh-track response if substantiated.
5. **Episode × production:** writers, directors, cast transitions, guest performers, production code, first airing, broadcast rating/share and sourcing.
6. **Episode × cultural context:** legal institutions vs. sitcom liberties, topical public events, language norms, race/gender/disability depictions, period social assumptions.
7. **Episode × reception:** contemporaneous reviews, retrospectives, nostalgia themes, debates, memorable moments, comparative preferences, community and time.
8. **Source × claim:** disagreements, corroboration, missing transcript spans, source quality, license and preservation status.

## Episode derived files (future)

```text
derived/canonical.json
derived/summary.md
annotations/scenes.jsonl
annotations/jokes.jsonl
annotations/cultural-context.jsonl
annotations/reception.jsonl
sources/source-ledger.jsonl
```

Every knowledge assertion should include at least one precise source pointer:
```json
{
  "claim_id": "S01E01:C001",
  "subject_id": "character:harry-stone",
  "predicate": "occupies_role",
  "object": "night-court-judge",
  "temporal_scope": {"episode": "S01E01"},
  "evidence": [{"source_url": "https://www.tvmaze.com/shows/1489/night-court/episodeguide", "locator": "Season 1 / episode 1", "evidence_type": "episode_guide"}],
  "confidence": "high",
  "status": "corroborated"
}
```

Annotate subjective readings as interpretations. Separate how fans describe the comedy from an analyst's mechanical classification. Positive and negative reactions may coexist. Include metadata on original broadcast versus syndication edits.
