# S05E05 "Safe": first-pass human-context speaker/turn review (26 October 2026)

**Status: editorial proposal only.** Original *Night Court* (1984–1992), season 5, episode 5 (aired 1987-10-29). No repository software, audio, video, speech recognizer, repository test, source regeneration, or private production-script aligner was run for this review. The source caption and previously committed derived files were **read only**. No original subtitles or reproduced dialogue are changed here.

**Machine-readable, cue-by-cue result:** [`text-only-speaker-proposals-v1.json`](seasons/S05/S05E05/derived/text-only-speaker-proposals-v1.json). It includes every C00001.1–C00300.1 source cue, a proposed single role or explicit abstention, seven **unapplied** internal-switch hypotheses, a rationale/confidence flag, and zero fabricated word/voice timestamps or Unicode split offsets. It is an editorial overlay, not a replacement speaker-attribution ledger.

## Source and live-repo reconciliation

- Repository: `gamesbyian/general-purpose`; initial `main` at `24ca5f7948ddac0fda2322d9537dfd0645117d63` (latest private pilot-delivery merge, #488). The four open PRs at the start, #99 and #163–165, concern independent Plex/FTP operations and are deliberately untouched.
- Held S05E05 subtitle: `seasons/S05/S05E05/dialogue/versions/subtitle-cat-english-online-caption-research-wit--9bdf7ef5e94675cc/original.srt`; pinned content SHA-256 `9bdf7ef5e94675ccc55238425c3ccf3dda6e46b92d9138ce0eb80a1837e978a0`.
- Actual material manually read: full [300-cue source-script scaffold](seasons/S05/S05E05/derived/source-script-scaffold-v1.md), [episode metadata](seasons/S05/S05E05/episode.json), [licensed recap](seasons/S05/S05E05/derived/reading-note.md), and existing owner [P0/P1 priorities](SCRIPT-PRIORITIES-AND-ACCEPTANCE-2026-10-25.md). The scaffold's ten **12-second-gap** dialogue blocks are not verified scenes.
- Context/corroboration: episode-specific [Wikiquote Safe section](https://en.wikiquote.org/wiki/Night_Court_(season_5)#Safe_[5.05]) labels part of the opening Harry/Dan safe exchange and first Devil/Dan transaction; [TVmaze episode credits](https://www.tvmaze.com/episodes/134326/night-court-5x05-safe) identify guest **roles**, not performed lines; [Night Court Wiki entry](https://nightcourt.fandom.com/wiki/Safe) offers secondary plot context. These sites are supplementary published textual witnesses, **not** independently listened original-episode identity evidence.
- Source text and its cue time envelopes remain canonical. Some subtitle strings appear transcribed incorrectly or run multiple people together. This review does not silently repair the dialogue or infer individual speech times within any source cue.

## Results: all 300 source captions reviewed

| Editorial disposition of original caption cues | Count |
| --- | ---: |
| Single named/persona-role proposal, high contextual confidence | **167** |
| Single named/persona-role proposal, medium confidence | **72** |
| Cue containing a *candidate* internal speaker switch, with ordered voice parts instead of one false whole-cue name | **7** |
| Deliberately unidentified whole cues | **54** |
| **Total original subtitle cues** | **300** |

**239/300** cues now have a provisional whole-cue character or persona proposal. This is **not a validated 79.7% correct-attribution figure**, because those predictions have not been audio-checked and seven further cues cannot safely be treated as a single voice. The first-pass review did not measure actual performed-turn total, precision, recall, editor time or cast voice accuracy. It created no source-audio-certified identities and did not change the authoritative two-pilot 621/130 or 0/193 independent AV-acceptance status.

The **167 high** classifications mean well-grounded *from reading* or text-specific Wikiquote attributions, not perfect certainty. Medium labels should be allowed to fail gracefully; they must not become a permanent erroneous name simply because the source scaffold previously had none.

## P0: proposed within-caption speaker changes (unapplied)

| Source cue | Ordered voice candidates | Why the one-cue/one-speaker convention fails |
| --- | --- | --- |
| **C00006.1** | Christine Sullivan → Harry Stone | She notices the new item; the reply directly addresses Miss Sullivan. |
| **C00011.1** | Christine Sullivan → Harry Stone | Her excuse about being ill ends before his teasing rejoinder. |
| **C00036.1** | Courtroom explainer **UNKNOWN** → Harry Stone | Description of trance channelers appears to run into the judge's skeptical reaction; the exact boundary needs source comparison. |
| **C00071.1** | Dan Fielding → Devil/Stu Blumberg | Dan's cut-off dismissal runs into the Devil's introduction. |
| **C00114.1** | Devil/Stu Blumberg → Dan Fielding | One voice finishes its previous statement, followed by Dan's brief reaction. |
| **C00177.1** | Dan Fielding → Devil/Stu Blumberg | Dan issues a demand; the Devil answers inside the same caption. |
| **C00208.1** | Dave (technician candidate) → **UNKNOWN** | An explosion proposal is followed by a different character's follow-up question. |

**Important:** These seven are ordered **lexical** speaker proposals. Do not apply a destructive split without reading the actual full SRT cue, locating exact Unicode text boundaries, conserving every character and cue-to-turn relation, and then checking the true soundtrack. In particular C00036 and C00208 are less certain; a text-only reader should never manufacture a precise millisecond or byte/character boundary.

A separate **same-speaker continuation** issue occurs repeatedly: C00012–C00014 (Harry), C00018–C00020 (Dan), C00029–C00030 (Mac), C00031–C00032 (Leona), C00043–C00044 (Leona's Darby persona), C00046–C00048 (Ross), C00072–C00074 (Devil), C00084–C00086 (Harry reading), C00092–C00107 (Harry's extended safe monologue), C00109–C00111 (Devil), C00161–C00176 (Harry), C00183–C00187 (Dan) and C00279–C00285 (Harry). These are candidate **display joins**, not a claim that no soundtrack cuts or overlapping voices exist. C00092–C00107 is uninterrupted in the text but spans an arbitrary scaffold gap; its speaker attribution follows the content, not the scaffold block number.

## P1: grounded character/persona observations

### Opening, safe installation and Halloween invitation (C00001–C00028)

Harry is instructing the movers and admiring his planned trick (C00001–C00002, C00004–C00005, C00007, C00009, C00012–C00014). The mover's query C00003 remains anonymous: a guest cast list does not identify which of the several workers spoke. Christine's weary reaction and attempted party excuse are C00008, C00010 and the **first part** of C00011. Harry's replies occur in the **second parts** of C00006 and C00011. Published episode-specific dialogue helps directly anchor the Harry/Dan handoffs at C00015–C00020, where Dan ridicules the safe trick and Harry rebuts him.

Bull is the strongest provisional participant in the party-invitation and pumpkin-head exchange (C00021–C00022, C00024, C00026–C00028), including the payoff where he needs eye holes. C00023 is likely Christine giving away her invitation. C00025 is tentatively Dan insulting Bull, but Roz could plausibly deliver the same gag. The sequence is a good reminder that **joke style alone is insufficient to establish a unique character**.

### Channeling case and Ed Sullivan impersonation (C00029–C00066)

Mac supplies the first-case call and charge (C00029–C00030). Leona Cowan's defense is C00031–C00032; an apparent claimed spirit speaking through her, **Darby**, takes over at C00040–C00041 and explicitly introduces itself in C00043–C00044. These are **performer-versus-persona distinctions**, not a second named guest actor appearing in the courtroom. Harry responds from the bench at C00033, C00037–C00039, C00042, C00045 and C00054–C00055. Dan is a provisional candidate for the prosecutor's case account at C00034 and the contemptuous disposal request C00058–C00060; the opening explanation in C00035 and the first voice of C00036 have **less reliable identities**.

Ross Gintz explains his situation at C00046–C00048. C00050–C00053, C00056 and C00066 read as his Ed Sullivan persona. C00049 is not assigned: the pedantic grammar correction could mark an actual switch to the persona or a different speaker. The C00063–C00065 goodbye sequence is also partly unresolved, despite the clear topic. Roz is a strong candidate for C00057, in which a bailiff asks permission to strike the witness.

**Casting caution:** the TVmaze guest table credits Ross Gintz, and a separate fan episode page suggests Gintz is associated with an Ed Sullivan impersonation. Keep `Ross Gintz`, `Ross Gintz (Ed Sullivan persona)` and the **final apparent Ed Sullivan voice** as deliberately distinguishable story roles. Their actor/voice equivalence cannot be settled from written captions.

### Dan's supposed Faustian bargain (C00067–C00083; C00108–C00125; C00177–C00190; C00263–C00276)

The seller is labeled **Devil/Stu Blumberg**, meaning the man in costume who gives his demonic aliases, not evidence that the literal supernatural Devil exists. The long exchange provides strong speaker anchoring through contract terms, Dan's name, southern background, and the character's knowledge of Dan's past. The general pattern is Devil at C00067, C00069, C00072–C00074, C00077, C00109–C00111, C00113, C00115–C00116, C00119–C00120, C00179, C00181–C00182, C00188–C00190 and C00265–C00267; Dan answers or objects in the neighboring specified cues. C00078–C00079 are **probably Dan reading the contract aloud**, but the text does not independently rule out the man holding it reading it to him.

The mixed cues C00071, C00114 and C00177 are crucial. Assigning all of any one to Dan or the Devil would bake a P0 error into an apparently confidently named screenplay. The brief C00125 response to Dan's search for a horned man could be the credited **Biker**; that remains only medium confidence. C00082–C00083 and C00269–C00270 / C00272 / C00276 are attributed provisionally to Roz's acidic banter, but those inferences are not as secure as the two principal bargainers.

### Harry alone in the safe and his conscience (C00084–C00107; C00130–C00137; C00161–C00176; C00192–C00223)

Harry's instructional reading, repeated attempts to free his hands, recognition of his predicament, rescue-note decision and meditation on the significance of his life support long Harry runs. The fictional book/instruction voice is treated provisionally as **Harry reading aloud**, not invented as an unseen narrator. His imagined `conscience` is marked as a separate **story voice** on C00216–C00217, C00219 and C00222–C00223; it may be an imagined persona or performed by the same actor, and the text cannot decide that.

**C00211–C00214 remain unknown.** The knock-knock gag could be Harry talking to himself or a deliberate switch to the conscience. Neither the first cue nor its punch line should acquire a voice simply because the later exchange appears to introduce the conscience.

### Missing judge, lunch note and rescue (C00126–C00160; C00195–C00210; C00224–C00262)

Bull is supported by his addressing Harry as `sir`, especially C00152, and by the explicitly addressed Bull rescue-plan payoff C00157–C00160. Mac is a plausible order-taker (C00142, C00145–C00148), but the lunch sequence has **multiple distinct speakers**. Do **not** treat C00138–C00160 as one voice, or assign sandwich orders by stereotype; seven of the most ambiguous reactions remain UNKNOWN.

The credited Dave is a provisional candidate for the safe technician beginning at C00195 and leading the drilling/blasting discussion through C00209; this role needs one source-AV check before a performer claim. Multiple worried coworkers interrupt Dave; C00208 is an intra-cue reply. C00206, the person who offers another drill, might be Bull or Art Fensterman, and **neither is secure enough to publish**. C00210 is a medium-confidence Roz proposal; the aggressive instruction alone is insufficient for high confidence.

Bull plausibly coaches the rescued Harry through C00248–C00252, and addresses him at C00259–C00260. Roz likely delivers the especially ferocious C00254–C00258 scolding, but C00253 and C00261 should stay unknown pending voice review. The joke-telling passage C00230–C00244 is deliberately **left unattributed**: laughter, joke set-ups and one-line punchlines do not identify which of several waiting characters performs each. The candidate `Art Fensterman` has **zero securely assigned cue units** in this pass. His being in the episode credits is not a license to attach him to a repair/mover line.

### Finale and Ed Sullivan-like encounter (C00277–C00300)

Harry's apparent conversation after the safe ordeal is textually anchored at C00279–C00286, C00289–C00291, C00293 and C00297. A second voice discusses an illusionist on `our show`, taking a secret to the grave and offering to demonstrate it: C00287–C00288, C00292, C00294–C00296 are tentatively labeled **Ed Sullivan persona/apparition**. The dialogue can support that persona without proving whether this is Ross Gintz, a supernatural Ed Sullivan, Harry's hallucination, an actor doubling a role or an intended ambiguity.

The very last C00298–C00300 `conscience`/prank turn is not assigned. It could be a final reversal among Harry and a personified inner voice. The source's abrupt ending does not justify a forced last-speaker guess.

## Highest-value abstention clusters and context pitfalls

1. **Group conversation and lunch:** C00138, C00140–C00141, C00143, C00149–C00150, C00153. Several coworkers alternate; review adjacent voices together, not individually.
2. **Rescue technician and helpers:** C00191, C00196, C00199, C00202, C00206–C00207, plus split C00208. Resolve which guest is Dave/Art and whether the drill speaker is a cast regular.
3. **Knock-knock/conscience scene:** C00211–C00214, C00220; speakers and even voice count cannot be settled by text alone.
4. **Wait-for-the-blast jokes:** C00224–C00244, especially C00230–C00237. Resist content/stereotype-based forced labels.
5. **Aftercare and finale:** C00253, C00261, C00277–C00278, C00298–C00300. The Ed Sullivan identity/performance ambiguity is central.
6. **Short fragments:** C00003, C00049, C00064–C00065, C00089–C00091, C00108 and C00128–C00129. These need local audio/visual context and may expose bad transcript segmentation or wording.

## Source-text problems observed but **not corrected**

- The trans-channeling explanation C00035–C00039 appears to cross voices without useful punctuation; its phrase resembling `mouthpieces` is rendered as an odd homophone in the held subtitle.
- The name on the Devil's license is inconsistent between the held subtitles and published episode-specific quotation. This report calls the role `Devil / Stu Blumberg` but **does not change the original recorded SRT bytes**.
- C00058–C00059, C00108, C00224–C00229, C00253–C00254 and C00277 display transcription fragments or unexpected wording. Do not infer theatrical intent from malformed strings, and do not insert guessed replacement dialogue.
- C00084–C00086 and C00130–C00132 could be dialogue Harry reads from printed escape instructions; a separate actual recorded voice would change the performance segmentation.
- Timed cue *envelopes* are available from SRT, but these are not precise start/end moments for an in-cue spoken fragment. No new subcue timing is claimed.

## Recommended follow-through, without expanding the tools

Treat this as a **new-episode test fixture** for the existing P0/P1 review design, not as an independently completed screenplay. For a fair calibration, listen to a source-spread sample containing strong, medium, and abstained cues rather than merely congratulating the high-confidence selections; include all seven mixed cues and full local context for the lunch, technician and conscience clusters. Check role **precision as well as coverage** before bulk applying any ledger. Preserve the cast/persona distinction and split/merge evidence under the existing immutable source SHA and lossless original-caption mapping.

The practical win is that a single **manual text-context pass** can provide 239 provisional whole-cue role proposals on an untouched 300-cue episode without running an ASR/VLM/diarization/scene-generation pipeline; its unknowns now identify precisely where real audiovisual review would buy the most information. No claim is made about hours saved, source-actor recognition accuracy or the 193-episode aggregate before comparison against an independently inspected original episode.
