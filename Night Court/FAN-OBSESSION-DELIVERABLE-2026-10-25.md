# Night Court: fan-obsession corpus product contract (2026-10-25)

**Owner's actual intended use:** privately supply an LLM with a rich, reliable knowledge base enabling it to *perform convincing, deeply informed enthusiasm for the original 1984–1992 Night Court*. This is an application deliverable, not an academic research contribution, model-training program or archival certification exercise.

This document complements, rather than changes, [the authoritative P0–P5 script priorities](SCRIPT-PRIORITIES-AND-ACCEPTANCE-2026-10-25.md). No work on the 2023 revival. Prioritize **useful knowledge, coverage, correction yield, and iteration speed**. Retain original witness provenance, factual uncertainty and the separate optional high-rigor archival certification ledger. The latter must not obstruct clearly labeled working scripts or fan-use retrieval products.

## Definition of success

A grounded LLM can readily and entertainingly discuss:
- Any episode's actual story, order of events, cases, participants, settings, conflict and resolution.
- Who said what, **with real speaker-turn continuity across caption boundaries**; indicate unknown or provisional character attribution rather than inventing it.
- How lines were delivered: deadpan timing, bafflement, sarcasm, hesitancy, exasperation, warmth, overstatement, pauses and interruptions **when audible/observed**.
- Character-specific comic behavior, relationships, growth, contradictions, running jokes, physical gags and callbacks across seasons.
- Period context: references, legal-procedural absurdities, production facts, performers/guest roles, cast changes, episode order and factual-versus-fan interpretations.
- Which details came from video, captions, external programme guides/quotes, criticism or interpretive inference.

An LLM can adopt a *fictional superfannish persona* in its response style while grounding specific assertions in retrieval. **Do not pretend a guessed joke, invented line, speech inflection or anecdote is in the episode.** An intentionally entertaining opinion is okay when marked as an interpretation; exact facts require source pointers.

## Two related but distinct output products

1. **Readable episode script**: merged same-speaker dialogue turns (P0), character identification (P1), supported performance annotation (P2), salient clothing and objects (P3), directed physical actions and stage business (P4); timing (P5) hidden except approximate review pointers. Original caption text is preserved and provenance lives in a sidecar. Allow useful *working* status with unresolved annotations.
2. **LLM fan corpus**: script retrieval segments PLUS per-episode dossiers, character dossiers, plot/case cards, joke/setup/payoff/callback cards, expression/delivery samples, prop/location continuity, period explanations, production/cast fact cards, disputed-claim records and episode-to-episode links. The fan corpus is what makes questions across 193 episodes answerable without loading 193 full screenplays into one prompt.

Maintain one canonical episode/character/source namespace and reusable source evidence. Do **not** create divergent prose factories for scripts, summaries, retrieval snippets and jokes; generate several views from shared scene/turn/claim records.

## Core record design (minimum)

Use atomic records with stable IDs. Structure shown as conceptual schema, not a claim that every field exists today:

```json
{
  "id": "S01E01:beat:001",
  "type": "comedic_beat",
  "episode_id": "S01E01",
  "scene_id": "S01E01:scene:provisional:001",
  "participants": ["character:lana-wagner", "role:painter"],
  "setup": "Paraphrased source-grounded context",
  "payoff": "Paraphrased event / delivery, not a fabricated quote",
  "mechanism": ["reversal", "deadpan"],
  "delivery": [{"kind": "deadpan", "status": "review_pending"}],
  "source_refs": [
    {
      "kind": "caption_witness",
      "caption_sha256": "source-edition-SHA",
      "cue_parts": ["C00004.1", "C00005.1"]
    }
  ],
  "evidence_status": "machine_or_editorial_proposal",
  "contradictions": [],
  "interpretation": true
}
```

Recommended record kinds:
- `turn`: source cue membership; speaker label/alternatives; dialogue; delivery segments; sound/reaction; provisional versus reviewed.
- `scene`: source-order location, participant list, event sequence, A/B story, scene-boundary status and evidence.
- `physical_beat`: **actor → action → target/object**, before/after state, surrounding shot IDs and observed uncertainty. Actor/recipient reversal is a severe failure.
- `comedic_beat`: setup, performance, payoff, mechanism, character response, callback references, narrative role.
- `character`: identity and aliases, recurring traits supported by specific episodes, relationships that change, cast membership separately sourced.
- `continuity_link`: entity-episode / episode-episode relation, direction, evidence per endpoint, contradicting appearances and spoiler relevance.
- `external_fact`: non-video cast, production, broadcast, reception, quotation attribution, independent source URL and legal/reuse note.

