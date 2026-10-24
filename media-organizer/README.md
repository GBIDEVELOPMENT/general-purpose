> **Initial cleanup complete and owner-accepted (2026-10-24).** To repeat the process with a single prompt, use [ONE-PROMPT-MAINTENANCE.md](ONE-PROMPT-MAINTENANCE.md). Earlier sections describe the tooling; see the dated [status ledger](STATUS-2026-10-24.md) for audited outcomes and outstanding deferred decisions.

# Mixed-library FTP Downloads organizer

Scope: organize owner media already stored under the remote `/downloads` directory for Plex. **Movies and television stay together.** Series/franchise subfolders are welcome when positively identified, but the initial safe pass does not move files between directories.

## Current operating stages

1. The reviewed PR merges to trusted `main`. A `push` to `main` affecting this utility automatically triggers a **read-only FTP inventory**. PRs run offline tests only and receive no FTP secret.
2. The inventory uploads a restricted Actions artifact and commits JSON, 150-entry browsable file shards, suggestions and counts to the separately tracked private branch [reports/ftp-media-inventory](https://github.com/gamesbyian/general-purpose/tree/reports/ftp-media-inventory/media-organizer/output). **No media or credential is downloaded, logged or committed.** Filenames, directory paths and sizes are private metadata and remain only in this private repository.
3. Review actual names and sizes, identify series and films from authoritative metadata, group subtitle/sidecar companions, and establish collision-free planned destinations. Preserve all questionable names for manual review.
4. For a simple same-directory episode-token rename batch, commit `media-organizer/approved-plan.json` to trusted `main` with `root`, `moves` and per-source `size`, all selected from the current suggestions. No more than 500 reviewed moves per run.
5. Only a **manual** `workflow_dispatch` from **main** with `mode=apply` executes approved changes. Configure a required-reviewer GitHub environment named `ftp-media-changes` for a further approval gate. All attempted changes appear in a `completed.json` journal uploaded as a private Actions artifact. This workflow never deletes or overwrites media.

`mode=inventory` may also be manually dispatched from `main` to refresh the snapshot. It does not modify the FTP directory. It defaults to plaintext FTP for compatibility with the existing Night Court connection; FTPS is preferable if the server supports it.

## Limits and outstanding features

The planner normalizes conservative `S01E01` tokens to `Show - S01E01`, recognizes show-titled ancestor directories and common subtitle language tags. It flags movies, anomalous episode numbers, ambiguous titles, multi-episode packs and destination collisions. It **does not** yet implement authoritative metadata matching, film/franchise folder creation, multi-part files, duplicate analysis, comprehensive sidecar linking, undo, or moving unrelated extras. That work should be driven by the first real inventory, not guessed in advance.

Scanning has directory/file/depth caps and records incomplete subtrees. An incomplete scan is never considered safe for applying changes. It uses FTP MLSD and may need a verified compatibility fallback if the server doesn't support it. FTP RNFR/RNTO semantics vary; the executor rechecks the destination, validates source sizes and refuses unrecognized or stale suggested changes, but a remote file arriving between checks remains a race. Keep a backup before bulk execution.

The `reports/ftp-media-inventory` branch is intentionally not merged into main. The report branch is a private history of filenames and file sizes; retain it or delete it deliberately after the cleanup if appropriate.

## Operation

[Organizer workflow](https://github.com/gamesbyian/general-purpose/actions/workflows/ftp-media-organizer.yml) | [Existing Night Court FTP tooling](https://github.com/gamesbyian/general-purpose/blob/main/.github/workflows/night-court-ftp.yml)

The FTP secret is already referenced from GitHub Actions as `FTP_PASSWORD`. Do not print its value, store it in files, or expose it to PR builds. The Shaw mailbox bridge is entirely unrelated and must not be accessed.
