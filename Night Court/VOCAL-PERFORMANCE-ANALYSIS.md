## Integration with owner-ranked dialogue priorities (2026-10-25)

See [SCRIPT-PRIORITIES-AND-ACCEPTANCE-2026-10-25.md](SCRIPT-PRIORITIES-AND-ACCEPTANCE-2026-10-25.md). P2 delivery inference must operate on P0 reconstructed speaker turns, with P1 identities anchored or explicitly UNKNOWN. A single vocal performance label may apply to only part of a continuous multi-caption turn; retain that internal span even if the published reader does not show timestamps. For delivery tags such as (exasperated), (sarcastic), (confused), (coy) and (hesitantly), distinguish audible manner and supported editorial interpretation; no emotion from subtitle text alone. Do not spend CPU on exact alignment before resolving speaking turns.

# Vocal performance and prosody reconstruction

Status: implementable production contract, 23 October 2026. Original *Night Court* (1984–1992) only.

## Purpose and input contract

193 original-series episode dialogue witnesses are held (192 timestamped SRTs; S09E19 has untimed source-page text). None is verified complete against actual source audio/video. Do not infer vocal delivery, emotion, identities, or physical action from captions alone.

This lane adds **acoustic performance observations** to the existing caption, speaker-attribution, scene, and visual evidence tracks. It produces *factual acoustic measurements* first and *reviewable performance descriptions* second. Never write guessed emotions into the immutable caption source.

Input is an owner-authorized decoded audio derivative of an identified video cut, preferably lossless 16-kHz or 48-kHz WAV/FLAC with source/media SHA, time-map to video and the original intact. Do not move full recordings into Git or Actions artifacts. Mixes with laugh tracks, music and background noise require source-separation confidence flags. Silence in the mix is not necessarily a performer's pause.

## Tool selection and installation tiers

| Tier | Tool | What we use it for | Practical constraint |
|---|---|---|---|
| Required | FFmpeg / ffprobe | Decode and inspect local media to uncompressed 16-bit mono WAV; preserve original-media identity | Existing system package; only bounded local proof in CI |
| Required | Python standard library baseline | RMS, peak and sample-level activity, voiced/nonvoiced proxy, interval diagnostics | **No reliable pitch, emotion or speaker identity inference** |
| Optional acoustic | openSMILE Python (eGeMAPSv02) | Pitch F0, loudness, voice quality and spectral measurements | **Feature extraction is subject to openSMILE licensing; explicitly evaluate commercial permission before use** |
| Optional acoustic | librosa / soundfile | Validated pitch contour and pitch movement, onset/rhythm features | CPU dependencies; opt-in installation |
| Optional transcription | faster-whisper and/or WhisperX | Speech transcription and alignment to held words | Model downloads need explicit acceptance; GPU recommended for faster throughput |
| Optional diarization | pyannote.audio | Anonymous speaker segments and overlap candidates | Some pipelines require separately accepted Hugging Face model terms/token |
| Experimental | SpeechBrain IEMOCAP emotion model, or emotion2vec | Compare candidate delivery/emotion labels | Acted-data domain shift, language/cultural bias, laughter bleed and significant false positives; never treat labels as facts |

**Tool sources:** https://github.com/ffmpeg/ffmpeg ; https://github.com/audeering/opensmile-python ; https://github.com/librosa/librosa ; https://github.com/SYSTRAN/faster-whisper ; https://github.com/m-bain/whisperX ; https://github.com/pyannote/pyannote-audio ; https://huggingface.co/speechbrain/emotion-recognition-wav2vec2-IEMOCAP .

Keep third-party packages and models **external to the repository**. We pin Python dependency ranges in separate tiered requirements and record actual runtime package versions, model revision and SHA. Model weights, credentials, episode audio and downloaded source videos must not be committed.

## Proposed schema (per utterance, separate from source text)

```json
{
  "schema": "night-court-vocal-performance/1",
  "episode_id": "S01E01",
  "media_version_id": "locally-confirmed-cut",
  "source_media_sha256": "sha256-of-original-file",
  "audio_sha256": "sha256-of-decoded-wav",
  "dialogue_version_id": "original-caption-version",
  "source_cue_ids": ["C0107"],
  "start_ms": 250000,
  "end_ms": 252000,
  "speaker_id": null,
  "features": {
    "rms_dbfs": -25.1,
    "peak_dbfs": -5.9,
    "activity_fraction": 0.71,
    "f0_median_hz": null,
    "f0_range_hz": null,
    "words_per_minute": null
  },
  "acoustic_conditions": ["tv_mix_with_possible_audience_laughter"],
  "candidate_delivery_labels": [],
  "source_evidence": ["audio:250000-252000", "caption:C0107"],
  "review_state": "machine_acoustic_measurement_unreviewed",
  "interpretation": null,
  "model_revisions": {},
  "independently_verified": false
}
```

Illustrative values above are synthetic, not a *Night Court* observation. A speaker's intensity should be normalized against **that speaker's own confirmed baseline**, with unknown speakers left unknown. Absolute volume of a TV mix is not absolute loudness of the character. Short utterances and multi-speaker overlap should generally abstain from pitch/emotion judgments.

## Useful performance vocabulary

Prefer observable, concise delivery language where justified: raised/lowered voice, steady or rising/falling pitch, clipped pacing, drawn-out syllables, abrupt pause, breathy delivery, exaggerated articulation, audible sigh, gasp, chuckle, strained voice, interrupted speech, audience laughter starting after a line.

Treat “sarcastic,” “playfully,” “frustrated,” “fearful,” “embarrassed,” “deadpan,” “deceptive,” and “angry” as *editorial interpretations* with a confidence/evidence note. A low-energy line is not necessarily deadpan; a rising pitch is not necessarily a question. Never infer a character's internal state from audio alone.

## Three-track analysis pipeline

1. **Immutable evidence:** video/audio identity, original caption cue, edition time-map, decoded PCM SHA, per-utterance time window, source stream and hardware/tool versions.
2. **Acoustics:** base RMS and peak; voiced/pitch/eGeMAPS features only with the correct optional backend; pauses, intensity changes and delivery baseline by verified speaker. Explicitly exclude audience/music-dominated clips from confident speaker measurements.
3. **Interpretation:** independent expressive model suggestions plus text/visual context and review. Publish performance stage directions only when supported. Store alternatives and abstentions. Compare with the cast member's own established vocal baseline across verified scenes.

## Pilot acceptance and scaling

Pilot on **S01E01** only after a real local video cut is identified. Start with one 15–30-second dialogue window and a control window with audience laughter. Verify all source/file hashes and exact time offset. Hand-check 20–40 lines for acoustic measurements and performance tags, then evaluate false-positive “emotion” labels and stage directions. Test high-pitched female/male voices, overlapping crowd, music, whispered dialogue, short exclamations and unidentifiable guests. Only then automate seasons in bounded batches; cache by media/audio SHA, configuration and model revision.

Outputs: `seasons/Sxx/SxxEyy/derived/vocal-performance/<edition>/<model>/utterances.jsonl` plus feature provenance, and readable stage directions *generated from reviewed events*, never written into source subtitle files.

No automatic claims of source AV completeness, speaker identity or emotion correctness. All performance predictions remain reviewable.
