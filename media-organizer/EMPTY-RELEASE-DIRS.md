# Empty old release directory cleanup

The owner wants a clean mixed FTP /downloads tree. When Plex moves have finished,
some old release folders become empty. This utility ONLY removes exact approved
directory paths after FTP confirms they are presently empty.

The PR that creates or changes `media-organizer/approved-empty-release.json`
runs syntax and unit tests **without** FTP credentials. Merging its exact paths
to trusted main triggers the FTP job. No file deletion, recursion, wildcard
matching, shell execution on the server, or move operations exist in this tool.

Example manifest format:

```json
{
  "root": "/downloads",
  "batch_id": "release_dirs_001",
  "description": "Remove vacated named release folders after completed file-move journal verification",
  "directories": ["/downloads/An.Old.TV.Release.S01"]
}
```

The manifest is kept separate from the implementation PR.
Absolute paths must stay under /downloads and cannot refer to /downloads
itself. Directory removal is sorted deepest first, rechecks the literal
name without case ambiguities, then verifies the directory has zero children
immediately before FTP RMD. A directory still containing media, archive
parts, art, or even another subfolder is skipped and reported. Skipped paths
are expected and safe. Do not use this utility to remove a whole show
or franchise folder without checking the newest completed move journals.
