# Speaker identity first: original Night Court pilot recovery

**Owner's primary engineering objective (2026-10-25): resolve missing/wrong speaker identities before any further tone, wardrobe, action or fandom enrichment.** Correct conversational turn segmentation is the immediate enabling operation: a cue containing two characters must be split before either can be named. The [ranked screenplay contract](SCRIPT-PRIORITIES-AND-ACCEPTANCE-2026-10-25.md) still governs P0→P5 evidence quality. Work on additional fan knowledge is secondary until pilot unknown identities are substantially reduced by source-backed evidence.

## Baselines, proposals and provenance

- Canonical original held source: **751 original speaking units**, across 404 S01 and 347 S09 source units. Current pre-correction provisional reader: **487 named, 264 unknown**; source audio independent identity acceptance: 0.
- High-value episode-specific external quote review yields **three original source units with new role proposals** and **four proposed speaker spans** after a missed two-person source paragraph is split. Private **v6 working-reader proposal**: **490 provisionally named source units, 261 unidentified**. This improves *editorial proposals*, not independently identified voices.
- **S01E01 C142.1**: external episode-specific IMDb quote attributes the brief complaint about irregular courtroom procedure to **Dan Fielding**. Direct short source quote matches original SRT cue verbatim. Original soundtrack was not checked in this pass.
- **S09E19 C027.1**: **Christine Sullivan** proposed based on IMDb's *same-position dialogue question*, which paraphrases rather than exactly reproduces the held source question. Review this one more cautiously.
- **S09E19 C034.1**: previous S09 transcript joins two voices in one paragraph; the leading fragment concludes Roz's preceding sentence, while the subsequent reaction is attributed to Christine in the external quotation sequence. This requires **P0 split before P1 naming**. Both individual spans point to original paragraph C034.1, with start/end character offsets and no invented timestamp.
- **S01E01 C028.1**: existing reader provisionally labels the line addressed *to Bull* as spoken by Bull. This is a suspicious self-address, **not proof of misattribution**. A review flag was added; do not automatically swap it to Lana without original-episode audio or independent attribution.

Source files: [external speaker evidence seed](research/pilot-speaker-external-quote-improvements-v1.json), [original-series source index](catalog/dialogue-index.jsonl), and existing v4/v5 source-exact speaking index. Episode-specific quotes: https://www.imdb.com/title/tt0660578/quotes/ and https://www.imdb.com/title/tt0660693/ ; separate indexed IMDb character pages also corroborate the S09 dialogue exchange. IMDb quotations may descend from the same subtitles, and an attributed online quote is **not** original-audio independent identity validation.

## Immediate commands

From the repository root:

```sh
PYTHONPATH='Night Court/tools' python -m unittest \
  test_build_external_speaker_reader_v6 test_export_fan_retrieval_chunks test_fan_sqlite_index

python 'Night Court/tools/build_external_speaker_reader_v6.py' \
  --output /tmp/night-court-private-speaker-v6

python 'Night Court/tools/export_fan_retrieval_chunks.py' \
  --speaker-v6-root /tmp/night-court-private-speaker-v6 \
  --output /tmp/night-court-fan-193-speaker-first
```

Both v6 pilot screenplays, a 4-span exact-source speaker evidence sidecar and a manifest are output only to the owner's private local directory; the unchanged original caption files and existing v5 readers remain in place. Unlike unsupported bulk subtitle duplicates, this source-linked **editorial delta** can be committed safely to the repository and regenerated whenever needed.

In an already-built private LLM fan corpus, replace the previous two pilot script chunks using the v6-aware export, and update the character FTS evidence by invoking:

```sh
python 'Night Court/tools/fan_sqlite_index.py' build \
  --corpus /tmp/night-court-fan-193-speaker-first/fan-retrieval-chunks.jsonl \
  --cards /tmp/night-court-fan-beats/pilot-fan-beat-cards.jsonl \
  --roles /tmp/night-court-private-character-evidence/pilot-character-reading-blocks.jsonl \
  --speaker-overrides /tmp/night-court-private-speaker-v6/speaker-improvement-overrides.jsonl \
  --database /tmp/night-court-fan-speaker-first.sqlite
```

The baseline 715 role reading blocks remain source-verifiable. In **opt-in** corrected search results, three original UNKNOWN blocks are replaced by four provenance-bound proposed speech segments, **716 indexed role segments**. Thus the fan LLM no longer receives the stale UNKNOWN label *as a second role-index fact for the very same utterance*. The original source text still belongs to the same 751 caption-derived units. This replacement does not claim a speaker identification from photographs or soundtrack.

## Prioritized private review queue for the remaining 261 UNKNOWNs

Generate the priority-sorted source-review packets **after** generating the new v6 readers:

```sh
python 'Night Court/tools/triage_unknown_speakers.py' \
  --speaker-v6-root /tmp/night-court-private-speaker-v6 \
  --output /tmp/night-court-private-speaker-review
```

