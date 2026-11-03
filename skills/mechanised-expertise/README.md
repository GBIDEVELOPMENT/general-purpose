# Mechanised Expertise skill

The activated [`SKILL.md`](SKILL.md) is a short decision router. It states when to decline analysis, selects one problem-specific reference, and retains a compact executable inquiry contract. Read **only that entrypoint first**; open a reference, script or source record when a verified cue and consequential unknown require it.

The deeper research is preserved in `references/`, `assets/`, `examples/`, `scripts/` and `tests/`. Historical entrypoint text before the usability refactor is archived under `references/legacy-entrypoint-v0.7.md` for traceability, not as an alternative authority. The 30 source-derived procedure descriptions are editorial transformations of pinned recommendations, not 30 independently tested improvements.

## Start-up examples

[`examples/first-run.md`](examples/first-run.md) shows routine, UX, concept-map and Android-native entry routes. The walkthrough is illustrative, not a completed agent trial.

## Validation

From the repository root:

```bash
python3 -m unittest discover -s skills/mechanised-expertise/tests -p 'test_*.py' -v
python3 skills/mechanised-expertise/scripts/audit_compositions.py
python3 skills/mechanised-expertise/scripts/audit_source_mechanisms.py
python3 skills/mechanised-expertise/scripts/check_inquiry.py skills/mechanised-expertise/examples/remote-reconnect.json
```

All compiler outputs remain hypothetical until the actual program, device, user or provider observation is verified. Local structural checks do not measure agent effectiveness. Verify that a target agent runtime can discover this SKILL.md under its configured skills root. A source repository containing it is not automatically an installed skill in unrelated projects.