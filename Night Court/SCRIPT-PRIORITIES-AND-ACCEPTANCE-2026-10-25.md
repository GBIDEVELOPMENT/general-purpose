# Authoritative script priorities and production acceptance contract

**Owner direction: 2026-10-25. Status: authoritative for original-series Night Court screenplay generation.**

This supersedes competing optimization priorities in older plans. Our output is a *semantically accurate, character-attributed, performance- and action-annotated reading screenplay for AI understanding*. Fine-grained synchronization is a support tool, not the finished product. Source-copyright, evidence provenance, editorial honesty, and the existing strict independent AV certification gate remain intact.

## Order of importance (ordinal, not interchangeable)

| Rank | Requirement | Primary failure to prevent |
|---|---|---|
| **0: highest** | **Correct division into speaker turns**, including merging consecutive subtitle lines by the *same* speaker and splitting within a caption when two speakers alternate | Caption boundaries mistaken for dialogue turns; merged two-speaker speech; fragmented same-speaker dialogue |
| **1** | **Speaker/character attribution** | Dialogue assigned to wrong named character, including adjacent-turn propagation errors |
| **2** | **Tone and delivery**, e.g. (exasperated), (sarcastic), (confused), (coy), (hesitantly), deadpan, whispering, shouting | Meaningful performance lost or psychological labels invented from text alone |
| **3** | **Wardrobe and props** | Missing visually grounded clothing and objects relevant to the story or physical comedy |
| **4** | **Stage directions / blocking** | Missing or reversed entrances, exits, approaches, positions, movement, gestures, who-does-what-to-whom |
| **5: lowest** | **Accurate timestamps** | Spending runtime on word/frame-level alignment instead of improving script meaning |

These ranks are **editorial triage order**, not a license to manufacture evidence or skip material stage action. Rank 3 precedes rank 4 in ordinary scheduling, but a crucial physical gag or actor/recipient reversal can be escalated ahead of incidental wardrobe. Preserve approximate cue/source references even when timestamps are omitted from the readable draft.

## Working representation

Keep **immutable evidence** separate from the **editorial script**.

- Evidence: source witness IDs, original cue IDs, raw caption text and cue splits, original media/audio SHA, approximate windows/offset maps, shot boundaries and cut hypotheses, anonymous acoustic speaker labels, ASR and diarizer proposals, cast/context candidates, visual observations, model revisions, confidence and review state. Never overwrite subtitles with inferred content.
- Script: scene heading and description; continuous character turns with text and evidence-supported performance parentheticals; relevant wardrobe/props; observed stage movement/actions. Precise milliseconds and unreviewed model labels do not clutter reader output.
- Every published name, tone or staging assertion must link to source evidence and an explicit review disposition. If unconfirmed, retain UNKNOWN, an alternative or a review item. A correct machine guess is not itself independent human review.

## Fast production procedure

1. **Caption ingestion and segmentation first.** Treat SRT boundaries, dashes, line breaks and caption sequence as evidence, not speaker truth. Resolve transitions within one cue; merge multiple cues from one speaker across caption boundaries, including off-screen speech and short pauses, without erasing meaningful interruptions. Retain original cue-to-turn many-to-many mapping and reversible text alignment.
2. **Anonymous acoustic diarization on full conversational context.** Use original audio activity, overlapping voices, shot/scene context and adjacent turns to establish who spoke when; maintain anonymous identities across excerpts where reliable. Prefer distinct-candidate turn boundaries over arbitrary word alignment. Flag laughter/music/overlap.
3. **Character naming after segmentation.** Anchor anonymous turns using visible lip-synchronized speaker, voice consistency, cast/guest roster and conversation context, with uncertainty flags. Do not assume a new subtitle cue implies a new character. Do not assign names by dialogue semantics alone or treat acoustic similarity as cast identity. Resolve conflicts and ambiguous short interjections through targeted AV review.
4. **Delivery pass on resolved turns.** Listen to source audio, compare speaker-relative prosody, pacing, emphasis, expressive context and acoustic anomalies. Label audible mechanics with high specificity; assign subjective tags (sarcastic, coy, exasperated, confused) only when source performance supports them. Prefer no tag to a fabricated tag. Make delivery span-specific inside long turns if it changes mid-speech.
5. **Visual description pass.** Identify concrete wardrobe/props across source-valid shots, tracking when objects appear, are handled, transferred or become relevant. Avoid inferred materials/colors if not visible.
6. **Action and blocking pass.** Track characters through shot and scene transitions; specify initiator, movement/action, target/recipient, location and order. Use shot-aware brief temporal runs selectively for gestures. Never join continuity across a cut without corroboration; check reversed actors and hand/object interactions explicitly.
7. **Editorial script render.** Produce a legible screenplay with merged turns, correct character headers, concise parentheticals, setting, relevant physical business and no routine displayed timestamps. Optional evidence sidecar holds coarse offsets for verification.
8. **Independent spot review and escalation.** Measure the ranked dimensions separately. Review most damaging errors first: erroneous speaker-turn boundaries, character swaps, false/omitted delivery, visual inaccuracies, staging mistakes. Escalate to expensive models or dense capture only for difficult passages or material comedic action.

