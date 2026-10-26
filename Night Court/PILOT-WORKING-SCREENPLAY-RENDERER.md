## Leading working editorial layer: private v16

The v15 renderer documented below remains an immutable-source reference baseline. The **current** editor-reviewed v16 applies the SHA/source-ref-checked [2026-10-26 manual role ledger](research/manual-context-editorial-speaker-review-v16.json). After building private v15 source-first rows as before:

    python 'Night Court/tools/apply_manual_context_pilot_review_v16.py' \
      --v15-root /tmp/night-court-private-v15 \
      --output /tmp/night-court-private-v16

The output includes both improved original-dialogue working manuscripts, SHA-bound provenance and source records, an editorial-only v16 report, and a current working-screenplay-layout manifest. It **does not** modify original SRT/paragraphs, v15 reader or original AV acceptance. Thirty source units newly become fully provisionally named; the current 100 UNKNOWN source units still require P0/P1 attention. Two role corrections reverse S09 C305/C306, while original C277 is reversibly split into two still-UNKNOWN parts.

To generate the matching private fan corpus, use the ordinary fan exporter with `--working-pilot-root /tmp/night-court-private-v16` instead of the old v15 directory. The source-backed CI also generates the 100-unit review worklist via `tools/plan_remaining_manual_v16_review.py`, using the original numeric S09 audio-locator artifact. Its S09 windows remain ASR **search proposals**, not original transcript timing.

# Private readable pilot screenplay layout (P0/P1, 2026-10-26)

This is a **working draft generator**, not an audiovisual acceptance shortcut. It turns the most recent private **v15 source-first reader** into two legible, source-linked original-series screenplay *dialogue* manuscripts, with one character heading for contiguous rows bearing the same provisional name. Because those names and boundaries have not been independently listened to, the output says **DISPLAY CONTINUATION, UNVERIFIED** rather than asserting a performed single turn. UNKNOWN turns are never merged and distinct voices provisionally split within one original cue are never rejoined.

## Run after regenerating the current v15 private reader

Run the existing source-first chain documented in the [Night Court README](README.md), ending with the output of tools/apply_s01_c219_source_turn.py. Then, with that private output directory:

    PYTHONPATH='Night Court/tools' python 'Night Court/tools/render_current_pilot_screenplays.py' \
      --source-first-v15 /tmp/night-court-private-current-v15 \
      --output /tmp/night-court-private-readable-pilots

The output directory must be **outside the repository**. The input directory example is a placeholder: point to the actual v15 output containing pilot-source-episode-turns-v15.jsonl and its cryptographic manifest. Add --no-layout-continuations for a conservative one-heading-per-raw-row view, useful for side-by-side review. No FTP, model/API invocation or media files are needed for the layout pass itself, though building the upstream private source-first reader requires its separately documented evidence.

Outputs:
- S01E01-working-screenplay.md and S09E19-working-screenplay.md: complete **working dialogue** presentation, without making up scenes, stage directions, tone, accurate subturn clocks or named guest voices.
- Two corresponding -working-screenplay-provenance.jsonl files: each original private reader row in unchanged sequence, its exact dialogue SHA-256, immutable source part refs, any existing precise Unicode spans and cue envelopes clearly labeled as **cue** times, not individual speech times.
- working-screenplay-layout-manifest.json: original 726 input source-reader block count, 751 original speaking-unit invariants, 621 provisional names / 130 unknowns, both source witness SHAs, display-only grouping counts and complete output digests.

This renderer validates the v15 manifest SHA against the reader JSONL bytes, the actual local held caption-source SHA through load_witness, all unique block IDs and ordered original cue-part references, precisely 404 S01 and 347 S09 original units, abstention on independently unverified voices, and the prohibition on inventing S09 timestamps. It does **not** reinterpret existing source-fragment conservation: that is checked by the upstream v13–v15 transforms. Source-text indentation in the Markdown is presentational, and the original reader rows are never overwritten. All full dialogue stays in private temporary output.

## Quality gate and next contribution

The output now has the useful *shape* of a working script, but the scene headings are deliberately placeholders pending review, and provisional display joins must be individually adjudicated using original soundtrack context. The renderer does not replace [issue #441](https://github.com/gamesbyian/general-purpose/issues/441), the current 34/96 source-UNKNOWN review queue, the S09 C291 uncertain handoff, the quarantined S09 C129 character guess, or genuine filmed-performance evidence.

No finished episode or new audio-certified character identity should be reported from layout grouping alone. Prioritize real source first P0/P1 corrections; then rerun this tool to produce reader-friendly manuscripts after those corrections. Once independently accepted speaker evidence exists, a follow-up generator can add source-reviewed scene/gesture/delivery fields without discarding this reversible dialogue view.

## Same-reader fan retrieval

With the *same* SHA-checked output directory, update the private fan retrieval corpus rather than indexing the old v5 manuscript:

    python 'Night Court/tools/export_fan_retrieval_chunks.py' \
      --working-pilot-root /tmp/night-court-private-readable-pilots \
      --output /tmp/night-court-private-current-fan-corpus

This command keeps the other 191 original source-only episode scaffolds, replaces only the **two pilot** script inputs, and marks their evidence tier `provisional_source_first_chronological_screenplay_layout`. It refuses wrong source counts, altered manuscript digests, unsupported AV promotion and invented S09 original timing. The private corpus chunks round-trip to the complete current screenplay text. The generator does not implicitly change the existing default historical v5 mode; the choice of current private output must be explicit and the script directory available. Both full screenplay and fan retrieval text remain private and uncommitted.

The private **seven-day GitHub Actions download** also includes `private-review/remaining-100-speaker-review.jsonl`, a ranked source-preserving P0/P1 packet with exact dialogue excerpts and neighboring lines for the 21 S01 /79 S09 unresolved original source units. This portable packet deliberately does **not** invent S09 audio clocks: it has S01 caption window leads and a `s09_candidate_audio_locator_loaded: false` flag. The original-audio-locator CI separately builds the fully time-leaded private queue when the original S09 numeric matching evidence exists. Neither packet assigns new voices or confirms performers.
