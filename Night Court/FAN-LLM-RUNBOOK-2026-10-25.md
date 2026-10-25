# Night Court fan assistant: retrieval and evaluation runbook

This is the **application-facing** layer of the [fan-corpus product contract](FAN-OBSESSION-DELIVERABLE-2026-10-25.md). It uses the existing original-series 1984–1992 private script witnesses. A *convincingly enthusiastic fan* persona is a style the model can perform; individual claims about actual episodes still require retrieval evidence.

## Quick local seed export

From repository root:

```sh
PYTHONPATH='Night Court/tools' python -m unittest test_export_fan_retrieval_chunks
python 'Night Court/tools/export_fan_retrieval_chunks.py' \
  --pilot-only --output /tmp/night-court-fan-pilots
python 'Night Court/tools/export_fan_retrieval_chunks.py' \
  --output /tmp/night-court-fan-193
```

Both commands are **read-only against sources**, require no tokens or model weights and write private data only to the selected local directory. Their output consists of source-preserving JSONL and a manifest. The all-episode pack contains copyrighted/private dialogue witnesses and should not be added to CI artifacts, external hosted embeddings, public commits or logs without the owner's separate decision. The output is a **retrieval seed**, not a full fan dossier or production-script verification.

Segment identity is `record_id` + `script_sha256`. If the source script changes, rebuild or invalidate old chunks. Each chunk states whether it came from a provisional two-pilot v5 reader or one of 191 caption-only scaffolds. Neither state implies acoustic speaker authentication or verified theatrical scene settings. The original S09E19 witness remains untimed.

## Prompt for an LLM consuming the retrieval index

**System/developer prompt:**

> You are performing the role of an extremely knowledgeable, detail-obsessed fan of the **original 1984–1992 Night Court**. Engage with curiosity, specificity, a feel for performance and the show's contradictions and recurring patterns. Avoid generic promotional summaries, and do not confuse the 2023 revival with the original.
>
> Use retrieved episode material as evidence for factual details. Retrieve when asked about a particular line, scene, episode, character appearance, prop or callback. Distinguish dialogue actually present in a held witness from inferred character attribution. Source-only scaffolds have **no verified scene boundaries, staging, speaker identities or vocal tone**. Two v5 pilot scripts contain richer but still partly provisional attribution and motion notes.
>
> Don't invent a character name for an `UNIDENTIFIED` voice, a quote, an episode event, a camera direction, actor behavior, a running joke or an unstated production anecdote. If the source supports the moment but its exact speaker/inflection is unknown, describe that uncertainty naturally. When evidence is provisional, offer the plausible reading without promoting it to source-verified certainty.
>
> Make room for interpretation: explain comic setup/payoff, timing, context, how personalities collide, changes across seasons, and period-specific allusions. Clearly signal when a conclusion is your *reading of the show* rather than a documented on-screen fact. If sources conflict, explain the discrepancy. A fan can have preferences and arguments; a retrieval system must not manufacture their factual basis.
>
> For brief casual fan discussion, be natural rather than reciting citations. For disputed details, exact dialogue, unfamiliar guest characters or user requests for sourcing, reference the episode and available cue/script locator. Honor spoiler preferences. Avoid claiming to have personally watched or lived through broadcasts: the fan voice is a role, not the system's real biography.
>
> Stay animated and knowledgeable without constantly forcing catchphrases or repeating only the best-known Harry/Dan/Bull jokes. Draw from later seasons and supporting characters whenever the retrieved evidence supports it.

## Retrieval routine

1. Parse the question into people, season/episode clues, dialogue fragments, prop/location, production context and cross-season comparison.
2. Search in this order: canon episode and character records → direct speech/scene chunks → relevant episode summaries/joke/continuity cards → verified external cast or production facts. If the fan layer has not yet been built, use the source script chunks directly.
3. Pull adjacent chunks for speaker continuity, jokes with delayed payoffs and shot/scene boundaries. Context across chunk breaks is essential; raw chunk boundaries have **no dramatic significance**.
4. Inspect `evidence_tier`, `speaker_names_verified`, `section_is_verified_visual_scene`, original timecoding and provenance fields. Never elevate claim strength solely because several semantically similar retrieved chunks agree; they may share the same caption source.
5. Form a concise answer with useful specificity. Quote briefly and accurately only where text is actually present and the setting permits it. Qualify unverified attribution or delivery in natural language.
6. For chronology, guest cast, broadcast facts and trivia absent from the script, look up an independent source rather than inferring off dialogue.

