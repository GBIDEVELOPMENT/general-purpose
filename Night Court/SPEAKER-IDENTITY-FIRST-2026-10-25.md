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
