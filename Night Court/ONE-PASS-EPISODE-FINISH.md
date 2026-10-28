# Finish a Night Court episode in one editorial pass

## Actual original-film audio pass, 27 October 2026 (current evidence)

**Both exact source-video SHA-pinned pilot films were acquired and processed successfully** in [private main Actions run #40559268586](https://github.com/GBIDEVELOPMENT/general-purpose/actions/runs/40559268586). The actual one-job elapsed runner window was **133 seconds (18:21:55–18:24:08 UTC)**, including setup, validation and source-result commit; source acquisition plus acoustic inference for **both** episodes took **43 seconds** (18:23:17–18:24:00 UTC). The dependency install consumed 50 seconds. These are verified step timings for **source voice comparison only**, not complete AV screenplay editing or reliable fleet averages. Model reports are committed at `saved-private/episode-finish-current/S01E01-original-audio-p0p1-evidence.json` and `S09E19-original-audio-p0p1-evidence.json`; the one-pass review packets have the exact audio report SHA and numerical machine hints. Media, decoded PCM, weights, and embeddings are not in Git.

| Source metric | S01E01 | S09E19 |
| --- | ---: | ---: |
| Source cue/paragraph windows considered | 267 | 103 |
| Usable embedded original-soundtrack windows | 253 | 98 |
| Provisional named-role leave-one-out correctness | **48/67 (71.64%)** | **24/35 (68.57%)** |
| Measured adjacent acoustic speaker-pair comparisons | 194 | 30 |
| Previously anonymous sound windows tested | 6 | 16 |
| High-priority machine/P0 *disagreement* comparisons | **26** | **7** |
| Provisional cast roles with especially weak model holdout | 3 | 3 |
| New source-audio independently verified character IDs | **0** | **0** |
| New independently AV-certified performed turns | **0** | **0** |

The role classifier's global holdouts **fail** the conservative 80% promotion threshold. Its provisional character labels and acoustic similarity comparisons are **not** human film observations or performance truth. No new named lines should be accepted from these model results alone. The 33 elevated boundaries reflect deliberately conservative **uncalibrated review-priority thresholds**, not 33 demonstrated segmentation mistakes. Similarly the six role-reference warnings are opportunities to listen, not six proven misattributions. Review the flagged passages first **during the normal source-order viewing**, without omitting the remaining boundaries or scene passages.

Original-film delivery has been repaired without a new per-episode pipeline: [#533](https://github.com/GBIDEVELOPMENT/general-purpose/pull/533) adds bounded network preflight; [#534](https://github.com/GBIDEVELOPMENT/general-purpose/pull/534) authenticates before heavyweight setup, retries transient FTP greetings and installs the source-audio FFmpeg decoder from a fixed SHA-256 Linux wheel rather than apt; [#535](https://github.com/GBIDEVELOPMENT/general-purpose/pull/535) preserves partial numeric source evidence, flags acoustic review disagreements, and skips stale manuscript review-packet writes safely. Successful original-source acquisition and analysis are **not** screenplay completion. The next required editorial work is actual synchronized source listening/viewing of P0/P1 high-risk segments and comprehensive performance/action coverage, recorded in the same stable decision ledger.

---


**Operating contract, 26 October 2026.** Two current source-preserving pilot
manuscripts exist on private main. The product is a rich, useful performed
screenplay. The version-per-experiment loop (v6 through v22), proliferating
GitHub Actions, and multiple handoff agents are **not** the new production
method. Those files are historical input/evidence, not instructions to spawn
another vNN. See the P0→P5 priority contract.

## One script, one source witness, one decision ledger, one publication

The **working manuscript** remains the existing canonical
`saved-private/pilot-current/SXXEXX-working-screenplay.md`. Do not create
`v23`, `v24`, new agent-specific manuscript directories or task-specific
renderers to perform normal episode editing. Preserve original SRT/transcript
and every source Unicode span under their immutable SHA. Corrections are
source-exact decisions in **one episode-local ledger**, applied to the same
canonical manuscript by a bounded render-and-validate operation; previous
decisions remain in Git history, not dozens of side-by-side screenplays.

**Original-film verification is now a mandatory, local SHA-256 check:** the
workbench hashes the user-selected exact original source file with browser
WebCrypto, compares it with the packet's pinned original AVI checksum, and
rejects exporting or recording any AV-attested decisions if the media edition
does not match. A locally transcoded playback proxy remains possible for AVI
codec compatibility but is separately labeled as unverified source-equivalence.
Each proposed adjacent dialogue boundary now starts **unreviewed**; the reviewer
must explicitly choose continuation, change, or overlap on actual audio.
To avoid 726 rote dropdown interactions, the player now has an optional
**"Endorse remaining proposed P0 boundaries after listening"** control
for each sequential passage. It is disabled in practice until original-film
SHA verification, source playback and the per-passage watched acknowledgement;
it only fills still-unreviewed boundaries, never overwrites a correction.
The final per-passage save checks each result. The web workbench observes local
non-seeking playback time (at least eight seconds per passage before review
signoff); Python rejects imported ledgers with no such recorded evidence.
Eight seconds is just a minimal anti-checkbox guard, **not** proof that an
entire passage or film was faithfully observed, or that the provisional
speakers were correct. Sustained source playback and skeptical review
remain necessary to make any AV acceptance claim.
Likewise internal caption switches require explicit observed spans or a
source-listened negative decision. The source check and UI gate reduce
accidental false signoff but cannot prove the human watched the film or that
a transcode preserved the original picture and sound.

**Exact-line acting and physical comedy:** P2 delivery, P3 wardrobe/props,
and P4 actor-action-target notes can now be entered on any individual
source reading block during the same playback, under its collapsed
"Beat-specific" editor. These optional notes survive the source-bound
local draft and the ONE episode decision ledger. The final screenplay
renders each observation immediately beside the original dialogue beat
it describes, not at the top of a 12-block scene. The older batch-wide
P2/P3/P4 fields remain available for continuity-wide observations.
No field is automatically populated or represented as witnessed unless
the original film was actually reviewed.

The browser **offline original-film review workbench** is
[episode-finish-workbench.html](episode-finish-workbench.html). Open it locally
(no network libraries), load one private review packet and the corresponding
locally held source film, then review all sequential blocks. It displays exact
original dialogue against the film, allows correction of every P0 transition
and P1 role, and collects performance, costume/props and actor-action-target
notes from the same playback. Export ONE JSON decision ledger and keep it in
the episode's private stable review location. A reviewer must validate their
local video against the original source SHA before certifying; HTML cannot
authenticate what they actually watched, and browser AVI codecs may require a
locally transcoded MP4 viewing proxy.

**Whole-episode playback acceptance (not only clips):** the source-verified
offline video player now tracks each second actually reached by contiguous
non-seeking playback, including footage between caption paragraphs and silent
physical comedy. Its compact watched-second timeline lives in the SAME
locally journaled and exportable episode decision ledger. A reviewer-attested
final screenplay fails the source-AV gate unless at least **97% of the 20–30
minute original-runtime playback** was covered and no continuous unattended
interval exceeds **8 seconds**. Fast seeks cannot manufacture coverage. The
per-passage minimum-eight-second gate remains a separate anti-checkbox check,
not a proxy for finishing the full episode. Video-player telemetry is neither
independent proof of attention nor a guarantee that a locally transcoded proxy
faithfully represents the original SHA-pinned AVI. Reviewer discipline and
independent editorial checks remain required. Incomplete JSON backups can
still be exported, but they cannot pass final acceptance.

**Crash-safe review continuity:** after each genuinely listened and confirmed passage,
the offline workbench keeps one local browser draft keyed by the source-identity
packet SHA. Reloading the SAME episode packet restores the confirmed P0/P1
decisions and P2/P3/P4 notes; re-verifying the original AVI remains mandatory.
Changing numeric audio scores or inferred lexical-seek hints cannot invalidate
those decisions. Changing the actual film edition, immutable dialogue,
canonical screenplay, or ordered source-block layout DOES invalidate the
review. The draft stores notes locally and unencrypted, not media or original
soundtrack; use **Clear locally saved episode decisions** to discard it.
Export the JSON ledger periodically, since browser cache may be cleared.

**Fast CI refresh:** a change to the existing episode finisher or this
single workflow now regenerates two SHA-bound review packets on `main`
without re-downloading either original film or rerunning acoustic models.
Only a separately modified trusted audio trigger
(`research/trigger-original-pilot-audio-evidence.txt`) dispatches expensive
original-source inference. The legacy manuscript factory remains independent
and is not relaunched for an AV editor-only code change.

The **single current review agenda** per pilot lives at
`saved-private/episode-finish-current/SXXEXX-one-pass-av-review.json`.
Regenerate it automatically from the exact canonical published screenplay and
source provenance using one script:

```sh
python 'Night Court/tools/episode_finish.py' --episode both \
  --snapshot 'Night Court/saved-private/pilot-current' \
  --output 'Night Court/saved-private/episode-finish-current'
```

The agenda copies exact original dialogue only inside this PRIVATE repository,
with per-reading-block SHA-256 comparison to the immutable canonical source
reader. No source dialogue is printed in CI logs or exported outside the
private repository. It never includes audio, film, frames or model hallucinated
speech. It pins the **actual original AVI SHA**, original dialogue witness, working
manuscript SHA, all candidate reading blocks, source IDs, all adjacent P0
boundary questions and all provisional speaker roles. Every block appears
exactly once in an ordered batch; boundaries between batches remain in the
queue. Each contiguous batch asks the reviewer/model to resolve P0, P1, P2,
P3 and P4 from the **same original synchronized audio/video playback**.
For S01, caption times are coarse finding aids, not performed voice timestamps.
S09's original transcript remains untimed: we never invent subtitle clocks.
The previously measured original soundtrack [run #40253914693](https://github.com/GBIDEVELOPMENT/general-purpose/actions/runs/40253914693)
provides **231/347 model-proposed audio seek ranges**, with 116 unlocated.
These are NOT certified synchronized dialogue or speaker identities. Import
that numeric evidence ONCE, preserving its verified original film/transcript
SHAs at `saved-private/episode-finish-current/S09E19-original-audio-locators.json`.
Future review packets reuse the stable file instead of new models, downloads,
manual syncing or screenplay versions. The HTML playback UI explicitly labels
these as unverified source-audio seek hints, not source transcript timecodes.

## Editorial production loop: no restarting the episode

1. **Preflight once.** Inspect source availability and SHA, cast, original
   transcript and current working screenplay. Collect known original-film
   audio locators and immutable frames once; cache ephemeral media privately.
2. **One end-to-end original playback**, taking all five relevant observation
   types in each shot/sequence. First mark every actual voice transition,
   adjacent cue continuation, in-caption handoff, interruption and overlap
   (P0). Then identify voices using audible/reference/visible evidence (P1),
   explicitly keeping genuinely uncertain voices UNIDENTIFIED. Note delivery
   (P2), props/wardrobe (P3), stage business and actor-action-target (P4).
   Use models for **proposals and triage**, never auto-promote to witnessed
   facts. Rerun excerpts only for conflicts/low confidence.
3. **Apply corrections to the one manuscript** using exact source part IDs,
   corrected turn boundaries and source-bound reviews. **For two voices inside a single original caption/reader block, use the P0 "within this caption" field in the offline workbench:** enter the first exact words spoken by the next character followed by `| CHARACTER`, or `@Unicode-codepoint-offset | CHARACTER` where that phrase repeats. The final reader uses exact original character spans, never mutates dialogue or invents voice timing. A blank field means *no internal handoff heard* only after original playback. Do not modify immutable
   original subtitles. Save one decision ledger at a stable path, e.g.
   `saved-private/episode-finish-current/S01E01-original-av-decisions.json`.
   Do not overwrite it with newly generated blank decisions.
   The offline editor **separately journals unconfirmed P0/P1 and P2–P4 form
   edits** before navigating to another passage, and saves each partial text
   change after a short pause. Returning to the passage restores those inputs
   without falsely counting them as listened-to or watched. Only a deliberate
   original-AV review confirmation promotes them into the signed decision
   ledger. Local draft recovery remains source-packet-SHA-bound, does not store
   film/media, and is not durable until exported to the private repository.
4. **Render the single source-exact reviewed screenplay.** Once the
   source-viewed JSON exists, validate every transition, block role, batch
   observation and original source/media SHA, then render the same named
   reviewed screenplay from the one ledger, not a vNN:
   ```sh
   python 'Night Court/tools/episode_finish.py' \\
     --episode S01E01 \\
     --snapshot 'Night Court/saved-private/pilot-current' \\
     --output 'Night Court/saved-private/episode-finish-current' \\
     --verify-decisions 'Night Court/saved-private/episode-finish-current/S01E01-original-av-decisions.json' \\
     --render-reviewed-screenplay
   ```
   **Durable promotion is automatic after the complete ledger is committed.**
   Put the workbench export at
   `Night Court/saved-private/episode-finish-current/S01E01-original-av-decisions.json`
   (or the analogous S09E19 path) in private `main`. The EXISTING
   `night-court-episode-finish.yml` workflow runs the source-verified
   final-reader validator, refuses partial/inconsistent source playback,
   and writes `S01E01-original-av-reviewed-screenplay.md` plus a SHA-guarded
   `S01E01-original-av-reviewed-manifest.json` **at the same stable paths**.
   No additional workflow or manuscript edition is created. Partial
   exports can also be committed: they are preserved as drafts and cannot
   publish a finished screenplay. The provisional immutable snapshot
   `pilot-current` remains available as source provenance; the accepted
   reader takes precedence for editorial consumption when its manifest
   verifies against that original manuscript and source witness.

   A second independent editor may add
   `S01E01-independent-original-av-acceptance.json` with the same packet
   SHA, decision-ledger SHA, rendered-screenplay SHA, pinned original film
   SHA, and **at least three independently checked source blocks from
   each third of the episode**. That report must come from a separate
   real reviewer and claim no remaining P0/P1 contradictions; passing the
   machine-readable gate alone never proves the reviewer watched film.

   This produces `S01E01-original-av-reviewed-screenplay.md` only after
   all exact caption rows are conserved and all source-reviewed turn and voice
   decisions are accepted or explicitly marked UNIDENTIFIED. The renderer
   refuses a same-speaker turn containing incompatible roles, lost original
   caption text or undocumented timing. The reviewer-attested file still
   requires independent second-editor spot checking, which cannot be proven
   by software alone.
5. **Accept or explicitly abstain.** Every adjacency, actor attribution and
   sequential viewing batch needs disposition. The source-pinned
   `verify_decisions` helper refuses missing turns, unheard source claims,
   absent scene passes, mismatched media SHA or stale manuscript. It checks
   a reviewer's declarations; it cannot prove a reviewer actually watched.
   Run an independent editorial spot check, reconcile harmful mistakes, then
   publish once. Stage directions never outrank wrong P0/P1.
6. **Move to the next episode.** One lead editor, one independent sample/review,
   not five agents spending two days relaying incremental versions.

## Actual current checkpoint, not a finish claim

The source-integrity-tested canonical manuscripts were saved successfully by
[main publication run #40441814247](https://github.com/GBIDEVELOPMENT/general-purpose/actions/runs/40441814247):

| | S01E01 | S09E19 | Combined |
|---|---:|---:|---:|
| Original caption-derived source units | 404 | 347 | **751** |
| Reading blocks (NOT independently heard turns) | 405 | 323 | **728** |
| Provisional displayed groups | 275 | 234 | **509** |
| Provisional adjacent joins requiring P0 confirmation | 130 | 89 | **219** |
| ALL adjacent source block boundaries requiring AV disposition | 404 | 322 | **726** |
| Units with UNKNOWN speech | 14 | 74 | **88** |
| Review batches (12 reading blocks per sequence) | 34 | 27 | **61** |
| Original-AV independently accepted voice/turn decisions | 0 | 0 | **0** |

The 61 review batches are **not 61 GitHub Actions runs**. They are adjacent
passages on the same 2 original videos, reviewed in source order in two
continuous sittings, not 61 12-second downloads. No fixed price or 30-minute
completion claim has been measured for this system. S01 contains sampled
original-picture evidence only. S09 source paragraphs need true soundtrack
alignment; original video has been previously decoded experimentally, but
the currently saved speaker labels are still contextual/model proposals.

## What the unified GitHub Actions job does

`.github/workflows/night-court-episode-finish.yml` is the single
**normal editorial review-queue workflow**, producing and preserving the
current two evidence-bound review packets on private main without inventing
AV certification. On PR it only runs offline integrity tests. The existing
`night-court-private-working-drafts.yml` remains the **canonical manuscript
publisher** while we migrate its legacy v6→v16 chain. It automatically
rebuilds the current source SHA-pinned edition and 193-episode fan retrieval,
then the one-pass workflow updates the two current AV agendas. Normal
episode edits should not dispatch the many older research/benchmark workflows.

Do **not** misreport this first infrastructure consolidation as completion
of source-video viewing, speech identification, source synchronization or
scene acceptance. The remaining nonautomatable bottleneck is authentic
original audiovisual evidence review and skeptical editorial judgement, not
another generator version. The next engineering increment is direct
source-once audio/video inference and integrated decisions applied to the
stable working manuscript, rather than producing another named edition.