Storage may be JSONL, JSON or SQLite if simpler. Working evidence can be `held_caption`, `external_attribution`, `original_sound_candidate`, `original_picture_candidate`, `source_av_reviewed` or `interpretive`; **do not collapse evidence modality and review status into one confidence score**. Original source cut/edition and text SHA remain attached. Keep untimed S09E19 original paragraphs untimed.

## Operational production order

**Stage A: make the pilots genuinely intelligible.** Fix source turns before source character assignment; annotate major delivery and visible comic action without spending weeks extracting every frame. The existing v5 pilot screenplays are useful starting material, with 487 of 751 pilot speaking units provisionally attributed. Use current ledger values, not old reader-block percentages.

**Stage B: produce fan dossiers simultaneously.** Every accepted or plausible scene note should yield retrieval records on characters, case plot, line delivery, joke structure and callback candidates as appropriate. Use the same source-bound clip/model call to request setting, entities, gestures, expressions, direct actions and gags; retain each field's independent status. Summarize by scene then by episode, cross-link in cast/character and story matrices. LLM summaries are proposals, not independent source truth.

**Stage C: expand to all 193 caption witnesses quickly.** Generate basic episode and character-retrieval text for all source-only scaffolds now; use the two richer pilots as quality controls. Promote content by meaningful source-backed improvement, not by completing more ASR benchmarks. Prioritize recurring cast episodes, continuity-rich arcs, and especially dialogue with difficult speaker transitions; label unknowns.

**Stage D: selective AV enrichment.** Speech tool chains provide P0/P1/P2; contiguous cut-safe clips + shot neighbor context provide P3/P4. Audio/visual models can supply suggestions faster than human transcription. However, the S01E01 verified-frame experiment found that Qwen reversed the actor performing a touch, and doubling sample frame rate did not fix it. Flag potentially damaging physical-gag descriptions for actual film review. Keep video stills, original media, model weights, secrets outside committed repo artifacts.

**Stage E: evaluate the *fan-answer product*.** Use a fixed retrieval challenge set with:
- precise but common facts, obscure minor-character questions, real episode-specific plot/case questions;
- two-person exchanges, consecutive same-person caption lines, in-caption handoffs, rapid interruptions;
- sarcasm/deadpan versus literal interpretation, physical business and reaction shots;
- questions comparing character behavior in different seasons, recurring gags and cast transitions;
- negative controls for false quotes, non-existent episodes, unsupported tone, wrong-show confusion and deliberate out-of-order scenes.

Score separately (i) correct recall, (ii) retrieval citation to episode/scene/source, (iii) invented details, (iv) meaningful humor/characterization, (v) latency/expense, (vi) number of genuinely covered episodes. Keep hidden-reference assessments separate from auto-generated candidate answers. A fluent model response alone is not evidence of correct coverage.

## Working quality policy

Use three independently displayed notions:
- **Corpus ready for fan retrieval**: source-backed episode-level material, clearly provisional where needed; appropriate for casual conversation.
- **Editorially useful screenplay**: the actual turn, identity and important staging priorities meet the existing ranked screenplay contract.
- **Independently AV certified archive**: the stricter, optional archival publication gate in [AV-SCRIPT-PUBLICATION-GATES.md](AV-SCRIPT-PUBLICATION-GATES.md). Current count remains 0/193. Do not quietly change those release status values.

No scientific novelty, no full-model training, no exhaustive word-level timestamps, no recurring large CPU video runs merely to improve a process metric. Favor reused open code and APIs only after a short paired value test. A competitor's architecture, paper, prompts or trained checkpoints may save us work; carry over actual code and datasets **only under their applicable licenses and permissions**, with notices where needed.

## Next useful measurable milestones

1. Source SHA-safe, working retrieval chunks for both v5 pilots and the remaining 191 source scaffolds, labeled with correct evidence tiers.
2. One high-impact P0/P1 comparison on the pilot opening and one later difficult exchange using borrowed DramaSR-style contextual candidate ranking and existing caption-first turns.
3. One paired original-film source review of actor/action/recipient across challenging physical gags, with Shot-by-Shot neighborhood context and existing Qwen baseline, not another indiscriminate episode pass.
4. Actual per-episode fan dossiers for both pilots: scene / plot / participants / 5–15 noteworthy comic beats / recurring-character connections, source-linked, with unknowns preserved.
5. Retrieval Q&A acceptance pack; demonstrate improved grounded answers versus the scripts alone before scheduling a 193-episode enrichment rollout.

See [UPSTREAM-REUSE-FOR-FAN-CORPUS-2026-10-25.md](UPSTREAM-REUSE-FOR-FAN-CORPUS-2026-10-25.md) for current adoption candidates and blockers.
