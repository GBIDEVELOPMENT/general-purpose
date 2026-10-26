# Context-only dialogue-turn and speaker reconstruction: reusable agent process

**Applies to:** Original-series *Night Court* (1984–1992), any episode `SXXEXX`.
**Owner intent:** A resourceful agent should reason through all available episode dialogue and contextual evidence, without running repository code or computational episode-processing tools, and save a reversible, source-bound attribution review.
**Priority:** P0 correct speaker-turn segmentation (join/split) **before** P1 speaker/character identity. Further performance, costume and staging annotation is out of scope except as explicitly supported by textual evidence.
**Authority:** Follow [script priorities](SCRIPT-PRIORITIES-AND-ACCEPTANCE-2026-10-25.md), the latest [README](README.md) and relevant `AGENTS.md`. This process specifies an *editorial investigation*, not a new acceptance standard.

## Invoke with a single episode identifier

Suggested short request to a new agent:

> Apply `Night Court/CONTEXTUAL-SPEAKER-RECONSTRUCTION-PROCESS.md` to **SXXEXX**. Read the latest held dialogue and relevant episode/repository context, reason carefully over all turns and speakers, consult helpful online sources, save source-linked findings in the repo, and merge qualified documentation-only work. **Do not run repository scripts, software, workflows, recognizers, diarizers, video processors or tests.**

Replace `SXXEXX` with the actual target, e.g. `S05E06`. The invoking message may specify stricter limits (such as report-only), which prevail. No additional instructions or elaborate prompt are necessary.

## Permitted and forbidden actions

**Permitted:** GitHub connector reads/writes, browser research, manually reading held subtitles, scripts, caption sidecars, manifests, credited cast, prior episode work and private artifacts if authorized and accessible; comparing passages conceptually; creating an editorial report and source-linked data file; focused PR/merge after checking live branch state. An agent may use available tools to *retrieve and inspect stored text*, but may not execute code for episode processing.

**Forbidden during this process:** Running scripts or software *in the repo*, tests, Actions workflows, runners, programmatic dialogue alignment, third-party processing executables, ASR, diarization, voice embeddings, video/frame parsing, audio playback/analysis, automated NLP extraction or model inference on video/audio. Do not dispatch or pay for external analysis tasks. Do not edit original SRT, caption, transcript or provenance files. Do not claim that textual deduction authenticated performed voices, motion, scene changes or audiovisual completeness.

If an artifact cannot be accessed without running forbidden software, record the limitation and use the newest accessible held dialogue. Do **not** abandon the task or silently use an older draft without noting it.

## Investigation procedure

### 1. Recover current repository and source reality

1. Inspect live `main`, Night Court README, `AGENTS.md`, source-first P0/P1 policy, episode-specific plans, issues, PRs, amendments and existing named units. Other agents may have advanced the project since an earlier chat.
2. Locate **the latest** held episode dialogue: original subtitle/closed-caption source, transcript versions, reading-script scaffold, generated manuscripts, episode-specific reports, cue-role amendments, source-sidecars, and if accessible the latest useful private workflow artifacts (read-only).
3. Record episode title, season/date, caption witness/edition, SHA/hash, original cue count, provisional performed-turn count *if actually available*, cast and guest roles. Never equate raw cue count with real performed turns.
4. Read the **entire available episode** in chronological order before finalizing speaker names. Re-read difficult scenes and later payoffs.
5. Check whether previous character assignments are provisional, directly sourced, or independently audio/visual-certified. An earlier AI guess is not a ground-truth anchor.

### 2. Build a narrative and participation model

Identify probable narrative threads, locations, conversational objectives, cast/guests, aliases, disguises, narrative reversals, callbacks and plot chronology. For each probable scene track **definite / probable / possible / merely-mentioned** participants, inferred arrivals and departures, and any off-screen, imagined, quoted or recorded voices.

A subtitle time gap is **not** proof of an actual scene cut. A name mentioned is **not** proof the person was on screen. A cast credit is **not** proof that a guest spoke a particular line. Episode synopses omit events and must not be promoted into observed scenes.

