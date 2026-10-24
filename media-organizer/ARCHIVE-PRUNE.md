# Archive extraction parity review and pruning

Full inventory found 23 RAR sets (736 parts) having a single matching
video in the same directory and total archive size within 13 KB of the
extracted video. Another 15 RAR-containing directories had no adjacent
video and are **not eligible** without further inspection.

The archive-specific mover supports exactly **one complete, contiguous
RAR/R00/R01... group per reviewed approval file**. It checks the specific
video path, file size, modification timestamp, all volume paths and
timestamps, presence of .rar and complete numbered sequence, common
volume stem, and total volume size within 0..1 MiB above extracted-video
size. During FTP preflight it confirms every volume and video still exist
and match, and rejects any additional matching volume omitted from the
manifest. It rechecks the video before every deletion, journaling partial
completion to the Actions artifact. Volume deletion itself is irreversible,
and may affect actively seeded torrents.

The initial approval manifest is **not included with the engine**.
To prune a complete set, create
`media-organizer/approved-archive-delete.json` in a standalone PR
reviewed against the current inventory. Only its merge to trusted main
triggers a privileged FTP deletion workflow. A PR never receives FTP
credentials. No archive deletion occurs because a similarly named film
exists elsewhere or because an archive is merely old.

The retained video isn't re-hashed against decompressed archive content:
this is an unusually strong but metadata-based extraction parity check.
If any evidence is uncertain, retain the archive.