This produces `speaker-identity-first-review.jsonl` with each unresolved source block's cue, nearby named/unnamed dialogue, source SHA, P0 boundary-risk tags, and S01 approximate padded **SRT** window for listening. No S09 timestamps are fabricated. A separate priority-40 item flags the previously labeled S01 C028 for possible speaker error; it is not counted as an unresolved source unit or silently assigned to Lana. Priority boosts identify difficult multi-voice cues, short interjections, merged transcript paragraph groups, probable syntax continuations, and unidentified clusters. Proximity to a named character is shown for reviewer context, **never treated as proof the unknown person has that name**.

Acceptance against the current source-ledger state: **97 S01 UNKNOWN + 164 S09 UNKNOWN = 261 remaining original source units**; one additional suspected incorrect legacy named label, ranked separately. No automated new role names or independently listened speaker confirmations are claimed. Do not publish this private queue; it contains source transcript text and working character hypotheses.

## Bounded S01 original-soundtrack review clips, with no audio in GitHub

The **speaker** queue may now be turned into a compact plan of source-only listening windows, prioritizing the highest-risk unknowns and coalescing overlapping windows into at most twelve short excerpts by default. It is independent of, and ranked ahead of, the animation/staging pipeline:

```sh
python 'Night Court/tools/plan_speaker_audio_review.py' \
  --queue /tmp/night-court-private-speaker-review/speaker-identity-first-review.jsonl \
  --output /tmp/night-court-private-speaker-listening-plan.json --max-clips 12
```

This first action only creates metadata. When the **real original S01E01 AVI is available locally**, and only if its complete file SHA-256 matches the pinned original media evidence `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962`, extract private 16kHz mono WAVs with:

```sh
python 'Night Court/tools/plan_speaker_audio_review.py' \
  --queue /tmp/night-court-private-speaker-review/speaker-identity-first-review.jsonl \
  --output /tmp/night-court-private-speaker-listening-plan.json \
  --original-avi /private/media/Night-Court-S01E01-original.avi \
  --audio-output /private/night-court/speaker-listening-wavs
```

**No original media** is downloaded by this new tool, its output is private local only, and no CI action here extracts, retains, uploads or prints television audio. Every WAV is a **candidate listening window, not acoustic speaker authentication**. The S01 subtitle timings are approximate reference points, not independently synchronized speech alignments, and may be wrong for a source edition. The untimed S09 original is explicitly deferred until a defensible original-audio/text alignment is established. The separate C028 potentially wrong legacy role is also deferred to its original cue locator until it receives an actual time/shot resolution.

This planner may reuse a verified original local media checkout from a trusted source job without another full-episode download, once available. Only a later human or validated diarization/voice pass can turn these clips into confirmed named speakers. Keep all media, ephemeral WAVs, thumbnails and acoustic voice embeddings outside GitHub and public CI artifacts.

## Next mandatory work

1. **Rank and review the remaining 261 unknown original units.** Prioritize S01 and S09 dialogues with multi-voice cue boundaries, short replies, adjacent named turns, repeated speaker/character quotes, and potentially incorrect already-named voices. A false Dan/Harry/Bull/Roz assignment is at least as damaging as an UNKNOWN.
2. **Use episode-character-attributed external quotes and full scene context first.** Provenanced quote matches can give fast candidate character anchors; do not equate quote/caption shared text with a second independent voice witness. If quote wording diverges, explicitly distinguish lexical match from scene-context candidate.
3. **Consume original sound/film in short context windows around unresolved turns.** Run anonymous voice clustering across uninterrupted scenes, use confirmed audiovisual character labels as anchors, then resolve the nearby unknown turns; use long-enough clips to avoid 1-word/overlap confusion. For untimed S09, align candidate original dialogue sequence to ASR only as a **proposed** location; do not manufacture source caption timestamps.
4. **Record independent speaker-identity dispositions**, distinguish audio/visual reviewed versus quote/context-inferred, and keep old source cue evidence and alternatives. Do not burn GPU on whole-episode video models when a targeted listen or a trusted existing character-quote anchor resolves the issue.
5. **Block the next layer of tone/physical enrichment** on these pilots until the high-impact character confusion and missed turn switches are dealt with. Archive-level 0/193 audiovisual verification remains a separate stringent release criterion.

No claim of a source-listened blind P1 accuracy measure or an independently confirmed new named speaker is made by this work.

## Larger P1 textual candidate pass: 583/751, 168 UNKNOWN (not AV verified)

