# S09E19: original 1992 soundtrack speaker comparison with aligned untimed paragraphs

**P0/P1 speaker identity first**, without forcing guesses to fill a desired number.

Actual owner-source [S09 dialogue↔audio run #40253914693](https://github.com/gamesbyian/general-purpose/actions/runs/40253914693) used the exact original AVI `51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649`, source 347 untimed paragraphs SHA `659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2`, and produced **231 original paragraph candidates with source-audio word locations**, 116 still unlocated; 1,803 original words globally lexically corroborated. The entire numeric/hashes-only original output has SHA `febac6aff2cb01ee36ac1c44b592317011d655628ede2eb83981b98201e3accc`. This is a machine-suggested *audio interval*, not a new timestamp on the original caption source.

## P1 implementation

The trusted `tools/compare_s09_original_speaker_embeddings.py` takes that **numeric-only** exact-report artifact (retrieved by an owner-trusted Action from run #40253914693, with SHA checked before any model or media), joins the timed candidate intervals to the already source-SHA checked source original dialogue role ledger, and:
1. Refuses weak lexical matching (at least 72% source paragraph match; at least three shared words) or a clip under 1.5 seconds, because the 100 ms head/tail padding and Resemblyzer's minimal input need speech that actually survives cropping.
2. Excludes known/suspected **multi-voice source paragraphs** such as C034, C102, C127, C146, C206, C211, C271, C290, C291, among others. A paragraph with two character performances is not one actor's voiceprint.
3. Extracts only longer and individually attributed dialogue references from the existing v4 original-episode source-reading ledger, at least 4 examples per character and up to 14 spread across the episode. Their labels **remain editorial proposals**, not source-audio verified identities.
4. Downloads the original SHA-pinned S09 AVI once on the trusted owner Action using existing repository FTP secret, decodes one ephemeral PCM file, computes transient local Resemblyzer voice embeddings, and calculates **leave-one-out provisional role recovery** before using any UNKNOWN cue embeddings.
5. Only *proposes* a candidate for any original UNKNOWN paragraph when >=3 distinct provisional voice references, >=20 held-out samples, >=65% provisional known-role holdout recovery and raw cosine >=0.69 with competitor margin >=0.10. Other original paragraphs abstain.
6. Retains only original paragraph IDs, unverified source-audio locator windows, SHA hashes, holdout counts/scores, cosine and margin. No private soundtrack/media, original subtitle words, actor voiceprint vector or model weights are uploaded or committed.

Source location/paragraph matching still has **no original audio synchronization verification**, even if the movie SHA is exact; source dialogue may be imprecise or overlaid with laughter. Voice similarity to previously *guessed* role labels can reinforce errors. The model is not a human actor identification certifier and does not prove any character voice, even when two independent AI models agree. A source speaker candidate **must pass targeted original film review** before it can count as an independently confirmed identity.

## Trusted execution

PR source-free synthetic tests: `python 'Night Court/tools/test_compare_s09_original_speaker_embeddings.py' -v`.

After merge, the one-shot owner-only trigger branch `research/night-court-owner-s09-speaker-embedding-trigger` may add `Night Court/research/trigger-original-s09-speaker-embedding.txt` in an **unmerged trigger PR**. The trusted workflow `.github/workflows/night-court-s09-original-speaker-matching.yml` reads *only base main* (no PR source execution), retrieves the existing numerical alignment artifact with action read permission and fully SHA-checks its fields, then performs the locally contained original source audio comparison. The separate no-secret job posts exact workflow run link and numerical counts (models, holdouts, accepted zero), and the private artifact retains only small numerical cue/voice **candidates** for 7 days.

**Followup:** review actual source-local actor/voice identification for high-confidence candidates and short/performance-mixed dialogue; keep original untimed 347 source paragraphs and all 751 original source-unit IDs unchanged. This system is only a pragmatic means to get better at naming actual *Night Court* speakers without gambling on adjacent textual role labels.

## Source-backed reference-bank recovery: current v8 roles, October 26

The first original-S09 model run [#40256897493](https://github.com/gamesbyian/general-purpose/actions/runs/40256897493) found only Christine (8) and Roz (7) with old v4 seed names, yielding **15/15 binary provisional-role holdout matches but 0 qualified actor-role predictions from 39 UNKNOWN audio intervals**, because the model required at least three voices and 20 viable known samples. This is a useful abstention, not a failed audio acquisition.

[Source-only v8 planning workflow #40257668073](https://github.com/gamesbyian/general-purpose/actions/runs/40257668073) rebuilt the **587 provisionally named, source-SHA-checked** pilot role reader and reconciled it to the *same 231 real S09 audio interval leads*, entirely without source media/FTP secret.

| Original lexical source coverage | Character voice-reference candidates with at least four source windows | Previously UNKNOWN single-voice audio candidates |
| --- | --- | --- |
| 72% (preferred) | Christine **10**, Roz **7**, Dan **5**, Mac **4** = **26** candidate seed intervals across four characters | **28** |
| 60% (exploratory) | Christine 11, Roz 8, Dan 5, Mac 5, Alex Patterson 4 = **33** across five characters | **32** |
| 50% (exploratory) | Same as 60%, no extra seed role | 32 |

These are **pre-embedding windows**, not 26 independently judged clean acoustic reference examples, and the existing contextual character guesses can be wrong. The next trusted original soundtrack pass uses the **unchanged stronger 72% lexical criterion**, with all original S09 paragraphs still untimed, all mixed-voice exclusions enforced, source model holdout still required, and explicit automatic abstention unless the remaining acoustic samples provide at least three distinct cast voices, 20 held-out samples, and 65% recovery of provisional source labels. No character name should be inferred from insufficient role coverage or the apparent 100% two-role holdout number.

## October 26 2026: upgrade original S09 voice references to latest source-role corpus

The original-S09 acoustic reference builder was still using the v8 **587 provisional named source units** even though the working original-caption P0/P1 reader reached **619/751 provisional names with 132 UNKNOWN**. The newer [source-cue-checked reference adapter](tools/compare_s09_original_speaker_embeddings.py) now reads the immutable `apply_source_role_amendments.py` output on the **entire v6→v13 speaker/turn derivation chain**. The source and reader SHA-256 receipts, all 347 original untimed paragraph IDs, exact current 718 candidate turn reading blocks, role uncertainty, and special quarantined C129 source cue are enforced.

Against the **actual original S09 231-paragraph numeric soundtrack alignment** at the unchanged minimum lexical matching coverage 0.72, the updated reference bank yielded:

| Original-S09 source audio planning metric | Prior v8 source names | Latest source-name patches |
|---|---:|---:|
| Character role reference groups passing 4-sample minimum | 4 | 4 |
| Christine / Dan / Mac / Roz voice-reference sample counts | 10 / 5 / 4 / 7 | 12 / 5 / 4 / 7 |
| Total eligible role-seed original paragraph windows | 26 | 28 |
| Unidentified original paragraphs with eligible sound windows | 28 | 18 |
| Independently human-certified actor identities | 0 | 0 |

The last row of 18 is **not** the number of original UNKNOWN caption units: the working source-role ledger has 132 UNKNOWN units across both pilots, including samples that lack a trustworthy S09 numerical soundtrack location, are too short, have weak lexical match, or contain apparent multiple voices. **PAUL** and other text-inferred guest roles may remain excluded by the four-sample and sound-alignment thresholds. No complete episode's identities have been independently film/audio certified.

Source paragraphs known to have mixed speaker roles (C034, C102, C127, C146, C188–C192, C206, C209, C211, C271, C284, C290–C291, etc.) are deliberately never used as a voice embedding anchor, even when editorial character labels exist. The old `--v8-source-roles` mode remains available for comparing past acoustic reports; it cannot be mixed with the new `--speaker-patch-root` input. The trusted original-film workflow uses reviewed `main` only and only numerical source-aligned results/uncertain hypotheses may leave its private runner. As before, a good sound model match is *evidence for subsequent performer review*, **not authentication of a fictional character by a human**.

```sh
python 'Night Court/tools/compare_s09_original_speaker_embeddings.py' \
  --source-alignment /private/night-court-s09-original-audio-paragraph-locators.json \
  --speaker-patch-root /private/night-court-private-source-role-patches \
  --minimum-coverage 0.72 \
  --output /private/night-court-current-source-speaker-plan.json --plan-only
```
