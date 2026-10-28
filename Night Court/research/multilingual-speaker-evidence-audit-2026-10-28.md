# Multilingual speaker-attribution evidence audit (28 October 2026)

**Scope:** original 1984–1992 *Night Court*, with immediate emphasis on S01E01 and S09E19. **Source constraints:** the owner-held video library is AVI without embedded subtitles. English subtitles are held separately in the research corpus; therefore the relevant search is for **standalone, independently created multilingual captions or transcripts with speaker labels**, not subtitles extracted from the AVI collection.

## Finding and acceptance

**No qualifying standalone non-English episode file containing independently verified per-line speaker attribution was found in this search.** A downloadable translation is not necessarily an independent source; a German dubbing cast list identifies a character in an episode but cannot independently assign a spoken sentence. Do not increment manuscript speaker-certification counts or create automatic named turns from any source in this audit.

Evidence classes:
- **A: independently verified per-turn speaker labels:** none found.
- **B: independent episode-specific character/cast identities:** confirmed German dubbing database; useful as a candidate roster only.
- **C: original-language dialogue subtitles without explicit attribution:** existing English SRTs and searchable English subtitle pages; these can still establish dialogue text and dash-delimited simultaneous/mixed turns.
- **D: translations derived from pre-existing English caption files:** verified on Subtitle Cat; **same evidence family**, no new speaker witness. Translation may even lose original dash boundaries.
- **E: language advertised as a translation-button option:** not a downloadable subtitle and not evidence that a file exists.

## Direct source checks

