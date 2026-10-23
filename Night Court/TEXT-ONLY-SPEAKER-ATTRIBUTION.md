# Text-only reconstruction of speakers from Night Court captions

**Status:** source-grounded research engineering, October 23, 2026. This is an agent-ready specification for the original 1984–92 series. Audio, video, handwritten speaker labels, and outside transcript mirrors are not prerequisites. Lack of audiovisual evidence prevents guaranteed speaker identification; the correct output may be `UNKNOWN`.

## Core idea

**Infer conversations, not isolated lines.** The hidden speaker is a latent variable for each utterance. The best speaker assignment for a line depends on the whole scene, the people known or likely to be present, questions and answers, direct address, recurring language patterns, and interpretations of other lines. The output is a *hypothesis-rich reconstruction*, never a new canonical source.

The repository currently holds 35 source-preserved English subtitle tracks for the original first two seasons. Five randomly selected episode beginnings have ~330–410 caption cues per episode, with some two-line captions marking distinct speech by leading dashes. Existing TVmaze show-wide main-cast records and episode guest-role credits provide candidates but do not prove an appearance or spoken line.

## Seven-stage evidence pipeline

1. **Immutable caption source and segmentation**. Parse the already stored `dialogue/versions/` source segments. Keep exact cue text, cue ID, milliseconds, edition, hash and path. Split *only strongly indicated* two-speaker caption typography, preserving the link to the original cue; an ordinary wrapped caption remains one unit. Never silently merge consecutive cues into one speech turn.
2. **Scene and participation hypotheses**. Use caption gaps, conversational continuity, location/entrance/exit phrases, named-address patterns and episode synopsis to hypothesize scene boundaries and a small active cast. A time gap is only a provisional boundary; an episode guest credit is not a guarantee of presence. Include unnamed/unknown/soundtrack/offscreen candidates.
3. **High-precision speaker anchors**. Detect explicit character prefix labels (e.g., `HARRY:`), names in directions if actually present, and contextually plausible self-introductions. Identify addressees separately from speakers: `Harry, look here` is *not* Harry speaking. `Your Honor` often denotes an addressee/office, not the judge's own line. Disallow automatic identification from a surname merely mentioned, a catchphrase, or speaker order alone.
4. **Independent local agent proposals**. Give Agent A a consecutive conversation packet and cast/guest names; ask it to resolve dialogue pragmatics and references, with alternative speakers for uncertain lines. Give Agent B the same source plus neighboring packets and longer story chronology, concentrating on scene membership, who knows what, and admissions/denials. Optionally Agent C learns a series-wide *soft* verbal-persona model from independently anchored material, never from its own unverified predictions.
5. **Bidirectional global reconciliation**. Model each candidate speaker as a latent state and maximize a scene-wide score from explicit anchors, cast/scene priors, sequential turn-taking, vocative-to-addressee relations, conversational reply plausibility, and persona evidence. Smooth across episode and across season. Unlike a simplistic alternating A/B pattern, allow multiple consecutive turns from one speaker, new entrants, audience noise and subtitle blocks containing two speakers. Revisit early assignments when later evidence proves who was present.
6. **Adversarial audit and confidence calibration**. A skeptic agent searches specifically for false persona stereotypes, impostors, jokes about identity, direct-address inversion, story contradictions, silent guest roles, offscreen lines and dramatic irony. Require meaningful support, evaluate against held-out *prelabeled* synthetic/open-licensed dialogues with labels hidden at test time, and publish per-role false attribution rates. Multiple agreeing LLM calls using the same evidence are **not independent ground truth**.
7. **Script-like rendering**. Attribute a character only when supported. A low-confidence line prints `UNKNOWN` or `POSSIBLY DAN / GUEST`, not a fabricated definitive credit. Render time markers and cue source links as needed, introduce scene headings as `[PROVISIONAL SCENE]`, retain sound-effect caption annotations separately, and preserve the original word sequence. Editorial stage directions inferred from text must say `[INFERRED]`; never create audiovisual action or laughter absent a source.

## Why 35 episodes make the approach stronger

Season-wide repetition supplies a weak character language model. Harry's manner of addressing a defendant, Dan's prosecutorial exchanges, Bull's guard duties and Mac's clerk duties may yield contextual clues, but stylistic caricatures are unsafe as hard evidence. The series cast list is a source for *possible* roles; guest credits for particular episodes narrow the hypothesis set. Early uncertainty can be revised using dialogue later in an episode or later in a season. Recurring objects, relationships and callback phrases can help resolve identity through plot knowledge, not voice characteristics.

**Avoid circular evidence:** if an agent guessed a line was Dan's, it cannot use that guessed line as an independent Dan-language training example. Only explicit labels, genuinely independently attributed material or externally corroborated factual references may enter a trusted seed pool. Other assignments can be used as a *soft hypothesis* and revisited, not ratified by self-training.

