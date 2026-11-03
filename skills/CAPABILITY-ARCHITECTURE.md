# Agent Skills capability architecture

This directory is a library of **complementary capabilities**, not a pyramid with one master methodology. Select the *single primary skill* whose deliverable matches the task; add another only for a concrete, unresolved dependency. No skill can grant permission to modify a project.

## Five orthogonal capabilities

| Capability | Primary output | Example | Avoid |
|---|---|---|---|
| Domain reference | Applicable platform/API contract, version, prerequisite and exception | Identify Room migration contract or Android background restriction | Treating borrowed guidance as executable proof |
| Operational execution | Changed implementation, research extract, user interaction, or test artifact | Fix a file grant bug and run the installed acceptance journey | Replacing work with a plan |
| Mechanised inquiry and decisions | Source-linked choice-changing questions, alternatives, discriminators, stop rules | Identify which unanswered retry condition changes a design | Asking an agent to imitate intuition or investigate everything |
| Conceptual modelling | Typed concepts and relationships, coverage results, qualified unknowns | Build a map of users, intents, states, media identities and recovery | Equating missing edges with real-world absence |
| Verification and evidence management | Independent observation tied to exact claim, environment, and revision | Show a persisted file survived restart, or mark untested | Promoting simulated, planned or verbal claims into observed success |

The same project can need several capabilities, but **none is a universal prerequisite**. A tiny visual correction may need only operational execution and a focused check. An ontology review may start directly with Concept Model Engineering. A complex UX problem may need user research, modelling, choice generation, implementation and runtime testing. The observed task determines the sequence.

## Two-way application without hierarchy

- **Mechanised inquiry → conceptual modelling:** generate a bounded question; invoke modelling only when an uncertain *relation* could alter a real decision, research question, or output.
- **Conceptual modelling → mechanised inquiry:** use deterministic extraction, alias checks, reverse traversals, counterexample probes and explicit stop conditions *inside the modelling workflow itself*. Do not require a full second skill just to run these operations.
- **Both → other work:** user research, implementation, testing, design, debugging and delivery can each consume findings. A model is a possible product deliverable, not an obligatory intermediary.
- **Other work → both:** observations and test outcomes may update source claims, conditional question templates and model relations. Preserve direct evidence and editorial inference separately.

## Routing examples

1. Known Compose layout bug with a reproducer: Android Development first; fix and test. No map or research committee.
2. Integrating two independent user workflows whose identities differ: primary engineering/product skill; invoke a bounded map only for relationships that could change implementation or UX.
3. Building an ontology from multilingual source material: Concept Model Engineering directly; apply its own mechanical source inventory, extraction, identity, relation, and gap-audit operations.
4. Compiling third-party recommendations into agent procedures: Mechanised Expertise; preserve pinned source scope, convert only inspectable conditions into operations, and separately record unsupported editorial extensions.
5. Reviewing a shipped result: task-specific verification; a passing mocked result never establishes remote/provider effects.

## Acceptance for changes to this library

For every new procedure specify **activation evidence, rejection condition, required inputs, ordered actions, named outputs, decision branch (when applicable), independent oracle, and stop rule**. A standalone reference may describe facts without becoming a mandatory workflow. Check both positive and negative control tasks. Do not require all skills in a single agent's initial context. No method gains authority merely because its name appears in a parent skill.
