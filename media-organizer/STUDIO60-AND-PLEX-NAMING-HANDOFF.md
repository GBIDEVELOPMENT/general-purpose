# Studio 60 and Plex filename review

Reviewed 2026-10-24 against the read-only `reports/ftp-media-inventory` catalogue
and independently audited move journals. This is a mixed `/downloads` FTP
library by owner preference; **do not** create separate Movies/TV roots.

## Studio 60 on the Sunset Strip (2006)

The inventory has 22 episodes in **each of four distinct versions**:

| Version | Original source | Destination for every episode |
|---|---|---|
| 1080p MP4 | `/downloads/S60/1080p` | `/downloads/Studio 60 on the Sunset Strip (2006)/Season 01`, suffix `- 1080p.mp4` |
| 720p MP4 | `/downloads/S60/720p` | Same season, suffix `- 720p.mp4` |
| XviD DVDRip AVI | `/downloads/Studio 60 on the Sunset Strip/Season 01` | Same season, suffix `- XviD DVDRip.avi` |
| DVD AVI + VobSub `.idx/.sub` | `/downloads/S60/DVD` | Same season, suffix `- DVD.avi/.idx/.sub` |

The exact episode titles come from the DVD directory's 22 named episode files,
not automatic media inference. PR #157 moved the first 66 regular episode files,
and its audit `studio60_editions_066` recorded **66/66 complete**.

PR #158 is the **sequential DVD batch**. It contains 22 main AVI files and all
44 matching `.idx` and `.sub` files, plus **three commentary files and three
documentary files**:

- Pilot commentary audio version `/Other/Pilot commentary audio track.avi/.idx/.sub`,
  to distinguish it from regular episode playback
- Making-of documentary `/Featurettes/Making of Studio 60 on the Sunset Strip.avi/.idx/.sub`,
  to identify it as a show extra rather than a film or ordinary episode

Do not delete any of these versions as duplicates. The DVD cover photograph is
preserved as artwork pending optional poster integration. The separately named
pilot screenshot JPEG was included in owner-authorized residual debris PR #168.
Release readme `.txt` files were left unchanged.

Plex may group different encodes of a common episode as playback versions rather
than displaying four independent episode entries; app control over which one
plays is not guaranteed. **The encoded media and all original alternative versions
remain on FTP**. Plex's TV naming guide recommends a year-qualified show folder,
`Season 01`, and `S01E01` style names.

## Other high-priority filename findings

1. **Original Night Court (1984)**: 193 DVDRip AVI files in nine directories
   use legacy `1x01` through `9x22` notation. They are TV episodes, not films.
   Exact SxxEyy correction plans in PRs #163–#165 are **held from FTP merge**
   until active Night Court speech/transcription agents no longer rely on old
   source paths. Episode count: S01 13; S02–S06 22 each; S07/S08 24 each; S09 22.
2. **TNG cross-season video**: `Star.Trek.The.Next.Generation.S03E26S04E01`
   represents both the Season 3 finale and Season 4 premiere. Preserve it
   rather than silently relabeling it `S03E26`. It requires deliberate
   multi-season Plex handling or a safe lossless split.
3. **DVD disc identifiers** such as `The.Durrells.S01D01` are not
   `S01E01` episode identifiers. Treat these as DVD/disc sets, never infer
   an episode from a disc number without inspecting its contents.
4. **Misplaced years and release labels**: e.g.
   `Bridgerton.S04E01.2026.1080p...`,
   `Queen.Charlotte...S01E01.2023.1080p...`,
   `Bait.2026.S01E02...`. The year may be a *broadcast* or download year,
   not the **premiere** year Plex uses to disambiguate shows.
   `Dateline.NBC.s33e34.2025.09.12...` is plausibly an *airdate* and
   should not have its date stripped without verifying programme metadata.
5. **Release descriptors and codec text** such as `H.264`, `H 265`,
   `HEVC`, `DV`, `HDR`, group suffix `-ETHEL`, `-LAMA`,
   and `PROPER` are filename claims, not independently verified streams.
   Prefer show/episode or movie title/year *before* those tokens.
6. **Samples and proof clips** such as `Sample.mkv` within film release
   folders can be mistaken for feature films. Do not rename or discard them
   automatically without confirming what content they represent.
7. **Library layout limit**: Plex explicitly recommends separate movie and
   TV library roots. We respect the user's single mixed FTP /downloads
   requirement, but cannot guarantee that even perfectly named files will
   always match if Plex is configured to scan the whole mixed root as one
   library.

The filename auditor in PR #160 automatically publishes a **read-only**
`plex-filename-audit.json` and Markdown triage alongside future inventory
snapshots. Its severity levels are conservative review categories,
**not** authorization for destructive rename/delete operations.

## References

- https://support.plex.tv/articles/naming-and-organizing-your-tv-show-files/
- https://support.plex.tv/articles/multiple-editions-tv-shows/
- https://support.plex.tv/articles/local-files-for-tv-show-trailers-and-extras/
- https://support.plex.tv/articles/naming-and-organizing-your-movie-media-files/