### 3. P0: reason about turns before character labels

For every caption or paragraph, ask whether it belongs to the **same performed speaking turn** as adjacent captions or whether it contains **multiple speakers**.

Analyze grammatical continuation, interruption, sentence completion, dialogue-directed interjections, overlap and quoted/document-read speech. Join consecutive same-speaker captions for editorial reading while retaining many-to-many source cue memberships. Propose internal speaker splits *without inventing audio timestamps or unverified Unicode offsets*. Flag source strings that look malformed or contain transcriber punctuation errors instead of silently rewriting the original text.

Track an ordered voice sequence for any mixed caption; never award a whole caption to the first speaker if another voice plainly appears. Distinguish source cue count, proposed turn fragments and *verified* speaking turns.

### 4. P1: resolve identity through complementary textual constraints

Treat every utterance as linked to the surrounding conversation. Apply **all** of these reasoning modes rather than merely guessing who sounds characteristic:

- **Coreference and syntax:** Resolve first/second/third-person pronouns, omitted subjects, possessives, nicknames, titles, demonstratives, familial/occupational descriptions and aliases across lines. For each relevant mention distinguish *speaker, addressee, referent* and *claimed persona*.
- **Conversational adjacency:** Match question↔answer, request↔response, accusation↔denial, challenge↔defense, setup↔punchline, greeting↔reply, correction↔error and interjection↔continuation. Conversational adjacency suggests structure but never guarantees an alternating-speaker rule.
- **Scene membership:** Use established participants and plausible entrances/exits to eliminate incompatible candidates, keeping off-screen or as-yet-unintroduced speakers possible.
- **Knowledge constraints:** Check what each character knows, witnesses, conceals, discovers or mistakes at that point. Test whether an attribution would have somebody respond to information they could not have received.
- **Distinctive roles:** Use who normally makes courtroom announcements, prosecutes, defends, rules, keeps records, escorts prisoners, etc. A role alone is weaker than explicit conversational evidence.
- **Character and series history:** Use established language, nicknames, recurring relationships, timelines, running gags, humor style and prior confident attributed lines. Avoid converting stereotypes ('Bull would say that') into certainty.
- **Long-range context:** Link callbacks and recurring props/topics across scene changes, and re-examine early lines in light of later developments.
- **Exclusion and alternatives:** Record why one character fits and which others remain possible. Rule out impossible identities before choosing the most plausible.
- **Performed persona versus performer:** Track channelled spirits, impersonations, roleplaying, internal conscience, fantasy, quoting, written instructions and recorded media separately from the *actual* character whose physical voice may be heard.

### 5. Search for direct, genuinely independent textual evidence

Inspect relevant **in-repo sources first**, followed by targeted online research such as episode Wikiquote, IMDb quote/cast information where available, TVmaze, TheTVDB, Night Court Wiki, episode recaps, reviews, public transcripts, and confidently named speech from other episodes.

Match specific quotations to the held text, noting changed wording, edition drift and attribution contradictions. Prefer sources which **explicitly associate a quotation with a character** over generic descriptions of a scene. Multiple webpages copying the same unattributed captions are not multiple independent confirmations. Cast listing alone cannot settle who delivered a specific turn. Respect copyrights; quote minimally, cite URLs and cue anchors rather than copying long transcripts.

### 6. Global bidirectional consistency review

Reconstruct *each entire scene* with provisional turn segmentation and candidate speaker labels. Review **forward and backward**, not just caption by caption:

- Does the conversational exchange remain coherent?
- Are pronouns, addressees, aliases and replies consistently resolved?
- Does the supposed speaker know what is being said?
- Is the participant in the scene, or is an entrance/exit missing?
- Is a continuous speech fragmented, or are several performers falsely merged?
- Has an earlier named label been wrongly trusted?
- Is an apparent self-answer or third-person self-reference intentional humor, quotation, acting or a true contradiction?
- Would a later well-grounded reply identify an earlier questioner?

