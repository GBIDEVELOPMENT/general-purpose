# Evaluating the skill without grading our own homework

The [decision corpus](../assets/decision-regressions.json) contains 16 adversarial historical decision points from [the casebook](historical-casebook.md). Each has three specific actions, one judged best under its *given* user intent, and a cited underlying retrospective. Some distractors sound protective but would harm normal behavior; others allow real unsafe writes.

## How to run

1. From this skill root run: `python3 scripts/evaluate_decisions.py --emit-prompts > /tmp/android-prompts.json`. Only the prompt/options, never expected answer, rationale or source, appear.
2. Give the prompts alone to a separate agent session, ideally one with the skill loaded and one without. Require JSON list of `{"id":"T01","choice":"A","rationale":"reason with risks/evidence"}`, one response per ID. Do **not** let a genuinely blind candidate see the repository, casebook, answer key or prior results. Otherwise mark the study open-book.
3. Score off-session with `python3 scripts/evaluate_decisions.py --grade /tmp/android-responses.json --strict`. Report correct/total and inspect rationales **manually** for invented evidence, valid alternatives, uncertainty and reasonable escalation. The scorer tests only option choice; it cannot judge code, engineering time, or Android behavior.
4. For real utility, randomize independent case sets and task order, use fresh agents matched for model/tool access, add new previously unseen scenarios, assess *actual patch* validity, exact-head CI evidence, side effects, review minutes and time-to-user-functionality. Never tune the skill on the same examples and call that an unbiased gain.

## Explicit limitations

- The answer key is stored beside prompts for transparency; the built-in corpus by itself is **not blind** or an independent benchmark. Prompts deliberately omit the key but the evaluator must withhold repository access to enforce real blinding.
- A perfect 16/16 multiple-choice grade **does not prove** safe Android code, real-device acceptance, or a faster project. Failing any one case is a diagnostic signal, not proof that all similar tasks fail.
- Cases are grounded in historical public PR/issue descriptions and host-repository evidence; some old PR text contained *pending* CI. Inspect current integrated source before applying any date-stamped status.
- The casebook is intentionally concise and linked; do not copy private user content, credentials or unreleased code into a public test corpus.
