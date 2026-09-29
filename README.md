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