When an inference contradicts another, **reopen both hypotheses**, including confident earlier ones. Preserve multiple hypotheses rather than forcibly selecting a unique character.

### 7. Exhaustive second pass and high-information triage

Revisit the entire source after initial assignments. Challenge every supposed high-confidence speaker with the strongest alternative. Re-examine guest introductions, rapid group exchanges, terse replies, suspicious joins, probable within-caption switches, malformed captions and cliffhanger/payoff scenes.

Prioritize unresolved lines that would unlock *several adjacent turns* or constrain participant sets. An isolated one-word reply may remain genuinely unidentifiable and deserves less effort than a switch starting a long exchange.

### 8. Evidence and confidence discipline

Every proposed role should have an evidence type and enough local context to be auditable:

- **High (contextual):** Strong conversational constraint or direct published speaker attribution, still **not** original-soundtrack verified.
- **Medium:** Plausible character with meaningful alternative(s).
- **Low:** Weak hypothesis kept only as a candidate, not printed as settled role.
- **UNKNOWN / abstain:** No adequately discriminating evidence.

Note whether support comes from *speaker/addressee reference, grammar, adjacency, scene membership, occupation, story continuity, quoted source, stylometry or exclusion*. Do not double-count dependent clues or infer independent confirmation from multiple similar LLM judgments. Retain the real possibility that a previous label is wrong.

## Deliverables: save to GitHub

**A. Episode editorial report** near the existing Night Court episode research, titled by episode and review date. Include the live-main state, exact latest source version/hash, whole-episode narrative/participation overview, source refs for strongest assignments, corrections to earlier labels, proposed P0 joins and mixed-cue ordered splits, guest/persona distinctions, support URLs, problems in original witness text, ambiguities, rejected alternatives, and a prioritized set of hard remaining questions.

**B. Machine-readable, reversible source sidecar** in the episode's `derived/` or established research lane. Follow an existing schema if suitable. Cover every original source cue, including abstentions. For each relevant cue or part track source cue ID, source version/hash, proposed turn membership, ordered speaker parts if a mixed cue, role/persona, confidence, competing candidates, evidence type, brief rationale and `text_only_unverified` status. If precise textual offsets or time envelopes have not been checked, store null/unknown rather than fake values. Do not overwrite source dialogue or insert speculative names into official acceptance ledgers.

**C. Counted outcome** listing original source cue denominator, high/medium/low and unknown **caption** dispositions, number of suspected in-cue switches and same-speaker joins, previously labeled corrections, and what is *not* verified. Do not turn these into character-attribution accuracy metrics absent true independently reviewed ground truth.

**D. Repository integration:** Create a focused branch and PR, inspect live diff/merge state, then merge safe, non-destructive, documentation-only results where justified. Respect concurrent agents and unrelated PRs. Confirm committed files on `main` or report clearly if blocked. Do not alter original source, run CI to produce more evidence, or count this as AV acceptance.

## Acceptance checklist

- [ ] Latest authoritative held episode source inspected and SHA/version recorded
- [ ] Whole accessible dialogue read, including endings and callbacks
- [ ] P0 joins and internal speaker switches independently considered
- [ ] Pronouns, references, addressees and scene participation examined
- [ ] Question–answer, interruption, knowledge and information-flow constraints examined
- [ ] Character-specific and cross-episode evidence used cautiously
- [ ] Helpful in-repo and online source attributions assessed for independence
- [ ] Early assignments re-evaluated in light of later passages
- [ ] Guest/performed-persona identity separated from physical-voice identity
- [ ] Conflicts, alternative roles and confident abstentions preserved
- [ ] Results are reversible, source-cue-linked, unverified and complete for the input cues
- [ ] Changes committed through a focused PR; final main status verified

**Optimization goal:** the most *correct* and *coherent* reconstructable account of who says what to whom, through reasoning and available text alone. Do not chase a named-coverage number or mistake an elegant guess for verified performance evidence.
