# FTP Downloads media organizer

Purpose: make the existing mixed `/downloads` directory easier for Plex without separating movies and shows. The owner permits series/franchise subfolders, but no automatic reclassification or deletion.

## Workflow

1. Merge the reviewed tooling PR.
2. Run **FTP media library organizer** from Actions with `mode=inventory` (the default). Download the artifact containing full paths, sizes, and conservative suggestions. The inventory is not committed to Git.
3. Inspect the inventory, identify ambiguous series/movie titles, then prepare `media-organizer/output/approved-plan.json` containing only explicitly reviewed exact moves with source size.
4. To execute, configure GitHub environment `ftp-media-changes` with required reviewer protection, then manually dispatch `mode=apply` from the trusted main branch. Review `completed.json` in the artifact. Do not approve apply with unreviewed candidates.

Existing Night Court and mail workflows remain untouched. Secrets must never appear in logs or PR artifacts. FTP is plaintext unless the server supports FTPS; prefer FTPS if it works.

Initial automation deliberately supports **same-directory renames only**. Later iterations can add folder creation, external film/TV identification, season folders, sidecar pairing and safe batched execution after real inventory is inspected. No automatic deletes, duplicate elimination, transcoding or content replacement. Keep originals when identification confidence is inadequate. If a rename is interrupted, consult the completed journal before retrying.

This is intentionally a conservative first pass: S01E01 tokens are normalized to `Show - S01E01`; movie-year matches and confusing titles go to review rather than being guessed. Plex detection also depends on library settings, agent, and directory structure.
