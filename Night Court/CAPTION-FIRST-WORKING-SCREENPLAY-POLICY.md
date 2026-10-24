## Delivered pilot files (2026-10-24)

The renderer and its source-free tests merged via [PR #310](https://github.com/gamesbyian/general-purpose/pull/310), fixed source-format whitespace in [PR #312](https://github.com/gamesbyian/general-purpose/pull/312), and published two actual whole-held-dialogue working scripts via [PR #313](https://github.com/gamesbyian/general-purpose/pull/313). The private original witness text is preserved: S01E01 has 336/336 SRT cues and 404 typographic speech units, S09E19 has 347/347 untimed paragraphs. Six existing sampled picture notes were incorporated in each, without fabricating other scenes or character assignments. Both have deterministic source manifests and targeted review queues. This is **2 source-complete dialogue working drafts**, **0 editor-ready, visually complete scripts**, and **0 independently certified full AV scripts**, with no silent model overrides.

# Night Court caption-first working-screenplay standard

**Effective 2026-10-24. This changes working-draft production priorities, not the independent archival acceptance standard.**

## Two separate deliverables

**Working screenplay (production/editing draft)** is the useful first deliverable. The best held caption/closed-captioning text is the **presumptive dialogue**. Existing textual variants and independent ASR are **exception detectors**, not votes that automatically replace captions. A complete *held-source-dialogue* draft is possible before every word has been listened to. Preserve exact subtitle SHA, cue/paragraph IDs and time provenance; changes to dialogue require editorial decision and original audio review when consequential.

**Archival AV-certified screenplay** is a higher, optional successor. It still requires the independently reviewed, source-video-grounded stage, performance, speaker and original-dialogue coverage set out in [AV-SCRIPT-PUBLICATION-GATES.md](AV-SCRIPT-PUBLICATION-GATES.md). The stricter gate remains intact and does not block creating, editing or distributing a properly labeled *working draft*.

## Fast operational rules

1. Start from original user-provided captions. S01E01 has 336 timed SRT cues; S09E19 has 347 **untimed** transcript paragraphs. Keep all original dialogue in order, with source refs. Never turn an S09 paragraph into an original caption timecode on the basis of matching ASR text.
2. One reasonably good free-decoding ASR pass is enough for *routine* dialogue checking when an appropriate model transcript is available. Model agreements corroborate but cannot overrule the text. For S01E01 preserve the 16 already known independent-model/SRT mismatches as **specific short listening tasks** rather than re-listening the entire episode or running heavier models by default. On top of mismatch review, use a small deterministic source-spread sample, including agreements. A clearly bad edition match or substantial repeat omissions triggers an escalated ASR/source check.
3. Treat caption timing as the working timeline, subject to edition drift. S09E19 has no original cue timing; treat any model timestamps as independently derived *proposals* until visual/audio synchronization is established. Standard screenplay does not require syllable-accurate word timestamps.
4. Speaker names may be printed when directly provided by a source cue or independently grounded in other evidence. Otherwise use identifiable temporary voice tags or provisional attributions explicitly marked as unverified; never confuse a cast list with automatic proof of a speaking voice. Unambiguous conventional attribution may be added during editorial work with source references without demanding formal diarization.
5. Prioritize actual scene boundaries, observed locations, entrances, props, reactions, physical comedy and comic delivery. Use already archived frame observations now. Blank or generic setting descriptions are an *editing gap*, not an excuse to fabricate a scene from subtitle silence or nearby dialogue. A significant gag must not be summarized solely from sound effects or absent images.
6. Measure delivery via understandable screenplay quality, not the number of research artifacts. Track whole-source text coverage, number of real scene descriptions, important physical gags represented, unresolved speaker labels, edition drift, targeted listening minutes, and minutes of **useful complete script** produced. Do not count metadata generation as scene acceptance.
7. Don't rerun both full-episode recognizers or model calibration merely because an episode draft is being formatted. Cache small, exact-source-SHA metadata; reserve stronger ASR, diarization and semantic video for difficult intervals and evidence that improves the script.

## Quality stages (kept separate)

| State | What actually exists | Claim allowed |
| --- | --- | --- |
| `SOURCE_ONLY_SCAFFOLD` | Dialogue source arranged in rough caption-gap blocks | Reading scaffold; not a screenplay |
| `COMPLETE_HELD_DIALOGUE_WORKING_DRAFT_VISUAL_AND_SPEAKER_EDIT_PENDING` | **All held dialogue preserved** in a readable, scene-editable episode draft, with existing observed directions and an actionable targeted review list | Complete source-dialogue **working draft**; not a completed visual screenplay |
| `WORKING_SCREENPLAY_EDITORIALLY_READY` | Dialogues and speaker identities are sufficiently legible; real settings, scene transitions and important physical action are substantially represented; editorial reading passes | Usable production-style draft, but not independently AV certified |
| `INDEPENDENTLY_AV_CERTIFIED` | Original-source whole episode reviewed with explicit acceptance | Independent archival screenplay under the unchanged strict publication policy |

No agent can promote a draft merely by generating files or by setting a status string. The editor-ready stage requires actual evidence-informed editorial assessment and an episode-level checklist showing the substantive scene, speaker and physical-comedy work was done. The strict archival gate is separately controlled.

## Current pilots and immediate production order

The script renderer `tools/build_caption_first_working_drafts.py` produces deterministic, SHA-pinned source-dialogue working drafts in each pilot's `derived/caption-first-working-draft-v1/` with a manifest and small audio review list.

- **S01E01:** timed 336-caption source; 16 priority original-audio discrepancies, 8 deterministic spread controls unless overlap; six time-sampled moving-picture notes around 01:00–01:30, plus a proper observed book-lined office heading. Current rest of episode is still missing a significant quantity of setting, speaker and physical action coverage.
- **S09E19:** original 347 untimed paragraphs; 8 source-spread controls; six sampled visual descriptions from the 15:00–15:25 candidate passage, properly called a **candidate** location in transcript order. No original word times are invented. Stage/scene continuity over the rest of the episode needs actual interpretation.

The first outputs explicitly count as **complete held-source-dialogue working drafts**, not finished AV scripts. They become genuinely readable screenplay products only after the unresolved scene/speaker descriptions and key silent gags are filled in. Improving that is the next production bottleneck; the dual-ASR benchmark alone cannot complete this step.

## Caption quality, spot checks and escalation

The existing S01 184/200 substantially corresponding spans are **not** a population accuracy estimate; the spans were chosen from independent recognizer agreement. Do not set a caption reliability percentage from them. Prioritize known disputed words and jokes, overlapping voices, line omissions, and random controls sampled across the whole episode. If the caption/video edition is clearly offset, wrong, clipped or systematically divergent, temporarily escalate matching and source listening; otherwise avoid another full-recognizer round. Ordinary wording tweaks go through editorial decisions rather than globally altering the original.

Output is private owner-directed research using held sources. Copyright/redistribution rights are not established by the source repository.
