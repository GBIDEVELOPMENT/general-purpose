# S09E19 “P.S. Do I Know You?” • episode editorial v17

**Owner:** Night Court Agent 2, S09E19 only. **Evidence level:** complete source-dialogue editorial pass; original performance **not** audiovisually certified. **Date:** 2026-10-26.

## Recovery and deliverables

Recovered the durable private `Night Court/saved-private/pilot-current/S09E19-working-screenplay.md` and its v16 source-linked reader/provenance, together with the current pilot ledger, issue #441, the prioritized screenplay contract, contextual reconstruction process, the S09 sound locator and embedding quarantines, and the earlier source-frame observations. This pass starts from main commit `6d2acbf1f7723fd32e73259bef24606f7af26044`, after merged #489 and #499. It neither downgrades the v16 source nor uses older v5/v13/v15 as the current manuscript.

Original **347 untimed** source-paragraph witness SHA-256: `659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2`. Original AVI SHA-256 in existing source reviews: `51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649`. No original audio was listened to or moving footage freshly inspected in this session; all new names and turn structures must remain provisional. No source timecodes were generated.

Durable episode-local outputs:
- `s09e19-source-exact-editorial-overlay-v17.json`: reversible, exact-text/old-role-guarded proposed speaker changes and cautious C291 split.
- `S09E19-editorial-v17-working-screenplay.md`: entire source-backed dialogue in chronological order under **11 editorial story sequences**, with explicit uncertainty and no invented performance detail.
- `S09E19-editorial-v17-provenance.jsonl`: all **323** resulting reading fragments and display groups, mapped to immutable v16 reading IDs, original part refs and original source SHA; C291 exact character-span offsets.
- `S09E19-all-347-cue-editorial-dispositions-v17.json`: one disposition for every immutable source unit, with retained UNKNOWN fragments, story strand and P0/P1 verification status.

## Source preservation and arithmetic

| Counter | Durable v16 baseline | This episode-local v17 | Explanation |
| --- | ---: | ---: | --- |
| Untimed original speaking units | 347 | **347** | No source edits |
| Editorial reading blocks | 322 | **323** | C291 provisionally divided into two, without lost characters |
| Entirely provisionally named units | 268 | **271** | Four source units resolved contextually, C291 becomes partly UNKNOWN |
| Units retaining any UNKNOWN | 79 | **76** | No fabricated all-named coverage |
| Independently original-audio-verified voices | 0 | **0** | No original-soundtrack acceptance |
| Independently verified performed boundaries | 0 | **0** | P0 is still provisional |

**Verified in-memory before committing:** each of the 322 original v16 S09 reading blocks matches the *exact concatenated text characters* of its corresponding v17 block(s), compared using the unique source `reading_block_id`. All 347 source cue IDs remain represented, the source SHA remains fixed on every block, all original source times are null, and exactly **12 v16 blocks** change role or segmentation (11 role edits and the one C291 split). One prior reader ref, C034.1, maps to *two* distinct immutable reading block IDs; validation uses the unique block IDs rather than naively de-duplicating the source ref.

## Significant dialogue and identity corrections

