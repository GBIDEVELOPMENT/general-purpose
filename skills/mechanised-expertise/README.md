# Mechanised Expertise Skill v0.1

This advisory skill connects existing general-purpose [Engineering Judgment](../engineering-judgment/SKILL.md), [Concept Model Engineering](../concept-model-engineering/SKILL.md) and [Android App Development](../android-app-development/SKILL.md) procedures. It adds dynamic inquiry generation, source-targeted research, knowledge-map audits, conditional choice, independent verification and a structured record format.

Unlike a universal checklist, question families are activated only by observed risk cues; routine, low-stakes changes should remain lightweight. Original third-party claims and novel heuristic proposals must remain distinguishable. The inquiry-card format is a **tool for complicated cases**, not a required artifact for every feature.

Run `python -m unittest discover -s skills/mechanised-expertise/tests -v` from repository root, or `python skills/mechanised-expertise/scripts/check_inquiry.py skills/mechanised-expertise/examples/remote-reconnect.json`. The teaching example is intentionally *unverified*: its scenarios are investigation hypotheses, not claims about a particular shipped app.

The companion v0.7 mobile research corpus contains an automatic (unreviewed) first-pass linkage between earlier recommendation IDs and proposed expertise questions. Its mapping is not published evidence of effectiveness.

## Source-backed strength combinations

The [synthesis table](references/source-synthesis.md) links 22 inspected pinned original recommendations to proposed conditional procedures; it does not establish their effectiveness. [Mechanised intuition](references/mechanised-intuition-method.md) defines expert cues, minimal high-value questions, coverage-qualified model gaps, decisions and independent proof. [User needs/prior art](references/user-needs-and-prior-art.md) extends this to UX, including nonusers, native-language feedback, accessibility and error recovery. The [worked list example](examples/transfer-list-discovery.md) is explicitly unverified.

The corpus still contains editorial, overlapping and incompletely mined source records; avoid counting generated mappings as corroboration. These references only load when the current task warrants them.

## Composition operators (v0.3)

The optional [10 conditional multi-source recipes](assets/compositions-v1.json) refer to the 22 pinned author prescriptions in [source-to-expertise-v09.csv](assets/source-to-expertise-v09.csv). Read [the application method](references/composition-operators.md) for activation, counterexamples, research routing, concept-map boundaries, decision reversals and independent proof. These are **new editorial compositions**, not independent source prescriptions or evidence that agents perform better.

Run `python3 skills/mechanised-expertise/scripts/audit_compositions.py` and `python3 -m unittest discover -s skills/mechanised-expertise/tests -v`. Structural checks reject unknown sources, absent exceptions, non-questions, missing oracles and effectiveness overclaims. They cannot substitute for real task trials.
