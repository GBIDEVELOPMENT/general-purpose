# Night Court agent recovery and pilot-completion handoff, 2026-10-24

## Durable checkpoint

Live latest known `main` commit after qualified integrations: `4787af50e95e9ceefe8366b89b81a72135424736` (PR #300). The previous agent integrated and CI-tested PRs #292 (S09E19 immutable source-once archive), #293 (actual ephemeral 3-frame pixel change measurements), #295 (rejected Whisper word timing proposals and independent Vosk neighbors), #296 (measured original-source pixel-stage report), #297 (S01E01 compact rejected-word export), #298 (bounded source-PTS and candidate-cut-aware 12-window continuous review planner, including two low-change controls), and #300 (16 S01E01 SRT/model conflicts reduced to 16 original-source listening requests, 71.9s combined). Trigger PRs #291, #286, #294 and #299 closed unmerged. PR #258 still open/safety blocked: do not bypass.

Latest genuine original-AVI S09E19 integrated run [#40129675505](https://github.com/gamesbyian/general-purpose/actions/runs/40129675505) **SUCCEEDED**. Its private numerical/text artifact is #12573968622, expires 2026-10-31T20:29:28Z. Artifact ZIP SHA-256 `49de244f965f07baa62b714984506ee55a1a6824e32d516196b8935dc64f064c`. Source report extracted JSON SHA-256 `b86f1de8be857216fa89102c43e8e0cf4ffce64106879ab7e8729ce505530318`. Original AVI SHA `51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649`; original untimed-text SHA `659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2`. Measured whole pass **213.936s** excluding startup/install; **202** native-PTS-confirmed ephemeral JPEGs, **31** three-frame pixel-difference bursts, **12** bounded continuous-source playback review requests totaling **32,488ms**, **90** rejected Whisper word-time hypotheses retained, 347 original paragraphs remain **all untimed**, no verified scenes/speakers/actions/script. This is a newer run than the 170.522s original-source triplet benchmark and must not replace its exact historical numbers.

## Current unmerged work: recover before editing

Branch: `feature/night-court-s09e19-continuity-rejected-word-source-import`. A first-pass importer exists at `Night Court/tools/import_s09e19_continuous_review_evidence.py`, commit `d7a45467d516974352f8ad792ccf542533e34da6`. It is **NOT validated or integrated**; do not claim archive completion. The intent is to enforce exact original research report JSON SHA and only publish tiny, source-grounded textual/numeric research under S09E19/derived, while never rewriting original untimed dialogue or claiming human acceptance. The input original report is preserved privately in artifact #12573968622, downloaded through the GitHub tool in prior session. Continue with synthetic tamper tests, a trusted-base owner-only artifact importer, verified strict SHA ZIP/JSON gate, push data to separate branch, PR independent review and CI, then merge only when qualified. Never commit source AVI/audio/JPEGs/weights. The importer expects the specific numeric report fields; verify these directly against downloaded JSON, not guesses.

## Precise definition of pilot completion

A *source-once evidence benchmark* is a different gate from a *finished richly annotated script*. Both pilots already satisfy core evidence-pass mechanics: same SHA-pinned original AVI, one PCM decode, independent Kaldi/Vosk and Whisper full-episode free ASR, full-video possible-edit scan, actual source-PTS-verified bounded frames, source-free QA and processing wall-clock. The original S01E01 integrated source-once run was **239.826s**; S09E19 original-source runs were **215.140s**, **170.522s**, and **213.936s**. These exclude runner setup/software installs, and none estimates fleet p95 with visual-language analysis.

The normative full script publication gate is `Night Court/AV-SCRIPT-PUBLICATION-GATES.md`. For each pilot, require:
1. Exact original video edition and immutable source transcript fingerprint.
2. Full-runtime dialogue coverage, audited original-source listening/alignment, all disputed and omitted lines handled. For S09E19 347 *untimed original* paragraphs cannot be assigned forged source timecodes. Model time suggestions stay separate.
3. Whole-episode speaker turns and identity accepted by source evidence, with overlaps/anonymous uncertain voices correctly marked.
4. Verified real screen locations, shot/scene changes and chronology, not subtitle-gap heuristics or FFmpeg score spikes.
5. Whole-runtime physical actions, prop business, entrances/exits, reactions, physical jokes and continuity, including missed low-motion controls, evidenced by actually interpreted continuous video.
6. Annotated speech delivery, tone/inflection, nonverbal sound/laughter where recoverable, independently evaluated, not merely F0 or model labels.
7. Readable full production screenplay with sourced stage directions and meaningful descriptive annotations.
8. Independent per-claim/per-scene original AV review, full-runtime gap check, traceable source references, signed/reviewed immutable episode acceptance manifest, and publication gate passing. Do not label a script complete merely because a document was rendered.

Current truth: **S01E01 0/17** bounded editorial tasks accepted; 16 disputed SRT/model consensus spans queued into 16 suggested short listening excerpts totaling **71.9s**, no listening adjudications. **S09E19 0/11** bounded editorial tasks accepted; 13 distinctive, order-consistent lexical paragraph hypotheses, no full 347-paragraph source-time alignment; 12 new unreviewed video playback windows. **Both remain 0 full-episode audiovisual accepted scripts, series 0/193.**

## Next engineering priorities

1. Finalize and integrate the current branch's SHA-locked S09E19 full-source 12-window/90-rejected-word research import before artifact expiry (October 31).
2. Exercise a small actual continuous original-video semantic review job on selected high-, low-score and editorial windows (private scratch), measure media bytes, latency and recall against independently reviewed real physical actions. The current 12 windows are only playback requests, not interpreted video.
3. Build actual anonymous full-episode diarization and ground named character voices with synchronized audio/mouth; no source embeddings or voiceprints retained.
4. Independently adjudicate the S01E01 sixteen contested phrases with original audio, test model agreement joint errors and missing captions, without promoting text by majority vote.
5. Produce one defensible full-episode draft for each pilot, scene-by-scene claim ledger, real passage performance descriptions, and independent review acceptance. Benchmark p95 including visual interpretation on more representative original episodes; two pilots are insufficient to estimate p95.
