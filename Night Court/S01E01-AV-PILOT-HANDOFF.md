# S01E01 audiovisual and vocal-performance pilot handoff

**Status: bounded local-media pipeline and actual S01E01 source audio/video sample processing completed; independent audiovisual and speaker verification remain open.** Dated 2026-10-23. Scope original 1984–1992 *Night Court*. This handoff supersedes historical 35-dialogue-witness planning figures: the actual private archive has 193 episode witnesses (192 SRT, one S09E19 untimed). Zero episode cuts have been certified audiovisually complete.

## Confirmed FTP inventory dispatch: 2026-10-23

Owner-dispatched [workflow run #40041061527](https://github.com/gamesbyian/general-purpose/actions/runs/40041061527) completed both offline and authenticated metadata-only inventory jobs. The read-only listing covered **193 AVI files across 10 directories**, with **no listing errors** and no scan cap reached. Source basenames use `Night Court - 1x01 - ...`, so the previous `S01E01`-only recognizer initially mislabeled all 193 as unmatched. The reconciled, self-contained [inventory JSON](catalog/ftp-video-inventory-2026-10-23.json) now maps **193 unique expected season/episode IDs with zero missing, duplicates or extra IDs**.

**S01E01 candidate:** `/downloads/Night Court TVRip S1-S9/Night.Court.S01.DVDRip.DivX/Night Court - 1x01 - All You Need Is Love.avi` (183,386,112 bytes). Subsequent real processing confirmed its AVI fingerprint, MPEG-4/MP3 streams, 1448.256-second runtime, bounded audio sample, frame hashes and a source speech-model sample. **Filename and digital evidence do not independently establish all audiovisual episode content, edition or transcript completeness.**

## Implemented in this PR

- `tools/run_s01e01_vocal_pilot.py`: accepts one **locally present, owner-confirmed** episode file; probes streams/duration with ffprobe, computes a streaming SHA-256 of the unchanged input, extracts only a bounded ≤30-second 16-kHz mono PCM excerpt using FFmpeg into a temporary directory, and runs the existing standard-library acoustic measurement backend. Outputs compact JSON (source hash, timestamps, RMS/peak/mix activity) without original media or credentials.
- `.github/workflows/night-court-s01e01-vocal-pilot.yml`: exercises the real ffprobe/FFmpeg pipeline on synthetic video plus a 190-Hz synthetic tone, rejects missing owner confirmation and tests the output's epistemic limits. No FTP/password access; no media/model downloads.
- `VOCAL-PERFORMANCE-ANALYSIS.md` and `VOCAL-TOOLCHAIN-QUICKSTART.md`: installed requirements and backend/rights caveats from merged PRs #85–86. An optional eGeMAPSv02/YIN backend passed synthetic CI, but is not yet called in the bounded pilot.

## How to execute on a real owner-authorized local S01E01

The source video must actually be accessible to the machine running this tool. The video folder `/downloads/Night Court TVRip S1-S9` is confirmed on the owner's FTP; its files have **not** been moved to this runtime. The existing read-only video-file inventory Actions workflow is `.github/workflows/night-court-ftp-video-metadata.yml`, manual dispatch with `protocol=ftp`, `remote_root=/downloads/Night Court TVRip S1-S9`. It will not fetch video bytes.

Example when the real episode file has been lawfully obtained on an authorized local workstation, without requiring additional GitHub Actions secrets:

```bash
python3 "Night Court/tools/run_s01e01_vocal_pilot.py" \
  --media "/local/verified/NightCourt-S01E01.mkv" \
  --episode S01E01 --start-seconds 60 --duration-seconds 15 \
  --confirm-original-series --confirm-rights \
  --output "/private/research/S01E01-pilot-vocal-evidence.json"
```

Example source file/path is illustrative. Source identity checks are owner assertions and filenames, **not** AV verification. Output lives outside the Git checkout unless a separate, deliberately reviewed import path is approved.

## Actual owner-hosted source processing workflow (next manual action)

The successful owner-dispatched FTP scan was fully reconciled and committed in PR #88: all 193 video filenames match canonical IDs, although their actual audiovisual contents remain unverified. This lane adds `Night Court/tools/pilot_ftp_video_acoustics.py` and a **manual-dispatch** workflow `.github/workflows/night-court-s01e01-real-audio.yml`. It is strictly limited to the exact 183,386,112-byte S01E01 AVI from that inventory. It downloads the one selected AVI transiently to an ephemeral GitHub Actions runner, computes its SHA, extracts at most 30 seconds of audio with FFmpeg, runs the existing local acoustic baseline, then **uploads only a small JSON evidence artifact**. Original media and derived WAV bytes are not uploaded or committed. All work uses the pre-existing repository `FTP_PASSWORD` secret, without redistributing credentials to other repos.

The workflow must be triggered deliberately from the default branch after its CI and merge, with `protocol=ftp` (the verified service compatibility mode), `start_seconds=60`, `duration_seconds=15`. FTPS is preferable if separately verified. It is **not** being represented as already dispatched or having analysed the actual episode. Remote material is not downloaded during the PR's offline CI tests.

This limited proof gets us real source-derived **mix-level RMS/peak/activity** and media stream metadata; it does not yet run Whisper, eGeMAPS, diarization, subtitle synchronization, visual observation or script reconstruction. After the manual run completes, review its artifact's hash, duration and stream information before accepting the episode's source cut.

## First actual S01E01 FTP media pilot succeeded (October 23, 2026)

The owner-controlled, base-code-only PR trigger [PR #93](https://github.com/gamesbyian/general-purpose/pull/93) launched trusted [workflow run #40042590948](https://github.com/gamesbyian/general-purpose/actions/runs/40042590948). The run **completed successfully**, including the 183,386,112-byte source AVI read, FFmpeg extraction and small JSON artifact. Permanent small result: [research/s01e01-real-ftp-acoustic-pilot.json](research/s01e01-real-ftp-acoustic-pilot.json). The source file SHA-256 is `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`; audiovisual identity beyond owner's filename assertion is still unverified.

The AVI is MPEG-4 video plus stereo 48-kHz MP3, duration **1448.256 seconds**. A **15-second mixed-soundtrack excerpt from 60 to 75 seconds** was converted to temporary 16-kHz mono PCM, measured (RMS **-20.35 dBFS**, peak **-3.97 dBFS**, sample activity over -40 dBFS **0.7773**), and then deleted from the runner. Source AVI and intermediate PCM were not included in the artifact. The original FTP read is still subject to the existing transport warning for plain FTP.

This is genuine **audio-processing infrastructure acceptance**, not speaker recognition, expressive delivery, original audio verification, source-caption time alignment, physical-stage-direction production or full-episode transcription. The remaining active task is to develop exact source-to-subtitle time mapping, candidate speaker diarization, optional acoustic pitch/eGeMAPS measurements on truly separated/clear speech, and scene-video evidence capture for a small cut-aligned sample.

## QA/acceptance ledger

| Gate | Result |
|---|---|
| 193/193 dialogue episode witnesses present | Completed in prior merged acquisitions |
| 192 SRTs plus S09E19 untimed source | Completed |
| Acoustic tools and optional eGeMAPS/F0 packages installed/tested on synthetic audio | Completed, CI #40040579138 |
| FFmpeg/ffprobe single-episode bounded orchestration | **Completed and exercised on original S01E01 source** |
| Actual S01E01 video-file identity and edition verified | **Not yet** |
| Actual authorized S01E01 audio excerpt obtained and acoustically measured | **Completed, real pilot #40042590948** |
| Caption/audio offset and drift map | **Source-only 60–90s word-timing hypotheses exist; global offset/drift unverified** |
| Speaker diarization and identity validation | **Not yet** |
| Vocal delivery observations vs laughter/music contamination | **Not yet** |
| Scene, physical action, and full episode AV script | **First source-linked static-frame scene passage rendered; dense 75–90s motion-review sampling in progress, complete production script not yet accepted** |

## Next engineering lanes

1. Inventory actual filenames and source media properties on FTP using the existing **manual** metadata workflow. Resolve exactly one S01E01 filename, expected cut and runtime without importing a full season.
2. Arrange authorized bounded source processing where video bytes are legitimately available. Avoid copying large videos to GitHub or Actions artifacts. Prefer media processing near the existing video storage, exporting only a compact evidence package after exact hash/cut checks.
3. Implement SRT-to-audio alignment and time-map for the S01E01 caption witness; compare different cuts and original soundtrack.
4. Add optional acoustic features to the bounded runner (same PCM excerpt), and a media-aware diarization and review layer. Do not confuse openSMILE/yin pitch with emotion recognition or speaker identity.
5. Add frame-grounded scene/action observations and ensure that source cue IDs, audio intervals, frame IDs and reviewer decisions share a consistent schema.
6. Independently review a pilot against actual footage before scheduling 193 episode processing. Never elevate an ASR or LLM judgment into audiovisual completeness without evidence.

**Resource constraint:** no full-episode copy, FTP media credential plumbing, or unattended multi-episode Actions factory was added. No preview frame or real dialogue snippet is represented as observed from video.
