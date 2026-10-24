# S01E01 sparse source-cut timing quality review

**Real source processing completed:** owner-controlled [workflow run #40050642750](https://github.com/gamesbyian/general-purpose/actions/runs/40050642750). This is an independent *quality triage of its model output*, not an accepted broadcast edit or a corrected subtitle track.

## What was actually observed

Five non-overlapping original S01E01 AVI samples were processed at 05:00, 10:00, 15:00, 20:00 and 22:30, each for 30 seconds. The original AVI SHA-256 is `5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962` and original source SRT SHA-256 is `aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496`. This is **150 seconds of sampled audio** from a 1448.256-second file, not complete episode listening.

The raw tiny.en model's source-cue starting-difference medians ranged wildly. The 05:00–05:30 sample matched the **same source caption twice**, once over 27 seconds away from its caption start. This is consistent with a badly segmented/duplicated model phrase and cannot establish episode drift. The other windows include audience sounds, model phrase repeats, caption gaps and potentially mismatched cue starts. Broad medians must not be automatically turned into a global source offset or slope.

`tools/import_s01e01_drift_qa.py` preserves the original compressed workflow report **as text/JSON only** in `seasons/S01/S01E01/derived/source-sync-review-v1/sparse-asr-original-source.json` and creates `drift-acceptance-triage.json`/Markdown. Before acceptance it checks:
- the exact episode source and original SRT SHA, unchanged source cue texts/time interval pairs and all five fixed windows;
- each bounded 30-second audio sample's SHA and ASR segment time bounds;
- clipped model intervals, repeated source cue matches and severe start-time discrepancies;
- a stricter manual-listening shortlist requiring strong text similarity, short credible model segments, time difference no greater than 2.5s and **unique** source-cue correspondence.

**No global offset is calculated or claimed.** A window needs at least two distinct possible anchors even to display a local median as an unverified listening suggestion. The release edition, scene action, speaker identities, expressive intonation and complete transcript remain unverified.

## Real continuation

1. Listen to the original video around at least two independent caption anchors per sampled window, checking repeated/overlapping speech and model hallucinations.
2. Resolve or explicitly exclude the anomalous first 05:00 sample; then assess source-to-caption timing differences against the already studied 60–90s passage.
3. Fit a synchronized episode edit offset/drift only after passing accepted source-text and audio proof, not from model-generated high-similarity text matches alone.
4. Preserve both the original subtitle file and every unverified model report; corrected source editions must be separate derived artifacts.
5. Coordinate FTP video renames with the separate Plex cleanup agent. The existing owner's source-video SHA, not a filename, is our stable identity.

See [S01E01 original sparse drift handoff](S01E01-SOURCE-CUT-DRIFT-HANDOFF.md) and [production workboard](AV-SCRIPT-PRODUCTION-WORKBOARD.md). This companion report supplies independent QA and source preservation, not another network run.
