# Post-cleanup Plex triage, 2026-10-24

Source: latest **complete** read-only inventory, Actions [40061383643](https://github.com/gamesbyian/general-purpose/actions/runs/40061383643), artifact 12547826734; report branch `reports/ftp-media-inventory`. This triage is non-destructive and must not be treated as approval to rename media.

## Verified current snapshot

- 3,062 files, 629 directories; scanner reported zero failures and zero truncated directories.
- 2,058 videos examined by `plex-filename-audit.py`; 193 legacy `1x01` filename flags, 10 multi-episode flags, one cross-season episode flag, one airdate-after-episode flag, and one unrecognized season-container flag.
- The current move-manifest reconciliation reports **80/80 30 Rock Season 4–7 destinations present with expected sizes**.
- 31/31 empty-folder removals audited in [40062058850](https://github.com/gamesbyian/general-purpose/actions/runs/40062058850).
- Exact 49 additional empty-folder candidates (excluding two rTorrent working paths) approved by [#241](https://github.com/gamesbyian/general-purpose/pull/241); trusted deletion run [40064246299](https://github.com/gamesbyian/general-purpose/actions/runs/40064246299) was still in progress at checkpoint. Verify its `completed.json` journal; a successful job conclusion alone is insufficient.

## Outstanding decisions and safe sequence

1. **Verify #241 FTP journal** and update the actual removed/skipped paths. If every one of the 49 is removed, 80 of the original 82 empty locations are gone. Preserve both excluded rTorrent working paths. A new inventory is required to claim a current total.
2. **Night Court title normalization**: PRs [#163](https://github.com/gamesbyian/general-purpose/pull/163), [#164](https://github.com/gamesbyian/general-purpose/pull/164), and [#165](https://github.com/gamesbyian/general-purpose/pull/165) hold 57+66+70=193 legacy episode path corrections. Do not merge while transcription/editing workflows still reference AVI originals. First coordinate source-path cutover, then execute serialized guarded manifests and audit each.
3. **TNG cross-season** `S03E26S04E01`: keep the intact file as a special-case mapping; a single-season filename rewrite would obscure one episode. Any split requires separate verified lossless plan.
4. **Ten multi-episode files**: audit each exact episode span and existing naming before changing. Preserve distinct editions, subtitles and sidecars.
5. **Airdate / unrecognized season entry**: inspect the two exact audit rows and parent context before planning a rename. Do not infer year/title from numeric strings alone.
6. **PR #99**: non-destructive older Plex matching hints. Reconcile against latest inventory; stale suggestions must not be applied mechanically.
7. **Remaining archives and images**: keep 12 previously unmatched RAR-containing locations and 16 uncertain images until presence of extracted video or artwork role is positively established. No bulk wildcard cleanup.

## Workflow and isolation

Continue to use private main-only secret-bearing FTP workflows with exact source size/mtime preflight and per-file journals. PR checks are offline, the `/downloads` root stays mixed, and moving active seeding paths may affect torrent jobs. Avoid modifying the Night Court production pipeline or rTorrent working directories in the FTP cleanup lane. Full post-change read-only inventory is necessary before closure.

## Exact risk-flag disposition from full inventory

The full audit JSON on `reports/ftp-media-inventory` narrows the non-Night-Court flags substantially:

- **False-positive season-context risk:** `/downloads/star-trek-ds9-laserdisc-720p-24/Star Trek DS9 - Behind The Scenes - Laserdisc 720p30 hevc aac20.mkv` is explicitly labeled a behind-the-scenes extra. Its missing episode number is appropriate; preserve as an extra, not rename to a fabricated episode.
- **Date suffix:** `/downloads/Dateline NBC/Dateline.NBC.s33e34.2025.09.12.The.Night.of.the.Audition.1080p.WEB.h264-EDITH.mkv` appears to carry an airdate; retain unchanged pending authoritative schedule matching. Filename alone is not evidence of wrong episode identity.
- **Ten multi-episode flags:** seven have the standard span format `SxxEyy-Ezz` (30 Rock S07 finale, Green Lantern S01 premiere, Voyager S01 premiere, DS9 S07 finale, Enterprise S01 premiere, TNG S01 premiere and S07 finale); keep intact. Three additional `SxxEyyEzz` names are within the `star-trek-ds9-laserdisc-720p-24` alternate-edition folder, for DS9 S01E01-E02 `Emissary`, S04E01-E02 `The Way Of The Warrior`, and S07E25-E26 `What You Leave Behind`. Those three are **potential formatting-only Plex corrections**, not duplicate deletions or episode splits; require exact source size and timestamp plus sidecar/collision checks before any FTP rename.
- **Cross-season TNG S03E26S04E01** remains a hold: do not silently map away S04E01.

Risk flag count is not an actionable move count: at least eight are benign as-is; the three DS9 span-format candidates still require a reviewed transaction manifest.
