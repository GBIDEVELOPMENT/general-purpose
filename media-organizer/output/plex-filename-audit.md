# Plex filename risk audit

Read-only filename heuristics. A flagged file is **not proven mislabeled**;
verify title, episode identity and codec with authoritative media data before moving.
No files were moved or deleted by this audit.

Inventory fully covered: **yes**.
Videos examined: **1577**.

## Counts by category

- **legacy_1x_episode**: 193
- **multiple_episodes**: 7
- **airdate_after_episode**: 1
- **episode_unrecognized_in_season**: 1

## Highest-risk examples

- **high / legacy_1x_episode**: `/downloads/Night Court TVRip S1-S9/Night.Court.S01.DVDRip.DivX/Night Court - 1x01 - All You Need Is Love.avi`. TV episode code uses 1x01 instead of S01E01
- **high / legacy_1x_episode**: `/downloads/Night Court TVRip S1-S9/Night.Court.S01.DVDRip.DivX/Night Court - 1x02 - Santa Goes Downtown.avi`. TV episode code uses 1x01 instead of S01E01
- **high / legacy_1x_episode**: `/downloads/Night Court TVRip S1-S9/Night.Court.S01.DVDRip.DivX/Night Court - 1x03 - The Former Harry Stone.avi`. TV episode code uses 1x01 instead of S01E01
- **high / legacy_1x_episode**: `/downloads/Night Court TVRip S1-S9/Night.Court.S01.DVDRip.DivX/Night Court - 1x04 - Welcome Back, Momma.avi`. TV episode code uses 1x01 instead of S01E01
- **high / legacy_1x_episode**: `/downloads/Night Court TVRip S1-S9/Night.Court.S01.DVDRip.DivX/Night Court - 1x05 - The Eye of the Beholder.avi`. TV episode code uses 1x01 instead of S01E01
- **high / legacy_1x_episode**: `/downloads/Night Court TVRip S1-S9/Night.Court.S01.DVDRip.DivX/Night Court - 1x06 - Death Threat.avi`. TV episode code uses 1x01 instead of S01E01
- **high / legacy_1x_episode**: `/downloads/Night Court TVRip S1-S9/Night.Court.S01.DVDRip.DivX/Night Court - 1x07 - Once in Love With Harry.avi`. TV episode code uses 1x01 instead of S01E01
- **high / legacy_1x_episode**: `/downloads/Night Court TVRip S1-S9/Night.Court.S01.DVDRip.DivX/Night Court - 1x08 - Quadrangle of Love.avi`. TV episode code uses 1x01 instead of S01E01
- **high / legacy_1x_episode**: `/downloads/Night Court TVRip S1-S9/Night.Court.S01.DVDRip.DivX/Night Court - 1x09 - Wonder Drugs.avi`. TV episode code uses 1x01 instead of S01E01
- **high / legacy_1x_episode**: `/downloads/Night Court TVRip S1-S9/Night.Court.S01.DVDRip.DivX/Night Court - 1x10 - Some Like It Hot.avi`. TV episode code uses 1x01 instead of S01E01
- **high / legacy_1x_episode**: `/downloads/Night Court TVRip S1-S9/Night.Court.S01.DVDRip.DivX/Night Court - 1x11 - Harry and the Rock Star.avi`. TV episode code uses 1x01 instead of S01E01
- **high / legacy_1x_episode**: `/downloads/Night Court TVRip S1-S9/Night.Court.S01.DVDRip.DivX/Night Court - 1x12 - Bull's Baby.avi`. TV episode code uses 1x01 instead of S01E01

## Known constraints

- This library deliberately mixes movies and TV shows at /downloads, which Plex warns may cause mismatching.
- Codec strings in filenames are claims by uploaders; they do not establish actual stream codec or resolution.
- Multi-edition episodes and subtitles require coordinated moves, never deduplication by episode code.
- No recommendation here authorizes automatic deletion or renaming.

