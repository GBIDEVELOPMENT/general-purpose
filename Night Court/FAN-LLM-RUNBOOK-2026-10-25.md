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
