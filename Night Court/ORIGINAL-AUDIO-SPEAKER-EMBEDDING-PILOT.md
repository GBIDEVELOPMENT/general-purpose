# Original soundtrack voice evidence: S01E01 P1 matching pilot (2026-10-25)

**Priority 1 is not 751 labels, but 751 correctly named original source units, with P0 true performance-turn switches repaired as necessary.** Current verified held source coverage remains 751 cue-derived units, with 583 *editorial proposals* and 168 remaining UNKNOWN. There are still zero new independently adjudicated sound/face actor identity recognitions in this process.

## Immediate source evidence experiment

`tools/compare_original_speaker_embeddings.py` now offers the first **genuine original-soundtrack-based** voice discrimination for S01E01. It uses one SHA-pinned owner FTP AVI (`5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`) and matches the original-caption SRT's actual candidate cue timings, keeping subtitles and AVI pinned to their recorded editions.

Pipeline:
1. Use the stable v4 character-ledger *provisional, longer, non-multivoice* speech units as candidate seed voice references. Require at least four same-role, timed cue examples, and spread up to 16 seed voices throughout the source film rather than learning one scene.
2. FFmpeg-decode the original AVI's primary audio to a private, ephemeral mono 16 kHz waveform once.
3. Use the openly distributed [Resemblyzer](https://github.com/resemble-ai/Resemblyzer) 0.1.4 local voice encoder to extract voice embeddings for those seed cues and for all sufficiently long **originally unknown** S01E01 cue candidates.
4. Compute leave-one-out identification against all other reference voices, **never using the candidate's own embedding**. Report whether the seeded cast reference voices are even acoustically coherent. No successful holdout means no promoted candidate predictions.
5. Rank only unverified sound similarity candidates using cosine similarity and a separation margin, with explicit negative/ambiguous abstention; retain source cue, source/video SHA, model and numeric scores, but **no voice embedding, model weights, transcript text, PCM or AVI** in the retained evidence report.

### Important limitations

* This is actor/voice **similarity conditional on pre-existing provisional speaker names**, not independent proof that those seed names were correct. Holdout accuracy estimates *internal consistency with previous guesses*, not real actor identification precision.
* Caption timestamps can disagree with video audio. No independently checked alignment was done by simply matching file SHA. A sample may include overlapping speech, laughter, music, dub/splice, or silence. Multi-voice caption cues are explicitly excluded; short/ambiguous audio is an abstention, not a guessed name.
* The public voice model was trained for speaker embeddings, not vetted on this sitcom. Model similarity thresholds are uncalibrated and cannot be interpreted as probability of a true identity.
* There is no transfer of the private original movie/audio to a hosted inference provider and no claim of audio-*confirmed* identity. The result is an **additional independent acoustic evidence feature**, feeding a focused real-film/audio reviewer acceptance workflow.
* S09E19 has an original **untimed** transcript; the source timing assumption is not available there. It requires original soundtrack transcript-to-ASR alignment before analogous embeddings can be meaningfully attached to its paragraph IDs.

### How to run

PR CI and local quick test use no source credential:
```sh
python 'Night Court/tools/test_compare_original_speaker_embeddings.py' -v
python 'Night Court/tools/compare_original_speaker_embeddings.py' \
  --plan-only --output /tmp/night-court-original-speaker-plan.json
```

After an independently reviewed and merged change to main, owner trigger branch **`research/night-court-owner-speaker-embedding-trigger`** with `Night Court/research/trigger-source-speaker-embedding.txt` requests the **existing trusted base** `night-court-source-speaker-embedding.yml` workflow. Its privileged job checks out only base `github.sha`, installs local source speaker-embedding model, reads the existing exact owner FTP original through the preconfigured secret, and emits only small numeric/hash/cue source identity proposals as a private 7-day Actions artifact. Trigger PR itself does not run source code from a PR head and is not merged.

Do not reproduce or archive owner credentials. Do not attach extracted speaker voiceprints to GitHub; numeric similarity scores are enough for subsequent **explicitly independent actual-audio/film review**. If heldout reference accuracy is below 0.6 or too few seed roles meet minimum support, the pipeline stops short of any named unknown-speaker proposals, recording diagnostics only.

Next steps: inspect resulting actual source sample counts, internal cross-validation accuracy, mean/median role separation, identify soundtrack/caption timing drift and anchor pollution, and *then* perform targeted original-AV listening to confirm or overturn sample candidates. Only audio-confirmed/vetted labels may count against the final release's independent speaker acceptance gate.