## Concrete formula (implementation target)

For source utterances `u[1..n]` and candidate speakers `s[1..n]`, use scene-aware approximate MAP inference:

```text
score(s) =
    Σ_i   w_anchor  * label_evidence(u_i, s_i)
  + Σ_i   w_cast    * role_prior(s_i, episode, scene)
  + Σ_i   w_prag    * discourse_fit(u_i, context, s_i)
  + Σ_i   w_style   * calibrated_character_language_fit(u_i, s_i)
  + Σ_i   w_mention * addressee_constraints(u_i, s_i)
  + Σ_i   w_reply   * neighboring_turn_compatibility(u_{i-1}, u_i, s_{i-1}, s_i)
  - penalties_for_contradictions_and_unexplained_scene_transitions
```

Optimize scene-wide using beam search, CRF/Viterbi with state constraints, a factor graph, or iterative LLM adjudication. The scores above are *not calibrated probabilities until tested*. Include an `UNKNOWN` state whose cost is low enough to prevent forced guesses. Allow multiple speakers per caption when typography supplies direct evidence, and preserve composite/overlapping timestamps.

A robust assignment output should include `turn_id`, `speaker_id`, `top_alternatives`, `confidence` plus confidence *definition*, `evidence[]` with original cue IDs, `reasoning_summary` (short, auditable, not private chain of thought), `model_revision`, `agent_role`, and `status`. Store agent proposals under a separate immutable provenance hierarchy; a mere proposal never changes source caption JSONL.

## Agent execution contract

Source packets are generated by `tools/prepare_speaker_attribution.py`, without any LLM API dependency. Each per-version `speaker-attribution/` folder contains:

- `candidate-roster.json`: credited show-wide/guest character candidates with status and aliases, including `UNKNOWN` fallbacks.
- `turns.jsonl`: normalized potential utterances with original caption cue references and source timing, deliberately speaker `UNKNOWN`.
- `agent-packets.jsonl`: overlapping 48-utterance work packets with six lines of context overlap, explicit source SHA and candidate roster.
- Catalogue: `catalog/speaker-attribution-preparation.json`, containing per-episode production counts and source limitations.

### Suggested independent worker instruction

> You are a **text-only dialogue speaker attribution worker** for an original *Night Court* episode. Use only the provided caption packet, adjacent source packets, cast candidate roster, and licensed episode metadata. Do not use fabricated memories of television episodes. First reason about scene participation, named addressees and dialogue pragmatics, including conversation transitions; then propose a speaker for each original `turn_id`. Never assume one cue equals one speaker or that turns strictly alternate. `UNKNOWN`, `UNIDENTIFIED_GUEST` and `OFFSCREEN_OR_CROWD` are valid outputs. Do not assume credited principal cast is present in every scene or that the person addressed is the person speaking. Return candidate speaker IDs, alternative IDs, a cautious numeric score, and short **observable evidence** referencing turn IDs. Never invent lines, stage action or source text. Use `speaker: UNKNOWN` if uncertain.

### Suggested independent skeptic instruction

> Review two sets of per-turn speaker proposals. Proactively challenge their strongest assertions. Find contradictions involving vocatives, replies, arrivals, episode-specific cast roles, scene location and uncredited guests. Prefer `UNKNOWN` to a named misattribution. Do not permit probabilistic confidence to be portrayed as a measured probability without calibration; label consensus only as *agent agreement*. Emit an alternative hypothesis when evidence supports one and preserve reasons for conflict. Do not revise the original captions.

## Evaluation without a human naming every line

For automatic regression, start with short original, license-compatible or synthetic dialogues in which speaker labels are known from the outset. Strip those labels before running attribution and score exact speaker accuracy, macro-F1, high-confidence precision, abstention rate, dialogue/scene segmentation quality, and whether the model overclaims on trick cases. Split training/test by *episode* or source to avoid memorizing exact lines. Separately test scenes with misleading direct address, three- or four-character rapid repartee, two speakers inside a single caption, anonymous defendants and incorrect cast assumptions.

Public NLP research is encouraging but its reported results **do not transfer directly** to these caption files. Project Dialogism Novel Corpus (PDNC) comprises 35,978 annotated quotes across 22 novels; an ACL 2023 paper finds that sequence-based attribution of nearby character mentions is competitive, but literary novels contain narration (e.g., “she said”) that stripped TV captions lack. BookNLP's quotation model is worth testing as an optional component, not blindly relying on its off-the-shelf score. See:
- https://aclanthology.org/2022.lrec-1.628/
- https://aclanthology.org/2023.acl-short.64/
- https://github.com/booknlp/booknlp

