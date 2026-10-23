# Drop zone: original Night Court dialogue files

Upload episode SRT/VTT/TXT files to a private `research/night-court-dialogue-*` branch, together with matching `.meta.json` sidecar files. The GitHub Actions `Night Court dialogue witness ingestion` job organizes them into the matching episode directory, preserves original bytes and records the exact source/rights claim.

Example upload pair:
- `S04E15.DVD.en.srt`
- `S04E15.DVD.en.srt.meta.json`

The sidecar needs `episode` (S04E15), `edition`, `rights_basis`, `confirmed: true`, and ideally `language`, `source_name`, `complete`, and `notes`. See the full [step-by-step guide](../DIALOGUE-INGESTION.md).

This folder intentionally contains no episode text yet. The importer never downloads anything from an external subtitle site, and it never infers completeness from filename or timing.


## Faster bulk upload

A season or entire series of existing caption files can be uploaded as **one ZIP**, plus one sidecar `<archive-name>.zip.meta.json`. The files inside must include original-series SxxEyy identifiers. The workflow extracts subtitle or transcript members only, preserving a separate hash/source manifest for each episode. No per-episode sidecars needed for a batch. See [bulk ZIP guide](../DIALOGUE-INGESTION.md) for exact JSON and size limits.

Do not upload DVD images or full video files here. The local media extractor can generate SRTs privately first.
