# Non-destructive Plex match hints

Plex supports `.plexmatch` files with `Title`, `Year`, `Season`,
and exact `ep: S01E01: filename.ext` directives. These can improve
matching without renaming any media or breaking paths used by a torrent
client. Official documentation:
https://support.plex.tv/articles/plexmatch/

`plexmatch/approved.json` identifies the exact folder, source video
filenames, sizes, FTP modification timestamps, show, year and season. The
trusted-main-only workflow checks that every original is still present
and unchanged. It refuses to overwrite an existing `.plexmatch`. It
uploads the small text file and then downloads that text only to verify
exact readback; it never retrieves video contents.

First real batch: all 22 `Studio 60 on the Sunset Strip` season-one AVI
files under the original DVDRip folder. This is deliberately isolated
from the separate `/downloads/S60` project tree and its tools.

To update a hint later, use a separate explicit reconciliation process.
Do not silently replace an existing manual `.plexmatch`. Do not infer
episode numbering solely from alphabetical sort when files are special,
multi-episode, or re-cut editions. All user media remains where it is.