[Source-ref-anchored editorial candidate ledger](research/pilot-contextual-speaker-proposals-v1.json) now covers **90 additional original speaking blocks comprising 93 original cue units**, after the three external-quote proposals from v6. These are **contextual name hypotheses** sourced from neighboring drama, character address and explicit episode quotes, *not independently heard voices*. C172.1 was corrected from a mistaken Lana hypothesis to Harry after checking the season-specific [Wikiquote original-episode quotation](https://en.wikiquote.org/wiki/Night_Court_(season_1)). C137.1, previously unidentified, is source-attributed to Lana by the same page. **Revision v7 source-level totals: 583 provisionally named, 168 unknown, zero newly independently confirmed by soundtrack.**

The corrected v7 source-first manuscript contains all 751 original subtitle-derived speaking units, with **716 editorial reading segments** after the previously restored S09 C034.1 internal two-voice turn. Crucially, the v7 manuscript is a *speakers-first* text document and does not pretend to reproduce v5 picture-based stage description. V5 remains available separately. The private v7 complete readers, role source evidence and cryptographic digest manifest are regenerated locally, not committed as bulk dialogue.

```sh
python 'Night Court/tools/build_contextual_speaker_reader_v7.py' \
  --v6 /tmp/night-court-private-speaker-v6 \
  --output /tmp/night-court-private-context-speaker-v7

python 'Night Court/tools/export_fan_retrieval_chunks.py' \
  --speaker-v7-root /tmp/night-court-private-context-speaker-v7 \
  --output /tmp/night-court-private-fan-speaker-v7

python 'Night Court/tools/fan_sqlite_index.py' build \
  --corpus /tmp/night-court-private-fan-speaker-v7/fan-retrieval-chunks.jsonl \
  --cards /tmp/night-court-private-fan-beats/pilot-fan-beat-cards.jsonl \
  --roles /tmp/night-court-private-character-evidence/pilot-character-reading-blocks.jsonl \
  --context-roles /tmp/night-court-private-context-speaker-v7/pilot-provisional-context-character-reads.jsonl \
  --database /tmp/night-court-private-fan-speaker-v7.sqlite
```

The updated private FTS index checks the SHA of the entire v7 source-role register and the exact unchanged original cue text for *every* reading block. It permits only one known original speaker split (S09 C034.1); it forbids changing already attributed original speaking units, losing source paragraphs or claiming audio verification. The resulting character retrieval evidence no longer contradicts its speaker-first script view with obsolete UNKNOWN labels at the 93 new candidate cue locations.

**Next highest ROI for approaching 751 accurate names:** acquire and align the actual original production scripts. A [1984 pilot screenplay listing at Scrybe](https://scrybe.to/resources/scripts/night-court-s01e01-all-you-need-is-love-script) shows a 54-page file, though login with verified email is required and edition must be checked. [Hollywood Script Shop](https://hollywoodscriptshop.com/television-scripts-n/) identifies the original pilot by its episode title, and [Scriptfly](https://scriptfly.com/searchpage/resultpage.php) lists both 'NIGHT COURT - Pilot' and 'NIGHT COURT - Ps Do I Know You?' for purchase. The user has not supplied those script bytes, so we **cannot claim character headings from them**. Production dialogue may differ from aired dialogue; align scene, sequence and distinctive phrases against the held caption source rather than replacing the real broadcast witnesses or automatically assigning every character on proximity. These source editions could be far more productive than multiplying LLM context guesses.

The first incorrect C172 candidate illustrates the central caution: getting to 751 through plausible but unverified labels would be damaging to a trustworthy fan persona. The remaining 168 are not solved by adding more confidence adjectives. Continue targeted source film listening and verified production script acquisition/ordered alignment; require separate evidence for actual speech identity.

## Direct route to better character evidence: actual production teleplays

Existing held subtitles often contain no speaker names. Instead of extending speculative context labels until the count reaches 751, obtain an **original 1984–1992 production script with explicit speaker headings**, align it to the *held aired dialogue*, identify revision/disagreement, then confirm uncertain material against real episode audio. Production manuscripts are another lexical/editorial witness and may include unused scenes, revised dialogue or cuts.

Public source leads as of 2026-10-25:
- [Hollywood Script Shop: original Night Court pilot specifically "pilot (all you need is love)"](https://hollywoodscriptshop.com/television-scripts-n/) within an original-series catalog.
- [Scriptfly: Night Court original "Pilot" and "Ps Do I Know You?" script listings](https://scriptfly.com/searchpage/resultpage.php), priced at approximately US $19.95 and US $14.95 respectively when checked; pricing and edition need rechecking before purchase.
- [Scrybe: "All You Need is Love" 54-page script listing](https://scrybe.to/resources/scripts/night-court-s01e01-all-you-need-is-love-script) requires an account with verified email. Its page also includes a conflicting **2023 pilot** episode association; **do not ingest without inspecting actual title page, copyright, cast and episode identity**. This may be a metadata collision rather than the correct 1984 production teleplay.

No owner purchase, private downloads, account signup or authentic screenplay content access has happened in this pass. Do not misrepresent these listings as obtained evidence.

A private, no-network plain-text screenplay-to-captions matcher is implemented at `tools/align_private_production_script.py`. With an authorized local **plain text** export of a screenplay which has conventional uppercase character headings:

```sh
python 'Night Court/tools/align_private_production_script.py' \
  --episode S01E01 \
  --script-text /private/Night-Court-1984-pilot-teleplay.txt \
  --output /private/night-court-pilot-script-lexical-speaker-proposals.json

python 'Night Court/tools/align_private_production_script.py' \
  --episode S09E19 \
  --script-text /private/Night-Court-1992-s09e19-teleplay.txt \
  --output /private/night-court-s09-teleplay-role-proposals.json
```

The tool maps known original-series character headings, scores nearby consecutive cue-parts in source order, rejects ambiguous repeated quote lines and unrelated revised dialogue, and **separately reports a possible contradiction with an already-named source unit**. Only source fingerprints, short locator IDs and role proposals are emitted, not the complete screenplay. No publication of privately acquired teleplay contents, and **zero automatic promotion to audio-certified dialogue**. Use its output to prioritize real soundtrack listens and to avoid falsely forcing a line from a production draft onto a different final broadcast performance. A PDF would need to be extracted to text separately before running this tool.

## First original-soundtrack voice comparison: 56/75 held-out role matches

A trusted-source, main-checked [original S01E01 acoustic identity proposal run](https://github.com/gamesbyian/general-purpose/actions/runs/40252708569) (invoked through [owner trigger PR #448](https://github.com/gamesbyian/general-purpose/pull/448)) completed the actual exact source AVI + original SRT cue voice embeddings with **Resemblyzer 0.1.4** locally. It used eight previously provisionally labeled voice reference roles, and never retained soundtrack, video, face data, model voiceprints or transcript text in its artifact. Its lightweight numeric report SHA-256 is `9729ed2882df04fcdc3706a491875e836873d334f5121be8d65809833e4a25e1`.

**Measured results:** 75 held-out provisionally known voice samples, **56/75 (74.67%)** assigned to their preexisting editorial role. This is a useful acoustic *consistency* measure and a very real error rate. It is emphatically **not** an actor identity true-label validation. Forty-two original previously unknown caption cues had enough appropriate audio for acoustic comparison; conservative cosine and role-margin filters generated only **six voice-model role proposals**, **36 abstentions**. The other original UNKNOWN cues are shorter, multivoice, otherwise unusable or excluded by the original-caption timing safety contract.

The six source cue numerical proposals:
- C074.1 → **Dan Fielding** (cosine 0.83307, margin 0.11950)
- C095.1 → **Dan Fielding** (0.87293, 0.09851)
- C097.1 → **Harry Stone** (0.85095, 0.15045), *already provisionally assigned from narrative context*
- C161.1 → **Harry Stone** (0.87834, 0.11500)
- C172.1 → **Harry Stone** (0.82920, 0.09943), *already assigned after published quote correction*
- C179.1 → **Lana Wagner** (0.84246, 0.13790)

Therefore **four** original source units formerly UNKNOWN in v7 receive **additional independent acoustic-model-supported provisional character names**, and two earlier textual assignments receive acoustic agreement evidence. The conservative new *working* speaker-reader count becomes **587 provisionally named / 164 UNKNOWN original cue units** once the audited `tools/build_original_audio_speaker_reader_v8.py` overlay is regenerated. **Zero** roles were independently verified by an actual actor-recognition/audio/video reviewer; the voice comparison uses preexisting provisional character labels as its reference seeds, and one wrong seed could corrupt another name. We must not claim 587 truly identified humans.

Source-only evidence ledger: [numeric original voice findings](research/s01e01-source-voice-acoustic-proposals-v1.json). Rebuild the speaker reader locally, after the v7 reader:

```sh
python 'Night Court/tools/build_original_audio_speaker_reader_v8.py' \
  --v7 /tmp/night-court-private-context-speaker-v7 \
  --output /tmp/night-court-private-source-audio-speaker-v8

python 'Night Court/tools/export_fan_retrieval_chunks.py' \
  --speaker-v8-root /tmp/night-court-private-source-audio-speaker-v8 \
  --output /tmp/night-court-private-fan-speaker-v8

python 'Night Court/tools/fan_sqlite_index.py' build \
  --corpus /tmp/night-court-private-fan-speaker-v8/fan-retrieval-chunks.jsonl \
  --cards /tmp/night-court-fan-beats/pilot-fan-beat-cards.jsonl \
  --roles /tmp/night-court-private-character-evidence/pilot-character-reading-blocks.jsonl \
  --acoustic-context-roles /tmp/night-court-private-source-audio-speaker-v8/pilot-original-acoustic-speaker-reads.jsonl \
  --database /tmp/night-court-private-fan-audio-v8.sqlite
```

Do not upload private WAVs, voiceprints or original video to public GitHub. Keep the zero-audio-verified status until actual original-film reviewer evidence. A follow-up should inspect the four new cue windows with the original picture and audio, compare anonymous voices against known characters, and correct source latency / overlapped laughter risk before accepting them. S09E19 still needs defensible original source paragraph-to-audio alignment to unlock the larger remaining UNKNOWN pool.

## More missing *speaker turns* inside held source caption units

An explicit [mixed-voice P0 review locator](research/probable-internal-speaker-switches-v1.json) now records **12 additional exact-source probable voice-switch locations**: one in timed S01E01 and eleven in untimed S09E19. These are not twelve newly accepted splits, and the original 751 caption-derived source-unit count is unchanged. Named identities remain unknown until original source audiovisual review. The read-only validator `tools/triage_internal_speaker_switches.py` verifies the original episode/cue SHA and single unique in-cue lexical boundary, preserves every source character, and generates private two-part review excerpts with no guessed named characters or untimed source clock.

Known high-impact problems include a speaker reply buried after a question in S09 C102, a named greeting at C127, the change from Dan to Harry implied within C146, competing dialogue within C206/C209/C211, rapid bar scene exchanges at C271/C284, and the identity-reveal farce C290/C291. S01 C219 also embeds a short reply behind a dash. Some of those may include **more than two** speaking turns; the proposal is a targeted audit starting point rather than authoritative segmentation. The established S09 C034.1 split remains tracked separately, already represented in the provisional v6–v8 scripts.

```sh
python 'Night Court/tools/triage_internal_speaker_switches.py' \
  --output /tmp/night-court-private-mixed-voice-review
```

Use candidate S09 original-audio ASR paragraph windows from the actual [S09 soundtrack alignment run](https://github.com/gamesbyian/general-purpose/actions/runs/40253914693), where available, to locate excerpts. That run placed **231/347** previously untimed original paragraphs into **unverified** original-audio windows, matching **1,803** original source words, and left 116 unlocated; those proposed *audio* positions are NOT original subtitle timecodes and do not establish who performed a line. Preserve the frozen original source text and ask an actual soundtrack reviewer to approve every source turn split and actor identity.

## Current 164-source-unit review queue, combining original S09 audio leads

After the v8 source-first private character evidence is generated (**587 provisionally named / 164 original-source UNKNOWN**), `tools/plan_next_speaker_review_v9.py` produces the current **P0/P1 working queue**, instead of repeating older 261-UNKNOWN baseline packets. It joins:

- Every still-unknown exact original source caption-part ID and SHA from the private v8 reader.
- Real S01 timed SRT cue neighborhoods (not verified movie synchronization).
- Real S09 [source-AVI audio-alignment report #40253914693](https://github.com/gamesbyian/general-purpose/actions/runs/40253914693), limited to its 231 **UNVERIFIED** audio-window suggestions, with original untimed paragraphs unchanged.
- Source-cue-exact suspected internal voice-switch flags and adjacent provisionally named speech, provided for review context, **not** evidence that a nearby name belongs to the unknown speaker.

```sh
python 'Night Court/tools/plan_next_speaker_review_v9.py' \
  --speaker-v8-root /tmp/night-court-private-source-audio-speaker-v8 \
  --s09-original-audio-locator /private/night-court-s09-original-audio-paragraph-locators.json \
  --output /private/night-court-review-next-164
```

The S09 numeric-only report is available through the owner-trusted private Actions artifact on the linked original alignment run (artifact 12622255206, original data SHA256 `febac6aff2cb01ee36ac1c44b592317011d655628ede2eb83981b98201e3accc`). The script fails closed on changed report bytes, original S09 episode SHA, v8 source-role manifest, or invented S09 original source timecodes; source lines stay out of logs and GitHub files. The output is a local review queue with no automatic P1 name acceptance.

### First original S09 voice comparison (real audio, **no qualified new labels**)

[Original S09 role-acoustic run #40256897493](https://github.com/gamesbyian/general-purpose/actions/runs/40256897493) processed **39 currently UNKNOWN** original paragraph audio windows, but its strict clean-original-source screening left only **two usable role-reference speakers**: **Christine Sullivan (8)** and **Roz Russell (7)**. Those 15 pre-labeled samples were 15/15 correctly classified by leave-one-out comparison **between just those two**. It is **not** a 100% cast voice recognition result. The model correctly declined to propose a new name because its minimum three distinct voice roles / 20 reference examples conditions were unsatisfied; zero original film actor identity independently confirmed. Thus v8 **remains 587/751 named proposals and 164 source unit UNKNOWN** after that run. Numeric original 1992 soundtrack evidence only was retained in the private 7-day action artifact; no original audio or speaker voiceprints were uploaded.

**Next work:** broaden original S09 voice reference bank by joining actual audio candidate intervals to the *latest source-checked v8 original role proposals* (rather than v4 pilot roles) and confirm whether more characters meet minimum source-lexical quality. If a fairer speaker reference bank still lacks sufficient distinct characters, don't run the same model repeatedly hoping to reach 751; try less fragmented source windows, paired short contextual audition of actual source film, or a locally obtained original teleplay with proper scene/role headers. Remember two people often share a paragraph. A character may never have a sufficient uninterrupted audio sample for a voiceprint, in which case image+dialogue context are needed.

## Second original-S09 soundtrack speaker experiment: 18/26 heldout, three proposed names and one quarantined

The source-verified [S09 original soundtrack v8-reference experiment](https://github.com/gamesbyian/general-purpose/actions/runs/40257892582) ran to completion on October 26 with four **provisionally** named reference voice groups (Christine 10, Roz 7, Dan 5, Mac 4), not just the original binary Christine/Roz bank. It found 28 original previously UNKNOWN paragraph audio samples, of which 4 passed the fixed local model's cosine and margin thresholds. Leave-one-out recovery was **18/26 (69.23%)**, with Mac only **1/4** and Dan **2/5** versus Christine **8/10** and Roz **7/7**. That is a modest accuracy result for the provisional seed labels, not reliable all-cast identity or permission to name every nearby character. The candidate original film AV and text alignments were not independently human reviewed.

The complete hash-only source-model numerical output is SHA256 `656ee523b6a2996c3be9a8adf9bdf59a1086226e613d7b3000f38b30bb5657f8`; [source-linked result ledger](research/s09-original-source-acoustic-speaker-proposals-v1.json) retains only the four source cue IDs, proposed roles, measured cosine/margin and editorial reasons, without copyrighted dialogue/audio/voiceprints. **Three** support *working-reader-only* name hypotheses: S09 C046 and C057 **Christine Sullivan**, C267 **Roz Russell**. The latter also appears to be a same-speaker continuation of C266, which needs a future P0 check.

**The fourth, C129, is deliberately quarantined and remains UNKNOWN.** The line concerns recording the wrong campaign advertisement, and a different character absent from the reference bank may actually be talking. A good similarity to Christine when Harry/Bull/others are absent from the acoustic candidate set is not enough. A suspicious confident model label is worse than a clear UNKNOWN for our fan-LLM screenplay goal.

The reproducible private [v9 working speaker-first reader](tools/build_s09_source_acoustic_speaker_reader_v9.py) incorporates only these three provisional names, retaining all held original source caption parts and source hashes, the known C034 two-voice split, and every original S09 paragraph's absent source timestamp. **Provisional total becomes 590 named / 161 UNKNOWN of the 751 original cue-derived units, while newly independently audio-verified actor identities remain 0.** We have not reduced the audiovisual verification gate from 0/193 by constructing this reader. The private retrieval export and SQLite role index can both use the same v9 source-evidence layer, so C129 stays UNKNOWN rather than being mislabeled in a secondary index.

```sh
python 'Night Court/tools/build_s09_source_acoustic_speaker_reader_v9.py' \
  --current-v8 /tmp/night-court-private-source-audio-speaker-v8 \
  --output /tmp/night-court-private-source-audio-speaker-v9

python 'Night Court/tools/export_fan_retrieval_chunks.py' \
  --speaker-v9-root /tmp/night-court-private-source-audio-speaker-v9 \
  --output /tmp/night-court-private-fan-speaker-v9
```

The next useful acoustic challenge should include **out-of-set negative references** (named character voices the model cannot train on) to estimate how often it confidently mistakes Harry/Bull/guest voices for Christine, Roz, Dan or Mac. Prefer original-local sound/film listening or correctly versioned production scripts for ambiguous cameo roles, and do not use repeated model agreement to certify a character name.

## Current working review queue: 161 unidentified original units (v9 truth)

[Source-first generator](tools/build_s09_source_acoustic_speaker_reader_v9.py) now conservatively emits the 590-named / 161-UNKNOWN provisional speaker evidence ledger, and C129 remains deliberately UNKNOWN despite its S09 acoustic out-of-set suspicion. The previous **164-unit** queue is a historical v8 snapshot, **not** the current P0/P1 work assignment.

Run the same lossless and SHA-bound review planner with `--speaker-v9-root` rather than an outdated v8 reader:

```sh
python 'Night Court/tools/plan_next_speaker_review_v9.py' \
  --speaker-v9-root /tmp/night-court-private-source-audio-speaker-v9 \
  --s09-original-audio-locator /private/night-court-s09-original-audio-paragraph-locators.json \
  --output /private/night-court-original-speaker-next-161
```

It produces `remaining-161-speaker-review.jsonl` and a summary in that **private outside-repository** directory. The full preserved S01 SRT cue offsets and 231 candidate original-S09 soundtrack audio positions are review *pointers* only. A newly ranked **P0 same-speaker continuation question** involves S09 C266→C267: the first paragraph's incomplete sentence flows grammatically into the next, which is provisionally attributed to Roz via an original soundtrack embedding result. The queue flags that as a candidate *one continuing speaking turn*, but **does not automatically label C266 as Roz or count it resolved**, because actual original voice identity and possible interruption remain unreviewed. The next source reviewer can check the scene and then apply a proper source-preserving same-turn merge, potentially resolving a missing name with one source operation.

All 161 unknown source units, duplicate/invalid original role parts, original caption text, original S09 untimed status and audio-alignment report exact digests are covered by the lightweight real-source non-media CI contract. The original 751 source unit denominator is fixed; true actor performance speaking-turn count can differ after P0 adjudication.

## October 26 current next-step handoff: v10 speaker turn model and source-mixed exchanges

The authoritative latest **reversible original-caption source reader** is `tools/build_s09_source_turns_v10.py`, now with **591 provisionally named original cue units, 160 UNKNOWN cue units, and 715 proposed reader speaking blocks**. In S09 the original source C266/C267 sentence is reunited into one provisional Roz turn (both original source cue IDs and the exact words are preserved). **No human or independently AV-confirmed speaker or P0 turn acceptance was added.** See merged [source-first v10 PR #461](https://github.com/gamesbyian/general-purpose/pull/461).

Use the updated `tools/plan_next_speaker_review_v9.py` program with `--speaker-v10-root` on the latest **private** reader and SHA-pinned 231-paragraph S09 original-audio candidate locator to produce `remaining-160-speaker-review.jsonl`. Older v8 and v9 input options remain for reproducible past counts, **not the current assignment**. The failed identity set is no longer 164, 161 or 264. The latest queue does not try to identify mixed-voice source paragraphs from a neighboring named speaker.

The P0 original-source possible internal-voice-switch review list now includes **16 source-exact candidates**: the original 12 and S09 C188, C189, C190, C191. These four contiguous S09 paragraphs have a dense unpunctuated exchange about Roz meeting her correspondent, containing multiple apparent comments/questions/replies in individual source cues. The new source-word split hints are reversible and exact; **none is approved as a true original-audio turn boundary and none is automatically attributed to Roz/Christine/Harry**. These cues remain expressly ineligible as naive single-voice acoustic reference samples. S09 C189/C190 can cross both caption and speaker boundaries; word-continuation logic alone is not speaker evidence.

Lightweight, no-secret real-source CI reconstructs the frozen v6→v10 private corpus, obtains the original earlier S09 numerical audio-locator artifact, proves 591/160 source-unit accounting and all 16 candidate P0 review positions, and checks that the disputed out-of-reference-bank C129 speaker remains UNKNOWN. This is the next stable entrypoint for first-priority source-audio review rather than expensive unspecific multimodal descriptions.

## Provisional rapid Roz/Christine dialogue reconstruction: v11 source spans

An additional high-value P0 source-text anomaly is the five-paragraph S09 C188–C192 exchange: the original held transcript lacks punctuation and places multiple apparent responses in the same paragraph. A scene-context *working hypothesis* separates these five frozen original S09 paragraphs into **six mixed/continuing speaker turns**, using **exact source Unicode character offsets**, source SHA-256 and reversible multi-paragraph grouping. The scene characters are proposed as Roz Russell and Christine Sullivan from text and surrounding scene context, **not independently recognized from the original soundtrack**.

The new `tools/build_s09_mixed_voice_turns_v11.py` requires the validated current v10 exact-source reader, checks original cue role and untimed status, partitions each of C188–C192 without omitting **even whitespace**, rejects repeated or out-of-order spans, and preserves all non-target reading records unchanged. The four previously wholly UNKNOWN source paragraphs C188, C189, C191 and C192 gain **provisional contextual roles**, while C190 is correctly recognized as a mixed-character cue rather than the earlier erroneous whole-cue Christine label. Original C190's roles are now two characters, not one. The five old reader blocks become six new provisional blocks: **716 proposed reader speaking turns** across both pilots, **595 original cue units with provisional named speaker coverage / 156 still UNKNOWN of 751**. The held original 347 S09 source paragraphs are STILL UNTImED; original film/audio character recognition and P0 actor boundaries independently verified here remain **zero**.

These six speaker-turn proposals are useful screenplay context, but some may need splitting/reassigning after actual moving-video and soundtrack inspection. No guessed roles have been promoted to certified performers. The private v11 full-script reader is selectable for all 193-episode lexical retrieval and FTS indexing with the matched v9→v10→v11 source-role evidence overlays. The exact-part-text hashes, original source cue hashes, original JSON role record hashes and no-AV-acceptance gates all run in CI. A future verified original soundtrack pass should first check C188–C192 as a contiguous human-performed exchange, rather than training a single voice on those multi-character original captions.

```sh
python 'Night Court/tools/build_s09_mixed_voice_turns_v11.py' \
  --v10 /tmp/night-court-private-speaker-turns-v10 \
  --output /tmp/night-court-private-speaker-turns-v11

python 'Night Court/tools/export_fan_retrieval_chunks.py' \
  --speaker-v11-root /tmp/night-court-private-speaker-turns-v11 \
  --output /tmp/night-court-private-fan-speaker-v11
```

## Working v12: source dialogue gives character roles before another model is necessary

The user-directed emphasis on actual useful named scripts permits **clearly editorial, non-AV-certified speaker names** when the episode itself supplies unusually strong character evidence. The [S09 high-context original cue ledger](research/s09-high-context-speaker-proposals-v12.json) records 12 tightly scoped source-reading blocks, spanning 15 original previously UNKNOWN source cue units. Every proposed role has a source-internal quote anchor, explicit reason, frozen original transcript SHA and zero independent soundtrack-voice/actor confirmation.

Especially useful source-continuity clues include Bull's pledge of his entire piggy bank followed by his own $40,000 reveal, the named Harriet campaign endorsement followed by Mac addressing her by name, Dan talking to Harry about the court safe and Harry's desire for Houdini-related memorabilia, and the real Alex's reply to Roz followed by their mutual apologies. The chosen original blocks are C091, C092, C099, C125, C126, C134–C135, C268, C298, C299, C335, C336–C337 and C340–C341. No uncertain multi-voice cue such as C129/C146/C189/C211/C271/C284 was forced to a single character, and the earlier disproven high-similarity C129 acoustic Christine hypothesis remains explicitly UNKNOWN.

The deterministic private [v12 source-backed speaker reader](tools/build_s09_high_context_speaker_reader_v12.py) only replaces **unidentified original-source reading blocks**, rejects replacing an existing named role, and keeps every original source cue word, original cue membership and S09 untimed status. It never changes the previously established P0 source spans or uses an unverified actor voice as fact. Across both pilots the new **working hypothesis coverage would be 610 provisionally named / 141 UNKNOWN original cue units, 716 provisional reading-turn blocks**. Until original audiovisual inspection confirms the source-to-performer attribution, the accepted independent actor-identity count is still zero. Those improved reading names flow to the same private 193-episode LLM retrieval and SQLite character index, not into the frozen original caption witness or tracked v5 staging manuscript.

```sh
python 'Night Court/tools/build_s09_high_context_speaker_reader_v12.py' \
  --v11 /tmp/night-court-private-speaker-turns-v11 \
  --output /tmp/night-court-private-speaker-context-v12

python 'Night Court/tools/export_fan_retrieval_chunks.py' \
  --speaker-v12-root /tmp/night-court-private-speaker-context-v12 \
  --output /tmp/night-court-private-fan-speaker-v12
```

This is **NOT** evidence that twelve new voices have been heard or verified. The named-source-unit denominator is not the number of true performed turns after all intra-cue speaker splits, and the full 0/193 independent audiovisual episode certifications remain unaffected.

## Original S09 explicit actor handoffs, source-first v13

The v12 contextual reader provides 610 provisional names but still treats some original paragraphs containing more than one character's lines as single UNKNOWN turns. Three P0 split-and-join operations can be reconstructed directly from source dialogue and **named addressees**, with each original source character retained under an exact Unicode offset:

- **C126→C127:** Harriet's Congress endorsement continues into the first two characters of C127, after which Mac clearly thanks **Harriet** and comments on advertising. Join the Harriet sentence across C126/C127 and split Mac into his own following speaking turn.
- **C146:** Dan offers to pull Harry's loose tooth; **Harry replies thanking Dan** in the same held source paragraph. Two proposed characters, two exact source text fragments.
- **C284:** Alex asks for his interlocutor's name, and **Roz abruptly says she's leaving** in the same source paragraph. Two proposed characters, two exact source text fragments.

The human/film acoustic adjudication remains **pending**, despite unusually strong textual turn and character evidence. All six newly rendered performance/actor labels are **editable source-context hypotheses**, not certified film turns or audiovisual cast IDs. [Explicit source-turn proposals](research/s09-explicit-address-speaker-turns-v13.json) preserve the immutability of the original 347 UNTIMED S09 witness paragraphs. The deterministic [v13 private source reader](tools/build_s09_explicit_handoff_turns_v13.py) reproduces every source cue's original Unicode string exactly and refuses any modified prior named role, missing original cue, duplicated/missing source characters or fake AV acceptance.

This gives **613 provisional named / 138 UNKNOWN of 751 original cue-derived source units** and **718 proposed true-speaking-turn reading blocks** across the two pilots. That higher turn-block count reflects editorial source span regrouping, **not independent verification of a new actor or one-to-one equivalence between subtitle cues and performed turns**. All other prior source and v12 character roles remain unchanged. The all-193 episode fan retrieval and private SQLite index use the latest v13 source-first manuscript and consistent role evidence, while existing frozen v5 rich staged scripts remain untouched.

## Stop rebuilding per-version role readers: generic source-checked speaker amendments

After v13 established the correct reversible mixed-caption turn structure, repeatedly authoring a fresh custom Python reader for each new group of straightforward character assignments is unnecessary overhead. The new [append-only source-role amendment ledger](research/source-role-amendments-v1.json) and generic [apply_source_role_amendments.py](tools/apply_source_role_amendments.py) support any number of small subsequent **UNKNOWN→working-name** patches, without new source-reader code per role. Each ledger record names the exact episode, original cue-part IDs, original source SHA, previously unidentified reading reference, matching source phrase, proposed character role, and the natural-language reason why it is plausible. The engine refuses duplicated original source parts, overwriting a known actor, editing source words/cue memberships, adding S09 subtitle clocks, or claiming false original sound/film verification. Future agents can extend the JSON amendments and rerun the existing read-only generator/tests; P0 genuine split/merge corrections still demand their own source-span review.

The first six append-only source proposals all belong to the **safe-room informant explicitly called Paul** at the end of the conversation. S09 C112 recognizes Judge Grimm's safe, C114/C115 recount the corruption/blackmail story, C117/C118 continue that historical tale, and C122 bids goodnight, immediately before C123/C124 answer **Paul** by name. These are six **guest character dialogue hypotheses** grounded in specific source turns and the named farewell, **not verified performer/voice claims**. Because the source transcript leaves the speaker unnamed and the guest may have no credited character listing, PAUL is a dialogue character label, not an actor identification.

The private patched source-first working script would have **619 source units provisionally named / 132 UNKNOWN out of the same immutable 751**, while preserving 718 proposed performance-reading blocks and **zero** independently original-A/V-verified actor identities. The generic patched reader can be selected into the full-193 source-dialogue LLM retrieval and the SQLite fan-evidence index, without exposing original episode bulk dialogue in Git/Actions logs.

```sh
python 'Night Court/tools/apply_source_role_amendments.py' \
  --v13 /tmp/night-court-private-speaker-turns-v13 \
  --output /tmp/night-court-private-source-role-patches

python 'Night Court/tools/export_fan_retrieval_chunks.py' \
  --speaker-patch-root /tmp/night-court-private-source-role-patches \
  --output /tmp/night-court-private-fan-speaker-patched
```