| Source / exact pointer | Verified observation | Value and limitations |
| --- | --- | --- |
| [Subtitle Cat S01E01 original-series DVD x265 Panda English upload](https://www.subtitlecat.com/subs/1079/Night%20Court%20%281984%29%20-%20S01E01%20-%20All%20You%20Need%20Is%20Love%20%28480p%20DVD%20x265%20Panda%29.eng.html) | English source and *Download* choices for Afrikaans, Greek, Hebrew, Spanish and English; French/German/Italian are *Translate* buttons only. The displayed English original is dialogue with dash-marked mixed utterances, not consistent `HARRY:`-style labeling. | Specific S01E01 discovery pointers, but site's upload index explicitly identifies source as English. **Not independent speaker attribution.** |
| [Subtitle Cat upload index](https://subtitlecat.com/list_page.php?from=1665100) | Original-series S01E01 through S01E13 uploaded in sequence on 2025-05-07 and explicitly tagged “translated from English”; the pilot upload is at 14:11:37. | Strong provenance evidence of common source family; neither quantity of languages nor number of downloads represents independent speaker witnesses. |
| [Subtitle Cat S02E13](https://subtitlecat.com/subs/1080/Night%20Court%20%281984%29%20-%20S02E13%20-%20Dans%20Parents%20%28480p%20DVD%20x265%20Panda%29.eng.html) | Greek, Portuguese (Brazil) and Spanish downloads beside English original. | Translation derivatives; no verified independent labels. |
| [Subtitle Cat S03E01](https://www.subtitlecat.com/subs/1081/Night%20Court%20%281984%29%20-%20S03E01%20-%20Hello%2C%20Goodbye%20%28480p%20DVD%20x265%20Panda%29.eng.html) | Greek download beside English original; most other languages are translation-button options. | Not a new attributed transcript. |
| [Subtitle Cat S04E01](https://www.subtitlecat.com/subs/1120/night_court_s04e01_the_next_voice_you_hear.html) | Dutch and English downloadable; displayed original English transcript is unlabelled and appears less clean than the DVD-format English source; source origin of Dutch not independently established. | Dutch track needs origin/byte-level inspection; must **not** be accepted as independent because a download button exists. |
| [SUBDL original-series season 1](https://subdl.com/subtitle/sd1301097/night-court/first-season) | Live index advertises one English DVD-rip pack (`Night.Court.S01.iNTERNAL.DVDRip.XviD-RUNNER`), and no foreign-language submission in the displayed list. | Separate provider check, no qualifying multilingual witness on visible index. |
| [SUBDL original-series season 9](https://subdl.com/subtitle/sd1301097/night-court/ninth-season) | Explicitly reports “No Subtitles Found.” | Negative result for S09E19 **on this provider only**, not proof that no other provider has captions. |
| [Deutsche Synchronkartei, original Night Court](https://www.synchronkartei.de/serie/14048) | German dubbing index lists 37 speaking roles. Specifically marks S01E01 for Carla B. (Rita Taggart), Louise Kerr (Peggy McCay), Phil Kerr (Joseph Perry), and a painter (actor unknown); main recurring roles have no episode number. It also notes its credits are not guaranteed complete/correct. | **Independent episode-specific guest-character candidate evidence**, not a speaker transcript. Cross-check cast/credit identities before adopting, especially inconsistent episode metadata. There is no S09E19-specific guest role in its visible index. |
| [Kalamazoo Public Library's season-one DVD catalogue](https://www.kpl.gov/catalog/item/?i=ent%3A%2F%2FSD_ILS%2F0%2FSD_ILS%3A1956409) | Records optional English, French and Spanish subtitles on the physical first-season DVD. | **Real physical-source language availability**, but this is not a verified separately downloadable SRT and does not establish names in the caption content. The owner-held AVI sources do not carry these streams. |
| [Apple TV original series, Canada](https://tv.apple.com/ca/show/night-court/umc.cmc.3v8igla11dgg4chywljv2og89), [Prime Video season nine](https://www.primevideo.com/-/es_419/detail/0GM6BC07DB0K3OBN2J37OF4HEL) | Current public storefront entries display only English CC, even when interface language is French or Spanish. | Localizing a storefront page is not evidence of translated caption streams. Streaming services are not a verified foreign-language standalone-source route. |

## Episode consequences

- **S01E01:** Four downloadable non-English SRT *translations* exist on Subtitle Cat; there is **no evidence of independent speaker names in them**. Independent German role data provides candidate names (Louise Kerr, Phil Kerr, painter; Carla B. requires further episode reconciliation). A live repository search confirmed all four role concepts (Carla Bouvier, Louise Kerr, Phil Kerr, and PAINTER) **already appear in the latest canonical S01E01 working screenplay**. Consequently, the German listing adds independent **cast corroboration** but **zero genuinely new named character roles** to this pilot, and does not support upgrading provisional P0/P1 turns to accepted.
- **S09E19:** SUBDL season-nine page is empty and the German casting index adds no episode-specific role. No verified independently attributed multilingual source found.
- **Other episodes:** German index covers 37 speaking roles over the series but is sparse. Subtitle Cat translations are generally derivative, even when many languages are downloadable. They may supply corroborating dialogue strings but must not count as cross-source speaker votes.

## Reproducible short-path acquisition and screening procedure

1. **Disambiguate the 1984 original from the 2023 revival** using an original-series episode title, 1984 identifier, show ID or original airing date. Include alternate localized titles, e.g. `Harrys wundersames Strafgericht`, `Tribunal de nuit` and `La Corte Nocturna`.
2. **Target standalone files with likely speaker labeling**: SDH/HI/CC/HoH, `malentendants`, `sordos`, `Hörgeschädigte`, `non udenti`, `[HARRY]`, `DAN:`, `<v Harry>` WebVTT, or ASS/SSA styles. These are search cues, never proof labels are present.
3. **Check source origin BEFORE translation/alignment**: prefer locally authored/non-English original, independently captured television captions or DVD OCR, not sites advertising “translated from English”. Treat machine translations and mirrors as one provenance family.
4. **Inspect original file (when lawfully obtained) before announcing results:** validate episode identity, content language, timing/cue count, speaker-label regex/hit examples, mixed-voice dash syntax, VTT voice tags/ASS styles, track length and whether apparent labels are dialogue/vocatives. Merely seeing `- A - B` marks a boundary, not a character.
5. **Compare with held English source** without modifying immutable `original.srt`: episode/scene match, chronological monotonic alignment, character label provenance, source SHA, source family, one-to-many and multi-speaker handling. Do not invent S09 timestamps or translate back into an English line unless independently aligned.
6. **Admit only new evidence**, as a separate referenced annotation keyed to immutable source cue/turn offsets and a confidence tier. A cast credit restricts candidate speakers; a verified foreign caption explicitly saying `HARRY:` can yield a proposed English speaker anchor after a separate content and timing match. Preserve UNKNOWN and abstain on ambiguity. All AV certification remains independent.
7. **Stop early if source family is duplicate:** one metadata/structure comparison plus targeted cue-label scan per candidate, rather than building a multilingual transcription pipeline whose entire input is machine-translated English.

## Action priority

**Next productive acquisition target:** a separate SDH/CC subtitle text file derived from an original closed-captioned broadcast or from independently sourced physical DVD subtitle streams, rather than further Subtitle Cat translation downloads. In parallel, import the **German episode-specific cast metadata** into a low-trust candidate roster only if it differs from the already-held TVmaze/IMDb episode cast graph. Do not fork a new script-factory workflow merely for this lead.

**Rights:** retain links, factual metadata, results and small evidence examples; don't bulk mirror copyrighted subtitle text into Git. No AVI media bytes or unpublished captions were obtained as part of this audit.
