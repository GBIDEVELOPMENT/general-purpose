# Vocal toolkit quickstart

The documented tool contract is [VOCAL-PERFORMANCE-ANALYSIS.md](VOCAL-PERFORMANCE-ANALYSIS.md).

## Locally, without external models

Use an authorized, existing local media file and FFmpeg to create a **bounded** audio excerpt (the following sample offset is arbitrary, not a claim of real episode timing):

```bash
ffmpeg -ss 60 -t 15 -i "/path/to/authorized/S01E01.mkv" -vn -ac 1 -ar 16000 -sample_fmt s16 -c:a pcm_s16le "/tmp/nc-voice-example.wav"
python3 "Night Court/tools/measure_vocal_performance.py" \
  --wav /tmp/nc-voice-example.wav --episode S01E01 --source-id unaligned-pilot \
  --start-ms 0 --end-ms 10000 --output /tmp/nc-vocal-baseline.json
```

The baseline is standard-library only. It measures mixed-audio signal RMS, peak, and activity. It does **not** estimate F0, label a speaker or diagnose an emotion.

## Optional pitch/voice features

```bash
bash "Night Court/tools/setup_vocal_environment.sh" acoustics
"Night Court/.venv-vocal-acoustics/bin/python" "Night Court/tools/measure_vocal_prosody_optional.py" \
  --wav /tmp/nc-voice-example.wav --start-ms 0 --end-ms 10000 \
  --output /tmp/nc-vocal-prosody.json
```

This produces **YIN pitch candidates** and openSMILE **eGeMAPSv02 functionals**, not authoritative emotional labels. The acoustic dependencies passed the GitHub Actions install and synthetic analysis smoke test; these installations are ephemeral to the runner, not persistent third-party binaries or weights in Git.

For heavier future tools:

```bash
bash "Night Court/tools/setup_vocal_environment.sh" asr
bash "Night Court/tools/setup_vocal_environment.sh" diarization
bash "Night Court/tools/setup_vocal_environment.sh" emotion
```

Each tier is independently optional and creates a separate Python environment. These commands **install Python packages, not Hugging Face model weights**, do not accept gated model terms, and are not a configured episode-media-processing deployment. Pin downloaded models, hardware variants and licensing before inference. For some diarization models, approval and an HF token are necessary. Never store tokens or media in Git, issue comments or Actions logs.

The original television mix includes audience laughter and music; no amount of model confidence establishes pure-speaker prosody in an overlapping passage. Apply identity/baseline comparisons only to evidence-supported speaker tracks.

## CI

Workflow: [night-court-vocal-toolchain.yml](../.github/workflows/night-court-vocal-toolchain.yml). On PRs touching this toolchain, it runs standard-library synthetic checks and a full openSMILE/librosa install plus eGeMAPS/F0 smoke test. A manual dispatch can re-run the optional acoustics installer. Never change this into bulk episode extraction without a dedicated bounded video/credential workflow.
