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

## Prioritized private review queue for the remaining 261 UNKNOWNs

Generate the priority-sorted source-review packets **after** generating the new v6 readers:

```sh
python 'Night Court/tools/triage_unknown_speakers.py' \
  --speaker-v6-root /tmp/night-court-private-speaker-v6 \
  --output /tmp/night-court-private-speaker-review
```

This produces `speaker-identity-first-review.jsonl` with each unresolved source block's cue, nearby named/unnamed dialogue, source SHA, P0 boundary-risk tags, and S01 approximate padded **SRT** window for listening. No S09 timestamps are fabricated. A separate priority-40 item flags the previously labeled S01 C028 for possible speaker error; it is not counted as an unresolved source unit or silently assigned to Lana. Priority boosts identify difficult multi-voice cues, short interjections, merged transcript paragraph groups, probable syntax continuations, and unidentified clusters. Proximity to a named character is shown for reviewer context, **never treated as proof the unknown person has that name**.

Acceptance against the current source-ledger state: **97 S01 UNKNOWN + 164 S09 UNKNOWN = 261 remaining original source units**; one additional suspected incorrect legacy named label, ranked separately. No automated new role names or independently listened speaker confirmations are claimed. Do not publish this private queue; it contains source transcript text and working character hypotheses.

## Bounded S01 original-soundtrack review clips, with no audio in GitHub

The **speaker** queue may now be turned into a compact plan of source-only listening windows, prioritizing the highest-risk unknowns and coalescing overlapping windows into at most twelve short excerpts by default. It is independent of, and ranked ahead of, the animation/staging pipeline:

```sh
python 'Night Court/tools/plan_speaker_audio_review.py' \
  --queue /tmp/night-court-private-speaker-review/speaker-identity-first-review.jsonl \
  --output /tmp/night-court-private-speaker-listening-plan.json --max-clips 12
```

This first action only creates metadata. When the **real original S01E01 AVI is available locally**, and only if its complete file SHA-256 matches the pinned original media evidence `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`, extract private 16kHz mono WAVs with:

```sh
python 'Night Court/tools/plan_speaker_audio_review.py' \
  --queue /tmp/night-court-private-speaker-review/speaker-identity-first-review.jsonl \
  --output /tmp/night-court-private-speaker-listening-plan.json \
  --original-avi /private/media/Night-Court-S01E01-original.avi \
  --audio-output /private/night-court/speaker-listening-wavs
```

**No original media** is downloaded by this new tool, its output is private local only, and no CI action here extracts, retains, uploads or prints television audio. Every WAV is a **candidate listening window, not acoustic speaker authentication**. The S01 subtitle timings are approximate reference points, not independently synchronized speech alignments, and may be wrong for a source edition. The untimed S09 original is explicitly deferred until a defensible original-audio/text alignment is established. The separate C028 potentially wrong legacy role is also deferred to its original cue locator until it receives an actual time/shot resolution.

This planner may reuse a verified original local media checkout from a trusted source job without another full-episode download, once available. Only a later human or validated diarization/voice pass can turn these clips into confirmed named speakers. Keep all media, ephemeral WAVs, thumbnails and acoustic voice embeddings outside GitHub and public CI artifacts.

## Next mandatory work

1. **Rank and review the remaining 261 unknown original units.** Prioritize S01 and S09 dialogues with multi-voice cue boundaries, short replies, adjacent named turns, repeated speaker/character quotes, and potentially incorrect already-named voices. A false Dan/Harry/Bull/Roz assignment is at least as damaging as an UNKNOWN.
2. **Use episode-character-attributed external quotes and full scene context first.** Provenanced quote matches can give fast candidate character anchors; do not equate quote/caption shared text with a second independent voice witness. If quote wording diverges, explicitly distinguish lexical match from scene-context candidate.
3. **Consume original sound/film in short context windows around unresolved turns.** Run anonymous voice clustering across uninterrupted scenes, use confirmed audiovisual character labels as anchors, then resolve the nearby unknown turns; use long-enough clips to avoid 1-word/overlap confusion. For untimed S09, align candidate original dialogue sequence to ASR only as a **proposed** location; do not manufacture source caption timestamps.
4. **Record independent speaker-identity dispositions**, distinguish audio/visual reviewed versus quote/context-inferred, and keep old source cue evidence and alternatives. Do not burn GPU on whole-episode video models when a targeted listen or a trusted existing character-quote anchor resolves the issue.
5. **Block the next layer of tone/physical enrichment** on these pilots until the high-impact character confusion and missed turn switches are dealt with. Archive-level 0/193 audiovisual verification remains a separate stringent release criterion.

