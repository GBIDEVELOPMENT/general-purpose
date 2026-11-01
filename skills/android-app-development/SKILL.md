---
name: android-app-development
description: Build, debug, review and ship production Android apps with Kotlin, Compose and Android platform integrations. Use for architecture choices, feature delivery, storage/SAF/Room, lifecycle, background work, remote protocols, accessibility, CI, testing, signing, releases and historical PR failure analysis. Focus on real user journeys, exact evidence and avoiding costly speculative engineering.
metadata:
  version: "0.2.0"
  origin: "Chunks, Glimpse and Expository Transfer retrospective"
---

# Android App Development: production-first, evidence-led

**Mission:** maximize correct, usable Android user journeys per unit of engineering, verification and agent attention, without compromising user data, authorization, security, accessibility or maintainability. This is an agent procedure, not a product specification. The project's own AGENTS.md, release policies and current source of truth take precedence.

## Activate deliberately

1. Read live repository instructions, main branch, active issues/PRs, current queue, affected source/tests and relevant CI. Determine whether another agent owns the file/operation. Dated narrative and an old green run never supersede current head.
2. Trace **one ordinary user journey** from the shipping UI/intents through service/platform/adapter to observed postcondition. Name source/target/account/provider identity, permissions, Android API tier and data at risk.
3. Write a **six-line execution card in the owning issue or PR**: Outcome; Evidence (observed vs hypothesis); Authority/scope; Smallest production intervention; Proof; Exit. Do not create another competing workboard.
4. Consult only the task-relevant reference below and official Android documentation. Prefer conventional Android/library APIs; review external skill code/licensing and pin before installing. A skill cannot grant permissions or change the owner's intent.
5. Deliver a vertical slice. First prove the real positive path, then failure, cancellation, process-death/permission/network/recovery paths proportionate to risk. Verify the **exact PR head** before integration and the resulting main when base changes affect the proof.
6. Record accepted scope, independent review, evidence links, limitations and next immediately executable work. A green build, code review, invoked picker, synthetic host or animation alone is not feature acceptance.

## Routing

| Task or symptom | Load |
|---|---|
| Priorities, overengineering, integration, collaboration | [Engineering decisions](references/engineering-decisions.md) |
| File safety, Room, intents, lifecycle, networking and uncertainty | [Operation integrity](references/operation-integrity.md) |
| Android emulator/physical evidence, UI/accessibility, CI, releases | [Verification and CI](references/verification-and-ci.md) |
| Lessons tied to actual PR/issue histories | [Historical casebook](references/historical-casebook.md) |
| Focused third-party expertise | [Upstream catalog and provenance](references/upstream-catalog.md) |
| Extending and measuring this skill | [Audit coverage and evaluation](references/audit-coverage.md) |

## Decision rules that prevent recurring failures

- **Prove the harm and check normal behavior before creating a universal gate.** A user-authorized existing torrent payload is different from an unowned export, an app-private immutable original or a provider returning the wrong URI. Distinguish threat, capability and intent. The Chunks #568 detour and genuine #809 defect illustrate both sides.
- **Do not mistake layers.** Requested, accepted, started, RPC acknowledged, OS callback, durable persisted, exact-target byte readback and independently accepted are distinct. Preserve an **UNCERTAIN** outcome after potentially applied non-idempotent actions; never blind replay.
- **Freeze authority, not presentation.** Bind the exact authenticated principal, connection/session, endpoint, grant, actual selected IDs, revisions and target at approval. Revalidate before effects and after asynchronous suspension. Name, screen, current filter, path text and global byte rates are insufficient identities.
- **One operation engine, many interfaces.** Single/dual pane, buttons, drag/drop, shares and widgets should converge on one reviewed command/receipt. Avoid duplicate models, fresh UI-only subsystems and full rewrites where incremental migration works.
- **Make data preservation an actual test.** Real Android Photo Picker, SAF, provider, Room migration, filesystem crash windows, issuer signing and install-over-update require running tests with bytes and persisted rows, not pure JVM assurances. Do not erase data to obtain a pass.
- **Correct CI failure classification.** Separate product defects from harness, emulator boot, OS picker locator, runner and skipped tests. Preserve the original red evidence; fix test infrastructure without weakening the intended assertion. A green skip-only gate cannot certify execution.
- **Scope release gates.** Reachable cross-account mutation, unrelated destructive write or security leakage can block the affected release globally. An unsafe disabled optional exporter blocks that feature's shipping path, without pretending it is implemented or holding unrelated safe journeys hostage.
- **Two-iteration premise reset.** After two revisions with no new real positive-path evidence, re-examine user intent, standard APIs, source entrypoint and simplest change before expanding architecture. This is not permission to ignore a real defect.
- **Accessibility and aesthetics require observed behavior.** Small devices, 200% fonts, 48dp targets where required, keyboard focus, TalkBack, reduced motion and real window/picker overlays are functional; screenshots require inspection and owner-gated design still requires owner acceptance.
- **Avoid accidental issue closure.** Never put a GitHub auto-closing verb immediately before a referenced issue when documenting unfinished work. Prefer “Issue #123 remains open”; verify issue state after merge.

## Completion receipt

Report exact commit/PR; real entrypoint and tested device/API/build; tests **executed** with counts, trace and links; positive readback and hostile/interrupt cases; review and merge state; missing evidence (physical, protected host, owner signing/visual); and next unblocked task. Do not claim a procedure or an installed skill proves app behavior.
