# Complete-dialogue ingestion for the original Night Court (1984–1992)

This is the **source-preserving local ingestion lane** for episode transcripts and timed captions. It does not fetch scripts from external websites, defeat DRM, or declare that any particular copy is legally authorized. It can process full versions the user supplies for a private research corpus, keeping each witness and its original bytes intact.

## How to add a caption track from your phone via GitHub

1. Open the private repository's `Night Court/incoming/` folder on the research branch `research/night-court-dialogue-ingestion`. Upload an SRT, VTT or TXT whose filename contains the original episode identifier, e.g. `S01E01.personal.dvd.en.srt`.
2. Next to the file, upload a small UTF-8 sidecar named **exactly** `S01E01.personal.dvd.en.srt.meta.json`:

```json
{
  "episode": "S01E01",
  "edition": "dvd-english-v1",
  "language": "en",
  "rights_basis": "lawfully_obtained_research_copy",
  "confirmed": true,
  "complete": true,
  "source_name": "Original DVD closed captions",
  "source_url": null,
  "notes": "Personal research transcript from a lawfully accessible source; no DRM bypass"
}
```

3. GitHub Actions runs `Night Court dialogue witness ingestion` on pushes to that branch or by manually starting `workflow_dispatch`. It parses the file, preserves the exact bytes, emits searchable segment/paragraph JSONL, creates a readable transcript, updates the episode holding record and commits the result to that **research branch**. Review it and merge via PR. If you upload to `main` directly, the automatic ingestion workflow does not run.

If you don't have an input file yet, the workflow and repo remain in their zero-dialogue state. The sidecar `confirmed` records the submitter's source/rights declaration, not an independent legal judgment.

## Local command (works on Android Termux, desktop, Codespaces)

```sh
python "Night Court/tools/import_dialogue.py" \
  --file "/path/to/Night.Court.S01E01.en.srt" \
  --episode S01E01 \
  --edition "DVD English closed captions" \
  --language en \
  --rights-basis lawfully_obtained_research_copy \
  --confirm-rights \
  --complete
```

Or with sidecar files:

```sh
python "Night Court/tools/import_dialogue.py" --inbox "Night Court/incoming"
python "Night Court/tools/validate_dialogue.py"
python "Night Court/tools/audit_holdings.py"
```

Optional local **generation** from video/audio legitimately available to you: audio transcription tools such as Whisper can generate SRT locally, without sending the original media to GitHub. For text subtitle streams in a DRM-free local media container, `ffmpeg -i local-recording.mkv` can list available subtitle streams, and `ffmpeg -i local-recording.mkv -map 0:s:0 -c:s srt S01E01.local.en.srt` can export compatible text subtitles. Image-based subtitle streams may require a separate transcription process; don't treat failed conversion as missing dialogue. These examples do not authorize circumvention of technical access controls or acquisition from unauthorized sources.

## Per-version outputs

```text
Night Court/seasons/S01/S01E01/
  episode.json
  dialogue/versions/
    dvd-english-v1--<sha256-prefix>/
      original.srt         # byte-for-byte source witness
      segments.jsonl       # lossless cue text and millisecond timestamps
      readable.txt         # normalization for retrieval
      manifest.json        # edition, rights declaration, hash, language, completeness
Night Court/catalog/dialogue-index.jsonl
```

SRT and VTT carry millisecond timing where present; TXT is imported as paragraphs without invented timing. Cue numbering is normalized, while original source bytes remain unchanged. Speaker identification, OCR accuracy, censorship edits, dialogue omissions and edition provenance cannot be established from file format alone.

Multiple source editions are preserved independently. A second version with a different hash or edition label never overwrites the first. The same version and bytes are idempotent. A same-version content collision raises an error. `declared_complete` records the submitter's statement; even a full-duration subtitle file can omit silence, lyrics, laughter or entire lines, so **episode-complete dialogue remains unverified pending audiovisual QA**.

## Quality criteria for future canonical synthesis

- Keep source caption cues, stage directions, sound effects, music notation, laughter and bracketed commentary distinguishable from spoken dialogue.
- Assign each transcript a video release identity and language, with time offset, caption revision and source URL where known.
- Measure temporal coverage against actual episode runtime before claiming completeness. Coverage cannot be inferred from an SRT's final timestamp alone.
- Collate versions with alignment, character turn parsing, diarization and lexical differences; never flatten alternate edits.
- Check episode/season numbering on the 1984 original, especially where same-name 2023 revival subtitle files exist. Filename alone is not proof of show identity.
- For complete legal analyses, determine separately which copying/research/format-shifting exceptions and platform rules apply to the actual source.
- Source byte hashes are provenance and integrity, not a claim that a subtitle supplier created all underlying dialogue.

## Engineering contract

