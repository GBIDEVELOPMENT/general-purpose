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
