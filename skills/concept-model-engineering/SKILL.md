---
name: concept-model-engineering
description: Construct, populate, audit, extend and explore evidence-backed conceptual models, ontologies, knowledge graphs, user journeys and feature maps. Use when synthesizing messy sources, designing workflows, discovering unmet needs, assessing completeness or evaluating supposedly novel gaps. Separates failures of knowledge acquisition from genuine research frontiers before proposing requirements.
metadata:
  version: "0.1.0"
  origin: "Chunks human graph, AYA understanding framework, Glimpse UX coverage, Expository operation states, UR-Recomp research frontier"
---

# Concept Model Engineering: earn the right to discover the blank spaces

**Goal:** turn a scoped question into a falsifiable, inspectable map whose unresolved regions can be explored without confusing **not in the map**, **not in the observed sources**, **not implemented by a particular product**, and **genuinely novel**. Preserve original evidence and competing interpretations. A map is a tool in a larger workflow, never its own justification.

## Activate proportionately

Invoke for meaningful product discovery, research synthesis, ontology or requirements design, unfamiliar code architecture, cross-project feature relationships, source normalization, frontier investigation or ambiguous user concepts. **Do not** require a full ontology exercise before a routine bug fix.

### Seven-pass procedure

1. **Frame the decision.** Name the *focus question* and the decisions the model must support. Define the domain, product/version, users, temporal scope, excluded regions and three to six *competency questions* the model must answer. Reuse established project concepts; don't invent a parallel ledger.
2. **Recover primary evidence.** Enumerate versioned source classes: original user comments/praise/complaints in their actual languages and contexts, counterexamples/nonusers, competing products, source code, standards, tests, owner decisions and already-existing project models. Keep evidence types independent; count duplicated reports only once. Record what was actually searched and what was inaccessible.
3. **Build the model.** Normalize synonyms and equivalent IDs before inferring absence. Separate concept/classes from instances, roles, attributes, actions and outcomes. Each consequential directed edge forms a meaningful proposition with a specific verb. Encode source, scope, time, uncertainty and truth kind. Cross-link disparate branches and record disagreements instead of averaging them away.
4. **Audit the representation before looking for discovery.** Test competency questions; re-extract from a held-out source; reverse-search from competitor features and unexpected user journeys; compare with a second modeling approach; inspect disconnected components, degree-one nodes, missing roles and absence of failure/recovery transitions. Identify any source type, language, platform or lifecycle phase whose coverage is systematically weak. Revise the map before ranking blank spaces.
5. **Classify each blank.** Label it **acquisition omission**, **alias/identity mismatch**, **schema blind spot**, **underlinked known facts**, **contradictory evidence**, **unknown fact**, **version/provider boundary**, **deliberate exclusion**, or **candidate frontier**. In an open-world map, unrecorded is never automatically false. Load [Frontier qualification](references/frontier-qualification.md).
6. **Challenge apparent novelty.** Search explicitly for implementations, synonyms, predecessors, non-obvious integrations and counterexamples in original-language terms; query relevant primary manuals/code, alternative software and dates. State novelty precisely: new to *this inventory*, new to *this version*, new composition of known primitives, or externally unconfirmed. An unexpected result can be valuable even if somebody else already implements it. A frontier designation is conditional and revisable.
7. **Return a bounded handoff.** Deliver the *smallest useful map delta*, qualified blanks, source and unanswered-question links, next investigation with expected information gain, and exact effects on the parent workflow. Never convert analytical hypotheses into normative product requirements, test claims or authorized work without applicable project authority.

## Load task-specific guidance

- [Frontier qualification and anti-false-novelty tests](references/frontier-qualification.md)
- [Evidence construction, conceptual modeling and integration](references/model-and-evidence.md)
- [Academic resources and existing agent skills](references/research-and-skills.md)
- [Project precedents and counterexamples](references/project-casebook.md)
- [Typed model format and validator](schema/concept-model-v1.schema.json), [fictional teaching fixture](examples/cross-system-journey.json)

## Required distinction

A model may be **adequate for a decision** without covering an entire universe. The correct claim is “adequately populated for *these questions, sources and conditions*.” A frontier claim is warranted only after basic omissions and known counterexamples have been actively sought. It remains a *testable research hypothesis*, not a proved world-first idea.

## Completion receipt

`Focus and scope | source/coverage inventory | changed concepts and specific directed edges | competency-question results | known limitations and contradictory evidence | suspected gaps + type | novelty-disconfirmation attempts | qualified frontier candidates | next action in parent workflow`.