## Early acceptance queries

Test these on the two existing v5 pilots and inspect the cited cue/episode source. These are **questions to evaluate**, not an answer key; no success is claimed.

- S01E01: Which dialogue belongs to the painter, and how does the initial exchange with Lana set up the comedy? Do the alternating caption lines reliably correspond to speaker changes?
- S01E01: What does Bull say about improving his vocabulary? Are the peculiar words real, misused, or deployed for a character beat? Distinguish actual quoted words from paraphrase.
- S01E01: What do we actually know about Harry's arrival before he appears? Which inferred stage directions about office furniture, props and actor gestures are independently observable?
- S01E01: Can the assistant explain an exchange spanning successive subtitle cues without accidentally changing speakers halfway through?
- S09E19: What is Roz's pen-pal arrangement and how does it begin? Can the model contrast Roz's account with Dan's response without manufacturing a camera shot?
- S09E19: What is Christine working on during the campaign-related dialogue, and who comments on the advertisement?
- S09E19: Can the model identify a possible source-text line break that accidentally splits one speaker's uninterrupted thought? Keep the original witness text intact while noting uncertain division.
- S09E19: Is there an original subtitle timestamp for the pen-pal conversation? Expected behavior: **no fabricated original timing**.
- Cross-pilot: Which familiar characters appear and how do their functions differ in these two pilot episodes? Avoid claiming an unverified named voice is certain.
- Cross-corpus negative control: Ask about a made-up original-series episode or nonexistent character. Expected behavior: avoid fabricating a confident plot.
- Performance negative control: Ask whether an unnamed speaker *definitely* delivered a line sarcastically, with no audio evidence. Expected behavior: separate textual irony from audible performance.
- Physical-gag negative control: Ask **who touches whom** in the S01 scene previously misdescribed by Qwen. Expected behavior: refuse to trust the unreviewed model output, use actual original-film directional evidence if present, and be explicit about its limits.

On every answer record `retrieved_sources`, `factual_error`, `source_confusion`, `invented_quote`, `turn_boundary_error`, `speaker_error`, `unsupported_tone`, `actor_target_reversal`, `material_omission`, `useful_fan_insight`, and approximate model cost/time. There is **no claimed quality score** until an independent real answer review is conducted. The proof of value is whether a model with the enriched corpus answers substantially better than the same model fed only our raw caption transcripts.

## Priority guardrails

1. Fix source cue segmentation and actor naming errors before investing in voice emotion or more stage minutiae.
2. Next extract the key comic premise, response, payoff and character context as *source-linked cards* from the same existing text and reviewed AV windows.
3. Maintain author/episode credits, interpretive notes and production trivia in separate externally sourced records, not as invented additions to a filmed scene.
4. Add continual cross-episode recall testing once the 193-episode text retrieval baseline is proven; enhance high-impact examples where the assistant gets stuck instead of uniformly reprocessing every frame.

## Local searchable retrieval, no model service

After the above all-episode seed export, a fully local BM25-style lexical search provides ranked exact-witness context without infrastructure, model weights, web/API uploads or embedding costs:

```sh
python 'Night Court/tools/search_fan_retrieval_chunks.py' \
  --corpus /tmp/night-court-fan-193/fan-retrieval-chunks.jsonl \
  --query 'Roz pen pal Alex' --episode S09E19 \
  --output /tmp/night-court-fan-roz-search.json
```

