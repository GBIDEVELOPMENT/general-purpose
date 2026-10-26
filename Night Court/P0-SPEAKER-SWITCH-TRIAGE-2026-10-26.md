# Original-series pilot P0 switch triage, 26 October 2026

This ledger distinguishes **provisionally segmented source turns** from **still-open source turn questions**. The original [16-question list](research/probable-internal-speaker-switches-v1.json) is a historical discovery set, **not a count of sixteen still-unsegmented captions**.

## Already segmented as provisional source turns

- S09 C102: question followed by reply, and C103 continuation/reaction, via [generic P0 turn amendments](research/source-turn-amendments-v1.json).
- S09 C127: Harriet continuation followed by Mac, C146 Dan/Harry, and C284 Alex/Roz, via [v13 explicit handoffs](research/s09-explicit-address-speaker-turns-v13.json).
- S09 C188–C191: multi-voice Roz/Christine passage via [v11 mixed-voice reader](tools/build_s09_mixed_voice_turns_v11.py).
- S09 C209 and C211: mixed voices separated via generic P0 turn amendments, with the uncertain second speaker explicitly UNKNOWN.

These are **source-context segmentation proposals**, not original audiovisual certification. Re-review the boundaries with actual audio; do not count them as independently confirmed.

## Outstanding original-source P0 questions

- **S01 C219:** inline dash/“Yeah.” reply may require a new performed turn.
- **S09 C121:** sentence completion followed by “Yeah, probably.” could switch voice.
- **S09 C206:** “No, this whole thing” may begin a second voice.
- **S09 C271:** “No, really.” may introduce another bar-scene speaker; potentially more than two voices.
- **S09 C290 and C291:** pronoun/identity farce; distinguish replies without assuming character from grammatical pronouns.

There are **six still-unsegmented candidates** from the original sixteen, subject to review of all previously proposed splits. The original source transcript remains untouched, and this list does not change the currently reported **621 provisionally named / 130 UNKNOWN original caption units**, **721 provisional reading blocks**, or **0 independently AV-certified original episodes**.

## Acceptance rule

For each outstanding cue: check source exact SHA, document the unique lexical boundary, reconstruct every original Unicode character with contiguous offsets, and assign UNKNOWN wherever character evidence is insufficient. Distinguish `source turn proposed` from `original moving-source turn independently verified`. Do not inflate named coverage for a cue with an UNKNOWN sub-turn. The next most valuable work is reviewing the six pending cases and comparing source soundtrack windows, not adding further speculative names.

## Subsequent v14 source-turn amendment: four S09 cases now provisionally segmented

The latest generic [source-turn amendment ledger](research/source-turn-amendments-v1.json) adds source-exact **UNKNOWN → UNKNOWN** provisional splits for S09 C121, C206, C271 and C290. Both resulting character fields remain null, because the source dialogue alone does not establish the original performers. The splits retain all original Unicode source characters and untimed source cue statuses, and the source-only tests check every exact split anchor. These four cues have therefore progressed from *boundary specified* to *boundary incorporated into the private provisional reader*, **not** *AV-verified performed speaker turns*.

Consequently the latest private working reader is expected to contain **725 proposed speaking-turn blocks**, while the original source-unit denominator remains 751 and speaker naming coverage remains **621 provisional / 130 UNKNOWN**. **S09 C291** cannot be split by this all-UNKNOWN tool because the source-first v7 context reader already supplies a provisional Alex label for the whole cue. A separate source-span-specific amendment must retain or explicitly downgrade that earlier uncertain label. **S01 C219** is another original discovery case whose split has a source-exact specification but has not yet been incorporated into the combined private reader. As before, previously proposed boundaries also need actual audiovisual verification.

## Latest v15 incorporation: all six original discoveries now have auditable boundaries; C291 not yet inserted

Source-exact P0 candidate specifications cover all six original unresolved discovery locations. Five are now incorporated into the *private* source-first reader without independently original-AV-verified performer labels: four S09 cues (C121, C206, C271, C290) from [generic turn amendments](research/source-turn-amendments-v1.json), plus the timed original S01 C219 cue from [v15 source turn overlay](tools/apply_s01_c219_source_turn.py). The S01 original 879532–882330 ms **subtitle cue bound** must not be presented as independent timings of either candidate voice. They remain UNKNOWN.

**S09 C291 is the only originally flagged cue with a source-exact candidate boundary but no integrated new source-turn split.** It carries a prior tentative **Alex Patterson** whole-cue label from the older original-episode contextual ledger. The generic UNKNOWN/UNKNOWN amendment correctly rejected an attempt to erase that existing label. A targeted versioned partial-role source-span reconciliation is required to decide whether only the latter fragment retains the Alex hypothesis, before either role is accepted. No new names were added by the five new source-only splits.

Latest private reader: **726 provisional speaking blocks** across the two pilots, **621 provisionally named / 130 UNKNOWN of 751 original caption source units**, **zero independently audiovisual-certified original episode or cast performer identities**. Earlier P0 splits, including these new ones, remain proposals pending true-source audio/video adjudication.
