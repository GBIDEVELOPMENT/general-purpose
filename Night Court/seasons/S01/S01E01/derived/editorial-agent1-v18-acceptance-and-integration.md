# S01E01 Agent 1: v18 scene/P0 editorial acceptance and integration handoff

**26 October 2026. Episode scope S01E01 only.** This is a further production-facing full working screenplay, with film-frame-supported stage observations and a concrete speaker-turn layout repair. Original performed audio and continuous film **have not** been independently accepted; the episode remains unfinished.

## Current deliverable

- [Complete v18 source-picture screenplay](../../../../saved-private/editorial-agent1-v18/S01E01-editorial-screenplay.md), with 11 inline, numbered sampled-picture observations and 276 provisional speaking-display groups.
- [Matching 405-block source-character provenance](../../../../saved-private/editorial-agent1-v18/S01E01-editorial-provenance.jsonl) and [v18 SHA/delivery manifest](../../../../saved-private/editorial-agent1-v18/manifest.json).
- [Eleven item film-frame evidence sidecar](editorial-agent1-v18-picture-annotations.json), derived exclusively from **previously visually inspected original-AVI source frame sets** already preserved with clip SHA/digest references in this project. Original AVI hash: `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`. SRT hash: `aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496`.
- [Full P0 structure inventory](editorial-agent1-v18-full-p0-inventory.json): **336** original caption cues, **404** original cue-part refs, **405** current provisional reader rows, **69** original captions represented by two provisional reader fragments, **129** same-speaker display joins, and explicit unchanged C219 multi-fragment handoff. Contains actual original cue boundaries (not invented subcue timings), proposed speaker orders, and 129 reversible join records. Every audiovisual-acceptance flag remains false.
- [Precise C175 same-speaker boundary editorial correction](editorial-agent1-v18-c175-turn-join.json): both dash-prefixed lines of this *one actual source subtitle cue* were already provisionally assigned to DAN FIELDING but misleadingly rendered as two separated Dan character headings. Consolidated these into one readable Dan delivery while retaining **both** original cue-part refs and reader/provenance rows. Source cue `C175` original combined clock **700920–704720 ms**, without made-up internal bounds. This is an editorial dialogue-continuation proposal, not independently heard performer verification.

## Meaningful on-screen material now captured in the readable manuscript

1. Opening office: lavender jacket, painting overalls with yellow sleeves, painting implement, book shelves and papers. Reviewed earlier from a bounded 0–20s original-film five-fps sequence; no off-window view of the couple is claimed.
2. Office telephone beat: a uniformed figure reaches for, holds, and lowers a black landline receiver, source-frame sampled over ~82.5–88.5s. Does **not** establish Bull's specific speaking synchronization.
3. Office-window comedy: a grey-shirted figure reclines along a padded window ledge and gestures; a lavender-clad figure approaches with a folder and another adult holds rolled papers. Earlier source 160–182s sampled frames.
4. Pictured **bridge-at-night establishing view** and subsequent **courtroom location** between C073 and C074. The original caption gap spans 255503–315769 ms (C073 end through C074 start); a sampled original image near source 261s shows an illuminated bridge, with the courtroom evidenced by sampled source imagery at 279s. **No exact transition/cut time** or specific bridge name is asserted.
5. Office confrontation: actual previously observed book-lined setting and robed/ lavender-clad figures in sampled views around 621s and 675s; no inference of uninterrupted 54s blocking.
6. Courtroom return around C182: adults at the courtroom rail and uniformed staff, visually sampled at ~747s.
7. Bench coin physical business: a robed figure holds a pale disk near a lavender-clad figure's head around the 838–858s frame sequence, then manipulates another such object during the Kerr reunion around ~1094–1114s. Subtitle calls the first a coin and the later one double-headed; **neither marking nor trick mechanism is visible** in held frame evidence.
8. Late bench posture: nearly empty courtroom, a casually dressed figure reclining unusually low in the judicial chair, lavender-clad figure coming through doorway with a folder; visual sampling 1258–1278s. A final single still places a casually dressed adult near the double doors around 1395s.