The JSON output holds full matched private script passages and neighboring chunks for continuity and is **not suitable for public CI logs**. Stdout prints counts only. Use the returned IDs, script/caption source SHAs, episode title and evidence tier to ground the final LLM answer; do not reclassify source-only chunks as visual stage truth or conflate adjacent chunks with independent confirmation. Repeat queries with known character aliases or episode filters when natural-language matches are weak. The current interface is token-based retrieval, not semantic embeddings or a continuously hosted RAG chatbot. A future fan-dossier index should expose character aliases, beat/card IDs and cross-episode continuity through the same retrieval contract. The smoke workflow tests original-source examples without exposing the text.

## First source-anchored fan-knowledge layer: pilot comedy and storyline cards

The source-preserving scripts remain the canonical witness. A **separate** set of 21 editorial reading cards makes the stories and jokes more legible to a fan-oriented LLM: S01E01 (10 cards: the painter, Bull's vocabulary, the new judge, the Kerr case and coin, Harry's music obsession); S09E19 (11 cards: Christine's campaign, Roz's letters, the old safe, the impostor scene and the ad-related setup). Each human-written card is tagged with *short original caption fragments and exact original cue positions*. Those captions are rechecked against unchanged source SHA and source text on every build. Card prose expresses an interpretation, **not independently witnessed delivery, shot direction, character voice identification or objective comic intention**.

Run after the all-episode source retrieval export:

```sh
python 'Night Court/tools/build_pilot_fan_beat_cards.py' \
  --output /tmp/night-court-fan-beats

python 'Night Court/tools/search_fan_corpus.py' \
  --corpus /tmp/night-court-fan-193/fan-retrieval-chunks.jsonl \
  --cards /tmp/night-court-fan-beats/pilot-fan-beat-cards.jsonl \
  --query 'Harry double-headed coin justice' --episode S01E01 \
  --output /tmp/night-court-fan-doubleheaded.json
```

The combined search returns **two noninterchangeable groups**: (1) original direct script passages with same-episode neighbors and source-edition hashes, (2) interpretive fan cards linked to original caption cues. If a card suggests a compelling comparison, read the direct evidence before treating any concrete fact as established. Neither group validates all filmed physical movement or performance. Do not automatically export combined search results to an external inference provider; the script hits contain held dialogue text.

The 21 cards are a grounded first seed, **not comprehensive coverage of every joke, a verified comedy classification, or all 193 episodes**. Expand only from source-checked excerpts and retain abstentions. The next useful enrichment is validating pilot speaker-turn merges and then cross-episode character/prop/callback connections.

## Reversible pilot character evidence and P0 continuation review

The original held subtitle/caption speaking-unit provenance now supports an optional **private character evidence export**:

```sh
python 'Night Court/tools/build_pilot_character_evidence.py' \
  --output /tmp/night-court-private-character-evidence
```

It joins the existing S01E01 v4 quote-corrected and S09E19 v4 impostor-role editorial speaker ledgers with the **unchanged original source cues**. The output produces role-labeled source quotation blocks, initial role-specific dossier seeds, and adjacent same-role speech-continuation **review candidates**. The result is useful for questions about which material is *provisionally* associated with a role, including two-voice original captions and S09's 36 joined continuation paragraphs.

S01 authentic SRT cue parts remain reversible and timed. S09's 347 original paragraph references are retained across 311 editorial reading blocks, **without inventing source timecodes**. Every source text block is reassembled and matched to the existing byte-identical SHA-256; missing/duplicate cue-part coverage or altered speaker-ledger source fails closed. The canonical pilot counts are 751 original speaking units, 487 provisionally named, and 264 unidentified. **None of those provisional attributions is an independent original-audio voice identification**, and proposed adjacent-same-role continuations must not silently become authoritative performance turns.

The fan assistant should prefer direct source-backed character evidence over inference from dialogue semantics alone, while retrieving adjacent evidence when a line is split across caption cues. A candidate speaker's identity remains uncertain wherever the held editorial annotations mark it as provisional. Real P0/P1 verification still requires source audio/visual comparison; the next step is benchmarked speaker inference or targeted listening that actually reduces the unresolved count and false turns.
