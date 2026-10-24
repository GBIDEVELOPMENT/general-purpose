# S01E01 complete bounded review: actual-source silent frame acquisition

**Scope:** An original-source **00:56.912–01:33.074** planned editorial review window covering the S01E01 11 caption turns and six stage-action candidates. Existing visual evidence covers earlier, narrower samples. The exact original AVI and SRT SHA and all task IDs are joined through `editorial-review-v1/review-cut-manifest.json`. Source AVI file size is checked and entire original AVI bytes are SHA-256 verified before any extraction.

`tools/build_s01e01_complete_review_frames.py` performs an owner-only, trusted GitHub workflow retrieval of that one exact AVI from the configured FTP server, then produces **145 nominal 4fps silent 320px JPEG samples**, four 8x5 contact sheets, a source-linked per-frame SHA-256 evidence index and a task-based navigation list. To include the final 162ms of the required source review region, the finite FFmpeg sampling range is padded to **00:56.912–01:33.162**; frame sample times are nominal and do *not* establish original frame presentation timestamps.

The source video is temporary and is deleted with the ephemeral directory; **no AVI, raw WAV/MP3 audio, credentials, embeddings, actor voiceprints or model weights** are committed, attached or offered for re-use. Only bounded low-resolution stills, contact sheets and provenance JSON enter a **private 7-day GitHub Actions artifact**, which the reviewer must inspect before drawing any new source-content conclusions. No character, speaking voice, mouth movement, delivery, emotional state, precise physical action onset or whole-episode completeness is accepted by extraction alone.

## Reproducible dispatch

1. Merge the offline-tested feature PR containing the source collector, then create a **same-repository owner PR** on branch `research/night-court-s01e01-complete-review-frames-trigger` changing only `Night Court/research/trigger-s01e01-complete-review-frames.txt`.
2. Trusted `pull_request_target` gate checks exact owner, repo, branch and main base, then checks out **trusted `github.sha` only**. FTP secret is available only to the source retrieval step, never PR-controlled code. The offline unit test runs first against synthetic video with no credentials.
3. Inspect action artifact and exact `frame-index.json`, verify all 145 JPEG digests, visually inspect review moments against source cue times. Next obtain secure continuous-original-video review and independently listen to original soundtrack for actual dialogue, named cast attribution and inflection. Persist only reviewed, supported metadata/annotations.

**Acceptance remains 0 of 17 original audiovisual reviewer tasks and 0 of 193 finished production scripts.** Prior source stills remain valid separate evidence layers, not overwritten. The workflow intentionally handles only the original 1984–1992 series' S01E01 episode.