No claim of a source-listened blind P1 accuracy measure or an independently confirmed new named speaker is made by this work.

## Larger P1 textual candidate pass: 583/751, 168 UNKNOWN (not AV verified)

[Source-ref-anchored editorial candidate ledger](research/pilot-contextual-speaker-proposals-v1.json) now covers **90 additional original speaking blocks comprising 93 original cue units**, after the three external-quote proposals from v6. These are **contextual name hypotheses** sourced from neighboring drama, character address and explicit episode quotes, *not independently heard voices*. C172.1 was corrected from a mistaken Lana hypothesis to Harry after checking the season-specific [Wikiquote original-episode quotation](https://en.wikiquote.org/wiki/Night_Court_(season_1)). C137.1, previously unidentified, is source-attributed to Lana by the same page. **Revision v7 source-level totals: 583 provisionally named, 168 unknown, zero newly independently confirmed by soundtrack.**

The corrected v7 source-first manuscript contains all 751 original subtitle-derived speaking units, with **716 editorial reading segments** after the previously restored S09 C034.1 internal two-voice turn. Crucially, the v7 manuscript is a *speakers-first* text document and does not pretend to reproduce v5 picture-based stage description. V5 remains available separately. The private v7 complete readers, role source evidence and cryptographic digest manifest are regenerated locally, not committed as bulk dialogue.

```sh
python 'Night Court/tools/build_contextual_speaker_reader_v7.py' \
  --v6 /tmp/night-court-private-speaker-v6 \
  --output /tmp/night-court-private-context-speaker-v7

python 'Night Court/tools/export_fan_retrieval_chunks.py' \
  --speaker-v7-root /tmp/night-court-private-context-speaker-v7 \
  --output /tmp/night-court-private-fan-speaker-v7

python 'Night Court/tools/fan_sqlite_index.py' build \
  --corpus /tmp/night-court-private-fan-speaker-v7/fan-retrieval-chunks.jsonl \
  --cards /tmp/night-court-private-fan-beats/pilot-fan-beat-cards.jsonl \
  --roles /tmp/night-court-private-character-evidence/pilot-character-reading-blocks.jsonl \
  --context-roles /tmp/night-court-private-context-speaker-v7/pilot-provisional-context-character-reads.jsonl \
  --database /tmp/night-court-private-fan-speaker-v7.sqlite
```

The updated private FTS index checks the SHA of the entire v7 source-role register and the exact unchanged original cue text for *every* reading block. It permits only one known original speaker split (S09 C034.1); it forbids changing already attributed original speaking units, losing source paragraphs or claiming audio verification. The resulting character retrieval evidence no longer contradicts its speaker-first script view with obsolete UNKNOWN labels at the 93 new candidate cue locations.

**Next highest ROI for approaching 751 accurate names:** acquire and align the actual original production scripts. A [1984 pilot screenplay listing at Scrybe](https://scrybe.to/resources/scripts/night-court-s01e01-all-you-need-is-love-script) shows a 54-page file, though login with verified email is required and edition must be checked. [Hollywood Script Shop](https://hollywoodscriptshop.com/television-scripts-n/) identifies the original pilot by its episode title, and [Scriptfly](https://scriptfly.com/searchpage/resultpage.php) lists both 'NIGHT COURT - Pilot' and 'NIGHT COURT - Ps Do I Know You?' for purchase. The user has not supplied those script bytes, so we **cannot claim character headings from them**. Production dialogue may differ from aired dialogue; align scene, sequence and distinctive phrases against the held caption source rather than replacing the real broadcast witnesses or automatically assigning every character on proximity. These source editions could be far more productive than multiplying LLM context guesses.

The first incorrect C172 candidate illustrates the central caution: getting to 751 through plausible but unverified labels would be damaging to a trustworthy fan persona. The remaining 168 are not solved by adding more confidence adjectives. Continue targeted source film listening and verified production script acquisition/ordered alignment; require separate evidence for actual speech identity.
