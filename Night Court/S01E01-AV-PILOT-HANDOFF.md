# S01E01 audiovisual and vocal-performance pilot handoff

**Status: bounded local-media executable added; original episode AV processing NOT yet performed.** Dated 2026-10-23. Scope original 1984–1992 *Night Court*. This handoff supersedes historical 35-dialogue-witness planning figures: the actual private archive has 193 episode witnesses (192 SRT, one S09E19 untimed). Zero episode cuts have been certified audiovisually complete.

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

## QA/acceptance ledger

| Gate | Result |
|---|---|
| 193/193 dialogue episode witnesses present | Completed in prior merged acquisitions |
| 192 SRTs plus S09E19 untimed source | Completed |
| Acoustic tools and optional eGeMAPS/F0 packages installed/tested on synthetic audio | Completed, CI #40040579138 |
| FFmpeg/ffprobe single-episode bounded orchestration | Implemented here, synthetic CI pending |
| Actual S01E01 video-file identity and edition verified | **Not yet** |
| Actual authorized S01E01 audio excerpt obtained and acoustically measured | **Not yet** |
| Caption/audio offset and drift map | **Not yet** |
| Speaker diarization and identity validation | **Not yet** |
| Vocal delivery observations vs laughter/music contamination | **Not yet** |
| Scene, physical action, and full episode AV script | **Not yet** |

## Next engineering lanes

1. Inventory actual filenames and source media properties on FTP using the existing **manual** metadata workflow. Resolve exactly one S01E01 filename, expected cut and runtime without importing a full season.
2. Arrange authorized bounded source processing where video bytes are legitimately available. Avoid copying large videos to GitHub or Actions artifacts. Prefer media processing near the existing video storage, exporting only a compact evidence package after exact hash/cut checks.
3. Implement SRT-to-audio alignment and time-map for the S01E01 caption witness; compare different cuts and original soundtrack.
4. Add optional acoustic features to the bounded runner (same PCM excerpt), and a media-aware diarization and review layer. Do not confuse openSMILE/yin pitch with emotion recognition or speaker identity.
5. Add frame-grounded scene/action observations and ensure that source cue IDs, audio intervals, frame IDs and reviewer decisions share a consistent schema.
6. Independently review a pilot against actual footage before scheduling 193 episode processing. Never elevate an ASR or LLM judgment into audiovisual completeness without evidence.

**Resource constraint:** no full-episode copy, FTP media credential plumbing, or unattended multi-episode Actions factory was added. No preview frame or real dialogue snippet is represented as observed from video.