## Acceptance and quantitative QA

Create a held-out *source-listened and source-viewed* reference set spanning both pilots and later episodes. Explicitly include captions with successive same-speaker lines, a speaker switch within one cue, interruptions/overlap, rapid exchanges, silent reaction, off-screen dialogue, anonymous guests, and a long emotional shift.

- **P0 turn segmentation:** independently count missed speaker changes, false turn breaks, same-speaker adjacent-cue failure-to-merge, cross-speaker erroneous merges, and exact boundary accuracy within a coarse listening tolerance. Measure error rates by episode and challenging case type. A merged two-speaker turn is critical even if text is correct.
- **P1 identification:** report character-attribution accuracy *on correctly segmented turns*, unknown/abstention frequency, confusion pairs and propagation errors; separately report end-to-end attributed-turn correctness to expose segmentation dependence.
- **P2 performance:** source-listened tag precision/recall per delivery category, unsupported subjective inference, meaningful-tone omissions, and abstentions; compare against an independent reviewer rather than assuming emotion classifier outputs are gold.
- **P3 wardrobe/props:** precision of observable claims and recall for narratively relevant objects; report unsupported colors/materials separately.
- **P4 staging:** actor-action-target accuracy, entrance/exit/scene location fidelity, temporal order and missed important physical comedy; require reviewer source observation.
- **P5 timing:** only coarse source-window recoverability, ordering and no invented synchronization; do not gate publication on millisecond/word precision.
- Record cost: elapsed episode p50/p95, model runtime, audio/visual calls, reviewer minutes and evidence bytes. **30-minute p95 initial evidence pass** remains a proposed throughput target, not achieved certification. Do not let a fast pass silently erase uncertain lines, character turns or important physical action.

**Promotion rule:** P0 or P1 critical errors block an editorially ready script in the affected passage. Evidence-free P2–P4 assertions block those assertions, not the source-dialogue working draft. A draft may be marked *working* before all dimensions are complete, but may only be marked *editorially ready* after substantive speaker/expressive/visual coverage review; independent AV certification remains a stricter separate episode-level gate. Never claim achieved thresholds or automated implementation without measurements.

## Implementation / migration work queue

1. Add a turn-boundary and consecutive-same-speaker merging stage with source cue membership retained. Support intra-cue speaker splits, overlap and explicit abstention. Place this **ahead of** named speaker attribution in the runnable workflow.
2. Extend the episode queue and source-linked review packet with counts: boundary uncertainty, same-speaker merges required, intra-cue switches, unnamed turns, performance tags pending, visually relevant props, actor/action/target defects, coarse-source-offset issues. Sort by this rank with explicit severe-action exceptions.
3. Generate reviewer fixtures for S01E01 and S09E19 containing short dialogue runs, split/merge decisions and challenging rapid exchange. Blind-listen for P0/P1 before inferring further timestamps.
4. Update script generator/parser to render one character header for a continued speaker turn, with parentheticals supported as reviewed annotations, and keep original cue lineage in a sidecar.
5. Run independent pilot QA on separate ranked scorecards and time/cost; set numeric go/no-go thresholds only after calibrated sample sizes. Preserve unknown labels and independently reviewed / machine proposed separation.
6. Deprecate old process wording that says exact word alignment must precede the first readable scripts. Forced alignment, extra ASR runs and dense picture sampling are **on-demand debugging aids** unless measured to improve P0–P4 accuracy or source traceability.

## Documentation precedence

This contract overrides priority sequencing in `AV-SCRIPT-FACTORY-PLAN.md`, `AV-SCRIPT-PRODUCTION-WORKBOARD.md`, `FAST-EPISODE-FACTORY-THROUGHPUT.md`, `VOCAL-PERFORMANCE-ANALYSIS.md`, `CAPTION-FIRST-WORKING-SCREENPLAY-POLICY.md` and old episode-specific handoffs when they conflict. Historical pilot data remains valid as historical evidence; do not retrospectively label any unreviewed source excerpt as independently AV accepted.
