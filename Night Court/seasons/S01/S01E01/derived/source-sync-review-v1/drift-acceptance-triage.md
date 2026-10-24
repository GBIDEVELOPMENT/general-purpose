# S01E01 five-window original source-to-SRT drift review

**No global offset or source timing drift is accepted.** A direct
tiny.en-to-subtitle start difference is not equivalent to a real cut
offset and can be grossly misleading with repeated or long ASR segments.

Source real-media run: [#40050642750](https://github.com/gamesbyian/general-purpose/actions/runs/40050642750)

| Source window | Candidate anchors | Proposed offset for listening only | Quality cautions |
|---|---:|---:|---|
| 300–330s | 0 | Not estimated | repeat_caption_match_possible_ASR_hallucination_or_repeated_line, suspicious_long_model_segment, insufficient_two_distinct_source_cue_anchors, no_strict_anchor_candidates |
| 600–630s | 1 | Not estimated | repeat_caption_match_possible_ASR_hallucination_or_repeated_line, end_boundary_model_proposal_clipped, insufficient_two_distinct_source_cue_anchors |
| 900–930s | 0 | Not estimated | repeat_caption_match_possible_ASR_hallucination_or_repeated_line, insufficient_two_distinct_source_cue_anchors, no_strict_anchor_candidates |
| 1200–1230s | 2 | -565.0ms, unverified | manual audio review required |
| 1350–1380s | 1 | Not estimated | suspicious_long_model_segment, insufficient_two_distinct_source_cue_anchors |

## Specific source review requirements

The 05:00–05:30 sample contains repeated matching ASR text,
including an implausible 27-second cue-start discrepancy. Do **not**
incorporate those proposals into a linear drift model.
Other windows include laughter/effects, model word hallucinations,
duplicated captions and imperfect utterance boundaries.
Independent listening must verify multiple unique original caption
anchors per window and at least one cross-window endpoint before
a drift slope or revised source subtitle timestamp can be accepted.
No actor/scene/emotion/episode completeness claim is established.
