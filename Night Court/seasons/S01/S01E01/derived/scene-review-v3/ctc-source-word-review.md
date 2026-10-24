# S01E01 independent CTC original-text word timing candidates

**No CTC output is a certified dialogue timestamp or speaker label.**
Source AVI SHA-256: `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`
Original SRT SHA-256: `aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496`
Acoustic model: `facebook/wav2vec2-base-960h`, revision `22aad52d435eb6dbaf354bdad9b0da84ce7d6156`
CTC word candidates: 42; word-level abstentions: 2.

| Original caption turn | Acoustic support | Candidate words | Abstentions |
|---|---|---:|---:|
| C0019 turn 1 | abstain_no_source_ASR_turn | 0 | 0 |
| C0019 turn 2 | candidate_ctc_forced_alignment_not_audio_verified | 9 | 0 |
| C0020 turn 1 | candidate_ctc_forced_alignment_not_audio_verified | 13 | 0 |
| C0021 turn 1 | candidate_ctc_forced_alignment_not_audio_verified | 6 | 0 |
| C0022 turn 1 | candidate_ctc_forced_alignment_not_audio_verified | 1 | 1 |
| C0022 turn 2 | abstain_no_source_ASR_turn | 0 | 0 |
| C0023 turn 1 | candidate_ctc_forced_alignment_not_audio_verified | 5 | 0 |
| C0024 turn 1 | candidate_ctc_forced_alignment_not_audio_verified | 7 | 0 |
| C0025 turn 1 | candidate_ctc_forced_alignment_not_audio_verified | 1 | 0 |
| C0026 turn 1 | candidate_ctc_forced_alignment_not_audio_verified | 0 | 1 |
| C0027 turn 1 | abstain_source_caption_outside_audio_window | 0 | 0 |

The CTC model is *forced* to find a monotonic path matching source text.
A path with plausible time ranges does not mean every word was spoken,
especially unusual vocabulary, laughter-covered sections or an incomplete cut.
This evidence must be independently auditioned and compared with the original
caption timing and tiny.en hypotheses before any production-script promotion.
No characters, speaker voiceprints or emotional inflection are identified.
