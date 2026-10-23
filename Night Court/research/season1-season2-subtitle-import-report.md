# Owner-supplied Seasons 1–2 subtitle import

Imported on 23 October 2026 into the private Night Court (1984–1992) research corpus.

Two owner-uploaded RAR packages were decompressed, CRC-checked, and moved into the research/source-archives directory. Their contents are preserved as individually versioned English SRT source witnesses within the 35 matching episode directories.

| Season | Episode coverage | Release label from filenames | Original archive |
|---|---:|---|---|
| S01 | S01E01–S01E13, 13 episodes | iNTERNAL.DVDRip.XviD-SPRiNTER | research/source-archives/night-court-first-season_english-365733.rar |
| S02 | S02E01–S02E22, 22 episodes | DVDRip.XviD-OSiTV | research/source-archives/night-court-second-season_english-365736.rar |

## Verified source outcomes

- 35 separately retained original SRT byte streams, representing every episode of Seasons 1 and 2.
- 12,995 timestamped caption cues and approximately 91,345 transcribed words.
- Exact source bytes, per-member original names, RAR CRC32, source and RAR SHA-256, language, edition labels, cue timing and episode identifiers are indexed.
- All 35 passed original source CRC32, SHA-256 and episode-identity integrity validation.
- S01E11 received the sole automated quality flag: repeated adjacent caption text. The other 34 tracks had no flags under current heuristics. None is certified complete.
- Independent audiovisual verification: 0/35. Timed source presence is not proof of no missing dialogue, specific video edition or correct captioned speaker identity.

Source-archive SHA-256:
- Season 1: e02c7c529662ff1e8354dcdc42393879c2535df10aecf7b5b5e7ce8f0e0bdc65
- Season 2: fecd355b278d4b6ce4a7c461f441403b73da82889833edaca98b93b7a19588d1

## Paths and catalogue

- catalog/rar-ingestion-manifest.json: RAR-to-episode-to-witness link with original filenames and per-member hashes
- catalog/dialogue-index.jsonl: source-version index including the 35 newly held files
- catalog/dialogue-coverage.json and dialogue-coverage.csv: which episodes physically hold source tracks
- catalog/dialogue-quality.json: source length, cue count, warning flags and timed coverage metrics
- seasons/S01/S01E03/episode.json: one example of an episode holding reference
- seasons/S01/S01E03/dialogue/versions/<edition-and-hash>/original.srt: original byte-exact source
- seasons/S01/S01E03/dialogue/versions/<edition-and-hash>/readable.txt, segments.jsonl, manifest.json and quality.json: matching derivatives and provenance

To search the held dialogue locally, run:
    python "Night Court/tools/search_dialogue.py" "judge" --source dialogue --season 1
    python "Night Court/tools/search_dialogue.py" "blizzard" --source dialogue --episode S02E10 --json

The release labels above come from filenames supplied with the archives; they are not independently verified claims about exact video masters. Prioritize spot-checking the S01E11 repeated-cue flag and selected episodes against a video source, then import Seasons 3–9 when source materials become available.

These subtitle bytes came from the owner's own repository upload, not automated scraping of a third-party transcript site. Any subsequent reuse or distribution needs a separate rights assessment.