All picture notes identify observable objects, clothing, position or bounded sampled motion, avoid unverified named actor-to-voice identification, and are tagged `PIC-01`–`PIC-11` in the script and evidence sidecar. Some continuous-sounding stage sentences describe an ordered *sampled-frame sequence*, not independently viewed original real-time moving film. The film was **not replayed** during v18 editing.

## Source conservation and epistemic acceptance

| Gate | v17 before | v18 current | Independent acceptance? |
|---|---:|---:|---|
| Original SRT cues | 336 | 336 | Original source SHA conserved |
| Original speaking-unit refs | 404 | 404 | Original text not modified |
| Private provisional reader blocks | 405 | 405 | Source refs preserved |
| Fully provisionally named original source units | 384 | 384 | 0 identity verifications |
| Source units with any UNKNOWN voice | 20 | 20 | UNKNOWN explicitly retained |
| Readable display groups | 277 | **276** | Proposed, not verified turns |
| Display joins (not AV-verified) | 128 | **129** | No soundtrack validation |
| Sampled-picture stage annotations in full reader | 0 | **11** | Existing historical picture reviews only |
| Independently accepted original-soundtrack actor voices | 0 | **0** | Awaiting AV replay |
| Full episode source picture/sound editorial completion | no | no | **NOT FINISHED** |

The source SRT is immutable, both C175 original caption lines remain byte-preserved within the original witness, and source character partitions, all source time envelope fields, dialogue identity attestations and source hashes persist in the new JSONL. C219's original 879532–882330 ms cue remains split into Harry provisional + UNKNOWN short reply, both parts still sharing the original cue's complete time envelope. There are still 69 original mixed/partitions to listen to and 129 display joins to verify. The single C175 repair leaves all original evidence reversibly accessible.

**Recent extra QC:** inspected all S01 *same-provisional-role consecutive display group boundaries*. Several may be intentional pauses, distinct stage actions or speech segments; do not merge them wholesale from matching role alone, especially Lana's repeated last-minute “Your Honor” calls before the late bench interaction, Harry's pivotal “I was home” followed by a new recess instruction, and extended coin/courtroom routines. The P0 join inventory preserves the open questions.

## Integration ownership and coordination with Agent 3

Agent 3 owns shared generator, pipelines, automatic artifact publisher and global manifests. **No shared generator/workflow, S09 screenplay or immutable original source changed in this PR**. Versioned S01 v18 output is safe to merge independently, then Agent 3 can incorporate the source-bound amendments after v16 using the existing role+turn ledgers. The **two v17 role corrections** must still be applied where not yet integrated: C028 Bull→Lana and C101 first voice UNKNOWN→Sheila. The **v18 C175 P0 layout correction** and 11 source-picture annotations are additive to those v17 decisions. A canonical post-v18 build is not equivalent to merely copying markdown; it should:
- verify original caption/film SHA, source cue parts and guard exact C175 text;
- preserve source C219 and C101 mixed parts without inventing timestamps;
- apply the two v17 contextual identity corrections;
- join C175's two DAN captions only in the readable layout (retain source parts and derived provenance);
- add stage annotations only if original SHA and cue anchors match;
- regenerate the S01 canonical manuscript and its 405-row provenance, and feed the same accepted role evidence into fan retrieval/FTS;
- update **computed** private producer and publisher assertions: S01 384 named /20 UNKNOWN; combined two-pilot 652/99 **only if** S09 unchanged; S01 source reader 405 blocks, **276 v18 display groups**, combined current pilot reader blocks still 727 if S09 322;
- retain 0 original-AV actor/turn verifications, stale-publisher protections, protected main-only private exports and independent archive-certification requirements.

Agent 3 may have made newer commits since this bounded S01 branch began. **Always reconcile live main and avoid overwriting newer editorial output**, even if it supersedes our v18 snapshot.

## Remaining urgent editorial work

Original original-AVI sound/picture replay of C028, C101, C175 and especially C219 second voice; listen and identify the 20 UNKNOWN source units plus named-role false positives. Then audit the 69 original multi-part captions and 129 display joins against original audio, attaching reviewed cue windows. Only then add source-listened tone/delivery, correct actor-to-action recipients, true scene cuts, entrances, comic reactions and final independent complete screenplay acceptance. This agent has not achieved those gates and will not declare the episode finished.
