# Speaker identity first: original Night Court pilot recovery

**Owner's primary engineering objective (2026-10-25): resolve missing/wrong speaker identities before any further tone, wardrobe, action or fandom enrichment.** Correct conversational turn segmentation is the immediate enabling operation: a cue containing two characters must be split before either can be named. The [ranked screenplay contract](SCRIPT-PRIORITIES-AND-ACCEPTANCE-2026-10-25.md) still governs P0→P5 evidence quality. Work on additional fan knowledge is secondary until pilot unknown identities are substantially reduced by source-backed evidence.

## Baselines, proposals and provenance

- Canonical original held source: **751 original speaking units**, across 404 S01 and 347 S09 source units. Current pre-correction provisional reader: **487 named, 264 unknown**; source audio independent identity acceptance: 0.
- High-value episode-specific external quote review yields **three original source units with new role proposals** and **four proposed speaker spans** after a missed two-person source paragraph is split. Private **v6 working-reader proposal**: **490 provisionally named source units, 261 unidentified**. This improves *editorial proposals*, not independently identified voices.
- **S01E01 C142.1**: external episode-specific IMDb quote attributes the brief complaint about irregular courtroom procedure to **Dan Fielding**. Direct short source quote matches original SRT cue verbatim. Original soundtrack was not checked in this pass.
- **S09E19 C027.1**: **Christine Sullivan** proposed based on IMDb's *same-position dialogue question*, which paraphrases rather than exactly reproduces the held source question. Review this one more cautiously.
- **S09E19 C034.1**: previous S09 transcript joins two voices in one paragraph; the leading fragment concludes Roz's preceding sentence, while the subsequent reaction is attributed to Christine in the external quotation sequence. This requires **P0 split before P1 naming**. Both individual spans point to original paragraph C034.1, with start/end character offsets and no invented timestamp.
- **S01E01 C028.1**: existing reader provisionally labels the line addressed *to Bull* as spoken by Bull. This is a suspicious self-address, **not proof of misattribution**. A review flag was added; do not automatically swap it to Lana without original-episode audio or independent attribution.

Source files: [external speaker evidence seed](research/pilot-speaker-external-quote-improvements-v1.json), [original-series source index](catalog/dialogue-index.jsonl), and existing v4/v5 source-exact speaking index. Episode-specific quotes: https://www.imdb.com/title/tt0660578/quotes/ and https://www.imdb.com/title/tt0660693/ ; separate indexed IMDb character pages also corroborate the S09 dialogue exchange. IMDb quotations may descend from the same subtitles, and an attributed online quote is **not** original-audio independent identity validation.

## Immediate commands

From the repository root:

```sh
PYTHONPATH='Night Court/tools' python -m unittest \
  test_build_external_speaker_reader_v6 test_export_fan_retrieval_chunks test_fan_sqlite_index

python 'Night Court/tools/build_external_speaker_reader_v6.py' \
  --output /tmp/night-court-private-speaker-v6

python 'Night Court/tools/export_fan_retrieval_chunks.py' \
  --speaker-v6-root /tmp/night-court-private-speaker-v6 \
  --output /tmp/night-court-fan-193-speaker-first
```

Both v6 pilot screenplays, a 4-span exact-source speaker evidence sidecar and a manifest are output only to the owner's private local directory; the unchanged original caption files and existing v5 readers remain in place. Unlike unsupported bulk subtitle duplicates, this source-linked **editorial delta** can be committed safely to the repository and regenerated whenever needed.

In an already-built private LLM fan corpus, replace the previous two pilot script chunks using the v6-aware export, and update the character FTS evidence by invoking:

```sh
python 'Night Court/tools/fan_sqlite_index.py' build \
  --corpus /tmp/night-court-fan-193-speaker-first/fan-retrieval-chunks.jsonl \
  --cards /tmp/night-court-fan-beats/pilot-fan-beat-cards.jsonl \
  --roles /tmp/night-court-private-character-evidence/pilot-character-reading-blocks.jsonl \
  --speaker-overrides /tmp/night-court-private-speaker-v6/speaker-improvement-overrides.jsonl \
  --database /tmp/night-court-fan-speaker-first.sqlite
```

The baseline 715 role reading blocks remain source-verifiable. In **opt-in** corrected search results, three original UNKNOWN blocks are replaced by four provenance-bound proposed speech segments, **716 indexed role segments**. Thus the fan LLM no longer receives the stale UNKNOWN label *as a second role-index fact for the very same utterance*. The original source text still belongs to the same 751 caption-derived units. This replacement does not claim a speaker identification from photographs or soundtrack.

## Next mandatory work

1. **Rank and review the remaining 261 unknown original units.** Prioritize S01 and S09 dialogues with multi-voice cue boundaries, short replies, adjacent named turns, repeated speaker/character quotes, and potentially incorrect already-named voices. A false Dan/Harry/Bull/Roz assignment is at least as damaging as an UNKNOWN.
2. **Use episode-character-attributed external quotes and full scene context first.** Provenanced quote matches can give fast candidate character anchors; do not equate quote/caption shared text with a second independent voice witness. If quote wording diverges, explicitly distinguish lexical match from scene-context candidate.
3. **Consume original sound/film in short context windows around unresolved turns.** Run anonymous voice clustering across uninterrupted scenes, use confirmed audiovisual character labels as anchors, then resolve the nearby unknown turns; use long-enough clips to avoid 1-word/overlap confusion. For untimed S09, align candidate original dialogue sequence to ASR only as a **proposed** location; do not manufacture source caption timestamps.
4. **Record independent speaker-identity dispositions**, distinguish audio/visual reviewed versus quote/context-inferred, and keep old source cue evidence and alternatives. Do not burn GPU on whole-episode video models when a targeted listen or a trusted existing character-quote anchor resolves the issue.
5. **Block the next layer of tone/physical enrichment** on these pilots until the high-impact character confusion and missed turn switches are dealt with. Archive-level 0/193 audiovisual verification remains a separate stringent release criterion.

No claim of a source-listened blind P1 accuracy measure or an independently confirmed new named speaker is made by this work.
