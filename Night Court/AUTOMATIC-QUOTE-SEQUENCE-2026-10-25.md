# Automatic quote-sequence alignment checkpoint, 2026-10-25

`tools/auto_align_quote_sequence.py` introduces order-constrained alignment across caption **parts** rather than manual cue indices. Input is the existing `research/s01e01-opening-attributed-sequence-v1.json` with an episode source SHA and attributed phrase fragments; the tool ignores its stored cue numbers when matching, then searches source caption units and proposes exact cue/part positions. The dynamic program is strictly monotonic, allows abstentions, avoids reusing the same unit, and rejects near-tied lexical candidates.

Run from repository root:

```sh
python 'Night Court/tools/test_auto_align_quote_sequence.py'
python 'Night Court/tools/auto_align_quote_sequence.py' --registry 'Night Court/research/s01e01-opening-attributed-sequence-v1.json' --output /tmp/night-court-auto-opening.json
```

**Evidence limitations:** online speaker attribution has not been validated by original soundtrack listening; matching a substring does not establish who spoke or true boundary correctness. Any automatic source cue proposal must remain `speaker_identity_accepted=false`. The code is a first-pass sequence matcher, not robust whole-episode joint quote alignment or source audio verification. Common lines and tied candidates abstain even when order could prefer a result. The pilot dataset is a short opening calibration and not a representative accuracy sample. Review original episode video/audio before applying labels to production readers.

**Next technical tasks:** run tests and source-backed pilot CLI with recorded results, improve quoted-turn segmentation for multiple snippets within one undashed cue, import a rights-aware larger episode-specific quotation registry, and evaluate held-out quote precision/recall plus genuine P0/P1 correction yield. Keep the S09E19 untimed source untimed and do not invent character anchors from merely credited cast listings.
