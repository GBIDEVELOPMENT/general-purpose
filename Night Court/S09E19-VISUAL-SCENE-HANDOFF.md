# S09E19 real scene settings and physical-action evidence pilot

**Status:** original 100-frame source image acquisition completed, plus first sample-grounded scene observations in integration review. Continuous video and voices remain unverified. Original series only.

The S09E19 untimed-source pilot [run #40054051699](https://github.com/gamesbyian/general-purpose/actions/runs/40054051699) proved the exact source AVI checksum (`51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649`) and produced 15 distinctive lexical candidate links across five 25-second voice windows. The **15:00–15:25** window was selected for the first visual pilot because it yielded **five candidate paragraph matches** in a comparatively concentrated area of the preserved 347-paragraph dialogue witness (around paragraphs 240–253).

`tools/build_s09e19_visual_source_packet.py` extracts exactly **100 JPEG stills at nominal four frames per second**, 320 pixels wide, plus a contact sheet and a source-index JSON containing each individual image SHA and nominal sample time. Original AVI and audio are not stored. The evidence is source-hash gated to the accepted 183,377,920-byte FTP AVI, processed only transiently in a trusted owner-only `pull_request_target` job on the **reviewed `github.sha` base**, not PR-head code.

**Important:** A 4fps sample is not continuous-video acceptance, and a visible person is not yet a named speaker. The packet makes no character, scene-setting, movement, reaction, vocal-tone, transcript timing or episode-completeness claims until the actual images have been inspected. The timed ASR-to-untimed-paragraph matches remain separate tentative source witnesses. The primary original subtitle-paragraph source remains untimed.

After the run, a strict importer must verify all 100 JPEG hashes, original AVI SHA, source-interval limits, and no original audio/video or source transcript rewrite before committing a private episode-local research packet. Editorial reviewers can then add **time-indexed descriptions of only things visible across ordered sampled frames**, explicitly labeling any inferred movement from before/after states. A future production script merges reviewed text, voice, setting and action with evidence pointers and distinct uncertainty states.

## Real original-series image review and first visual observations

Owner-triggered [run #40054491519](https://github.com/gamesbyian/general-purpose/actions/runs/40054491519) **succeeded**, acquiring **100 exact-source SHA-indexed images** and a contact sheet from the 15:00–15:25 original AVI. Artifact #12544518469 was visually inspected. The source frames show a conversation at an interior counter, with a uniformed adult and a gray-jacketed adult; between nominal 913.00 and 913.25 seconds the view changes to a seated person in burgundy with a conspicuous yellow collar and a glass on the table. The seated person changes head position and moves hands over the following sampled seconds. Between nominal 919.50 and 919.75 seconds the picture changes to a bearded adult in a jacket and tie; later samples show a smile.

These are **sampled, AI-reviewed visual observations**, with exact frame numbers and SHA-256 recorded in the integration output `seasons/S09/S09E19/derived/visual-review-v1/visual-source-review.json`, NOT independently reviewed 25fps continuous-motion frames or exact shot cut timestamps. Stage notes use unidentified visual descriptions. The model's five tentative lexical anchors to the untimed 347-paragraph source are kept as unconfirmed paragraph locators, **not line-to-speaker assignments or new subtitle timecodes**.

The importer `tools/import_s09e19_visual_review.py` verifies every frame and exact source AVI/TXT SHA, rejects extra media and false accepted scene/speaker flags, and emits the narrow, evidence-linked [scene visual notes](seasons/S09/S09E19/derived/visual-review-v1/scene-visual-observations.md). A separate independent listener/video acceptance gate remains necessary before any production screenplay claim.

No bulk 193-episode media acquisition or unsupervised audiovisual certification is authorized by this pilot.
