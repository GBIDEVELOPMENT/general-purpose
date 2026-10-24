# Cleanup of release debris

Owner requested deletion of `.nfo` files, screenshot directories and screenshot files,
and multipart archives **after extraction is confirmed**. The authoritative discovery
source is the current full inventory in private branch `reports/ftp-media-inventory`.

`delete_debris.py` creates separate queues:

* `.nfo`: eligible for exact-pinned deletion
* Images **inside named Screens/Screenshots directories** or with unambiguous
  screenshot basenames: eligible for exact-pinned deletion
* Artwork (poster, cover, fanart, title-card) and other ambiguous images: preserved
* Archive parts (RAR/Rxx etc.) with a video in the same directory: **review only**
* Archive parts without evidence of extracted media in the same directory: preserved

A same-directory video is not proof that an archive was extracted or is redundant.
Archive deletion must wait for extraction/matching evidence and a separate
archive-specific implementation. `.sfv` checksums and archives are not deleted
by this workflow.

For deletion, commit `media-organizer/approved-delete.json` with exact
`root`, `batch_id`, `description` and up to 80 `entries`. Each entry
pins absolute `from`, `size`, `modify`, and either `nfo` or
`screenshot` category. The PR is tested without secrets. Merge to main
triggers deletion under the `ftp-media-changes` environment. Preflight
checks all entries before deleting any and rechecks each file before DELE.
A completed file list is uploaded even on partial execution. No wildcard,
recursive remote deletion or directory removal is supported.

Be aware deleting files used by an active torrent can affect seeding.
This is a targeted cleanup of files the owner explicitly classified as unwanted.
