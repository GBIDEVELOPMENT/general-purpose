# Night Court audiovisual script-generation factory

## First real source-audio checkpoint: 23 October 2026

The trusted-base, owner-PR-triggered [S01E01 acoustic run #40042590948](https://github.com/gamesbyian/general-purpose/actions/runs/40042590948) **succeeded**. Source AVI SHA-256 and stream/runtime metadata, plus 15 seconds of mixed-audio RMS/peak/activity diagnostics, are retained as compact, private [pilot evidence](research/s01e01-real-ftp-acoustic-pilot.json). The FTP-to-ephemeral-runner-to-FFmpeg pipeline is now empirically proven with one real source. No voice identity, ASR, pitch, emotional delivery or visual-stage annotations were yet inferred, and the source remains not AV-verified.

Next implementation should extract test-aligned candidate caption timings using this cut, and only then run richer voice/video tools. Keep the same bounded PR-triggered trusted-base pattern and store only verified small derived evidence, not raw media.

## Confirmed source-video inventory checkpoint: October 23, 2026

The owner ran the existing FTP metadata workflow successfully ([run #40041061527](https://github.com/gamesbyian/general-purpose/actions/runs/40041061527)). Its 193 AVI files were all unrecognized initially because filenames use `1x01` notation. The reconciled [193-file inventory](catalog/ftp-video-inventory-2026-10-23.json) maps all expected episode IDs one-to-one. The exact S01E01 183,386,112-byte AVI file is identified by filename and path; source identity, duration, streams and content remain **unverified until audiovisual processing**. Do not re-run the network inventory solely to fix filenames.

## Implementation checkpoint: October 23, 2026

The original 1984–1992 Night Court corpus **now holds 193/193 episode dialogue witnesses**, comprising **192 timed SRT sources and S09E19 untimed source-page text**. Historical 35-track and 158-missing counts elsewhere in this document describe its initial drafting state and must not be used as current prerequisites.

Vocal acoustic measurement and optional eGeMAPS/YIN tooling are merged in PRs #85–86 with successful synthetic CI. A new bounded **S01E01 local-video pilot** is being implemented in PR #87; see [S01E01-AV-PILOT-HANDOFF.md](S01E01-AV-PILOT-HANDOFF.md). It extracts at most 30 seconds of owner-confirmed local media audio, fingerprints input, and stores only a measurement manifest. **It has not yet analyzed real Night Court audio, performed ASR/diarization, verified captions against an episode cut, or reconstructed visual scenes.** The existing manual FTP metadata workflow is still the appropriate next step for identifying media candidates before any remote audiovisual processing. Do not confuse synthetic FFmpeg acceptance with real-episode acceptance.


Status: engineering proposal, October 23, 2026. **No new video or audio files transferred.** The original 1984–1992 series has 193 episodes. 35 owner-provided S01/S02 SRT witnesses are already archived; do not re-import the original two RARs.

## Confirmed inputs and infrastructure

- Actual remote original-series TVRip root: `/downloads/Night Court TVRip S1-S9` on the owner's Seedhost FTP account, discovered by the existing authenticated FTP inventory. Filename-level media inventory has **not yet been dispatched successfully**: workflow run #40029419991 passed only the offline job; the network inventory job was skipped on a push event.
- Dedicated metadata-only workflow: `.github/workflows/night-court-ftp-video-metadata.yml`. Its owner-authorized manual workflow_dispatch runs `Night Court/tools/ftp_video_metadata.py` using the repository's already-configured FTP_PASSWORD. No credentials should be copied, displayed or transferred to another repo.
- Existing `tools/extract_local_media.py` converts suitable existing text subtitle streams or runs optional locally installed faster-whisper; `tools/import_dialogue.py`, `import_dialogue_bundle.py`, `validate_dialogue.py`, `audit_dialogue_quality.py`, `compare_dialogue_versions.py` and source-grounded speaker/turn tools consume text witnesses.
- Uniracers' existing Drive workflow `gamesbyian/UR-Recomp/.github/workflows/vault-direct-intake.yml` uses pinned `gdown==6.4.2` to **download from a public Drive folder** with explicit source-review gates. It is **not a Drive uploader**, should not be copied verbatim into Night Court, and does not confer access to private Drive storage. Preserve each repo's secret boundaries.
- Connected Google Drive can be useful for owner-managed deliverables, but this repository has no verified automatic upload authorization yet. Do not claim a Google Drive staging path has been created until the writer's credentials and upload operations are tested.

## Recommended architecture: keep source files at Seedhost, ship tiny forensic witnesses

A full episode video need never enter GitHub or ChatGPT Drive. For each verified original-series episode, use a bounded worker to access a local/remote-mounted video copy, run ffprobe, extract audio, sample sparse visual frames, transcribe speech, and create a provenance-rich episode bundle. Store the large binary witness files in **a dedicated `Night Court Script Factory/` directory on the existing FTP service** first: this avoids an extra FTP-to-GitHub-to-Drive move and uses the system already holding the video. Put durable, compact JSON/SRT/CSV/Markdown and hashes in the private GitHub corpus. Google Drive is a secondary user-facing mirror after an authorized upload mechanism has been validated.

**Preferred audio**: mono 16 kHz lossless FLAC, 16-bit, from the original soundtrack; usually about 8–20 MB per ~22-minute episode (actual sizes vary). This is a strong ASR/diarization input. If the model accepts native stereo/high-rate audio or the original has important channel differences, preserve an optional stereo FLAC at 48 kHz as a separate source witness. Do not discard the original soundtrack upstream. Optional lightweight listening/proof copy: mono Opus at roughly 40–64 kbps, often 3–6 MB per episode. Never use the Opus derivative as the *sole* authoritative input for final dialogue attribution.

**Preferred visual evidence**: do not default to a continuous 4-fps video for *all* 193 episodes. At 22 minutes it produces ~5,280 frames per episode, ~1.02 million across the series. Even when compressed, that can be much larger and costlier than necessary, and frame-rate sampling alone misses fast cuts and exact character utterance times. Better to generate:
1. **0.5–1 fps low-resolution reference frames** (for example 384–512 px wide) with shot-boundary keyframes; use 0.5 fps as a starting archival preview.
2. **A shot-change/contact sheet index** using FFmpeg scene scoring. Treat detection thresholds as tunable; lots of rapid cuts/lighting changes can over-trigger.
3. **Targeted 3–4 fps windows only** around uncertain character speakers, gags with visible action, gestures, insert shots, and transitions that require visual correlation.
4. Keep original-quality small frame stills for evidence review at selected timestamps, with a source timestamp and checksum.
5. Optional synthetic per-episode “scrub” MP4 at 1 fps H.264, no soundtrack, typically modest in size. Use it only for visual reference, not for detecting phonemes or full facial movement.

These are **complementary**: extracting and compressing video does not improve word accuracy by itself; audio leads for speech content, images help speaker attribution/physical comedy, and retained original timing binds them.

### An episode bundle

```
Night Court Script Factory/
  S01/S01E01/
    inventory.json             # source path (redacted credential), edition, size, duration, streams, language, hash if computed
    audio/
      mono-16k.flac            # transcription/diarization source
      listening.opus           # optional
    visuals/
      scene-cuts.jsonl         # scene/shot frame timestamps and confidence
      contact-sheets/         # bounded thumbnail atlases
      preview-0p5fps.mp4      # optional sampled-frame review; no soundtrack
      windows/               # targeted higher-fps evidence snippets
    analysis/
      asr-primary.srt
      asr-alternative.srt       # independent model if worth the compute
      words.jsonl              # word timestamps and uncertainty estimates
      speaker-embeddings.json  # anonymous diarization labels, NOT character names
      diarization.jsonl        # speaker turns and overlap intervals
      alignments.jsonl         # ASR vs held subtitles and manual corrections
      qc.json                 # WER proxy, duration, gaps, overlaps, source hashes, unresolved segments
    manifest.json              # immutable paths, SHA-256, tool versions, params, processing status
```

**GitHub stores** small structured derivatives: `seasons/Sxx/SxxEyy/dialogue/` versioned timed scripts, explicit speaker-turn candidates, visual event annotations, provenance, metadata, quality and source-to-claim evidence. Avoid uploading full videos to GitHub, issue comments, Action logs, or chatbot messages.

### Pipeline, in order

**P0: video catalog.** Manually dispatch the existing metadata workflow. Check each episode's naming, 1984/revival identity, actual media duration and stream availability before ingesting bytes. Record unmatched/duplicate filenames without guessing an episode ID. All 193 episodes require a matched source/version or a missing flag.

**P1: bounded single-episode proof.** Choose a first-season episode with a held SRT witness and a well-matched file; run FFmpeg `ffprobe`, text subtitle extraction first, 16-kHz mono FLAC and a 0.5-fps visual preview. Measure source media duration, speech file size, decoded speech, frame/shot counts and upload bytes. Use a deliberate owner-restricted work environment with access to the FTP root. No blind upload.

**P2: transcript comparison.** Prefer actual embedded source captions when available. ASR with faster-whisper, at least one medium/large model appropriate to the compute; detect and align existing subtitle text with speech, preserving competing readings. Generate word-level evidence with source segment offsets. Where captions and audio disagree, flag with timestamps for review, do not silently adopt either. Speech hallucinations in silence, names, music and laughter are likely failure points.

**P3: speaker identification.** Perform anonymous diarization first, then correlate speaker intervals to visual shots and established character roster. Require support for proposed recurring character names: repeated face/voice continuity, unambiguous dialogue address and cross-scene evidence. Character labels have confidence and evidence locators; never presume a TVmaze cast credit proves appearance. Use 3–4 fps windows for turns whose speaker identity remains uncertain; near-silent visual gags can be annotated independently.

**P4: scripts and scene graph.** Align utterances, non-speech cues, physical actions and edits to timeline; attach multi-source citations and known-source-edition qualifiers. Create readable scripts and machine-readable structured scene/event/comedy graphs. LLM summarizers should see snippets with source IDs and timestamps, not hallucinate absent dialogue.

**P5: QA acceptance before wide processing.** Test at least three representative conditions: (a) held SRT matches media, (b) OCR/image-caption or audio-only fallback, (c) rapid dialogue/overlap and visually ambiguous speakers. Require nonzero source byte/hash integrity, audio/video duration reconciliation, source matching, source timing, unresolved speaker count and explicit AV review status. Passing an ASR run is not equivalent to verified episode-complete dialogue.

**P6: season factory.** Once the single-episode evidence pack succeeds, process seasons in small non-overlapping jobs, cache outputs by SHA-256 and tool configuration, and skip already accepted episodes. Separate I/O/network slots from CPU/GPU slots to avoid overwhelming the FTP host or the account-wide GitHub runner cap. Never block workers polling a single runner; issue jobs only when inputs and resource budgets are known.

## Storage, transfer and credentials

- **Default storage: existing FTP media account** in a sibling derived-data folder, e.g. `/downloads/Night Court Script Factory/`. This is a proposed new directory, not a verified existing folder. For archival safety, preserve inputs read-only and create derivatives in a separate location.
- **Google Drive alternate**: `ChatGPT/Night Court Script Factory` if the owner prefers browser-friendly review/share and upload permissions are available. A connected Drive read/search does not imply unattended GitHub Actions upload. Before implementation, establish whether a proper Google service account with limited folder access or delegated OAuth credential is available; don't borrow unrelated Uniracers recovery credentials.
- Use encrypted FTPS/SFTP transport where the host supports it; the existing confirmed S60 path uses plain FTP. Plain FTP exposes authentication and content in transit and is a security tradeoff. Never paste credentials into logs, repositories, source metadata or issue comments.
- Process a small batch and stage summary manifests to GitHub; upload binaries directly to the chosen store from the processing host. Add resumable transfers, checksums and re-download spot checks before deleting temporary working files.
- Owner's privacy/rights expectations: use locally/legitimately accessible source media, avoid DRM bypass, and keep copies restricted to the owner's private research context. No published transcript mirrors.

## Size budget, not promises

For ~22-minute episodes, 16-kHz mono PCM would be around 42 MB; 16-kHz mono FLAC often materially smaller, for planning say 8–20 MB/episode. At 193 episodes that is **roughly 1.5–3.9 GB** of lossless mono audio. Optional Opus 48 kbps is about 8 MB per episode mathematically (`48 kbps * 1,320 sec / 8 = 7.9 MB`) and **~1.5 GB** for the series. Preview video size depends strongly on resolution/codec/content; **measure a single actual episode before forecasting**. Contact sheets, cut lists and scripts are generally much smaller than continuous-frame output.

The original 193 video files remain the authoritative visual/audio source. Do not delete them or claim derivatives are reversible to broadcast masters.

## Immediate next actions

1. Run the already created [Night Court FTP video metadata](https://github.com/gamesbyian/general-purpose/actions/workflows/night-court-ftp-video-metadata.yml) with `protocol=ftp`, root `/downloads/Night Court TVRip S1-S9`; look for a **workflow_dispatch** run with its inventory job completed (not merely a push-triggered offline test).
2. Reconcile resulting filename/size/stream metadata with all 193 `episode.json` IDs and 35 existing owner-supplied S01/S02 subtitles.
3. Choose one representative matched episode; implement and test a bounded media-derivative job with no GitHub uploads of video and no secret disclosure.
4. Compare whether processing in place on the Seedhost server, on a separate machine with secure transfer, or on a permitted cloud runner minimizes avoidable video bytes crossing the network.
5. Keep `catalog/dialogue-coverage.json` authoritative: presently 35 held tracks/episodes, 158 without held dialogue, zero independently AV-verified complete. Source leads are separate from held bytes.
