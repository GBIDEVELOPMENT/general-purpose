# Plex filename risk audit

Read-only filename heuristics. A flagged file is **not proven mislabeled**;
verify title, episode identity and codec with authoritative media data before moving.
No files were moved or deleted by this audit.

Inventory fully covered: **no; scan was truncated or failed**.
Videos examined: **1381**.

## Counts by category

- **year_after_episode_code**: 30
- **multiple_episodes**: 8
- **movie_year_only_in_folder**: 3
- **sample_or_proof_video**: 3
- **cross_season_episode**: 1
- **episode_unrecognized_in_season**: 1

## Highest-risk examples

- **high / cross_season_episode**: `/downloads/Star Trek TNG Complete HEVC D3FiL3R/Star Trek TNG S03 HEVC D3FiL3R w-s/Star.Trek.The.Next.Generation.S03E26S04E01.BluRay.1080p.HEVC.DD5.1-D3FiL3R.mkv`. File spans two seasons; do not lose second episode code
- **high / sample_or_proof_video**: `/downloads/A.Big.Bold.Beautiful.Journey.2025.Hybrid.2160p.WEB-DL.DV.HDR.DDP5.1.Atmos.H265-AOC/Sample.mkv`. Non-feature media can be falsely matched as a film or episode
- **high / sample_or_proof_video**: `/downloads/Michael.2026.2160p.WEB-DL.DDP5.1.Atmos.SDR.H265-AOC/Sample.mkv`. Non-feature media can be falsely matched as a film or episode
- **high / sample_or_proof_video**: `/downloads/Southland.Tales.2006.1080p.Bluray.x264-SECTOR7/Sample/sector7-southland.tales.1080p-sample.mkv`. Non-feature media can be falsely matched as a film or episode
- **medium / episode_unrecognized_in_season**: `/downloads/star-trek-ds9-laserdisc-720p-24/Star Trek DS9 - Behind The Scenes - Laserdisc 720p30 hevc aac20.mkv`. TV season container but media name lacks standard SxxEyy identification
- **medium / movie_year_only_in_folder**: `/downloads/A.Big.Bold.Beautiful.Journey.2025.Hybrid.2160p.WEB-DL.DV.HDR.DDP5.1.Atmos.H265-AOC/Sample.mkv`. Likely film lacks title/year in its own basename; review with Plex film rules
- **medium / movie_year_only_in_folder**: `/downloads/Michael.2026.2160p.WEB-DL.DDP5.1.Atmos.SDR.H265-AOC/Sample.mkv`. Likely film lacks title/year in its own basename; review with Plex film rules
- **medium / movie_year_only_in_folder**: `/downloads/Southland.Tales.2006.1080p.Bluray.x264-SECTOR7/sector7-southland.tales.1080p-x264.mkv`. Likely film lacks title/year in its own basename; review with Plex film rules
- **medium / year_after_episode_code**: `/downloads/Bridgerton S04 2026 1080p NF WEB-DL DDP5 1 Atmos H 264-HDSWEB/Bridgerton.S04E01.2026.1080p.NF.WEB-DL.DDP5.1.Atmos.H.264-HDSWEB.mkv`. Year after episode marker may be an airing/release year, not show premiere year
- **medium / year_after_episode_code**: `/downloads/Bridgerton S04 2026 1080p NF WEB-DL DDP5 1 Atmos H 264-HDSWEB/Bridgerton.S04E02.2026.1080p.NF.WEB-DL.DDP5.1.Atmos.H.264-HDSWEB.mkv`. Year after episode marker may be an airing/release year, not show premiere year
- **medium / year_after_episode_code**: `/downloads/Bridgerton S04 2026 1080p NF WEB-DL DDP5 1 Atmos H 264-HDSWEB/Bridgerton.S04E03.2026.1080p.NF.WEB-DL.DDP5.1.Atmos.H.264-HDSWEB.mkv`. Year after episode marker may be an airing/release year, not show premiere year
- **medium / year_after_episode_code**: `/downloads/Bridgerton S04 2026 1080p NF WEB-DL DDP5 1 Atmos H 264-HDSWEB/Bridgerton.S04E04.2026.1080p.NF.WEB-DL.DDP5.1.Atmos.H.264-HDSWEB.mkv`. Year after episode marker may be an airing/release year, not show premiere year

## Known constraints

- This library deliberately mixes movies and TV shows at /downloads, which Plex warns may cause mismatching.
- Codec strings in filenames are claims by uploaders; they do not establish actual stream codec or resolution.
- Multi-edition episodes and subtitles require coordinated moves, never deduplication by episode code.
- No recommendation here authorizes automatic deletion or renaming.

