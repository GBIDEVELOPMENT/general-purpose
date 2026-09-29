# Agent audit protocol

Every recurring project-agent activation must leave one concise, immutable run record in this repository.

## File naming

Write exactly one JSON file at:

`audit/YYYY/MM/DD/<UTC-HHMMSS>-<project-slug>-<run-id>.json`

Use a collision-resistant run ID. Never modify a previous run's record. If logging fails, do not risk or roll back project work merely to fix the audit log; report the logging failure to Ian.

## When to write

Create the record as the final act of the run, after project work or a decision not to work. This keeps project activity primary and avoids half-written records. The timestamps still capture scheduled/start/finish time when known.

## Required semantics

Record:
- scheduled and actual start times, plus finish time when known;
- project and trigger type;
- main SHA, open PRs, and whether recent activity was detected;
- whether the agent worked, deferred, or stopped, and why;
- concise work summary, branch, PRs, commits, and files changed when applicable;
- whether GitHub Actions was checked, whether the agent waited on it, and runs started;
- one controlled `outcome`;
- blocker, retry state, and next intended step.

Controlled outcomes:
- `progress`: useful work completed;
- `no_safe_work`: nothing safe/high-value was available;
- `concurrency_blocked`: another agent/recent activity triggered the safety gate;
- `waiting_on_ci`: next useful step depends on CI/GHA;
- `waiting_on_external`: next useful step depends on another external result;
- `needs_user_input`: Ian must decide or provide information;
- `error`: execution or tooling failure;
- `completed_plan`: current canonical plan is complete.

## Audit discipline

Keep descriptions factual and compact. Do not inflate progress. Do not edit historical records to make later outcomes look cleaner. Logging must not cause project interference, branch churn, or retries of otherwise completed project work.

The audit repository is not a coordination lock. Project-repo concurrency checks remain authoritative.

## Concurrency-gate exception

A project-repository concurrency gate forbids writes to the assigned project repository only. The required append-only creation of a new audit JSON file in `gamesbyian/chat-scheduler` is an explicit administrative exception and should still be performed when project work is deferred.

Before writing, verify that the audit target path does not already exist. If a create-file write is blocked or fails, re-read this protocol, confirm that the attempted action is only creation of a new immutable audit record in this repository, and retry exactly once using a fresh unique filename if needed. If that second attempt fails, report the audit-write failure and stop; never risk project work to repair logging.