The importer performs **zero network retrieval**. It supports UTF-8 (with BOM), UTF-16 and Windows-1252, caps input at 20 MB, rejects episodes outside all 193 original episode IDs, and requires an explicit rights declaration and acknowledgment. Input never becomes production code or executable instructions. A separate offline test file creates synthetic episodes and synthetic dialogue only. GitHub Actions passes `validate.py`, `test_import_dialogue.py`, `validate_dialogue.py` and `audit_holdings.py`; the user-provided actual source files are not supplied as test fixtures.

This is a practical ingest lane, not a judgment about fair dealing or fair use. In Canada, Copyright Act sections 29 (research/private study) and 29.22 (conditional reproduction for private purposes) are relevant, subject to individual circumstances and no DRM circumvention. The U.S. four-factor fair-use test considers transformative research purposes and amount copied. Private storage and noncommercial intent are relevant facts, not universal exemptions.


## Search imported dialogue alongside episode synopses

The `tools/search_dialogue.py` CLI searches physically stored caption/transcript cues and the separately licensed encyclopedia synopsis index without blurring their evidence status:

```bash
python "Night Court/tools/search_dialogue.py" "Harry" --source both --limit 10
python "Night Court/tools/search_dialogue.py" "court" --source capsules --season 1
python "Night Court/tools/search_dialogue.py" "magic" --source dialogue --episode S01E01 --json
python "Night Court/tools/search_dialogue.py" "hello" --source dialogue --language en --timecoded
```

With no imported dialogue, `--source dialogue` returns zero hits. The default `--source both` can still return licensed synopsis matches for all 193 episodes. A zero-result search is **not** evidence that the phrase never occurred onscreen. JSON results carry episode ID, edition, language, source SHA, cue number/timestamps, exact local manifest path and optional **explicitly labeled** speaker field. Unlabeled captions do not receive guessed characters.

## Import QC and gaps requiring review

After import, `tools/audit_dialogue_quality.py` creates a per-version `quality.json`, plus `catalog/dialogue-quality.json` and CSV. It calculates approximate word count, timing span, source caption time union, overlaps, cue ordering, duplicated adjacent text, substantial gaps, and suspiciously short caption timelines.

```bash
python "Night Court/tools/audit_dialogue_quality.py"
python "Night Court/tools/test_dialogue_quality_search.py"
```

The metrics are deliberately **diagnostics only**. Genuine episode captions can have large quiet stretches, opening credits, commercials, music, overlapping speakers or late start times. The tool never treats an unflagged track as complete, and never treats a flagged track as confirmed incomplete. `quality.json` is tied to the source SHA and immutable version manifest.

The GitHub upload workflow now performs synthetic QC/search tests, regenerates reports, and smoke-tests caption/synopsis lookup on every research dialogue branch upload.


## New: Extract transcripts directly from local episode media

`tools/extract_local_media.py` makes the ingestion pipeline usable with **a local, lawfully accessible, DRM-free copy of an episode**. It reads local media containers with `ffprobe`, selects actual text subtitle streams by codec/language, converts those streams to SRT with `ffmpeg`, then feeds the resulting full timed text into the existing source-preserving importer. Source video/audio stays on your machine; only the extracted subtitle text goes to the repository when you commit the result.

Inspect first, without copying anything:

```sh
python "Night Court/tools/extract_local_media.py" \
  --media "/path/to/Night.Court.S01E01.mkv" --dry-run
```

Extract available English text subtitles into S01E01's versioned source holdings:

```sh
python "Night Court/tools/extract_local_media.py" \
  --media "/path/to/Night.Court.S01E01.mkv" \
  --episode S01E01 --edition "Owned DVD edition" --language en \
  --rights-basis lawfully_obtained_research_copy \
  --confirm-rights --confirm-original-series
```

Batch-process a folder of **original-series** episodes whose filenames include `SxxEyy` identifiers:

```sh
python "Night Court/tools/extract_local_media.py" \
  --directory "/path/to/NightCourt1984" --edition "Owned DVD box set" \
  --rights-basis lawfully_obtained_research_copy \
  --confirm-rights --confirm-original-series
```

Use `--all-text-tracks` to preserve every decodable text subtitle variant as a distinct witness. By default the importer chooses a matching English stream, favoring the default stream; `--track-index N` selects an explicit `ffprobe` stream index. It deliberately rejects image-based PGS/VobSub tracks rather than pretending to parse their content. Note that some DVD closed captions are embedded as analog/digital video-caption data, not separate text streams. In those cases the text-subtitle extraction path may find nothing. This is not proof that the recording lacks captions.

### Offline speech-to-text fallback

For audio/video with no usable subtitle text track, there is an **opt-in** local faster-whisper route:

```sh
python -m pip install faster-whisper
python "Night Court/tools/extract_local_media.py" \
  --media "/path/to/Night.Court.S01E01.mkv" \
  --episode S01E01 --mode asr --model "/local/models/faster-whisper-base" \
  --edition "Personally generated ASR v1" \
  --rights-basis lawfully_obtained_research_copy \
  --confirm-rights --confirm-original-series
```