## Acceptance gates before calling output a “script”

- **Coverage:** every original caption word is retained in a turn, or explicitly classified as non-dialogue. No source cues silently dropped.
- **Attribution:** every definitive named speaker has traceable grounded evidence, and agreement across agents is not confused with objective validation.
- **Consistency:** stable character identifiers, separate named addressee/speaker fields, justified scene roster, no guess-induced learning loops.
- **Reproducibility:** preserve source SHA, source edition, model/agent revisions, packet positions, prompt versions, confidence definition, and changes.
- **Output:** uncertainty is visible and readable, preserving conversational order without hallucinated audiovisual directions.

A zero-human workflow is feasible if “unknown” remains acceptable. A zero-human workflow that labels **every** line correctly from text alone is not generally possible, because some exchanges are observationally indistinguishable without voices or visuals.


## Agent vote format and provisional renderer

An agent receives `agent-packets.jsonl` for an episode version and writes one source-linked vote per turn it can evaluate. Save it at `speaker-attribution/votes/context-agent.jsonl` (and separately `skeptic-agent.jsonl` or other distinct worker IDs).

```json
{"turn_id":"S01E01:C00001:1","speaker_id":"tvmaze:99640","confidence":0.82,"source_sha256":"COPY EXACT SHA FROM CANDIDATE ROSTER SOURCE","evidence_turn_ids":["S01E01:C00001:1"],"short_evidence_summary":"Illustrative schema only; cite a real neighboring exchange here."}
```

The example is **synthetic documentation, not a claim** that the episode's first line was spoken by Harry. Replace every value with grounded packet evidence. Speaker IDs must match `candidate-roster.json`, or use `UNKNOWN`, `UNIDENTIFIED_GUEST`, or `OFFSCREEN_OR_CROWD`. The SHA must match the actual caption version. Never infer a speaker from title alone.

Run:

```sh
python "Night Court/tools/reconcile_speaker_votes.py"
python "Night Court/tools/test_reconcile_speaker_votes.py"
```

The reconciler requires at least two distinctly named agents with agreement ratings at or above 0.75 before tentatively labeling an unlabeled turn. Even then, it marks the result `uncalibrated_agent_agreement`, **not** verified fact. Any speaker conflict, a single agent, low ratings or a possible self-address leaves the turn as `UNKNOWN`. Truly explicit textual speaker prefixes override suggestions and are labeled as such. Each vote's evidence pointers are checked against exact original turn IDs and the source hash; unrelated or fabricated character IDs are rejected.

Only versions **with vote files** receive `speaker-proposals-reconciled.jsonl` and `script-provisional.md` for reading. With zero agent votes, no scripts are fabricated. A global `catalog/speaker-attribution-reconciliation.json` records the situation honestly. The original captions are never overwritten.


## Implementation update: scene participation from credits and addressed names

The 35 existing episode subtitle witnesses already have immutable actor/character candidate rosters from TVmaze and 15,014 caption-derived potential utterances. `tools/build_scene_participation.py` adds a **non-speaker-assigning** evidence pass that summarizes scene-by-scene which characters have textual support. It preserves the separate provenance of:

1. **Show-wide cast credits:** possible series characters, not proof of appearance in a particular episode or scene.
2. **Episode guest actor/role credits:** stronger *episode-level* possibility, still not evidence the credited character was present during a given caption interval.
3. **Explicit caption labels:** a precisely sourced `NAME:` speaker label can identify its own turn when it uniquely matches a roster name.
4. **Names used in direct address:** e.g., an opening `Hi, Bull` provides a hypothesis that Bull is the **listener**, specifically *not* the speaker of that utterance. A named listener may support a scene participation hypothesis without identifying the speaking character.
5. **Unknown people:** `UNKNOWN`, `UNIDENTIFIED_GUEST`, and `OFFSCREEN_OR_CROWD` remain possible, even with a detailed cast list.

Generated per-version `speaker-attribution/scene-participation-evidence.json` gives each provisional scene its source time span, turn references, characters with explicit text support, unmentioned episode guest roles, and unmentioned principal-cast candidates. `catalog/scene-participation-evidence.json` reports coverage without copying spoken lines into the global index.

```sh
python "Night Court/tools/prepare_speaker_attribution.py"
python "Night Court/tools/build_scene_participation.py"
python "Night Court/tools/test_scene_participation.py"
```

This is a stage for narrowing the candidate set in subsequent dialogue reasoning, **not** a new dialogue attribution system or a learned speaker model. Name mentions may be misleading, guest roles may be silent or offscreen, and camera edits cannot be recovered reliably from caption timing alone. No definitive line speaker is promoted without reliable evidence. The independent agent-vote/skeptic/reconciliation process remains the next stage.
