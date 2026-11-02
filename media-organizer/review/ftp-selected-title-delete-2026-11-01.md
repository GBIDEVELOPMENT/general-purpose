# FTP /downloads deletion review, 2026-11-01

**REVIEW ONLY. NOT AUTHORIZED TO DELETE. DO NOT MERGE THIS BRANCH TO MAIN AS A DELETION APPROVAL.**

Source: successful authenticated full read-only FTP inventory [GitHub Actions run 41375014383](https://github.com/GBIDEVELOPMENT/general-purpose/actions/runs/41375014383). Inventory errors 0; truncated directories 0.

**19 selected titles; 289 exact file paths; 463,387,620,682 bytes (463.39 GB, 431.56 GiB).**
Movies: 47 files, 80.15 GB. TV: 242 files, 383.24 GB.

The [complete JSON manifest](ftp-selected-title-delete-2026-11-01.json) enumerates all 289 paths, FTP sizes and modification times, and directory candidates. Nothing has been deleted, renamed or moved.

## Movies

| Title | Exact files | Reported size |
|:--|--:|--:|
| Black Bag (2025) | 1 | 10.59 GB |
| Bob Trevino Likes It (2025) | 1 | 1.58 GB |
| Cleaner (2025) | 5 | 1.93 GB |
| Dune (2021) | 1 | 10.24 GB |
| Dune: Part Two (2024) | 34 | 9.45 GB |
| Edge of Tomorrow (2014) | 1 | 9.56 GB |
| Southland Tales (2006) | 1 | 9.39 GB |
| Superman (2025) | 1 | 20.71 GB |
| The Life of Chuck (2024) | 1 | 1.58 GB |
| Wolfs (2024) | 1 | 5.14 GB |

## TV series

| Title | Exact files | Reported size |
|:--|--:|--:|
| Ice Pilots NWT | 1 | 3.27 GB |
| Invincible | 2 | 1.45 GB |
| Joey | 46 | 58.57 GB |
| Legion | 8 | 47.14 GB |
| Masters of the Air | 9 | 91.37 GB |
| Spider-Noir | 1 | 4.98 GB |
| Star Trek: The Next Generation | 172 | 174.18 GB |
| The Celebrity Traitors: Uncloaked | 1 | 0.24 GB |
| World War II with Tom Hanks | 2 | 2.02 GB |

## Non-destructive checks / required blockers

- All selected paths are unique and belong to the 19 matched title roots. There are no hidden files in those roots in the complete FTP inventory.
- `/downloads/rtorrent` and `/downloads/watch/rtorrent` show zero entries; neither is included. This **does not** prove that no active torrent seeds a selected title.
- `/downloads/Star Trek` contains 399 files, only 172 of which are the selected TNG series. Shared parent and all other Trek shows remain untouched.
- Known Night Court production files (193) are outside the selection and untouched. The historically flagged TNG cross-season file `S03E26S04E01` is absent from the current inventory; if it reappears, stop and assess its production dependency.
- `Dune: Part Two` includes 31 numbered RAR parts, `.rar`, `.sfv` and MKV. Thirty archive items report zero bytes; only `.r21`, `.r22` and `.r23` report 500,000,000 bytes each. Recheck live before deletion.
- Termalin returned **zero connected hosts**, so current rTorrent infohashes, seeding states and process-side file handles could not be verified. This is a **blocking unknown** for execution.
- Actual disk freed may differ from the sum of file sizes due to hard links or shared allocation.
- Before any deletion, require a separate explicit user confirmation, current per-file exact-path size/mtime preflight, live torrent/process dependency inspection, trusted execution boundary, durable journal and post-delete inventory. No wildcard or recursive delete.

No existing `approved-delete.json` manifest was changed. This entire review lives on the private branch `review/ftp-titles-2026-11-01`.