Whisper's speech recognition runs on your machine. By default the command refuses model weight downloads and expects an already cached local model; the explicit `--allow-model-download` flag enables model retrieval. A capable CPU or GPU and enough local storage are needed for reasonable performance. The result receives a separate edition label; do not confuse auto-transcription with a verified closed-caption file. Speech recognition can miss music, crosstalk, names, nonverbal comedy, or invent words, so independent spot checking remains essential.

**Extraction reliability:** The extractor normalizes common FFmpeg language tags (for example `eng`→`en`, `fra`/`fre`→`fr`) when matching `--language`. Folder-level `--dry-run` can inspect media even without an `SxxEyy` filename, because it makes no claim about episode assignment. Local automatic speech recognition always records `complete: false` even when the caller supplies `--complete`: model output is not independently complete by virtue of reaching the end of a recording. The ingestion workflow installs `ffmpeg` if absent in order to perform a real synthetic-container round-trip test instead of silently skipping it.

Both routes reuse the same `dialogue/versions/` archive, source declarations, hash verification, query index and quality diagnostics. The original episode video or audio is **never committed** by these tools. Media must not be DRM-protected; these tools do not remove access controls or acquire third-party episode files. Synthetic four-second MKV extraction is tested by a dedicated narrow GitHub Actions workflow; no copyrighted episode is used as a fixture.


## Bulk-import an entire season or series from one ZIP

You no longer need to upload a separate rights declaration for each individual caption file. A ZIP can contain up to **500** SRT, VTT or TXT tracks with SxxEyy somewhere in each member's filename. All members are assigned to the correct original-series episode based on the filename, preserving their source bytes, cue timing, source ZIP SHA and per-file CRC. Individual editions remain separately versioned.

Upload just **two files** to the private `Night Court/incoming/` directory on a research dialogue branch:

- `NightCourtOriginal-Season1.zip`, containing `S01E01.eng.srt`, `S01E02.eng.srt`, etc.
- `NightCourtOriginal-Season1.zip.meta.json`, with one package-level source/rights declaration:

```json
{
  "edition": "Original series DVD English captions",
  "language": "en",
  "rights_basis": "lawfully_obtained_research_copy",
  "confirmed": true,
  "complete": false,
  "source_name": "Original Night Court season 1, privately acquired caption package",
  "notes": "Personal research source. Individual track completeness not yet checked."
}
```

`complete: true` is allowed when you believe the files cover full episodes, but it **never** implies independently AV-verified completeness. For language/edition exceptions, the optional `overrides` dictionary maps exact ZIP member names to `language`, `edition`, `complete` or `notes` overrides.

The existing GitHub Actions importer now detects ZIPs before processing any standalone source files. It does **not** follow ZIP symlinks or archive paths, and rejects traversal paths, excessive file sizes, suspected decompression bombs and malformed original-series episode identifiers. It never executes archive content.

For local import:

```sh
python "Night Court/tools/import_dialogue_bundle.py" \
  --bundle "/path/to/NightCourtOriginal-Season1.zip" \
  --metadata "/path/to/NightCourtOriginal-Season1.zip.meta.json"
python "Night Court/tools/validate_dialogue.py"
python "Night Court/tools/audit_dialogue_quality.py"
```

A safe preflight (only lists episode identities, no ingest) is available with `--dry-run`. Use `--inbox "Night Court/incoming"` for multiple ZIPs, with each ZIP's corresponding `.meta.json` sidecar. Uploaded ZIPs remain in the private incoming directory until you intentionally remove them; the original individual files are also preserved under each episode's version directory. Keep archives under 90 MB each. The workflow doesn't acquire, redistribute, transcribe or scrape TV episodes by itself.


## Reconcile alternate dialogue versions without selecting a canonical text

`tools/compare_dialogue_versions.py` reads only **physically held** caption and transcript witnesses. When an episode has two or more sources, it picks the version with the most tokenized text as a **comparison anchor, not a canonical transcript**, and aligns every other version against it. It reports normalized exact duplicates, near-equal wording, likely excerpt/subset overlap and substantial differences.

```sh
python "Night Court/tools/compare_dialogue_versions.py"
```

Outputs include `catalog/dialogue-variant-comparison.json` and an episode-specific `dialogue/variant-comparison.json` for episodes with multiple held sources. Every comparison preserves each source version ID, source SHA, word count, limited word differences and explicit caveats. When identical long normalized content appears assigned to two different episode IDs, a cross-episode misidentification flag is raised.

Audio captions, inserted sound effects and character labels can affect wording comparison; the alignment removes basic markup and brackets for approximate matching only. Full original sources remain untouched. For performance, comparisons use at most the first 15,000 normalized words per witness. No comparison score alone certifies accuracy, edition alignment, or completeness.