1. **C287 / C288 reversed real-character questions.** V16 assigned “Who was she?” to Roz and the “Who was he?” rejoinder to Alex. In the story, Roz hired Lisette to act as her, and Alex hired the separately credited **The Guy** to act as him. The real Alex therefore asks about the woman hired by Roz; the real Roz asks about the man hired by Alex. The speaker labels have been swapped **at high contextual confidence**, not original-voice certified. The prior context audit actually reasoned this referential direction correctly while the v16 labels remained inverted.
2. **C291 P0 handoff.** The source-exact text is `He. He was me.`. Preserve its first `He. ` as UNKNOWN and its second `He was me.` as Alex Patterson. The earlier Alex attribution is not silently erased; the first pronoun remains genuinely ambiguous. The previous S09 C290 two-part role abstention also remains intact.
3. **C272–C280 bartender/nut-salesman exchange.** The bartender's `I'll tell you what.` leads directly into the already named offer to buy drinks. C277's first fragment, offering the free snacks, is provisionally the bartender; its second fragment questions their freshness and continues into Alex's C279–C280 complaint about nuts. The bartender defends their freshness in C278. Both C277 source parts retain their original wording and exact ordered separation. The first bartender identification has lower confidence than the Alex objection because an off-screen patron is still possible.
4. **C206 first voice.** Christine's discomfort with the campaign coverage is a plausible speaker for the distressed opening fragment. Dan interrupts and calls the matter boring in the second fragment. Marked **medium confidence** owing to damaged source wording and absent vocal verification; the two-voice split predates this review.
5. **Alias cleanup at C281, C283, C296–C297.** Earlier `ALEX` labels now consistently read **ALEX PATTERSON**. This identifies the actual pen pal who complains about nuts, gives his name and later confesses to paying for the substitute performer. It does **not** rename the actor credited as **The Guy (playing Alex)**, who retains his distinct character identity for C216–C259.
6. **Preserved prior correction C305/C306.** Roz refers back to *her own* invented size-three claim; Alex answers. No regression to earlier reversed assignments.

### Deliberate abstentions

- **C129:** the original-audio reference-bank mismatch stays quarantined UNKNOWN; adjacent Harriet participation and the automobile advert gag do not override the audio concern.
- **C121 and C271:** existing exact-character P0 candidate splits retained, but actual speaker boundaries and participants remain unverified, particularly the possibility of more than two voices in C271.
- **C188–C192:** multiple text-derived Roz/Christine fragments remain in their earlier order; the transcribed text is damaged, and punctuation cannot certify the original sound.
- **C209/C211:** the original within-paragraph handoffs are retained and their unknown voices not upgraded. A plausible role based solely on prior character stereotypes is insufficient.
- **C222–C265:** anonymous spectator jokes, disguise comments and brief bar reactions remain unresolved rather than merging the actual pen pals, the hired actors and onlookers.
- **C289–C291:** the deliberately confusing he/she/you/me exchange requires original sound and ideally moving-image reaction views. C291's first fragment is now candidly unidentified.
- **C343–C347:** enthusiastic interjections during the safe's anticlimax cannot be distributed among Harry, Dan and other onlookers from subtitle text.

The remaining **76** source cues with at least one unidentified fragment are explicitly enumerated in the all-cue disposition file. The most concentrated sets are 16 in the hired doubles/spectators exchange, 14 in the office safe discussion, 10 in the restaurant dance and wager, and 7 in the real-couple exchange. No claims of 76 wrong names, or of 271 correct actor identities, are made.

## Dialogue structure, story continuity and physical evidence

The manuscript follows eleven **dialogue-derived** sequences: (1) campaign mailings/letters, (2) Fingers Kirby court proceedings, (3) Judge Grimm's office safe, (4) electoral response/safe preparations, (5) Roz's confession to Christine, (6) the lock-picking/ad backlash, (7) hired impostors' restaurant conversation, (8) the art-collection dance and spectator wager, (9) real Alex and Roz, (10) the commercial's buried footage, and (11) the safe's turkey-sandwich payoff. These are editorial convenience divisions, **not** independently observed original camera-edit boundaries.

Already retained **actual original-frame evidence** establishes: a book-lined office; a courthouse courtroom; the brightly lit restaurant/bar; dark clothing and a burgundy dress on *unidentified* restaurant dancers; a sparking object and smoke while two unidentified adults shelter behind a partition in a nominal **684–704 s** image sequence; and the dancing couple swaying and turning in nominal **951–971 s** 5fps image sequence. See `derived/source-photo-scene-overview-v1/observations.json` and `derived/physical-motion-original-v1/observations.json`. These are **sampled image observations**, not continuous motion independently checked here and **not synchronized source transcript timings**. The available evidence cannot responsibly name the actor who lit or crossed the sparking object, certify who was touching whom, or place specific words exactly on those images.

The dialogue establishes a verbal joke structure: Dan's dismissive commercial response, Mac's frustration that his crafted ad is reduced to an appraisal of Christine's figure, Roz's hesitant self-description, the substitute Alex's overly florid art discourse, the real Alex's obsessive snack expertise, and the eventual safe anticlimax. **No original vocal tone, sarcastic inflection, pause, overlap or stage gesture was newly certified**. Any performance description in a future final AV screenplay must be based on the sound and original moving picture rather than treating these semantic readings as heard inflections.

## Remaining completion and integration gate

The **episode editorial source-dialogue deliverable is saved**. The *final AV-certified screenplay is still blocked*: the existing original 1992 soundtrack and moving footage have not been reviewed to adjudicate all 76 UNKNOWN source units, the 11 important within-source P0 switches, or the physical business. Original-source review should cluster the 15:00–15:25 restaurant scene, C277–C291 bar dialog, C188–C211 ad/meeting handoffs, and the safe opening rather than launching another broad ASR benchmark. For any accepted name or motion, log original AVI/audio SHA, precise source position independently checked, actual actor/action/recipient, evidence and reviewer. Do not create timecodes on the 347 original untimed paragraphs.

**Agent 3 integration handoff:** Wire the episode-local source-exact v17 amendment layer into the durable private S09 current-screenplay selection and provenance manifest, *after* checking its expected v16 source reader and per-row text guards. Keep the shared S01 path and v16 baseline untouched, run existing private source/SHA conservation tests and durable artifact workflow, and only update common current manifests through the integration lane. Until then, `saved-private/pilot-current/` remains the shared canonical v16, while this committed episode-local v17 manuscript is the newer, explicitly qualified S09 editorial reading. Neither alone satisfies independent AV acceptance. Do not close #441 as completed.

External plot/cast context used solely to constrain candidate characters: [Apple episode synopsis](https://tv.apple.com/ca/episode/ps-do-i-know-you/umc.cmc.55pw7ljknq3ttj9993slpfkdg?showId=umc.cmc.3v8igla11dgg4chywljv2og89), [IMDb episode cast](https://www.imdb.com/title/tt0660693/), and [TVmaze's Alex credited role](https://www.tvmaze.com/characters/846493/night-court-alex). These sources are **not** voice-identity certifications.
