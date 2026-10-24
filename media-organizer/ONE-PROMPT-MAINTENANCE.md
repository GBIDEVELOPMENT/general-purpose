# One-prompt FTP Downloads maintenance

**Status:** Initial owner-directed cleanup accepted and closed on 2026-10-24. This document is the operational starting point for future sessions, not authorization to run periodic background tasks.

## Prompt for next time

> Please do another complete FTP Downloads cleanup in `gamesbyian/general-purpose`, following `media-organizer/ONE-PROMPT-MAINTENANCE.md`. Work autonomously through inventory, planning, guarded GitHub PRs and trusted FTP workflows, verify every transaction journal, update the status ledger, and finish with a concise before/after report. Preserve the existing mixed movies/TV layout, rTorrent working paths, alternate media editions and active Night Court dependencies. Escalate only genuinely ambiguous or potentially destructive media decisions.

This is a **single initial instruction**, not a promise of uninterrupted execution across disconnected chat sessions. Continue as far as the active session and available tools permit. Workflow completion may require a follow-up turn if a run is still executing.

## Scope and standing preferences

- FTP root is `/downloads`; films and television **remain mixed** at top level, with series/season and film/franchise subfolders.
- Prefer Plex-compatible `Show (Year)/Season 01/Show (Year) - S01E01.ext` and `S01E01-E02` for true multipart episodes. Distinct quality editions and subtitle companions stay distinct. Preserve names and folder structures when Plex already recognizes them.
- Owner previously authorized deleting `.nfo`, screenshots and `Screens` debris and multipart RAR volumes **only when extraction is positively verified**. Empty obsolete release directories may be removed with nonrecursive live emptiness checks. Authorization is scoped to demonstrated junk, never a wildcard for all videos or archives.
- Leave `/downloads/rtorrent`, `/downloads/watch/rtorrent`, active torrent-related paths, unmatched archive sets, potentially valuable artwork, and any media used by active production/transcription pipelines alone without positive evidence they are safe to alter.
- Special hold: original *Night Court* AVI filenames while other workflows depend on them; TNG cross-season `S03E26S04E01` is not a one-season episode. Avoid assuming `PROPER`, HDR, resolution and release labels prove actual stream characteristics.
- File moves may break torrent seeding references; inspect active jobs and coordinate path changes when necessary.
- Never commit or print FTP credentials. Use the existing trusted GitHub Actions workflows and repository secrets. PR checks are offline, and writes are restricted to the main-branch trusted job.

## Single-session operating procedure

1. Read `AGENTS.md`, this document, `media-organizer/STATUS-2026-10-24.md`, `POST-CLEANUP-PLEX-TRIAGE-2026-10-24.md`, and the README files for each executor. Reconcile current `main`, recent merges, open PRs, GitHub Actions runs and the `reports/ftp-media-inventory` branch. Do not replay completed manifests.
2. **Inventory first.** Use `.github/workflows/ftp-media-organizer.yml` (read-only, trusted `main`) and review its audit artifact, `summary.json`, full inventory and Plex risk audit. Demand `scan_errors=0`, `truncated_dirs=0` before making claims about absence. Any truncated subtree is unknown. Inventory records can be stale after a concurrent FTP write; do not overlap scans with movers.
3. Classify: high-confidence Plex renames and series/franchise grouping, genuine metadata/screenshot debris, verified extracted RAR groups, and obsolete empty directories. Separate ambiguous content, sidecars, subtitle tracks, multi-episode and alternate-edition media. Do not confuse a heuristic warning with a verified defect.
4. Produce exact-path, bounded manifest(s) using existing executors. Validate root, uniqueness, source sizes and available MLSD modify timestamps; preflight all move sources before any operation and require collision-free destinations. Check video and subtitle companions; preserve original extensions and content. Prefer the existing tests rather than creating a bespoke high-privilege workflow.
5. Create PR(s) against `main` for plans. Allow offline tests; verify their result. Merge only a reviewed, limited manifest. The merge triggers trusted FTP apply. **Serialize privileged writes**. Never allow an old PR to overwrite the current approved manifest, and do not assume a PR green check made remote changes.
6. Retrieve each trusted run's ZIP artifact and inspect `completed.json` or equivalent: batch ID, every expected path, actual moved/deleted/skipped counts, remaining failures. `success` is necessary but **not sufficient**. A partial batch requires journal-based idempotent recovery before any repeat. If a task is still running, work ahead on analysis and documentation but do not launch conflicting FTP modifications.
7. Clean vacated paths using `approved-empty-release.json` and `empty_release_dirs.py` only after move journals prove sources are vacated. It uses literal paths and nonrecursive FTP `RMD` with a live empty check. Skip and investigate directories with any children, including hidden items; always retain rTorrent work areas.
8. When writes settle, do a fresh complete read-only inventory. Compare before/after file counts, empty folders, anomalies, moves and storage savings only where evidence is reliable. File counts can legitimately change after deletes and reorganizations, directory counts after removing old folders.
9. Add a dated, append-only completion checkpoint to the status ledger with run IDs, PRs, commit SHAs, artifacts, actual totals, exact exceptions, preservation holds and follow-up priorities. Do not overwrite historical evidence. Close the user-directed cleanup as complete when high-confidence work is executed and audited; classify unresolved judgment calls as explicitly **deferred**, not invisible.
10. Report the result concisely with links to the latest inventory, audit runs and important PRs. Be transparent if pending CI or inaccessible artifact prevents completion.

## Provenance of first accepted pass

Owner accepted the cleanup on 2026-10-24, after:
- 697 NFO/screenshot debris files and 666 independently verified redundant RAR volumes deleted, plus subsequent targeted debris cleanup (earlier detailed ledger).
- 211 earlier TV moves, seven film moves, substantial subsequent Trek, Studio 60 and 30 Rock organization; 27 surplus Trek copies pruned under reviewed criteria.
- Complete inventory run [40061383643](https://github.com/gamesbyian/general-purpose/actions/runs/40061383643): 3,062 files / 629 dirs, zero scanner errors or truncation, before the final empty-folder jobs.
- Guarded empty release folders: [40062058850](https://github.com/gamesbyian/general-purpose/actions/runs/40062058850) removed 31/31; [40064246299](https://github.com/gamesbyian/general-purpose/actions/runs/40064246299) removed 48/49, skipping one absent/case-conflicted `The Boys` release directory. 79 verified removals across those two jobs. Preserve the two rTorrent working directories. No later complete inventory was taken, so do not present the prior 629-dir total as current.

**Closure means the owner is satisfied with this pass**, not that every filename or unexplained archive is cleared. Keep outstanding *Night Court*, TNG cross-season, DS9 span and other explicit judgment calls as a deferred queue, unless future owner instructions override those holds.
