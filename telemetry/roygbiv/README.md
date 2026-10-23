# ROYGBIV creative usage evidence

**Repository:** `gamesbyian/general-purpose` (private)  
**Data branch:** `data/roygbiv-usage`  
**Producer:** `gamesbyian/wallgen` ROYGBIV Creative Behaviour Recorder, when explicitly enabled.  
**Status:** Storage destination reserved; **no app-side recorder, credentials, data events or uploads are configured yet.**

## Separation and naming

This branch houses independently retrievable, append-only personal usage evidence. It is separate from recurring-agent audit records under `audit/` and must not contaminate normal `main` development or trigger normal project CI. Future general-purpose use could add other namespaced products alongside ROYGBIV.

Proposed immutable paths: `telemetry/roygbiv/YYYY/MM/DD/<session-id>/<batch-id>.json`. Each batch is a bounded set of recorder event envelopes with unique IDs and monotonic local event sequence. Source schema and current semantics live in the [ROYGBIV telemetry plan](https://github.com/gamesbyian/wallgen/blob/main/docs/CREATIVE-BEHAVIOUR-RECORDER-PLAN-2026-10-22.md), tracked by [#542](https://github.com/gamesbyian/wallgen/issues/542).

No files of raw interaction data have been created yet. Any eventual test records must be clearly marked as fixtures and not counted as observed usage.

## Write and retrieval contract

- The Pages client first records **consented** usage into IndexedDB. A separate optional personal sync mode uploads **bounded batches** using GitHub's Contents API and `branch=data/roygbiv-usage`. No browser credential is included in GitHub Pages source, repository settings files, recipe links or PNG metadata.
- Use deterministic per-batch paths/IDs, never overwrite an existing batch, avoid one commit per slider gesture, and retain the outbox locally until actual API acknowledgement. Retries that encounter a preexisting path must verify that the existing blob matches the expected batch before marking it acknowledged; a failure cannot silently discard data.
- Keep chronological recipe changes, complete exact export/supersession snapshots and optional survey answers in the same evidentiary chain. Never present an Android app exit as a confirmed intentional abandonment.
- Strictly omit access tokens, user-entered PNG metadata, uploaded source photos, full URLs, unbounded text inputs and raw keystroke/pointer recordings by default. Store only what the recorder's disclosed user settings authorize.
- Consumers should specify `ref=data/roygbiv-usage` when reading GitHub files. Build reports from these private records and cite the source batch and revision; preserve provenance and distinguish telemetry observation from agent interpretation.
- This destination is **not a security boundary:** a fine-grained personal access token granting Contents write to `general-purpose` can access the repository beyond this branch and folder. Prefer short-lived/rotatable credentials and protect the user's existing private repository contents. Dedicated repository isolation remains an optional security improvement if required later.
- No workflow should run on every telemetry batch commit. Any analytics job must be on-demand or carefully scheduled and not hold up normal app use.

This file is a destination contract only, not evidence that instrumentation, private authentication, backend services, upload or retrieval have been implemented.
