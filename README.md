# Chat Scheduler Audit Log

This private repository is the audit trail for recurring ChatGPT project-agent runs.

## Design

- Each activation writes a new immutable JSON record under `audit/YYYY/MM/DD/`.
- Agents never edit prior run records.
- Records use `schema/run-record.schema.json`.
- `scripts/build_reports.py` aggregates records into:
  - `reports/automation-runs.csv`
  - `reports/automation-summary.md`
- The audit log is observational. Logging must never interfere with project work.

See `docs/agent-audit-protocol.md` for the required run procedure and controlled vocabularies.

## One-off public tweet recovery

For the separate account-free @ianmakesjokes collector and its evidence-producing
GitHub Actions workflow, see [public tweet recovery](docs/public-tweet-recovery.md).
This utility does not change the recurring-agent audit ledger.

## Shaw email integration (opt-in)

This repository also contains a separate [Shaw IMAP/SMTP command-line client](docs/shaw-mail-bridge.md) for read-only mailbox and folder access and explicitly approved outgoing messages. The client is accompanied by an **experimental encrypted GitHub Actions command bridge** using private issue #6. It can be exercised with a credential-free ping. Do not add the real mailbox secret until the privileged-workflow trust risk described in the guide is addressed. Offline safety tests run without secrets.

## Glimpse native wallpaper-manager design (formerly Waltz)

The separate [Glimpse design and specification workspace](Glimpse/README.md) contains the approved paper-reel direction, complete 73-scenario feature audit, Kotlin/Compose implementation plans, controlled single/dual-reel layout comparisons, editable art, binary reference files and [conversation/production diary](Glimpse/production-diary/2026-10-22-conversation-record.md). The former `Waltz/` directory was renamed to `Glimpse/` on 2026-10-22 without rebuilding or discarding its contents. This design project is separate from the recurring-agent audit log.

## Android app development agent skill

The independently versioned [Android App Development skill](skills/android-app-development/SKILL.md) synthesizes actual production lessons from Chunks, Glimpse and Expository Transfer. It includes [33 historical cases](skills/android-app-development/references/historical-casebook.md), platform and review playbooks, 16 offline engineering-decision regression scenarios, and a self-contained CI-validated Python test suite. Its directory is the canonical private source for now. The skill is *advisory* and does not change or authorize operations in any other project; automatic discovery in another agent runtime still requires a reviewed installation.
