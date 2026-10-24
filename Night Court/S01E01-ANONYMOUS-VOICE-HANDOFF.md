# S01E01 anonymous voice-similarity proof

**Status: first-pass engineering with source-independent synthetic CI pending.** Source only: original 1984–1992 *Night Court*, one pre-approved 60–90-second S01E01 window. The [ECAPA-TDNN VoxCeleb model](https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb) is publicly released under Apache-2.0, with the supported current SpeechBrain `speechbrain.inference.speaker.EncoderClassifier` embedding interface. The model is pretrained for speech speaker verification, not for sitcom-character attribution or noisy television soundtracks.

## Evidence method

`tools/s01e01_anonymous_voice_similarity.py` verifies the same original S01E01 source AVI SHA and unchanged source-caption/ASR evidence, decodes only the known 60–90-second original audio window, and submits ASR-proposed speech intervals longer than 850ms to the speaker encoder. Very short candidate turns and near-silence **abstain**. Audio can include music, laughter, applause and overlapping actors, so model embeddings are not guaranteed to describe a single speaker.

It stores **only a matrix of anonymous, uncalibrated pairwise cosine similarities**, source ASR segment/time IDs, model revision and technical caveats. It does not cluster voices into authoritative speaker identities, perform source-verified diarization, infer vocal tone or emotion, name characters or store any raw voice embedding/voiceprint. Similarity is not the probability two characters are the same speaker.

## Security and reproducibility

The trusted `.github/workflows/night-court-trusted-s01e01-ecapa.yml` is owner-only, exact-marker-branch and `pull_request_target` gated, with reviewed main-only checkout (`github.sha`) and disabled credential persistence. Crucially, **FTP_PASSWORD is exposed only in the first-party source download step**, never to the third-party SpeechBrain model. Original AVI bytes are confirmed with the known SHA and deleted before artifact publication. The model download is pin-recorded by remote commit hash at runtime and stays within ephemeral runner storage. CPU Torch/TorchAudio use matched 2.8 versions; SpeechBrain 1.0.3 is constrained away from incompatible Hugging Face Hub 1.x.

Only a private, seven-day JSON artifact is saved when the real run succeeds. This is an additional bounded analysis pass, not permission to run thousands of episode model downloads or a 193-episode bulk factory.

## Review acceptance

Compare the anonymously similar ASR spans against verified original listening and the 17-item [editorial acceptance packet](seasons/S01/S01E01/derived/editorial-review-v1/acceptance-worklist.md), carefully excluding audience, overlapping speakers and clips under 850ms. A human source reviewer must separately identify a speaker and corroborate mouth-to-voice timing before any named character can be promoted into a production scene. Cast credits are only priors.

Current source-only scripts for all 193 episodes, nine-season AV task queue and S01E01 v3 script are not overwritten by this experiment.
