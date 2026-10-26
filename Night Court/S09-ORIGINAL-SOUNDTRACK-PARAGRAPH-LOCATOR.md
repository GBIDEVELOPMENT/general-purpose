# S09E19: original untimed source paragraphs to actual soundtrack (P0/P1 dependency)

Original 1992 **Night Court** S09E19 *P.S. Do I Know You?* contains **347 original held untimed transcript paragraphs**. Their text SHA-256 remains `659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2`. The original owner AVI independently SHA-checked in earlier experiments has SHA-256 `51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649`, size 183,377,920 bytes. This exact source pairing is the sole accepted input for this pilot.

**Speaker identity is still priority one.** S09 accounts for the majority of remaining unidentified speakers. Its original source text has no timestamps, so arbitrary caption-to-audio matching cannot be used as proof of who speaks. Prior source pilots used at most 40 lexical ASR snippets; the external public SubtitleCat site did not yield a defensible complete timed witness. The new `tools/align_s09_original_audio_paragraphs.py` is the needed no-new-training foundation.

Pipeline:

1. On an owner-only trusted source runner (never executing unreviewed PR code with FTP credentials), download the known S09 original AVI once, verify size and exact full-file SHA.
2. Decode one ephemeral 16-kHz mono original soundtrack and run the existing, fast, CPU Whisper tiny.en unprompted recognizer to produce a local-only timed ASR word stream.
3. Flatten all 347 exact original untimed source paragraphs into source-word sequence, preserving each original paragraph ID. Find **monotonically ordered blocks of at least 3 exact lexical tokens** between the two sequences using Python's standard-library `SequenceMatcher`, without telling the recognizer the source transcript.
4. Offer candidate **source-audio start/end windows** only for paragraphs with at least three exact globally matched words and at least 46% of the paragraph's words matched. Omit short or repeatedly ambiguous words and spans longer than 18 seconds.
5. Retain only the matched original paragraph IDs, numerical original audio **candidate** windows, coverage and original movie/caption/decoded-PCM SHA; **no full source dialogue, original ASR word stream, film, PCM, voiceprints or model weights** in any retained artifact.

This is an efficient source-video/untimed-text alignment *candidate* pass, **not source caption timestamp recovery, audio verification, speaker diarization or original broadcast confirmation**. Any matched paragraph may contain two speakers and must be split appropriately. Studio laughter, variation between this AVI and source captions, silent scenes and ASR hallucination can also produce errors. A source paragraph which lacks enough evidence remains **unlocated** with original timestamps null. We explicitly do not present these candidates as 347 exact film-synchronized timecodes.

## Usage

```sh
python 'Night Court/tools/test_align_s09_original_audio_paragraphs.py' -v
python 'Night Court/tools/align_s09_original_audio_paragraphs.py' \
  --offline-plan-only --output /tmp/no-s09-video-requested.json
```

Actual source run is requested only by a PR from the exact branch `research/night-court-owner-s09-original-audio-align-trigger` changing `Night Court/research/trigger-s09-original-audio-paragraph-alignment.txt`, under trusted reviewed-base workflow `.github/workflows/night-court-s09-original-audio-paragraph-alignment.yml`. The trigger PR must stay **unmerged**. Once the source run finishes, an isolated secret-free notifier reports only original paragraph matched/unmatched counts to that trigger PR; only compact numerical/hashes + tentative original-audio windows are retained in a private Actions artifact for 7 days.

## What comes next

If original-source alignment yields a useful number of high-lexical-coverage candidate windows, pair those windows with an updated S09 source-role reading ledger and audio speaker-embedding reference comparisons, **only for multiword and uncontested speaker candidates**. First test held-out internal cast voice recovery; compare P0 speaker-change uncertainties (e.g. C034.1, C102, C127, C146, C188–C191, C211, C271, C291–C293) against actual original soundtrack and scene video. Count truly resolved speakers and wrongly named old roles only when grounded. Keep all original 347 untimed source cues and their SHA unchanged throughout.
